#!/bin/sh
# checks a given file out of CVS, runs pod2html on it, and prints only the body

tmpdir=/tmp/pod2html.tmp.$$

PrintUsageAndExit() {
  echo "USAGE: $0 <cvsroot> <file>"
  rm -rf $tmpdir
  exit 2
}

RunIt() {
  eval $@
  rc=$?
  if [ $rc -ne 0 ]; then
    echo "ERROR: command <$@> returned <$rc>"
    rm -rf $tmpdir
    exit 1
  fi
}

cvsroot=$1
file=$2

if [ -z "$cvsroot" -o -z "$file" ]; then
  PrintUsageAndExit
fi

CVSROOT=$cvsroot; export CVSROOT

RunIt mkdir $tmpdir
RunIt cd $tmpdir
RunIt cvs -Q checkout $file
RunIt pod2html $file | awk 'BEGIN {
  shouldprint = 0
}
/^<!-- INDEX BEGIN -->$/ {
  shouldprint = 1
}
/^<\/[bB][oO][dD][yY]>$/ {
  shouldprint = 0
}
{
  if( shouldprint == 1 ) print
}'
RunIt cd /
RunIt rm -rf $tmpdir
