# Voeux 2026

    python generate_grille.py "BONNE ANNEE TOTO" PREFIX_
    sed -i -f motifs.sed PREFIX_grille.svg

On obtient PREFIX_grille.svg la grille avec les inserts extra (logos / photo) et PREFIX_grille_mots_definitions.json qui contient les numéros des mots, les mots et leurs définitions.

Pour générer les pages au format PDF, il faut lancer la commande suivante :

    bash replace_mots.sh PREFIX_grille_mots_definitions.json pages/[nom du template]/ PREFIX

les fichiers sont placés dans le dossier `output/PREFIX/`

### Impression au format booklet

Paquets requis : [a5toa4](https://packages.debian.org/bullseye/texlive-extra-utils) et [pdftk](https://packages.debian.org/bullseye/pdftk)

Potentiellement, l'erreur `I can't find the format file ``pdflatex.fmt'!` apparait et il faut ajouter des paquets latex supplémentaires

Concatener les 4 pages dans un seul fichier via pdftk :

    pdftk output/NOM/page{1,2,3,4}.pdf cat output output/NOM/NOM.pdf

Puis générer le booklet :

    a5toa4 --booklet output/NOM/NOM.pdf

Cela créé un fichier suffixé par `-booklet` au format pdf

Pour l'impression en recto-verso, il faut sélectionner `bord court` sinon le verso est dans le mauvais sens
