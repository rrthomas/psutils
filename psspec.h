/* psspec.h
 * Page spec routines for page rearrangement
 *
 * (c) Reuben Thomas 2012-2016
 * (c) Angus J. C. Duggan 1991-1997
 * See file LICENSE for details.
 */

/* pagespec flags */
#define ADD_NEXT (0x01)
#define ROTATE   (0x02)
#define HFLIP    (0x04)
#define VFLIP    (0x08)
#define SCALE    (0x10)
#define OFFSET   (0x20)
#define REVERSED (0x40)
#define GSAVE    (ROTATE|HFLIP|VFLIP|SCALE|OFFSET)

typedef struct pagespec {
   int pageno, flags, rotate;
   double xoff, yoff, scale;
   struct pagespec *next;
} PageSpec ;

typedef struct pgrange {
   int first, last;
   struct pgrange *next;
} PageRange;

extern double width, height; /* Width and height of output paper in PostScript pt */
extern double iwidth, iheight; /* Width and height of input paper in PostScript pt */

extern PageSpec *newspec(void);
extern long parseint(char **sp);
extern double parsedouble(char **sp);
extern double parsedimen(char **sp);
extern double singledimen(char *str);
extern void pstops(PageRange *pagerange, int signature, int modulo, int pps, int odd, int even, int reverse,
                   int nobind, PageSpec *specs, double draw, off_t *ignorelist);
extern PageRange *makerange(int beg, int end, PageRange *next);
extern PageRange *addrange(char *str, PageRange *rp);
