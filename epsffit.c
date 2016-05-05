/* epsffit.c
 * Fit EPSF file into constrained size
 *
 * (c) Reuben Thomas 2012-2016
 * (c) Angus J. C. Duggan 1991-1997
 * See file LICENSE for details.
 *
 * Added filename spec (from Larry Weissman) 5 Feb 93
 * Accepts double %%BoundingBox input, outputs proper BB, 4 Jun 93. (I don't
 * like this; developers should read the Big Red Book before writing code which
 * outputs PostScript.
 */

#include "config.h"

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>
#include <unistd.h>
#include "progname.h"
#include "binary-io.h"
#include "minmax.h"

#include "psutil.h"
#include "psspec.h"

const char *syntax = "[-c] [-r] [-a] [-m] [-s] LLX LLY URX URY [INFILE [OUTFILE]]";

const char *argerr_message = "bad dimension";

int
main(int argc, char **argv)
{
   int bbfound = 0;              /* %%BoundingBox: found */
   int urx = 0, ury = 0, llx = 0, lly = 0;
   double furx, fury, fllx, flly;
   int showpage = 0, centre = 0, rotate = 0, aspect = 0, maximise = 0;
   char buf[BUFSIZ];
   int opt;

   set_program_name(argv[0]);

   while((opt = getopt(argc, argv, "csramv")) != EOF) {
     switch(opt) {
     case 'c': centre = 1; break;
     case 's': showpage = 1; break;
     case 'r': rotate = 1; break;
     case 'a': aspect = 1; break;
     case 'm': maximise = 1; break;
     case 'v':
     default:
       usage();
       break;
     }
   }

   if ((argc - optind) < 4)
      usage();

   fllx = singledimen(argv[optind++]);
   flly = singledimen(argv[optind++]);
   furx = singledimen(argv[optind++]);
   fury = singledimen(argv[optind++]);

   parse_input_and_output_files(argc, argv, optind, 0);

   while (fgets(buf, BUFSIZ, infile)) {
      if (buf[0] == '%' && (buf[1] == '%' || buf[1] == '!')) {
	 /* still in comment section */
	 if (!strncmp(buf, "%%BoundingBox:", 14)) {
	    double illx, illy, iurx, iury;	/* input bbox parameters */
	    if (sscanf(buf, "%%%%BoundingBox:%lf %lf %lf %lf\n",
		       &illx, &illy, &iurx, &iury) == 4) {
	       bbfound = 1;
	       llx = (int)illx;	/* accept doubles, but convert to int */
	       lly = (int)illy;
	       urx = (int)(iurx+0.5);
	       ury = (int)(iury+0.5);
	    }
	 } else if (!strncmp(buf, "%%EndComments", 13)) {
	    strcpy(buf, "\n"); /* don't repeat %%EndComments */
	    break;
	 } else writestring(buf);
      } else break;
   }

   if (!bbfound)
      die("no %%%%BoundingBox:");

   /* put BB, followed by scale&translate */
   double xoffset = fllx, yoffset = flly;
   double width = urx-llx, height = ury-lly;

   if (maximise)
      if ((width > height && fury-flly > furx - fllx) ||
          (width < height && fury-flly < furx - fllx))
         rotate = 1;

   int fwidth, fheight;
   if (rotate) {
      fwidth = fury - flly;
      fheight = furx - fllx;
   } else {
      fwidth = furx - fllx;
      fheight = fury - flly;
   }

   double xscale = fwidth/width;
   double yscale = fheight/height;

   if (!aspect)         /* preserve aspect ratio ? */
      xscale = yscale = MIN(xscale,yscale);
   width *= xscale;     /* actual width and height after scaling */
   height *= yscale;
   if (centre) {
      if (rotate) {
         xoffset += (fheight - height)/2;
         yoffset += (fwidth - width)/2;
      } else {
         xoffset += (fwidth - width)/2;
         yoffset += (fheight - height)/2;
      }
   }
   writestringf("%%%%BoundingBox: %d %d %d %d\n", (int)xoffset, (int)yoffset,
           (int)(xoffset + (rotate ? height : width)),
           (int)(yoffset + (rotate ? width : height)));
   if (rotate) {  /* compensate for original image shift */
      xoffset += height + lly * yscale;  /* displacement for rotation */
      yoffset -= llx * xscale;
   } else {
      xoffset -= llx * xscale;
      yoffset -= lly * yscale;
   }
   writestring("%%EndComments\n");
   if (showpage)
      writestring("save /showpage{}def /copypage{}def /erasepage{}def\n");
   else
      writestring("%%BeginProcSet: epsffit 1 0\n");
   writestring("gsave\n");
   writestringf("%.3f %.3f translate\n", xoffset, yoffset);
   if (rotate)
      writestring("90 rotate\n");
   writestringf("%.3f %.3f scale\n", xscale, yscale);
   if (!showpage)
      writestring("%%EndProcSet\n");
   do {
      writestring(buf);
   } while (fgets(buf, BUFSIZ, infile));
   writestring("grestore\n");
   if (showpage)
      writestring("restore showpage\n"); /* just in case */

   return 0;
}
