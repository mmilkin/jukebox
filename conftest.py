import pytest


@pytest.fixture(autouse=True, scope='session')
def setup():
    from jukebox.registry import configure_registry
    configure_registry()
