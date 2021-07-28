from qiskit.providers import BaseBackend
from qiskit.providers.models import BackendConfiguration
from spinninjob import SpinninJob

class SpinninBackend(BaseBackend):
    def __init__(self, provider=None):
        configuration = {
            'backend_name': 'SpinninBackend',
            'backend_version': '0.0.1',
            'simulator': False,
            'local': True,
            'basis_gates': ['rx', 'ry', 'rz', 'cp'],
            'memory': True,
            'n_qubits': 1,
            'conditional': False,
            'max_shots': 10000,
            'open_pulse': True,
            'gates': [],
            'coupling_map': None
        }
        
        super().__init__(configuration=BackendConfiguration.from_dict(configuration), provider=provider)

    def run(self, qobj):
        job = SpinninJob(self, qobj=qobj)
        job.submit()
        return job

