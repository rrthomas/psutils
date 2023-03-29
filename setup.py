import os
from build_manpages.build_manpages import build_manpages, get_install_cmd, get_build_py_cmd # type: ignore
from setuptools import setup
from setuptools.command.build_py import build_py
from setuptools.command.install import install

# Override build_py command to run help2man
class my_build_py(build_py):
    def build_manpage(self, name):
        self.spawn(['help2man', '--no-info', '--no-discard-stderr', f'--include={name}-include.man', f'--include=man-include.man', f'--output={name}.1', f'./{name}'])

    def run(self):
        os.environ['COLUMNS'] = '999'
        self.build_manpage('pstops')
        self.build_manpage('psbook')
        self.build_manpage('psselect')
        self.build_manpage('psnup')
        self.build_manpage('psresize')
        self.build_manpage('psjoin')
        self.build_manpage('extractres')
        self.build_manpage('includeres')
        self.build_manpage('epsffit')
        super().run()

# Override build_manpages command to do nothing
class my_build_manpages(build_manpages):
    def run(self):
        pass

setup(
    cmdclass={
        'build_manpages': my_build_manpages,
        'build_py': get_build_py_cmd(my_build_py),
        'install': get_install_cmd(install),
    }
)

# Test we have 'paper' (from libpaper) installed
import subprocess
try:
    subprocess.call(['paper'])
except OSError:
    raise SystemExit('psutils needs libpaper >= 2 to work')
