/* psspec.c
 * Page spec routines for page rearrangement
 *
 * (c) Reuben Thomas 2012-2016
 * (c) Angus J. C. Duggan 1991-1997
 * See file LICENSE for details.
 */

#include "config.h"

#include "psutil.h"
#include "psspec.h"

#include <string.h>
#include <math.h>

#include "xvasprintf.h"
#include "gcd.h"
#include "minmax.h"

/* Output paper size */
double width = -1;
double height = -1;
/* Input paper size, if different from output */
double iwidth = -1;
double iheight = -1;
// Global scale factor
static double scale = 1;
// Global page offsets
static double hshift = 0;
static double vshift = 0;
// Global rotation
static int rotate = 0;

PageRange *makerange(int beg, int end, PageRange *next)
{
   PageRange *new;
   if ((new = (PageRange *)malloc(sizeof(PageRange))) == NULL)
      die("out of memory");
   new->first = beg;
   new->last = end;
   new->next = next;
   return (new);
}

PageRange *addrange(char *str, PageRange *rp)
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
PageSpec *newspec(void)
{
   PageSpec *temp = (PageSpec *)malloc(sizeof(PageSpec));
   if (temp == NULL)
      die("out of memory");
   temp->pageno = temp->flags = temp->rotate = 0;
   temp->scale = 1;
   temp->xoff = temp->yoff = 0;
   temp->next = NULL;
   return (temp);
}

/* dimension parsing routines */
long parseint(char **sp)
{
   char *s = *sp;
   long num = atol(s);

   while (isdigit((unsigned char)*s))
      s++;
   if (*sp == s) argerror();
   *sp = s;
   return (num);
}

double parsedouble(char **sp)
{
   char *s = *sp;
   double num = atof(s);

   while (isdigit((unsigned char)*s) || *s == '-' || *s == '.')
      s++;
   if (*sp == s) argerror();
   *sp = s;
   return (num);
}

double parsedimen(char **sp)
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

double singledimen(char *str)
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
 type/operatortype eq{ /PStoPSenablepage cvx 1 index\n\
 load 1 array astore cvx {} bind /ifelse cvx 4 array\n\
 astore cvx def}{pop}ifelse}{pop}ifelse}forall\n\
 /PStoPSenablepage true def\n\
[/letter/legal/executivepage/a4/a4small/b5/com10envelope%nullify\n\
 /monarchenvelope/c5envelope/dlenvelope/lettersmall/note%paper\n\
 /folio/quarto/a5]{dup where{dup wcheck{exch{}put}%operators\n\
 {pop{}def}ifelse}{pop}ifelse}forall\n\
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
void pstops(PageRange *pagerange, int signature, int modulo, int pps, int odd, int even, int reverse, int nobind, PageSpec *specs, double draw, off_t *ignorelist)
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
   int page_to_real_page[1000000]; // FIXME!
   for (PageRange *r = pagerange; r != NULL; r = r->next) {
      int inc = r->last < r->first ? -1 : 1;
      for (int currentpg = r->first; r->last - currentpg != -inc; currentpg += inc) {
         if (currentpg == 0 || (currentpg <= pages &&
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
               char *label = xasprintf("%c%d", sep, page_to_real_page[page_index_to_real_page(np, maxpage, modulo, signature, pagebase)] + 1);
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
         if (beginprocset && use_procset)
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
