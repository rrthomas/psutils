# PSUtils utility library

package PSUtils;

use v5.14;
use strict;
use warnings;
no if $] >= 5.018, warnings => "experimental::smartmatch";

use Fcntl qw(:seek);
use POSIX qw(strtod locale_h);

use IPC::Run3 qw(run3);

use base qw(Exporter);
our @EXPORT = qw(singledimen paper_size parsepaper iscomment parse_file
                 setup_input_and_output extn type filename);


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
      die("paper size not set\n") if !defined($width);
      $num *= $width;
    }
    when (/^h/) {
      die("paper size not set\n") if !defined($width);
      $num *= $height;
    }
    default { die("bad dimension\n") if $str ne ""; };
  }
  setlocale(LC_ALL, $old_locale);
  return $num;
}

# Get the size of the given paper, or the default paper if no argument given.
sub paper {
  my ($cmd, $silent) = @_;
  unshift @{$cmd}, "paper";
  my $out;
  run3 $cmd, undef, \$out, $silent ? \undef : undef, {return_if_system_error=>1};
  die("could not run `paper' command\n") if $? == -1;
  if ($? == 0) {
    chomp $out;
    return $out;
  }
}

sub paper_size {
  my ($paper_name) = @_;
  chomp($paper_name = paper([])) unless defined($paper_name);
  my $dimensions = paper(["--unit=pt", "--size", "$paper_name"], 1) or return;
  $dimensions =~ /^([\d.]+) ([\d.]+)/;
  return int($1 + 0.5), int($2 + 0.5); # round dimensions to nearest point
}

sub parsepaper {
  my ($width, $height) = paper_size($_[0]);
  if (!defined($width)) {
    my ($w, $h) = split /x/, $_[0];
    eval { ($width, $height) = (singledimen($w), singledimen($h)); }
      or die("paper size '$_[0]' unknown\n");
  }
  return $width, $height;
}

# Build array of pointers to start/end of pages
sub parse_file {
  my ($infile, $explicit_output_paper) = @_;
  my $nesting = 0;
  my $psinfo = {
    headerpos => 0,
    pagescmt => 0,
    endsetup => 0,
    beginprocset => 0,          # start and end of pstops procset
    endprocset => 0,
    pages => undef,
    sizeheaders => [],
    pageptr => [],
  };
  seek $infile, 0, SEEK_SET;
  for (my $record = 0; my $buffer = <$infile>; $record = tell $infile) {
    if ($buffer =~ /^%%/) {
      if ($nesting == 0 && iscomment($buffer, "Page:")) {
        push @{$psinfo->{pageptr}}, $record;
      } elsif ($psinfo->{headerpos} == 0 && $explicit_output_paper &&
                 (iscomment($buffer, "BoundingBox:") ||
                  iscomment($buffer, "HiResBoundingBox:") ||
                  iscomment($buffer, "DocumentPaperSizes:") ||
                  iscomment($buffer, "DocumentMedia:"))) {
        # FIXME: read input paper size (from DocumentMedia comment?) if not
        # set on command line.
        push @{$psinfo->{sizeheaders}}, $record;
      } elsif ($psinfo->{headerpos} == 0 && iscomment($buffer, "Pages:")) {
        $psinfo->{pagescmt} = $record;
      } elsif ($psinfo->{headerpos} == 0 && iscomment($buffer, "EndComments")) {
        $psinfo->{headerpos} = tell $infile;
      } elsif (iscomment($buffer, "BeginDocument") ||
                 iscomment($buffer, "BeginBinary") ||
                 iscomment($buffer, "BeginFile")) {
        $nesting++;
      } elsif (iscomment($buffer, "EndDocument") ||
                 iscomment($buffer, "EndBinary") ||
                 iscomment($buffer, "EndFile")) {
        $nesting--;
      } elsif ($nesting == 0 && iscomment($buffer, "EndSetup")) {
        $psinfo->{endsetup} = $record;
      } elsif ($nesting == 0 && iscomment($buffer, "BeginProlog")) {
        $psinfo->{headerpos} = tell $infile;
      } elsif ($nesting == 0 && iscomment($buffer, "BeginProcSet: PStoPS")) {
        $psinfo->{beginprocset} = $record;
      } elsif ($psinfo->{beginprocset} && !$psinfo->{endprocset} && iscomment($buffer, "EndProcSet")) {
        $psinfo->{endprocset} = tell $infile;
      } elsif ($nesting == 0 && (iscomment($buffer, "Trailer") ||
                                   iscomment($buffer, "EOF"))) {
        seek $infile, $record, SEEK_SET;
        last;
      }
    } elsif ($psinfo->{headerpos} == 0) {
      $psinfo->{headerpos} = $record;
    }
  }
  push @{$psinfo->{pageptr}}, tell $infile;
  $psinfo->{pages} = $#{$psinfo->{pageptr}};
  $psinfo->{endsetup} = ${$psinfo->{pageptr}}[0]
    if $psinfo->{endsetup} == 0 || $psinfo->{endsetup} > ${$psinfo->{pageptr}}[0];

  return $psinfo;
}

# Return true if $x is a DSC comment starting with $y
sub iscomment {
  my ($x, $y) = @_;
  return substr($x, 2, length($y)) eq $y;
}

# Set up input and output files
sub setup_input_and_output {
  my $infile = \*STDIN;
  my $outfile = \*STDOUT;

  if ($#ARGV >= 0) {            # User specified an input file
    my $file = shift @ARGV;
    open($infile, $file) or die("cannot open input file $file\n");
    binmode($infile) or die("could not set input to binary mode\n");
  }

  if ($#ARGV >= 0) {            # User specified an output file
    my $file = shift @ARGV;
    open($outfile, $file) or die("cannot open output file $file\n");
    binmode($outfile) or die("could not set output to binary mode\n");
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
  die("filename not found for resource " . join(" ", @_) . "\n")
    if $name =~ /^$/;
  return $name;
}


return 1;
