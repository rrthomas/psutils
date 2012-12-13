# Makefile for PS utilities
#
# Copyright (C) Angus J. C. Duggan 1991-1996
# See file LICENSE for details.

prefix=/usr

BINDIR = $(prefix)/bin
SCRIPTDIR = $(BINDIR)
INCLUDEDIR = $(prefix)/lib/psutils
PERL = $(prefix)/bin/perl

BINMODE = 0755
MANMODE = 0644
CHMOD = chmod
INSTALL = install -c -m $(BINMODE)
INSTALLMAN = install -c -m $(MANMODE)
MANEXT = 1
MANDIR = $(prefix)/man/man$(MANEXT)

CFLAGS = -O2 -g -Wall -Werror

BIN = psbook psselect pstops epsffit psnup \
	psresize
SHELLSCRIPTS = getafm showchar
PERLSCRIPTS = fixfmps fixpsditps fixpspps \
	fixtpps fixwfwps fixwpps fixscribeps fixwwps \
	fixdlsrps extractres includeres psmerge
MANPAGES = psbook.$(MANEXT) psselect.$(MANEXT) pstops.$(MANEXT) epsffit.$(MANEXT) psnup.$(MANEXT) \
	psresize.$(MANEXT) psmerge.$(MANEXT) fixscribeps.$(MANEXT) getafm.$(MANEXT) \
	fixdlsrps.$(MANEXT) fixfmps.$(MANEXT) fixpsditps.$(MANEXT) \
	fixpspps.$(MANEXT) fixtpps.$(MANEXT) fixwfwps.$(MANEXT) fixwpps.$(MANEXT) \
	fixwwps.$(MANEXT) extractres.$(MANEXT) includeres.$(MANEXT) \
	showchar.$(MANEXT)

all: $(BIN) $(PERLSCRIPTS) $(MANPAGES) $(SHELLSCRIPTS)

psutil.o: psutil.h patchlev.h pserror.h psutil.c

psspec.o: psutil.h patchlev.h psspec.h pserror.h psspec.c

pserror.o: psutil.h patchlev.h pserror.h pserror.c

epsffit.o: epsffit.c pserror.h patchlev.h

epsffit: epsffit.o pserror.o
	$(CC) $(CCFLAGS) -o epsffit pserror.o epsffit.o -lpaper

psnup: psnup.o psutil.o psspec.o pserror.o
	$(CC) $(CCFLAGS) -o psnup psutil.o psspec.o pserror.o psnup.o -lpaper

psnup.o: psutil.h patchlev.h psspec.h pserror.h psnup.c

psresize: psresize.o psutil.o pserror.o psspec.o
	$(CC) $(CCFLAGS) -o psresize psutil.o psspec.o pserror.o psresize.o \
          -lpaper

psresize.o: psutil.h patchlev.h psspec.h pserror.h psresize.c

psbook: psbook.o psutil.o pserror.o psspec.o
	$(CC) $(CCFLAGS) -o psbook psutil.o pserror.o psspec.o psbook.o -lpaper

psbook.o: psutil.h patchlev.h pserror.h psbook.c

psselect: psselect.o psutil.o pserror.o psspec.o
	$(CC) $(CCFLAGS) -o psselect psutil.o pserror.o psspec.o psselect.o -lpaper

psselect.o: psutil.h patchlev.h pserror.h psselect.c

pstops: pstops.o psutil.o psspec.o pserror.o
	$(CC) $(CCFLAGS) -o pstops psutil.o psspec.o pserror.o pstops.o -lpaper

pstops.o: psutil.h patchlev.h psspec.h pserror.h pstops.c

getafm:	getafm.sh
	cp $? $@

showchar:	showchar.sh
	cp $? $@

psmerge: psmerge.pl
	cp $? $@
	$(CHMOD) $(BINMODE) $@

fixfmps: fixfmps.pl
	cp $? $@
	$(CHMOD) $(BINMODE) $@

fixpsditps: fixpsditps.pl
	cp $? $@
	$(CHMOD) $(BINMODE) $@

fixpspps: fixpspps.pl
	cp $? $@
	$(CHMOD) $(BINMODE) $@

fixscribeps: fixscribeps.pl
	cp $? $@
	$(CHMOD) $(BINMODE) $@

fixtpps: fixtpps.pl
	cp $? $@
	$(CHMOD) $(BINMODE) $@

fixwfwps: fixwfwps.pl
	cp $? $@
	$(CHMOD) $(BINMODE) $@

fixwpps: fixwpps.pl
	cp $? $@
	$(CHMOD) $(BINMODE) $@

fixwwps: fixwwps.pl
	cp $? $@
	$(CHMOD) $(BINMODE) $@

fixdlsrps: fixdlsrps.pl
	cp $? $@
	$(CHMOD) $(BINMODE) $@

extractres: extractres.pl
	cp $? $@
	$(CHMOD) $(BINMODE) $@

includeres: includeres.pl
	$(PERL) maketext INCLUDE=$(INCLUDEDIR) $? > $@
	$(CHMOD) $(BINMODE) $@

epsffit.$(MANEXT): epsffit.man
	$(PERL) maketext MAN="$(MANPAGES)" $? > $@

psnup.$(MANEXT): psnup.man
	$(PERL) maketext MAN="$(MANPAGES)" $? > $@

psresize.$(MANEXT): psresize.man
	$(PERL) maketext MAN="$(MANPAGES)" $? > $@

psbook.$(MANEXT): psbook.man
	$(PERL) maketext "MAN=$(MANPAGES)" $? > $@

psselect.$(MANEXT): psselect.man
	$(PERL) maketext "MAN=$(MANPAGES)" $? > $@

pstops.$(MANEXT): pstops.man
	$(PERL) maketext "MAN=$(MANPAGES)" $? > $@

psmerge.$(MANEXT): psmerge.man
	$(PERL) maketext "MAN=$(MANPAGES)" $? > $@

fixfmps.$(MANEXT): fixfmps.man
	$(PERL) maketext "MAN=$(MANPAGES)" $? > $@

fixpsditps.$(MANEXT): fixpsditps.man
	$(PERL) maketext "MAN=$(MANPAGES)" $? > $@

fixpspps.$(MANEXT): fixpspps.man
	$(PERL) maketext "MAN=$(MANPAGES)" $? > $@

fixscribeps.$(MANEXT): fixscribeps.man
	$(PERL) maketext "MAN=$(MANPAGES)" $? > $@

fixtpps.$(MANEXT): fixtpps.man
	$(PERL) maketext "MAN=$(MANPAGES)" $? > $@

fixwfwps.$(MANEXT): fixwfwps.man
	$(PERL) maketext "MAN=$(MANPAGES)" $? > $@

fixwpps.$(MANEXT): fixwpps.man
	$(PERL) maketext "MAN=$(MANPAGES)" $? > $@

fixwwps.$(MANEXT): fixwwps.man
	$(PERL) maketext "MAN=$(MANPAGES)" $? > $@

fixdlsrps.$(MANEXT): fixdlsrps.man
	$(PERL) maketext "MAN=$(MANPAGES)" $? > $@

extractres.$(MANEXT): extractres.man
	$(PERL) maketext "MAN=$(MANPAGES)" $? > $@

includeres.$(MANEXT): includeres.man
	$(PERL) maketext "MAN=$(MANPAGES)" INCLUDE=$(INCLUDEDIR) $? > $@

getafm.$(MANEXT): getafm.man
	$(PERL) maketext "MAN=$(MANPAGES)" $? > $@

showchar.$(MANEXT): showchar.man
	$(PERL) maketext "MAN=$(MANPAGES)" $? > $@

clean:
	rm -f *.o

veryclean realclean: clean
	rm -f $(BIN) $(PERLSCRIPTS) $(MANPAGES)

install: install.bin install.script install.man

install.bin: $(BIN)
	-mkdir $(BINDIR)
	@for i in $(BIN); do \
		echo Installing $$i; \
		$(INSTALL) $$i $(BINDIR); \
	done

install.script: $(PERLSCRIPTS) $(SHELLSCRIPTS)
	-mkdir $(SCRIPTDIR)
	@for i in $(PERLSCRIPTS) $(SHELLSCRIPTS); do \
		echo Installing $$i; \
		$(INSTALL) $$i $(SCRIPTDIR); \
	done

install.man: $(MANPAGES)
	-mkdir $(MANDIR)
	@for i in $(MANPAGES); do \
		echo Installing manual page for $$i; \
		$(INSTALLMAN) $$i $(MANDIR)/$$i; \
	done
