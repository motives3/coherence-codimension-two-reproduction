# Exact complex coherence in codimension two

Xuan Li · Preprint

[Read the PDF](paper.pdf) · [Download the LaTeX source](source.zip)

The paper determines the minimum coherence of N unit vectors in
C^(N-2) for every integer N >= 180. It gives an explicit construction and
classifies all equality cases, including for the corresponding general
matrix problem. The sufficient threshold 180 is not claimed minimal.

## Files

`main.tex` is the entry point. The five files in `sections/` and five files
in `appendices/`, together with the main document and bibliography, are
listed in [SHA256SUMS.txt](SHA256SUMS.txt). The source ZIP contains the
same 13 TeX, BibTeX and BBL files available in this directory.

`main.bbl` is included so the paper can be compiled without running BibTeX.
`references.bib` is provided for readers who wish to regenerate it.
The source uses standard LaTeX packages and relative input paths.

## Compile

Extract `source.zip` into a fresh directory. From that directory, run:

```sh
pdflatex -no-shell-escape -interaction=nonstopmode -halt-on-error main.tex
pdflatex -no-shell-escape -interaction=nonstopmode -halt-on-error main.tex
pdflatex -no-shell-escape -interaction=nonstopmode -halt-on-error main.tex
```

The output is `main.pdf`. The three passes populate the contents and
cross-references. The supplied `paper.pdf` has 47 pages.
Compilation requires a TeX installation with `geometry`, the AMS packages,
`mathtools`, `booktabs`, `array`, `longtable`, `fontenc`, `lmodern`,
`hyperref` and `microtype`. It does not require Python, the certificate
archive, network access or another checkout.

## Reproduction materials

The [repository guide](../README.md) describes the exact certificates and
their verification. Compiling this paper does not verify the arithmetic
certificates or rerun any mathematical computation.

The paper cites the preserved
[b7a51dbc324b mathematical snapshot](https://github.com/motives3/coherence-codimension-two-reproduction/tree/b7a51dbc324ba260a92c2fafd3642e686cefe91a).
The separate software archive uses the
[7fa9cdc7472c snapshot](https://github.com/motives3/coherence-codimension-two-reproduction/tree/7fa9cdc7472c726c0db2dad8efd92f5f5ccabe57),
which adds the detailed AI disclosure without changing the certificates
or verification code.

## Citation

```bibtex
@unpublished{Li2026ExactComplexCoherence,
  author = {Xuan Li},
  title = {Exact complex coherence in codimension two},
  year = {2026},
  note = {Preprint},
  url = {https://github.com/motives3/coherence-codimension-two-reproduction/blob/main/paper/paper.pdf}
}
```

## AI disclosure and rights

The Acknowledgments state the use of OpenAI Codex, including GPT-6 Astra
with the Ultra reasoning setting, in mathematical exploration and argument
development, computational work, and manuscript drafting and revision.
They retain the author's responsibility for all content. The
[repository disclosure](../README.md#use-of-generative-ai) gives the same
account.

The manuscript has a [separate rights notice](LICENSE.txt). Its public
availability does not place it under the licenses used for the software
or reproduction data.
