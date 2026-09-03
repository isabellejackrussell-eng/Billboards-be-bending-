import numpy as np

# =====================================================================
# Euler-Bernoulli vs Timoshenko comparison
# Reuses the same 7-element frame, materials and geometry as the main
# analysis. Solves the frame under the max rated wind speed (FoS=2.5
# case) using both formulations and compares tip + per-element
# deflections.
# =====================================================================

# -----------------------------------
# Structure and Material Properties
# -----------------------------------
def beta(A, L, I):
    return (A * L**2) / I

E_mod = 200e9
G_mod = 77e9

L1 = np.sqrt(0.33**2 + 0.25**2); alpha1 = 0.9224
L2 = 0.25;                        alpha2 = 0.0
L3 = np.sqrt(0.17**2 + 0.125**2); alpha3 = 0.9224
L4 = 0.375;                       alpha4 = 0.0
L5 = np.sqrt(0.375**2 + 0.5**2);  alpha5 = 0.9224
L6 = 0.5;                         alpha6 = 1.57
L7 = 0.5;                         alpha7 = 1.57

I_sec = 1.688115e-6
A_sec = 1.492257e-3

Ls = [L1, L2, L3, L4, L5, L6, L7]
alphas = [alpha1, alpha2, alpha3, alpha4, alpha5, alpha6, alpha7]
As_gross = [A_sec] * 7
Is = [I_sec] * 7
betas = [beta(A_sec, L, I_sec) for L in Ls]

Assembly1 = np.array([[0,0,0,1,0,0],[0,0,0,0,1,0],[0,0,0,0,0,1]] + [[0]*6]*12)
Assembly2 = np.array([[0,0,0,1,0,0],[0,0,0,0,1,0],[0,0,0,0,0,1]] + [[0]*6]*12)
Assembly3 = np.array([[1,0,0,0,0,0],[0,1,0,0,0,0],[0,0,1,0,0,0],
                       [0,0,0,1,0,0],[0,0,0,0,1,0],[0,0,0,0,0,1]] + [[0]*6]*9)
Assembly4 = np.array([[0]*6]*3 + [[1,0,0,0,0,0],[0,1,0,0,0,0],[0,0,1,0,0,0],
                       [0,0,0,1,0,0],[0,0,0,0,1,0],[0,0,0,0,0,1]] + [[0]*6]*6)
Assembly5 = np.array([[0]*6]*3 + [[1,0,0,0,0,0],[0,1,0,0,0,0],[0,0,1,0,0,0]] +
                      [[0]*6]*3 + [[0,0,0,1,0,0],[0,0,0,0,1,0],[0,0,0,0,0,1]] + [[0]*6]*3)
Assembly6 = np.array([[0]*6]*6 + [[1,0,0,0,0,0],[0,1,0,0,0,0],[0,0,1,0,0,0],
                       [0,0,0,1,0,0],[0,0,0,0,1,0],[0,0,0,0,0,1]] + [[0]*6]*3)
Assembly7 = np.array([[0]*6]*9 + [[1,0,0,0,0,0],[0,1,0,0,0,0],[0,0,1,0,0,0],
                       [0,0,0,1,0,0],[0,0,0,0,1,0],[0,0,0,0,0,1]])
Assemblies = [Assembly1, Assembly2, Assembly3, Assembly4, Assembly5, Assembly6, Assembly7]

# -----------------------------------
# Core FEA functions
# -----------------------------------
def local_frame_EB(E, I, L, beta):
    return (E * I / L**3) * np.array([
        [beta, 0, 0, -beta, 0, 0],
        [0, 12, 6*L, 0, -12, 6*L],
        [0, 6*L, 4*L**2, 0, -6*L, 2*L**2],
        [-beta, 0, 0, beta, 0, 0],
        [0, -12, -6*L, 0, 12, -6*L],
        [0, 6*L, 2*L**2, 0, -6*L, 4*L**2]])

def local_frame_Timoshenko(E, I, L, beta, G, As):
    Phi = (12 * E * I) / (G * As * L**2)
    f = 1 / (1 + Phi)
    Ke = (E * I / L**3) * np.array([
        [beta, 0, 0, -beta, 0, 0],
        [0, 12*f, 6*L*f, 0, -12*f, 6*L*f],
        [0, 6*L*f, (4+Phi)*L**2*f, 0, -6*L*f, (2-Phi)*L**2*f],
        [-beta, 0, 0, beta, 0, 0],
        [0, -12*f, -6*L*f, 0, 12*f, -6*L*f],
        [0, 6*L*f, (2-Phi)*L**2*f, 0, -6*L*f, (4+Phi)*L**2*f]])
    return Ke, Phi

def transform_matrix(alpha):
    c, s = np.cos(alpha), np.sin(alpha)
    lam = np.array([[c, s, 0], [-s, c, 0], [0, 0, 1]])
    z = np.zeros((3, 3))
    return np.block([[lam, z], [z, lam]])

def global_frame(K, alpha):
    Lambda = transform_matrix(alpha)
    return Lambda.T @ K @ Lambda, Lambda

def global_stiffness(Assembly, K_hat):
    return Assembly @ K_hat @ Assembly.T

def displacements(Q, KG):
    return np.linalg.solve(KG, Q)

def global_deflections(Assembly, q):
    return Assembly.T @ q

def element_deflections(Lambda, D):
    return Lambda @ D

def UDL_frame_f_eq(w_bar, L):
    return np.array([[0], [w_bar*L/2], [w_bar*L**2/12],
                      [0], [w_bar*L/2], [-w_bar*L**2/12]])

def Axial_UDL_frame_f_eq(p_bar, L):
    return np.array([[p_bar*L/2], [0], [0], [p_bar*L/2], [0], [0]])

def F_eq(Lambda, f_eq):
    return Lambda.T @ f_eq

def Q_eq(Assembly, F_eq):
    return Assembly @ F_eq

def global_udl_to_local(w_gx, w_gy, alpha):
    c, s = np.cos(alpha), np.sin(alpha)
    p_bar = c*w_gx + s*w_gy
    w_bar = -s*w_gx + c*w_gy
    return p_bar, w_bar

# -----------------------------------
# Wind load setup (FoS = 2.5 rated speed)
# Update V_max below if your own script gives a different value.
# -----------------------------------
sign_depth = 3.0
V_max = 62.2567          # m/s, from the FoS=2.5 calculation
pressure = 0.6 * V_max**2
w_UDL = pressure * sign_depth
w_gx, w_gy = -w_UDL, 0.0

def solve_case(As_list):
    """Builds K, K_hat, KG for every element using the given shear-area
    list, solves under the wind UDL on elements 6 and 7 (index 5, 6),
    and returns q, per-element local deflections d[], and Phi values."""
    Ks, Phis = [], []
    for i in range(7):
        if As_list is None:
            Ks.append(local_frame_EB(E_mod, Is[i], Ls[i], betas[i]))
            Phis.append(0.0)
        else:
            K, Phi = local_frame_Timoshenko(E_mod, Is[i], Ls[i], betas[i], G_mod, As_list[i])
            Ks.append(K)
            Phis.append(Phi)

    K_hats, Lambdas = [], []
    for i in range(7):
        Kh, Lam = global_frame(Ks[i], alphas[i])
        K_hats.append(Kh)
        Lambdas.append(Lam)

    KG_Total = sum(global_stiffness(Assemblies[i], K_hats[i]) for i in range(7))

    p6, wb6 = global_udl_to_local(w_gx, w_gy, alpha6)
    p7, wb7 = global_udl_to_local(w_gx, w_gy, alpha7)
    feq6 = Axial_UDL_frame_f_eq(p6, L6) + UDL_frame_f_eq(wb6, L6)
    feq7 = Axial_UDL_frame_f_eq(p7, L7) + UDL_frame_f_eq(wb7, L7)
    Qeq6 = Q_eq(Assembly6, F_eq(Lambdas[5], feq6))
    Qeq7 = Q_eq(Assembly7, F_eq(Lambdas[6], feq7))
    Q_total = Qeq6 + Qeq7

    q = displacements(Q_total, KG_Total)
    Ds = [global_deflections(Assemblies[i], q) for i in range(7)]
    ds = [element_deflections(Lambdas[i], Ds[i]) for i in range(7)]
    return q, ds, Phis

# Euler-Bernoulli (As_list = None -> uses local_frame_EB)
q_EB, d_EB, _ = solve_case(None)

# Timoshenko (shear area for hollow circular section, per course notes)
As_shear = [2 * A / np.pi for A in As_gross]
q_T, d_T, Phis = solve_case(As_shear)

# -----------------------------------
# Results
# -----------------------------------
print(f"V_max = {V_max:.4f} m/s ({V_max*3.6:.2f} km/h)")
print()
print("Phi (shear parameter) per element:")
for i, p in enumerate(Phis, start=1):
    print(f"  Element {i}: Phi = {p:.5f}")

print()
print("Tip (node G) deflection comparison:")
print(f"  Euler-Bernoulli: X={q_EB[12,0]*1000:.4f} mm, Y={q_EB[13,0]*1000:.4f} mm, theta={q_EB[14,0]:.6e} rad")
print(f"  Timoshenko:      X={q_T[12,0]*1000:.4f} mm, Y={q_T[13,0]*1000:.4f} mm, theta={q_T[14,0]:.6e} rad")
dx = (q_T[12,0]-q_EB[12,0])*1000
dy = (q_T[13,0]-q_EB[13,0])*1000
dth = q_T[14,0]-q_EB[14,0]
print(f"  Change:          dX={dx:.4f} mm, dY={dy:.4f} mm, dtheta={dth:.6e} rad")

print()
print("Per-element deflection comparison (transverse Delta_v = d5-d2, rotational Delta_theta = d6-d3):")
for i in range(7):
    dv_EB = (d_EB[i][4,0] - d_EB[i][1,0]) * 1000
    dth_EB = d_EB[i][5,0] - d_EB[i][2,0]
    dv_T = (d_T[i][4,0] - d_T[i][1,0]) * 1000
    dth_T = d_T[i][5,0] - d_T[i][2,0]
    print(f"  Element {i+1}: EB dv={dv_EB:.4f} mm, dtheta={dth_EB:.6e} rad | "
          f"Timoshenko dv={dv_T:.4f} mm, dtheta={dth_T:.6e} rad | "
          f"Change dv={dv_T-dv_EB:.5f} mm, dtheta={dth_T-dth_EB:.3e} rad")
