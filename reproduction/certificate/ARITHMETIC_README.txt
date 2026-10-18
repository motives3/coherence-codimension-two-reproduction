INDEPENDENT FIXED-WITNESS ACCEPTANCE -- V2.5 REPRODUCTION DISTRIBUTION
Evidence origin: v2.1.

Required relative structure:
  certificate/verify_certificates.py
  certificate/supplement.zip
  certificate/INDEX.json
  validation/global_arithmetic.py
  validation/continuous_arithmetic.py
  validation/local_arithmetic.py

Python >= 3.10, standard library only. Full independent reproduction:
  python -B certificate/verify_certificates.py
The default runs all three stages. --stage global and --stage continuous
are partial diagnostics. --stage local runs its prerequisites but is also
labeled partial. Only the default all-stage run reports complete acceptance.
Use an absolute script path to run from any working directory. --archive
and --index can select alternative locations for those two input files.

The archive contains fourteen JSON inputs. Eleven are byte-identical to the
historical acceptance; three contain only neutral replacements of 17 inert
source_sha256 metadata keys. All arithmetic verifier files are unchanged.
The historical report is not a run on this sanitized archive. See
../PRIVACY_TRANSFORM.json and ../validation/PRIOR_ACCEPTANCE_BINDING.json.

The optional validation/readonly_run.py installs an audited CPython guard
over the reviewed verifier's file I/O, subprocess calls and socket connections.
It is not a security sandbox for arbitrary code. The verifier itself extracts
or writes no files. Reports go to stdout; progress goes to stderr. The caller
may redirect either stream. No old historical module is imported or executed.

SCOPE OF A FULL RUN
1. Archive hashes/membership and the complete closed-domain input cover.
2. Global anchor/count bounds, uniform and regional localization budgets,
   phase interfaces and candidate polar bounds.
3. Every fixed root intersection and intrinsic residual lower bound; complete
   overlap/projected/stationary bounds; all 480 degree-six scalar certificates.
4. Physical curvature, finite normal optimization and complete signed or
   unsigned remainder on all 228 adopted regions, with all mixed, same-group,
   radial-weight and phase constraints retained.
5. Strict margins > 1/10000 on the 7,320-cell cover.

The fourteen saved witnesses are not re-searched or subdivided by the full
verifier. Nevertheless a full run is substantial arithmetic recomputation;
it was intentionally not repeated to create this package. check_package.py
at the package root performs only packaging/dependency checks.

The analytic identities, geometric implications, propagation to every integer
N >= 180, and equality argument remain manuscript proof obligations. This is
a computer-assisted proof, not proof-assistant formalization. Prior saved
regression outputs are labeled as prior results, not new packaging runs.
