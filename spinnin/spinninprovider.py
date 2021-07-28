from collections import OrderedDict

from qiskit.providers import BaseProvider
from qiskit.providers.models import BackendConfiguration

from spinninbackend import SpinninBackend


class SpinninProvider(BaseProvider):
    """Provider for Spinnin backends."""

    def __init__(self):
        """Return a new SpinninProvider."""
        super().__init__()

        # Populate the list of remote backends.
        self._backends = [SpinninBackend(provider=self)]
    
    def get_backend(self, name=None, **kwargs):
        return super().get_backend(name=name, **kwargs)

    def backends(self, name=None, **kwargs):
        backends = self._backends

        if name:
            backends = [b for b in backends if b.name() == name]

        return list(backends)

