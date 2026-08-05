import pytest
from recognition.accessGrantor import (
    AccessGrantor,
    AccessGrantorExample,
    accessGrantorExample,
)


def test_abstract_base_cannot_be_instantiated():
    with pytest.raises(TypeError):
        AccessGrantor()


def test_grant_access_with_data_returns_none():
    grantor = AccessGrantorExample()
    assert grantor.grantAccess("Messi") is None


def test_grant_access_without_data_returns_none():
    grantor = AccessGrantorExample()
    assert grantor.grantAccess(None) is None


def test_singleton_is_example_instance():
    assert isinstance(accessGrantorExample, AccessGrantorExample)
    assert isinstance(accessGrantorExample, AccessGrantor)
