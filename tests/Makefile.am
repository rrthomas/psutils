# Tests Makefile.am
#
# Copyright (C) Reuben Thomas 2016-2019
# See LICENSE for license

TEST_EXTENSIONS = .sh
SH_LOG_COMPILER = $(srcdir)/tests/run-test

EMPTY =

TESTS = \
	%D%/psbook-20.sh \
	%D%/psbook-20-signature-4.sh \
	%D%/psbook-3.sh \
	%D%/psbook-3-signature-4.sh \
	%D%/psbook-invalid-signature-size.sh \
	%D%/psjoin-1-2.sh \
	%D%/psjoin-1-2-even.sh \
	%D%/psjoin-1-2-save.sh \
	%D%/psjoin-1-2-nostrip.sh \
	%D%/psnup-20-1.sh \
	%D%/psnup-20-2.sh \
	%D%/psnup-20-3.sh \
	%D%/psnup-20-4.sh \
	%D%/psnup-20-1-inpaper-a5.sh \
	%D%/psnup-20-1-inpaper-a5-outpaper-a5.sh \
	%D%/psnup-20-1-inpaper-a4-outpaper-a5.sh \
	%D%/psnup-20-2-inpaper-a5.sh \
	%D%/psnup-20-3-inpaper-a5.sh \
	%D%/psnup-20-4-inpaper-a5.sh \
	%D%/psnup-20-3-rotatedleft.sh \
	%D%/psnup-20-3-rotatedright.sh \
	%D%/psnup-20-1-flip.sh \
	%D%/psnup-20-4-flip.sh \
	%D%/psnup-20-4-297mmx210mm.sh \
	%D%/psnup-20-4-columnmajor.sh \
	%D%/psnup-20-4-margin-10.sh \
	%D%/psnup-20-4-border-20.sh \
	%D%/psnup-20-3-impossible-tolerance.sh \
	%D%/psnup-20-4-impossible-margin.sh \
	%D%/psnup-20-4-impossible-border.sh \
	%D%/psresize-20-A5.sh \
	%D%/psresize-20-A3.sh \
	%D%/psresize-20-A4.sh \
	%D%/psresize-20-Letter.sh \
	%D%/psresize-20-A5in-A4.sh \
	%D%/psresize-20-A3in-A4.sh \
	%D%/psselect-odd.sh \
	%D%/psselect-even.sh \
	%D%/psselect-reverse.sh \
	%D%/psselect-even-reverse.sh \
	%D%/psselect-positive-range.sh \
	%D%/psselect-negative-range.sh \
	%D%/psselect-positive-negative-range.sh \
	%D%/psselect-individual-pages-and-dash-p.sh \
	%D%/psselect-options-and-complex-pagerange.sh \
	%D%/psselect-invalid-pagerange.sh \
	%D%/epsffit.sh \
	%D%/epsffit-center.sh \
	%D%/epsffit-rotate.sh \
	%D%/epsffit-aspect.sh \
	%D%/epsffit-maximize.sh \
	%D%/epsffit-center-rotate.sh \
	%D%/epsffit-rotate-aspect.sh \
	%D%/epsffit-rotate-maximize.sh \
	%D%/epsffit-center-rotate-aspect.sh \
	%D%/epsffit-center-rotate-maximize.sh \
	%D%/epsffit-center-rotate-aspect-maximize.sh \
	%D%/epsffit-showpage.sh \
	%D%/extractres-and-includeres.sh \
	$(EMPTY)

XFAIL_TESTS = \
	%D%/psbook-invalid-signature-size.sh \
	%D%/psselect-invalid-pagerange.sh \
	%D%/psnup-20-3-impossible-tolerance.sh \
	%D%/psnup-20-4-impossible-margin.sh \
	%D%/psnup-20-4-impossible-border.sh \
	$(EMPTY)

RESULTS = \
	%D%/psbook-20-expected.ps \
	%D%/psbook-20-signature-4-expected.ps \
	%D%/psbook-3-expected.ps \
	%D%/psbook-3-signature-4-expected.ps \
	%D%/psjoin-1-2-expected.ps \
	%D%/psjoin-1-2-even-expected.ps \
	%D%/psjoin-1-2-save-expected.ps \
	%D%/psjoin-1-2-nostrip-expected.ps \
	%D%/psnup-20-1-expected.ps \
	%D%/psnup-20-2-expected.ps \
	%D%/psnup-20-3-expected.ps \
	%D%/psnup-20-4-expected.ps \
	%D%/psnup-20-1-inpaper-a5-expected.ps \
	%D%/psnup-20-1-inpaper-a5-outpaper-a5-expected.ps \
	%D%/psnup-20-1-inpaper-a4-outpaper-a5-expected.ps \
	%D%/psnup-20-2-inpaper-a5-expected.ps \
	%D%/psnup-20-3-inpaper-a5-expected.ps \
	%D%/psnup-20-4-inpaper-a5-expected.ps \
	%D%/psnup-20-3-rotatedleft-expected.ps \
	%D%/psnup-20-3-rotatedright-expected.ps \
	%D%/psnup-20-1-flip-expected.ps \
	%D%/psnup-20-4-flip-expected.ps \
	%D%/psnup-20-4-297mmx210mm.ps \
	%D%/psnup-20-4-columnmajor.ps \
	%D%/psnup-20-4-margin-10.ps \
	%D%/psnup-20-4-border-20.ps \
	%D%/psresize-A5-expected.ps \
	%D%/psresize-A3-expected.ps \
	%D%/psresize-A4-expected.ps \
	%D%/psresize-Letter-expected.ps \
	%D%/psresize-A5in-A4-expected.ps \
	%D%/psresize-A3in-A4-expected.ps \
	%D%/psselect-odd-expected.ps \
	%D%/psselect-even-expected.ps \
	%D%/psselect-reverse-expected.ps \
	%D%/psselect-even-reverse-expected.ps \
	%D%/psselect-positive-range-expected.ps \
	%D%/psselect-negative-range-expected.ps \
	%D%/psselect-positive-negative-range-expected.ps \
	%D%/psselect-individual-pages-and-dash-p-expected.ps \
	%D%/psselect-options-and-complex-pagerange-expected.ps \
	%D%/epsffit-expected.ps \
	%D%/epsffit-center-expected.ps \
	%D%/epsffit-rotate-expected.ps \
	%D%/epsffit-aspect-expected.ps \
	%D%/epsffit-maximize-expected.ps \
	%D%/epsffit-center-rotate-expected.ps \
	%D%/epsffit-rotate-aspect-expected.ps \
	%D%/epsffit-rotate-maximize-expected.ps \
	%D%/epsffit-center-rotate-aspect-expected.ps \
	%D%/epsffit-center-rotate-maximize-expected.ps \
	%D%/epsffit-center-rotate-aspect-maximize-expected.ps \
	%D%/epsffit-showpage-expected.ps \
	%D%/extractres-and-includeres-expected.ps \
	%D%/ISO-8859-1Encoding-expected.enc \
	%D%/a2ps-a2ps-hdr2.02-expected.ps \
	%D%/a2ps-black+white-Prolog2.01-expected.ps \
	%D%/includeres-expected.ps \
	$(EMPTY)

EXTRA_DIST += %D%/mktestfile $(SH_LOG_COMPILER) $(TESTS) $(RESULTS) %D%/psutils-wrapper.in

AM_TESTS_ENVIRONMENT = srcdir=$(srcdir)/tests PATH=$(abs_top_srcdir):$(PATH) PERL5LIB=$(abs_top_srcdir)

# These files depend on Makefile so they are rebuilt if do_subst'ituted
# variables change.
tests/psutils-wrapper: tests/psutils-wrapper.in
tests/psutils-wrapper: Makefile
	$(MKDIR_P) tests
	$(AM_V_GEN)rm -f $@ $@-t \
## Common substitutions.
	  && in=$@.in && $(do_subst) <$(srcdir)/$$in >$@-t
	$(generated_file_finalize)
$(TESTS): tests/psutils-wrapper $(bin_SCRIPTS) $(bin_PROGRAMS)
DISTCLEANFILES += tests/psutils-wrapper

clean-local:
	rm -f $(builddir)/tests/*-input.ps $(builddir)/tests/*-output.ps
