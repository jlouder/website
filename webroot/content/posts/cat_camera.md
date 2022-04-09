---
title: "New cat camera"
date: 2022-04-09T14:18:15-04:00
draft: false
toc: false
images:
  - https://raw.githubusercontent.com/jlouder/foscam-viewer/main/screenshot.png
tags:
  - untagged
---
For years, I've had an old but simple system to keep an eye on the cats when
I'm away: an old IP camera (Foscam brand) is on the wifi network. For real-time
viewing, the camera has a built-in web server with a simple interface to see a
live video and move the camera around. For historical viewing, a simple script
is pulling an image every several seconds, and every few hours making those
into a video.

This worked perfectly well, but things were getting a little old. For one
thing, the camera's plastic housing was starting to get a little tacky, which
is nasty. Also, the camera's images were just 640x480.  Cameras like this are
pretty cheap, so why not upgrade and get something more modern?

My requirements for the new camera were:

* No cloud. I already have or can make the software to capture and show
stills and videos from the camera. Me watching images from the camera should
involve me and the camera -- an no one else.
* Better resolution. Just about any camera on the market currently should
do that.
* A live view web interface that doesn't look horrible on mobile. Again,
anything currently being sold should do that.

## Selecting a camera

The "no cloud" was the hardest requirement to meet. There are tons of IP cameras
out there, but for many it's hard to tell without buying the camera whether you
can access images and video without connecting it to their cloud.

I ended up going with the **Foscam R4S**. It appeared to be the current version of
what I had before, a bit smaller now, which was a nice improvement. Also the
plastic isn't sticky because the camera isn't 10 years old.

I found a document about their API for the camera, which is a bit crude and
odd, but did seem to support what I needed -- capturing a still image. Like
my old camera, the R4S has a built-in web interface to let you configure it,
view live video, and move the camera around.

Swapping out the old camera for this one should be pretty easy, right?

## Challenge #1: Configuring the Foscam R4S

I imagined that configuring the Foscam R4S would go something like this: plug
it in to the wired network, access it with a browser, and do the basic setup
(wifi, users and passwords, and such). Nope, this thing offers you two ways to
configure it once you plug it in to the wired network:

1. Use the Foscam app on your phone to configure it. The very first thing the
Foscam app requires you to do is set up a cloud account with them.  Nope, not
going to happen.
2. Use a web browser to configure it. The very first thing its web interface
does is give you a Windows executable to install as a browser plug-in, which is
required for their web interface. Nope, not going to happen.

Thankfully, the camera's [API](https://github.com/jlouder/foscam-viewer/blob/main/Foscam-IPCamera-CGI-User-Guide-AllPlatforms-2015.11.06.pdf)
is pretty full-featured. I was able to use it to do the configuration I needed,
which was changing passwords and getting it on the wireless network.

The API is a little odd. It's a couple of CGIs you hit on the camera's web
server and pass a bunch of parameters. Everything returns an XML response, but
it's pretty well documented in Foscam's API guide. The wireless setup in
particular took several attempts but I did eventually get the camera on the
wireless network.

There's a simple call you can make to fetch a live image from the camera.
That's exactly what I needed for my existing video-making script, so no issues
there.

## Challenge #2: Viewing live images and moving the camera around

At this point I've got my historical videos of the camera's images working.
But I don't have any way to look at live video, and more importantly I don't
have a way to move the camera!

The way they want you to do this is just like the way they want you to do the
initial configuration -- either use their app on your phone (and their cloud),
or use a web browser from a Windows machine running their proprietary browser
plugin.

So I decided to create my own tiny web application to show a live stream from
the camera and let you move the camera around in different directions.  This is
all I really wanted from the web interface anyway. For other, more
seldomly-performed activities (like changing passwords, turning the timestamp
overlay on or off, etc.) I'd just manually call their API. I do those things so
rarely that it's not important to have them in the web app.

## Challenge #3: Viewing live video

The Foscam R4S has a couple of ways you can get video out of it: RTSP or an
MJPEG stream. RSTP worked great from an RSTP-capable viewer (like VLC), but
that wouldn't work for my web app. I need something a browser can understand.

The old camera's web interface fed you an MJPEG stream, so that seemed the way
to go. However, I couldn't get that to work through the API. There's a separate
HTTPS port you have to use for that call, and no matter how hard I tried,
it always gave me an HTTP 500. Maybe I was missing some one-time setup that
would've been done for me had I used their configuration methods, or maybe
it just doesn't work.

Even if it did work, it almost doesn't matter because the built-in HTTPS server
can't speak TLS 1.3, which means no modern web browser can talk to it. The only
way I could talk to it was to use `curl --tls-max 1.2`.

After looking into what would be involved in making my web app read the
camera's RSTP stream and turn it into something a browser can understand
(that's hard), I decided to just implement my own MJPEG stream. Turns out,
that's pretty simple.  You send a response with a `Content-Type:
multipart/x-mixed-replace; boundary={some string}` and then repeatedly send
images, each with their own `Content-Type` and `Content-Length` headers,
separated by the boundary string. (It's easy enough that I could do it in just
about 20 lines of Perl. [Here's that
code.](https://github.com/jlouder/foscam-viewer/blob/5c7bf0f04f42313c9ae5561c4654b6430d60a288/lib/FoscamViewer/Controller/Webapp.pm#L17))

So I could just repeatedly fetch an image, write a JPEG and the boundary
string, and repeat. As simple and crude as this sounded, it worked and gives
the illusion of video in the browser.

## The finished app

{{< figure src="https://github.com/jlouder/foscam-viewer/raw/main/screenshot.png?raw=true"
           link="https://github.com/jlouder/foscam-viewer" class="thumbnail" >}}

I told you it was simple, right? All I need is the video feed and some buttons to
move the camera around.

If you're interested in this app, [take a look at it on
GitHub](https://github.com/jlouder/foscam-viewer) where I've documented how to
install and configure it.
