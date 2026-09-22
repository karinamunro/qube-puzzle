######################################################################
# Note:
# Must be run on another file

# Status: ok

# Updates:
# Returns the R2, U2 and F2 circuits as unitary matrices

######################################################################


def perm_matrix():

    from sympy import Matrix
    from sympy.physics.quantum import TensorProduct
    import numpy as np

    X = Matrix([[0, 1], [1, 0]])
    I = Matrix([[1, 0], [0, 1]])
    I3 = Matrix([[1, 0, 0], [0, 1, 0], [0, 0, 1]])
    X3 = Matrix([[0, 0, 1], [1, 0, 0], [0, 1, 0]])
    SUMX_t3_c2 = Matrix([[1,0,0,0,0,0],[0,0,0,0,0,1],[0,0,1,0,0,0],
                    [0,1,0,0,0,0],[0,0,0,0,1,0],[0,0,0,1,0,0]])
    OSUMX_t3_c2 = Matrix([[0,0,0,0,1,0],[0,1,0,0,0,0],[1,0,0,0,0,0],[0,0,0,1,0,0],[0,0,1,0,0,0],[0,0,0,0,0,1]])
    SUMX_t2_c3 = Matrix([[1,0,0,0,0,0],[0,0,0,0,1,0],[0,0,1,0,0,0],[0,0,0,1,0,0],[0,1,0,0,0,0],[0,0,0,0,0,1]])
    SUMX_t2_id2_c3 = Matrix([[1,0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,1,0,0,0,0],[0,0,1,0,0,0,0,0,0,0,0,0],[0,0,0,1,0,0,0,0,0,0,0,0],
                            [0,0,0,0,0,0,0,0,0,0,1,0],[0,0,0,0,0,1,0,0,0,0,0,0],[0,0,0,0,0,0,1,0,0,0,0,0],[0,1,0,0,0,0,0,0,0,0,0,0],
                            [0,0,0,0,0,0,0,0,1,0,0,0],[0,0,0,0,0,0,0,0,0,1,0,0],[0,0,0,0,1,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0,1]])

    a = TensorProduct(I,I,I3,X)
    b = TensorProduct(I,I,X3,I)@TensorProduct(I,I,SUMX_t3_c2)
    d = TensorProduct(I,I,OSUMX_t3_c2)@TensorProduct(I,SUMX_t2_c3,I)@TensorProduct(I,I,X3,I)@TensorProduct(SUMX_t2_id2_c3,I)@TensorProduct(I,I,X3,I)@TensorProduct(X,X,SUMX_t3_c2)

    r = a
    u = a@b
    f = b@a@d

    r_arr = np.asarray(r, dtype=np.complex128)
    u_arr = np.asarray(u, dtype=np.complex128)
    f_arr = np.asarray(f, dtype=np.complex128)

    return r_arr, u_arr, f_arr