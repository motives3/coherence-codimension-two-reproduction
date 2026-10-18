EXACT COMPLEX COHERENCE IN CODIMENSION TWO
Reproduction materials associated with manuscript v2.5; N >= 180.

Public repository:
https://github.com/motives3/coherence-codimension-two-reproduction
The manuscript source and PDF are not distributed here.

Python >= 3.10, standard library only. From this directory:
  python -B check_package.py
checks packaging only. It does not execute mathematical verification.

Independent full arithmetic reproduction, if requested by the reader:
  python -B certificate/verify_certificates.py
or:
  python -B validation/readonly_run.py
These commands perform substantial arithmetic. Read certificate/ARITHMETIC_README.txt.
No full arithmetic run, regression run or search was performed for this release.

The archive contains the same fourteen witness records consumed by the
historical acceptance. Eleven are byte-identical. In three records, 17 keys
within source_sha256 metadata have been replaced by neutral labels. No values
or other bytes were changed; the four arithmetic verifier files are unchanged.
These labels are never consumed by the mathematical stages. See
PRIVACY_TRANSFORM.json and validation/PRIOR_ACCEPTANCE_BINDING.json.

The unchanged historical ARITHMETIC_ACCEPTANCE.json records 5,266,235 checks
on the earlier 1,007-member archive. It is not a run on this public distribution.
The packaging checker verifies eleven old input hashes and three new hashes;
it does not reconstruct the omitted private path strings. Independent readers
can execute the full arithmetic verifier against this archive and INDEX.

Some saved records contain FAIL labels for unused alternatives. The verifier
selects the adopted subproofs explicitly. The analytic reductions, infinite
range and equality argument remain in the manuscript, which is not included.

All runtime paths are relative to these files. Historical relative source
labels are provenance only and are not external runtime dependencies.
Code: MIT. Data and documentation: CC BY 4.0. See LICENSE.txt and ../LICENSE.md.
