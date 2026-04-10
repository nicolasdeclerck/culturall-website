import pytest
from django.test import Client

from network.models import NetworkMember

pytestmark = pytest.mark.django_db


class TestNetworkMemberListView:
    url = "/api/network/"

    def test_empty_list(self, client: Client):
        resp = client.get(self.url)
        assert resp.status_code == 200
        assert resp.json() == []

    def test_returns_members(self, client: Client):
        NetworkMember.objects.create(name="Partenaire A", member_type="Institutionnel")
        NetworkMember.objects.create(name="Partenaire B", member_type="Privé")

        resp = client.get(self.url)
        data = resp.json()

        assert len(data) == 2
        names = {m["name"] for m in data}
        assert names == {"Partenaire A", "Partenaire B"}

    def test_member_fields(self, client: Client):
        NetworkMember.objects.create(name="Mon Partenaire", member_type="Associatif")

        resp = client.get(self.url)
        member = resp.json()[0]

        assert member["name"] == "Mon Partenaire"
        assert member["member_type"] == "Associatif"
        assert member["logo_url"] is None

    def test_ordering_by_name(self, client: Client):
        NetworkMember.objects.create(name="Zebra", member_type="Type A")
        NetworkMember.objects.create(name="Alpha", member_type="Type B")

        resp = client.get(self.url)
        data = resp.json()
        assert data[0]["name"] == "Alpha"
        assert data[1]["name"] == "Zebra"

    def test_post_not_allowed(self, client: Client):
        resp = client.post(self.url)
        assert resp.status_code == 405


class TestNetworkMemberModel:
    def test_str(self, db):
        member = NetworkMember(name="Mon partenaire")
        assert str(member) == "Mon partenaire"
