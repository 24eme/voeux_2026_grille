#!/bin/bash

ARGC=$#
MAX_ARGS=3

if [ "$ARGC" -ne "$MAX_ARGS" ]; then
  echo "Usage: bash replace_mots.sh <PREFIX_grille_mots_definitions.json> <chemin/vers/pages/> <nom_destinataire>"
  exit 1
fi

JSON_MOTS="$1"
PATH_PAGES="$2"
DESTINATAIRE="$3"

[[ "$PATH_PAGES" != */ ]] && PATH_PAGES="${PATH_PAGES}/"

if [ ! -f "${PATH_PAGES}page1.svg" ]; then
  echo "page1.svg not found!"
  exit 1
fi

if [ ! -f "${PATH_PAGES}page2.svg" ]; then
  echo "page2.svg not found!"
  exit 1
fi

if [ ! -f "${PATH_PAGES}page4.svg" ]; then
  echo "page4.svg not found!"
  exit 1
fi

MOTS_VERTI=$(jq -r '.[] | select(.orientation=="V") | "\(.mot_id). \(.definition)"' "$JSON_MOTS" | tr "\n" '|' | sed 's/|/\\n/g')

MOTS_HORIZ=$(jq -r '.[] | select(.orientation=="H") | "\(.mot_id). \(.definition)"' "$JSON_MOTS" | tr "\n" '|' | sed 's/|/\\n/g')

SOLUTIONS=$(jq -r '.[] | "\(.mot_id). \(.mot)"' "$JSON_MOTS" | tr "\n" ' ')

mkdir -p "/tmp/$DESTINATAIRE"
sed -e "s/%MOTS_VERTI%/$MOTS_VERTI/" -e "s/%MOTS_HORIZ%/$MOTS_HORIZ/" ${PATH_PAGES}page2.svg > /tmp/"$DESTINATAIRE"/page2.svg
sed "s/%SOLUTIONS%/$SOLUTIONS/" ${PATH_PAGES}page4.svg > /tmp/"$DESTINATAIRE"/page4.svg

mkdir -p "./output/$DESTINATAIRE"
inkscape -o "./output/$DESTINATAIRE"/page2.svg /tmp/"$DESTINATAIRE"/page2.svg
inkscape -o "./output/$DESTINATAIRE"/page4.svg /tmp/"$DESTINATAIRE"/page4.svg
