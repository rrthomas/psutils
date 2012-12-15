/* psspec.h
 * Copyright (C) Angus J. C. Duggan 1991-1995
 * See file LICENSE for details.
 *
 * routines for page rearrangement specs
 */

/* pagespec flags */
#define ADD_NEXT (0x01)
#define ROTATE   (0x02)
#define HFLIP    (0x04)
#define VFLIP    (0x08)
#define SCALE    (0x10)
#define OFFSET   (0x20)
#define GSAVE    (ROTATE|HFLIP|VFLIP|SCALE|OFFSET)

typedef struct pagespec {
   int reversed, pageno, flags, rotate, hflip, vflip;
   double xoff, yoff, scale;
   struct pagespec *next;
} PageSpec ;

extern double width, height;

extern PageSpec *newspec(void);
extern int parseint(char **sp);
extern double parsedouble(char **sp);
extern double parsedimen(char **sp);
extern double singledimen(char *str);
extern void pstops(int modulo, int pps, int nobind, PageSpec *specs,
		   double draw);
extern void pstops_write(int modulo, int pps, int nobind, PageSpec *specs,
                         double draw, off_t *ignorelist);
