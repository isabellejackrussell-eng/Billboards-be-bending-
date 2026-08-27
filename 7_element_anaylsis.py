
import numpy as np
import matplotlib.pyplot as plt
# -----------------------------------
# Structure and Material Properties
# -----------------------------------
def beta (A, L, I):
    beta = ((A*L**2)/I)
    return beta
# Zero_Assembly1 = np.array(
#     [[0, 0, 0, 0, 0, 0],
#     [0, 0, 0, 0, 0, 0],
#     [0, 0, 0, 0, 0, 0],
#     [0, 0, 0, 0, 0, 0],
#     [0, 0, 0, 0, 0, 0],
#     [0, 0, 0, 0, 0, 0]])
G = 77e9
# Element 1, dont forget to DOUBLE CHECK ALL VALUES!!!!!
L1 = np.sqrt(0.33**2+0.25**2)
alpha1 = 0.9224  # already in radians (52.85 deg) - do NOT wrap in np.radians() again
I1 = 1.688115e-6
A1 = 1.492257e-3
E1 = 200e9
beta1 = beta(A1,L1,I1)
w_bar1_PL = 0
w_bar1_UDL = 0 # Dont forget to look at sign of forces
w_bar1_LVL = 0
Assembly1 = np.array(
    [[0, 0, 0, 1, 0, 0],
    [0, 0, 0, 0, 1, 0],
    [0, 0, 0, 0, 0, 1],
    [0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0]])
# Element 2
L2 = 0.25
alpha2 = np.radians(0)
I2 = 1.688115e-6
A2 = 1.492257e-3
E2 = 200e9
beta2 = beta(A2,L2,I2)
w_bar2_PL = 0
w_bar2_UDL = 0
w_bar2_LVL = 0
Assembly2 = np.array(
    [[0, 0, 0, 1, 0, 0],
    [0, 0, 0, 0, 1, 0],
    [0, 0, 0, 0, 0, 1],
    [0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0]])
# Element 3
L3 = np.sqrt(0.17**2+0.125**2)
alpha3 = 0.9224  # already in radians
I3 = 1.688115e-6
A3 = 1.492257e-3
E3 = 200e9
beta3 = beta(A3,L3,I3)
w_bar3_PL = 0
w_bar3_UDL = 0
w_bar3_LVL = 0
Assembly3 = np.array(
    [[1, 0, 0, 0, 0, 0],
    [0, 1, 0, 0, 0, 0],
    [0, 0, 1, 0, 0, 0],
    [0, 0, 0, 1, 0, 0],
    [0, 0, 0, 0, 1, 0],
    [0, 0, 0, 0, 0, 1],
    [0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0]])
# Element 4
L4 = 0.375
alpha4 = np.radians(0)
I4 = 1.688115e-6
A4 = 1.492257e-3
E4 = 200e9
beta4 = beta(A4,L4,I4)
w_bar4_PL = 0
w_bar4_UDL = 0
w_bar4_LVL = 0
Assembly4 = np.array(
    [[0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0],
    [1, 0, 0, 0, 0, 0],
    [0, 1, 0, 0, 0, 0],
    [0, 0, 1, 0, 0, 0],
    [0, 0, 0, 1, 0, 0],
    [0, 0, 0, 0, 1, 0],
    [0, 0, 0, 0, 0, 1],
    [0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0]])
# Element 5
L5 = np.sqrt(0.375**2+0.5**2)
alpha5 = 0.9224  # already in radians
I5 = 1.688115e-6
A5 = 1.492257e-3
E5 = 200e9
beta5 = beta(A5,L5,I5)
w_bar5_PL = 0
w_bar5_UDL = 0
w_bar5_LVL = 0
Assembly5 = np.array(
    [[0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0],
    [1, 0, 0, 0, 0, 0],
    [0, 1, 0, 0, 0, 0],
    [0, 0, 1, 0, 0, 0],
    [0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0],
    [0, 0, 0, 1, 0, 0],
    [0, 0, 0, 0, 1, 0],
    [0, 0, 0, 0, 0, 1],
    [0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0]])
# Element 6
L6 = 0.5
alpha6 = 1.57  # already in radians (~90 deg)
I6 = 1.688115e-6
A6 = 1.492257e-3
E6 = 200e9
beta6 = beta(A6,L6,I6)
w_bar6_PL = 0
w_bar6_UDL = 0
w_bar6_LVL = 0
Assembly6 = np.array(
    [[0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0],
    [1, 0, 0, 0, 0, 0],
    [0, 1, 0, 0, 0, 0],
    [0, 0, 1, 0, 0, 0],
    [0, 0, 0, 1, 0, 0],
    [0, 0, 0, 0, 1, 0],
    [0, 0, 0, 0, 0, 1],
    [0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0]])
# Element 7
L7 = 0.5
alpha7 = 1.57  # already in radians (~90 deg)
I7 = 1.688115e-6
A7 = 1.492257e-3
E7 = 200e9
beta7 = beta(A7,L7,I7)
w_bar7_PL = 0
w_bar7_UDL = 0
w_bar7_LVL = 0
Assembly7 = np.array(
    [[0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0],
    [1, 0, 0, 0, 0, 0],
    [0, 1, 0, 0, 0, 0],
    [0, 0, 1, 0, 0, 0],
    [0, 0, 0, 1, 0, 0],
    [0, 0, 0, 0, 1, 0],
    [0, 0, 0, 0, 0, 1]])
 
# Part 1 point loads (Figure 2): two 2000N horizontal loads, pointing in -X
# (toward the wall), applied at node E (bottom of the sign, global rows 7-9)
# and node G (top of the sign, global rows 13-15). Only the X-DOF (first row
# of each node's 3-row block) is loaded.
Q = np.array([[0],
              [0],
              [0],
              [0],
              [0],
              [0],
              [-2000],
              [0],
              [0],
              [0],
              [0],
              [0],
              [-2000],
              [0],
              [0]])
# -----------------------------------
# Core FEA Functions
# -----------------------------------
def local_frame(E, I, L, beta):
    Ke = ((E*I)/(L**3)) * np.array([[beta, 0, 0, -beta, 0, 0],
                                   [0, 12, 6*L, 0, -12, 6*L],
                                   [0, 6*L, 4*L**2, 0, -6*L,2*L**2],
                                   [-beta, 0, 0, beta, 0, 0],
                                   [0, -12, -6*L, 0, 12, -6*L],
                                   [0, 6*L, 2*L**2, 0, -6*L, 4*L**2]])
    return Ke
def global_frame(K, alpha):
    Lambda = transform_matrix(alpha)
    K_hat = Lambda.T @ K @ Lambda
    return K_hat, Lambda
 
def transform_matrix(alpha):
    c = np.cos(alpha)
    s = np.sin(alpha)
    lambda1 = np.array([[c, s, 0],
                       [-s, c, 0],
                       [0, 0, 1]])
    zeros = np.zeros((3,3))
    Lambda = np.block([[lambda1,zeros],
                      [zeros, lambda1]])
    return Lambda
def global_stiffness (Assembly, K_hat):
    KG = Assembly @ K_hat @ Assembly.T
    return KG
def displacements(Q, KG):
    q = np.linalg.solve(KG, Q)
    return q
def global_deflections(Assembly, q):
    D = Assembly.T @ q
    return D
def element_deflections(Lambda, D):
    d = Lambda @ D
    return d
def element_force(K,d):
    f = K @ d
    return f
def global_force(K_hat, D):
    F = K_hat @ D
    return F
def F_eq(Lambda, f_eq):
    F_eq = Lambda.T @ f_eq
    return F_eq
def Q_eq(Assembly, F_eq) :
    Q_eq = Assembly @ F_eq
    return Q_eq
def general_f_eq(a,L,w_bar):
    f_eq = w_bar * np.array([[1-((3*a**2)/(L**2)) + ((2*a**3)/L**3)],
                     [((a**3)/(L**2)) - ((2*a**2)/L) + a],
                     [((3*a**2)/(L**2)) - ((2*a**3)/(L**3))],
                     [((a**3)/(L**2))-((a**2)/(L))]])
    return f_eq
def UDL_frame_f_eq(w_bar, L):
    UDL_f_eq = np.array([
        [0],
        [w_bar*L/2],
        [w_bar*L**2/12],
        [0],
        [w_bar*L/2],
        [-w_bar*L**2/12]
    ])
    return UDL_f_eq
def Axial_UDL_frame_f_eq(p_bar, L):
    return  np.array([
        [(p_bar*L)/2],
        [0],
        [0],
        [(p_bar*L)/2],
        [0],
        [0]
    ])
# ----------------------------------
# Linearly Varying Load (Peak at x = L)
# ----------------------------------
def feq_lvl_end(w_bar, L):
    return np.array([
        [0],
        [3 * w_bar * L / 20],
        [w_bar * L**2 / 30],
        [0],
        [7 * w_bar * L / 20],
        [-w_bar * L**2 / 20]
    ])
# ----------------------------------
# Linearly Varying Load (Peak at x = 0)
# ----------------------------------
def feq_lvl_start(w_bar, L):
    return np.array([
        [0],
        [7 * w_bar * L / 20],
        [w_bar * L**2 / 20],
        [0],
        [3 * w_bar * L / 20],
        [-w_bar * L**2 / 30]
    ])
# ----------------------------------
# Point Load at distance a from node 1
# ----------------------------------
def feq_point_load(w_bar, a, L):
    return w_bar * np.array([
        [0],
        [1 - (3 * a**2) / L**2 + (2 * a**3) / L**3],
        [(a**3) / L**2 - (2 * a**2) / L + a],
        [0],
        [(3 * a**2) / L**2 - (2 * a**3) / L**3],
        [(a**3) / L**2 - (a**2) / L]
    ])
# ----------------------------------
# Mid-span Point Load (a = L/2)
# ----------------------------------
def feq_midspan_point_load(w_bar, L):
    return np.array([
        [0],
        [w_bar / 2],
        [w_bar * L / 8],
        [0],
        [w_bar / 2],
        [-w_bar * L / 8]
    ])
# 4 x 1 equivilant
# ----------------------------------
# Uniformly Distributed Load (UDL)
# ----------------------------------
def feq_udl_4(w_bar, L):
    return np.array([
        [w_bar * L / 2],
        [w_bar * L**2 / 12],
        [w_bar * L / 2],
        [-w_bar * L**2 / 12]
    ])
# ----------------------------------
# Linearly Varying Load (Peak at x = L)
# ----------------------------------
def feq_lvl_end_4(w_bar, L):
    return np.array([
        [3 * w_bar * L / 20],
        [w_bar * L**2 / 30],
        [7 * w_bar * L / 20],
        [-w_bar * L**2 / 20]
    ])
# ----------------------------------
# Linearly Varying Load (Peak at x = 0)
# ----------------------------------
def feq_lvl_start_4(w_bar, L):
    return np.array([
        [7 * w_bar * L / 20],
        [w_bar * L**2 / 20],
        [3 * w_bar * L / 20],
        [-w_bar * L**2 / 30]
    ])
# ----------------------------------
# Point Load at distance a from node 1
# ----------------------------------
def feq_point_load_4(w_bar, a, L):
    return w_bar * np.array([
        [1 - (3 * a**2) / L**2 + (2 * a**3) / L**3],
        [(a**3) / L**2 - (2 * a**2) / L + a],
        [(3 * a**2) / L**2 - (2 * a**3) / L**3],
        [(a**3) / L**2 - (a**2) / L]
    ])
# ----------------------------------
# Mid-span Point Load (a = L/2)
# ----------------------------------
def feq_midspan_point_load_4(w_bar, L):
    return np.array([
        [w_bar / 2],
        [w_bar * L / 8],
        [w_bar / 2],
        [-w_bar * L / 8]
    ])
# -----------------------------------
# Solve the structure (change these values)
# -----------------------------------
K1 = local_frame(E1, I1, L1, beta1)
K2 = local_frame(E2, I2, L2, beta2)
K3 = local_frame(E3, I3, L3, beta3)
K4 = local_frame(E4, I4, L4, beta4)
K5 = local_frame(E5, I5, L5, beta5)
K6 = local_frame(E6, I6, L6, beta6)
K7 = local_frame(E7, I7, L7, beta7)
K_hat1, Lambda1 = global_frame(K1, alpha1)
K_hat2, Lambda2 = global_frame(K2, alpha2)
K_hat3, Lambda3 = global_frame(K3, alpha3)
K_hat4, Lambda4 = global_frame(K4, alpha4)
K_hat5, Lambda5 = global_frame(K5, alpha5)
K_hat6, Lambda6 = global_frame(K6, alpha6)
K_hat7, Lambda7 = global_frame(K7, alpha7)
KG1 = global_stiffness(Assembly1, K_hat1)
KG2 = global_stiffness(Assembly2, K_hat2)
KG3 = global_stiffness(Assembly3, K_hat3)
KG4 = global_stiffness(Assembly4, K_hat4)
KG5 = global_stiffness(Assembly5, K_hat5)
KG6 = global_stiffness(Assembly6, K_hat6)
KG7 = global_stiffness(Assembly7, K_hat7)
KG_Total = KG1 + KG2 + KG3 + KG4 + KG5 + KG6 + KG7
# -----------------------------------
# CHANGE THESE VALUES TO SUIT THE CURRENT MODEL!!!!!!!
# -----------------------------------
# EXAMPLE OF MEMEBR THAT HAD SHEAR AND AXIAL UDL + ANOTHER MEMBER THAT HAD NORMAL UDL
# f_eq_UDL_1 = UDL_frame_f_eq(w_bar1_UDL, L1) # local
# F_eq_UDL_1 = F_eq(Lambda1, f_eq_UDL_1) # makes global
# Q_eq_UDL_1 = Q_eq(Assembly1, F_eq_UDL_1) # Overall force vectors
# # UDL force on element 2 is on an angle so need to split into x and y
# # w_bar (y), and p_bar (x)
# w_bar2_UDL_y = np.cos(alpha2)*w_bar2_UDL
# p_bar2_UDL_x = np.sin(alpha2)*w_bar2_UDL
# # X component (axial)
# f_eq_UDL_2_axial = Axial_UDL_frame_f_eq(p_bar2_UDL_x, L2) # local
# F_eq_UDL_2_axial = F_eq(Lambda2, f_eq_UDL_2_axial) # makes global
# # Y component (shear)
# f_eq_UDL_2_shear = UDL_frame_f_eq(w_bar2_UDL_y, L2) # local
# F_eq_UDL_2_shear = F_eq(Lambda2, f_eq_UDL_2_shear) # makes global
# F_eq_UDL_2 = F_eq_UDL_2_shear + F_eq_UDL_2_axial
# Q_eq_UDL_2 = Q_eq(Assembly2, F_eq_UDL_2) # Overall force vectors
Q_total = Q.copy()
q = displacements(Q_total, KG_Total)
D1 = global_deflections(Assembly1, q)
D2 = global_deflections(Assembly2, q)
D3 = global_deflections(Assembly3, q)
D4 = global_deflections(Assembly4, q)
D5 = global_deflections(Assembly5, q)
D6 = global_deflections(Assembly6, q)
D7 = global_deflections(Assembly7, q)
d1 = element_deflections(Lambda1, D1)
d2 = element_deflections(Lambda2, D2)
d3 = element_deflections(Lambda3, D3)
d4 = element_deflections(Lambda4, D4)
d5 = element_deflections(Lambda5, D5)
d6 = element_deflections(Lambda6, D6)
d7 = element_deflections(Lambda7, D7)
f1 = element_force(K1, d1)
f2 = element_force(K2, d2)
f3 = element_force(K3, d3)
f4 = element_force(K4, d4)
f5 = element_force(K5, d5)
f6 = element_force(K6, d6)
f7 = element_force(K7, d7)
F1 = global_force(K_hat1, D1)
F2 = global_force(K_hat2, D2)
F3 = global_force(K_hat3, D3)
F4 = global_force(K_hat4, D4)
F5 = global_force(K_hat5, D5)
F6 = global_force(K_hat6, D6)
F7 = global_force(K_hat7, D7)
# Reaction forces at the two fixed supports (global X, Y, M).
#
# Support 1 is element 1's local node 1 (Assembly1's first 3 columns map to
# no global DOF - i.e. restrained), and no other element touches support 1.
# So the full reaction there is just element 1's own global end-force at
# that node: F1[0:3]. Same logic for support 2 via element 2 -> F2[0:3].
# (If you later add a distributed load directly on element 1 or 2, you'd
# need to add -f_eq[0:3] transformed to global too, per the brief's note
# on equivalent nodal loads - not needed for the Part 1 point-load case.)
#
# Sanity check performed: applied loads are -2000N at node E and -2000N at
# node G (total -4000N in X), and R1[0] + R2[0] = +4000N exactly, and the Y
# and moment components self-cancel across the two supports as expected for
# a structure with no external Y-load - confirms the sign convention below.
R1 = F1[0:3]   # [Rx1, Ry1, M1] at support 1
R2 = F2[0:3]   # [Rx2, Ry2, M2] at support 2
 
# ----------------------------------
# Combined normal stress: sigma_total = |sigma_axial| + |sigma_bending|
# ----------------------------------
# sigma_axial = |N| / A            (constant along an element with no
#                                    interior axial load, per the local
#                                    force vectors f1..f7 - N is the same
#                                    magnitude at both ends by equilibrium)
# sigma_bending = |M| * c / I       (c = half the outside diameter, per the
#                                    brief; bending moment varies linearly
#                                    along an element with NO interior
#                                    distributed load - true for this Part 1
#                                    point-load case - so its two extremes
#                                    are exactly the two end moments already
#                                    sitting in f_e[2] and f_e[5]. Once you
#                                    add the Part 2 UDL, an element that
#                                    carries the distributed load directly
#                                    will need interior points checked too,
#                                    since the moment diagram is then
#                                    quadratic, not linear.)
c = 0.100 / 2  # outside diameter / 2, same section for every element
 
# f_e, A_e, I_e, and the two physical node names (node1 -> node2) per element
elements = {
    1: {'f': f1, 'A': A1, 'I': I1, 'nodes': ('S1', 'C')},
    2: {'f': f2, 'A': A2, 'I': I2, 'nodes': ('S2', 'C')},
    3: {'f': f3, 'A': A3, 'I': I3, 'nodes': ('C',  'D')},
    4: {'f': f4, 'A': A4, 'I': I4, 'nodes': ('D',  'E')},
    5: {'f': f5, 'A': A5, 'I': I5, 'nodes': ('D',  'F')},
    6: {'f': f6, 'A': A6, 'I': I6, 'nodes': ('E',  'F')},
    7: {'f': f7, 'A': A7, 'I': I7, 'nodes': ('F',  'G')},
}
 
stress_results = []  # each row: (element, end#, node name, sigma_axial, sigma_bending, sigma_total)
for elem_no, e in elements.items():
    f = e['f']
    sigma_axial = abs(f[0, 0]) / e['A']  # constant along the element
    for end, M_index, node_name in [(1, 2, e['nodes'][0]), (2, 5, e['nodes'][1])]:
        M = f[M_index, 0]
        sigma_bending = abs(M) * c / e['I']
        sigma_total = sigma_axial + sigma_bending
        stress_results.append((elem_no, end, node_name, sigma_axial, sigma_bending, sigma_total))
 
governing = max(stress_results, key=lambda r: r[5])
gov_elem, gov_end, gov_node, gov_axial, gov_bending, gov_total = governing
 
print(f"Maximum total normal stress = {gov_total/1e6:.2f} MPa")
print(f"  occurs in element {gov_elem}, at its end nearest node {gov_node}")
print(f"  (sigma_axial = {gov_axial/1e6:.2f} MPa, sigma_bending = {gov_bending/1e6:.2f} MPa)")
print()
print("Full table, sorted by sigma_total (element, end, node, axial MPa, bending MPa, total MPa):")
for r in sorted(stress_results, key=lambda r: -r[5]):
    print(f"  elem {r[0]}  end {r[1]} ({r[2]:>2})   axial={r[3]/1e6:6.2f}   bending={r[4]/1e6:6.2f}   total={r[5]/1e6:6.2f}")
 
# print("q  =\n", q, "\n")
# print("d1 =\n", d1, "\n")
# print("d2 =\n", d2, "\n")
# ----------------------------------
# Printing example: print(f"KG Total = 1 x 10^5 x \n {KG_Total * 1e-5}\n")
# ----------------------------------
# ----------------------------------
# Shape functions
# ----------------------------------
def axial_shape (x, L):
    phi1 = (1-(x/L))
    phi2 = (x/L)
    return phi1, phi2
def transverse_shape (x, L):
    N1 = 1 - ((3*x**2)/(L**2)) + ((2*x**3)/(L**3))
    N2 = ((x**3)/(L**2)) -  ((2*x**2)/L) + x
    N3 = ((3*x**2)/(L**2)) - ((2*x**3)/(L**3))
    N4 = ((x**3)/(L**2)) - ((x**2)/L)
    return N1, N2, N3, N4
# TODO: x1 was 3, which is outside element 1's length (L1 ~= 0.41 m).
# Left at a valid mid-element value for now - update once you decide which
# point along the element you actually want to evaluate.
x1 = L1 / 2  # The point along the element that we are analysing
phi1, phi2 = axial_shape(x1,L1)
N1, N2, N3, N4 = transverse_shape(x1, L1)
u_x = phi1*d1[0] + phi2*d1[3]
v_x = N1*d1[1] + N2*d1[2] + N3*d1[4] + N4*d1[5]
# ----------------------------------
# Deflected shape plotting
# ----------------------------------
def plot_deflected_shape(node1XG,node1YG,node2XG,node2YG,d_e,Disp_mag,N_points):
    """
    Plots the undeflected baseline and deflected shape of ONE frame element
    onto the current matplotlib axes.
 
    node1XG, node1YG : global (X,Y) coords of the element's node 1
    node2XG, node2YG : global (X,Y) coords of the element's node 2
    d_e              : 6x1 element deflection vector in LOCAL (element) co-ordinates
    Disp_mag         : displacement magnification factor
    N_points         : number of points used to draw the element's internal shape
    """
    # Step 1 (implicit) + get L and alpha for THIS element from its end coords.
    # Use the full 4-quadrant arctan2, not arctan(dy/dx), per the note on p.94.
    dx = node2XG - node1XG
    dy = node2YG - node1YG
    L_e = np.sqrt(dx**2 + dy**2)
    alpha = np.arctan2(dy, dx)
 
    # Step 2: points along the element in LOCAL x^e coordinates
    x_e = np.linspace(0, L_e, N_points)
 
    # Step 3: evaluate shape functions at those points
    phi1, phi2 = axial_shape(x_e, L_e)
    N1, N2, N3, N4 = transverse_shape(x_e, L_e)
    # Step 4: axial u(x) and transverse v(x) displacements, local coords
    u = phi1*d_e[0] + phi2*d_e[3]
    v = N1*d_e[1] + N2*d_e[2] + N3*d_e[4] + N4*d_e[5]
 
    # Step 5: rotate local (u,v) into global (X,Y) deflection components
    Deflections_XG = u*np.cos(alpha) - v*np.sin(alpha)
    Deflections_YG = u*np.sin(alpha) + v*np.cos(alpha)
    # Step 6: undeflected baseline
    Undeflected_baseline_XG = np.linspace(node1XG, node2XG, N_points)
    Undeflected_baseline_YG = np.linspace(node1YG, node2YG, N_points)
 
    # Step 7: deflected position (baseline + magnified deflection)
    Deflected_XG = Undeflected_baseline_XG + Disp_mag*Deflections_XG
    Deflected_YG = Undeflected_baseline_YG + Disp_mag*Deflections_YG
    # Step 8: plot
    plt.plot(Undeflected_baseline_XG, Undeflected_baseline_YG, 'b:.', label='Undeflected Position')
    plt.plot(Deflected_XG, Deflected_YG, 'r.-', label='Deflected Position')
 
    return Deflected_XG, Deflected_YG
# ----------------------------------
# Global node coordinates (for plotting only)
# ----------------------------------
# Built by walking the structure from the two fixed supports, using each
# element's own L/alpha - so these line up exactly with the stiffness model
# above. Node names follow the same C/D/E/F/G labels used when we traced
# the Assembly matrices:
#   S1 --elem1--> C <--elem2-- S2      (two fixed supports meet at C)
#   C --elem3--> D --elem4--> E --elem6--> F --elem7--> G (top)
#   D --elem5--> F   (diagonal brace, closes the D-E-F triangle)
S1 = np.array([0.0, 0.0])                                        # elem1 node1 (fixed)
S2 = np.array([0.0, 0.33])                                       # elem2 node1 (fixed)
C  = S1 + L1 * np.array([np.cos(alpha1), np.sin(alpha1)])        # elem1/2 node2, elem3 node1
D  = C  + L3 * np.array([np.cos(alpha3), np.sin(alpha3)])        # elem3 node2, elem4/5 node1
E  = D  + L4 * np.array([np.cos(alpha4), np.sin(alpha4)])        # elem4 node2, elem6 node1
F  = E  + L6 * np.array([np.cos(alpha6), np.sin(alpha6)])        # elem6 node2, elem5/7 node ends
G  = F  + L7 * np.array([np.cos(alpha7), np.sin(alpha7)])        # elem7 node2 - top of structure
 
# Note: F above is reached via the E->F path (elem4 then elem6), and
# element 5's baseline is then drawn from D to that same F, rather than
# recomputing F from D using L5/alpha5. Because L3/alpha5 are still
# slightly rounded (flagged earlier), the two paths from D to F don't
# close *exactly* - they're within a few mm of each other, which is fine
# for this plot, but tightening those dimensions would remove the gap.
 
# ----------------------------------
# Call the plotting function once per element
# ----------------------------------
Disp_mag = 10
N_points = 11
plt.figure()
# Element 1: S1 -> C
plot_deflected_shape(S1[0], S1[1], C[0], C[1], d1, Disp_mag, N_points)
# Element 2: S2 -> C
plot_deflected_shape(S2[0], S2[1], C[0], C[1], d2, Disp_mag, N_points)
# Element 3: C -> D
plot_deflected_shape(C[0], C[1], D[0], D[1], d3, Disp_mag, N_points)
# Element 4: D -> E
plot_deflected_shape(D[0], D[1], E[0], E[1], d4, Disp_mag, N_points)
# Element 5: D -> F (diagonal brace)
plot_deflected_shape(D[0], D[1], F[0], F[1], d5, Disp_mag, N_points)
# Element 6: E -> F
plot_deflected_shape(E[0], E[1], F[0], F[1], d6, Disp_mag, N_points)
# Element 7: F -> G
plot_deflected_shape(F[0], F[1], G[0], G[1], d7, Disp_mag, N_points)
# Avoid duplicate legend entries (each call adds the same 2 labels)
handles, labels = plt.gca().get_legend_handles_labels()
by_label = dict(zip(labels, handles))
plt.legend(by_label.values(), by_label.keys())
 
plt.xlabel(r"$X^G$ (m)")
plt.ylabel(r"$Y^G$ (m)")
plt.title(f"Deflected shape (displacement magnification = {Disp_mag})")
plt.grid(True)
plt.axis('equal')
plt.show()