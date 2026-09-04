"""
part3_timoshenko.py
================================================================
ENME302 Assignment #1 - Sensitivity to the Euler-Bernoulli assumption
(Timoshenko frame element formulation)

Rebuilds the structure using the Timoshenko element formulation (brief's
Table 2), which adds shear deformation on top of the Euler-Bernoulli
bending already used everywhere else, and compares the two at the maximum
rated wind speed found in Part 2 (V_max, FoS = 2.5):

  - how much the TIP (node G) deflection changes when shear deformation is
    included
  - a per-element table of the change in each element's own transverse
    deflection (d5^e - d2^e) and end-to-end rotation (d6^e - d3^e), the
    exact quantities the brief asks for

Both models (Euler-Bernoulli and Timoshenko) are built with the same
generic assemble_structure() helper from frame_model.py, from the SAME
geometry/section/Assembly matrices - only the element formulation differs
(local_frame vs local_frame_timoshenko, selected via each element's
'timoshenko_Phi' key).

Requires frame_model.py and part2_distributed_wind.py in the same folder.
See DESCRIPTION.md for the full write-up of the method and what the
comparison means physically.
"""
import numpy as np
from frame_model import *
from part2_distributed_wind import get_V_max, sign_depth

ELEMENT_NAMES = [('1', 'S1', 'C'), ('2', 'S2', 'C'), ('3', 'C', 'D'),
                  ('4', 'D', 'E'), ('5', 'D', 'F'), ('6', 'E', 'F'), ('7', 'F', 'G')]

L_list = [L1, L2, L3, L4, L5, L6, L7]
alpha_list = [alpha1, alpha2, alpha3, alpha4, alpha5, alpha6, alpha7]
Assembly_list = [Assembly1, Assembly2, Assembly3, Assembly4, Assembly5, Assembly6, Assembly7]
A_list = [A1, A2, A3, A4, A5, A6, A7]
I_list = [I1, I2, I3, I4, I5, I6, I7]
E_list = [E1, E2, E3, E4, E5, E6, E7]


def make_elements(use_timoshenko):
    """Build the elements list (see frame_model.assemble_structure) for
    either the Euler-Bernoulli (use_timoshenko=False) or Timoshenko
    (use_timoshenko=True) formulation, from the SAME geometry/section."""
    elements = []
    for i in range(7):
        e = {'E': E_list[i], 'I': I_list[i], 'A': A_list[i], 'L': L_list[i],
             'alpha': alpha_list[i], 'Assembly': Assembly_list[i]}
        if use_timoshenko:
            As = AS_SECTION   # brief's formula: As = 2A/pi, same for every element (same section)
            e['timoshenko_Phi'] = timoshenko_phi(E_list[i], I_list[i], G_STEEL, As, L_list[i])
        elements.append(e)
    return elements


def solve_udl_case(built, KG_Total, V_ms, depth=sign_depth):
    """Solve this structure (EB or Timoshenko - 'built' is whichever
    assemble_structure() produced) under the wind UDL on elements 6 & 7,
    at wind speed V_ms. Mirrors part2_distributed_wind.solve_wind_case(),
    generalised to work with either formulation's 'built' element list."""
    pressure = 0.6 * V_ms**2
    w_udl = pressure * depth
    w_gx, w_gy = -w_udl, 0.0

    e6, e7 = built[5], built[6]
    p6, wb6 = global_udl_to_local(w_gx, w_gy, e6['alpha'])
    p7, wb7 = global_udl_to_local(w_gx, w_gy, e7['alpha'])
    feq6 = Axial_UDL_frame_f_eq(p6, e6['L']) + UDL_frame_f_eq(wb6, e6['L'])
    feq7 = Axial_UDL_frame_f_eq(p7, e7['L']) + UDL_frame_f_eq(wb7, e7['L'])
    Qeq6 = Q_eq(e6['Assembly'], F_eq(e6['Lambda'], feq6))
    Qeq7 = Q_eq(e7['Assembly'], F_eq(e7['Lambda'], feq7))
    Q_total = Qeq6 + Qeq7

    q = displacements(Q_total, KG_Total)
    D = [global_deflections(e['Assembly'], q) for e in built]
    d = [element_deflections(e['Lambda'], Dv) for e, Dv in zip(built, D)]
    return q, D, d


if __name__ == "__main__":
    V_max, _ = get_V_max()
    print(f"Comparing at V_max = {V_max:.3f} m/s (the FoS=2.5 rated wind speed found in Part 2)\n")

    # ============================================================
    # Build and solve both models at the SAME wind speed
    # ============================================================
    eb_elements, KG_eb = assemble_structure(make_elements(use_timoshenko=False))
    ti_elements, KG_ti = assemble_structure(make_elements(use_timoshenko=True))

    q_eb, D_eb, d_eb = solve_udl_case(eb_elements, KG_eb, V_max)
    q_ti, D_ti, d_ti = solve_udl_case(ti_elements, KG_ti, V_max)

    print("Timoshenko shear-flexibility parameter Phi per element (Phi=0 would")
    print("recover Euler-Bernoulli exactly - the brief's formula, Phi = 12EI/(G As L^2)):")
    for i, (name, n1, n2) in enumerate(ELEMENT_NAMES):
        print(f"  element {name} ({n1}-{n2}): Phi = {ti_elements[i]['timoshenko_Phi']:.6f}")
    print()

    # ============================================================
    # Tip (node G) deflection comparison
    # ============================================================
    print("================================================================")
    print("Tip deflection at node G (top of structure)")
    print("================================================================")
    Gx_eb, Gy_eb, Gth_eb = q_eb[12, 0], q_eb[13, 0], q_eb[14, 0]
    Gx_ti, Gy_ti, Gth_ti = q_ti[12, 0], q_ti[13, 0], q_ti[14, 0]
    mag_eb = np.hypot(Gx_eb, Gy_eb)
    mag_ti = np.hypot(Gx_ti, Gy_ti)

    print(f"  Euler-Bernoulli: X={Gx_eb*1000:.4f} mm, Y={Gy_eb*1000:.4f} mm, "
          f"|d|={mag_eb*1000:.4f} mm, theta={Gth_eb:.6e} rad")
    print(f"  Timoshenko:      X={Gx_ti*1000:.4f} mm, Y={Gy_ti*1000:.4f} mm, "
          f"|d|={mag_ti*1000:.4f} mm, theta={Gth_ti:.6e} rad")
    print(f"  Change (Timoshenko - Euler-Bernoulli):")
    print(f"    dX = {(Gx_ti-Gx_eb)*1000:+.4f} mm  ({(Gx_ti-Gx_eb)/Gx_eb*100:+.3f}% of EB's X)")
    print(f"    dY = {(Gy_ti-Gy_eb)*1000:+.4f} mm  ({(Gy_ti-Gy_eb)/Gy_eb*100:+.3f}% of EB's Y)")
    print(f"    d|d| = {(mag_ti-mag_eb)*1000:+.4f} mm  ({(mag_ti-mag_eb)/mag_eb*100:+.3f}% of EB's |d|)")
    print()

    # ============================================================
    # Per-element table: transverse deflection (d5-d2) and rotation
    # change (d6-d3) within each element, EB vs Timoshenko (0-indexed:
    # d[1]=d2 (v at node1), d[4]=d5 (v at node2), d[2]=d3 (theta1), d[5]=d6 (theta2))
    # ============================================================
    print("================================================================")
    print("Per-element transverse deflection (d5-d2) and rotation change (d6-d3)")
    print("================================================================")
    header = f"  {'elem':<6}{'EB: d5-d2 (mm)':>16}{'Ti: d5-d2 (mm)':>16}{'change (%)':>12}   {'EB: d6-d3 (rad)':>17}{'Ti: d6-d3 (rad)':>17}{'change (%)':>12}"
    print(header)
    for i, (name, n1, n2) in enumerate(ELEMENT_NAMES):
        v_eb = (d_eb[i][4, 0] - d_eb[i][1, 0])
        v_ti = (d_ti[i][4, 0] - d_ti[i][1, 0])
        th_eb = (d_eb[i][5, 0] - d_eb[i][2, 0])
        th_ti = (d_ti[i][5, 0] - d_ti[i][2, 0])
        v_pct = (v_ti - v_eb) / v_eb * 100 if abs(v_eb) > 1e-12 else float('nan')
        th_pct = (th_ti - th_eb) / th_eb * 100 if abs(th_eb) > 1e-12 else float('nan')
        print(f"  {name:<6}{v_eb*1000:16.5f}{v_ti*1000:16.5f}{v_pct:12.2f}   "
              f"{th_eb:17.6e}{th_ti:17.6e}{th_pct:12.2f}")

    print()
    print("(Phi values and the %-change columns above are what to base the brief's")
    print("'is the Euler-Bernoulli assumption valid for this structure' discussion on -")
    print("see DESCRIPTION.md for how to read them.)")
