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

mkdir -p "tmp/$OUTPUT_SUBDIR"
PREFIX="tmp/$OUTPUT_SUBDIR/$OUTPUT_SUBDIR"

JSON_MOTS="${PREFIX}_grille_mots_definitions.json"
GRILLE="${PREFIX}_grille.svg"

if python3 generate_grille.py "$MESSAGE" "${PREFIX}_" ${DICTIONNAIRE:+ "$DICTIONNAIRE"}; then
  sed -i -f motifs.sed "$GRILLE"
fi

if ! test -f $GRILLE ; then
  echo "$GRILLE not found"
  exit 5;
fi

if [ ! -f "${PATH_PAGES}/page1.svg" ]; then
  echo "page1.svg not found!"
  exit 1
fi

if [ ! -f "${PATH_PAGES}/page2.svg" ]; then
  echo "page2.svg not found!"
  exit 2
fi

if [ ! -f "${PATH_PAGES}/page3.svg" ]; then
  echo "page3.svg not found!"
  exit 3
fi

if [ ! -f "${PATH_PAGES}/page4.svg" ]; then
  echo "page4.svg not found!"
  exit 4
fi

sed "s/%NOM%/$DESTINATAIRE/" ${PATH_PAGES}/page1.svg > tmp/"$OUTPUT_SUBDIR"/page1.svg

MOTS_VERTI=$(jq -r '.[] | select(.orientation=="V") | "\(.mot_id). \(.definition)"' "$JSON_MOTS" | tr "\n" '|' | sed 's/|/\\n/g')

MOTS_HORIZ=$(jq -r '.[] | select(.orientation=="H") | "\(.mot_id). \(.definition)"' "$JSON_MOTS" | tr "\n" '|' | sed 's/|/\\n/g')

SOLUTIONS=$(jq -r '.[] | "\(.mot_id). \(.mot)"' "$JSON_MOTS" | tr "\n" ' ')

sed -e "s/%MOTS_VERTI%/$MOTS_VERTI/" -e "s/%MOTS_HORIZ%/$MOTS_HORIZ/" ${PATH_PAGES}/page2.svg > tmp/"$OUTPUT_SUBDIR"/page2.svg
sed "s/%SOLUTIONS%/$SOLUTIONS/" ${PATH_PAGES}/page4.svg > tmp/"$OUTPUT_SUBDIR"/page4.svg

sed '/%GRILLE%/Q' ${PATH_PAGES}/page3.svg > tmp/"$OUTPUT_SUBDIR"/page3.svg
sed '1d' $GRILLE >> tmp/"$OUTPUT_SUBDIR"/page3.svg
sed '1,/%GRILLE%/d' ${PATH_PAGES}/page3.svg >> tmp/"$OUTPUT_SUBDIR"/page3.svg

sed "s/%SOLUTIONS%/$SOLUTIONS/" ${PATH_PAGES}/page4.svg > tmp/"$OUTPUT_SUBDIR"/page4.svg


if ! test -f tmp/"$OUTPUT_SUBDIR"/page1.svg; then
	echo ERROR: tmp page1 missing;
	exit 6;
fi
if ! test -f tmp/"$OUTPUT_SUBDIR"/page2.svg; then
        echo ERROR: tmp page2 missing;
        exit 7;
fi
if ! test -f tmp/"$OUTPUT_SUBDIR"/page3.svg; then
        echo ERROR: tmp page3 missing;
        exit 8;
fi
if ! test -f tmp/"$OUTPUT_SUBDIR"/page4.svg; then
        echo ERROR: tmp page4 missing;
        exit 9;
fi


mkdir -p "./output/$OUTPUT_SUBDIR"

inkscape -o "./output/$OUTPUT_SUBDIR"/page1.pdf tmp/"$OUTPUT_SUBDIR"/page1.svg > /dev/null 2>&1
inkscape -o "./output/$OUTPUT_SUBDIR"/page2.pdf tmp/"$OUTPUT_SUBDIR"/page2.svg > /dev/null 2>&1
inkscape -o "./output/$OUTPUT_SUBDIR"/page3.pdf tmp/"$OUTPUT_SUBDIR"/page3.svg > /dev/null 2>&1
inkscape -o "./output/$OUTPUT_SUBDIR"/page4.pdf tmp/"$OUTPUT_SUBDIR"/page4.svg > /dev/null 2>&1

pdftk "./output/$OUTPUT_SUBDIR/page1.pdf" "./output/$OUTPUT_SUBDIR/page2.pdf" "./output/$OUTPUT_SUBDIR/page3.pdf" "./output/$OUTPUT_SUBDIR/page4.pdf" cat output "./output/$OUTPUT_SUBDIR/carte_finale.pdf"

a5toa4 --booklet "./output/$OUTPUT_SUBDIR/carte_finale.pdf"

if test -f "./output/$OUTPUT_SUBDIR/carte_finale.pdf" && test -f "./output/$OUTPUT_SUBDIR/carte_finale-booklet.pdf"; then
	echo "./output/$OUTPUT_SUBDIR/carte_finale-booklet.pdf généré";
else
	echo "ERROR dans la génération : pas de ./output/$OUTPUT_SUBDIR/carte_finale-booklet.pdf"
	exit 10;
fi
