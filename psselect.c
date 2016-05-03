/* psselect.c
 * Rearrange pages in conforming PS file for printing in signatures
 *
 * (c) Reuben Thomas 2012-2016
 * (c) Angus J. C. Duggan 1991-1997
 * See file LICENSE for details.
 */

#include "config.h"

#include <unistd.h>
#include "progname.h"

#include "psutil.h"

const char *syntax = "[-q] [-e] [-o] [-r] [-pPAGES] [INFILE [OUTFILE]]";

const char *argerr_message = "";

typedef struct pgrange {
   int first, last;
   struct pgrange *next;
} PageRange ;

static PageRange *makerange(int beg, int end, PageRange *next)
{
   PageRange *new;
   if ((new = (PageRange *)malloc(sizeof(PageRange))) == NULL)
      die("out of memory");
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

static int negative_page_to_positive(int n, int pages)
{
  if (n < 0) {
    n += pages + 1;
    if (n < 1)
      n = 1;
  }
  return n;
}

static int process_pages(PageRange *pagerange, int odd, int even, int count_only)
{
  int maxpage = 0;
  /* select all pages in range if odd or even not set */
  int all = !(odd || even);
  for (PageRange *r = pagerange; r != NULL; r = r->next) {
    int inc = r->last < r->first ? -1 : 1;
    for (int currentpg = r->first; r->last - currentpg != -inc; currentpg += inc) {
      if (currentpg == 0 ||
          (currentpg <= pages &&
           ((currentpg & 1) ? (odd || all) : (even || all)))) {
        if (!count_only) {
          if (currentpg)
            writepage(currentpg - 1);
          else
            writeemptypage();
        }
        maxpage++;
      }
    }
  }
  return maxpage;
}

int
main(int argc, char *argv[])
{
   int even = 0, odd = 0, reverse = 0;
   PageRange *pagerange = NULL;

   set_program_name (argv[0]);

   int opt;
   while((opt = getopt(argc, argv, "eorqvp:")) != EOF) {
     switch(opt) {
     case 'e':	/* even pages */
       even = 1;
       break;
     case 'o':	/* odd pages */
       odd = 1;
       break;
     case 'r':	/* reverse */
       reverse = 1;
       break;
     case 'p':	/* page spec */
       pagerange = addrange(optarg, pagerange);
       break;
     case 'q':	/* quiet */
       verbose = 0;
       break;
     case 'v':	/* version */
     default:
       usage();
       break;
     }
   }

   /* If we haven't gotten a page range yet, we better get one now */
   if (pagerange == NULL && !reverse && !even && !odd) {
     if (optind > argc)
       usage();
     pagerange = addrange(argv[optind++], NULL);
   }

   parse_input_and_output_files(argc, argv, optind, 1);

   scanpages(NULL);

   /* add default page range */
   if (!pagerange)
      pagerange = makerange(1, -1, NULL);

   /* reverse page list if not reversing pages (list constructed bottom up) */
   if (!reverse) {
      PageRange *revlist = NULL;
      PageRange *next = NULL;
      while (pagerange) {
	 next = pagerange->next;
	 pagerange->next = revlist;
	 revlist = pagerange;
	 pagerange = next;
      }
      pagerange = revlist;
   } else { /* swap start & end if reversing */
      PageRange *r;
      for (r = pagerange; r; r = r->next) {
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

   /* First pass: count pages */
   int maxpage = process_pages(pagerange, odd, even, 1);

   /* Second pass: write header, then pages, then trailer */
   writeheader(maxpage, NULL);
   writeprolog();
   writesetup();
   (void)process_pages(pagerange, odd, even, 0);
   writetrailer();

   return 0;
}
