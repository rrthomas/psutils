/* pserror.c
 * Copyright (C) Angus J. C. Duggan 1991-1995
 * See file LICENSE for details.
 *
 * Warnings and errors for PS programs
 */

#include "psutil.h"
#include "pserror.h"

#include <string.h>

/* Message function: for messages, warnings, and errors sent to stderr.
   If called with the flag MESSAGE_EXIT set, the routine does not return. */
void message(int flags, const char *format, ...)
{
  va_list args ;

  if ( flags & MESSAGE_PROGRAM )
    fprintf(stderr, "%s: ", program) ;

  if ( (flags & MESSAGE_NL) )
    putc('\n', stderr) ;

  va_start(args, format) ;
  vfprintf(stderr, format, args);
  va_end(args) ;

  if ( flags & MESSAGE_EXIT )	/* don't return to program */
    exit(1) ;
}
