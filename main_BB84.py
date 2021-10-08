#---------------------------------------------------------------------
# QKD: RELIABLE LOWER BOUND FOR P&M - BB84 PROTOCOL SIMULATION
#---------------------------------------------------------------------
    #
    #   AUTHOR:
    #       Sebastiano Cocchi
    #
    #   LENGUAGE:
    #       Python 3
    #
    #   DESCRIPTION:
    #      "THIS SCRIPT FINDS A RELIABLE LOWER BOUND FOR THE SECRET 
    #       KEY RATE OF THE BB84 PROTOCOL WITH TWO MUBs IN THE PREPARE 
    #       AND MEASURE (P&M) SCHEME.
    #       TO RECOVER THE ENTANGLED-BASED (EB) SCHEMES SECURITY
    #       PROOF, SOURCE-REPLACEMENT SCHEME IS PERFORMED (A 
    #       BRIEF DESCRIPTION IS PRESENTED HERE BELOW).
    #       LOWER BOUND IS FOUND FIRSTLY CALCULATING THE MINIMUM OF THE 
    #       RELATIVE ENTROPY BETWEEN THE STATE (SHARED BY ALICE AND
    #       BOB) AND THE STATE AFTER THE ALICE HOLDS HIS RAW KEY.
    #       THIS WILL FIND THE WORST CASE SCENARIO IN WHICH EVE HOLD A 
    #       PURIFICATION OF THE QUBIT.
    #       THUS, THE PROBLEM IS CONVERTED INTO A MAXIMIZATION PROBLEM OF 
    #       FORMER THE FUNCTION.
    #       THE CLASS OF THESE MINIMIZATIONS/MAXIMIZATIONS IS SEMIDEFINITE
    #       PROBLEMS (SDP).
    #       THE TWO RESULTS MAY BE VERY CLOSE TO EACH OTHER AND PROVIDE A
    #       RELIABLE LOWER BOUND ON THE KEY RATE."
    #
    #   FURTHER READINGS CAN BE FOUND AT:
    #       https://doi.org/10.22331/q-2018-07-26-77
    #       https://doi.org/10.1103/PhysRevResearch.3.013274
    #
    #   PACKAGES REQUIRED:
    #    * numpy
    #    * scipy
    #    * cvxpy (with solvers CVXOPT, it can be obtained by 'pip install cvxopt')
    #    * matplotlib
    #
    #   SYMBOLS INDEX:
    #    1)  .x. = tensor product
    #    2)  .+. = direct sum
    #    3)  **+ = hermitian conjugate
    #    4)  .T  = matrix transpose
    #    5)  s.t.= such that
    #
#---------------------------------------------------------------------
# EB AND P&M SCHEMES:
#---------------------------------------------------------------------
    # " An entangled state composed of two photons is created.
    #   One particle is given to Alice, one to Bob.
    #   Both perform a measurment in one of the two bases."
    #
    #              |Psi>          
    #   Alice <______|______>   Bob    
    #   
    # Prepare and Measure (P&M) scheme:
    # " Alice prepares a qubit and sends it to Bob."
    #
#---------------------------------------------------------------------
# SOURCE-REPLACEMENT SCHEME for P&M BB84:
#---------------------------------------------------------------------
    # P&M schemes can be seen as EB schemes using the
    # so-called Source-Replacement scheme in which Alice
    # can choose between {|0>,|1>} and {|+>,|->}.
    # She create an entangled state psi_AA', where A is a
    # register in H^4 and A' is the register in which is encoded the bit,
    # so it is a H^2.
    #
    #
    #   SCHEME:
    #
    #                                            ........Eve............
    #   ..............Alice............          : U_E=I_A.0.E_A'(rho) :         .......Bob.......
    #   :               |PHI>_AA'     :          :........../\.........:         :    A' --> B   :
    #   :   ________________/\________:____________________/  \__________________:_______________
    #   :   A:{0,1,2,3}H^2      A':{0,1,+,-}H^2                                  :B:{0,1,+,-}H^2 :
    #   :       dim=4           dim=2 :                                          :     dim=2     :
    #   :        |                    :                                          :       |       :
    #   :        V                    :                                          :       V       :
    #   :      POVM_A                 :                                          :    POVM_B     :
    #   :.............................:                                          :...............:
    #
    #   STATE A    : STATE A'(B') : BASIS CHOICE : BIT VALUE 
    #       |0>    :     |0>      :      Z       :     0
    #       |1>    :     |1>      :      Z       :     1
    #       |2>    :     |+>      :      X       :     0
    #       |3>    :     |->      :      X       :     1
    #
#---------------------------------------------------------------------
# PROCEDURE, CALCULATION AND ALGORITHM
#---------------------------------------------------------------------
    #   PROCEDURE:
    #    1- Alice creates the states:
    #           |psi>_AA' = sum_i p_i |i>_A .o. |phi_i>_A'
    #    2- Alice sends the qubit A' via quantum channel;
    #    3- ANNOUNCEMENT PHASE:
    #       POVMA and POVMB are the POVM of Alice and Bob, by which are
    #       defined Bob announcement
    #            KB_b = \sum_{\beta_b} \sqrt{POVMB^{b,\beta_b}} .o. |b>_{\tilde{B}} .o. |\beta_b>_{\bar{B}}
    #       where \tilde{B} and \bar{B} are the announcement, and the second index denotes a particular
    #       element associated with that announcement.
    #       Alice announcement is
    #            KA_a = \sum_{\alpha_a} \sqrt{POVMA^{a,\alpha_a}} .o. |a>_{\tilde{A}} .o. |\alpha_a>_{\bar{A}}
    #       The action of KA and Kb on the state \rho is
    #           rho_2 = \sum_{a,b} ( KA_a .o. KB_b ).\rho.( KA_a .o. KB_b )**+
    #                 = A(\rho)
    #   4- SIFTING PHASE:
    #       viewed as a projector of the form
    #           Proj = \sum_{a,b} |a><a|_{\tilde{A}} .o. |b><b|_{\tilde{B}} 
    #       and identities elsewhere.
    #   5- KEY MAP:
    #       write the key map as the function g(a, \alpha_a, b). We deﬁne an isometry V that stores the key
    #       information in a register system R, as follows
    #           V = \sum_{a, \alpha_a, b} |g(a, \alpha_a, b)>_R .0. |a><a|_{\tilde{A}} .o. |\alpha_a><\alpha_a|_{\bar{A}} .o. |b><b|_{\tilde{B}}
    #   6- PINCHING CHANNEL:
    #       decohere the register in order to obtain a classical register R
    #           Z(\sigma) = \sum_j (|j><j|_R .o. I ).\sigma.(|j><j|_R .o. I )
    #       where I denotes the identity acting on the other subsystems.
    #   
    #   CALCULATION:
    #    1- construct the state rho_AB;
    #    2- quantum channel acting on rho_AB (like depolarization, etc.);
    #    3- define the CP map as:
    #       G(\rho) = V . proj . A(\rho) . proj . V**+
    #    4- define the pinching channel as
    #       Z(\rho) = \sum_j (|j><j|_R .o. I ).\sigma.(|j><j|_R .o. I )
    #    5- construct the basis of operators
    #           Gamma_i = POVM_i
    #       and find the Gram-Schmidt process for them.
    #    6- enlarge the basis using THeta_j complete set for A s.t.
    #           Tr[ \Theta_j \rho_AB] = \theta_j      
    #    7- calculation of the constraints:
    #           p_i = Tr[POVM_i . \rho_AB]
    #
    #   ALGORITHM:
    #    1- set counter=0, epsilon, maxit and rho_0 as starting point using the Gamma_tilde
    #           rho_0 = \sum_i gamma_tilde_i Gamma_tilde_i  +  \sum_j  omega_j  Omega_j
    #   STEP 1
    #    2- calculate
    #           f(\rho) = D( G(\rho_0) || Z(G(\rho_0)) )
    #       where 
    #           D(\rho||\sigma) = Tr[ \rho. log(\rho) ] - Tr[ \rho. log(\sigma) ]
    #       is the Relative Entropy.
    #    3- calculate the gradient of this function
    #           grad_f(\rho).T = G**+(log(G(\rho))) + G**+(log(Z(G(\rho))))
    #    4- minimize  : \Delta rho = arg min _{\delta rho} [ (\delta rho).T grad_f(\rho_0) ]
    #       subject to: constraints p_i.
    #    IF: Tr[ (\Delta rho).T . grad_f(\rho_0) ] < \epsilon and GOTO STEP 2
    #    ELSE: find tt \in [0, 1] s.t. minimize f( \rho_0 + tt*\Delta rho )
    #    5- encrease the counter by 1 and set \rho_0 = \rho_0 + tt*\Delta rho
    #       for the next iteration and repeat from 2-.
    #    IF: counter == maxit GOTO STEP 2.
    #           
    #   STEP 2
    #    0- from STEP 1 we know \rho and its gradient
    #    1- maximize : gamma_i.y 
    #      subject to: sum_j y_j Gamma_j <= grad_f(\rho)
    #   
    #   LOWER BOUND:
    #    the result is:
    #      f(rho) - Tr( rho . grad_f(rho) ) + max{gamma_i.y }
    #
#---------------------------------------------------------------------
# The program is diveded in two parts:
#   1) explanation of the conceptual steps of the procedure and
#      the declaration of the usefule operators;
#   2) the algorithm procedure implementing the operators defined in 
#      the previous point and SDP minimization procedure.
# N.B.: the algorithm is a recursive iteration incrementing the depolarization
#       probability.
#---------------------------------------------------------------------
# PART 1): definition of the operators
#---------------------------------------------------------------------

import numpy as np
from scipy.linalg import sqrtm
from src import qkd
import matplotlib.pyplot as plt
import time

start_time = time.time()

# parameters
da = 4
db = 2
dtot = da*db
nst = 4
epsilon = 1e-10
Pz = 0.5
start, stop, step = 0., 0.12, 3
maxit = 1000
finesse = 5
solver_name = "MOSEK"

# define states
states = [qkd.zero, qkd.one, qkd.plus, qkd.minus]
basis = np.eye(da)

# ALICE probabilities
Px = (1. - Pz)
ProbAlice = [Pz, Pz/2., Px/2., Px/2.]
if (np.sum(ProbAlice) != 1): print("ProbAlice != 1")

# BOB porbabilities
BS = [0.7, 0.3] # beamsplitter
ProbBob = [BS[0]/2., BS[0]/2., BS[1]/2., BS[1]/2.]
if (np.sum(ProbBob) != 1): print("ProbBob != 1")

#  post selection and probability of passing the post selection process
postselect_prob = [Pz*BS[0], Px*BS[1]]
ppass = sum(postselect_prob)

# local measurments (|0><0|, |1><1|, |+><+| and |-><-|)
sigma_00 = np.outer( states[0], np.conj(states[0]) )
sigma_11 = np.outer( states[1], np.conj(states[1]) )
sigma_pp = np.outer( states[2], np.conj(states[2]) )
sigma_mm = np.outer( states[3], np.conj(states[3]) )

# define identities for convinience
id_a = np.eye(da)
id_b = np.eye(db)
id_tot = np.eye(dtot)
id_2 = np.eye(2)
id_4 = np.eye(4)
id_8 = np.eye(8)
id_64 = np.eye(64)
id_128 = np.eye(128)

# After the qubit sending, Alice can measure A using the POVM
POVMA = [
    np.outer( basis[0], np.conj(basis[0]) ),
    np.outer( basis[1], np.conj(basis[1]) ),
    np.outer( basis[2], np.conj(basis[2]) ),
    np.outer( basis[3], np.conj(basis[3]) )
]
# which have dimension 4-by-4 and satisfy POVM properties
if ( np.allclose(sum([ ii for ii in POVMA]), id_a ) == False ): print("sum POVMA**+ POVMA != 1", sum([ ii for ii in POVMA]) )
for ii in POVMA:
    if(np.allclose( np.conj(ii).T, ii) == False ): print("POVMA NOT hermitian")
    if(np.all( np.linalg.eigvals(ii) < -1e-8)): print("POVMA is NEGATIVE")

# On the other hand, Bob can measure using the POVM
POVMB = [
    0.5*sigma_00,
    0.5*sigma_11,
    0.5*sigma_pp,
    0.5*sigma_mm
]
# which have dimension 2-by-2 and satisfy POVM properties
if ( np.allclose(sum([ii for ii in POVMB]), id_b ) == False ): print("sum POVMB**+ POVMB != 1", sum([ ii for ii in POVMB]) )
for ii in POVMB:
    if(np.allclose( np.conj(ii).T, ii) == False ): print("POVMB NOT hermitian")
    if(np.all( np.linalg.eigvals(ii) < - 1e-8)): print("POVMB is NEGATIVE")

# The POVM of the entire system is given by
POVM = []
for ii in POVMA:
        for jj in POVMB:
            temp = np.kron( ii, jj )
            POVM.append( temp )
# which have dimension 8-by-8 and satisfy POVM properties
if ( np.all(sum([ np.conj(ii).T @ ii for ii in POVM]) != id_tot ) ): print("sum POVM**+ POVM != 1",[np.conj(ii).T @ ii for ii in POVM])
for ii in POVM:
    if(np.allclose( np.conj(ii).T, ii) == False ): print("POVM NOT hermitian")
    if(np.all( np.linalg.eigvals(ii) < - 1e-8)): print("POVM is NEGATIVE")

# PUBLIC ANNOUNCEMENT:
#   kraus operators of A dim = 16-by-4
KA = [ np.kron( sqrtm(POVMA[0]), np.kron(qkd.zero[:, np.newaxis], qkd.zero[:, np.newaxis])) +
       np.kron( sqrtm(POVMA[1]), np.kron(qkd.zero[:, np.newaxis], qkd.one[:, np.newaxis])),
       np.kron( sqrtm(POVMA[2]), np.kron(qkd.one[:, np.newaxis] , qkd.zero[:, np.newaxis])) +
       np.kron( sqrtm(POVMA[3]), np.kron(qkd.one[:, np.newaxis] , qkd.one[:, np.newaxis]))
]
#   which satisfy Kraus property
if ( np.allclose( np.sum([ np.conj(ii).T @ ii for ii in KA]), id_a) ): print("sum KA**+ KA != 1", sum([ np.conj(ii).T @ ii for ii in KA]) )
#   kraus operators of B dim = 8-by-4
KB = [ np.kron(sqrtm(POVMB[0]), np.kron(qkd.zero[:, np.newaxis], qkd.zero[:, np.newaxis])) +
       np.kron(sqrtm(POVMB[1]), np.kron(qkd.zero[:, np.newaxis], qkd.one[:, np.newaxis])),
       np.kron(sqrtm(POVMB[2]), np.kron(qkd.one[:, np.newaxis] , qkd.zero[:, np.newaxis])) +
       np.kron(sqrtm(POVMB[3]), np.kron(qkd.one[:, np.newaxis] , qkd.one[:, np.newaxis]))
]
#   which satisfy Kraus property
if ( np.allclose(np.sum([ np.conj(ii).T @ ii for ii in KB]), id_b ) ): print("sum KB**+ KB != 1", sum([ np.conj(ii).T @ ii for ii in KB]) )
#   The total Kraus representation of the Public Announcement is
K = []
for ii in KA:
        for jj in KB:
            K.append( np.kron(ii, jj))
#   which satisfy Kraus property
if ( np.allclose(np.sum([ np.conj(ii).T @ ii for ii in K]), id_tot ) ): print("sum K**+ K != 1", sum([ np.conj(ii).T @ ii for ii in K]) )

# SIFTING PHASE:
#   acts like a projector with dimension 128-by-128
proj = np.kron( id_a, np.kron( sigma_00, np.kron( np.kron(id_2, id_b), np.kron( sigma_00, id_2 ))) ) +\
       np.kron( id_a, np.kron( sigma_11, np.kron( np.kron(id_2, id_b), np.kron( sigma_11, id_2 ))) )

# KEY MAP:
#   is a isometry which creates a new register R which stores the information on the bits
#   and it is a 258-by-258 matrix
V = np.kron( qkd.zero[:, np.newaxis], np.kron( np.kron(id_a, id_2), np.kron( sigma_00, np.kron(id_b, id_4)) )) +\
    np.kron( qkd.one[:, np.newaxis] , np.kron( np.kron(id_a, id_2), np.kron( sigma_11, np.kron(id_b, id_4)) ))

# PINCHING CHANNEL:
#   decohere the register R. It has the effect of making R a classical register
pinching = [ np.kron( sigma_00 , np.kron( np.kron(id_a, np.kron( id_4, id_b )), id_4 )),
             np.kron( sigma_11 , np.kron( np.kron(id_a, np.kron( id_4, id_b )), id_4 )) ]

# this set is used to extend POVM_tilde to a basis
Omega = []
Omega_ab = []
for ii in range(4):
    for jj in range(4):
        M = 0.5 * np.kron(qkd.pauli[ii], qkd.pauli[jj])
        #check for hermiticity
        if(np.allclose(M, np.conj(M).T) == False): print("Gamma", ii, jj, "not hermitian.")
        #check if is a Tr[G_mu G_mu]==1
        if( abs(np.trace(M @ M) - 1.) >= 1e-8): print("Tr[G_mu G_mu] != 1", np.trace(M @ M))
        Omega.append( M )
        for kk in range(4):
            Omega_ab.append( np.kron(M,qkd.pauli[kk]) )

# new simulation
sim = qkd.QKD(4, 2 ,4, basis, ProbAlice, states, ProbBob)
sim.set_povm(POVM)
sim.set_public_string_announcement(K)
sim.set_sifting_phase_postselection(proj)
sim.set_key_map(V)
sim.set_pinching_channel(pinching)
sim.set_operator_basis_a(Omega)
sim.set_operator_basis_ab(Omega_ab)
sim.get_full_hermitian_operator_basis()

qber = np.linspace(start, stop, step)

key_th      = []
key_primal  = []
key_dual    = []

# numerical
for ii in qber:
    print("\n QBER =", ii)

    # theorical
    hp = qkd.binary_entropy(ii)

    # apply quantum channel
    sim.apply_quantum_channel(qkd.depolarizing_channel(2*ii))

    # set constraints
    gamma = []
    for jj in sim.orth_set_a:
        gamma.append(np.trace( jj @ sim.rho_ab))
    for jj in sim.povm:
        gamma.append(np.trace( jj @ sim.rho_ab))
    sim.set_constraints(gamma, np.concatenate([sim.orth_set_a, sim.povm]))

    # compute primal and dual problem
    sim.compute_primal(epsilon, maxit, finesse)
    sim.compute_dual(solver_name="MOSEK")

    key_th.append(1 - 2*hp)
    key_primal.append( sim.primal_sol - hp)
    key_dual.append( sim.dual_sol - hp)

    print("--- --- --- --- --- --- --- --- ---")
    print(" step 1 =", sim.primal_sol)
    print(" step 2 =", sim.dual_sol)

print( "\n CPU time: ", time.time() - start_time, "s")

fig, ax = plt.subplots(figsize=(20, 11))
ax.plot(qber, key_th, "--", linewidth=1.2, alpha=0.5, label="theorical")
ax.plot(qber, key_primal, "o", alpha=0.5, label="step 1")
ax.plot(qber, key_dual, ".", alpha=0.5, label="step 2")
plt.xlabel("QBER")
plt.ylabel("Secret key rate")
plt.title("Reliable lower bound P&M BB84 with public announcement and sifting")
plt.ylim([0., None])
plt.xlim([0., None])
plt.legend(loc='best')
plt.grid()
plt.savefig("analysis/test_"+str(100*Pz)+".png")
plt.show()
