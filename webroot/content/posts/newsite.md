---
title: "New web site!"
date: 2020-08-16T13:25:02-04:00
draft: false
toc: false
images:
tags:
  - untagged
---
<figure style="float: right; margin-top: 0; margin-left: 1em; margin-bottom: 1em;">
  <img src="/images/old_website.png" style="border: 1px solid black" />
  <figcaption style="text-align: center;" >
    The old site, circa 2005, from the <a href="https://web.archive.org/web/20200228133831/http://www.loudermilk.org/">Wayback Machine</a>
  </figcaption>
</figure>

It's time for a change of scenery around here. Actually, it's more than time --
the old site design was from 2005. It had lots of nested tables and wasn't
mobile-friendly at all (hey, there was no mobile in 2005!). But I was ahead of
my time in one respect: it was a statically-generated site way before static
sites were cool.

The old site was built with a tool called Website META Language (or WML), which
I'd first heard about in the late 90s to give you some idea of its age.  It had
a bunch of different backends that would make "passes" over your files and do
different things -- one could expand includes, another could evaluate Perl
code, for example -- giving you lots of features. But it's showing its age and
I thought it was time to make a change.

The new site is built with <a href="https://gohugo.io/">Hugo</a>, a modern
static site generator. Because of the way the old site worked, I originally
thought I first needed to find a new static site generator, and then I needed
to update the design to something more modern by hand. While I certainly could
do that with Hugo, Hugo has some native support for themes, with tons of
open-source themes available.  So for now I'm using the <a
href="https://github.com/rhazdon/hugo-theme-hello-friend-ng">hello-friend-ng</a>
theme.

The old site just had a bunch of standalone pages, in a few different categories.
There were blog entries, but they were only shown on the very front page, and even
then they were just snippets pulled from my LiveJournal page (I told you it was from
2005).

For the new site, I converted several of the more popular and still relevant
pages to blog-style posts, since Hugo makes that type of page really easy. And
I can add permalinks to make any well-known URLs still work (like the <a
href="/milk/">milk bet</a>, by far the most popular page on the site). I think
this will make it more likely that I'll update the site more frequently, but I
suppose time will tell.

