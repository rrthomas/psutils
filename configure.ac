# configure.ac for psutils
# Process this file with autoconf to produce a configure script

AC_INIT(psutils, 1.90, rrt@sc3d.org)
AC_CONFIG_AUX_DIR([build-aux])
AM_INIT_AUTOMAKE([-Wall -Werror foreign 1.11])

AC_PATH_PROG(PERL, perl)

# Generate output files
AC_OUTPUT([
	Makefile
	epsffit
	extractres
	includeres
	psbook
	psjoin
	psnup
	psresize
	psselect
	pstops
	],
	[chmod +x epsffit extractres includeres psbook psjoin psnup psresize
	    psselect pstops]
)
