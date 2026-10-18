#!/usr/bin/env python3
"""Read-only packaging check for the metadata-sanitized v2.5 distribution.

Does not call mathematical verify() functions or reconstruct private labels.
"""
import argparse
import importlib
import json
from hashlib import sha256
from pathlib import Path, PurePosixPath
import sys

sys.dont_write_bytecode = True
BASE = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE / 'certificate'))
import verify_certificates as accepted_cli

def digest(path):
    h = sha256()
    with path.open('rb') as f:
        for block in iter(lambda: f.read(1 << 20), b''):
            h.update(block)
    return h.hexdigest()

def require(ok, label):
    if not ok:
        raise ValueError(label)

def safe_path(base, name):
    p = PurePosixPath(name)
    require(not p.is_absolute() and '..' not in p.parts and ':' not in name
            and '\\' not in name, 'safe relative path')
    path = base / name
    require(path.resolve().is_relative_to(base.resolve()), 'path containment')
    return path

def main():
    argparse.ArgumentParser(description=__doc__).parse_args()
    ctx = None
    try:
        manifest = json.loads((BASE / 'PUBLIC_MANIFEST.json').read_bytes())
        for rel, item in manifest['files'].items():
            path = safe_path(BASE, rel)
            require(path.stat().st_size == item['size'] and digest(path) == item['sha256'],
                    'public file binding ' + rel)
        report = json.loads((BASE / 'validation/ARITHMETIC_ACCEPTANCE.json').read_bytes())
        binding = json.loads((BASE / 'validation/PRIOR_ACCEPTANCE_BINDING.json').read_bytes())
        transform_path = safe_path(BASE, binding['transformation_record'])
        require(digest(transform_path) == binding['transformation_sha256'], 'transformation binding')
        transform = json.loads(transform_path.read_bytes())
        require(digest(BASE / 'validation/ARITHMETIC_ACCEPTANCE.json') == binding['prior_report_sha256'],
                'unchanged historical report')
        require(report['status'] == 'PASS' and report['complete_arithmetic_acceptance'],
                'historical complete acceptance, not a new run')
        require(report['input_sha256'] == binding['historical_input_sha256'], 'historical input hashes')
        require(report['verifier_sha256'] == binding['verifier_sha256'], 'historical source hashes')
        require(len(report['input_sha256']) == 14, 'fourteen historical inputs')
        changes = transform['changes']
        require(len(changes) == 3 and sum(x['changed_key_occurrences'] for x in changes.values()) == 17,
                'three metadata-only records, seventeen replacements')
        ctx = accepted_cli.Context(BASE / 'certificate/supplement.zip', BASE / 'certificate/INDEX.json')
        integrity = ctx.integrity()  # Hashes and ZIP membership only.
        require(integrity['sha256'] == binding['current_archive_sha256'], 'current archive binding')
        require(set(ctx.zip.namelist()) == set(report['input_sha256']) == set(binding['public_input_sha256']),
                'complete input closure')
        unchanged = 0
        for rel, old_hash in report['input_sha256'].items():
            raw = ctx.zip.read(rel)
            public_hash = sha256(raw).hexdigest()
            require(public_hash == binding['public_input_sha256'][rel], 'public input hash ' + rel)
            if rel not in changes:
                require(public_hash == old_hash, 'unchanged witness bytes ' + rel)
                unchanged += 1
                continue
            item = changes[rel]
            require(old_hash == item['historical_sha256'] and public_hash == item['public_sha256'],
                    'documented transformation digests ' + rel)
            require(len(item['replacements']) == item['changed_key_occurrences'], 'replacement count')
            obj = accepted_cli.unique_json(raw)
            seen = set()
            for replacement in item['replacements']:
                pointer = replacement['object_path']
                require(pointer and pointer[-1] == 'source_sha256', 'metadata scope')
                cursor = obj
                for part in pointer:
                    cursor = cursor[part]
                label = replacement['public_label']
                location = (tuple(pointer), label)
                require(location not in seen, 'unique metadata location')
                seen.add(location)
                require(label.startswith('redacted-source-'), 'neutral source label')
                require(cursor[label] == replacement['source_sha256_value'], 'preserved source digest')
        require(unchanged == 11, 'eleven byte-identical witnesses')
        for rel, expected in report['verifier_sha256'].items():
            require(digest(safe_path(BASE, rel)) == expected, 'unchanged arithmetic verifier ' + rel)
        modules = []
        for stage in ['global', 'continuous', 'local']:
            module = importlib.import_module(stage + '_arithmetic')
            path = Path(module.__file__).resolve()
            require(path == BASE / 'validation' / (stage + '_arithmetic.py'), 'local module origin')
            require(callable(module.verify), 'arithmetic entry point available, not called')
            modules.append(path.relative_to(BASE).as_posix())
        print(json.dumps({'status': 'PASS', 'scope': 'Packaging and recorded metadata transfer only',
              'fixed_threshold': 180, 'public_files_checked': len(manifest['files']),
              'archived_json_inputs': 14, 'byte_identical_json_inputs': 11,
              'metadata_redacted_json_inputs': 3, 'metadata_key_replacements': 17,
              'byte_identical_verifier_sources': 4, 'imported_local_modules': modules,
              'archive_sha256': integrity['sha256'],
              'historical_mathematical_check_count': report['checks'],
              'old_private_label_bytes_reconstructed': False,
              'mathematical_verification_executed': False, 'regression_tests_executed': False,
              'searches_executed': False, 'files_written_or_extracted': False}, indent=2))
        return 0
    except Exception as exc:
        print(json.dumps({'status': 'FAIL', 'error': str(exc),
                         'mathematical_verification_executed': False}, indent=2))
        return 1
    finally:
        if ctx is not None:
            ctx.zip.close()

if __name__ == '__main__':
    raise SystemExit(main())
