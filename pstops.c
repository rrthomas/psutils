/* pstops.c
 * Rearrange pages in conforming PS file
 *
 * (c) Reuben Thomas 2012-2016
 * (c) Angus J. C. Duggan 1991-1997
 * See file LICENSE for details.
 */

#include "config.h"

#include <unistd.h>
#include <string.h>
#include "progname.h"

#include "psutil.h"
#include "psspec.h"

const char *syntax = "[-q] [-b] [-wWIDTH -hHEIGHT|-pPAPER] [-dLWIDTH] [-sSIGNATURE] PAGESPECS [INFILE [OUTFILE]]";

const char *argerr_message = "page specification error:\n"
  "  pagespecs = [[signature:]modulo:]spec\n"
  "  spec      = [-]pageno[@scale][L|R|U|H|V][(xoff,yoff)][,spec|+spec]\n"
  "              modulo >= 1; 0 <= pageno < modulo\n"
  "  SIGNATURE = 0, 1, or a positive multiple of 4";

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
   while((opt = getopt(argc, argv, "qbd::eh:op:rR:s:vw:0123456789")) != EOF) {
     switch(opt) {
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
     case 'h':	/* page height */
       height = singledimen(optarg);
       break;
     case 'p':	/* paper type */
       if (!paper_size(optarg, &width, &height))
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
         char *spec_txt = malloc((optarg ? strlen(optarg) : 0) + 3);
         if(!spec_txt) die("no memory for spec allocation");
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

   parse_input_and_output_files(argc, argv, optind, 1);

   scanpages(NULL);
   pstops(pagerange, signature, modulo, pagesperspec, odd, even, reverse, nobinding, specs, draw, NULL);

   return 0;
}
