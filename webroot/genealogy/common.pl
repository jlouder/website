#!/usr/bin/perl5.6.1 -w
# $Id$
# ick! but he.net must use perl 5.6.1, because /usr/bin/perl is ancient

# where the libraries are installed at he.net
use lib '/home/jlouder/perl/lib.6/site-perl';

use strict;
use Gedcom;
use Date::Manip;
use CGI qw(:standard);
use CGI::Carp 'fatalsToBrowser';
use FindBin;
use Time::localtime;

#### BEGIN CONFIGURATION
##
                                                                                                                                         
# the gedcom data file
$main::dataFile = "$FindBin::Bin/data.gedcom";
                                                                                                                                         
# dimensions of the 'people' boxes
my $width = 120;
my $height = 60;
                                                                                                                                         
# the URL of the directory containing images (relative to the script URL)
# if present, must end in trailing slash!
my $imageUrl = '';
 
##
#### END CONFIGURATION

# Date::Manip acts funny if I don't call this
Date_Init();

# subroutine prototypes
sub StartHTML($);
sub EndHTML();
sub ErrorPage($);
sub NumSiblings($);
sub NumChildren($);
sub CurrentSpouse($);
sub Name($);
sub NameWithLastFirst($);
sub PersonCell;
sub ConnectorCell($);
sub PreviousMarriageCell;
sub PrintTable;
sub IsAlive($);
sub YearsLived($);
sub PersonSelectorPage($);
sub FamiliesSorted($);

# SUBROUTINE:  StartHTML($title)
# RETURNS:     The beginnings of an HTML page, with $title as the title.
sub StartHTML($) {
  my $title = $_[0];

  return <<"__EOF__";
<html>
<head>
<title>$title</title>
<style type="text/css">
<!--
body {
  background: #5d5d54;
  font-family: Arial, Helvetica, sans serif;
  font-size: 10pt;
  color: #ffffcc;
}
 
td {
  font-size: 9pt;
}

h1, h2, h3 {
  margin-top: 0;
  margin-bottom: 0;
}

a:link
{
  color: #ffffcc;
  font-weight: bold;
}
 
a:visited
{
  color: #ffffcc;
  font-weight: bold;
}

.personouter {
  background-color: #a0a0a0;
}

.personhighlight {
  background-color: #c02000;
}

.personinner {
  background-color: #273c53;
  font-size: 9pt;
}

a.personinner:link, a.personinner:visited {
  font-weight: normal;
  text-decoration: none;
}
-->
</style>
</head>
 
<body>
__EOF__
}

# SUBROUTINE:  EndHTML()
# RETURNS:     The end of an HTML page
sub EndHTML() {
  return "</body>\n</html>\n";
}

# SUBROUTINE:  ErrorPage($error_message)
# DESCRIPTION: Prints a pretty error page with $error_message and exits.
sub ErrorPage($) {
  my $error_message = $_[0];

  print header(), StartHTML('Error'), h1('Error'), $error_message, EndHTML();
 
  exit;
}

# SUBROUTINE:  NumSiblings($individual)
# RETURNS:     The number of siblings that $individual has.
sub NumSiblings($) {
  my $individual = $_[0];

  my @siblings = $individual->siblings();
  return $#siblings + 1;
}

# SUBROUTINE:  NumChildren($individual)
# RETURNS:     The number of children that $individual has.
sub NumChildren($) {
  my $individual = $_[0];
                                                                                
  my @children = $individual->children();
  return $#children + 1;
}

# SUBROUTINE:  CurrentSpouse($individual)
# RETURNS:     The current spouse of $individual, or undef if none.
sub CurrentSpouse($) {
  my $individual = $_[0];

  # FIXME: this should check to ensure they're still married
  # FIXME: It would be more useful to have a CurrentMarriage function
  return $individual->spouse();
}

# SUBROUTINE:  Name($individual)
# RETURNS:     The properly cased name of $individual.
sub Name($) {
  my $individual = $_[0];
 
  my $name = $individual->name();
  $name =~ s:/::g;
  if( defined($individual->get_value('name nick')) ) {
    $name .= ' (' . $individual->get_value('name nick') . ')';
  }
 
  return $name;
}

# SUBROUTINE:  NameWithLastFirst($individual)
# RETURNS:     Similar to Name(), but with "Lastname, First Middle"
sub NameWithLastFirst($) {
  my $individual = $_[0];

  my $name = $individual->name();
  my $newname = $name;

  # the last name will be surrounded by '/' characters
  if( $name =~ m:(.*)/(.+)/(.*): ) {
    # reorder the name
    $newname = "$2, $1 $3";
    # remove any extra whitespace
    $newname =~ s/\s+/ /g;
    # remove any trailing whitespace
    $newname =~ s/\s+$//;
  }

  return $newname;
}

# SUBROUTINE:  PersonCell($individual, [ $highlight = 0 ] )
# RETURNS:     The HTML that goes inside a table cell for a person. This
#              person's box is highlighted if $highlight is 1.
sub PersonCell {
  my $individual = $_[0];
  my $highlight = $_[1];
  if( !defined($highlight) ) {
    $highlight = 0;
  }

  my $class = $highlight ? 'personhighlight' : 'personouter';

  # the start of the person cell
  my $html = "<table width=\"$width\" border=\"0\" cellspacing=\"0\" " .
             "cellpadding=\"1\" class=\"$class\"><tr><td>" .
             '<table width="100%" border="0" cellspacing="0" ' .
             'cellpadding="5" class="personinner"><tr>' .
             "<td height=\"$height\" class=\"personinner\">";

  if( !defined($individual) ) {
    $html .= '(unknown person)';
  } else {
    # the person's name should be a link to their detail page
    $html .= '<a class="personinner" href="detail.cgi?id=' .
             $individual->{xref} . '">' . Name($individual) . '</a>';

    $html .= '<br><a href="' . CGI::script_name() . '?id=' .
             $individual->{xref} . '"><img alt="recenter tree here" ' .
             'border="0" ' . "src=\"${imageUrl}tree.gif\"></a>";

    if( !IsAlive($individual) ) {
      $html .= '&nbsp;(' . YearsLived($individual) . ')';
    }

  }

  # the end of the person cell
  $html .= '</td></tr></table></td></tr></table>';

  return $html;
}

# SUBROUTINE:  ConnectorCell($connectorNumber)
# RETURNS:     The HTML for a connector of the specified number. The connector
#              numbers aren't described here.
sub ConnectorCell($) {
  my $connectorNumber = $_[0];

  return "<img src=\"${imageUrl}c${connectorNumber}.gif\">";
}

# SUBROUTINE:  PreviousMarriageCell($individual, @prevFamilies)
# RETURNS:     The HTML for a cell with information about previous marriages
#              with links to those families;
sub PreviousMarriageCell {
  my $individual = shift;
  my @prevFamilies = @_;

  my $html = "<table width=\"$width\" cellpadding=\"3\" cellspacing=\"0\">" .
             "<tr><td height=\"$height\">Other marriages:<br>";
  foreach my $fam ( @prevFamilies ) {
    my $spouse = $individual->sex() eq 'M' ? $fam->wife() : $fam->husband();
    $html .= "<a href=\"" . CGI::script_name() . "?id=" .
             $individual->{xref} . "&fam=" . $fam->{xref} . "\">" .
             Name($spouse) . "</a><br>";
  }
  $html .= "</td></table>";

  return $html;
}


# SUBROUTINE:  PrintTable(@table)
# DESCRIPTION: Prints the tree as an HTML table, using @table
sub PrintTable {
  my @table = @_;

  # find max width
  my $lastcol = -1;
  foreach my $i ( 0 .. $#table ) {
    if( $#{$table[$i]} > $lastcol ) {
      $lastcol = $#{$table[$i]};
    }
  }

  print "<table border='0' cellpadding='0' cellspacing='0'>\n";
  foreach my $i ( 0 .. $#table ) {
    print "  <tr>\n";
    foreach my $j ( 0 .. $lastcol ) {
      print "    <td align='center' valign='center'>";
      if( defined($table[$i][$j]) ) {
        print $table[$i][$j];
      } else {
        print "&nbsp;";
      }
      print "</td>\n";
    }
    print "  </tr>\n";
  }

  print "</table>\n";
}

# SUBROUTINE:  IsAlive($individual)
# RETURNS:     1 if $individual is currently living, 0 otherwise
sub IsAlive($) {
  my $individual = $_[0];

  return !defined($individual->get_record('death'));
}

# SUBROUTINE:  YearsLived($individual)
# RETURNS:     The years $individual lived, as a string like "1909 - 1975".
#              For individuals still living, there is no second year.
sub YearsLived($) {
  my $individual = $_[0];

  my $birth_date = $individual->get_value('birth date');
  my $death_date = $individual->get_value('death date');

  my $birth_year = '?';
  my $death_year = IsAlive($individual) ? '' : '?';

  if( defined($birth_date) ) {
    $birth_year = UnixDate($birth_date, "%Y");
  }
  if( defined($death_date) ) {
    $death_year = UnixDate($death_date, "%Y");
  }

  return $birth_year . ' - ' . $death_year;
}

# SUBROUTINE:  PersonSelectorPage($ged)
# DESCRIPTION: Prints a page listing all the individuals, and exits.
# ARGUMENTS:   $ged is a Gedcom object
sub PersonSelectorPage($) {
  my $ged = $_[0];

  # sort people based on last,first name
  my @individuals = sort { NameWithLastFirst($a) cmp NameWithLastFirst($b) }
                      $ged->individuals();
  my $count = $#individuals + 1;

  print header(), StartHTML('Select a person'),
        "<p>Select a person to be the center of the tree. This person's ",
        "children, siblings, parents, and grandparents will be shown.</p>",
        "<p>There are $count people in the tree.</p>",
        "\n<ul>\n";

  foreach my $ind ( @individuals ) {
    print "<li><a href=\"", CGI::script_name(), '?id=', $ind->{xref}, "\">",
          NameWithLastFirst($ind), "</a>";

    if( !IsAlive($ind) ) {
      print " (", YearsLived($ind), ")";
    }

    print "</li>\n";
  }

  print "</ul>\n", EndHTML();

  exit;
}

# SUBROUTINE:  FamiliesSorted($individual)
# RETURNS:     A list of $individual's Gedcom::Family objects in which he
#              appears as a spouse, sorted by date.
sub FamiliesSorted($) {
  my $individual = $_[0];
 
  my @families = $individual->fams();
 
  # no marriages? easy!
  if( ! @families ) {
    # $individual was never married
    return undef;
  }
 
  # just one marriage? easy!
  if( @families == 1 ) {
    return $families[0];
  }
 
  # multiple marriages
  # build a hash whose key is the marriage and value is the date it ended
  # (undef for date means it never ended)
  my %ended;
  foreach my $fam ( @families ) {
    # get the spouse -- husband or wife depending on sex of $individual
    my $spouse = $individual->sex() eq 'M' ? $fam->wife() : $fam->husband();
 
    # was there a divorce?
    if( $fam->get_record('divorce') ) {
      # put divorce date into %ended
      $ended{$fam} = $fam->get_value('divorce date');
      # if we don't have a divorce date, make one up (use current date)
      if( !defined($ended{$fam}) ) {
        $ended{$fam} = ctime();
      }
                                                                                                                                                             
      # skip to the next marriage
      next;
    }
                                                                                                                                                             
    # did the spouse die before $individual?
    my $spouseDeath = $spouse->get_value('death date');
    my $indDeath = $individual->get_value('death date');
    if( defined($spouseDeath) ) {
      # if $individual is still alive, marriage ended at $spouseDeath
      if( IsAlive($individual) ) {
        $ended{$fam} = $spouseDeath;
        next;
      }
 
      # must have a date for $individual's death, or not enough info to decide
      if( defined($indDeath) ) {
        if( Date_Cmp($spouseDeath, $indDeath) == -1 ) {
          # spouse died before $individual; marriaged ended at $spouseDeath
          $ended{$fam} = $spouseDeath;
          next;
        }
      }
    }
 
    # marriage never ended, use a future date for the "end"
    $ended{$fam} = 'December 31, 9999';
  }
 
  # sort by date marriage ended
  return sort { Date_Cmp($ended{$a}, $ended{$b}) } @families;
}

# to make 'require' happy
return 1;
