website
=======

This is the source code to Joel's personal web site. For many years it was in CVS, and I've converted the repository to import
the history for each file.

To build the web site, you'll need [WML](thewml.org). From the top of the source tree, run:

```
wmk -a -F include -I $PWD/webroot/include
```
