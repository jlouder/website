#!/usr/bin/perl5.6.1 -w
# $Id$
# ick! but he.net must use perl 5.6.1, because /usr/bin/perl is ancient

# where the libraries are installed at he.net
use lib '/home/jlouder/perl/lib.6/site-perl';

# common functions and configuration
require 'common.pl';

use Gedcom;
use Date::Manip;

# prototypes
sub TableRow($$);
sub DateAndPlace($$);
sub LinkToPerson($);

# SUBROUTINE:  TableRow($label, $data)
# DESCRIPTION: Prints a row in the table if $data is not undef
sub TableRow($$) {
  my ($label, $data) = @_;

  if( !defined($data) ) {
    return;
  }

  print "<tr><td><b>$label</b></td>\n",
        "<td>$data</td></tr>\n";
}

# SUBROUTINE:  DateAndPlace($individual, $event_name)
# DESCRIPTION: Returns a string with the date and place for $event_name.
sub DateAndPlace($$) {
  my ($individual, $event_name) = @_;

  my $string = $individual->get_value($event_name . ' date');
  if( defined($individual->get_value($event_name . ' place')) ) {
    if( defined($string) ) {
      $string .= ' in ';
    }
    $string .= $individual->get_value($event_name . ' place');
  }

  return $string;
}

# SUBROUTINE:  LinkToPerson($individual)
# DESCRIPTION: Returns the HTML for a link to $individual's detail page. The
#              text is the person's name.
sub LinkToPerson($) {
  my $individual = $_[0];

  return '<a href="' . CGI::script_name() . '?id=' . $individual->{xref} .
         '">' . Name($individual) . '</a>';
}


# load the data file
my $ged = Gedcom->new(gedcom_file => $dataFile);

my $q = new CGI;

# find the individual whose details should be shown
my $id = $q->param('id');
if( !defined($id) ) {
  PersonSelectorPage($ged);
}
my $ind = $ged->get_individual($id);
if( !defined($ind) ) {
  ErrorPage("Person $id not found");
}

# calling the Gedcom functions can be expensive, so save the values of
# some often-needed functions
my @families = FamiliesSorted($ind);

print header(), StartHTML(Name($ind)),
      "<div align=\"center\"><h1>", Name($ind), "</h1>\n",
      "<br /><a href=\"tree.cgi?id=" . $ind->{xref} . "\">See family ",
      "tree for this person</a><br /><br /></div>\n";

print "<p><table border=\"1\" cellpadding=\"3\">\n";

# can't use DateAndPlace for birth date/place because
# we need to hide birth dates of people still alive
my $bday_place;
if( IsAlive($ind) ) {
  $bday_place = '(birth date hidden)';
} else {
  $bday_place = $ind->get_value('birth date');
}
if( defined($ind->get_value('birth place')) ) {
  if( defined($bday_place) ) {
    $bday_place .= ' in ';
  }
  $bday_place .= $ind->get_value('birth place');
}
TableRow("Born", $bday_place);
TableRow("Died", DateAndPlace($ind, 'death'));
TableRow("Buried", DateAndPlace($ind, 'burial'));
TableRow("Baptised", DateAndPlace($ind, 'baptism'));
TableRow("Occupation", $ind->get_value('occupation'));

# print all the notes about this person
foreach my $note ( $ind->get_value('note') ) {
  TableRow("Note", $note);
}

# start a new table for parents/siblings/children
print "</table></p>\n",
      "<p><table border=\"1\" cellpadding=\"3\">\n";

# print the parents
TableRow("Parents", (defined($ind->father()) ? LinkToPerson($ind->father())
                                             : "(father unknown)") . ' and ' .
                    (defined($ind->mother()) ? LinkToPerson($ind->mother())
                                             : "(mother unknown)"));

# print the siblings
my @siblings = $ind->siblings();
if( @siblings ) {
  my @siblingLinks;
  foreach my $sibling ( @siblings ) {
    push @siblingLinks, LinkToPerson($sibling);
  }
  TableRow(@siblings > 1 ? 'Siblings' : 'Sibling',
           join(', ', @siblingLinks));
}

# print each marriage, starting with the oldest
foreach my $family ( @families ) {
  next unless defined($family);

  # print the spouse name, (optional) marriage date/location
  my $marriage = LinkToPerson( $ind->sex() eq 'M' ? $family->wife()
                                                  : $family->husband() );

  # add on the marriage date, if there is one
  if( defined($family->get_value('marriage date')) ) {
    if( defined($marriage) ) {
      $marriage .= ' ';
    }
    $marriage .= $family->get_value('marriage date');
  }

  # add on the marriage place, if there is one
  if( defined($family->get_value('marriage place')) ) {
    if( defined($marriage) ) {
      $marriage .= ' in ';
    }
    $marriage .= $family->get_value('marriage place');
  }

  TableRow("Married", $marriage);

  # print any children from this marriage
  my @childrenLinks;
  foreach my $child ( $family->children() ) {
    push @childrenLinks, LinkToPerson($child);
  }
  if( @childrenLinks ) {
    TableRow(@childrenLinks > 1 ? 'Children' : 'Child',
             join(', ', @childrenLinks));
  }
}

print "</table></p>\n";

print '<br /><br /><div align="center"><a href="index.html">Back to the ',
      'Loudermilk Genealogy page</a></div>',
      EndHTML();
