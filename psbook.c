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
#include "psspec.h"

const char *syntax = "[-q] [-sSIGNATURE] [INFILE [OUTFILE]]\n       SIGNATURE must be positive and divisible by 4";

const char *argerr_message = "";

int
main(int argc, char *argv[])
{
   int signature = 0;

   set_program_name(argv[0]);

   int opt;
   while ((opt = getopt(argc, argv, "vqs:")) != EOF) {
     switch (opt) {
     case 's':	/* signature size */
       signature = atoi(optarg);
       if (signature < 1 || signature % 4)
         usage();
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

   parse_input_and_output_files(argc, argv, optind, 1);

   /* rearrange pages */
   scanpages(NULL);
   pstops(signature, 1, 1, 0, newspec(), 0.0, NULL);

   return 0;
}
