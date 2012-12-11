/* psresize.c
 * Copyright (C) Angus J. C. Duggan 1991-1995
 * See file LICENSE for details.
 *
 * alter pagesize of document
 *
 * Usage:
 *      psresize [-q] [-w<dim>] [-h<dim>] [-ppaper] [-W<dim>] [-H<dim>]
 *            [-Ppaper] [in [out]]
 *              -w<dim> sets the output paper width
 *              -h<dim> sets the output paper height
 *              -ppaper sets the output paper size (width and height) by name
 *              -W<dim> sets the input paper width
 *              -H<dim> sets the input paper height
 *              -Ppaper sets the input paper size (width and height) by name
 */

#include <unistd.h>

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
   fprintf(stderr, "Usage: %s [-q] [-wwidth] [-hheight] [-ppaper] [-Wwidth] [-Hheight] [-Ppaper] [infile [outfile]]\n",
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

int
main(int argc, char *argv[])
{
   double scale, rscale;			/* page scale */
   double waste, rwaste;			/* amount wasted */
   double vshift, hshift;			/* page centring shifts */
   int rotate;
   double inwidth = -1;
   double inheight = -1;
   Paper *paper = NULL;
   PageSpec *specs;
   int opt;

#ifdef HAVE_LIBPAPER
   paperinit();
   {
     const char *default_size = systempapername();
     if (!default_size) default_size = defaultpapername ();
     if (default_size) paper = findpaper(default_size);
     if (paper) {
       inwidth = width = (double)PaperWidth(paper);
       inheight = height = (double)PaperHeight(paper);
     }
   }
   paperdone();
#elif defined(PAPER)
   if ( (paper = findpaper(PAPER)) != (Paper *)0 ) {
      inwidth = width = (double)PaperWidth(paper);
      inheight = height = (double)PaperHeight(paper);
   }
#endif

   vshift = hshift = 0;
   rotate = 0;

   verbose = 1;


   program = *argv;

   while((opt = getopt(argc, argv,
                       "qw:h:p:W:H:P:")) != EOF) {
     switch(opt) {

     case 'q':	/* quiet */
       verbose = 0;
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
     case 'W':	/* input page width */
       inwidth = singledimen(optarg, argerror, usage);
       break;
     case 'H':	/* input page height */
       inheight = singledimen(optarg, argerror, usage);
       break;
     case 'P':	/* input paper type */
       if ( (paper = findpaper(optarg)) != (Paper *)0 ) {
         inwidth = (double)PaperWidth(paper);
         inheight = (double)PaperHeight(paper);
       } else
         message(FATAL, "paper size '%s' not recognised\n", optarg);
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
      message(FATAL, "output page width and height must be set\n");

   if (inwidth <= 0 || inheight <= 0)
      message(FATAL, "input page width and height must be set\n");

   /* try normal orientation first */
   scale = MIN(width/inwidth, height/inheight);
   waste = (width-scale*inwidth)*(width-scale*inwidth) +
      (height-scale*inheight)*(height-scale*inheight);
   hshift = (width - inwidth*scale)/2;
   vshift = (height - inheight*scale)/2;

   /* try rotated orientation */
   rscale = MIN(height/inwidth, width/inheight);
   rwaste = (height-scale*inwidth)*(height-scale*inwidth) +
      (width-scale*inheight)*(width-scale*inheight);
   if (rwaste < waste) {
      double tmp = width;
      scale = rscale;
      hshift = (width + inheight*scale)/2;
      vshift = (height - inwidth*scale)/2;
      rotate = 1;
      width = height;
      height = tmp;
   }

   width /= scale;
   height /= scale;

   /* now construct specification list and run page rearrangement procedure */
   specs = newspec();

   if (rotate) {
      specs->rotate = 90;
      specs->flags |= ROTATE;
   }
   specs->pageno = 0;
   specs->scale = scale;
   specs->flags |= SCALE;
   specs->xoff = hshift;
   specs->yoff = vshift;
   specs->flags |= OFFSET;
      
   pstops(1, 1, 0, specs, 0.0);		/* do page rearrangement */

   exit(0);
}

