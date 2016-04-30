/* psbook.c
 * (c) Reuben Thomas 2012-2016
 * (c) Angus J. C. Duggan 1991-1997
 * See file LICENSE for details.
 *
 * rearrange pages in conforming PS file for printing in signatures
 */

#include "config.h"

#include <unistd.h>
#include "progname.h"

#include "psutil.h"

const char *syntax = "[-q] [-sSIGNATURE] [INFILE [OUTFILE]]\n       SIGNATURE must be positive and divisible by 4\n";

const char *argerr_message = "";

int
main(int argc, char *argv[])
{
   int signature = 0;
   int currentpg, maxpage;
   int opt;

   set_program_name (argv[0]);

   while((opt = getopt(argc, argv, "vqs:")) != EOF) {
     switch(opt) {
     case 's':	/* signature size */
       signature = atoi(optarg);
       if (signature < 1 || signature % 4) usage();
       break;
     case 'q':	/* quiet */
       quiet = 1;
       break;
     case 'v':	/* version */
     default:
       usage();
       break;
     }
   }
   verbose = !quiet;

   parse_input_and_output_files(argc, argv, optind);

   scanpages(NULL);

   if (!signature)
      signature = maxpage = pages+(4-pages%4)%4;
   else
      maxpage = pages+(signature-pages%signature)%signature;

   /* rearrange pages */
   writeheader(maxpage, NULL);
   writeprolog();
   writesetup();
   for (currentpg = 0; currentpg < maxpage; currentpg++) {
      int actualpg = currentpg - currentpg % signature;
      int page_on_sheet = currentpg % 4;
      if (page_on_sheet == 0 || page_on_sheet == 3)
	 actualpg += signature - 1 - (currentpg % signature) / 2;
      else
	 actualpg += (currentpg % signature) / 2;
      if (actualpg < pages)
	 writepage(actualpg);
      else
	 writeemptypage();
   }
   writetrailer();

   return 0;
}
