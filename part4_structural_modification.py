"""
part4_structural_modification.py
================================================================
ENME302 Assignment #1 - Structural Modifications (open-ended design task)

The brief asks for a modified structure - keeping the two support points
and the sign face (nodes E, F, G) fixed, but free to change anything
between them - and a comparison of how the peak rated wind speed and the
total material use change as a result.

This file builds and compares FOUR designs, all solved the same way
(Euler-Bernoulli, same UDL wind-loading method as Part 2, same FoS = 2.5
against the same 350 MPa yield):

  Baseline   - the original 7-element structure (frame_model.py), for
               reference.
  Design B   - "Braced": ADD one new diagonal element directly from node C
               to node E, in addition to all 7 original elements.
  Design C   - "Lightweight": remove no elements, but CHANGE every existing
               element's tube to a thinner wall (same 100mm OD, larger bore),
               using less material per element.
  Design D   - "Braced (S2-G)": an alternative brace ADDING one new element
               from fixed support S2 straight to the top node G, instead of
               C-E. A second, independently-proposed answer to the same
               open-ended question - see DESCRIPTION.md for how it compares
               to Design B.

Rationale for each (see DESCRIPTION.md for the full discussion):
  Design B targets the stress concentration found in Parts 1 & 2 (element 3
  and the D joint) by giving the base of the vertical mast a second, more
  direct load path from C straight to E, rather than relying entirely on
  the slender D-E outrigger (element 4) and the C-D-F diagonal chain.
  Design C tests the opposite lever: the baseline structure has V_max well
  above the brief's "Very High" wind category (see Part 2's results), which
  suggests there is spare capacity to remove material from instead.
  Design D takes a more direct approach to overall stiffness - one long
  brace spanning almost the full height of the structure - rather than
  targeting the specific C/D stress concentration.

Requires frame_model.py and part2_distributed_wind.py in the same folder.
See DESCRIPTION.md for the full write-up of the results and the rationale
behind each design choice.
"""
import numpy as np
from frame_model import *
from part2_distributed_wind import wind_table, sign_depth, sigma_yield, FoS_required, sigma_allow

ELEM_NAMES_BASE = ['1 (S1-C)', '2 (S2-C)', '3 (C-D)', '4 (D-E)', '5 (D-F)', '6 (E-F)', '7 (F-G)']


def base_elements(A=A_SECTION, I=I_SECTION):
    """The 7 original elements, with a (possibly modified) uniform section
    A, I - everything else (geometry, Assembly matrices) unchanged from
    frame_model.py. Elements 6, 7 stay at list positions 5, 6 in every
    design below, since that's what solve_udl_case() assumes."""
    L_list = [L1, L2, L3, L4, L5, L6, L7]
    alpha_list = [alpha1, alpha2, alpha3, alpha4, alpha5, alpha6, alpha7]
    Assembly_list = [Assembly1, Assembly2, Assembly3, Assembly4, Assembly5, Assembly6, Assembly7]
    return [{'E': E_STEEL, 'I': I, 'A': A, 'L': L_list[i], 'alpha': alpha_list[i],
             'Assembly': Assembly_list[i]} for i in range(7)]


def add_CE_brace(elements, A=A_SECTION, I=I_SECTION):
    """Design B: add element 8, a new diagonal brace directly from node C
    to node E (both already-existing free nodes - no new DOF needed, just
    a new 15x6 Assembly matrix mapping local node1->C, local node2->E)."""
    L8 = np.hypot(*(E - C))
    alpha8 = np.arctan2(E[1] - C[1], E[0] - C[0])
    Assembly8 = np.zeros((15, 6))
    Assembly8[0:3, 0:3] = np.eye(3)   # local node 1 -> C (global rows 0-2)
    Assembly8[6:9, 3:6] = np.eye(3)   # local node 2 -> E (global rows 6-8)
    return elements + [{'E': E_STEEL, 'I': I, 'A': A, 'L': L8, 'alpha': alpha8, 'Assembly': Assembly8}]


def add_S2G_brace(elements, A=A_SECTION, I=I_SECTION):
    """Design D: add element 8, a new diagonal brace from fixed support S2
    directly to node G (top of the mast). S2's end of the brace is fixed
    (like elements 1/2), so only the G end maps into the global DOF."""
    L8 = np.hypot(*(G - S2))
    alpha8 = np.arctan2(G[1] - S2[1], G[0] - S2[0])
    Assembly8 = np.zeros((15, 6))
    Assembly8[12:15, 3:6] = np.eye(3)   # local node 2 -> G (global rows 12-14)
    return elements + [{'E': E_STEEL, 'I': I, 'A': A, 'L': L8, 'alpha': alpha8, 'Assembly': Assembly8}]


def solve_udl_case(built, KG_Total, V_ms, depth=sign_depth, udl_indices=(5, 6)):
    """Solve 'built' (any assemble_structure() elements list where indices
    5 and 6 are elements 6 and 7 - the sign face) under the wind UDL at
    V_ms, and return the full stress table + governing (max) sigma_total.
    Generalises part2_distributed_wind.solve_wind_case() to an arbitrary
    element list/topology, so it works for the baseline AND both modified
    designs without duplicating the method for each."""
    pressure = 0.6 * V_ms**2
    w_udl = pressure * depth
    w_gx, w_gy = -w_udl, 0.0

    feq = {}
    Q_total = np.zeros((KG_Total.shape[0], 1))
    for idx in udl_indices:
        e = built[idx]
        p_bar, w_bar = global_udl_to_local(w_gx, w_gy, e['alpha'])
        feq[idx] = Axial_UDL_frame_f_eq(p_bar, e['L']) + UDL_frame_f_eq(w_bar, e['L'])
        Q_total = Q_total + Q_eq(e['Assembly'], F_eq(e['Lambda'], feq[idx]))
        e['_w_bar'] = w_bar   # stash for the stress loop below

    q = displacements(Q_total, KG_Total)

    results = []
    for idx, e in enumerate(built):
        Dv = global_deflections(e['Assembly'], q)
        dv = element_deflections(e['Lambda'], Dv)
        f_true = e['K'] @ dv
        if idx in feq:
            f_true = f_true - feq[idx]
        sigma_axial = abs(f_true[0, 0]) / e['A']
        w_bar = e.get('_w_bar', 0.0)
        x_vals, M_vals = moment_along_element(f_true[2, 0], f_true[5, 0], w_bar, e['L'])
        sigma_bending_vals = np.abs(M_vals) * c / e['I']
        sigma_total_vals = sigma_axial + sigma_bending_vals
        i_max = int(np.argmax(sigma_total_vals))
        results.append((idx, x_vals[i_max], e['L'], sigma_axial,
                         sigma_bending_vals[i_max], sigma_total_vals[i_max]))

    governing = max(results, key=lambda r: r[5])
    return {'q': q, 'stress_results': results, 'governing': governing, 'sigma_max': governing[5]}


def find_V_max(built, KG_Total, V_ref=None):
    """Same linear-scaling trick as Part 2: solve once at a reference wind
    speed, then scale directly to the FoS=2.5 rated speed (stress is
    exactly proportional to V^2 for a linear elastic model)."""
    if V_ref is None:
        V_ref = np.sqrt(wind_table['Low'] / 0.6)
    case_ref = solve_udl_case(built, KG_Total, V_ref)
    V_max = V_ref * np.sqrt(sigma_allow / case_ref['sigma_max'])
    case_max = solve_udl_case(built, KG_Total, V_max)   # re-solve to confirm
    return V_max, case_ref, case_max


def summarise(label, elements, names):
    built, KG_Total = assemble_structure(elements)
    mass = structure_mass(elements)
    V_max, case_ref, case_max = find_V_max(built, KG_Total)
    gov = case_max['governing']
    print(f"--- {label} ---")
    print(f"  Elements: {len(elements)}   Total steel mass: {mass:.3f} kg")
    print(f"  V_max (FoS={FoS_required}) = {V_max:.3f} m/s ({V_max*3.6:.1f} km/h)")
    print(f"  Governing at V_max: element {names[gov[0]]}, x={gov[1]:.4f} m of "
          f"{gov[2]:.4f} m, sigma_total={gov[5]/1e6:.2f} MPa (should = {sigma_allow/1e6:.1f} MPa)")
    q = case_max['q']
    print(f"  Node G deflection at V_max: X={q[12,0]*1000:.4f} mm, Y={q[13,0]*1000:.4f} mm")
    print()
    return {'label': label, 'mass': mass, 'V_max': V_max, 'q_G': (q[12, 0], q[13, 0])}


if __name__ == "__main__":
    print("================================================================")
    print("Baseline (7 elements, original section - see frame_model.py)")
    print("================================================================")
    baseline_summary = summarise("Baseline", base_elements(), ELEM_NAMES_BASE)

    print("================================================================")
    print("Design B: 'Braced' - add a diagonal brace directly from C to E")
    print("================================================================")
    names_B = ELEM_NAMES_BASE + ['8 (C-E, NEW)']
    designB_summary = summarise("Design B (braced)", add_CE_brace(base_elements()), names_B)

    print("================================================================")
    print("Design C: 'Lightweight' - thinner wall on all 7 original elements")
    print("================================================================")
    OD_new, ID_new = 0.100, 0.093   # same 100mm OD, thinner wall (90mm -> 93mm bore)
    A_new = np.pi / 4 * (OD_new**2 - ID_new**2)
    I_new = np.pi / 64 * (OD_new**4 - ID_new**4)
    print(f"  New section: OD={OD_new*1000:.0f}mm, ID={ID_new*1000:.0f}mm "
          f"-> A={A_new:.6e} m^2 ({A_new/A_SECTION*100:.1f}% of baseline A), "
          f"I={I_new:.6e} m^4 ({I_new/I_SECTION*100:.1f}% of baseline I)")
    designC_summary = summarise("Design C (lightweight)", base_elements(A=A_new, I=I_new), ELEM_NAMES_BASE)

    print("================================================================")
    print("Design D: alternative brace - S2 straight to G (vs Design B's C-E)")
    print("================================================================")
    names_D = ELEM_NAMES_BASE + ['8 (S2-G, NEW)']
    designD_summary = summarise("Design D (braced, S2-G)", add_S2G_brace(base_elements()), names_D)

    # ============================================================
    # Comparison table
    # ============================================================
    print("================================================================")
    print("Comparison")
    print("================================================================")
    print(f"  {'Design':<25}{'Mass (kg)':>12}{'Mass vs base':>14}{'V_max (m/s)':>14}{'V_max vs base':>16}")
    base_mass = baseline_summary['mass']
    base_Vmax = baseline_summary['V_max']
    all_designs = [baseline_summary, designB_summary, designC_summary, designD_summary]
    for s in all_designs:
        print(f"  {s['label']:<25}{s['mass']:12.3f}{s['mass']/base_mass*100:13.1f}%"
              f"{s['V_max']:14.3f}{s['V_max']/base_Vmax*100:15.1f}%")
    print()
    V_very_high = 50.0   # m/s, Table 1's "Very High" category
    for s in all_designs:
        margin = "above" if s['V_max'] >= V_very_high else "BELOW"
        print(f"  {s['label']}: V_max is {margin} Table 1's 'Very High' (50 m/s) category "
              f"by {abs(s['V_max']-V_very_high):.1f} m/s")
    print()
    print("See DESCRIPTION.md for the rationale behind each design and what this")
    print("mass/V_max trade-off means for choosing between them.")
