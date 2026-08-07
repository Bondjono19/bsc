import pytest

from recognition.accessGrantor import AccessGrantor
from recognition.grantors.example import AccessGrantorExample
from recognition.utils.access_grantor_loader import load_access_grantor_impl

EXAMPLE_PATH = "recognition.grantors.example:AccessGrantorExample"


def test_abstract_base_cannot_be_instantiated():
    with pytest.raises(TypeError):
        AccessGrantor()


def test_example_implements_the_interface():
    assert issubclass(AccessGrantorExample, AccessGrantor)
    assert isinstance(AccessGrantorExample(), AccessGrantor)


def test_grant_access_with_data_returns_none():
    grantor = AccessGrantorExample()
    assert grantor.grantAccess("Messi") is None


def test_grant_access_without_data_returns_none():
    grantor = AccessGrantorExample()
    assert grantor.grantAccess(None) is None


# --- Implementation loader -------------------------------------------------


def test_loader_returns_configured_implementation(monkeypatch):
    monkeypatch.setenv("ACCESS_GRANTOR", EXAMPLE_PATH)
    grantor = load_access_grantor_impl()
    assert isinstance(grantor, AccessGrantorExample)
    assert isinstance(grantor, AccessGrantor)


def test_loader_rejects_class_that_is_not_an_access_grantor(monkeypatch):
    # A loadable class that does not implement the interface must be refused.
    monkeypatch.setenv("ACCESS_GRANTOR", "json:JSONDecoder")
    with pytest.raises(TypeError):
        load_access_grantor_impl()


def test_loader_requires_the_env_var(monkeypatch):
    monkeypatch.delenv("ACCESS_GRANTOR", raising=False)
    with pytest.raises(KeyError):
        load_access_grantor_impl()
