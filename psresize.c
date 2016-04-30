/* psresize.c
 * Alter page size of document
 *
 * (c) Reuben Thomas 2012-2016
 * (c) Angus J. C. Duggan 1991-1997
 * See file LICENSE for details.
 */

#include "config.h"

#include <unistd.h>
#include "progname.h"

#include "psutil.h"
#include "psspec.h"

const char *syntax = "[-q] -wWIDTH -hHEIGHT|-pPAPER -WWIDTH -HHEIGHT|-PPAPER [INFILE [OUTFILE]]\n";

const char *argerr_message = "bad dimension\n";

int
main(int argc, char *argv[])
{
   double scale, rscale;			/* page scale */
   double waste, rwaste;			/* amount wasted */
   double vshift, hshift;			/* page centring shifts */
   int rotate;
   double inwidth = -1;
   double inheight = -1;
   off_t sizeheaders[20];			/* headers to remove */
   PageSpec *specs;
   int opt;

   set_program_name (argv[0]);

   vshift = hshift = 0;
   rotate = 0;

   verbose = 1;

   while((opt = getopt(argc, argv,
                       "qw:h:p:W:H:P:")) != EOF) {
     switch(opt) {

     case 'q':	/* quiet */
       verbose = 0;
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
     case 'W':	/* input page width */
       inwidth = singledimen(optarg);
       break;
     case 'H':	/* input page height */
       inheight = singledimen(optarg);
       break;
     case 'P':	/* input paper type */
       if (!paper_size(optarg, &inwidth, &inheight))
         die("paper size '%s' not recognised", optarg);
       break;
     case 'v':	/* version */
     default:
       usage();
     }
   }

   check_paper_size_set();

   infile = stdin;
   outfile = stdout;

   if (argc > optind + 2)
     usage();

   if (optind != argc) {
     /* User specified an input file */
     if ((infile = fopen(argv[optind], "rb")) == NULL)
       die("can't open input file %s", argv[optind]);
     optind++;
   }

   if (optind != argc) {
     /* User specified an output file */
     if ((outfile = fopen(argv[optind], "wb")) == NULL)
       die("can't open output file %s", argv[optind]);
     optind++;
   }

   check_input_and_output_in_binary_mode(infile, outfile);

   if ((infile=seekable(infile))==NULL)
      die("can't seek input");

   scanpages(sizeheaders);

   if (inwidth <= 0 || inheight <= 0)
      die("input page width and height must both be set");

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
      
   pstops(1, 1, 0, specs, 0.0, sizeheaders); /* do page rearrangement */

   return 0;
}

