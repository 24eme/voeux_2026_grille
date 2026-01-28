#!/bin/bash

cd  $(dirname $0)/

if ! test "$1" ; then
	echo arg pad missing;
	exit 1;
fi
pad=$1

echo "Comparaison avec le pad :"

bash test.sh "$pad" /tmp/cartes.list

pdftk $(cat /tmp/cartes.list | grep 'OK$' | awk '{print $1}') cat output cartes-booklet.pdf
ls -lh cartes-booklet.pdf
rm /tmp/cartes.list
