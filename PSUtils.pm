# PSUtils utility library

package PSUtils;

use v5.14;
use strict;
use warnings;
no if $] >= 5.018, warnings => "experimental::smartmatch";

use POSIX qw(strtod locale_h);

use base qw(Exporter);
our @EXPORT = qw(singledimen paper_size parsepaper setup_input_and_output extn type filename);


# Argument parsers
sub singledimen {
  my ($str, $width, $height) = @_;
  my $old_locale = setlocale(LC_ALL);
  setlocale(LC_ALL, "C");
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
    default { die("bad dimension") if $str ne ""; };
  }
  setlocale(LC_ALL, $old_locale);
  return $num;
}

# Get the size of the given paper, or the default paper if no argument given.
sub paper_size {
  my ($paper_name) = @_;
  chomp($paper_name = `paper`) unless defined($paper_name);
  my $dimensions = `paper --unit=pt --size $paper_name 2>/dev/null` or return;
  $dimensions =~ /^([\d.]+) ([\d.]+)/;
  return int($1 + 0.5), int($2 + 0.5); # round dimensions to nearest point
}

sub parsepaper {
  my ($width, $height) = paper_size($_[0]);
  if (!defined($width)) {
    my ($w, $h) = split /x/, $_[0];
    eval { ($width, $height) = (singledimen($w), singledimen($h)); }
      or die("paper size '$_[0]' unknown");
  }
  return $width, $height;
}

# Set up input and output files
sub setup_input_and_output {
  my $infile = \*STDIN;
  my $outfile = \*STDOUT;

  if ($#ARGV >= 0) {            # User specified an input file
    my $file = shift @ARGV;
    open($infile, $file) or die("cannot open input file $file");
    binmode($infile) or die("could not set input to binary mode");
  }

  if ($#ARGV >= 0) {            # User specified an output file
    my $file = shift @ARGV;
    open($outfile, $file) or die("cannot open output file $file");
    binmode($outfile) or die("could not set output to binary mode");
  }

  usage(1) if $#ARGV != -1; # Check no more arguments were given

  return $infile, $outfile;
}

# Resource extensions
sub extn {
  my %exts = ("font" => ".pfa", "file" => ".ps", "procset" => ".ps",
              "pattern" => ".pat", "form" => ".frm", "encoding" => ".enc");
  return $exts{$_[0]};
}

# Resource types
sub type {
  my %types = ("%%BeginFile:" => "file", "%%BeginProcSet:" => "procset",
               "%%BeginFont:" => "font");
  return $types{$_[0]};
}

# Resource filename
sub filename {			# make filename for resource in @_
  my $name;
  foreach (@_) {		# sanitise name
    s/[!()\$\#*&\\\|\`\'\"\~\{\}\[\]\<\>\?]//g;
    $name .= $_;
  }
  $name =~ s@.*/@@;		# drop directories
  die("filename not found for resource ", join(" ", @_), "\n")
    if $name =~ /^$/;
  return $name;
}


return 1;
