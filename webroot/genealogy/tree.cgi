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
my $dataFile = "$FindBin::Bin/data.gedcom";

# dimensions of the 'people' boxes
my $width = 120;
my $height = 60;

# the URL of the directory containing images (relative to the script URL)
# if present, must end in trailing slash!
my $imageUrl = '';

##
#### END CONFIGURATION

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
    $html .= Name($individual);

    $html .= '<br><a href="' . $ENV{'SCRIPT_URI'} . '?id=' .
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
    $html .= "<a href=\"" . $ENV{'SCRIPT_URI'} . "?id=" .
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

  print header(), StartHTML('Select a person'),
        "<p>Select a person to be the center of the tree. This person's ",
        "children, siblings, parents, and grandparents will be shown.</p>",
        "\n<ul>\n";

  foreach my $ind ( @individuals ) {
    print "<li><a href=\"", $ENV{'SCRIPT_URI'}, '?id=', $ind->{xref}, "\">",
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



# main()

# Date::Manip acts funny if I don't call this
Date_Init();

# load the data file
my $ged = Gedcom->new(gedcom_file => $dataFile);
if( ! $ged->validate() ) {
  ErrorPage("Data file $dataFile failed validation");
}

my $q = new CGI;

# find the individual whose tree should be drawn
my $id = $q->param('id');
if( !defined($id) ) {
  PersonSelectorPage($ged);
}
my $ind = $ged->get_individual($id);
if( !defined($ind) ) {
  ErrorPage("Person $id not found");
}

# build the table (list of lists) for this individual
my @table;

# calling the Gedcom functions can be expensive, so save the values of
# some often-needed functions
my $numSiblings = NumSiblings($ind);
my @prevFamilies = FamiliesSorted($ind);
my $currentFamily;
if( defined(my $famid = $q->param('fam')) ) {
  # user asked for a specific family
  $currentFamily = $ged->get_family($famid);
  if( !defined($currentFamily) ) {
    ErrorPage("Family $famid not found");
  }
  # remove current family from @prevFamilies, so it's a list of other marriages
  my @otherFamilies;
  foreach my $fam ( @prevFamilies ) {
    if( $fam != $currentFamily ) {
      push @otherFamilies, $fam;
    }
  }
  @prevFamilies = @otherFamilies;
} else {
  # current family is most recent one
  $currentFamily = pop @prevFamilies;
}
my $currentSpouse;
my $numChildren = 0;
my @children;
if( defined($currentFamily) ) {
  $currentSpouse = $ind->sex() eq 'M' ? $currentFamily->wife()
                                        : $currentFamily->husband();
  @children = $currentFamily->children();
  $numChildren = $#children + 1;
}
print "DEBUG: calculated numChildren=$numChildren\n";

# calculate indent of first two rows (grandparents, parents)
my $indent_from_peer_row = $numSiblings - 3 +
                           (defined($currentSpouse) * 2);
my $indent_from_children_row = $numChildren - 2;
my $indent = $indent_from_peer_row;
if( $indent_from_children_row > 0 ) {
  $indent += $indent_from_children_row;
}

# build grandparents row
my @row0;
# fill indent cells with nothing
foreach my $count ( 1 .. $indent ) {
  push @row0, undef;
}
my $mother = $ind->mother();
my $father = $ind->father();
# paternal grandfather
if( defined($father) ) {
  push @row0, PersonCell($father->father());
} else {
  push @row0, PersonCell(undef);
}
push @row0, undef;	# blank cell
# paternal grandmother
if( defined($father) ) {
  push @row0, PersonCell($father->mother());
} else {
  push @row0, PersonCell(undef);
}
push @row0, undef;	# blank cell
# maternal grandfather
if( defined($mother) ) {
  push @row0, PersonCell($mother->father());
} else {
  push @row0, PersonCell(undef);
}
push @row0, undef;	# blank cell
# maternal grandmother
if( defined($mother) ) {
  push @row0, PersonCell($mother->mother());
} else {
  push @row0, PersonCell(undef);
}
# done with grandparents row
push @table, [ @row0 ];

# connector rows below grandparents
my @row1;
# fill indent cells with nothing
foreach my $count ( 1 .. $indent ) {
  push @row1, undef;
}
push @row1, ConnectorCell(1);
push @row1, ConnectorCell(4);
push @row1, ConnectorCell(2);
push @row1, undef;	# blank cell
push @row1, ConnectorCell(1);
push @row1, ConnectorCell(4);
push @row1, ConnectorCell(2);
push @table, [ @row1 ];

my @row2;
# fill indent cells with nothing
foreach my $count ( 1 .. $indent ) {
  push @row2, undef;
}
push @row2, undef;	# blank cell
push @row2, ConnectorCell(3);
push @row2, undef;	# blank cell
push @row2, undef;	# blank cell
push @row2, undef;	# blank cell
push @row2, ConnectorCell(3);
push @table, [ @row2 ];

# build parents row
my @row3;
# fill indent cells with nothing
foreach my $count ( 1 .. $indent ) {
  push @row3, undef;
}
push @row3, undef;	# blank cell
push @row3, PersonCell($father);
push @row3, undef;	# blank cell
push @row3, undef;	# blank cell
push @row3, undef;	# blank cell
push @row3, PersonCell($mother);
# done with parents row
push @table, [ @row3 ];

# first connector row below parents
# the second is built along with the peer row
my @row4;
# fill indent cells with nothing
foreach my $count ( 1 .. $indent ) {
  push @row4, undef;
}
push @row4, undef;	# blank cell;
push @row4, ConnectorCell(1);
push @row4, ConnectorCell(4);
push @row4, ConnectorCell(4);
push @row4, ConnectorCell(4);
push @row4, ConnectorCell(2);
push @table, [ @row4 ];

# build peers row, the connector row above it, and the row below it
my @row5;
my @row6;
my @row7;
# fill indent cells with nothing
if( $numChildren > 0 ) {
  if( $numChildren == 1 && $numSiblings == 0 ) {
    # the dreaded special case; can't figure out a formula that handles this
    $indent = 1;
  } else {
    $indent = $indent_from_children_row;
  }
} else {
  $indent = $indent_from_peer_row * -1;
}
if( $indent < 0 ) {
  $indent = 0;
}
foreach my $count ( 1 .. $indent ) {
  push @row5, undef;
  push @row6, undef;
  push @row7, undef;
}
# spouse, if present
if( defined($currentSpouse) ) {
  # no connectors above spouse
  push @row5, undef;	# blank cell
  push @row5, undef;	# blank cell

  push @row6, PersonCell($currentSpouse);
  # between the spouse and individual, print a note if there are previous
  # marriages
  if( @prevFamilies ) {
    push @row6, PreviousMarriageCell($ind, @prevFamilies);
  } else {
    push @row6, undef;	# blank cell
  }

  push @row7, ConnectorCell(1);
  push @row7, ConnectorCell(4);
  push @row7, ConnectorCell(2);
}
# the individual
my @siblings = $ind->siblings();
push @row5, @siblings ? ConnectorCell(6) : ConnectorCell(3);
push @row6, PersonCell($ind, 1);
# blank cell to the right of them if they have siblings
if( @siblings ) {
  push @row5, ConnectorCell(7);
  push @row6, undef;	# blank cell
}

# siblings
foreach my $sibling ( @siblings ) {
  push @row5, ConnectorCell(9);
  push @row5, ConnectorCell(7);

  push @row6, PersonCell($sibling);
  push @row6, undef;	# blank cell
}

# if there were siblings, fix up some of the connectors
if( @siblings ) {
  # fix connector above last sibling, and trailing connector
  $row5[$#row5] = undef;	# remove trailing connector
  $row5[$#row5 - 1] = ConnectorCell(5);

  # fix middle connector coming down from parents
  my $parentConnectorOffset = $indent;
  if( $parentConnectorOffset < 0 ) {
    $parentConnectorOffset = 0;
  }
  if( defined($currentSpouse) ) {
    $parentConnectorOffset += 2;
  }
  $parentConnectorOffset += @siblings;
  if( defined($row6[$parentConnectorOffset]) ) {
    $row5[$parentConnectorOffset] = ConnectorCell(8);
  } else {
    $row5[$parentConnectorOffset] = ConnectorCell(10);
  }
}

# done with peers row
push @table, [ @row5 ];
push @table, [ @row6 ];
# nothing below row 6 unless person is married
if( defined($currentSpouse) ) {
  push @table, [ @row7 ];
}

# build children row, and the connector row above it
my @row8;
my @row9;
# fill indent cells with nothing
#$indent = $indent_from_children_row * -1 + $indent_from_peer_row * -1;
$indent = 0;
if( $numChildren == 1 && $numSiblings == 0 ) {
  # the special case
  $indent = 2;
} elsif( $indent_from_children_row * -1 > 0 ) {
  $indent = $indent_from_children_row * -1;
}
foreach my $count ( 1 .. $indent ) {
  push @row8, undef;
  push @row9, undef;
}
# the children
# FIXME: This should use CurrentMarriage to only get the right children
foreach my $child ( @children ) {
  push @row8, ConnectorCell(9);
  push @row8, ConnectorCell(7);

  push @row9, PersonCell($child);
  push @row9, undef;	# blank cell
}
# fixup connectors above children
# remove trailing connector
$row8[$#row8] = undef;
# fix middle connector
# fix first/last connector if > 1 child
if( $numChildren == 1 ) {
  $row8[$#row8-1] = ConnectorCell(3);
} else {
  # fix first and last connectors
  $row8[$indent] = ConnectorCell(6);
  $row8[$#row8-1] = ConnectorCell(5);

  # fix middle connector
  my $middle = $indent + $numChildren - 1;
  if( defined($row9[$middle]) ) {
    $row8[$middle] = ConnectorCell(8);
  } else {
    $row8[$middle] = ConnectorCell(10);
  }
}
# done with children row
# only add these rows if there are children
if( $numChildren > 0 ) {
  push @table, [ @row8 ];
  push @table, [ @row9 ];
}

print header(), StartHTML("Family tree for " . Name($ind));
PrintTable(@table);
print EndHTML();
