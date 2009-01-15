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
);

my $remote_host = gethostbyaddr(inet_aton($ENV{'REMOTE_ADDR'}), AF_INET) ||
                  $ENV{'REMOTE_ADDR'};

$q = new CGI;
my $message = $q->param('message');

# make sure the message isn't blank
if( $message =~ /^\S*$/ ) {
  die "Message is blank, not sending.";
}

# send this to my phone or email depending on what time it is
my $email_address;
my $hour = (localtime time)[2];		# 0-23, Eastern time zone
if( $hour < 8 || $hour >= 22 ) {
  $email_address = 'joel@loudermilk.org';
} else {
  $email_address = '4077483615@mobile.mycingular.net';
}

# prepend the web client's name to the message
my $subject = "Web message from: $remote_host";

# If the sender is blacklisted, send the message to /dev/null, but make
# it look like it was sent.
my $sendmail = defined $blacklisted_hosts{$remote_host} ?
  '>/dev/null' : '|/usr/bin/sendmail -t';

# send the message to my pager
open SENDMAIL, $sendmail or die "Can't open $sendmail: $!";
print SENDMAIL << "__EOF__";
To: $email_address
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
