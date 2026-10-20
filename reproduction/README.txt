EXACT COMPLEX COHERENCE IN CODIMENSION TWO
Certificate data and code supporting the proof for N >= 180.

Public repository:
https://github.com/motives3/coherence-codimension-two-reproduction
Python >= 3.10, standard library only. From this directory:
  python -B check_package.py
This checks file hashes, archive membership and local dependencies.
It does not verify the mathematical inequalities.

To verify all certificates:
  python -B certificate/verify_certificates.py
or:
  python -B validation/readonly_run.py
Both commands perform arithmetic on the saved inputs. A successful full run
exits with code 0 and reports status PASS and complete_arithmetic_acceptance
true. Partial diagnostics report PASS_PARTIAL. Reports go to stdout and
progress to stderr.

certificate/ARITHMETIC_README.txt explains the commands, adopted profiles,
coverage and C = 3 record. PROVENANCE.md describes how the public inputs
correspond to the saved historical reports.

The analytic reductions, extension to all N >= 180, and equality argument
are in the manuscript in ../paper/. The separate software deposit contains
the reproduction materials only.

This guide describes the current GitHub distribution. The software archive
at https://doi.org/10.5281/zenodo.23477764 preserves version 1.0.0 from
commit 7fa9cdc7472c726c0db2dad8efd92f5f5ccabe57. Its certificates,
verifier sources and saved reports match those distributed here;
reader documentation has since been updated.

All runtime paths are relative to the scripts. Code: MIT. Data and
documentation: CC BY 4.0. See LICENSE.txt and ../LICENSE.md.
