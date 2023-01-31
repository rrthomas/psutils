# configure.ac for psutils
# Process this file with autoconf to produce a configure script

AC_INIT(psutils, 2.10, rrt@sc3d.org)
AC_CONFIG_AUX_DIR([build-aux])
AM_INIT_AUTOMAKE([-Wall foreign 1.11])

gl_EARLY
gl_INIT
AM_PATH_PYTHON

# Require GNU Make
AX_CHECK_GNU_MAKE([], [AC_MSG_ERROR([make must be GNU Make])])

# Require libpaper
AC_PATH_PROG(PAPER, paper)
AS_IF([test -z "$ac_cv_path_PAPER"], AC_MSG_ERROR([psutils needs libpaper to work]))

# help2man
# Set a value even if not found, so that an invocation via build-aux/missing works
AC_PATH_PROG([HELP2MAN], [help2man], [help2man])

# Generate output files
AC_CONFIG_FILES([Makefile])
AC_CONFIG_FILES([pre-inst-env], [chmod +x pre-inst-env])
AC_CONFIG_FILES([psbook], [chmod +x psbook])
AC_CONFIG_FILES([psjoin], [chmod +x psjoin])
AC_CONFIG_FILES([psnup], [chmod +x psnup])
AC_CONFIG_FILES([pstops], [chmod +x pstops])
AC_CONFIG_FILES([psresize], [chmod +x psresize])
AC_CONFIG_FILES([psselect], [chmod +x psselect])
AC_CONFIG_FILES([includeres], [chmod +x includeres])
AC_CONFIG_FILES([extractres], [chmod +x extractres])
AC_CONFIG_FILES([epsffit], [chmod +x epsffit])
AC_OUTPUT
