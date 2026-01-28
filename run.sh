if ! test "$1"; then
	echo bash $0 url_pad_export_txt | bash
	exit 1
fi

rm -f txt
wget -q "$1"
grep -v '#' txt  | grep ';' | grep -v gabriel,charlene,vincent | awk -F ';' '{if ($5) { dir=toupper(gensub(" ", "_", "g", $5"_"$1)); print "test -d output/"dir" || bash replace.sh \""$2"\" \""$1"\" \"output/"dir"\" \"pages/"$3"\" dictionnaires/"$4".json"} }'
