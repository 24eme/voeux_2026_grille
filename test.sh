#!/bin/bash

output=/tmp/$$.tmp
if test "$2"; then
	output=$2
fi

if ! test "$1"; then
	echo pad missing;
	exit 1
fi
pad=$1

bash run.sh "$pad" | sed 's/.* bash replace.sh/bash test_one.sh/' | bash > $output 
cat $output | awk '{print $2}' | sort | uniq -c

if test -f /tmp/$$.tmp; then
	rm /tmp/$$.tmp
fi
