# Makefile for PSUtils
#
# Copyright (C) Reuben Thomas 2012-2025
# See COPYING for license

test:
	tox

build:
	python -m build

dist:
	git diff --exit-code && \
	rm -rf ./dist && \
	mkdir dist && \
	$(MAKE) build

release-pypi:
	twine upload dist/*

release:
	$(MAKE) test &&
	$(MAKE) dist &&
	version=$$(grep version pyproject.toml | grep -o "[0-9.]\+") && \
	twine upload dist/* && \
	gh release create v$$version --title "Release v$$version" dist/* && \
	git pull --tags

loc:
	cloc psutils
	cloc tests/*.py

.PHONY:	dist
