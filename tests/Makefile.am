# Tests Makefile.am
#
# Copyright (C) Reuben Thomas 2016-2017
# See LICENSE for license

TEST_EXTENSIONS = .sh
SH_LOG_COMPILER = $(srcdir)/tests/run-test

TESTS = \
	%D%/psbook-20.sh \
	%D%/psbook-20-signature-4.sh \
	%D%/psbook-3.sh \
	%D%/psbook-3-signature-4.sh \
	%D%/psbook-invalid-signature-size.sh \
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
	%D%/psselect-odd.sh \
	%D%/psselect-even.sh \
	%D%/psselect-reverse.sh \
	%D%/psselect-even-reverse.sh \
	%D%/psselect-positive-range.sh \
	%D%/psselect-negative-range.sh \
	%D%/psselect-positive-negative-range.sh \
	%D%/psselect-individual-pages-and-dash-p.sh \
	%D%/psselect-options-and-complex-pagerange.sh \
	%D%/psselect-invalid-pagerange.sh

# Tests to write:

# psnup-20-4-210mmx297mm.sh
# psnup-20-4-columnmajor.sh
# psnup-20-4-margin-10.sh
# psnup-20-4-border-20.sh
# psnup-20-3-impossible-tolerance.sh
# psnup-20-4-impossible-margin.sh
# psnup-20-4-impossible-border.sh

# psjoin-1-2.sh
# psjoin-1-2-even.sh
# psjoin-1-2-save.sh
# psjoin-1-2-nostrip.sh

# psresize-20-4-A5.sh
# psresize-20-4-A3.sh
# psresize-20-4-A4.sh
# psresize-20-4-Letter.sh
# psresize-20-4-A4in-A4.sh
# psresize-20-4-A5in-A4.sh
# psresize-20-4-A3in-A4.sh

# epsffit-center.sh
# epsffit-rotate.sh
# epsffit-aspect.sh
# epsffit-maximise.sh
# epsffit-center-rotate.sh
# epsffit-center-rotate-aspect.sh
# epsffit-center-rotate-maximize.sh
# epsffit-center-rotate-aspect-maximize.sh
# epsffit-showpage.sh

# extractres (have at least one resource of each type in input)

# includeres-pfa
# includeres-ps
# includeres-pat
# includeres-frm
# includeres-enc

XFAIL_TESTS = \
	%D%/psbook-invalid-signature-size.sh \
	%D%/psselect-invalid-pagerange.sh

RESULTS = \
	%D%/psbook-20-expected.sh \
	%D%/psbook-20-signature-4-expected.sh \
	%D%/psbook-3-expected.sh \
	%D%/psbook-3-signature-4-expected.sh \
	%D%/psbook-invalid-signature-size-expected.sh \
	%D%/psnup-20-1-expected.sh \
	%D%/psnup-20-2-expected.sh \
	%D%/psnup-20-3-expected.sh \
	%D%/psnup-20-4-expected.sh \
	%D%/psnup-20-1-inpaper-a5-expected.sh \
	%D%/psnup-20-1-inpaper-a5-outpaper-a5-expected.sh \
	%D%/psnup-20-1-inpaper-a4-outpaper-a5-expected.sh \
	%D%/psnup-20-2-inpaper-a5-expected.sh \
	%D%/psnup-20-3-inpaper-a5-expected.sh \
	%D%/psnup-20-4-inpaper-a5-expected.sh \
	%D%/psnup-20-3-rotatedleft-expected.sh \
	%D%/psnup-20-3-rotatedright-expected.sh \
	%D%/psnup-20-1-flip-expected.sh \
	%D%/psnup-20-4-flip-expected.sh \
	%D%/psselect-odd-expected.sh \
	%D%/psselect-even-expected.sh \
	%D%/psselect-reverse-expected.sh \
	%D%/psselect-even-reverse-expected.sh \
	%D%/psselect-positive-range-expected.sh \
	%D%/psselect-negative-range-expected.sh \
	%D%/psselect-positive-negative-range-expected.sh \
	%D%/psselect-individual-pages-and-dash-p-expected.sh \
	%D%/psselect-options-and-complex-pagerange-expected.sh \
	%D%/psselect-invalid-pagerange-expected.sh

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
