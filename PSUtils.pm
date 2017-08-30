# PSUtils utility library

package PSUtils;

use v5.14;
use strict;
use warnings;
no if $] >= 5.018, warnings => "experimental::smartmatch";

use POSIX qw(strtod round);

use base qw(Exporter);
our @EXPORT = qw(singledimen paper_size parsepaper);


# Argument parsers
sub singledimen {
  my ($str, $width, $height) = @_;
  my ($num, $unparsed) = strtod($str);
  $str = substr($str, length($str) - $unparsed);
  for ($str) {
    $num *= 1 when /^pt/;
    $num *= 72 when /^in/;
    $num *= 28.346456692913385211 when /^cm/;
    $num *= 2.8346456692913385211 when /^mm/;
    when (/^w/) {
      die("paper size not set") if !defined($width);
      $num *= $width;
    }
    when (/^h/) {
      die("paper size not set") if !defined($width);
      $num *= $height;
    }
    default { usage(1, "bad dimension") };
  }
  return $num;
}

# Get the size of the given paper, or the default paper if no argument given.
sub paper_size {
  my ($paper_name) = @_;
  chomp($paper_name = `paper`) unless defined($paper_name);
  my $dimensions = `paper --unit=pt --size $paper_name 2>/dev/null` or return;
  $dimensions =~ /^([\d.]+) ([\d.]+)/;
  return round($1), round($2); # round dimensions to nearest point
}

sub parsepaper {
  die("Option $_[0] requires an argument") unless $_[1] ne "";
  my ($width, $height) = paper_size($_[1]);
  if (!defined($width)) {
    my ($w, $h) = split /x/, $_[1];
    eval { ($width, $height) = (singledimen($w), singledimen($h)); }
      or die("paper size '$_[1]' unknown");
  }
  return $width, $height;
}


return 1;
