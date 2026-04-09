# Frontend — Next.js 14 (multi-stage, mode standalone)
#
# Targets :
#   - development  : `npm run dev` avec hot reload
#   - builder      : `npm run build` (compile Next.js standalone)
#   - production   : runtime minimal (~50MB), utilisateur non-root
#
# Le code applicatif vit dans ../frontend (contexte de build = ./frontend
# dans les compose files).
#
# Prérequis : next.config.js doit contenir `output: 'standalone'`.

# ─── Stage : base ──────────────────────────────────────────────
FROM node:20-alpine AS base

WORKDIR /app

# ─── Stage : deps (layer cacheable) ────────────────────────────
FROM base AS deps

COPY package.json package-lock.json* ./
RUN npm ci

# ─── Stage : development ───────────────────────────────────────
FROM deps AS development

COPY . .

EXPOSE 3000
CMD ["npm", "run", "dev"]

# ─── Stage : builder ───────────────────────────────────────────
FROM deps AS builder

COPY . .
ENV NEXT_TELEMETRY_DISABLED=1
RUN npm run build

# ─── Stage : production ────────────────────────────────────────
FROM base AS production

ENV NODE_ENV=production \
    NEXT_TELEMETRY_DISABLED=1

# Utilisateur non-root
RUN addgroup --system --gid 1001 nodejs \
    && adduser --system --uid 1001 nextjs

# Copier la sortie standalone
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static
COPY --from=builder --chown=nextjs:nodejs /app/public ./public

USER nextjs

EXPOSE 3000
ENV PORT=3000 HOSTNAME=0.0.0.0

CMD ["node", "server.js"]
