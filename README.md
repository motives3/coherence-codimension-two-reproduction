# Exact complex coherence in codimension two: reproduction materials

Exact certificate data and independent arithmetic verification code associated
with manuscript **v2.5**, for the fixed sufficient threshold **N >= 180**.
The threshold is not claimed minimal.

This repository distributes only the sanitized reproduction package. The
manuscript source and PDF are not included. The analytic reductions,
propagation to all N >= 180 and equality classification remain in the
manuscript; the data and code here cover its computational component.

## Contents

| Path | Contents |
| --- | --- |
| `reproduction/certificate/` | Fourteen exact JSON witnesses in `supplement.zip`, index and verifier entry point |
| `reproduction/validation/` | Three arithmetic modules, regression sources and historical acceptance records |
| `reproduction/check_package.py` | Fast packaging and dependency check |
| `reproduction/PRIVACY_TRANSFORM.json` | Metadata-only changes and their limits |
| `reproduction/validation/PRIOR_ACCEPTANCE_BINDING.json` | Historical and current input hashes |
| `REPOSITORY_MANIFEST.json` | File hashes for this distribution |

## Requirements and quick check

Python **3.10 or later**, standard library only. From the repository root:

```sh
python -B reproduction/check_package.py
```

This checks hashes, archive membership, the recorded metadata transfer and
local module imports. It does not perform mathematical verification. Runtime
dependencies are resolved relative to the scripts; no private checkout,
manuscript directory or network service is needed.

## Independent arithmetic verification

```sh
python -B reproduction/certificate/verify_certificates.py
```

The optional CPython read-only wrapper is:

```sh
python -B reproduction/validation/readonly_run.py
```

These commands perform substantial arithmetic on fixed witnesses. Read the
[arithmetic guide](reproduction/certificate/ARITHMETIC_README.txt) before
interpreting stage outputs. No mathematical verification, regression test,
search or optimization was rerun to prepare this public distribution.

## Evidence and metadata

The unchanged historical full report records 5,266,235 checks on an earlier
1,007-member archive. This distribution contains its fourteen required JSON
witnesses and the same four arithmetic verifier files.

Eleven witnesses are byte-identical to the historical inputs. In the other
three, 17 machine-path keys within inert `source_sha256` metadata were
replaced by neutral labels. All other bytes and source digest values were
checked unchanged. The archive, index and packaging manifests have new hashes.
The historical acceptance is not presented as a run on this distribution.
The public packaging check does not reconstruct the omitted private labels;
the full arithmetic verifier remains available for independent use.

## License and attribution

- Python code and Git configuration files: **MIT**.
- Witness data, reports and distribution documentation: **CC BY 4.0**.

See [LICENSE.md](LICENSE.md) and the included license texts. Attribute this
distribution by its project title and repository URL; repository contributor
identities do not determine manuscript authorship. No arXiv identifier or
Zenodo DOI has been assigned to this distribution.
