@PERL@
# psmerge: merge PostScript files produced by same application and setup
# usage: psmerge [-oout.ps] file1.ps file2.ps ...
#
# Copyright (C) Angus J. C. Duggan 1991-1995
# See file LICENSE for details.

use strict;
$^W = 1;
my $prog = ($0 =~ m,([^/\\]*)$,) ? $1 : $0;
my $outfile = undef;

usage() unless @ARGV;

while ($ARGV[0] =~ /^-/) {
   $_ = shift;
   if (/^-o(.+)/) {
      $outfile = $1;
   } elsif (/^-t(horough)?$/) {
      # This doesn't do anything, but we leave it for backward compatibility.
   } else {
      usage();
   }
}

my $gs = find_gs();
if (defined $gs)
{
   # Just invoke gs
   $outfile = '/dev/stdout' unless defined $outfile;
   exec +(qw(gs -q -dNOPAUSE -dBATCH -sDEVICE=pswrite),
	  "-sOutputFile=$outfile", '-f', @ARGV);
   die "$prog: exec /usr/bin/gs failed\n";
}
else
{
   warn +("$prog: /usr/bin/gs not found; falling back to old," .
	  " less functional behavior\n");
}

if (defined $outfile)
{
   if (!close(STDOUT) || !open(STDOUT, ">$outfile")) {
      print STDERR "$prog: can't open $1 for output\n";
      exit 1;
   }
}

my $page = 0;
my $first = 1;
my $nesting = 0;

my @header = ();
my $header = 1;

my @trailer = ();
my $trailer = 0;

my @pages = ();
my @body = ();

my @resources = ();
my $inresource = 0;

while (<>) {
   if (/^%%BeginFont:/ || /^%%BeginResource:/ || /^%%BeginProcSet:/) {
      $inresource = 1;
      push(@resources, $_);
   } elsif ($inresource) {
      push(@resources, $_);
      $inresource = 0 if /^%%EndFont/ || /^%%EndResource/ || /^%%EndProcSet/;
       } elsif (/^%%Page:/ && $nesting == 0) {
	  $header = $trailer = 0;
	  push(@pages, join("", @body)) if @body;
	  $page++;
	  @body = ("%%Page: ($page) $page\n");
       } elsif (/^%%Trailer/ && $nesting == 0) {
	  push(@trailer, $_);
	  push(@pages, join("", @body)) if @body;
	  @body = ();
	  $trailer = 1;
	  $header = 0;
       } elsif ($header) {
	  push(@trailer, $_);
	  push(@pages, join("", @body)) if @body;
	  @body = ();
	  $trailer = 1;
	  $header = 0;
       } elsif ($trailer) {
	  if (/^%!/ || /%%EOF/) {
	     $trailer = $first = 0;
	  } elsif ($first) {
	     push(@trailer, $_);
	  }
       } elsif (/^%%BeginDocument/ || /^%%BeginBinary/ || /^%%BeginFile/) {
	  push(@body, $_);
	  $nesting++;
       } elsif (/^%%EndDocument/ || /^%%EndBinary/ || /^%%EndFile/) {
	  push(@body, $_);
	  $nesting--;
       }
}

print @trailer;

sub find_gs
{
   my $path = $ENV{'PATH'} || "";
   my @path = split(':', $path);
   foreach my $dir (@path)
   {
      return "$dir/gs" if -x "$dir/gs";
   }
   undef;
}

sub usage
{
   print STDERR "Usage: $prog [-oout] file...\n";
   exit 1;
}

@END@
