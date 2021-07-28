#!/usr/bin/env python
# coding: utf-8

# In[ ]:

from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister, execute, Aer
from qiskit.transpiler import PassManager
from spinninbackend import SpinninBackend
from spinninjob import SpinninJob
from spinninprovider import SpinninProvider

qreg = QuantumRegister(1)
creg = ClassicalRegister(1)
qc = QuantumCircuit(qreg, creg)
qc.x(qreg[0])
qc.y(qreg[0])
qc.measure(qreg, creg)

# Use the custom provider to simulate the circuit
provider = SpinninProvider()

job = execute(qc, provider.get_backend('SpinninBackend'), optimization_level=0, pass_manager=PassManager(), shots=1024)

result = job.result()

# Print the results of both providers
print('Hadamard simulator:')
print(result)