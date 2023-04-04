# Makefile for PSUtils
#
# Copyright (C) Reuben Thomas 2012-2023
# See COPYING for license

dist:
	tox && \
	git diff --exit-code && \
	rm -rf ./dist && \
	mkdir dist && \
	python -m build

release: distcheck
	git diff --exit-code && \
	git tag -a -m "Release tag" "v$(VERSION)" && \
	git push && git push --tags && \
	woger github package=$(PACKAGE) version=$(VERSION) dist_type=tar.gz

# FIXME: Set this list automatically from setup.cfg:
# options.scripts + options.packages contents
SOURCES = psutils/__init__.py \
    pstops psbook psjoin psresize psselect psnup \
    pdftopdf pdfbook pdfjoin pdfresize pdfselect pdfnup \
    epsffit extractres includeres

loc:
	cloc $(SOURCES)

.PHONY:	dist
