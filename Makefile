# Makefile for PSUtils
#
# Copyright (C) Reuben Thomas 2012-2023
# See COPYING for license

test:
	tox

dist:
	git diff --exit-code && \
	rm -rf ./dist && \
	mkdir dist && \
	python -m build

release-pypi:
	twine upload dist/*

release:
	make test
	make dist
	package=psutils && \
	version=$$(grep version pyproject.toml | grep -o "[0-9.]\+") && \
	gh release create v$$version --title "Release v$$version" dist/$$package-$$version-py3-none-any.whl dist/$$package-$$version.tar.gz && \
	git tag v$$version && \
	git push --tags

loc:
	cloc psutils
	cloc tests/*.py

.PHONY:	dist
