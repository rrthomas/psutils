/* psnup.c
 * Copyright (C) Angus J. C. Duggan 1991-1995
 * See file LICENSE for details.
 *
 * put multiple pages onto one physical sheet of paper
 *
 * Usage:
 *      psnup [-q] [-w<dim>] [-h<dim>] [-ppaper] [-b<dim>] [-m<dim>]
 *            [-l] [-c] [-f] [-sscale] [-d<wid>] [-nup] [in [out]]
 *              -w<dim> sets the paper width
 *              -h<dim> sets the paper height
 *              -ppaper sets the paper size (width and height) by name
 *              -W<dim> sets the input paper width, if different from output
 *              -H<dim> sets the input paper height, if different from output
 *              -Ppaper sets the input paper size, if different from output
 *              -m<dim> sets the margin around the paper
 *              -b<dim> sets the border around each page
 *              -sscale alters the scale at which the pages are displayed
 *              -l      used if pages are in landscape orientation (rot left)
 *              -r      used if pages are in seascape orientation (rot right)
 * 		-c	for column-major layout
 *		-f	for flipped (wider than tall) pages
 * 		-d<wid>	to draw the page boundaries
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

static void usage(void)
{
   fprintf(stderr, "%s release %d patchlevel %d\n", program, RELEASE, PATCHLEVEL);
   fprintf(stderr, "Copyright (C) Angus J. C. Duggan, 1991-1995. See file LICENSE for details.\n");
   fprintf(stderr, "Usage: %s [-q] [-wwidth] [-hheight] [-ppaper] [-Wwidth] [-Hheight] [-Ppaper] [-l] [-r] [-c] [-f] [-mmargin] [-bborder] [-dlwidth] [-sscale] [-nup] [infile [outfile]]\n",
	   program);
   fflush(stderr);
   exit(1);
}

static void argerror(void)
{
   message(FATAL, "bad dimension\n");
}

#define MIN(x,y) ((x) > (y) ? (y) : (x))
#define MAX(x,y) ((x) > (y) ? (x) : (y))

/* return next larger exact divisor of number, or 0 if none. There is probably
 * a much more efficient method of doing this, but the numbers involved are
 * small, so it's not a big loss. */
static int nextdiv(int n, int m)
{
   while (++n <= m) {
      if (m%n == 0)
	 return (n);
   }
   return (0);
}

int
main(int argc, char *argv[])
{
   int horiz = 0, vert = 0, rotate = 0, column = 0;
   int flip = 0, leftright = 0, topbottom = 0;
   int nup = 1;
   double draw = 0;				/* draw page borders */
   double scale = 1.0;				/* page scale */
   double uscale = 0;				/* user supplied scale */
   double ppwid, pphgt;				/* paper dimensions */
   double margin, border;			/* paper & page margins */
   double vshift, hshift;			/* page centring shifts */
   double iwidth, iheight ;			/* input paper size */
   double tolerance = 100000;			/* layout tolerance */
   Paper *paper = NULL;
   off_t sizeheaders[20];			/* headers to remove */
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

   margin = border = vshift = hshift = column = flip = 0;
   leftright = topbottom = 1;
   iwidth = iheight = -1 ;

   verbose = 1;
   program = *argv;

   while((opt =
          getopt(argc, argv,
                 "qd::lrfcw:W:h:H:m:b:t:s:p:P:n:1::2::3::4::5::6::7::8::9::"))
         != EOF) {
     switch(opt) {
     case 'q':	/* quiet */
       verbose = 0;
       break;
     case 'd':	/* draw borders */
       if (optarg)
         draw = singledimen(optarg, argerror, usage);
       else
         draw = 1;
       break;
     case 'l':	/* landscape (rotated left) */
       column = !column;
       topbottom = !topbottom;
       break;
     case 'r':	/* seascape (rotated right) */
       column = !column;
       leftright = !leftright;
       break;
     case 'f':	/* flipped */
       flip = 1;
       break;
     case 'c':	/* column major layout */
       column = !column;
       break;
     case 'w':	/* page width */
       width = singledimen(optarg, argerror, usage);
       break;
     case 'W':	/* input page width */
       iwidth = singledimen(optarg, argerror, usage);
       break;
     case 'h':	/* page height */
       height = singledimen(optarg, argerror, usage);
       break;
     case 'H':	/* input page height */
       iheight = singledimen(optarg, argerror, usage);
       break;
     case 'm':	/* margins around whole page */
       margin = singledimen(optarg, argerror, usage);
       break;
     case 'b':	/* border around individual pages */
       border = singledimen(optarg, argerror, usage);
       break;
     case 't':	/* layout tolerance */
       tolerance = atof(optarg);
       break;
     case 's':	/* override scale */
       uscale = atof(optarg);
       break;
     case 'p':	/* output (and by default input) paper type */
       if ( (paper = findpaper(optarg)) != (Paper *)0 ) {
         width = (double)PaperWidth(paper);
         height = (double)PaperHeight(paper);
       } else
         message(FATAL, "paper size '%s' not recognised\n", optarg);
       break;
     case 'P':	/* paper type */
       if ( (paper = findpaper(optarg)) != (Paper *)0 ) {
         iwidth = (double)PaperWidth(paper);
         iheight = (double)PaperHeight(paper);
       } else
         message(FATAL, "paper size '%s' not recognised\n", optarg);
       break;
     case 'n':	/* n-up, for compatibility with other psnups */
       if ((nup = atoi(optarg)) < 1)
         message(FATAL, "-n %d too small\n", nup);
       break;
     case '1':
     case '2':
     case '3':
     case '4':
     case '5':
     case '6':
     case '7':
     case '8':
     case '9':
       if(optarg) {
         char *valuestr = (char *) malloc(strlen(optarg) + 2);
         valuestr[0] = opt;
         strcpy(&(valuestr[1]), optarg);

         /* really should check that valuestr is only digits here...*/
         if ((nup = atoi(valuestr)) < 1)
           message(FATAL, "-n %d too small\n", nup);
         free(valuestr);
       } else {
         nup = (opt - '0');
       }
       break;
     case 'v':	/* version */
     default:
       usage();
     }
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

   if (width <= 0 || height <= 0)
      message(FATAL, "page width and height must be set\n");

   /* subtract paper margins from height & width */
   ppwid = width - margin*2;
   pphgt = height - margin*2;

   if (ppwid <= 0 || pphgt <= 0)
      message(FATAL, "paper margins are too large\n");

   scanpages(sizeheaders);

   /* set default values of input height & width */
   if ( iwidth > 0 )
     width = iwidth ;
   if ( iheight > 0 )
     height = iheight ;

   /* Finding the best layout is an optimisation problem. We try all of the
    * combinations of width*height in both normal and rotated form, and
    * minimise the wasted space. */
   {
      double best = tolerance;
      int hor;
      for (hor = 1; hor; hor = nextdiv(hor, nup)) {
	 int ver = nup/hor;
	 /* try normal orientation first */
	 double scl = MIN(pphgt/(height*ver), ppwid/(width*hor));
	 double optim = (ppwid-scl*width*hor)*(ppwid-scl*width*hor) +
	    (pphgt-scl*height*ver)*(pphgt-scl*height*ver);
	 if (optim < best) {
	    best = optim;
	    /* recalculate scale to allow for internal borders */
	    scale = MIN((pphgt-2*border*ver)/(height*ver),
			(ppwid-2*border*hor)/(width*hor));
	    hshift = (ppwid/hor - width*scale)/2;
	    vshift = (pphgt/ver - height*scale)/2;
	    horiz = hor; vert = ver;
	    rotate = flip;
	 }
	 /* try rotated orientation */
	 scl = MIN(pphgt/(width*hor), ppwid/(height*ver));
	 optim = (pphgt-scl*width*hor)*(pphgt-scl*width*hor) +
	    (ppwid-scl*height*ver)*(ppwid-scl*height*ver);
	 if (optim < best) {
	    best = optim;
	    /* recalculate scale to allow for internal borders */
	    scale = MIN((pphgt-2*border*hor)/(width*hor),
			(ppwid-2*border*ver)/(height*ver));
	    hshift = (ppwid/ver - height*scale)/2;
	    vshift = (pphgt/hor - width*scale)/2;
	    horiz = ver; vert = hor;
	    rotate = !flip;
	 }
      }

      /* fail if nothing better than worst tolerance was found */
      if (best == tolerance)
	 message(FATAL, "can't find acceptable layout for %d-up\n", nup);
   }

   if (flip) {	/* swap width & height for clipping */
      double tmp = width;
      width = height;
      height = tmp;
   }

   if (rotate) {	/* rotate leftright and topbottom orders */
      int tmp = topbottom;
      topbottom = !leftright;
      leftright = tmp;
      column = !column;
   }

   /* now construct specification list and run page rearrangement procedure */
   {
      int page = 0;
      PageSpec *specs, *tail;

      tail = specs = newspec();

      while (page < nup) {
	 int up, across;		/* page index */

	 if (column) {
	    if (leftright)		/* left to right */
	       across = page/vert;
	    else			/* right to left */
	       across = horiz-1-page/vert;
	    if (topbottom)		/* top to bottom */
	       up = vert-1-page%vert;
	    else			/* bottom to top */
	       up = page%vert;
	 } else {
	    if (leftright)		/* left to right */
	       across = page%horiz;
	    else			/* right to left */
	       across = horiz-1-page%horiz;
	    if (topbottom)		/* top to bottom */
	       up = vert-1-page/horiz;
	    else			/* bottom to top */
	       up = page/horiz;
	 }
	 if (rotate) {
	    tail->xoff = margin + (across+1)*ppwid/horiz - hshift;
	    tail->rotate = 90;
	    tail->flags |= ROTATE;
	 } else {
	    tail->xoff = margin + across*ppwid/horiz + hshift;
	 }
	 tail->pageno = page;
	 if (uscale > 0)
	    tail->scale = uscale;
	 else
	    tail->scale = scale;
	 tail->flags |= SCALE;
	 tail->yoff = margin + up*pphgt/vert + vshift;
	 tail->flags |= OFFSET;
	 if (++page < nup) {
	    tail->flags |= ADD_NEXT;
	    tail->next = newspec();
	    tail = tail->next;
	 }
      }
      
      pstops_write(nup, 1, 0, specs, draw, sizeheaders); /* do page rearrangement */
   }

   exit(0);
}

