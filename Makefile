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

loc:
	cloc psutils

.PHONY:	dist
