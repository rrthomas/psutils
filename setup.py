from build_manpages.build_manpages import build_manpages, get_install_cmd, get_build_py_cmd # type: ignore
from setuptools import setup

setup(
    cmdclass={ # type: ignore
        'build_manpages': build_manpages,
        'build_py': get_build_py_cmd(),
        'install': get_install_cmd(),
    }
)

# Test we have 'paper' (from libpaper) installed
import subprocess
try:
    subprocess.check_output(['paper'])
except OSError:
    raise SystemExit('psutils needs libpaper >= 2 to work')
