/* psutil.c
 * PSUtils utility functions
 *
 * (c) Reuben Thomas 2012-2016
 * (c) Angus J. C. Duggan 1991-1997
 * See file LICENSE for details.
 */

#include "config.h"

#define _FILE_OFFSET_BITS 64

#include "psutil.h"
#include "psspec.h"

#include <string.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <stdio.h>
#include <stdarg.h>

#include "progname.h"
#include "xvasprintf.h"
#include "verror.h"
#include "binary-io.h"
#include "minmax.h"

#define iscomment(x,y) (strncmp(x,y,strlen(y)) == 0)

int pages;
int verbose = 1;
FILE *infile;
FILE *outfile;
char pagelabel[BUFSIZ];
int pageno;
off_t beginprocset = 0;		/* start of pstops procset */
int outputpage = 0;

static char buffer[BUFSIZ];
static off_t pagescmt = 0;
static off_t headerpos = 0;
static off_t endsetup = 0;
static off_t endprocset = 0;
static int maxpages = 100;
static off_t *pageptr;

_Noreturn void usage(void)
{
  fprintf(stderr, "%s %s\n%sUsage: %s %s\n",
          program_name, PACKAGE_VERSION,
          "(c) Reuben Thomas <rrt@sc3d.org> 2012-2016\n(c) Angus J. C. Duggan 1991-1997\nSee file LICENSE for details.\n",
          program_name, syntax);
  exit(1);
}

void argerror(void)
{
   verbose = 0; /* We won't be in the middle of a line during argument parsing */
   die(argerr_message);
}

/* Message function: for messages, warnings, and errors sent to stderr.
   The routine does not return. */
void die(const char *format, ...)
{
  va_list args;

  if (verbose) /* We may be in the middle of a line */
    putc('\n', stderr);

  va_start(args, format);
  verror(1, 0, format, args); /* Does not return */
}

/* Read a line from a FILE * and return it. */
char *xgetline(FILE *fp)
{
  char *l = NULL;
  size_t n;
  return getline(&l, &n, fp) == -1 ? NULL : l;
}

/* Read a line from a pipe and return it without any trailing newline. */
static char *pgetline(const char *cmd)
{
  char *l = NULL;
  FILE *fp = popen(cmd, "r");
  if (fp) {
    l = xgetline(fp);
    size_t len = strlen(l);
    if (l && l[len - 1] == '\n')
      l[len - 1] = '\0';
    if (pclose(fp) != 0) {
      free(l);
      l = NULL;
    }
  }
  return l;
}

/* Get the size of the given paper, or the default paper if paper_name == NULL. */
int paper_size(const char *paper_name, double *width, double *height)
{
  char *cmd = NULL, *l = NULL;
  int res = 0;
  if (paper_name == NULL) /* Use default paper name */
    paper_name = pgetline(PAPER);
  if (paper_name && (cmd = xasprintf(PAPER " --unit=pt --size %s", paper_name)) && (l = pgetline(cmd)))
    res = sscanf(l, "%lg %lg", width, height);
  free(l);
  free(cmd);
  return res == 2;
}

void check_paper_size_set(void)
{
  /* Ensure output paper size is set */
  if (width == -1 && height == -1 && !paper_size(NULL, &width, &height))
    die("output paper size not set, and could not get default paper size");
  if (width <= 0 || height <= 0)
    die("output page width and height must both be set");
}

/* Make a file seekable, using temporary files if necessary */
static FILE *seekable(FILE *fp)
{
  /* If fp is seekable, we're OK */
  off_t fpos;
  if ((fpos = ftello(fp)) >= 0)
    if (!fseeko(fp, (off_t) 0, SEEK_END) && !fseeko(fp, fpos, SEEK_SET))
      return fp;

  /* Otherwise, copy fp to a temporary file */
  FILE *ft = tmpfile();
  if (ft == NULL)
    return NULL;
  size_t r;
  for (char buffer[BUFSIZ]; (r = fread(buffer, sizeof(char), BUFSIZ, fp)) > 0;) {
    if (fwrite(buffer, sizeof(char), r, ft) != r)
      return NULL;
  }
  if (!feof(fp))
    return NULL;

  /* Discard the input file, and rewind the temporary */
  (void) fclose(fp);
  if (fseeko(ft, (off_t) 0, SEEK_SET) != 0)
    return NULL;

  return ft;
}

void parse_input_and_output_files(int argc, char *argv[], int optind, int seeking)
{
  infile = stdin;
  outfile = stdout;

  if (optind < argc) {
    /* User specified an input file */
    if ((infile = fopen(argv[optind], "rb")) == NULL)
      die("can't open input file %s", argv[optind]);
    optind++;
  }

  if (optind < argc) {
    /* User specified an output file */
    if ((outfile = fopen(argv[optind], "wb")) == NULL)
      die("can't open output file %s", argv[optind]);
    optind++;
  }

  if (optind != argc)
    usage();

  if (infile == stdin && set_binary_mode(fileno(stdin), O_BINARY) < 0)
    die("could not set stdin to binary mode");
  if (outfile == stdout && set_binary_mode(fileno(stdout), O_BINARY) < 0)
    die("could not set stdout to binary mode");

  if (seeking && (infile = seekable(infile)) == NULL)
    die("cannot seek input");
}

/* copy input file from current position upto new position to output file,
 * ignoring the lines starting at something ignorelist points to */
static int fcopy(off_t upto, off_t *ignorelist)
{
  off_t here = ftello(infile);

  if (ignorelist != NULL) {
    while (*ignorelist > 0 && *ignorelist < upto) {
      while (*ignorelist > 0 && *ignorelist < here)
        ignorelist++;
      char *buffer;
      if (!fcopy(*ignorelist, NULL) || (buffer = xgetline(infile)) == NULL)
	return 0;
      free(buffer);
      ignorelist++;
      here = ftello(infile);
    }
  }

  size_t numtocopy;
  char buffer[BUFSIZ];
  for (off_t bytes_left = upto - here; bytes_left > 0; bytes_left -= numtocopy) {
    numtocopy = MIN(bytes_left, BUFSIZ);
    if (fread(buffer, sizeof(char), numtocopy, infile) < numtocopy ||
        fwrite(buffer, sizeof(char), numtocopy, outfile) < numtocopy)
      return 0;
  }
  return 1;
}

/* build array of pointers to start/end of pages */
void scanpages(off_t *sizeheaders)
{
   char *comment = buffer+2;
   int nesting = 0;
   off_t record;

   if (sizeheaders)
     *sizeheaders = 0;

   if ((pageptr = (off_t *)malloc(sizeof(off_t)*maxpages)) == NULL)
      die("out of memory");
   pages = 0;
   fseeko(infile, (off_t) 0, SEEK_SET);
   while (record = ftello(infile), fgets(buffer, BUFSIZ, infile) != NULL)
      if (*buffer == '%') {
	 if (buffer[1] == '%') {
	    if (nesting == 0 && iscomment(comment, "Page:")) {
	       if (pages >= maxpages-1) {
		  maxpages *= 2;
		  if ((pageptr = (off_t *)realloc((char *)pageptr,
					     sizeof(off_t)*maxpages)) == NULL)
		     die("out of memory");
	       }
	       pageptr[pages++] = record;
	    } else if (headerpos == 0 && iscomment(comment, "BoundingBox:")) {
	       if (sizeheaders) {
		  *(sizeheaders++) = record;
		  *sizeheaders = 0;
	       }
	    } else if (headerpos == 0 && iscomment(comment, "HiResBoundingBox:")) {
	       if (sizeheaders) {
		  *(sizeheaders++) = record;
		  *sizeheaders = 0;
	       }
	    } else if (headerpos == 0 && iscomment(comment,"DocumentPaperSizes:")) {
	       if (sizeheaders) {
		  *(sizeheaders++) = record;
		  *sizeheaders = 0;
	       }
	    } else if (headerpos == 0 && iscomment(comment,"DocumentMedia:")) {
	       if (sizeheaders) {
		  *(sizeheaders++) = record;
		  *sizeheaders = 0;
	       }
	    } else if (headerpos == 0 && iscomment(comment, "Pages:"))
	       pagescmt = record;
	    else if (headerpos == 0 && iscomment(comment, "EndComments"))
	       headerpos = ftello(infile);
	    else if (iscomment(comment, "BeginDocument") ||
		     iscomment(comment, "BeginBinary") ||
		     iscomment(comment, "BeginFile"))
	       nesting++;
	    else if (iscomment(comment, "EndDocument") ||
		     iscomment(comment, "EndBinary") ||
		     iscomment(comment, "EndFile"))
	       nesting--;
	    else if (nesting == 0 && iscomment(comment, "EndSetup"))
	       endsetup = record;
	    else if (nesting == 0 && iscomment(comment, "BeginProlog"))
	       headerpos = ftello(infile);
	    else if (nesting == 0 &&
		       iscomment(comment, "BeginProcSet: PStoPS"))
	       beginprocset = record;
	    else if (beginprocset && !endprocset &&
		     iscomment(comment, "EndProcSet"))
	       endprocset = ftello(infile);
	    else if (nesting == 0 && (iscomment(comment, "Trailer") ||
				      iscomment(comment, "EOF"))) {
	       fseeko(infile, record, SEEK_SET);
	       break;
	    }
	 } else if (headerpos == 0 && buffer[1] != '!')
	    headerpos = record;
      } else if (headerpos == 0)
	 headerpos = record;
   pageptr[pages] = ftello(infile);
   if (endsetup == 0 || endsetup > pageptr[0])
      endsetup = pageptr[0];
}

/* seek a particular page */
void seekpage(int p)
{
   fseeko(infile, pageptr[p], SEEK_SET);
   char *buffer = xgetline(infile);
   if (buffer != NULL && iscomment(buffer, "%%Page:")) {
      char *start, *end;
      for (start = buffer+7; isspace((unsigned char)*start); start++);
      if (*start == '(') {
	 int paren = 1;
	 for (end = start+1; paren > 0; end++)
	    switch (*end) {
	    case '\0':
	       die("Bad page label while seeking page %d", p);
	    case '(':
	       paren++;
	       break;
	    case ')':
	       paren--;
	       break;
            default:
               break;
	    }
      } else
	 for (end = start; !isspace((unsigned char)*end); end++);
      strncpy(pagelabel, start, end-start);
      pagelabel[end-start] = '\0';
      free(buffer);
      pageno = atoi(end);
   } else
      die("I/O error seeking page %d", p);
}

/* Output routines. */
void writestring(const char *s)
{
  writestringf("%s", s);
}

void writestringf(const char *f, ...)
{
  va_list ap;
  va_start(ap, f);
  vfprintf(outfile, f, ap);
  va_end(ap);
}

/* write page comment */
void writepageheader(const char *label, int page)
{
   if (verbose) {
      if (page < 0)
         fprintf(stderr, "[*] ");
      else
         fprintf(stderr, "[%d] ", page);
   }
   writestringf("%%%%Page: %s %d\n", page < 0 ? "*" : label, ++outputpage);
}

/* write the body of a page */
void writepagebody(int p)
{
   if (!fcopy(pageptr[p+1], NULL))
      die("I/O error writing page %d", outputpage);
}

void writeheadermedia(int p, off_t *ignore, double width, double height)
{
   fseeko(infile, (off_t) 0, SEEK_SET);
   if (pagescmt) {
      if (!fcopy(pagescmt, ignore) || fgets(buffer, BUFSIZ, infile) == NULL)
	 die("I/O error in header");
      if (width > -1 && height > -1) {
         writestringf("%%%%DocumentMedia: plain %d %d 0 () ()\n", (int) width, (int) height);
         writestringf("%%%%BoundingBox: 0 0 %d %d\n", (int) width, (int) height);
      }
      writestringf("%%%%Pages: %d 0\n", p);
   }
   if (!fcopy(headerpos, ignore))
      die("I/O error in header");
}

/* write prologue to end of setup section excluding PStoPS procset */
int writepartprolog(void)
{
   if (beginprocset && !fcopy(beginprocset, NULL))
      die("I/O error in prologue");
   if (endprocset)
      fseeko(infile, endprocset, SEEK_SET);
   if (!fcopy(endsetup, NULL))
      die("I/O error in prologue");
   return !beginprocset;
}

/* write from end of setup to start of pages */
void writesetup(void)
{
   if (!fcopy(pageptr[0], NULL))
      die("I/O error in prologue");
}

/* write trailer */
void writetrailer(void)
{
   fseeko(infile, pageptr[pages], SEEK_SET);
   while (fgets(buffer, BUFSIZ, infile) != NULL) {
      writestring(buffer);
   }
   if (verbose)
      fprintf(stderr, "Wrote %d pages\n", outputpage);
}
