#!/bin/bash

if ! test "$5"; then
  echo "Usage: bash replace.sh <MESSAGE> <nom_destinataire> <output_subdir> <chemin/vers/pages/> <chemin/vers/dictionnaire>"
  exit 1
fi

MESSAGE="$1"
DESTINATAIRE="$2"
OUTPUT_SUBDIR=$(echo $3 | sed 's/output\///' | sed "s/'//g")
PATH_PAGES="$4"
DICTIONNAIRE="$5"

if test -f output/$OUTPUT_SUBDIR/carte_finale.pdf && test -f output/$OUTPUT_SUBDIR/carte_finale-booklet.pdf ; then
	echo output/$OUTPUT_SUBDIR/carte_finale-booklet.pdf OK
else
	echo output/$OUTPUT_SUBDIR/carte_finale-booklet.pdf ERROR
fi
