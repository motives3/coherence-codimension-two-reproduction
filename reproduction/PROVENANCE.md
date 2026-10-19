# Certificate provenance

The public archive contains fourteen JSON witnesses used by the arithmetic
verifier for the sufficient threshold N >= 180. The saved acceptance reports
record computations performed before this public archive was assembled.
This document explains how those reports correspond to the distributed inputs.

## Saved acceptance and public inputs

[ARITHMETIC_ACCEPTANCE.json](validation/ARITHMETIC_ACCEPTANCE.json) records
5,266,235 checks on an earlier archive containing 1,007 members. The fourteen
inputs consumed by its mathematical stages are the witnesses included in
[supplement.zip](certificate/supplement.zip). The four arithmetic verifier
files are unchanged from that acceptance run.

Eleven witnesses are byte-identical to the historical inputs. In the other
three, seventeen keys within `source_sha256` metadata were replaced by neutral
labels to remove machine-specific paths. The preparation comparison checked
that the source digest values and all other bytes were unchanged. The
mathematical stages do not read these labels.

[PRIVACY_TRANSFORM.json](PRIVACY_TRANSFORM.json) records the changed locations
and old and new digests.
[PRIOR_ACCEPTANCE_BINDING.json](validation/PRIOR_ACCEPTANCE_BINDING.json)
binds the historical report, its inputs, the public inputs and the verifier
sources. [INDEX.json](certificate/INDEX.json) lists the public archive members
with their sizes and hashes.

The removed path strings are not distributed, so a reader cannot reconstruct
the three original full-file digests from this package alone. The packaging
check validates the current hashes and recorded correspondence; it does not
repeat the original byte comparison or establish a new mathematical acceptance.
The full verifier can be run directly on the public inputs.

The saved report is a historical result, not the output of a run on the public
archive. Its check count includes integrity checks for 1,007 archive members;
a run on the fourteen-member public archive therefore has a different total
check count. Elapsed times and total check counts should not be used as exact
output targets. The [arithmetic guide](certificate/ARITHMETIC_README.txt)
gives the acceptance fields and exit status to inspect.

## Diagnostic records and adopted estimates

The witnesses retain the names and status fields assigned when they were
produced. Some records include failed or diagnostic alternatives alongside
estimates used in the final proof. These overall status labels are not the
verifier's acceptance criteria: it reconstructs the adopted inequalities from
the saved inputs. The arithmetic guide identifies the sources used for each
of the four profiles and explains the C = 3 record.

Paths beginning with `research/` are fixed identifiers inside the archive.
They preserve the correspondence with the saved reports and are not external
runtime dependencies.

## Version correspondence

The arithmetic evidence originated with manuscript v2.1 and was retained in
the v2.5 submission baseline. Subsequent editorial preparation did not change
the threshold, certificates or arithmetic verifier. These version labels
describe the manuscript history, not separate mathematical acceptance runs.

The manuscript cites the public snapshot
[b7a51dbc324ba260a92c2fafd3642e686cefe91a](https://github.com/motives3/coherence-codimension-two-reproduction/tree/b7a51dbc324ba260a92c2fafd3642e686cefe91a).
The documentation revision of 19 October 2026 preserves that commit and the
original certificate archive, index, Python sources, saved reports and input
binding records. It updates the reader documentation, citation metadata and
distribution manifests. No mathematical verification, regression tests,
searches or optimization were rerun for this documentation revision.

## File manifests

[PUBLIC_MANIFEST.json](PUBLIC_MANIFEST.json) records the files in the
`reproduction/` directory, excluding the manifest itself.
[REPOSITORY_MANIFEST.json](../REPOSITORY_MANIFEST.json) additionally covers the
root documentation, citation metadata and Git configuration files, excluding
itself. These distribution hashes change when documentation changes. The
certificate archive and its index retain their original hashes.
