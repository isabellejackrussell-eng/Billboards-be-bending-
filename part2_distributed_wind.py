"""
part2_distributed_wind.py
================================================================
ENME302 Assignment #1 - Part 2: Distributed Wind Loading

Converts Table 1's wind pressures into an equivalent UDL on the sign
face, represents that UDL as equivalent nodal loads, and solves:
  1. the 'Low' wind zone case (115 km/h) - deflections + governing stress
  2. the maximum wind speed the structure can be rated for at a factor
     of safety of 2.5 against yield (350 MPa) - deflections + reactions

Requires frame_model.py in the same folder.
See DESCRIPTION.md for the full write-up of the method and what the
results below mean physically.
"""
import numpy as np
from frame_model import *

# ================================================================
# Table 1: wind categories -> basic static pressure (kPa -> Pa)
# ================================================================
wind_table = {
    'Low': 0.61e3,
    'Medium': 0.82e3,
    'High': 1.16e3,
    'Very High': 1.50e3,
}
sign_depth = 3.0  # m - depth of the sign board into the page


def pressure_to_udl(pressure_Pa, depth=sign_depth):
    """Convert a wind pressure (Pa, normal to the sign face) into an
    equivalent UDL (N/m) along the frame."""
    return pressure_Pa * depth


def solve_wind_case(V_ms, depth=sign_depth):
    """Solve the frame under a UDL wind load on the sign face (elements 6
    & 7 - the E->F->G vertical run, the only part of the frame at the
    sign's actual location) for wind speed V_ms (m/s), blowing directly
    onto the sign (global -X, matching Figure 2/3's arrows).
    Returns q, per-element deflections/true forces, the full stress
    table, and the governing (max) sigma_total anywhere in the structure.
    """
    pressure = 0.6 * V_ms**2              # Pa, per the brief's note
    w_udl = pressure_to_udl(pressure, depth)  # N/m

    w_gx, w_gy = -w_udl, 0.0
    p6, wb6 = global_udl_to_local(w_gx, w_gy, alpha6)
    p7, wb7 = global_udl_to_local(w_gx, w_gy, alpha7)

    feq6 = Axial_UDL_frame_f_eq(p6, L6) + UDL_frame_f_eq(wb6, L6)
    feq7 = Axial_UDL_frame_f_eq(p7, L7) + UDL_frame_f_eq(wb7, L7)

    Qeq6 = Q_eq(Assembly6, F_eq(Lambda6, feq6))
    Qeq7 = Q_eq(Assembly7, F_eq(Lambda7, feq7))
    Q_total = Qeq6 + Qeq7   # Part 2: UDL only, Part 1's point loads removed

    qv = displacements(Q_total, KG_Total)

    Assemblies = [Assembly1, Assembly2, Assembly3, Assembly4, Assembly5, Assembly6, Assembly7]
    Lambdas = [Lambda1, Lambda2, Lambda3, Lambda4, Lambda5, Lambda6, Lambda7]
    Ks = [K1, K2, K3, K4, K5, K6, K7]
    Ds = [global_deflections(Asm, qv) for Asm in Assemblies]
    ds = [element_deflections(Lam, D) for Lam, D in zip(Lambdas, Ds)]
    fs = [element_force(K, d) for K, d in zip(Ks, ds)]
    # Elements 6 & 7 carry the UDL directly - subtract the equivalent load
    # to recover the TRUE internal member-end forces.
    fs[5] = fs[5] - feq6
    fs[6] = fs[6] - feq7

    Ls = [L1, L2, L3, L4, L5, L6, L7]
    As = [A1, A2, A3, A4, A5, A6, A7]
    Is = [I1, I2, I3, I4, I5, I6, I7]
    w_bars = [0.0, 0.0, 0.0, 0.0, 0.0, wb6, wb7]

    results = []
    for idx in range(7):
        f = fs[idx]
        sigma_axial = abs(f[0, 0]) / As[idx]
        M1, M2 = f[2, 0], f[5, 0]
        x_vals, M_vals = moment_along_element(M1, M2, w_bars[idx], Ls[idx])
        sigma_bending_vals = np.abs(M_vals) * c / Is[idx]
        sigma_total_vals = sigma_axial + sigma_bending_vals
        i_max = int(np.argmax(sigma_total_vals))
        results.append((idx + 1, x_vals[i_max], Ls[idx], sigma_axial,
                         sigma_bending_vals[i_max], sigma_total_vals[i_max]))

    governing = max(results, key=lambda r: r[5])
    return {'V': V_ms, 'w_UDL': w_udl, 'q': qv, 'D': Ds, 'd': ds, 'f': fs,
            'stress_results': results, 'governing': governing, 'sigma_max': governing[5]}


def print_case(case, label):
    q_ = case['q']
    print(f"--- {label} ---")
    print(f"Equivalent UDL on the sign face: w = {case['w_UDL']:.1f} N/m "
          f"(V = {case['V']:.3f} m/s = {case['V']*3.6:.1f} km/h)")
    print(f"Top of structure (node G) deflection:")
    print(f"  X = {q_[12, 0]*1000:.4f} mm")
    print(f"  Y = {q_[13, 0]*1000:.4f} mm")
    print(f"  theta = {q_[14, 0]:.6e} rad")
    g = case['governing']
    print(f"Maximum total normal stress = {g[5]/1e6:.2f} MPa, in element {g[0]}, "
          f"at x = {g[1]:.4f} m along its {g[2]:.4f} m length")
    print("Governing point per element, sorted by sigma_total:")
    for r in sorted(case['stress_results'], key=lambda r: -r[5]):
        frac = (r[1] / r[2] * 100) if r[2] else 0.0
        print(f"  elem {r[0]}  x={r[1]:.4f} m ({frac:4.1f}% along)   "
              f"axial={r[3]/1e6:6.2f}   bending={r[4]/1e6:6.2f}   total={r[5]/1e6:6.2f}")
    print()


# ================================================================
# Reference values reused by other files (part3_timoshenko.py,
# part4_structural_modification.py) so they don't need retyping.
# ================================================================
sigma_yield = 350e6
FoS_required = 2.5
sigma_allow = sigma_yield / FoS_required   # 140 MPa


def get_V_max():
    """Convenience for other files: the FoS=2.5 max rated wind speed,
    computed the same way as the __main__ block below (via the 'Low' case
    as the linear-scaling reference point), without printing/plotting.
    Returns (V_max, case_low)."""
    V_low = np.sqrt(wind_table['Low'] / 0.6)
    case_low = solve_wind_case(V_low)
    V_max = V_low * np.sqrt(sigma_allow / case_low['sigma_max'])
    return V_max, case_low


if __name__ == "__main__":
    # ============================================================
    # 1) 'Low' wind zone (115 km/h) - the first case in the brief
    # ============================================================
    V_low = np.sqrt(wind_table['Low'] / 0.6)   # m/s, back-calculated from Table 1's own formula
    case_low = solve_wind_case(V_low)
    print_case(case_low, "Part 2, 'Low' wind zone (115 km/h, 0.61 kPa)")

    # ============================================================
    # 2) Maximum rated wind speed for a factor of safety of 2.5 against yield
    # ============================================================
    # The FE model is linear elastic, so every stress scales exactly with the
    # applied UDL, which itself scales with V^2 (pressure = 0.6*V^2). So the
    # governing element/location doesn't change with wind speed, and V_max
    # can be solved for directly rather than iterating/bisecting:
    V_max = V_low * np.sqrt(sigma_allow / case_low['sigma_max'])

    print(f"--- Max rated wind speed for FoS >= {FoS_required} ---")
    print(f"Allowable stress = yield / FoS = {sigma_yield/1e6:.0f} / {FoS_required} = {sigma_allow/1e6:.1f} MPa")
    print(f"V_max = V_low * sqrt(sigma_allow / sigma_low) = {V_max:.3f} m/s ({V_max*3.6:.1f} km/h)")

    case_max = solve_wind_case(V_max)
    print(f"Check - re-solving directly at V_max gives sigma_max = {case_max['sigma_max']/1e6:.4f} MPa "
          f"(should equal {sigma_allow/1e6:.1f} MPa)")
    print()

    q_max = case_max['q']
    print(f"Deflections at the top of the structure (node G) at V_max:")
    print(f"  X = {q_max[12, 0]*1000:.4f} mm")
    print(f"  Y = {q_max[13, 0]*1000:.4f} mm")
    print(f"  theta = {q_max[14, 0]:.6e} rad")

    F1_max = global_force(K_hat1, case_max['D'][0])
    F2_max = global_force(K_hat2, case_max['D'][1])
    R1_max = F1_max[0:3]
    R2_max = F2_max[0:3]
    print()
    print(f"Reactions at V_max:")
    print(f"  Support 1: Rx={R1_max[0,0]:.2f} N, Ry={R1_max[1,0]:.2f} N, M={R1_max[2,0]:.2f} N.m")
    print(f"  Support 2: Rx={R2_max[0,0]:.2f} N, Ry={R2_max[1,0]:.2f} N, M={R2_max[2,0]:.2f} N.m")
    print(f"  Equilibrium check: sum(Rx) = {R1_max[0,0]+R2_max[0,0]:.4f} N "
          f"(should equal total UDL force = {case_max['w_UDL']*(L6+L7):.4f} N)")

    # ============================================================
    # Plots
    # ============================================================
    d_low = case_low['d']
    plot_structure_deflected_shape(*d_low, Disp_mag=10,
                                    title="Part 2: deflected shape, 'Low' wind (115 km/h)")

    d_max = case_max['d']
    plot_structure_deflected_shape(*d_max, Disp_mag=10,
                                    title=f"Part 2: deflected shape at V_max ({V_max:.1f} m/s)")
    plt.show()
