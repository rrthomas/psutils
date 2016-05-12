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

#include "gcd.h"

double width = -1;
double height = -1;

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


int page_index_to_real_page(PageSpec *ps, int maxpage, int modulo, int signature, int pagebase)
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

static const char *prologue = /* PStoPS procset */
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

void pstops(int signature, int modulo, int pps, int nobind, PageSpec *specs, double draw, off_t *ignorelist)
{
   int maxpage = ((pages+modulo-1)/modulo)*modulo;
   if (signature == 0)
      signature = maxpage = pages+(4-pages%4)%4;
   else {
      unsigned long lcm = (signature / gcd(signature, modulo)) * modulo;
      maxpage = pages+(lcm-pages%lcm)%lcm;
   }

   /* rearrange pages: doesn't cope properly with loaded definitions */
   writeheadermedia((maxpage/modulo)*pps, ignorelist, width, height);
   writestring("%%BeginProcSet: PStoPS");
   if (nobind)
      writestring("-nobind");
   writestring(" 1 15\n");
   writestring(prologue);
   if (nobind) /* desperation measures */
      writestring("/bind{}def\n");
   writestring("%%EndProcSet\n");
   /* save transformation from original to current matrix */
   if (writepartprolog()) {
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

	 if (real_page < pages)
	    seekpage(real_page);
	 if (!add_last) {	/* page label contains original pages */
	    PageSpec *np = ps;
	    char *eob = pagelabel;
	    char sep = '(';
	    do {
               eob += sprintf(eob, "%c%d", sep, page_index_to_real_page(np, maxpage, modulo, signature, pagebase) + 1);
	       sep = ',';
	    } while ((np->flags & ADD_NEXT) && (np = np->next));
	    strcpy(eob, ")");
	    writepageheader(pagelabel, real_page < pages ? ++pageindex : -1);
	 }
	 writestring("userdict/PStoPSsaved save put\n");
	 if (ps->flags & GSAVE) {
	    writestring("PStoPSmatrix setmatrix\n");
	    if (ps->flags & OFFSET)
	       writestringf("%f %f translate\n", ps->xoff, ps->yoff);
	    if (ps->flags & ROTATE)
	       writestringf("%d rotate\n", ps->rotate);
	    if (ps->flags & HFLIP)
	       writestringf("[ -1 0 0 1 %f 0 ] concat\n", width*ps->scale);
	    if (ps->flags & VFLIP)
	       writestringf("[ 1 0 0 -1 0 %f ] concat\n", height*ps->scale);
	    if (ps->flags & SCALE)
	       writestringf("%f dup scale\n", ps->scale);
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
	 if (real_page < pages)
	    writepagesetup();
         if (beginprocset)
            writestring("PStoPSxform concat\n");
         if (real_page < pages)
	    writepagebody(real_page);
	 else
            writestring("showpage\n");
	 writestring("PStoPSsaved restore\n");
      }
   }
   writetrailer();
}
