ARITHMETIC VERIFICATION GUIDE
Exact complex coherence in codimension two

This guide describes verification of the saved rational certificates used
in the proof for N >= 180. The verifier reconstructs the
arithmetic from the saved inputs without running the programs that produced
them.

REQUIREMENTS AND COMMANDS

Use Python 3.10 or later. All dependencies are in the standard library or
included in this repository. Keep the certificate/ and validation/ directories
in their supplied locations. No network access or separate research checkout
is required.

From the repository root, run the full arithmetic verifier with:
  python -B reproduction/certificate/verify_certificates.py

From the reproduction/ directory, the equivalent command is:
  python -B certificate/verify_certificates.py

An absolute path to verify_certificates.py works from any working directory.
The script resolves its default inputs and modules relative to its own
location. The --archive and --index options select alternative input files.

For a packaging check without mathematical verification, run from the
repository root:
  python -B reproduction/check_package.py

The packaging check verifies file hashes, archive membership, the recorded
metadata changes and the availability of the local modules. It does not
call the arithmetic verification stages.

OUTPUT AND PARTIAL RUNS

The default verifier command runs the global, continuous and local stages.
On success it exits with code 0 and writes a JSON report to stdout containing:
  "status": "PASS"
  "complete_arithmetic_acceptance": true

Progress messages go to stderr. Either stream may be redirected by the
caller. A failed check produces a JSON report with "status": "FAIL" and
exit code 1.

The --stage global and --stage continuous options run individual stages.
The --stage local option also runs its global and continuous prerequisites.
All three options report "PASS_PARTIAL" and set
"complete_arithmetic_acceptance" to false on success. Use the default command
for complete arithmetic acceptance.

The historical report records 5,266,235 checks on an archive containing 1,007
members. The public archive contains the fourteen required input records,
so its integrity-check count and total check count differ. Elapsed time and
the total check count should not be compared as exact expected outputs.
The historical report is evidence of the earlier run, not a run on the
current public archive. See ../PROVENANCE.md for the input and
source-hash correspondence.

WHAT THE FULL RUN CHECKS

1. Archive hashes, member names and the complete closed-domain input cover.
2. Global anchor and count bounds, uniform and regional localization
   estimates, phase constraints and candidate polar bounds.
3. Fixed root intersections, intrinsic residual lower bounds, overlap and
   projected bounds, stationary estimates and all 480 degree-six scalar
   certificates.
4. Physical curvature, the explicit finite normal comparison, and the full
   signed or unsigned remainder bounds for the 228 adopted local regions.
   These comparisons retain the mixed, same-group, radial-weight and phase
   terms required by the proof.
5. The complete 7,320-cell cover: 2,039 cells are excluded by count bounds;
   the remaining 5,281 cells are covered by 228 local regions, each with a
   margin greater than 1/10000.

The full verifier performs substantial arithmetic on fixed witnesses. It
does not search for new witnesses or subdivide the saved regions. The
analytic identities, geometric implications, propagation to all integers
N >= 180, and equality classification are proved in the manuscript. The
software checks the arithmetic part of that proof.

HOW THE LOCAL RECORDS ARE USED

Saved status fields describe the particular estimates present when a record
was produced. They are not acceptance criteria for the final proof. Some
records carry FAIL_LOCAL_MARGIN or DIAGNOSTIC_CHANGED_MEAN_ONLY labels for
earlier aggregate estimates or partial diagnostics. The verifier reconstructs
the adopted combinations below and checks their final margins directly.

Profile       Regions   Adopted comparison
odd_3_4          60      PROFILE_180.json
odd_11_4         53      PROFILE_180.json
r2_3 (C = 3)    55      PROFILE_180.json together with the mean-curvature
                        estimate in STRESS_SAVED_NORMAL.json. The verifier
                        reconstructs the complete normal comparison using
                        that estimate and the original remainder bounds.
r2_1 (C = 1)    60      FROZEN_FULL_182.json supplies the baseline quantities;
                        REFINED_182_NORMAL.json supplies the complete refined
                        comparison, including its signed remainder bounds.

The corresponding member names in supplement.zip are:
  research/codim2_below200_20261017/local/PROFILE_180.json
  research/codim2_residue2_20261018/curvature/STRESS_SAVED_NORMAL.json
  research/codim2_residue2_20261018/local/FROZEN_FULL_182.json
  research/codim2_residue2_20261018/local/REFINED_182_NORMAL.json

These are identifiers inside the archive, not paths to external runtime
dependencies. The full verification also reads the other ten records listed
in INDEX.json. The archive is read in place; no extraction is needed.

THE C = 3 WORST REGION

The saved report ../validation/C3_WORST_ACCEPTANCE.json contains the r2_3
region with zero-based indices (u_index, w_index) = (17, 23). Its detailed
record is copied from the historical full acceptance report and contains
162 accepted checks. It also includes a shorter ledger of outward rational
bounds for this region.

The full verifier reconstructs all 55 r2_3 regional margins, checks that
(17, 23) attains their minimum, and includes the resulting detailed record
under C3_worst in its output. The saved C3 report is a reference for comparing
the output; the verifier computes these checks from the certificate inputs.

OPTIONAL READ-ONLY WRAPPER

From the repository root, CPython users may run:
  python -B reproduction/validation/readonly_run.py

This wrapper installs a CPython audit hook that rejects write-mode file
opens and the listed filesystem, subprocess and socket operations used by
the verifier. It is not a security sandbox for arbitrary code. The verifier
itself neither writes nor extracts files, and the wrapper disables bytecode
cache writes. Reports and progress still use stdout and stderr.

DATA PROVENANCE

See ../PROVENANCE.md for the correspondence between the historical reports
and public inputs, including the metadata redactions and the limits of the
recorded comparisons.
