/* psutil.h
 * Copyright (C) Angus J. C. Duggan 1991-1995
 * See file LICENSE for details.
 *
 * utilities for PS programs
 */
#define _FILE_OFFSET_BITS 64
#include <stdio.h>
#include <stdlib.h>
#include <ctype.h>

/* Definitions for functions found in psutil.c */
extern void set_paper_size(const char *paper_name);
const struct paper *get_paper(const char *paper_name);
extern FILE *seekable(FILE *fp);
extern void writepage(int p);
extern void seekpage(int p);
extern void writepageheader(char *label, int p);
extern void writepagesetup(void);
extern void writepagebody(int p);
extern void writeheader(int p, off_t *ignorelist);
extern void writeheadermedia(int p, off_t *ignorelist, double width, double height);
extern int writepartprolog(void);
extern void writeprolog(void);
extern void writesetup(void);
extern void writetrailer(void);
extern void writeemptypage(void);
extern void scanpages(off_t *sizeheaders);
extern void writestring(const char *s);

/* These variables are exported to the client program */
extern char *program ;
extern int pages;
extern int verbose;
extern FILE *infile;
extern FILE *outfile;
extern char pagelabel[BUFSIZ];
extern int pageno;

/* Useful macros */
#define MIN(x,y) ((x) > (y) ? (y) : (x))
#define COPYRIGHT_STRING "Copyright Reuben Thomas <rrt@sc3d.org> 2012\nCopyright (C) Angus J. C. Duggan, 1991-1997\nSee file LICENSE for details.\n"
