"""
part1_point_loading.py
================================================================
ENME302 Assignment #1 - Part 1: Point Loading at Nodal Points

Applies the two 2000N horizontal point loads from Figure 2, solves for
deflections, extracts support reactions, and computes the combined normal
stress (axial + bending) in every element to find the governing (max)
stress location.

The solve itself lives in solve_part1() so other files (currently
part1_equilibrium_checks.py) can reuse these exact results without
re-solving the model or re-running this file's prints/plots. Running this
file directly (python part1_point_loading.py) prints the full results and
shows the deflected-shape plot, same as before.

Requires frame_model.py in the same folder.
See DESCRIPTION.md for the full write-up of the method and what the
results below mean physically.
"""
import numpy as np
from frame_model import *


def solve_part1():
    """Solve the Part 1 point-load case. Returns a dict with the reduced
    global solution q, per-element GLOBAL end-force vectors F (index 0..6
    for elements 1..7 - used for equilibrium/reaction checks), per-element
    LOCAL end-force vectors f (used for the stress calculation - no f_eq
    correction needed since Part 1 has no distributed loads), the two
    support reactions R1/R2, and the full stress table."""
    # Load vector: two 2000N horizontal loads pointing in -X (toward the
    # wall), applied at node E (bottom of the sign, global rows 7-9) and
    # node G (top of the sign, global rows 13-15) - see Figure 2. Only the
    # X-DOF (first row of each node's 3-row block) is loaded.
    Q = np.array([[0], [0], [0], [0], [0], [0],
                  [-2000],
                  [0], [0], [0], [0], [0],
                  [-2000],
                  [0], [0]])

    q = displacements(Q, KG_Total)

    Assemblies = [Assembly1, Assembly2, Assembly3, Assembly4, Assembly5, Assembly6, Assembly7]
    Lambdas = [Lambda1, Lambda2, Lambda3, Lambda4, Lambda5, Lambda6, Lambda7]
    Ks = [K1, K2, K3, K4, K5, K6, K7]
    K_hats = [K_hat1, K_hat2, K_hat3, K_hat4, K_hat5, K_hat6, K_hat7]

    D = [global_deflections(Asm, q) for Asm in Assemblies]
    d = [element_deflections(Lam, Dv) for Lam, Dv in zip(Lambdas, D)]
    # No distributed loads in Part 1, so K@d IS the true internal force,
    # in both local coordinates (f, for stress) and global (F, for
    # reactions/equilibrium checks).
    f = [element_force(K, dv) for K, dv in zip(Ks, d)]
    F = [global_force(K_hat, Dv) for K_hat, Dv in zip(K_hats, D)]

    # ============================================================
    # Reactions at the two fixed supports.
    # Support 1 = element 1's local node 1 (only element touching it), so
    # its reaction is simply F[0][0:3]. Same logic for support 2 via
    # element 2.
    # ============================================================
    R1 = F[0][0:3]   # [Rx1, Ry1, M1] at support 1
    R2 = F[1][0:3]   # [Rx2, Ry2, M2] at support 2

    # ============================================================
    # Combined normal stress: sigma_total = |sigma_axial| + |sigma_bending|
    # c = half the outside diameter. No distributed loads in Part 1, so the
    # bending moment is linear along each element - its two extremes are
    # exactly the two end moments already in f_e[2] and f_e[5], so only the
    # ends need checking (Part 2 needs interior points too - see
    # moment_along_element in frame_model.py).
    # ============================================================
    As_ = [A1, A2, A3, A4, A5, A6, A7]
    Is_ = [I1, I2, I3, I4, I5, I6, I7]
    node_pairs = [('S1', 'C'), ('S2', 'C'), ('C', 'D'), ('D', 'E'),
                  ('D', 'F'), ('E', 'F'), ('F', 'G')]

    stress_results = []
    for idx in range(7):
        fe = f[idx]
        sigma_axial = abs(fe[0, 0]) / As_[idx]
        for end, M_index, node_name in [(1, 2, node_pairs[idx][0]), (2, 5, node_pairs[idx][1])]:
            M = fe[M_index, 0]
            sigma_bending = abs(M) * c / Is_[idx]
            sigma_total = sigma_axial + sigma_bending
            stress_results.append((idx + 1, end, node_name, sigma_axial, sigma_bending, sigma_total))

    governing = max(stress_results, key=lambda r: r[5])

    return {'q': q, 'D': D, 'd': d, 'f': f, 'F': F, 'R1': R1, 'R2': R2,
            'stress_results': stress_results, 'governing': governing}


if __name__ == "__main__":
    results = solve_part1()
    q = results['q']
    d1, d2, d3, d4, d5, d6, d7 = results['d']
    R1, R2 = results['R1'], results['R2']

    print(f"Top of structure (node G) deflection:")
    print(f"  X = {q[12, 0]*1000:.4f} mm")
    print(f"  Y = {q[13, 0]*1000:.4f} mm")
    print(f"  theta = {q[14, 0]:.6e} rad")

    print()
    print("Reactions:")
    print(f"  Support 1: Rx={R1[0,0]:.2f} N, Ry={R1[1,0]:.2f} N, M={R1[2,0]:.2f} N.m")
    print(f"  Support 2: Rx={R2[0,0]:.2f} N, Ry={R2[1,0]:.2f} N, M={R2[2,0]:.2f} N.m")
    print(f"  Equilibrium check: sum(Rx) = {R1[0,0]+R2[0,0]:.4f} N "
          f"(should equal +4000 N, balancing the two -2000N applied loads)")
    print(f"                     sum(Ry) = {R1[1,0]+R2[1,0]:.6f} N (should be ~0)")
    print(f"  (see part1_equilibrium_checks.py for the full overall + subsection")
    print(f"   equilibrium analysis the brief asks for)")

    gov_elem, gov_end, gov_node, gov_axial, gov_bending, gov_total = results['governing']
    print()
    print(f"Maximum total normal stress = {gov_total/1e6:.2f} MPa")
    print(f"  occurs in element {gov_elem}, at its end nearest node {gov_node}")
    print(f"  (sigma_axial = {gov_axial/1e6:.2f} MPa, sigma_bending = {gov_bending/1e6:.2f} MPa)")
    print()
    print("Full table, sorted by sigma_total (element, end, node, axial MPa, bending MPa, total MPa):")
    for r in sorted(results['stress_results'], key=lambda r: -r[5]):
        print(f"  elem {r[0]}  end {r[1]} ({r[2]:>2})   axial={r[3]/1e6:6.2f}   bending={r[4]/1e6:6.2f}   total={r[5]/1e6:6.2f}")

    # ================================================================
    # Plot the deflected shape
    # ================================================================
    plot_structure_deflected_shape(d1, d2, d3, d4, d5, d6, d7, Disp_mag=10,
                                    title="Part 1: deflected shape under the two 2000N point loads")
    plt.show()
