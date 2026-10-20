# Exact complex coherence in codimension two

Xuan Li · Preprint

[Read the paper](paper/paper.pdf) · [LaTeX source and build instructions](paper/README.md) ·
[Certificate guide](reproduction/certificate/ARITHMETIC_README.txt)

The paper determines the minimum coherence of $N$ unit vectors in
$\mathbb{C}^{N-2}$ for every integer $N \ge 180$. It gives an explicit
four-block construction and classifies all equality cases, both for vector
families and for the corresponding matrix problem.

For integers $1 \le n < N$, minimum coherence is defined by

```math
\mu_{\mathbb{C}}(n,N)
=\min_{\substack{v_1,\ldots,v_N\in\mathbb{C}^n\\
\lVert v_i\rVert_2=1\ (1\le i\le N)}}
\max_{i\ne j}\lvert v_i^*v_j\rvert.
```

Here $v_i^*v_j$ is the Hermitian inner product, conjugate-linear in its first
argument. The code verifies the finite arithmetic estimates in the proof;
the analytic reductions, extension to the full range and equality
classification are established in the paper.

## Verification

The verifier requires **Python 3.10 or later**, with no third-party packages.
From the repository root, first check the files and dependencies:

```sh
python -B reproduction/check_package.py
```

Then run the arithmetic verification:

```sh
python -B reproduction/certificate/verify_certificates.py
```

This recomputes the bounds from the saved inputs through the global,
continuous and local stages. A successful full run exits with code 0 and
reports `"status": "PASS"` and `"complete_arithmetic_acceptance": true`.

The optional wrapper uses a CPython audit hook to reject file writes,
subprocess creation and socket connections during verification:

```sh
python -B reproduction/validation/readonly_run.py
```

Full verification can take substantial time. Reports go to standard output
and progress messages to standard error. The
[certificate guide](reproduction/certificate/ARITHMETIC_README.txt) describes
partial runs, the four certificate profiles, the $C = 3$ boundary case and
the limits of the audit hook.

## Certificate data

The certificates cover 7,320 budget cells: 2,039 are excluded by count
bounds, and 5,281 are covered by 228 local regions. Each accepted local
region has a certified margin greater than $10^{-4}$.

| Files | Purpose |
| --- | --- |
| [`reproduction/certificate/`](reproduction/certificate/) | Fourteen exact JSON witnesses in `supplement.zip`, certificate index and verifier |
| [`reproduction/validation/`](reproduction/validation/) | Arithmetic modules, regression sources and saved acceptance reports |
| [Provenance](reproduction/PROVENANCE.md) | Correspondence between the saved reports and public certificate inputs |
| [`REPOSITORY_MANIFEST.json`](REPOSITORY_MANIFEST.json) | File hashes |

## Citation

| Archived material | Version DOI |
| --- | --- |
| Paper PDF and LaTeX source | [10.5281/zenodo.23495415](https://doi.org/10.5281/zenodo.23495415) |
| Reproduction materials, version 1.0.0 | [10.5281/zenodo.23477764](https://doi.org/10.5281/zenodo.23477764) |

Use the [paper citation](paper/README.md#citation) when citing the mathematical
results and [CITATION.cff](CITATION.cff) for the reproduction materials.
When using a GitHub checkout, also record its commit.

The paper cites the
[b7a51dbc324b snapshot](https://github.com/motives3/coherence-codimension-two-reproduction/tree/b7a51dbc324ba260a92c2fafd3642e686cefe91a).
Software version 1.0.0 archives the
[7fa9cdc7472c snapshot](https://github.com/motives3/coherence-codimension-two-reproduction/tree/7fa9cdc7472c726c0db2dad8efd92f5f5ccabe57),
which contains the same certificates and verifier with the detailed AI
disclosure.

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
