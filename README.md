# Exact complex coherence in codimension two

This repository accompanies *Exact complex coherence in codimension two* by
Xuan Li. It provides the [paper PDF](paper/paper.pdf), its
[LaTeX source and build instructions](paper/README.md), and exact certificate
data and Python code for verifying the computer-assisted estimates used in
the proof for **N >= 180**.

The manuscript determines the minimum coherence of N unit vectors in
C^(N-2), gives an explicit construction, and classifies the equality cases
in this range. The code checks the finite arithmetic estimates. The analytic
reductions, extension to all N >= 180, and equality argument are given in the
manuscript. The manuscript is provided as a preprint. The threshold 180 is
sufficient; no claim of minimality is made.

## Contents

| Path | Contents |
| --- | --- |
| [Paper](paper/paper.pdf) | Preprint PDF |
| [LaTeX source](paper/) | Main document, sections, appendices and bibliography; [source ZIP](paper/source.zip) |
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

Use the [paper citation](paper/README.md#citation) when citing the mathematical
results. Use [CITATION.cff](CITATION.cff) to cite the reproduction materials
and record the commit used. The manuscript cites the preserved
[b7a51dbc324b snapshot](https://github.com/motives3/coherence-codimension-two-reproduction/tree/b7a51dbc324ba260a92c2fafd3642e686cefe91a).

The separate software archive corresponds to the
[7fa9cdc7472c snapshot](https://github.com/motives3/coherence-codimension-two-reproduction/tree/7fa9cdc7472c726c0db2dad8efd92f5f5ccabe57),
which contains the reproduction materials and the detailed AI disclosure.
The manuscript files were added afterward; that archive remains unchanged.

## Use of generative AI

OpenAI's Codex was used extensively in the research and preparation of the
manuscript, including use of GPT-6 Astra with the Ultra reasoning setting.
Its use included literature searches and comparisons with earlier results
(Section 2); exploration and development of the four-block construction
and its algebraic formulas (Sections 3 and 6); and formulation, refinement,
and critical examination of arguments concerning the matrix reduction,
global localization, local comparison, and equality cases (Sections 4, 7,
and 8). Section numbers refer to the accompanying manuscript.

Codex was also used in developing the computational work associated with
Section 9 and this reproduction package. This included implementing and
revising code for numerical exploration, certificate generation,
rational-arithmetic verification, and regression tests.

AI-generated drafts of mathematical arguments and explanatory prose were
used and revised during the preparation of the manuscript. Codex was also
used to organize the presentation, revise notation and cross-references,
and edit the English.

The author assumes responsibility for all content, including the
mathematical claims, references, code, and final text.

## License and attribution

- Python code and Git configuration files: **MIT**.
- Witness data, reports and distribution documentation: **CC BY 4.0**.
- Manuscript PDF and LaTeX/BibTeX files: **rights retained by Xuan Li**;
  see the [manuscript rights notice](paper/LICENSE.txt).

See [LICENSE.md](LICENSE.md) for the file scopes and attribution requirements.
