import pytest

from network.models import NetworkMember

pytestmark = pytest.mark.django_db


class TestNetworkMemberModel:
    def test_str(self, db):
        member = NetworkMember(name="Mon partenaire")
        assert str(member) == "Mon partenaire"
