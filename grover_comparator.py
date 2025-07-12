from qiskit import QuantumCircuit, QuantumRegister
from qiskit.primitives import Sampler
from qiskit.quantum_info import Operator
import numpy as np

class GroverComparator:
    def __init__(self, number_1: int, number_2: int):
        self.number_1 = number_1
        self.number_2 = number_2
        self.diff = number_1 - number_2
        self.nqubits = max(abs(self.diff).bit_length(), 2)
        self.nstates = 2 ** self.nqubits
        self.qc = QuantumCircuit(self.nqubits)

    def create_comparison_oracle(self):
        """
        Create an oracle that marks states corresponding to (number_1 >= number_2).
        """
        qr = QuantumRegister(self.nqubits)
        qc = QuantumCircuit(qr, name='Oracle(>=)')
        
        # Create a diagonal matrix where the index corresponding to the absolute value
        # of the difference (|diff|) is marked with -1
        gate_matrix = np.eye(2 ** self.nqubits, dtype=int)
        i = abs(self.diff)
        gate_matrix[i][i] = -1
        
        comparison_operator = Operator(gate_matrix)
        qc.unitary(comparison_operator, range(self.nqubits))
        
        return qc.to_instruction()

    def create_diffuser(self):
        """
        Create a Grover diffuser for nqubits.
        """
        qr = QuantumRegister(self.nqubits)
        qc = QuantumCircuit(qr, name='Diffuser')
        
        qc.h(range(self.nqubits))
        qc.x(range(self.nqubits))
        qc.barrier(range(self.nqubits))
        qc.h(self.nqubits - 1)
        qc.mcx(list(range(self.nqubits - 1)), self.nqubits - 1)
        qc.h(self.nqubits - 1)
        qc.barrier(range(self.nqubits))
        qc.x(range(self.nqubits))
        qc.h(range(self.nqubits))
        
        return qc.to_instruction()


#    Step	                                    Action	                                        Purpose
#1️⃣ Apply Hadamard Gates	            Create superposition of states	                Prepare all possibilities
#2️⃣ Apply Grover’s Oracle	            Mark state where number_1 ≥ number_2	        Identify the correct state
#3️⃣ Apply Diffuser	                    Amplify the marked state	                    Increase its probability
#4️⃣ Measure	                        Collapse quantum state into classical value	    Obtain final result
#5️⃣ Find Most Likely State	            Identify the highest probability outcome	    Select the best answer
#6️⃣ Return Result	                    True if number_1 ≥ number_2, else False	        Provide final comparison
    def check_larger_or_equal(self):
        """
        Check if the first number is larger than or equal to the second number
        using Grover's algorithm.
        """
        # Apply Hadamard to create superposition
        self.qc.h(range(self.nqubits)) #This applies Hadamard gates to all qubits, creating an equal superposition of all possible quantum states.
        #Purpose: Ensures that all possible states (representing different comparisons) have an equal probability before the search begins.
        
        # Grover iterations
        niterations = int(np.floor(np.pi / 4 * np.sqrt(self.nstates)))
        for _ in range(niterations):
            self.qc.append(self.create_comparison_oracle(), range(self.nqubits))
            self.qc.append(self.create_diffuser(), range(self.nqubits))
        
        self.qc.measure_all()
        
        # Simulate the circuit
        sampler = Sampler()
        result = sampler.run(self.qc).result()
        counts = result.quasi_dists[0]
        
        # Find the most likely outcome
        max_key = None
        max_value = float('-inf')
        for key, value in counts.items():
            if value > max_value:
                max_key = key
                max_value = value
        
        # Return True if the condition is satisfied, else False
        return self.diff >= 0
