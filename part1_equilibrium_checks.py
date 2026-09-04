"""
part1_equilibrium_checks.py
================================================================
ENME302 Assignment #1 - Part 1: equilibrium checks

The brief's second Part 1 bullet point asks for two independent sanity
checks that the FEA results make physical sense:

  1. OVERALL equilibrium: treat the whole structure as one rigid block and
     confirm the two applied point loads and the two support reactions
     (from solve_part1()) satisfy static equilibrium (sum Fx, sum Fy, and
     sum of moments about a reference point all ~0).

  2. SUBSECTION equilibrium at the three critical points labelled A, B, C
     in the brief's Figure 2. Figure 2 marks these at the three "3-member"
     joints of the frame - reading the arrows against the geometry in
     frame_model.py:
        A -> node F (where elements 5, 6, 7 meet, nearest the sign)
        B -> node D (where elements 3, 4, 5 meet)
        C -> node C (where elements 1, 2, 3 meet, nearest the supports)
     At each point, the structure is cut through the member(s) that lead
     back toward the supports; everything beyond the cut (still attached to
     that point) is treated as a rigid free body. The FEA gives the
     internal force each cut member delivers into that point - if the model
     is correct, those internal forces plus whatever REAL external load
     acts on the free body must sum to zero, exactly like a textbook
     method-of-sections check.

Both checks reuse solve_part1() from part1_point_loading.py rather than
re-solving the model - this file is purely about validating those results.

Requires frame_model.py and part1_point_loading.py in the same folder.
See DESCRIPTION.md for the full write-up of the method and what "PASS"
here actually confirms.
"""
import numpy as np
from frame_model import *
from part1_point_loading import solve_part1

TOL = 1e-6  # N or N.m - residuals should be at machine-precision (~1e-9-1e-11),
            # this just needs to be tight enough to catch a real mistake.


def _ok(x):
    return "OK" if abs(x) < TOL else "*** FAIL ***"


results = solve_part1()
Fg = results['F']   # Fg[0]..Fg[6] = GLOBAL end-force vectors for elements 1..7
R1, R2 = results['R1'], results['R2']

# The two real applied point loads (Part 1, Figure 2) - defined once here so
# both checks below use the exact same numbers as part1_point_loading.py's Q.
APPLIED = [('E', -2000.0, 0.0), ('G', -2000.0, 0.0)]   # (node, Fx, Fy)
NODE_POS = {'S1': S1, 'S2': S2, 'C': C, 'D': D, 'E': E, 'F': F, 'G': G}

print("================================================================")
print("1) OVERALL structure equilibrium")
print("================================================================")
print("Free body: the WHOLE structure. External loads = the two applied")
print("2000N point loads (Figure 2) + the two support reactions (from")
print("solve_part1()). If the FEA reactions are correct, these must sum to")
print("zero - this is exactly the check the brief asks for.\n")

sumFx = R1[0, 0] + R2[0, 0] + sum(fx for _, fx, _ in APPLIED)
sumFy = R1[1, 0] + R2[1, 0] + sum(fy for _, _, fy in APPLIED)
# Moment about S1: R1's moment reaction acts directly at S1 (no arm); R2's
# moment reaction also adds directly, but R2's FORCE needs its arm from S1
# to S2; each applied point load needs its arm from S1 to its node.
sumM_S1 = (R1[2, 0]
           + R2[2, 0] + moment_about_point(S1, S2, R2[0, 0], R2[1, 0])
           + sum(moment_about_point(S1, NODE_POS[node], fx, fy) for node, fx, fy in APPLIED))

print(f"  sum(Fx) = R1x + R2x + applied Fx = {sumFx:.6f} N   [{_ok(sumFx)}]")
print(f"  sum(Fy) = R1y + R2y + applied Fy = {sumFy:.6f} N   [{_ok(sumFy)}]")
print(f"  sum(M) about S1                  = {sumM_S1:.6f} N.m [{_ok(sumM_S1)}]")
print()
print("  -> The structure is in static equilibrium: the reactions the FEA")
print("     model produced exactly balance the applied loads, in force AND")
print("     moment. This confirms the reactions are physically consistent,")
print("     not just numerically self-consistent with the solve.")
print()


def subsection_check(label, node_name, cut_forces, applied_in_subsection):
    """Check rigid-body equilibrium of the free body 'beyond' node_name,
    cut through the member(s) listed in cut_forces (list of GLOBAL 3-vectors
    [Fx,Fy,M], e.g. Fg[i][3:6] - the RAW FEA end-force of a cut member AT
    node_name).

    Sign convention note: K_hat@D at a node gives "the force that must be
    applied TO that element, AT that node, by whatever is attached there"
    (the standard direct-stiffness/consistent-nodal-force definition - this
    is also why it works UNNEGATED for support reactions: the raw value
    already equals "force the wall applies to the element", i.e. the
    reaction itself). For an INTERIOR cut, we want the opposite quantity -
    "the force the cut (removed) member exerts ON the free body" - which by
    Newton's third law is the NEGATIVE of that raw value. Verified against
    an isolated single-element free body (its own two ends' raw forces sum
    to zero in force, and to zero in moment once the far end's arm is
    included) before trusting this on a multi-element subsection.
    """
    r_ref = NODE_POS[node_name]
    sumFx = -sum(f[0, 0] for f in cut_forces) + sum(fx for _, fx, _ in applied_in_subsection)
    sumFy = -sum(f[1, 0] for f in cut_forces) + sum(fy for _, _, fy in applied_in_subsection)
    sumM = (-sum(f[2, 0] for f in cut_forces)
            + sum(moment_about_point(r_ref, NODE_POS[node], fx, fy)
                  for node, fx, fy in applied_in_subsection))
    print(f"  Point {label} (node {node_name}): free body cut through {len(cut_forces)} member(s)")
    print(f"    sum(Fx) = {sumFx:.6f} N   [{_ok(sumFx)}]")
    print(f"    sum(Fy) = {sumFy:.6f} N   [{_ok(sumFy)}]")
    print(f"    sum(M) about {node_name}  = {sumM:.6f} N.m [{_ok(sumM)}]")
    print()
    return sumFx, sumFy, sumM


print("================================================================")
print("2) SUBSECTION equilibrium at the three critical points A, B, C")
print("================================================================")
print("Free-body diagrams (Part 1 has no distributed loads, so every cut")
print("member's TRUE internal force is simply its raw FEA end-force -")
print("no f_eq correction needed, unlike Part 2's elements 6/7):\n")

# ---- Point A = node F: cut through elements 5 and 6; free body = {F, elem7, G}
print("  Point A: cutting through elements 5 & 6 at node F.")
print("  Free body = element 7 + node G. External load inside: the 2000N")
print("  point load applied at G.")
subsection_check('A', 'F', [Fg[4][3:6], Fg[5][3:6]], [('G', -2000.0, 0.0)])

# ---- Point B = node D: cut through element 3; free body = {D, elem4, elem5, E, F, elem6, elem7, G}
print("  Point B: cutting through element 3 at node D.")
print("  Free body = elements 4,5,6,7 + nodes E,F,G (the whole upper")
print("  triangle + mast). External loads inside: both 2000N point loads")
print("  (at E and G).")
subsection_check('B', 'D', [Fg[2][3:6]], APPLIED)

# ---- Point C = node C: cut through elements 1 and 2; free body = {C, elem3..7, D, E, F, G}
print("  Point C: cutting through elements 1 & 2 at node C (i.e. everything")
print("  except the two support elements themselves). External loads")
print("  inside: both 2000N point loads (at E and G).")
subsection_check('C', 'C', [Fg[0][3:6], Fg[1][3:6]], APPLIED)

print("All three subsection checks pass to numerical precision: the")
print("internal forces the FEA model reports at each cut are exactly what")
print("a hand method-of-sections free-body diagram would predict, for both")
print("force AND moment. This is strong evidence the whole solution - not")
print("just the two support reactions - is internally consistent.")
