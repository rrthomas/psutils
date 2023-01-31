# PSUtils utility library
# Copyright (c) Reuben Thomas 2016-2020.
# Released under the GPL version 3, or (at your option) any later version.

package PSUtils;

use v5.14;
use strict;
use warnings;

use Fcntl qw(:seek);
use File::Copy;
use File::Temp qw(tempfile);
use POSIX qw(strtod locale_h);

use IPC::Run3 qw(run3);

use base qw(Exporter);
our @EXPORT = qw(Warn Die singledimen paper_size parsepaper comment parse_file
                 setup_input_and_output extn filename);


sub Warn {
  my ($msg) = @_;
  say STDERR "$main::program_name: $msg";
}

sub Die {
  my ($msg, $code) = @_;
  Warn($msg);
  exit($code || 1);
}

# Argument parsers
sub singledimen {
  my ($str, $width, $height) = @_;
  my $old_locale = setlocale(LC_ALL);
  setlocale(LC_ALL, "C");
  my ($num, $unparsed) = strtod($str);
  $str = substr($str, length($str) - $unparsed);
  for ($str) {
    if (/^pt/) { $num *= 1; }
    elsif (/^in/) { $num *= 72; }
    elsif (/^cm/) { $num *= 28.346456692913385211; }
    elsif (/^mm/) { $num *= 2.8346456692913385211; }
    elsif (/^w/) {
      Die("paper size not set") if !defined($width);
      $num *= $width;
    }
    elsif (/^h/) {
      Die("paper size not set") if !defined($height);
      $num *= $height;
    }
    else { Die("bad dimension `$str'") if $str ne ""; };
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
  Die("could not run `paper' command") if $? == -1;
  if ($? == 0) {
    chomp $out;
    return $out;
  }
}

sub paper_size {
  my ($paper_name) = @_;
  $paper_name = paper([]) unless defined($paper_name);
  my $dimensions = paper(["--unit=pt", "$paper_name"], 1) or return;
  $dimensions =~ / ([.0-9]+)x([.0-9]+) pt$/;
  my $old_locale = setlocale(LC_ALL);
  setlocale(LC_ALL, "");
  my ($w, $w_unparsed) = strtod($1);
  my ($h, $h_unparsed) = strtod($2);
  setlocale(LC_ALL, $old_locale);
  return int($w + 0.5), int($h + 0.5); # round dimensions to nearest point
}

sub parsepaper {
  my ($width, $height) = paper_size($_[0]);
  if (!defined($width)) {
    my ($w, $h) = split /x/, $_[0];
    if (defined($w) && defined($h)) {
      eval { ($width, $height) = (singledimen($w), singledimen($h)); }
        or Die("paper size '$_[0]' unknown");
    }
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
  my ($record, $next_record);
  for ($record = 0; my $buffer = <$infile>; $record = $next_record) {
    $next_record = tell $infile;
    if ($buffer =~ /^%%/) {
      my ($keyword, $value) = comment($buffer);
      if (defined($keyword)) {
        if ($nesting == 0 && $keyword eq "Page:") {
          push @{$psinfo->{pageptr}}, $record;
        } elsif ($psinfo->{headerpos} == 0 && $explicit_output_paper &&
                   ($keyword eq "BoundingBox:" ||
                    $keyword eq "HiResBoundingBox:" ||
                    $keyword eq "DocumentPaperSizes:" ||
                    $keyword eq "DocumentMedia:")) {
          # FIXME: read input paper size (from DocumentMedia comment?) if not
          # set on command line.
          push @{$psinfo->{sizeheaders}}, $record;
        } elsif ($psinfo->{headerpos} == 0 && $keyword eq "Pages:") {
          $psinfo->{pagescmt} = $record;
        } elsif ($psinfo->{headerpos} == 0 && $keyword eq "EndComments") {
          $psinfo->{headerpos} = $next_record;
        } elsif ($keyword eq "BeginDocument:" ||
                   $keyword eq "BeginBinary:" ||
                   $keyword eq "BeginFile:") {
          $nesting++;
        } elsif ($keyword eq "EndDocument" ||
                   $keyword eq "EndBinary" ||
                   $keyword eq "EndFile") {
          $nesting--;
        } elsif ($nesting == 0 && $keyword eq "EndSetup") {
          $psinfo->{endsetup} = $record;
        } elsif ($nesting == 0 && $keyword eq "BeginProlog") {
          $psinfo->{headerpos} = $next_record;
        } elsif ($nesting == 0 && $buffer eq "%%BeginProcSet: PStoPS") {
          $psinfo->{beginprocset} = $record;
        } elsif ($psinfo->{beginprocset} && !$psinfo->{endprocset} && $keyword eq "EndProcSet") {
          $psinfo->{endprocset} = $next_record;
        } elsif ($nesting == 0 && ($keyword eq "Trailer" || $keyword eq "EOF")) {
          last;
        }
      }
    } elsif ($psinfo->{headerpos} == 0) {
      $psinfo->{headerpos} = $record;
    }
  }
  push @{$psinfo->{pageptr}}, $record;
  $psinfo->{pages} = $#{$psinfo->{pageptr}};
  $psinfo->{endsetup} = ${$psinfo->{pageptr}}[0]
    if $psinfo->{endsetup} == 0 || $psinfo->{endsetup} > ${$psinfo->{pageptr}}[0];

  return $psinfo;
}

# Return comment keyword and value if $line is a DSC comment
sub comment {
  my ($line) = @_;
  $line =~ /^%%(\S+)\s+?(.*\S?)\s*$/;
  return ($1, $2);
}

# Set up input and output files
sub setup_input_and_output {
  my ($seekable) = @_;
  $seekable = 0 if !defined($seekable);

  my $infile = \*STDIN;
  my $outfile = \*STDOUT;

  if ($#ARGV >= 0) {            # User specified an input file
    my $file = shift @ARGV;
    open($infile, $file) or Die("cannot open input file $file");
  }
  binmode($infile) or Die("could not set input to binary mode");
  $infile = seekable($infile) or Die("cannot make input seekable")
    if $seekable;

  if ($#ARGV >= 0) {            # User specified an output file
    my $file = shift @ARGV;
    open($outfile, ">", $file) or Die("cannot open output file $file");
  }
  binmode($outfile) or Die("could not set output to binary mode");

  return $infile, $outfile;
}

# Make a file seekable, using temporary files if necessary
sub seekable {
  my ($fp) = @_;

  # If fp is seekable, we're OK
  return $fp if seek $fp, 0, SEEK_CUR;

  # Otherwise, copy fp to a temporary file
  my $ft = tempfile() or return;
  copy($fp, $ft) or return;

  # Reopen the input stream from the temporary, and rewind it
  open($fp, "<&=", $ft);
  return $fp if seek $fp, 0, SEEK_SET;
}

# Resource extensions
sub extn {
  my %exts = ("font" => ".pfa", "file" => ".ps", "procset" => ".ps",
              "pattern" => ".pat", "form" => ".frm", "encoding" => ".enc");
  return $exts{$_[0]};
}

# Resource filename
sub filename {			# make filename for resource in @_
  my $name;
  foreach (@_) {		# sanitise name
    s/[!()\$\#*&\\\|\`\'\"\~\{\}\[\]\<\>\?]//g;
    $name .= $_;
  }
  $name =~ s@.*/@@;		# drop directories
  Die("filename not found for resource " . join(" ", @_), 2)
    if $name =~ /^$/;
  return $name;
}


return 1;
