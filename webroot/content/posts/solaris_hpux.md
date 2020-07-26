---
title: "Solaris versus HP-UX"
date: 2005-04-09T08:56:48-04:00
draft: false
toc: false
images:
aliases:
  - /software/solaris-hpux.html
tags:
  - untagged
---
## Background

I got my start as a UNIX sysadmin using Solaris back in college, and I've
been a fan of Solaris ever since. Where I work, there is often talk of
Sun versus HP for large UNIX systems, and I am always a proponent of
Sun's systems, mainly because of Solaris.

Many people are quick to dismiss my opinion as a simple personal preference,
thinking that since I'm more familiar with Solaris I'm basing my opinion on
my emotions and not giving HP fair consideration. I have spent a decent
amount of time on HP-UX, though, and I have created the list below to detail
the reasons why I believe that from a system administrator's perspective,
Solaris is a superior operating system to HP-UX.

For the comparison, I chose relatively older but still very popular
versions of both operating systems:
 * Solaris 8 (also known as SunOS 5.8 or Solaris 2.8), released in 2000
 * HP-UX 11iv1 (also known as HP-UX 11.11), released in 2000

To be fair, I have found many features of HP-UX that
I am quite fond of and wish Solaris had. I've pointed those out
[below](#what-hp-ux-gets-right) as
well.

## What HP-UX gets wrong

<span class="x" /> **No shadow passwords by default.** Shadow
passwords are possible, but you have to turn them on after installing
the OS. Not having these is a huge security issue, and HP turns a blind
eye toward it by making the administrator fix the gaping out-of-the-box
security hole.

<span class="x" /> **No process-tracing program by default.** Out
of the box, HP-UX has no equivalent of the Solaris `truss` or
Linux `strace` program to let you trace a process' system calls. One
is available (`tusc`), but it's on a supplemental CD. This is an
essential tool of any operating system, and should be available on every
installation.

<span class="x" /> **No /usr/proc/bin-equivalent tools at all.**
The Solaris /usr/proc/bin utilities are incredibly useful. There's
`pstack` to show you a process' stack (for each thread), `psig`
to see the signal handlers for a process, `ptree` to draw an ASCII
chart of a process' parents and children, and several others. Most of these
aren't tools you need all the time, but when you need them, there is no
substitute. HP-UX has none of these.

<span class="x" /> **Difficult to tell how much physical memory is
installed.** This came as quite a shock to me, but there's no sure-fire,
easy way to quickly see how much memory is installed in an HP-UX system.
The most common answer I see to this question is to run `dmesg` and look
for a particular message that was logged at boot time, but that doesn't work
your system has been up a long time. There's a C interface to get this
information, but no built-in command line utility. I eventually wrote a
simple C program to return the amount of physical memory, but it shouldn't
be that hard.

<span class="x" /> **Difficult to tell if you have a more recent version
of a particular patch installed.** Let's suppose you hear about a
security vulnerability in your OS, and the vendor has already released a
patch. You want to check whether you already have this patch (or a later
version of it) installed on your system, but this is difficult with HP-UX.
With Solaris, the patch you're checking for would be named something like
123456-02. Any later versions of that patch would begin with "123456-" and
increment the last number, so it's easy to see if you have the patch in
question or later (meaning you don't need to worry about the issue the
patch resolved). With HP-UX, the patch you're looking for would be named
something like PHKL_12345, but any later versions of it would have completely
different numbers. There's no way to easily tell if you have a later version
of that patch &mdash; all you can easily tell is if you have the version in question
or not.

<span class="x" /> **Can't use @ or # characters in passwords by
default.** By default, the @ and # characters won't work in passwords
because /bin/login interprets them as kill and erase, respectively. Sure, you
can fix this, but would you ever have expected this? Suppose you're
running a mixed environment, where the HP-UX systems use NIS or LDAP to use
passwords created on another platform. Any users with these characters in
their passwords won't be able to log in. Maybe these terminal settings were
useful twenty years ago when we used our UNIX servers to connect dozens of
80-character terminals, but those days are long gone, and this default is
ridiculous.

<span class="x" /> **Can't tell what a device is from its hardware
path.** Maybe I'm just stupid, but I could stare at the HP-UX hardware
paths for devices all day without realizing that 0/1/1/0.1.0 is a disk and
0/4/1/0 is a network adapter. In Solaris, those would be more like
/devices/pci@1f,4000/scsi@3/sd@0,0:a for the disk and
/devices/pseudo/clone@0:hme for the network adapter. These seem just as
arbitrary at first, but there are clues in the pathnames: "sd" is the driver
for <u>S</u>CSI <u>d</u>isks, and "hme" is the driver for
<u>h</u>undred-<u>m</u>egabit <u>E</u>thernet NICs.

<span class="x" /> **No single command to shut down and power off.**
In Solaris, an `init 5` will shut down and power off, and an `init
0` will shut down and halt. HP-UX gives you only the latter, and if you're
shutting down a system for hardware replacement, your only choice is to
`shutdown -h`, wait for the console message that says it's okay to
power off, and either physically power off then, or log in to the MP/GSP
and issue the poweroff there.

<span class="x" /> **The kernel must be relinked when tunables are
changed.** I thought we were past the days when you needed a compiler
and some source code to make a tuning change to the kernel, but HP-UX isn't.
Where Solaris would just need an edit to /etc/system, HP-UX needs to update
some header files and relink the kernel.

<span class="x" /> **Kernel tunable defaults are not reasonable.**
The HP-UX defaults for lots of tunables look like they haven't been updated
in 15 years. For example, the default for the maximum number of processes any
non-root user can have running (maxuprc) is 75.

<span class="x" /> **Startup scripts belong in /etc, not /sbin.**
Most System V unices place startup scripts in /etc/init.d and /etc/rc?.d,
but HP-UX puts them in /sbin/init.d and /sbin/rc?.d. If it was 20 years ago
and we were having a debate about where the startup scripts should go, I'd
vote for /sbin instead of /etc. But other vendors have been doing things one
way for 20 years, and HP-UX could at least give admins coming from another
flavor of UNIX the courtesy of a symlink. But they don't.

<span class="x" /> **Huge copyright message at every login.** If
you've never logged in to a HP-UX system before, you're missing out &mdash; your
login is greeted by a 28-line list of copyright messages. Every time. Is this
really necessary? Somehow, I doubt Sun is jeopardizing their copyrights to
Solaris by not assaulting their users with these notices dozens of times
each day.

<span class="x" /> **Syslog rotation is inadequate.** HP-UX's idea
of rotating the syslog is to copy syslog.log to OLDsyslog.log when the
system boots. That leaves you with not much logging at all if you boot your
system frequently, or probably too much logging if you rarely boot your
system. Now, Solaris 8 isn't too much better at log rotation, but it rotates
your syslog once a week and keeps four old copies in addition to the current
one, so you always know how much log information you have. With HP-UX, you
may have a little or you may have a lot. You'll probably never know until
you need some old information and don't have it.

<span class="x" /> **Sendmail configuration is
painful.** HP-UX doesn't give you the m4 configuration files for
sendmail so that you can use the m4 macros to generate a `sendmail.cf`.
Instead, they expect you to hack `sendmail.cf` directly. This is not
the way sendmail is intended to be configured.

<span class="x" /> **Load average calculations are
different.** In HP-UX, unlike Solaris, Linux, or just about any other
UNIX, load averages reported by `uptime` are divided by the number of
processors in the system, so that a load average of 1.0 means the system has
as many processes in the run queue as it has processors. That's all well and
good, and it might even be a better approach than the other vendors, but
once again HP-UX breaks with tradition and confuses administrators of other
platforms.

<span class="x" /> **You need a patch and special mount
option to read a CD-ROM with RockRidge extensions.** The ISO9660
filesystem format, used on CD-ROMs, limits the filenames to 8.3-character
names. RockRidge extensions allow longer filenames and allow UNIX file
permissions to be stored on the CD-ROM. HP-UX is the only UNIX I've encountered
that doesn't handle this format natively. Not only do you need a patch to
support it, but you have to mount your CD-ROM with `-o rr` to read
RockRidge extensions.

<span class="x" /> **Swap volumes/files can not be
removed on the fly.** HP-UX lets you add a new swap volume or file
while the system is running, but to remove it you have to reboot.

<span class="x" /> **There is no /etc/nsswitch.conf.**
By default, there is no /etc/nsswitch.conf, and name service switch library
uses compiled-in defaults. If you don't want to use the mysterious defaults,
just create a file of your own.

<span class="x" /> **Manual device file creation for
LVM.** LVM is nice, but when I create a volume group, I really shouldn't
have to run `mknod` myself and stick a device file in
/dev/vg<em>xx</em>.

## What HP-UX gets right

Believe it or not, I actually do like quite a few things about HP-UX. They
are outweighed in importance by the things I don't like, but I list them here
nonetheless to prove I'm not just mean.

<span class="checkmark" /> **Startup/shutdown log.**
Many times I've watched a Solaris system boot and have seen a startup script
print an error message. As soon as I can think, "hey, something's not right,"
it's off the screen and lost forever. HP-UX saves the output of the startup
and shutdown scripts in a /etc/rc.log, so you can investigate any failures
later. Don't beat them up about logging to /etc &mdash; /var isn't mounted when
they need to start writing to the log.

<span class="checkmark" /> **Startup/shutdown messages
are pretty.** Instead of showing me stdout/stderr from every startup
and shutdown script, HP-UX gives me a one-line summary of each thing it's
doing, like "Starting NFS Server," and then either "OK" or "FAIL." This is
nice, since some Solaris startup scripts print several lines of output
and others print none at all. And since the detailed output is logged
elsewhere, I don't lose any information.

<span class="checkmark" /> **Boot-up can be
interrupted.** If you're booting HP-UX, and you notice that a critical
service failed to start, you can interrupt the boot with control-backslash,
get a shell, and debug it immediately, rather than waiting for the system
to come all the way up. This is useful when the service you're trying to
debug is so critical that you know you'll need to reboot after making the
fix anyway.

<span class="checkmark" /> **/etc/rc.config.d is
nice.** Most of the configuration of daemons that in Solaris would
be done by editing various per-daemon configuration files in /etc is done
in HP-UX by editing files in /etc/rc.config.d and setting the values of
predefined variables. These files are sourced by the init.d startup scripts,
and tell them things like whether an NFS server should start, where's the
NTP server, what IP address should an interface have, etc. It's a more
consistent interface to the system's configuration.

<span class="checkmark" /> **Kernel tunables can be
set in terms of other tunables.** You can choose to set a tunable's
value absolutely &mdash; say, to 1024 &mdash; or in terms of another tunable &mdash; for
example, to maxuprc * 10. This is pretty nice, since you can edit fewer
tunables and have the relative ones scale automatically. This feature was
removed in HP-UX 11iv2, though.

<span class="checkmark" /> **fstab is a better name
than vfstab.** Sorry, Solaris &mdash; /etc/vfstab should be /etc/fstab,
because that's what *everybody else* calls it.

<span class="checkmark" /> **Patch rating system.**
Every HP-UX patch has a rating, so you can tell how widely used the patch
is and how thoroughly tested it has been.

<span class="checkmark" /> **Downloaded patches can be
bundled into a depot.** When you download patches from HP's web site,
you have the option of making the patches into a software depot. If you're
installing them on multiple systems, this makes it a lot easier than
managing all the patches individually.

<span class="checkmark" /> **Separation of analyze
phase from install phase for software/patch installation.** HP-UX's
software distribution system (SD-UX) separates the analyze phase (checking
disk space, checking prerequisites, etc.) from the installation phase when
installing patches or software. With a bundle of patches, this can be
a big time saver. You can perform the analyze phase for all the patches
ahead of time, which won't modify anything on the system, and do the
installation phase during your system's maintenance window. In Solaris,
patches take a long time to install, and much of the time is spent calculating
whether or not the patch should be applied at all.

<span class="checkmark" /> **The output of ioscan is
easier to read than prtconf.** If I want to quickly see what devices
are attached to the system, HP-UX's ioscan is much easier to read than
Solaris' prtconf. Of course, tea leaves are probably easier to read than
prtconf, so that's not saying much.
