# Exact complex coherence in codimension two

Xuan Li · Preprint

[Read the PDF](paper.pdf) · [Download the LaTeX source](source.zip) ·
[Archived paper](https://doi.org/10.5281/zenodo.23495415)

The paper determines the minimum coherence
$\mu_{\mathbb{C}}(N-2,N)$ of $N$ unit vectors in
$\mathbb{C}^{N-2}$ for every integer $N \ge 180$. It gives an explicit
construction and classifies all equality cases in both the coherence
problem and the corresponding general matrix problem.

## Compile the paper

The [source ZIP](source.zip) contains the 13 source files in this directory:
`main.tex`, five sections, five appendices, `references.bib` and `main.bbl`.
File hashes are listed in [SHA256SUMS.txt](SHA256SUMS.txt).

`main.bbl` is included so the paper can be compiled without running BibTeX.
`references.bib` is provided for readers who wish to regenerate it.

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
`hyperref` and `microtype`.

## Reproduction materials

The [repository guide](../README.md#verification) gives the commands for
verifying the exact arithmetic certificates.

The paper cites the
[b7a51dbc324b mathematical snapshot](https://github.com/motives3/coherence-codimension-two-reproduction/tree/b7a51dbc324ba260a92c2fafd3642e686cefe91a).
The [separate software archive](https://doi.org/10.5281/zenodo.23477764),
version 1.0.0, corresponds to the
[7fa9cdc7472c snapshot](https://github.com/motives3/coherence-codimension-two-reproduction/tree/7fa9cdc7472c726c0db2dad8efd92f5f5ccabe57),
which contains the same certificates and verifier with the detailed AI
disclosure.

## Citation

Use the paper DOI [10.5281/zenodo.23495415](https://doi.org/10.5281/zenodo.23495415)
when citing the mathematical results:

```bibtex
@unpublished{Li2026ExactComplexCoherence,
  author = {Xuan Li},
  title = {Exact complex coherence in codimension two},
  year = {2026},
  note = {Preprint},
  doi = {10.5281/zenodo.23495415},
  url = {https://doi.org/10.5281/zenodo.23495415}
}
```

For the reproduction materials, use the separate software DOI
[10.5281/zenodo.23477764](https://doi.org/10.5281/zenodo.23477764)
and the metadata in [CITATION.cff](../CITATION.cff).

## AI disclosure and rights

The Acknowledgments state the use of OpenAI Codex, including GPT-6 Astra
with the Ultra reasoning setting, in mathematical exploration and argument
development, computational work, and manuscript drafting and revision.
The author takes responsibility for all content. The
[repository disclosure](../README.md#use-of-generative-ai) gives the same
account.

The manuscript has a [separate rights notice](LICENSE.txt). Its public
availability does not place it under the licenses used for the software
or reproduction data.
