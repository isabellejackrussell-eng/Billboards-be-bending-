# ENME302 Assignment 1 — Code Walkthrough

This document explains what the code does, part by part: the method used, and what the results mean physically. It's a reference for **your own understanding** — the assignment brief explicitly prohibits using AI to generate the *written report*, so treat this as study notes, not text to paste in. Once you understand a section, write that part of the report yourself, in your own words.

Six code files go with this document, matching the brief's structure one-to-one:

- **`frame_model.py`** — the shared FE model (geometry, stiffness, assembly). Not a "part" of the brief by itself, but the foundation everything else builds on.
- **`part1_point_loading.py`** — Part 1 of the brief (point loads): deflections, reactions, stress.
- **`part1_equilibrium_checks.py`** — Part 1's equilibrium analysis (overall + the three critical points A, B, C).
- **`part2_distributed_wind.py`** — Part 2 of the brief (UDL wind loading).
- **`part3_timoshenko.py`** — the "Sensitivity to Euler-Bernoulli Beam Bending Assumption" section (Timoshenko element, shear deformation).
- **`part4_structural_modification.py`** — the "Structural Modifications" open-ended design task.

Every file after `frame_model.py` starts with `from frame_model import *` (and some also import from `part2_distributed_wind.py`), so keep all six files in the same folder.

The only thing left after these six files is the report itself, and the hand-drawn appendix sketches — both of which you need to do yourselves (see "Still outstanding" at the end).

---

## 0. `frame_model.py` — Modelling and Analysis

This corresponds to the brief's "Modelling and Analysis" section: turning Figure 1's dimensioned sketch into a finite element model, before any load is applied.

### Method

**Geometry.** The structure has 7 elements and 7 nodes: two fixed supports (`S1` at the base of the wall, `S2` higher up) and five free nodes (`C`, `D`, `E`, `F`, `G`, with `G` at the top). Every element's length `L` and orientation `alpha` (angle from the global X-axis) is computed with `np.arctan2(rise, run)` directly from Figure 1's dimensions, rather than typed-in decimal angles:

| Element | Connects | L (m) | alpha (computed from) |
|---|---|---|---|
| 1 | S1 → C | 0.414 | atan2(0.33, 0.25) = 52.85° |
| 2 | S2 → C | 0.25 | 0° |
| 3 | C → D | 0.211 | atan2(0.17, 0.125) = 53.75° |
| 4 | D → E | 0.375 | 0° |
| 5 | D → F | 0.625 | atan2(0.5, 0.375) = 53.13° (diagonal brace) |
| 6 | E → F | 0.5 | 90° |
| 7 | F → G | 0.5 | 90° |

Elements 4, 5 and 6 form a closed triangle between D, E and F — a bracing detail, not just a straight chain — which is why the structure needs exactly 7 elements to connect 7 nodes (a simple tree would only need 6). This closed loop also makes the structure statically indeterminate: you can't solve every internal member force by hand statics alone, which is exactly why a stiffness-method FE model is the right tool here.

**A geometry bug found by the equilibrium checks.** Earlier versions of this model set `alpha3 = alpha5 = alpha1` (52.85°), on the visual impression that the diagonal brace (element 5, D→F) is a straight continuation of the S1–C diagonal. It looks that way in Figure 1, but the dimensions say otherwise: element 5 rises 0.5m over a 0.375m run (53.13°), not the same slope as elements 1/3 (52.85°) — a small (~0.3°) but real difference. This was invisible in every deflection/reaction/stress result checked up to that point — they all still looked physically sensible — but it showed up as a small, non-zero residual in `part1_equilibrium_checks.py`'s rigid-body checks: element 5 was the only element that failed its own isolated free-body check (by exactly the amount that then propagated into every subsection check downstream of it). Switching every angle to an exact `arctan2()` computation removed this (and every other rounding-sized residual — the node coordinates now land on exact values like D=(0.375, 0.500) instead of (0.3775, 0.4979)), and the equilibrium checks now pass to floating-point precision. This is a good demonstration of *why* the equilibrium check is worth doing: it caught a real modelling error that the stress and deflection results alone did not reveal, since those still "looked right" either way. Worth a sentence in your report's methods/limitations discussion.

**Section properties.** All elements share the same 100mm OD / 90mm ID hollow circular steel section: `A = π/4·(OD²−ID²) ≈ 1.492×10⁻³ m²` and `I = π/64·(OD⁴−ID⁴) ≈ 1.688×10⁻⁶ m⁴`. (An earlier version of this code had `I` **100× too large** — an exponent slip, `1e-4` instead of `1e-6` — which would have made every element artificially stiff; long since fixed.)

**Element stiffness matrices.** For each element, `local_frame()` builds the 6×6 Euler-Bernoulli stiffness matrix in the element's own local coordinates (matching the brief's Table 2 exactly), using `β = AL²/I`. `transform_matrix()` builds the rotation matrix for that element's angle, and `global_frame()` rotates the local matrix into global coordinates: `K̂ = Λᵀ K Λ`. `local_frame_timoshenko()` builds the alternative Timoshenko version of the same matrix (used only by `part3_timoshenko.py` — see below); passing `Phi=0` into it reproduces `local_frame()` exactly, which is a good sanity check that the two formulations are consistent.

**Assembly.** Each element has its own 15×6 "Assembly" matrix — a matrix of 0s and 1s that says which of the element's 6 local degrees of freedom (DOF) map to which of the 15 *global* DOF (5 free nodes × 3 DOF each: X, Y, rotation). A local DOF belonging to a fixed support simply maps to nothing (an all-zero column) — that's how the fixed boundary conditions are applied, rather than the more common approach of building a full stiffness matrix and deleting rows/columns for restrained DOF. `global_stiffness()` uses this to fold each element's contribution into the right place in the 15×15 system: `KG_e = Assembly · K̂ · Assemblyᵀ`. Summing all seven gives `KG_Total`, the full structure stiffness matrix.

**Generic multi-topology helpers.** `build_element()` and `assemble_structure()` are a generalised version of the same build process, taking a plain list of `{E, I, A, L, alpha, Assembly}` dictionaries instead of the seven hardcoded module-level variables. `part3_timoshenko.py` and `part4_structural_modification.py` use these to build *alternative* structures (a different element formulation, or a different topology/section) without re-deriving the direct stiffness method each time. `moment_about_point()` and `structure_mass()` are small helpers used by the equilibrium checks and the structural modification comparison respectively.

### What the result means

There's no "result" to interpret yet — this file just builds the model. Running it directly prints the node coordinates and confirms `KG_Total` is a 15×15 matrix, which is the expected size for 5 free nodes × 3 DOF. This is also where you'd pull the individual element `K` matrices and `Assembly` matrices for the brief's appendix requirement (sketches + assembly matrices per element).

---

## 1. `part1_point_loading.py` — Part 1: Point Loading

### Method

**Applying the loads.** Figure 2 shows two 2000N horizontal loads, both pushing toward the wall (−X direction), applied at the two nodes that bracket the sign face: `E` (its base) and `G` (its top). In the global load vector `Q` (15×1), this means putting `−2000` in the row corresponding to each node's X-DOF and leaving everything else zero. Solving `KG_Total · q = Q` for `q` gives the displacement of every free DOF in the structure.

**Recovering element-level results.** `q` only has the *global*, *reduced* displacements. To get anything useful for a specific element, you: (1) pull out that element's 6 relevant entries from `q` via its Assembly matrix (`global_deflections`), (2) rotate those into the element's own local axes (`element_deflections`), and (3) multiply by the local stiffness matrix to get the local end forces — axial force, shear, and moment at each end (`element_force`). The GLOBAL version of the same end-force vector (`global_force`, `K̂·D`) is also computed for every element and returned alongside the local one — the local version is what stress needs, the global version is what the equilibrium checks in `part1_equilibrium_checks.py` need, since global vectors can be added directly across differently-oriented elements.

**Reactions.** Only element 1 touches support S1, and only element 2 touches support S2 — so each support's reaction is just that one element's global end-force vector at its fixed end (`F[0][0:3]`, `F[1][0:3]`). No summing needed, because nothing else shares that node.

**Stress.** `σ_total = |σ_axial| + |σ_bending|`, with `σ_axial = |N|/A` and `σ_bending = |M|·c/I` (`c` = 50mm, half the outside diameter, per the brief). Since Part 1 has no distributed loads on any element, the bending moment is *linear* along each element — so its largest magnitude is always at one of the two ends, and checking both ends of all 7 elements is sufficient to find the true maximum anywhere in the structure.

### What the results mean

- **Top deflection ≈ 3.0mm horizontal, 1.1mm vertical.** This is the classic "cantilever" signature — the free end furthest from the fixed base moves the most, since it's carrying the accumulated bending of everything below it. The vertical component exists because the structure isn't a simple straight cantilever — the diagonal geometry couples horizontal loading into some vertical movement too.
- **Reactions**: support 1 sees Rx ≈ −10.2kN, support 2 sees Rx ≈ +14.2kN (opposite signs — one support is being pulled in the load's direction, the other resists it in reaction, and together they balance the applied 4000N — confirmed exactly, to floating-point precision, by `part1_equilibrium_checks.py`). Both also carry vertical force and moment even though the applied loads are purely horizontal — the diagonal geometry converts some of that horizontal load into vertical/moment reactions at the base.
- **Maximum stress ≈ 81 MPa, in element 3 (the short diagonal segment between C and D), right at the C end.** This is well under the 350 MPa yield stress, which makes sense — Part 1 is a simplified approximation of wind loading using just two point loads, not the real distributed pressure. Element 3 being the hot spot makes physical sense too: it's short, so a given moment produces a larger stress gradient across its section relative to its length, and it sits close to the base where bending moments from everything above it accumulate. This same element governs in Part 2 as well, and is exactly the joint that `part4_structural_modification.py`'s "braced" design targets.

---

## 1b. `part1_equilibrium_checks.py` — Part 1: Equilibrium Checks

This is the brief's second Part 1 bullet point: two independent sanity checks that the reaction/internal-force results actually make physical sense, done entirely separately from the direct-stiffness solve itself.

### Method

**Overall equilibrium.** Treat the whole structure as one rigid block. The only things acting on it are the two applied 2000N loads and the two support reactions (already computed in `solve_part1()`) — sum them (ΣFx, ΣFy, and ΣM about a reference point, here S1) and confirm they land on zero. This is a genuinely independent check: it doesn't reuse anything from how `q` was solved, only the *results* (reactions) that came out of it.

**Subsection equilibrium at points A, B, C.** The brief's Figure 2 marks three points where the structure could be "cut" and treated as a rigid free body. Matching the arrows in Figure 2 against the model's actual joint locations, these are the three three-member joints: **A = node F** (elements 5, 6, 7 meet here, nearest the sign), **B = node D** (elements 3, 4, 5), **C = node C** (elements 1, 2, 3, nearest the supports — conveniently the same letter as the node name here). At each point, cut through whichever member(s) lead back toward the supports, and treat everything beyond the cut as a free body: the FEA-computed internal force at the cut, plus whatever real external load acts within that free body, must sum to zero — exactly like a textbook method-of-sections check, just using FEA-computed internal forces instead of hand-solved ones.

**The sign convention, and why it needed care.** The direct-stiffness quantity `K̂·D` at a node gives *"the force that must be applied to that element, at that node, by whatever is attached there"* — which is why it works completely unchanged as a support reaction (the wall's reaction *is* exactly that force). But for an interior cut, the free body wants the opposite direction — *"the force the cut member exerts on the free body"* — which by Newton's third law is the *negative* of the raw value. This was checked (and the sign nailed down) by first testing it on the simplest possible case: does one isolated element's own two end-forces satisfy its own equilibrium (paying attention to the arm term for the moment balance)? That check passed to ~1e-13, confirming the formula, before trusting it on a multi-element free body.

### What the results mean

Every check — overall, and all three subsection cuts — now balances to floating-point precision (~1e-10 or better in force, exactly 0.000000 in the printed output). That's strong, independent confirmation that the whole solution is physically self-consistent, not just numerically self-consistent with its own solve. As described in section 0 above, getting a *clean* zero here (rather than a small-but-real non-zero residual) is what originally caught the alpha3/alpha5 geometry bug — worth mentioning in your report as evidence the equilibrium check earned its place in the analysis, not just a box-ticking exercise.

---

## 2. `part2_distributed_wind.py` — Part 2: Distributed Wind Loading

### Method

**Pressure → UDL.** Table 1 gives wind pressure in kPa for each category. Multiplying by the sign's depth (3m into the page) converts that pressure into a uniformly distributed load (UDL) in N/m along the frame: `w = pressure × depth`. The brief also gives the pressure formula directly (`Pressure = 0.6·V²`, V in m/s), which is used later to sweep across wind speed.

**Which elements carry it.** The UDL acts on the sign face — physically, that's the vertical run from `E` up through `F` to `G` (elements 6 and 7), which is both the only part of the frame oriented vertically *and* the only part actually located at the sign's position. This is also the same span Part 1's two point loads were bracketing, so the two parts are modelling the same physical loading, just with different levels of approximation.

**Equivalent nodal loads.** A finite element can only be loaded at its two end nodes — it can't take a distributed load directly. So a UDL has to be converted into a statically-equivalent pair of end forces/moments (the "fixed-end force" concept from beam theory) using standard formulas (`UDL_frame_f_eq`, for the transverse component; `Axial_UDL_frame_f_eq`, for the tiny axial component that would exist if the element weren't exactly vertical). Since the wind is horizontal but elements 6/7 are vertical, `global_udl_to_local()` projects the global UDL vector into the element's local axial/transverse directions first.

These equivalent loads get solved for `q` exactly like Part 1's point loads. But there's a catch: once the solve is done, `K·d` for elements 6 and 7 no longer equals their *true* internal force, because part of what they're carrying is the distributed load sitting directly on them, not just the deformation transmitted from their neighbours. The fix is to subtract the equivalent load back out: `f_true = K·d − f_eq`. Skip this step and elements 6/7's stresses come out wrong (silently — no error, just wrong numbers), which is an easy mistake to make.

**Interior stress check.** Because elements 6/7 now carry the UDL directly, their bending moment is no longer linear along their length — it's a parabola. So checking only the two ends (like Part 1 could) isn't enough; the true peak could be mid-element. `moment_along_element()` computes the full moment as a function of position, validated against a textbook cantilever-under-UDL case before being trusted here.

**Maximum rated wind speed.** Because the whole model is linear elastic, every stress in the structure scales exactly with the load, and the load scales with V² (`pressure = 0.6·V²`). So rather than guessing-and-checking different wind speeds, the speed that brings the governing stress up to the allowable value can be solved directly: `V_max = V_ref · √(σ_allow / σ_ref)`, using the already-solved "Low" case as the reference point. This is then double-checked by fully re-solving the model at that computed speed and confirming the resulting stress lands exactly on the allowable value. `get_V_max()` packages this up as a reusable function — `part3_timoshenko.py` and `part4_structural_modification.py`'s design comparisons both build on it rather than recomputing it.

### What the results mean

- **"Low" wind case (31.9 m/s / 114.8 km/h): top deflection ≈ 1.27mm, max stress ≈ 37.0 MPa**, still governed by element 3, same as Part 1. Smaller than Part 1's numbers because the UDL's total force (1830N) is less than Part 1's two 2000N point loads combined (4000N), and it's spread over a length rather than concentrated at the ends.
- **Element 6's governing stress point sits ~81% along its length, not at either end** — direct evidence that the interior-point check was necessary, not just a formality. If the code had only checked the ends (like Part 1's approach), this particular peak would have been missed.
- **Maximum rated wind speed ≈ 62.0 m/s (223 km/h) for a factor of safety of 2.5 against yield.** This is well above even the "Very High" category in Table 1 (50 m/s / 180 km/h) — meaning, in this simplified model, the sign has a healthy margin against the codified wind categories. This margin is exactly what motivates `part4_structural_modification.py`'s "lightweight" design option below. Worth flagging in your discussion: because stress scales with *V²*, not V, the relationship between safety margin and wind speed is not linear.

---

## 3. `part3_timoshenko.py` — Sensitivity to the Euler-Bernoulli Assumption

### Method

**What Timoshenko adds.** The Euler-Bernoulli element used everywhere else assumes plane sections stay perpendicular to the beam's neutral axis as it bends — i.e. it ignores shear deformation entirely. The Timoshenko formulation (brief's Table 2) adds a shear-flexibility parameter `Φ = 12EI/(G·As·L²)` into the stiffness matrix; `Φ = 0` recovers Euler-Bernoulli exactly (checked directly: `local_frame_timoshenko(..., Phi=0)` is bit-for-bit identical to `local_frame(...)` for the same inputs — a good confidence check before trusting the rest of the comparison). `As`, the shear area, uses the brief's formula for a hollow circular section: `As = 2A/π`.

**Building two parallel structures.** `make_elements(use_timoshenko)` builds the *same* geometry, section and Assembly matrices either way — only whether each element gets a `timoshenko_Phi` value attached differs. `frame_model.assemble_structure()` (see section 0) turns either list into a fully-built stiffness system, so the Euler-Bernoulli and Timoshenko models are guaranteed to differ *only* in their element formulation, nothing else.

**Solving at V_max.** Both models are solved under the exact same UDL wind load, at the V_max found in Part 2 (the FoS = 2.5 rated speed) — `solve_udl_case()` mirrors Part 2's `solve_wind_case()` but works generically on whichever "built" element list it's given.

**The comparison table.** The brief specifically asks for, per element, the change in the transverse deflection *within* that element (`d5^e − d2^e`, i.e. the local-y displacement at node 2 minus node 1 — the element's own bending/shear deflection, independent of rigid-body movement) and the change in end-to-end rotation (`d6^e − d3^e`). In this code's 0-indexed local deflection vectors, that's `d[4]-d[1]` and `d[5]-d[2]` respectively.

### What the results mean

- **Every element's `Φ` sits between about 0.14 and 1.24** — not negligible. `Φ` is essentially a ratio of bending flexibility to shear flexibility; values order-1 or above mean shear deformation is contributing a similar amount of flexibility to bending, not a small correction on top of it. This is a direct consequence of the tube's proportions: these are short, thick members (e.g. element 2 is only 0.25m long with a 100mm-diameter section — an L/D ratio around 2.5), and shear deformation in beam theory scales up as members get "stubbier".
- **Tip (node G) deflection increases by about 6.3%** once shear is included — a real, but not dramatic, effect at the structure's overall scale. That 6.3% is a genuinely useful number for your report's "is Euler-Bernoulli valid here" discussion: it tells you the *overall* deflection prediction is reasonably (not perfectly) robust to the assumption.
- **Per-element, the picture is much more mixed** — some elements' internal transverse deflection changes by only ~6%, but element 6 (the one furthest from the base, along a load path with the smallest Φ) changes by ~36% in its `d6-d3` rotation term, while elements 1 and 2 (both directly at the fixed supports, both with sizeable Φ) actually show a small *decrease* in their own `d5-d2` term. This isn't a bug — the structure is statically indeterminate (recall the closed D-E-F loop), so adding a new deformation mechanism (shear) to every element doesn't just uniformly scale everything up; it lets load redistribute across the redundant load paths, and different members can respond differently, even oppositely, to that redistribution. This element-by-element table is exactly the evidence the brief's per-element comparison is asking you to base your written discussion on.

---

## 4. `part4_structural_modification.py` — Structural Modifications

### Method

Three designs, all solved identically (same UDL method as Part 2, same FoS = 2.5 target against the same 350 MPa yield), so the comparison is apples-to-apples:

- **Baseline** — the original 7-element structure, for reference.
- **Design B ("Braced")** — adds one new 8th element, a diagonal brace directly from node C to node E (both already-existing free nodes — no new DOF needed, just a new 15×6 Assembly matrix). *Rationale:* Parts 1, 2 and the equilibrium checks all repeatedly identified element 3 and the joint at D as the structure's stress hot-spot — that region currently relies on the slender D–E outrigger (element 4) plus the C-D-F diagonal chain to get load up to the mast. A direct C-to-E brace gives that load a second, more direct path, bypassing D's joint entirely for part of the load.
- **Design C ("Lightweight")** — keeps the original 7-element topology but thins every tube's wall (100mm OD unchanged, bore opened from 90mm to 93mm). *Rationale:* Part 2 found the baseline structure's rated wind speed (62.0 m/s) sits well above Table 1's "Very High" category (50 m/s) — there's spare capacity to trade for weight savings, rather than only ever adding material.

`solve_udl_case()` generalises Part 2's wind-load solver to work on *any* element list/topology (not just the fixed 7-element baseline), and `find_V_max()` reuses the same "solve once, then scale by √(σ_allow/σ_ref)" trick from Part 2, since the V²-stress-scaling property holds for any linear elastic model, whatever its topology.

`structure_mass()` (in `frame_model.py`) computes total steel mass as `Σ(density × A_e × L_e)` using a typical structural steel density of 7850 kg/m³.

### What the results mean

| Design | Mass | vs baseline | V_max | vs baseline |
|---|---|---|---|---|
| Baseline | 33.7 kg | 100% | 62.0 m/s | 100% |
| B — Braced | 39.9 kg | +18% | 75.7 m/s | +22% |
| C — Lightweight | 23.9 kg | −29% | 53.0 m/s | −14% |

- **Design B is a genuinely favourable trade**: an 18% mass increase buys a 22% increase in rated wind speed — *more* than proportional. That's a signature of successfully relieving a stress concentration rather than just "adding more of the same" everywhere: the new brace specifically fixes the weakest link (element 3/joint D), so a comparatively small amount of extra material has an outsized effect on the governing stress. Interestingly, the governing element also *changes* under this design (element 2, not element 3) — evidence the brace did its job and shifted the bottleneck elsewhere.
- **Design C is a real, quantifiable weight-safety trade-off**: it saves 29% of the material at the cost of 14% of the rated wind speed, landing at 53.0 m/s — still 3 m/s above the "Very High" category, but with a much thinner margin than the baseline's 12 m/s. Whether that's an acceptable trade depends on factors outside this model (corrosion allowance, fatigue, buckling of a thinner-walled tube, manufacturing tolerances) — worth flagging explicitly as a limitation if you discuss this design in your report.
- Both are legitimate, defensible answers to the brief's open-ended question — there's no single "correct" modification, which is exactly what the brief says to expect. Feel free to try your own variations by editing `base_elements()`/`add_CE_brace()`'s parameters (e.g. a different `ID_new`, or bracing a different pair of nodes) — the whole point of the generic `assemble_structure()` machinery in `frame_model.py` is to make that quick to experiment with.

---

## Still outstanding (not in these files)

Everything from the brief's technical analysis is now covered by the six code files above. What's left is work only you and your partner can (and are required to) do:

- The hand-drawn appendix sketches (overall structure + global DOF, free-body diagram of each element with its own DOF) — `frame_model.py`'s printed node coordinates and each element's `Assembly` matrix are what you'd reference/paste alongside these.
- The written report itself — introduction, methods, results/discussion, conclusions, executive summary. This document gives you the "what happened and why" for every result; turning that into your own words, with your own interpretation and recommendations, is the part the brief requires to be entirely your own work.
- The AI declaration/acknowledgement statement the brief requires — noting where and how AI (this code) was used, per the brief's academic integrity requirements.
