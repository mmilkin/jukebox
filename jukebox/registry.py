from zope.interface.adapter import AdapterRegistry
from zope.interface.interface import adapter_hooks
import zope.interface


registry = AdapterRegistry()


def hook(provided, object):
    adapter = registry.lookup1(zope.interface.providedBy(object), provided, '')
    if not adapter:
        return
    return adapter(object)
adapter_hooks.append(hook)


def configure_registry():
    from jukebox import interfaces
    from jukebox import storage

    registry.register(
        [interfaces.ISearchableStorage],
        interfaces.IStorage,
        '',
        storage.NoOpStorageAdaptor
    )
    registry.register(
        [interfaces.IStorage],
        interfaces.ISearchableStorage,
        '',
        storage.NoOpSearchableStorage
    )
