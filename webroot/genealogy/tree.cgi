#!/usr/bin/perl5.6.1 -w
# $Id$
# ick! but he.net must use perl 5.6.1, because /usr/bin/perl is ancient

# where the libraries are installed at he.net
use lib '/home/jlouder/perl/lib.6/site-perl';

# common functions and configuration
require 'common.pl';

use FindBin;
use Gedcom;
use Date::Manip;

# load the data file
my $ged = Gedcom->new(gedcom_file => $dataFile);

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

print header(), StartHTML("Family tree for " . Name($ind)),
      "<div align=\"center\"><h3>Family tree for:</h3>\n",
      "<h1>", Name($ind), "</h1><br />",
      "Click a person's name for details, or click a tree icon to ",
      "recenter the tree on that person.<br /><br /></div>\n";

PrintTable(@table);

print '<br /><br /><div align="center"><a href="index.html">Back to the ',
      'Loudermilk Genealogy page</a></div>',
      EndHTML();
