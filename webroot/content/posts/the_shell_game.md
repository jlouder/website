---
title: "The shell game"
date: 2009-07-08T21:20:25-04:00
draft: false
toc: false
images:
tags:
  - untagged
---
At work today, I found myself explaining why I use tcsh instead of ksh as my interactive shell. I've had this discussion a number of times over the years, as our shop has primarily ksh users, so I thought I'd write down some of my reasons.



First off, I'm not talking about writing shell scripts (lest you try to point out that [csh programming is considered harmful](http://www.faqs.org/faqs/unix-faq/shell/csh-whynot/)). I'm talking about an interactive shell. And no, I don't write scripts in csh, but more on that later.



I got hooked on tcsh when I first got started with UNIX by my old boss [Steve Ulmer](http://www.ulmer.org/). It wasn't until I came to my current job (now more than 10 years ago) and saw everyone using ksh that I came to realize how superior tcsh is as an interactive shell. Here are some things I do with tcsh that ksh can't do:





* Command history with one keystroke. Just press the up arrow to go back in history, down to go forward. Once you're used to this, pressing ksh's ESC-k sequence feels so awkward.

* Deduplication of command history. If I want to run the same command ten times, I just press the up arrow then enter ten times. But if I then want to run the command I ran before that one I just ran ten times, I only need to press up twice. ksh would have me press ESC, then 'k' eleven times. This may sound trivial, but I do this a lot when waiting for something to finish.

* More sane completion behavior. Aside from the fact I can complete with one keystroke (TAB, instead of the oh-so-natural ESC-\\), tcsh lets me immediately see a list of possible matches, unless of course there are too many in which case it asks if I really want to see all _N_ matches.

* Programmable completion rules. I can (and do, thanks Steve!) tell tcsh that if I press TAB to autocomplete the first argument to 'cd', it should use only directories. The first argument to chgrp? Only groups. The filename I pass to 'vi'? Never a .o file. The hostname argument to ssh? A predefined list of my favorite systems. You get the picture.

* I put the command history number in my prompt, so if I can see a previous command on my screen and want to re-run it, I can do so without scrolling through the command history to find it. For instance, to re-run command number 13 I just enter "!13" and I'm done.





Clever readers will point out that bash can do everything I've mentioned. That's why I'm not writing about how tcsh is better than bash, just ksh, as an interactive shell. I've thought about switching to bash, but it wouldn't really give me more than I have now. And also, after this long I kind of enjoy being the only person using tcsh at work. It's even somewhat of a security feature -- people who sit down at my shell usually quickly get frustrated because "it's not working right."



I mentioned earlier that I don't write scripts in tcsh, or csh for that matter. But I don't write them in ksh either. My philosophy (more of Steve's influence here, too) is that if you're writing a shell script, write it for the Bourne shell. It's the lowest common denominator, and every UNIX-ish system you'll run it on will have something that understands Bourne shell. You might not necessarily have a ksh. If you think that's always safe to assume, ask the programmers at my office who are recoding scripts because Red Hat switched from pdksh to AT&amp;T ksh with RHEL5.



If you're writing a shell script and you need the extra features of ksh (like arrays, or doing math directly in the shell), you should really be using a more powerful scripting language like Perl anyway. Your users will thank you, too, when your scripts drastically increase in speed because you're not fork()ing a dozen times per second to accomplish simple tasks built into a more full-featured interpreter.
