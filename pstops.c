/* pstops.c
 * Copyright (C) Angus J. C. Duggan 1991-1995
 * See file LICENSE for details.
 *
 * rearrange pages in conforming PS file for printing in signatures
 *
 * Usage:
 *       pstops [-q] [-b] [-d] [-w<dim>] [-h<dim>] [-ppaper] <pagespecs> [infile [outfile]]
 */

#include <unistd.h>
#include <string.h>

#include "psutil.h"
#include "psspec.h"
#include "pserror.h"
#include "patchlev.h"

#ifdef HAVE_LIBPAPER
#include <paper.h>
#endif

char *program ;
int pages ;
int verbose ;
FILE *infile ;
FILE *outfile ;
char pagelabel[BUFSIZ] ;
int pageno ;

void usage(void)
{
   fprintf(stderr, "%s release %d patchlevel %d\n", program, RELEASE, PATCHLEVEL);
   fprintf(stderr, "Copyright (C) Angus J. C. Duggan, 1991-1995. See file LICENSE for details.\n");
   fprintf(stderr, "Usage: %s [-q] [-b] [-wwidth] [-hheight] [-dlwidth] [-ppaper] <pagespecs> [infile [outfile]]\n",
	   program);
   fflush(stderr);
   exit(1);
}

static void argerror(void)
{
   fprintf(stderr, "%s: page specification error:\n", program);
   fprintf(stderr, "  <pagespecs> = [modulo:]<spec>\n");
   fprintf(stderr, "  <spec>      = [-]pageno[@scale][L|R|U][(xoff,yoff)][,spec|+spec]\n");
   fprintf(stderr, "                modulo>=1, 0<=pageno<modulo\n");
   fflush(stderr);
   exit(1);
}

static int modulo = 1;
static int pagesperspec = 1;

static PageSpec *parsespecs(char *str)
{
   PageSpec *head, *tail;
   unsigned long spec_count = 0;
   long num = -1;

   head = tail = newspec();
   while (*str) {
      if (isdigit(*str)) {
	 num = parseint(&str, argerror);
      } else {
	 switch (*str++) {
	 case ':':
	    if (spec_count || head != tail || num < 1) argerror();
	    modulo = num;
	    num = -1;
	    break;
	 case '-':
	    tail->reversed = !tail->reversed;
	    break;
	 case '@':
            tail->scale *= parsedouble(&str, argerror);
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
	 case '(':
	    tail->xoff += parsedimen(&str, argerror);
	    if (*str++ != ',') argerror();
	    tail->yoff += parsedimen(&str, argerror);
	    if (*str++ != ')') argerror();
	    tail->flags |= OFFSET;
	    break;
	 case '+':
	    tail->flags |= ADD_NEXT;
	 case ',':
	    if (num < 0 || num >= modulo) argerror();
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
   int nobinding = 0;
   double draw = 0;
   Paper *paper = NULL;
   int opt;

#ifdef HAVE_LIBPAPER
   paperinit();
   {
     const char *default_size = systempapername();
     if (!default_size) default_size = defaultpapername ();
     if (default_size) paper = findpaper(default_size);
     if (paper) {
       width = (double)PaperWidth(paper);
       height = (double)PaperHeight(paper);
     }
   }
   paperdone();
#elif defined(PAPER)
   if ( (paper = findpaper(PAPER)) != (Paper *)0 ) {
      width = (double)PaperWidth(paper);
      height = (double)PaperHeight(paper);
   }
#endif

   verbose = 1;

   program = *argv;

   while((opt = getopt(argc, argv, "qd::bw:h:p:v0123456789")) != EOF) {
     switch(opt) {
     case 'q':	/* quiet */
       verbose = 0;
       break;
     case 'd':	/* draw borders */
       if(optarg)
         draw = singledimen(optarg, argerror, usage);
       else
         draw = 1;
       break;
     case 'b':	/* no bind operator */
       nobinding = 1;
       break;
     case 'w':	/* page width */
       width = singledimen(optarg, argerror, usage);
       break;
     case 'h':	/* page height */
       height = singledimen(optarg, argerror, usage);
       break;
     case 'p':	/* paper type */
       if ( (paper = findpaper(optarg)) != (Paper *)0 ) {
         width = (double)PaperWidth(paper);
         height = (double)PaperHeight(paper);
       } else
         message(FATAL, "paper size '%s' not recognised\n", optarg);
       break;
     case 'v':	/* version */
       usage();
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
         char *spec_txt = alloca((optarg ? strlen(optarg) : 0) + 3);
         if(!spec_txt) message(FATAL, "no memory for spec allocation\n");
         spec_txt[0] = '-';
         spec_txt[1] = opt;
         spec_txt[2] = 0;
         if (optarg) strcat(spec_txt, optarg);
         specs = parsespecs(spec_txt);
       } else {
         usage();
       }
       break;
     default:
       usage();
       break;
     }
   }

   if (specs == NULL) {
     if(optind == argc) usage();
     specs = parsespecs(argv[optind]);
     optind++;
   }

   infile = stdin;
   outfile = stdout;

   /* Be defensive */
   if((argc - optind) < 0 || (argc - optind) > 2) usage();

   if (optind != argc) {
     /* User specified an input file */
     if ((infile = fopen(argv[optind], OPEN_READ)) == NULL)
       message(FATAL, "can't open input file %s\n", argv[optind]);
     optind++;
   }

   if (optind != argc) {
     /* User specified an output file */
     if ((outfile = fopen(argv[optind], OPEN_WRITE)) == NULL)
       message(FATAL, "can't open output file %s\n", argv[optind]);
     optind++;
   }

   if (optind != argc) usage();
   if (specs == NULL) usage();

#if defined(MSDOS) || defined(WINNT)
   if ( infile == stdin ) {
      int fd = fileno(stdin) ;
      if ( setmode(fd, O_BINARY) < 0 )
         message(FATAL, "can't open input file %s\n", argv[4]);
    }
   if ( outfile == stdout ) {
      int fd = fileno(stdout) ;
      if ( setmode(fd, O_BINARY) < 0 )
         message(FATAL, "can't reset stdout to binary mode\n");
    }
#endif
   if ((infile=seekable(infile))==NULL)
      message(FATAL, "can't seek input\n");

   pstops(modulo, pagesperspec, nobinding, specs, draw);

   exit(0);
}
