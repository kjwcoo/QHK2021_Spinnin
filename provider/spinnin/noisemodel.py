import numpy as np
from qiskit import QuantumCircuit
from qiskit.providers.aer import AerSimulator
from qiskit.quantum_info.operators import Operator4
from qiskit.circuit import Gate

from qiskit.providers.aer.noise import NoiseModel
from qiskit.providers.aer.noise import mixed_unitary_error
from qiskit.providers.aer.noise import QuantumError

"""
Experiment parameters
"""
J_0 = 100*10^6
sigma_J_0 = 0.1 * J_0
h_0 = 5 * J_0 
sigma_h_0 = 0.0001 * J_0 
epsilon = 0.1 * J_0^(-1)

"""
Noisy gates
"""
class NoisyI( Gate ):
    def __init__( self, tau, delta_B, label=None ):
        super().__init__( 'NoisyI ', 1, [ tau, delta_B ], label=label )
        
    def _define( self ):
        qc = QuantumCircuit( 1 )
        qc.unitary( self.to_matrix(), [ 0 ] )
        
        self.definition = qc
        
    def to_matrix( self ):
        t = float( self.params[ 0 ] )
        d = float( self.params[ 1 ] )
        
        return np.array( [ [ np.exp( -1.0j * t * d / 2 ), 0 ],
                            [ 0, np.exp(1.0j * t * d / 2) ] ] )

class NoisyX( Gate ): 
    def __init__( self, tau, delta_B, delta_J, label=None ):
        super().__init__( 'NoisyX ', 1, [ tau, delta_B, delta_J ], label=label )
        
    def _define( self ):
        qc = QuantumCircuit( 1 )
        qc.unitary( self.to_matrix(), [ 0 ] )
        
        self.definition = qc
        
    def to_matrix( self ):
        t = float( self.params[ 0 ] )
        d = float( self.params[ 1 ] )
        j = float( self.params[ 2 ] )
        prefactor = np.sqrt( ( J_0 + j )^2 + d^2 )
        return np.array( [ [ np.cos( prefactor * t ) - 1.0j * d / prefactor * np.sin( prefactor * t ), -1.0j ( J_0 + j ) / prefactor * sin( prefactor * t ) ],
                            [ -1.0j ( J_0 + j ) / prefactor * sin( prefactor * t ), np.cos( prefactor * t ) + 1.0j * d / prefactor * np.sin( prefactor * t )] ] )

class NoisyY( Gate ): 
    def __init__( self, tau, delta_B, delta_J, label=None ):
        super().__init__( 'NoisyY ', 1, [ tau, delta_B, delta_J ], label=label )
        
    def _define( self ):
        qc = QuantumCircuit( 1 )
        qc.unitary( self.to_matrix(), [ 0 ] )
        
        self.definition = qc
        
    def to_matrix( self ):
        t = float( self.params[ 0 ] )
        d = float( self.params[ 1 ] )
        j = float( self.params[ 2 ] )
        prefactor = np.sqrt( ( J_0 + j )^2 + d^2 )
        return np.array( [ [ np.cos( prefactor * t ) - 1.0j * d / prefactor * np.sin( prefactor * t ), -( J_0 + j ) / prefactor * sin( prefactor * t ) ],
                            [ ( J_0 + j ) / prefactor * sin( prefactor * t ), np.cos( prefactor * t ) + 1.0j * d / prefactor * np.sin( prefactor * t )] ] )

class NoisyRZZ( Gate ):
    def __init__( self, tau, delta_J, label=None ):
        super().__init__( 'NoisyRZZ ', 1, [ tau, delta_J ], label=label )
        
    def _define( self ):
        qc = QuantumCircuit( 2 )
        qc.unitary( self.to_matrix(), [ 0, 1 ] )
        
        self.definition = qc
        
    def to_matrix( self ):
        t = float( self.params[ 0 ] )
        j = float( self.params[ 1 ] )
        
        return np.array( [ np.exp( epsilon * ( J_0 + j )^2 ), np.exp( -epsilon * ( J_0 + j )^2 ), np.exp( -epsilon * ( J_0 + j )^2 ), np.exp( epsilon * ( J_0 + j )^2 ) ] )
    
"""
Pre-generate standard sampling points
"""
samplingNum = 1000
samplingPoints = np.random.uniform( -3.0, 3.0, samplingNum) # Sample thousand points for 3-sigma
samplingProbs = 1/np.sqrt( 2*np.pi ) * np.exp( -samplingPoints^2 / 2 )

noiseModel = NoiseModel()

"""
Noise model configuration
NOTE: "tau" in this code is a nonsense variable.
"""
noisyI = []
for i in range( samplingNum ):
    noisyI.append( ( NoisyI( tau, h_0 + samplingPoints[ i ] * sigma_h_0 ), samplingProbs[ i ] ) ) 
errorI = mixed_unitary_error( noisyI )
noiseModel.add_quantum_error( errorI, [ 'id' ])

noisyX = []
for i in range( samplingNum ):
    noisyX.append( ( NoisyX( tau, h_0 + samplingPoints[ i ] * sigma_h_0, J_0 + samplingPoints[ i ] * sigma_J_0 ), samplingProbs[ i ] ) ) 
errorX = mixed_unitary_error( noisyX )
noiseModel.add_quantum_error( errorX, [ 'rx' ])

noisyY = []
for i in range( samplingNum ):
    noisyY.append( ( NoisyY( tau, h_0 + samplingPoints[ i ] * sigma_h_0 , J_0 + samplingPoints[ i ] * sigma_J_0 ), samplingProbs[ i ] ) ) 
errorY = mixed_unitary_error( noisyY )
noiseModel.add_quantum_error( errorY, [ 'ry' ])

noisyRZZ = []
for i in range( samplingNum ):
    noisyRZZ.append( ( NoisyRZZ( tau, J_0 + samplingPoints[ i ] * sigma_J_0 ), samplingProbs[ i ] ) ) 
errorRZZ = mixed_unitary_error( noisyRZZ )
noiseModel.add_quantum_error( errorRZZ, [ 'rzz' ])

