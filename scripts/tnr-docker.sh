#!/usr/bin/env bash
# tnr-docker.sh — Manage the ephemeral Docker environment for regression tests.
#
# Stack : Next.js + Django/Wagtail + Postgres + MinIO + Nginx
#
# Usage:
#   ./scripts/tnr-docker.sh up      # Build, start, migrate, init MinIO bucket, seed test data
#   ./scripts/tnr-docker.sh down    # Tear down and remove volumes
#   ./scripts/tnr-docker.sh status  # Show running services
#
# The environment is accessible at http://localhost:8080
#
# Placeholders à remplacer :
#   culturall-website    : nom du projet docker compose pour la TNR
#                            (ex: studio-site-tnr)

set -euo pipefail

PROJECT_NAME="culturall-website-tnr"
COMPOSE="docker compose -p $PROJECT_NAME \
  -f docker-compose.base.yml \
  -f docker-compose.test.yml \
  --env-file .env.test"

cd "$(dirname "$0")/.."

usage() {
    echo "Usage: $0 {up|down|status}"
    echo ""
    echo "  up      Build and start the ephemeral TNR environment"
    echo "  down    Tear down the environment and remove all data"
    echo "  status  Show running services"
    exit 1
}

wait_for_django() {
    echo "Waiting for Django to be ready..."
    local retries=30
    while [ $retries -gt 0 ]; do
        if $COMPOSE exec -T django python -c "import django; django.setup()" 2>/dev/null; then
            echo "Django is ready."
            return 0
        fi
        retries=$((retries - 1))
        sleep 2
    done
    echo "ERROR: Django did not become ready in time."
    $COMPOSE logs django
    exit 1
}

wait_for_nextjs() {
    echo "Waiting for Next.js to be ready..."
    local retries=30
    while [ $retries -gt 0 ]; do
        if $COMPOSE exec -T nextjs wget -q -O /dev/null http://localhost:3000 2>/dev/null; then
            echo "Next.js is ready."
            return 0
        fi
        retries=$((retries - 1))
        sleep 2
    done
    echo "ERROR: Next.js did not become ready in time."
    $COMPOSE logs nextjs
    exit 1
}

run_migrations() {
    echo "Running Django/Wagtail migrations..."
    $COMPOSE exec -T django python manage.py migrate --noinput
    echo "Collecting static files..."
    $COMPOSE exec -T django python manage.py collectstatic --noinput || true
}

seed_test_data() {
    echo "Seeding test data (Wagtail superuser + 2 test users)..."
    $COMPOSE exec -T django python manage.py shell <<'PYTHON'
from django.contrib.auth import get_user_model

User = get_user_model()

# Superuser pour Wagtail admin
if not User.objects.filter(username="admin").exists():
    User.objects.create_superuser(
        username="admin",
        email="admin@example.com",
        password="Adminpass123!",
    )
    print("Created superuser: admin / Adminpass123!")

# Utilisateur de test 1
if not User.objects.filter(email="testuser@example.com").exists():
    User.objects.create_user(
        username="testuser",
        email="testuser@example.com",
        password="Testpass123!",
        first_name="Test",
        last_name="User",
    )
    print("Created user: testuser")

# Utilisateur de test 2
if not User.objects.filter(email="testuser2@example.com").exists():
    User.objects.create_user(
        username="testuser2",
        email="testuser2@example.com",
        password="Testpass123!",
        first_name="Test2",
        last_name="User2",
    )
    print("Created user: testuser2")
PYTHON
    echo "Test data seeded."
}

cmd_up() {
    echo "Building and starting TNR environment (Next.js + Django/Wagtail + MinIO)..."
    $COMPOSE up --build -d

    wait_for_django
    run_migrations
    seed_test_data
    wait_for_nextjs

    # Le bucket MinIO est créé automatiquement par le service `minio-init`
    # défini dans docker-compose.base.yml. On vérifie qu'il s'est bien terminé.
    if $COMPOSE ps minio-init 2>/dev/null | grep -q "Exit 0\|exited (0)"; then
        echo "MinIO bucket initialized."
    else
        echo "WARN: minio-init has not exited cleanly. Check logs:"
        $COMPOSE logs minio-init || true
    fi

    echo ""
    echo "============================================"
    echo "  TNR environment ready!"
    echo "  URL  : http://localhost:8080"
    echo "  Admin: http://localhost:8080/admin/  (admin / Adminpass123!)"
    echo "============================================"
    echo ""
    echo "Run regression tests with:"
    echo "  BASE_URL=http://localhost:8080 API_URL=http://localhost:8080 /regression-tests"
    echo ""
    echo "Tear down when done:"
    echo "  ./scripts/tnr-docker.sh down"
}

cmd_down() {
    echo "Tearing down TNR environment..."
    $COMPOSE down -v --remove-orphans
    echo "TNR environment removed."
}

cmd_status() {
    $COMPOSE ps
}

case "${1:-}" in
    up)     cmd_up ;;
    down)   cmd_down ;;
    status) cmd_status ;;
    *)      usage ;;
esac
