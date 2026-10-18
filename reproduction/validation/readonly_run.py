"""Run the portable verifier with a process-wide write/execute/network guard.

The caller may redirect stdout/stderr before starting this process. The guard
applies to all Python imports and arithmetic acceptance thereafter. No files
are created by this wrapper. An attempted mutation is a validation failure.
"""
import sys
sys.dont_write_bytecode = True
import os
from pathlib import Path
import runpy

WRITE_FLAGS = os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_TRUNC | os.O_APPEND
MUTATIONS = {'os.remove','os.rename','os.rmdir','os.mkdir','os.link','os.symlink',
             'os.truncate','os.chmod','os.chown','os.utime','os.system',
             'subprocess.Popen','socket.connect','socket.bind'}

def readonly(event, args):
    if event == 'open':
        mode, flags = args[1], args[2]
        if (isinstance(mode, str) and any(c in mode for c in 'wax+')) or flags & WRITE_FLAGS:
            raise RuntimeError('read-only audit rejected file write: '+str(args[0]))
    if event in MUTATIONS:
        raise RuntimeError('read-only audit rejected operation: '+event)

if __name__ == '__main__':
    script = Path(__file__).resolve().parent.parent/'certificate/verify_certificates.py'
    sys.argv[0] = str(script)
    sys.addaudithook(readonly)
    runpy.run_path(str(script), run_name='__main__')
