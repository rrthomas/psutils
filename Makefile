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

release:
	make test
	make dist
	twine upload dist/* && \
	git tag v$$(grep version pyproject.toml | grep -o "[0-9.]\+") && \
	git push --tags

loc:
	cloc psutils
	cloc tests/*.py

.PHONY:	dist
