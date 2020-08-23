import subprocess
import tempfile
import logging

log = logging.getLogger(__name__)


def gource(custom_log, args):
    with tempfile.NamedTemporaryFile() as fp:
        fp.write(custom_log.encode())
        subprocess.run([
            'gource',
            '--path',
            fp.name
        ], check=True)
