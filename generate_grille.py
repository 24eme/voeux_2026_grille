import sys
import json

class MotCroise:

    def __init__(self):
        self.grille_yx = []
        self.grille_taille = 0
        self.mots = []
        self.message = ""
        self.mots_message = []
        self.msg_positions = []


    def addMot(self, mot, definition):
        self.mots.append([mot.upper(), definition])

    def loadJson(self, json_file):
        with open(json_file) as f:
            mots = json.load(f)
            for m in mots:
                self.addMot(m, mots[m])

    def setMessage(self, msg):
        self.message = msg
        for (mot,definition) in self.mots:
            for lettre in self.message:
                if lettre in mot:
                    self.mots_message.append(mot)
                    break;

    def setPositionMot(self, mot, position_x, position_y, orientation):
        if orientation == 'H':
            for mot_x in (range(len(mot))):
                self.grille_yx[position_y][mot_x + position_x] = mot[mot_x]
            return
        if orientation == 'V':
            for mot_y in (range(len(mot))):
                self.grille_yx[position_y + mot_y][position_x] = mot[mot_y]
            return
        raise Exception('unknown orientation '+orientation)

    def isPositionOK(self, mot, position_x, position_y, orientation):
        has_intersection = False
        move_on_x = 0
        move_on_y = 0
        if orientation == 'H':
            #test si mot trop long en x
            if len(mot) + position_x > self.grille_taille:
                return False
            move_on_x = 1
        if orientation == 'V':
            #test si mot trop long en y
            if len(mot) + position_y > self.grille_taille:
                return False
            move_on_y = 1
        for m in range(len(mot)):
            x = position_x + m * move_on_x
            y = position_y + m * move_on_y
            #il nous faut au moins une intersection
            if mot[m] == self.grille_yx[y][x]:
                has_intersection = True
                continue
            #si rencontre une lettre déjà positionnées : position non permise
            if self.grille_yx[y][x] != ' ':
                return False
            if move_on_y:
                #si est collé à un autre mot en x (avant) : position non permise
                if x > 0 and self.grille_yx[y][x - 1] != ' ':
                    return False
                #si est collé à un autre mot en x (après) : position non permise
                if x + 1 < self.grille_taille and  self.grille_yx[y][x + 1] != ' ':
                    return False
            if move_on_x:
                #si est collé à un autre mot en y (avant) : position non permise
                if y > 0 and self.grille_yx[y - 1][x] != ' ':
                    return False
                #si est collé à un autre mot en x (après) : position non permise
                if y + 1 < self.grille_taille and self.grille_yx[y + 1][x] != ' ':
                    return False
        #On test qu'il n'y a pas de mot déjà placé en tout début ou toute fin de la position interrogée
        if move_on_x:
            if position_x > 0:
                if self.grille_yx[position_y][position_x - 1] != ' ':
                    return False
            if position_x + len(mot) < self.grille_taille:
                if self.grille_yx[position_y][position_x + len(mot)] != ' ':
                    return False
        if move_on_y:
            if position_y > 0:
                if self.grille_yx[position_y - 1][position_x] != ' ':
                    return False
            if position_y + len(mot) < self.grille_taille:
                if self.grille_yx[position_y + len(mot)][position_x] != ' ':
                    return False

        return has_intersection

    def generate(self, taille):
        self.grille_taille = taille
        for x in range(taille):
            self.grille_yx.append([' ' for y in range(taille)])

        self.mots_message.sort(key=lambda s: len(s), reverse=True)

        self.setPositionMot(self.mots_message[0], int(taille / 2) - int (len(self.mots_message[0]) / 2), int(taille / 2), 'H')

        for mot in self.mots_message:
            positions_mot = []
            need_new_mot = False
            for x in range(taille):
                if need_new_mot:
                    break
                for y in range(taille):
                    if need_new_mot:
                        break
                    for o in ['V', 'H']:
                        if self.isPositionOK(mot, x, y, o):
                            positions_mot.append([x, y, o])
                            need_new_mot = True
                            break
            for (x, y, o) in positions_mot:
                self.setPositionMot(mot, x, y, o)
                break

    def identifyLettresMessage(self):
        lettres = list(self.message)
        l = lettres.pop(0)
        debut = 0
        for y in range(self.grille_taille):
            for x in range(debut, self.grille_taille):
                print([x,y])
                if l == ' ':
                    l = lettres.pop(0)
                    debut = 0
                    break
                if l == self.grille_yx[y][x]:
                    self.msg_positions.append([x, y])
                    debut = x
                    if not len(lettres):
                        return True
                    l = lettres.pop(0)
        if len(lettres):
            return False
        return True

    def print(self):
        for g in self.grille_yx:
            print(g)
            print()


if __name__ == "__main__":

    mot_secret="BONNE ANNEE JESUS"
    if len(sys.argv) > 1:
        mot_secret=sys.argv[1].upper()

    mc = MotCroise()
    mc.loadJson("mots_principaux.json")
    mc.loadJson("mots_complementaires.json")
    mc.setMessage(mot_secret)
    mc.generate(25)
    mc.print()
