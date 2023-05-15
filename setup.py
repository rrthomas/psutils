"""
setup.py for psutils
"""

import subprocess
from build_manpages.build_manpages import (  # type: ignore
    build_manpages,
    get_install_cmd,
    get_build_py_cmd,
)
from setuptools import setup

setup(
    cmdclass={
        "build_manpages": build_manpages,
        "build_py": get_build_py_cmd(),
        "install": get_install_cmd(),
    }
)

# Test we have 'paper' (from libpaper) installed
try:
    subprocess.check_output(["paper"])
except OSError as exc:
    raise SystemExit("psutils needs libpaper >= 2 to work") from exc
