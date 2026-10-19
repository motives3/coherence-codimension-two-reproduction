# Exact complex coherence in codimension two: reproduction materials

This repository accompanies *Exact complex coherence in codimension two* by
Xuan Li. It contains exact certificate data and Python code for verifying the
computer-assisted estimates used in the proof for **N >= 180**.

The manuscript determines the minimum coherence of N unit vectors in
C^(N-2), gives an explicit construction, and classifies the equality cases
in this range. The code checks the finite arithmetic estimates. The analytic
reductions, extension to all N >= 180, and equality argument are given in the
manuscript. Its PDF and source are not included in this repository. The
threshold 180 is sufficient; no claim of minimality is made.

## Contents

| Path | Contents |
| --- | --- |
| `reproduction/certificate/` | Fourteen exact JSON witnesses in `supplement.zip`, index and verifier entry point |
| `reproduction/validation/` | Three arithmetic modules, regression sources and historical acceptance records |
| `reproduction/check_package.py` | Fast packaging and dependency check |
| [Arithmetic guide](reproduction/certificate/ARITHMETIC_README.txt) | Commands, expected output, adopted certificates and coverage |
| [Provenance](reproduction/PROVENANCE.md) | Evidence history and correspondence between the saved reports and public inputs |
| [CITATION.cff](CITATION.cff) | Citation metadata |
| `REPOSITORY_MANIFEST.json` | File hashes for this distribution |

## Requirements and quick check

Python **3.10 or later**, standard library only. From the repository root:

```sh
python -B reproduction/check_package.py
```

The quick check verifies file hashes, archive membership, the recorded input
correspondence, and module availability. Success produces a JSON report with
`"status": "PASS"` and `"mathematical_verification_executed": false`.
It checks the package, not the mathematical inequalities.

All runtime dependencies are included or belong to the Python standard
library. Script locations determine the input paths, so the commands need
neither network access nor another checkout.

## Verify the certificates

```sh
python -B reproduction/certificate/verify_certificates.py
```

The verifier recomputes the bounds from the saved inputs without importing
the code that generated the certificates. It runs the global, continuous and
local stages in order. A successful full run exits with code 0 and reports
`"status": "PASS"` and `"complete_arithmetic_acceptance": true`.

The optional wrapper uses a CPython audit hook to reject file writes,
subprocess creation and socket connections during verification:

```sh
python -B reproduction/validation/readonly_run.py
```

Both commands perform substantial arithmetic on the fixed certificates;
they do not search for new certificates. Reports go to standard output and
progress messages to standard error. The [arithmetic guide](reproduction/certificate/ARITHMETIC_README.txt)
explains partial runs, the four adopted profiles, the C = 3 boundary case,
and the limits of the audit hook.

## Evidence and citation

The certificates cover 7,320 budget cells: 2,039 are excluded by count
bounds, and 5,281 are covered by 228 local regions. Each accepted local
region has a certified margin greater than 1/10000.

The saved acceptance reports predate the public packaging step. Their
relationship to the fourteen public inputs is described in
[Provenance](reproduction/PROVENANCE.md), including the metadata changes and
the interpretation of diagnostic failure labels.

Use [CITATION.cff](CITATION.cff) to cite the reproduction materials and record
the commit used. The manuscript cites the preserved
[b7a51dbc324b snapshot](https://github.com/motives3/coherence-codimension-two-reproduction/tree/b7a51dbc324ba260a92c2fafd3642e686cefe91a).

## Use of generative AI

OpenAI's Codex and ChatGPT were used during this project to assist with
literature searches, mathematical exploration, the development and checking
of proof arguments, implementation of certificate-generation and verification
code, and drafting and revision of the manuscript. The author assumes
responsibility for all content, including the mathematical claims,
references, code, and final text.

## License and attribution

- Python code and Git configuration files: **MIT**.
- Witness data, reports and distribution documentation: **CC BY 4.0**.

See [LICENSE.md](LICENSE.md) for the file scopes and attribution requirements.
