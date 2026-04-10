import io

import pytest
from django.core.files.images import ImageFile
from django.test import Client
from wagtail.images.models import Image

from network.models import NetworkMember

pytestmark = pytest.mark.django_db


def _create_test_image(name="test.png"):
    """Create a minimal 1x1 PNG image for testing."""
    # Minimal valid 1x1 white PNG
    import struct
    import zlib

    def _chunk(chunk_type, data):
        c = chunk_type + data
        return struct.pack(">I", len(data)) + c + struct.pack(">I", zlib.crc32(c) & 0xFFFFFFFF)

    header = b"\x89PNG\r\n\x1a\n"
    ihdr = _chunk(b"IHDR", struct.pack(">IIBBBBB", 1, 1, 8, 2, 0, 0, 0))
    raw = zlib.compress(b"\x00\xff\xff\xff")
    idat = _chunk(b"IDAT", raw)
    iend = _chunk(b"IEND", b"")
    png_data = header + ihdr + idat + iend

    f = io.BytesIO(png_data)
    f.name = name
    image = Image(title=name)
    image.file = ImageFile(f, name=name)
    image.save()
    return image


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

    def test_member_with_logo(self, client: Client):
        image = _create_test_image("logo.png")
        NetworkMember.objects.create(
            name="Avec Logo", member_type="Partenaire", logo=image
        )

        resp = client.get(self.url)
        member = resp.json()[0]

        assert member["logo_url"] is not None
        assert "logo" in member["logo_url"]

    def test_post_not_allowed(self, client: Client):
        resp = client.post(self.url)
        assert resp.status_code == 405


class TestNetworkMemberModel:
    def test_str(self, db):
        member = NetworkMember(name="Mon partenaire")
        assert str(member) == "Mon partenaire"
