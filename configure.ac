# configure.ac for psutils
# Process this file with autoconf to produce a configure script

AC_INIT(psutils, 2.03, rrt@sc3d.org)
AC_CONFIG_AUX_DIR([build-aux])
AM_INIT_AUTOMAKE([-Wall foreign 1.11])

gl_EARLY
gl_INIT
AC_PATH_PROG(PERL, perl)

# Require GNU Make
AX_CHECK_GNU_MAKE([], [AC_MSG_ERROR([make must be GNU Make])])

# help2man
# Set a value even if not found, so that an invocation via build-aux/missing works
AC_PATH_PROG([HELP2MAN], [help2man], [help2man])

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
