# configure.ac for psutils
# Process this file with autoconf to produce a configure script

AC_INIT(psutils, 1.92, rrt@sc3d.org)
AC_CONFIG_AUX_DIR([build-aux])
AM_INIT_AUTOMAKE([-Wall -Werror foreign 1.11])

gl_EARLY
gl_INIT
AC_PATH_PROG(PERL, perl)

# Generate output files
AC_CONFIG_FILES([
  Makefile
  epsffit.in
  extractres.in
  includeres.in
  psbook.in
  psjoin.in
  psnup.in
  psresize.in
  psselect.in
  pstops.in
])
AC_CONFIG_FILES([pre-inst-env], [chmod +x pre-inst-env])
AC_OUTPUT
