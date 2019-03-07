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
	%D%/psnup-20-1-inpaper-A5.sh \
	%D%/psnup-20-1-inpaper-A5-outpaper-A5.sh \
	%D%/psnup-20-1-inpaper-A4-outpaper-A5.sh \
	%D%/psnup-20-2-inpaper-A5.sh \
	%D%/psnup-20-3-inpaper-A5.sh \
	%D%/psnup-20-4-inpaper-A5.sh \
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

INPUTS = \
	%D%/psbook-20-input.ps \
	%D%/psbook-20-signature-4-input.ps \
	%D%/psbook-3-input.ps \
	%D%/psbook-3-signature-4-input.ps \
	%D%/psjoin-1-2-input.ps \
	%D%/psjoin-1-2-even-input.ps \
	%D%/psjoin-1-2-save-input.ps \
	%D%/psjoin-1-2-nostrip-input.ps \
	%D%/psnup-20-1-input.ps \
	%D%/psnup-20-2-input.ps \
	%D%/psnup-20-3-input.ps \
	%D%/psnup-20-4-input.ps \
	%D%/psnup-20-1-inpaper-A5-input.ps \
	%D%/psnup-20-1-inpaper-A5-outpaper-A5-input.ps \
	%D%/psnup-20-1-inpaper-A4-outpaper-A5-input.ps \
	%D%/psnup-20-2-inpaper-A5-input.ps \
	%D%/psnup-20-3-inpaper-A5-input.ps \
	%D%/psnup-20-4-inpaper-A5-input.ps \
	%D%/psnup-20-3-rotatedleft-input.ps \
	%D%/psnup-20-3-rotatedright-input.ps \
	%D%/psnup-20-1-flip-input.ps \
	%D%/psnup-20-4-flip-input.ps \
	%D%/psnup-20-4-297mmx210mm-input.ps \
	%D%/psnup-20-4-columnmajor-input.ps \
	%D%/psnup-20-4-margin-10-input.ps \
	%D%/psnup-20-4-border-20-input.ps \
	%D%/psresize-20-A5-input.ps \
	%D%/psresize-20-A3-input.ps \
	%D%/psresize-20-A4-input.ps \
	%D%/psresize-20-Letter-input.ps \
	%D%/psresize-20-A5in-A4-input.ps \
	%D%/psresize-20-A3in-A4-input.ps \
	%D%/psselect-odd-input.ps \
	%D%/psselect-even-input.ps \
	%D%/psselect-reverse-input.ps \
	%D%/psselect-even-reverse-input.ps \
	%D%/psselect-positive-range-input.ps \
	%D%/psselect-negative-range-input.ps \
	%D%/psselect-positive-negative-range-input.ps \
	%D%/psselect-individual-pages-and-dash-p-input.ps \
	%D%/psselect-options-and-complex-pagerange-input.ps \
	%D%/epsffit-input.ps \
	%D%/epsffit-center-input.ps \
	%D%/epsffit-rotate-input.ps \
	%D%/epsffit-aspect-input.ps \
	%D%/epsffit-maximize-input.ps \
	%D%/epsffit-center-rotate-input.ps \
	%D%/epsffit-rotate-aspect-input.ps \
	%D%/epsffit-rotate-maximize-input.ps \
	%D%/epsffit-center-rotate-aspect-input.ps \
	%D%/epsffit-center-rotate-maximize-input.ps \
	%D%/epsffit-center-rotate-aspect-maximize-input.ps \
	%D%/epsffit-showpage-input.ps \
	%D%/extractres-and-includeres-input.ps \
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
	%D%/psnup-20-1-inpaper-A5-expected.ps \
	%D%/psnup-20-1-inpaper-A5-outpaper-A5-expected.ps \
	%D%/psnup-20-1-inpaper-A4-outpaper-A5-expected.ps \
	%D%/psnup-20-2-inpaper-A5-expected.ps \
	%D%/psnup-20-3-inpaper-A5-expected.ps \
	%D%/psnup-20-4-inpaper-A5-expected.ps \
	%D%/psnup-20-3-rotatedleft-expected.ps \
	%D%/psnup-20-3-rotatedright-expected.ps \
	%D%/psnup-20-1-flip-expected.ps \
	%D%/psnup-20-4-flip-expected.ps \
	%D%/psnup-20-4-297mmx210mm-expected.ps \
	%D%/psnup-20-4-columnmajor-expected.ps \
	%D%/psnup-20-4-margin-10-expected.ps \
	%D%/psnup-20-4-border-20-expected.ps \
	%D%/psresize-20-A5-expected.ps \
	%D%/psresize-20-A3-expected.ps \
	%D%/psresize-20-A4-expected.ps \
	%D%/psresize-20-Letter-expected.ps \
	%D%/psresize-20-A5in-A4-expected.ps \
	%D%/psresize-20-A3in-A4-expected.ps \
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

EXTRA_DIST += %D%/mktestfile $(SH_LOG_COMPILER) $(TESTS) $(INPUTS) $(RESULTS)

AM_TESTS_ENVIRONMENT = srcdir=$(srcdir)/tests PATH=$(abs_top_builddir):$(PATH) PERL5LIB=$(abs_top_srcdir)

DISTCLEANFILES += ISO-8859-1Encoding.enc a2ps-a2ps-hdr2.02.ps a2ps-black+white-Prolog2.01.ps


clean-local:
	rm -f $(builddir)/tests/*-output.ps
