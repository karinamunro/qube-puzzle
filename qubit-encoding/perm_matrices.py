######################################################################
# Note:
# Must be run on another file

# Status: ok

# Updates:
# Returns the R2, U2 and F2 circuits as unitary matrices

######################################################################

def perm_matrix():

    import pennylane as qml

    qubits = ['w','x','y1','y2','z']

    def R2_circuit():
        qml.X(wires = 'z')
        return qml.state()

    def U2_circuit():
        qml.X(wires = 'y2')
        qml.Toffoli(wires = ['y1','z','y2'])
        qml.Toffoli(wires = ['z','y2','y1'])
        qml.CNOT(wires = ['y1','y2'])
        qml.CNOT(wires = ['y2','y1'])
        qml.X(wires = 'y2')
        qml.X(wires = 'z')
        return qml.state() 

    def F2_circuit():
        qml.X(wires = 'y2')
        qml.CNOT(wires = ['y2','x'])
        qml.Toffoli(wires = ['y1','z','x'])
        qml.Toffoli(wires = ['z','y2','y1'])
        qml.Toffoli(wires = ['y1','z','y2'])
        qml.CNOT(wires = ['y1','w'])
        qml.Toffoli(wires = ['z','y2','w'])
        qml.CNOT(wires = ['y1', 'y2'])
        qml.X(wires = 'y1')
        qml.X(wires = 'z')
        qml.SWAP(wires = ['y1','y2'])
        return qml.state()

    dev = qml.device("default.qubit", wires = qubits)

    # Construct the permutation matrices from the circuits
    R2_qnode = qml.QNode(R2_circuit, dev)
    R2_matrix = qml.matrix(R2_qnode)()

    U2_qnode = qml.QNode(U2_circuit, dev)
    U2_matrix = qml.matrix(U2_qnode)()

    F2_qnode = qml.QNode(F2_circuit, dev)
    F2_matrix = qml.matrix(F2_qnode)()

    return R2_matrix, U2_matrix, F2_matrix