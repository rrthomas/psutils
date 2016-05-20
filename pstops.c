/* pstops.c
 * Rearrange pages in conforming PS file
 *
 * (c) Reuben Thomas 2012-2016
 * (c) Angus J. C. Duggan 1991-1997
 * See file LICENSE for details.
 */

#include "config.h"

#define _FILE_OFFSET_BITS 64

#include <stdio.h>
#include <stdlib.h>
#include <stdarg.h>
#include <unistd.h>
#include <string.h>
#include <math.h>
#include <ctype.h>
#include <sys/types.h>
#include <sys/stat.h>

#include "progname.h"
#include "xalloc.h"
#include "xvasprintf.h"
#include "verror.h"
#include "binary-io.h"
#include "gcd.h"
#include "minmax.h"

/* pagespec flags */
#define ADD_NEXT (0x01)
#define ROTATE   (0x02)
#define HFLIP    (0x04)
#define VFLIP    (0x08)
#define SCALE    (0x10)
#define OFFSET   (0x20)
#define REVERSED (0x40)
#define GSAVE    (ROTATE|HFLIP|VFLIP|SCALE|OFFSET)

typedef struct pagespec {
  int pageno, flags, rotate;
  double xoff, yoff, scale;
  struct pagespec *next;
} PageSpec;

typedef struct pgrange {
  int first, last;
  struct pgrange *next;
} PageRange;

#define iscomment(x,y) (strncmp(x,y,strlen(y)) == 0)

static size_t pages;
static int verbose = 1;
static FILE *infile;
static FILE *outfile;
static char *pagelabel = NULL;
static int pageno;
static off_t beginprocset = 0;		/* start of pstops procset */
static int outputpage = 0;

static off_t pagescmt = 0;
static off_t headerpos = 0;
static off_t endsetup = 0;
static off_t endprocset = 0;
static size_t maxpages = 100;
static off_t *pageptr;

static const char *syntax = "[-q] [-b] [-e|-o] [-r] [-RPAGES] [-wWIDTH -hHEIGHT|-pPAPER] [-WWIDTH -HHEIGHT|-PPAPER] [-dWIDTH] [-sSIGNATURE] PAGESPECS [INFILE [OUTFILE]]";

static _Noreturn void usage(void)
{
  fprintf(stderr, "%s %s\n%sUsage: %s %s\n",
          program_name, PACKAGE_VERSION,
          "(c) Reuben Thomas <rrt@sc3d.org> 2012-2016\n(c) Angus J. C. Duggan 1991-1997\nSee file LICENSE for details.\n",
          program_name, syntax);
  exit(1);
}

/* Message function: for messages, warnings, and errors sent to stderr.
   The routine does not return. */
static void die(const char *format, ...)
{
  va_list args;

  if (verbose) /* We may be in the middle of a line */
    putc('\n', stderr);

  va_start(args, format);
  verror(1, 0, format, args); /* Does not return */
}

static void argerror(void)
{
  verbose = 0; /* We won't be in the middle of a line during argument parsing */
  die("page specification error:\n"
      "  PAGESPECS = [[SIGNATURE:]MODULO:]SPEC\n"
      "  SPEC      = [-]PAGENO[@SCALE][L|R|U|H|V][(XOFF,YOFF)][,SPEC|+SPEC]\n"
      "              MODULO >= 1; 0 <= PAGENO < MODULO\n"
      "  SIGNATURE = 0, 1, or a positive multiple of 4");
}

/* Read a line from a FILE * and return it. */
static char *xgetline(FILE *fp)
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
static int paper_size(const char *paper_name, double *width, double *height)
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
static void scanpages(off_t *sizeheaders)
{
  int nesting = 0;

  pageptr = (off_t *)XCALLOC(maxpages, off_t);
  pages = 0;
  fseeko(infile, (off_t) 0, SEEK_SET);
  off_t record;
  for (char *buffer; record = ftello(infile), (buffer = xgetline(infile)) != NULL; free(buffer))
    if (*buffer == '%' && buffer[1] == '%') {
      if (nesting == 0 && iscomment(buffer, "%%Page:")) {
        if (pages >= maxpages - 1)
          pageptr = (off_t *)x2nrealloc(pageptr, &maxpages, sizeof(off_t));
        pageptr[pages++] = record;
      } else if (headerpos == 0 && sizeheaders && (iscomment(buffer, "%%BoundingBox:") ||
                                                   iscomment(buffer, "%%HiResBoundingBox:") ||
                                                   iscomment(buffer, "%%DocumentPaperSizes:") ||
                                                   iscomment(buffer, "%%DocumentMedia:"))) {
        *(sizeheaders++) = record;
      } else if (headerpos == 0 && iscomment(buffer, "%%Pages:"))
        pagescmt = record;
      else if (headerpos == 0 && iscomment(buffer, "%%EndComments"))
        headerpos = ftello(infile);
      else if (iscomment(buffer, "%%BeginDocument") ||
               iscomment(buffer, "%%BeginBinary") ||
               iscomment(buffer, "%%BeginFile"))
        nesting++;
      else if (iscomment(buffer, "%%EndDocument") ||
               iscomment(buffer, "%%EndBinary") ||
               iscomment(buffer, "%%EndFile"))
        nesting--;
      else if (nesting == 0 && iscomment(buffer, "%%EndSetup"))
        endsetup = record;
      else if (nesting == 0 && iscomment(buffer, "%%BeginProlog"))
        headerpos = ftello(infile);
      else if (nesting == 0 && iscomment(buffer, "%%BeginProcSet: PStoPS"))
        beginprocset = record;
      else if (beginprocset && !endprocset && iscomment(buffer, "%%EndProcSet"))
        endprocset = ftello(infile);
      else if (nesting == 0 && (iscomment(buffer, "%%Trailer") ||
                                iscomment(buffer, "%%EOF"))) {
        fseeko(infile, record, SEEK_SET);
        break;
      }
    } else if (headerpos == 0)
      headerpos = record;
  pageptr[pages] = ftello(infile);
  if (endsetup == 0 || endsetup > pageptr[0])
    endsetup = pageptr[0];
}

/* seek a particular page */
static void seekpage(int p)
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
    if (pagelabel != NULL)
      free(pagelabel);
    pagelabel = strndup(start, end - start);
    pageno = atoi(end);
    free(buffer);
  } else
    die("I/O error seeking page %d", p);
}

/* Output routines. */
static void writestringf(const char *f, ...)
{
  va_list ap;
  va_start(ap, f);
  vfprintf(outfile, f, ap);
  va_end(ap);
}

static void writestring(const char *s)
{
  writestringf("%s", s);
}

/* write page comment */
static void writepageheader(const char *label, int page)
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
static void writepagebody(int p)
{
  if (!fcopy(pageptr[p+1], NULL))
    die("I/O error writing page %d", outputpage);
}

static void writeheadermedia(int p, off_t *ignore, double width, double height)
{
  fseeko(infile, (off_t) 0, SEEK_SET);
  if (pagescmt) {
    char *line;
    if (!fcopy(pagescmt, ignore) || (line = xgetline(infile)) == NULL)
      die("I/O error in header");
    free(line);
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
static int writepartprolog(void)
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
static void writesetup(void)
{
  if (!fcopy(pageptr[0], NULL))
    die("I/O error in prologue");
}

static /* write trailer */
void writetrailer(void)
{
  fseeko(infile, pageptr[pages], SEEK_SET);
  for (char *buffer; (buffer = xgetline(infile)) != NULL; free(buffer))
    writestring(buffer);
  if (verbose)
    fprintf(stderr, "Wrote %d pages\n", outputpage);
}


// Page spec routines for page rearrangement

/* Output paper size */
static double width = -1;
static double height = -1;
/* Input paper size, if different from output */
static double iwidth = -1;
static double iheight = -1;
// Global scale factor
static double scale = 1;
// Global page offsets
static double hshift = 0;
static double vshift = 0;
// Global rotation
static int rotate = 0;

static PageRange *makerange(int beg, int end, PageRange *next)
{
  PageRange *new = (PageRange *)XZALLOC(PageRange);
  new->first = beg;
  new->last = end;
  new->next = next;
  return (new);
}

static PageRange *addrange(char *str, PageRange *rp)
{
  int first=0;
  int sign;

  if(!str) return NULL;

  sign = (*str == '_' && ++str) ? -1 : 1;
  if (isdigit((unsigned char)*str)) {
    first = sign*atoi(str);
    while (isdigit((unsigned char)*str)) str++;
  }
  switch (*str) {
  case '\0':
    if (first || sign < 0)
      return (makerange(first, first, rp));
    break;
  case ',':
    if (first || sign < 0)
      return (addrange(str+1, makerange(first, first, rp)));
    break;
  case '-':
  case ':':
    str++;
    sign = (*str == '_' && ++str) ? -1 : 1;
    if (!first)
      first = 1;
    if (isdigit((unsigned char)*str)) {
      int last = sign*atoi(str);
      while (isdigit((unsigned char)*str)) str++;
      if (*str == '\0')
        return (makerange(first, last, rp));
      if (*str == ',')
        return (addrange(str+1, makerange(first, last, rp)));
    } else if (*str == '\0')
      return (makerange(first, -1, rp));
    else if (*str == ',')
      return (addrange(str+1, makerange(first, -1, rp)));
  default: /* Avoid a compiler warning */
    break;
  }
  die("invalid page range");
  return NULL;
}

/* create a new page spec */
static PageSpec *newspec(void)
{
  PageSpec *temp = (PageSpec *)XZALLOC(PageSpec);
  temp->pageno = temp->flags = temp->rotate = 0;
  temp->scale = 1;
  temp->xoff = temp->yoff = 0;
  temp->next = NULL;
  return (temp);
}

/* dimension parsing routines */
static long parseint(char **sp)
{
  char *s = *sp;
  long num = atol(s);

  while (isdigit((unsigned char)*s))
    s++;
  if (*sp == s) argerror();
  *sp = s;
  return (num);
}

static double parsedouble(char **sp)
{
  char *s = *sp;
  double num = atof(s);

  while (isdigit((unsigned char)*s) || *s == '-' || *s == '.')
    s++;
  if (*sp == s) argerror();
  *sp = s;
  return (num);
}

static double parsedimen(char **sp)
{
  double num = parsedouble(sp);
  char *s = *sp;

  if (strncmp(s, "pt", 2) == 0) {
    s += 2;
  } else if (strncmp(s, "in", 2) == 0) {
    num *= 72;
    s += 2;
  } else if (strncmp(s, "cm", 2) == 0) {
    num *= 28.346456692913385211;
    s += 2;
  } else if (strncmp(s, "mm", 2) == 0) {
    num *= 2.8346456692913385211;
    s += 2;
  } else if (*s == 'w') {
    if (width < 0)
      die("width not set");
    num *= width;
    s++;
  } else if (*s == 'h') {
    if (height < 0)
      die("height not set");
    num *= height;
    s++;
  }
  *sp = s;
  return (num);
}

static double singledimen(char *str)
{
  double num = parsedimen(&str);
  if (*str) usage();
  return (num);
}


static int negative_page_to_positive(int n, int pages)
{
  if (n < 0) {
    n += pages + 1;
    if (n < 1)
      n = 1;
  }
  return n;
}

static int page_index_to_real_page(PageSpec *ps, int maxpage, int modulo, int signature, int pagebase)
{
  int page_number = (ps->flags & REVERSED ? maxpage - pagebase - modulo : pagebase) + ps->pageno;
  int real_page = page_number - page_number % signature;
  int page_on_sheet = page_number % 4;
  if (page_on_sheet == 0 || page_on_sheet == 3)
    real_page += signature - 1 - (page_number % signature) / 2;
  else
    real_page += (page_number % signature) / 2;
  return real_page;
}

static const char *procset = /* PStoPS procset */
  /* Wrap these up with our own versions.  We have to  */
  "userdict begin\n\
[/showpage/erasepage/copypage]{dup where{pop dup load\n\
 type/operatortype eq{ /PStoPSenablepage cvx 1 index\
 load 1 array astore cvx {} bind /ifelse cvx 4 array\
 astore cvx def}{pop}ifelse}{pop}ifelse}forall\
 /PStoPSenablepage true def\n\
[/letter/legal/executivepage/a4/a4small/b5/com10envelope\n" // nullify
  " /monarchenvelope/c5envelope/dlenvelope/lettersmall/note\n" // paper
  " /folio/quarto/a5]{dup where{dup wcheck{exch{}put}\n" // operators
  " {pop{}def}ifelse}{pop}ifelse}forall\n\
/setpagedevice {pop}bind 1 index where{dup wcheck{3 1 roll put}\n\
 {pop def}ifelse}{def}ifelse\n\
/PStoPSmatrix matrix currentmatrix def\n\
/PStoPSxform matrix def/PStoPSclip{clippath}def\n\
/defaultmatrix{PStoPSmatrix exch PStoPSxform exch concatmatrix}bind def\n\
/initmatrix{matrix defaultmatrix setmatrix}bind def\n\
/initclip[{matrix currentmatrix PStoPSmatrix setmatrix\n\
 [{currentpoint}stopped{$error/newerror false put{newpath}}\n\
 {/newpath cvx 3 1 roll/moveto cvx 4 array astore cvx}ifelse]\n\
 {[/newpath cvx{/moveto cvx}{/lineto cvx}\n\
 {/curveto cvx}{/closepath cvx}pathforall]cvx exch pop}\n\
 stopped{$error/errorname get/invalidaccess eq{cleartomark\n\
 $error/newerror false put cvx exec}{stop}ifelse}if}bind aload pop\n\
 /initclip dup load dup type dup/operatortype eq{pop exch pop}\n\
 {dup/arraytype eq exch/packedarraytype eq or\n\
  {dup xcheck{exch pop aload pop}{pop cvx}ifelse}\n\
  {pop cvx}ifelse}ifelse\n\
 {newpath PStoPSclip clip newpath exec setmatrix} bind aload pop]cvx def\n\
/initgraphics{initmatrix newpath initclip 1 setlinewidth\n\
 0 setlinecap 0 setlinejoin []0 setdash 0 setgray\n\
 10 setmiterlimit}bind def\n\
end\n";

static void xastrcat(char **s1, const char *s2)
{
  char *t = xasprintf("%s%s", *s1 ? *s1 : "", s2);
  free(*s1);
  *s1 = t;
}

// FIXME: improve variable names
static void pstops(PageRange *pagerange, int signature, int modulo, int pps, int odd, int even, int reverse, int nobind, PageSpec *specs, double draw, off_t *ignorelist)
{
  // If input paper size given and different from output paper size, find best orientation for output
  if (iwidth >= 0 && (iwidth != width || iheight != height)) {
    // Calculate normal orientation
    scale = MIN(width / iwidth, height / iheight);
    double waste = pow(width - scale * iwidth, 2) + pow(height - scale * iheight, 2);

    // Calculate rotated orientation
    double rscale = MIN(height / iwidth, width / iheight);
    double rwaste = pow(height - scale * iwidth, 2) + pow(width - scale * iheight, 2);

    // Use the orientation with the least waste
    if (rwaste < waste) {
      scale = rscale;
      rotate = 90;
      double tmp = width;
      width = height;
      height = tmp;
      hshift = (height - iheight * scale) / 2; // FIXME: height + inheight * scale ?
      vshift = (width - iwidth * scale) / 2;
    } else {
      hshift = (width - iwidth * scale) / 2;
      vshift = (height - iheight * scale) / 2;
    }

    width /= scale;
    height /= scale;
  }

  /* If no page range given, select all pages */
  if (pagerange == NULL)
    pagerange = makerange(1, -1, NULL);

  /* Reverse page list if not reversing pages (list constructed bottom up) */
  if (!reverse) {
    PageRange *revlist = NULL;
    for (PageRange *next = NULL; pagerange; pagerange = next) {
      next = pagerange->next;
      pagerange->next = revlist;
      revlist = pagerange;
    }
    pagerange = revlist;
  } else { /* Swap start & end if reversing */
    for (PageRange *r = pagerange; r; r = r->next) {
      int temp = r->last;
      r->last = r->first;
      r->first = temp;
    }
  }

  /* adjust for end-relative pageranges */
  for (PageRange *r = pagerange; r; r = r->next) {
    r->first = negative_page_to_positive(r->first, pages);
    r->last = negative_page_to_positive(r->last, pages);
  }

  /* Get list of pages */
  int pages_to_output = 0;
  size_t page_to_real_page[1000000]; // FIXME!
  for (PageRange *r = pagerange; r != NULL; r = r->next) {
    int inc = r->last < r->first ? -1 : 1;
    for (int currentpg = r->first; r->last - currentpg != -inc; currentpg += inc) {
      if (currentpg == 0 || (currentpg <= (int)pages &&
                             !(odd && !even && currentpg % 2 == 0) &&
                             !(even && !odd && currentpg % 2 == 1)))
        page_to_real_page[pages_to_output++] = currentpg - 1;
    }
  }

  /* Adjust for signature size */
  int maxpage = ((pages_to_output + modulo - 1) / modulo) * modulo;
  if (signature == 0)
    signature = maxpage = pages_to_output + (4 - pages_to_output % 4) % 4;
  else {
    unsigned long lcm = (signature / gcd(signature, modulo)) * modulo;
    maxpage = pages_to_output + (lcm - pages_to_output % lcm) % lcm;
  }

  // Work out whether we need procset
  int global_transform = scale != 1 || hshift != 0 || vshift != 0 || rotate != 0;
  int use_procset = global_transform;
  if (use_procset == 0)
    for (PageSpec *p = specs; p && !use_procset; p = p->next)
      use_procset |= p->flags & (GSAVE | ADD_NEXT);

  /* rearrange pages: doesn't cope properly with loaded definitions */
  writeheadermedia((maxpage / modulo) * pps, ignorelist, width, height);
  if (use_procset) {
    writestring("%%BeginProcSet: PStoPS");
    if (nobind)
      writestring("-nobind");
    writestring(" 1 15\n");
    writestring(procset);
    if (nobind) /* desperation measures */
      writestring("/bind{}def\n");
    writestring("%%EndProcSet\n");
  }
  /* save transformation from original to current matrix */
  if (writepartprolog() && use_procset) {
    writestring("userdict/PStoPSxform PStoPSmatrix matrix currentmatrix\n\
 matrix invertmatrix matrix concatmatrix\n\
 matrix invertmatrix put\n");
  }
  writesetup();
  int pageindex = 0;
  for (int pagebase = 0; pagebase < maxpage; pagebase += modulo) {
    int add_last = 0;
    for (PageSpec *ps = specs; ps != NULL; ps = ps->next) {
      int real_page = page_index_to_real_page(ps, maxpage, modulo, signature, pagebase);
      if (real_page < pages_to_output && page_to_real_page[real_page] < pages)
        seekpage(page_to_real_page[real_page]);
      if (!add_last) {	/* page label contains original pages */
        PageSpec *np = ps;
        char *pagelabel = NULL;
        char sep = '(';
        do {
          char *label = xasprintf("%c%ld", sep, page_to_real_page[page_index_to_real_page(np, maxpage, modulo, signature, pagebase)] + 1);
          xastrcat(&pagelabel, label);
          free(label);
          sep = ',';
        } while ((np->flags & ADD_NEXT) && (np = np->next));
        xastrcat(&pagelabel, ")");
        writepageheader(pagelabel, real_page < pages_to_output && page_to_real_page[real_page] < pages ? ++pageindex : -1);
      }
      if (use_procset)
        writestring("userdict/PStoPSsaved save put\n");
      if (global_transform || ps->flags & GSAVE) {
        writestring("PStoPSmatrix setmatrix\n");
        if (ps->flags & OFFSET)
          writestringf("%f %f translate\n", ps->xoff + hshift, ps->yoff + vshift);
        if (ps->flags & ROTATE)
          writestringf("%d rotate\n", (ps->rotate + rotate) % 360);
        if (ps->flags & HFLIP)
          writestringf("[ -1 0 0 1 %f 0 ] concat\n", width * ps->scale * scale);
        if (ps->flags & VFLIP)
          writestringf("[ 1 0 0 -1 0 %f ] concat\n", height * ps->scale * scale);
        if (ps->flags & SCALE)
          writestringf("%f dup scale\n", ps->scale * scale);
        writestring("userdict/PStoPSmatrix matrix currentmatrix put\n");
        if (width > 0 && height > 0) {
          writestringf("userdict/PStoPSclip{0 0 moveto\n\
 %f 0 rlineto 0 %f rlineto -%f 0 rlineto\n\
 closepath}put initclip\n", width, height, width);
          if (draw > 0)
            writestringf("gsave clippath 0 setgray %f setlinewidth stroke grestore\n", draw);
        }
      }
      if ((add_last = (ps->flags & ADD_NEXT) != 0))
        writestring("/PStoPSenablepage false def\n");
      if (beginprocset && real_page < pages_to_output && page_to_real_page[real_page] < pages) {
        /* search for page setup */
        for (;;) {
          char *buffer = xgetline(infile);
          if (buffer == NULL)
            die("I/O error reading page setup %d", outputpage);
          if (!strncmp(buffer, "PStoPSxform", 11))
            break;
          if (fputs(buffer, outfile) == EOF)
            die("I/O error writing page setup %d", outputpage);
          free(buffer);
        }
      }
      if (!beginprocset && use_procset)
        writestring("PStoPSxform concat\n");
      if (real_page < pages_to_output && page_to_real_page[real_page] < pages)
        writepagebody(page_to_real_page[real_page]);
      else
        writestring("showpage\n");
      if (use_procset)
        writestring("PStoPSsaved restore\n");
    }
  }
  writetrailer();
}

static int signature = 1;
static int modulo = 1;
static int pagesperspec = 1;

static PageSpec *parsespecs(char *str)
{
  PageSpec *head, *tail;
  unsigned long spec_count = 0;
  long num = -1;

  head = tail = newspec();
  while (*str) {
    if (isdigit((unsigned char)*str)) {
      num = parseint(&str);
    } else {
      switch (*str++) {
      case ':':
        if (spec_count > 1 || head != tail || num < 0)
          argerror();
        modulo = num;
        num = -1;
        break;
      case '-':
        tail->flags ^= REVERSED;
        break;
      case '@':
        tail->scale *= parsedouble(&str);
        tail->flags |= SCALE;
        break;
      case 'l': case 'L':
        tail->rotate += 90;
        tail->flags |= ROTATE;
        break;
      case 'r': case 'R':
        tail->rotate -= 90;
        tail->flags |= ROTATE;
        break;
      case 'u': case 'U':
        tail->rotate += 180;
        tail->flags |= ROTATE;
        break;
      case 'h': case 'H':
        tail->flags ^= HFLIP;
        break;
      case 'v': case 'V':
        tail->flags ^= VFLIP;
        break;
      case '(':
        tail->xoff += parsedimen(&str);
        if (*str++ != ',') argerror();
        tail->yoff += parsedimen(&str);
        if (*str++ != ')') argerror();
        tail->flags |= OFFSET;
        break;
      case '+':
        tail->flags |= ADD_NEXT;
      case ',':
        if (num < 0 || num >= modulo)
          argerror();
        if ((tail->flags & ADD_NEXT) == 0)
          pagesperspec++;
        tail->pageno = num;
        tail->next = newspec();
        tail = tail->next;
        num = -1;
        break;
      default:
        argerror();
      }
      spec_count++;
    }
  }
  if (num >= modulo)
    argerror();
  else if (num >= 0)
    tail->pageno = num;
  return (head);
}

int
main(int argc, char *argv[])
{
  PageSpec *specs = NULL;
  PageRange *pagerange = NULL;
  int nobinding = 0, even = 0, odd = 0, reverse = 0;
  double draw = 0;

  set_program_name (argv[0]);

  int opt;
  while ((opt = getopt(argc, argv, "qbd::eh:H:op:P:rR:s:vw:W:0123456789")) != EOF) {
    switch (opt) {
    case 'q':	/* quiet */
      verbose = 0;
      break;
    case 'b':	/* no bind operator */
      nobinding = 1;
      break;
    case 'd':	/* draw borders */
      draw = optarg ? singledimen(optarg) : 1;
      break;
    case 'e':  /* select even pages */
      even = 1;
      break;
    case 'o':  /* select odd pages */
      odd = 1;
      break;
    case 'r':  /* reverse pages */
      reverse = 1;
      break;
    case 'w':	/* page width */
      width = singledimen(optarg);
      break;
    case 'W':	/* input page width */
      iwidth = singledimen(optarg);
      break;
    case 'h':	/* page height */
      height = singledimen(optarg);
      break;
    case 'H':	/* input page height */
      iheight = singledimen(optarg);
      break;
    case 'p':	/* paper type */
      if (!paper_size(optarg, &width, &height))
        die("paper size '%s' not recognised", optarg);
      break;
    case 'P':	/* paper type */
      if (!paper_size(optarg, &iwidth, &iheight))
        die("paper size '%s' not recognised", optarg);
      break;
    case 'R': /* page ranges */
      pagerange = addrange(optarg, pagerange);
      break;
    case 's':  /* signature size */
      signature = parseint(&optarg);
      if (signature < 0 || (signature > 1 && signature % 4))
        usage();
      break;
    case '0':
    case '1':
    case '2':
    case '3':
    case '4':
    case '5':
    case '6':
    case '7':
    case '8':
    case '9':
      if (specs == NULL) {
        char *spec_txt = xzalloc((optarg ? strlen(optarg) : 0) + 3);
        spec_txt[0] = '-';
        spec_txt[1] = opt;
        spec_txt[2] = '\0';
        if (optarg) strcat(spec_txt, optarg);
        specs = parsespecs(spec_txt);
        free(spec_txt);
      } else
        usage();
      break;
    case 'v':	/* version */
    default:
      usage();
      break;
    }
  }

  if (specs == NULL) {
    if (optind == argc)
      usage();
    specs = parsespecs(argv[optind++]);
  }

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

  if ((infile = seekable(infile)) == NULL)
    die("cannot seek input");

  if ((iwidth <= 0) ^ (iheight <= 0))
    die("input page width and height must both be set, or neither");

  off_t *sizeheaders = iwidth >= 0 ? XCALLOC(20, off_t) :NULL;
  scanpages(sizeheaders);
  pstops(pagerange, signature, modulo, pagesperspec, odd, even, reverse, nobinding, specs, draw, sizeheaders);

  return 0;
}
