#!/usr/bin/perl -w

use CGI;
use CGI::Carp qw(fatalsToBrowser);
use Socket;
use Net::SNPP;

my $logfile = '/home/jlouder/pager.log';

my $remote_host = gethostbyaddr(inet_aton($ENV{'REMOTE_ADDR'}), AF_INET) ||
                  $ENV{'REMOTE_ADDR'};

$q = new CGI;
my $message = $q->param('message');

# make sure the message isn't blank
if( $message =~ /^\S*$/ ) {
  die "Message is blank, not sending.";
}

# prepend the web client's name to the message
my $subject = "Web message from: $remote_host";

# send the message to my pager
open SENDMAIL, "|/usr/bin/sendmail -t" or die "Can't run sendmail: $!";
print SENDMAIL << "__EOF__";
To: 4073102323\@messaging.sprintpcs.com
Subject: $subject

$message
__EOF__
close SENDMAIL;

# also write the message to a log
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
