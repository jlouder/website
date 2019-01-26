#!/usr/bin/perl -w
# $Id$

use CGI;
use CGI::Carp qw(fatalsToBrowser);
use Socket;

$ENV{TZ} = 'US/Eastern';
my $logfile = '/home/jlouder/pager.log';

# hosts we don't want messages from, period
my %blacklisted_hosts = map { $_ => 1 } qw(
  static.162.198.46.78.clients.your-server.de
  static.142.88.46.78.clients.your-server.de
  hosted-by.altushost.com
  91.201.66.76
);

my $remote_host = gethostbyaddr(inet_aton($ENV{'REMOTE_ADDR'}), AF_INET) ||
                  $ENV{'REMOTE_ADDR'};

$q = new CGI;
my $message = $q->param('message');

# make sure the message isn't blank
if( $message =~ /^\S*$/ ) {
  die "Message is blank, not sending.";
}

# 2019-01-26: Looking back through the log, it's been easily 10 years
# since I got a legitimate message through this thing. Quit emailing
# these and just write to the log.
open LOGFILE, ">>$logfile" or die "Can't open logfile \"$logfile\" $!";
my $date = `date`;
chomp $date;
print LOGFILE "$date $remote_host: $message\n";
close LOGFILE;

# success, print a message
print << "__EOF__";
Content-Type:	text/html

<HTML>
<HEAD>
<TITLE>Success!</TITLE>
</HEAD>
<BODY BGCOLOR="#ffffff" TEXT="#000000">
<FONT FACE="Arial, Helvetica" SIZE="2">
Your message was successfully sent.
</FONT></BODY></HTML>
__EOF__
