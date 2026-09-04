"""
frame_model.py
================================================================
ENME302 Assignment #1 (2026) - shared FE model for the billboard frame.

This module defines the geometry (from Figure 1's dimensions), material
and section properties, the 7 local stiffness matrices, the coordinate
transforms, and the assembled global stiffness matrix KG_Total - i.e.
everything from the brief's "Modelling and Analysis" section, before any
specific load case is applied.

It also holds the generic direct-stiffness-method functions and
equivalent-nodal-load helper functions reused by every load case.

Import this into a part-specific script with:

    from frame_model import *

See DESCRIPTION.md for the full write-up of the method and what each
result means.
"""
import numpy as np
import matplotlib.pyplot as plt

# ================================================================
# Section / material properties (shared by every element)
# ================================================================
# Circular hollow section: OD = 100mm, ID = 90mm, steel.
E_STEEL = 200e9   # Pa
G_STEEL = 77e9    # Pa
OD = 0.100        # m
ID = 0.090        # m
c = OD / 2        # distance to outermost fibre, for bending stress

A_SECTION = np.pi / 4 * (OD**2 - ID**2)          # m^2
I_SECTION = np.pi / 64 * (OD**4 - ID**4)          # m^4  (was 100x too large
                                                   #       in the original code - fixed)
AS_SECTION = 2 * A_SECTION / np.pi                # m^2 - shear area (brief's
                                                   # formula for a hollow
                                                   # circular section), used
                                                   # by the Timoshenko element
STEEL_DENSITY = 7850   # kg/m^3 - typical structural steel, used for the
                        # material-use comparison in the structural
                        # modification task


def beta(A, L, I):
    return (A * L**2) / I


def timoshenko_phi(E, I, G, As, L):
    """Shear-flexibility parameter Phi for the Timoshenko element (brief's
    Table 2): Phi = 12EI / (G As L^2). Phi = 0 recovers Euler-Bernoulli."""
    return (12 * E * I) / (G * As * L**2)


# ================================================================
# Geometry: 7 elements, from Figure 1's dimensions
# ================================================================
# Two fixed supports on the left (S1 at the base, S2 higher up the wall),
# connected through 5 free nodes: C, D, E, F, G (G is the top of the
# structure, where the sign's UDL/point loads are applied).
#
#   S1 --elem1--> C <--elem2-- S2      (both supports meet at C)
#   C  --elem3--> D --elem4--> E --elem6--> F --elem7--> G  (top)
#   D  --elem5--> F                     (diagonal brace, closes the
#                                        D-E-F triangle)
#
# L, alpha per element - computed EXACTLY via np.arctan2(rise, run) from
# Figure 1's dimensions, rather than typed-in decimal approximations.
#
# IMPORTANT finding from part1_equilibrium_checks.py: earlier versions of
# this file set alpha5 = alpha1 = alpha3 = 0.9224 rad (52.85 deg), on the
# assumption that the diagonal brace (element 5, D->F) is a continuation of
# the same S1-C-D diagonal line. It looks that way in Figure 1, but it
# ISN'T exactly true: element 5 rises 0.5m over a 0.375m run (atan2(0.5,
# 0.375) = 53.13 deg), while elements 1/3 rise 0.33m over 0.25m (atan2
# (0.33, 0.25) = 52.85 deg) - a different slope. Reusing 52.85 deg for
# element 5 was a small but real geometry error: it made the FE model's
# element 5 not quite line up with where D and F actually are. This was
# invisible in every result checked up to that point (deflections,
# reactions Fx/Fy, stresses all still looked sensible - it's only a ~0.3
# degree error), but it showed up as a small, non-zero moment residual in
# the rigid-body equilibrium checks (part1_equilibrium_checks.py) - element
# 5 was the ONLY element that failed its own isolated self-equilibrium
# check, by exactly the amount that then propagated into every subsection
# check downstream of it. That's a good demonstration of why the
# equilibrium check is worth doing: it caught a bug the stress/deflection
# results alone did not reveal. Using exact atan2() throughout (rather than
# rounded decimals like 0.9224 or 1.57) removes this and every other
# rounding-sized residual, so the checks now pass to floating-point
# precision (~1e-9), not just "close enough".
L1 = np.sqrt(0.33**2 + 0.25**2)
alpha1 = np.arctan2(0.33, 0.25)     # 52.85 deg

L2 = 0.25
alpha2 = 0.0

L3 = np.sqrt(0.17**2 + 0.125**2)
alpha3 = np.arctan2(0.17, 0.125)    # 53.75 deg - C->D's OWN rise/run
                                     # (0.17 = 0.5-0.33, 0.125 = 0.375-0.25)

L4 = 0.375
alpha4 = 0.0

L5 = np.sqrt(0.375**2 + 0.5**2)
alpha5 = np.arctan2(0.5, 0.375)     # 53.13 deg - D->F's OWN rise/run
                                     # (fixed: previously wrongly reused
                                     # alpha1/3's 52.85 deg - see note above)

L6 = 0.5
alpha6 = np.pi / 2                  # exactly vertical

L7 = 0.5
alpha7 = np.pi / 2                  # exactly vertical

# Every element shares the same section, so every element uses the same
# A, I - defined once above (A_SECTION, I_SECTION) rather than repeated
# per element.
A1 = A2 = A3 = A4 = A5 = A6 = A7 = A_SECTION
I1 = I2 = I3 = I4 = I5 = I6 = I7 = I_SECTION
E1 = E2 = E3 = E4 = E5 = E6 = E7 = E_STEEL

beta1 = beta(A1, L1, I1)
beta2 = beta(A2, L2, I2)
beta3 = beta(A3, L3, I3)
beta4 = beta(A4, L4, I4)
beta5 = beta(A5, L5, I5)
beta6 = beta(A6, L6, I6)
beta7 = beta(A7, L7, I7)

# ================================================================
# Assembly matrices: map each element's 6 local DOFs to the 15-row
# reduced global DOF vector (5 free nodes x 3 DOF each). A column of all
# zeros means that local DOF belongs to a FIXED support and is simply
# omitted from the system (that's how the boundary conditions are
# applied here, instead of deleting rows/columns from a full matrix).
# ================================================================
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

# ================================================================
# Global node coordinates (for plotting / reporting only - not used by
# the stiffness solve itself, which only needs L and alpha per element)
# ================================================================
S1 = np.array([0.0, 0.0])                                  # elem1 node1 (fixed)
S2 = np.array([0.0, 0.33])                                 # elem2 node1 (fixed)
C = S1 + L1 * np.array([np.cos(alpha1), np.sin(alpha1)])   # elem1/2 node2, elem3 node1
D = C + L3 * np.array([np.cos(alpha3), np.sin(alpha3)])    # elem3 node2, elem4/5 node1
E = D + L4 * np.array([np.cos(alpha4), np.sin(alpha4)])    # elem4 node2, elem6 node1
F = E + L6 * np.array([np.cos(alpha6), np.sin(alpha6)])    # elem6 node2, elem5/7 node ends
G = F + L7 * np.array([np.cos(alpha7), np.sin(alpha7)])    # elem7 node2 - top of structure

# ================================================================
# Core direct-stiffness-method functions
# ================================================================
def local_frame(E, I, L, beta):
    """Euler-Bernoulli frame element stiffness matrix in LOCAL coordinates
    (6x6), matching the brief's Table 2 formula exactly."""
    return (E * I / L**3) * np.array(
        [[beta, 0, 0, -beta, 0, 0],
         [0, 12, 6 * L, 0, -12, 6 * L],
         [0, 6 * L, 4 * L**2, 0, -6 * L, 2 * L**2],
         [-beta, 0, 0, beta, 0, 0],
         [0, -12, -6 * L, 0, 12, -6 * L],
         [0, 6 * L, 2 * L**2, 0, -6 * L, 4 * L**2]])


def local_frame_timoshenko(E, I, L, beta, Phi):
    """Timoshenko frame element stiffness matrix in LOCAL coordinates (6x6),
    matching the brief's Table 2 formula exactly. Adds the shear-flexibility
    parameter Phi (0 recovers the Euler-Bernoulli matrix from local_frame()
    above) - see timoshenko_phi(). Used by part3_timoshenko.py."""
    k = 1 / (1 + Phi)
    return (E * I / L**3) * np.array(
        [[beta, 0, 0, -beta, 0, 0],
         [0, 12 * k, 6 * L * k, 0, -12 * k, 6 * L * k],
         [0, 6 * L * k, (4 + Phi) * L**2 * k, 0, -6 * L * k, (2 - Phi) * L**2 * k],
         [-beta, 0, 0, beta, 0, 0],
         [0, -12 * k, -6 * L * k, 0, 12 * k, -6 * L * k],
         [0, 6 * L * k, (2 - Phi) * L**2 * k, 0, -6 * L * k, (4 + Phi) * L**2 * k]])


def transform_matrix(alpha):
    """6x6 rotation matrix taking a GLOBAL vector to LOCAL element
    coordinates: local = Lambda @ global."""
    c_, s_ = np.cos(alpha), np.sin(alpha)
    lambda1 = np.array([[c_, s_, 0], [-s_, c_, 0], [0, 0, 1]])
    zeros = np.zeros((3, 3))
    return np.block([[lambda1, zeros], [zeros, lambda1]])


def global_frame(K, alpha):
    """Rotate a local element stiffness matrix into global coordinates:
    K_hat = Lambda^T @ K @ Lambda. Also returns Lambda for reuse."""
    Lambda = transform_matrix(alpha)
    K_hat = Lambda.T @ K @ Lambda
    return K_hat, Lambda


def global_stiffness(Assembly, K_hat):
    """Expand one element's global stiffness matrix into the full
    (reduced) global system using its Assembly (Boolean mapping) matrix."""
    return Assembly @ K_hat @ Assembly.T


def build_element(E, I, A, L, alpha, Assembly, timoshenko_Phi=None):
    """Build K (local), K_hat (global), Lambda, and this element's
    contribution KG to the global stiffness matrix, from its raw properties.
    Pass timoshenko_Phi to use the Timoshenko formulation (local_frame_timoshenko)
    instead of Euler-Bernoulli (local_frame). This is the generic, reusable
    version of the element-by-element build done explicitly for the baseline
    7-element model below - used to build ALTERNATIVE structures (different
    topology and/or element formulation) without re-deriving the method.
    See part3_timoshenko.py and part4_structural_modification.py."""
    b = beta(A, L, I)
    if timoshenko_Phi is None:
        K = local_frame(E, I, L, b)
    else:
        K = local_frame_timoshenko(E, I, L, b, timoshenko_Phi)
    K_hat, Lambda = global_frame(K, alpha)
    KG = global_stiffness(Assembly, K_hat)
    return K, K_hat, Lambda, KG


def assemble_structure(elements):
    """elements: list of dicts, one per element, each with keys
    E, I, A, L, alpha, Assembly (mapping that element into a COMMON reduced
    global DOF numbering shared by every element in the list), and
    optionally 'timoshenko_Phi' (omit, or set None, for Euler-Bernoulli).
    Returns (built, KG_Total): 'built' is the same list of dicts with
    K, K_hat, Lambda, KG added to each entry, and KG_Total is their summed
    global stiffness matrix, ready for displacements(Q, KG_Total)."""
    built = []
    KG_Total = None
    for e in elements:
        K, K_hat, Lambda, KG = build_element(
            e['E'], e['I'], e['A'], e['L'], e['alpha'], e['Assembly'],
            timoshenko_Phi=e.get('timoshenko_Phi'))
        entry = dict(e)
        entry.update(K=K, K_hat=K_hat, Lambda=Lambda, KG=KG)
        built.append(entry)
        KG_Total = KG if KG_Total is None else KG_Total + KG
    return built, KG_Total


def structure_mass(elements, density=STEEL_DENSITY):
    """Total steel mass (kg) of a list of elements (each a dict with 'A'
    and 'L' keys, m^2 and m) - mass = density * sum(A_e * L_e)."""
    return density * sum(e['A'] * e['L'] for e in elements)


def moment_about_point(r_ref, r_force, Fx, Fy):
    """2D moment (about the out-of-plane Z axis) of a force (Fx, Fy) GLOBAL
    N applied at global position r_force (m), about reference point r_ref
    (m): M = (r_force - r_ref) x F. Used by the rigid-body free-body
    equilibrium checks (see part1_equilibrium_checks.py) to bring an
    external point load's moment contribution about a cut point into the
    balance, since only a force's own end-moment (from the FEA solution)
    already acts "at" that point with no arm needed - an external force
    applied elsewhere needs its arm accounted for explicitly."""
    dx = r_force[0] - r_ref[0]
    dy = r_force[1] - r_ref[1]
    return dx * Fy - dy * Fx


def displacements(Q, KG):
    """Solve KG @ q = Q for the reduced global nodal displacement vector."""
    return np.linalg.solve(KG, Q)


def global_deflections(Assembly, q):
    """Extract one element's 6x1 global displacement vector from the full
    reduced solution q."""
    return Assembly.T @ q


def element_deflections(Lambda, D):
    """Rotate an element's global displacement vector into local
    coordinates: d = Lambda @ D."""
    return Lambda @ D


def element_force(K, d):
    """Local element end-force vector from local stiffness and local
    displacement: f = K @ d. NOTE: for an element carrying a distributed
    load directly, this must have f_eq subtracted to get the TRUE internal
    force - see Axial_UDL_frame_f_eq / UDL_frame_f_eq below."""
    return K @ d


def global_force(K_hat, D):
    """Global element end-force vector: F = K_hat @ D."""
    return K_hat @ D


def F_eq(Lambda, f_eq):
    """Rotate a local equivalent-nodal-load vector into global
    coordinates: F_eq = Lambda^T @ f_eq."""
    return Lambda.T @ f_eq


def Q_eq(Assembly, F_eq_global):
    """Expand a global equivalent-nodal-load vector into the reduced
    global load vector using the element's Assembly matrix."""
    return Assembly @ F_eq_global


# ================================================================
# Equivalent nodal load formulas (for representing distributed loads as
# statically-equivalent point forces/moments at the element's two nodes -
# needed for Part 2's UDL and any future distributed-load case)
# ================================================================
def UDL_frame_f_eq(w_bar, L):
    """Local fixed-end/equivalent nodal load vector for a UDL of
    magnitude w_bar (local-transverse direction) over a frame element."""
    return np.array([[0], [w_bar * L / 2], [w_bar * L**2 / 12],
                      [0], [w_bar * L / 2], [-w_bar * L**2 / 12]])


def Axial_UDL_frame_f_eq(p_bar, L):
    """Local equivalent nodal load vector for a UNIFORM AXIAL load p_bar
    along a frame element."""
    return np.array([[(p_bar * L) / 2], [0], [0],
                      [(p_bar * L) / 2], [0], [0]])


def general_f_eq(a, L, w_bar):
    return w_bar * np.array(
        [[1 - (3 * a**2) / L**2 + (2 * a**3) / L**3],
         [(a**3) / L**2 - (2 * a**2) / L + a],
         [(3 * a**2) / L**2 - (2 * a**3) / L**3],
         [(a**3) / L**2 - (a**2) / L]])


def feq_lvl_end(w_bar, L):
    """Linearly varying load, peak at x = L."""
    return np.array([[0], [3 * w_bar * L / 20], [w_bar * L**2 / 30],
                      [0], [7 * w_bar * L / 20], [-w_bar * L**2 / 20]])


def feq_lvl_start(w_bar, L):
    """Linearly varying load, peak at x = 0."""
    return np.array([[0], [7 * w_bar * L / 20], [w_bar * L**2 / 20],
                      [0], [3 * w_bar * L / 20], [-w_bar * L**2 / 30]])


def feq_point_load(w_bar, a, L):
    """Point load w_bar at distance a from node 1."""
    return w_bar * np.array(
        [[0], [1 - (3 * a**2) / L**2 + (2 * a**3) / L**3],
         [(a**3) / L**2 - (2 * a**2) / L + a],
         [0], [(3 * a**2) / L**2 - (2 * a**3) / L**3],
         [(a**3) / L**2 - (a**2) / L]])


def feq_midspan_point_load(w_bar, L):
    return np.array([[0], [w_bar / 2], [w_bar * L / 8],
                      [0], [w_bar / 2], [-w_bar * L / 8]])


def global_udl_to_local(w_global_x, w_global_y, alpha):
    """Project a UDL given as a GLOBAL force-per-length vector into local
    axial (p_bar) and transverse (w_bar) components for an element at
    orientation alpha, using the same convention as transform_matrix()."""
    c_, s_ = np.cos(alpha), np.sin(alpha)
    p_bar = c_ * w_global_x + s_ * w_global_y
    w_bar = -s_ * w_global_x + c_ * w_global_y
    return p_bar, w_bar


def moment_along_element(M1, M2, w_bar, L, N_points=101):
    """True bending moment M(x) in local coordinates along an element,
    given its TRUE end moments M1, M2 (after subtracting f_eq, if the
    element carries a distributed load) and the local-transverse UDL
    magnitude w_bar acting on it (0 if none). w_bar=0 collapses this to
    plain linear interpolation between the end moments.
    Validated against a cantilever loaded only by a UDL w: reduces to the
    standard M(s) = -w*s^2/2 measured from the free end.
    """
    x = np.linspace(0, L, N_points)
    M = M1 * (1 - x / L) + M2 * (x / L) + (w_bar / 2) * x * (L - x)
    return x, M


# ================================================================
# Shape functions + deflected-shape plotting utility
# ================================================================
def axial_shape(x, L):
    phi1 = 1 - (x / L)
    phi2 = x / L
    return phi1, phi2


def transverse_shape(x, L):
    N1 = 1 - (3 * x**2) / L**2 + (2 * x**3) / L**3
    N2 = (x**3) / L**2 - (2 * x**2) / L + x
    N3 = (3 * x**2) / L**2 - (2 * x**3) / L**3
    N4 = (x**3) / L**2 - (x**2) / L
    return N1, N2, N3, N4


def plot_deflected_shape(node1XG, node1YG, node2XG, node2YG, d_e, Disp_mag, N_points):
    """Plot the undeflected baseline and deflected shape of ONE frame
    element onto the current matplotlib axes, using cubic Hermite shape
    functions and the element's real global end coordinates."""
    dx = node2XG - node1XG
    dy = node2YG - node1YG
    L_e = np.sqrt(dx**2 + dy**2)
    alpha = np.arctan2(dy, dx)

    x_e = np.linspace(0, L_e, N_points)
    phi1, phi2 = axial_shape(x_e, L_e)
    N1, N2, N3, N4 = transverse_shape(x_e, L_e)

    u = phi1 * d_e[0] + phi2 * d_e[3]
    v = N1 * d_e[1] + N2 * d_e[2] + N3 * d_e[4] + N4 * d_e[5]

    Deflections_XG = u * np.cos(alpha) - v * np.sin(alpha)
    Deflections_YG = u * np.sin(alpha) + v * np.cos(alpha)

    Undeflected_baseline_XG = np.linspace(node1XG, node2XG, N_points)
    Undeflected_baseline_YG = np.linspace(node1YG, node2YG, N_points)

    Deflected_XG = Undeflected_baseline_XG + Disp_mag * Deflections_XG
    Deflected_YG = Undeflected_baseline_YG + Disp_mag * Deflections_YG

    plt.plot(Undeflected_baseline_XG, Undeflected_baseline_YG, 'b:.', label='Undeflected Position')
    plt.plot(Deflected_XG, Deflected_YG, 'r.-', label='Deflected Position')
    return Deflected_XG, Deflected_YG


def plot_structure_deflected_shape(d1, d2, d3, d4, d5, d6, d7, Disp_mag=10, N_points=11, title=""):
    """Plot all 7 elements' deflected shapes on one figure, given their
    local deflection vectors d1..d7 for whichever load case was solved."""
    plt.figure()
    plot_deflected_shape(S1[0], S1[1], C[0], C[1], d1, Disp_mag, N_points)
    plot_deflected_shape(S2[0], S2[1], C[0], C[1], d2, Disp_mag, N_points)
    plot_deflected_shape(C[0], C[1], D[0], D[1], d3, Disp_mag, N_points)
    plot_deflected_shape(D[0], D[1], E[0], E[1], d4, Disp_mag, N_points)
    plot_deflected_shape(D[0], D[1], F[0], F[1], d5, Disp_mag, N_points)
    plot_deflected_shape(E[0], E[1], F[0], F[1], d6, Disp_mag, N_points)
    plot_deflected_shape(F[0], F[1], G[0], G[1], d7, Disp_mag, N_points)
    handles, labels = plt.gca().get_legend_handles_labels()
    by_label = dict(zip(labels, handles))
    plt.legend(by_label.values(), by_label.keys())
    plt.xlabel(r"$X^G$ (m)")
    plt.ylabel(r"$Y^G$ (m)")
    plt.title(title or f"Deflected shape (displacement magnification = {Disp_mag})")
    plt.grid(True)
    plt.axis('equal')


# ================================================================
# Assemble the global stiffness matrix (shared by every load case)
# ================================================================
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


if __name__ == "__main__":
    # Running this file directly just confirms the model builds cleanly
    # and prints a quick summary - it doesn't apply any load case (see
    # part1_point_loading.py / part2_distributed_wind.py for that).
    print("Frame model built OK.")
    print(f"A = {A_SECTION:.6e} m^2, I = {I_SECTION:.6e} m^4")
    print("Node coordinates (m):")
    for name, pt in [('S1', S1), ('S2', S2), ('C', C), ('D', D), ('E', E), ('F', F), ('G', G)]:
        print(f"  {name}: ({pt[0]:.4f}, {pt[1]:.4f})")
    print(f"KG_Total shape: {KG_Total.shape}")
