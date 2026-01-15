import sys
import json
import copy

class MotCroise:

    def __init__(self, grille_yx, mots_possibles, message, nb_mot=0):
        self.grille_yx = grille_yx.copy()
        self.grille_taille = len(grille_yx)
        self.mots = mots_possibles.copy()
        self.message = message
        self.msg_positions = []
        self.mots_nb = nb_mot
        self.score = -1
        self.nb_lettres_found = 0
        self.score_matrix = [0] * len(self.message)
        self.iteration_nb = 0
        self.initScoreMatrix()

    def initScoreMatrix(self):
        x = 0
        min_y = 0
        mots = self.message.split( )
        for mot in mots:
            max_y = min_y + int(self.grille_taille / len(mots))
            min_x = 0
            for lettre in list(mot):
                max_x = min_x + int(self.grille_taille / len(mot))
                self.score_matrix[x] = [min_x, max_x, min_y, max_y]
                min_x = max_x + 1
                x += 1
            x += 1
            min_y = max_y + 1


    def removeMot(self, mot):
        self.mots.remove(mot)

    def setPositionMot(self, mot, position_x, position_y, orientation):
        self.mots_nb += 1
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

    def getScore(self, is_premier=False):
        self.identifyLettresMessage(is_premier)
        return self.score

    def identifyLettresMessage(self, is_premier=False):
        lettres = list(self.message)
        self.score = 0
        self.nb_lettres_found = 0
        self.msg_positions = []
        debut = 0
        lettre_id = -1
        if (is_premier):
            lettre_id = int(len(lettres)/2) - 2
            lettres = lettres[int(len(lettres)/2) - 1:]
        l = 'X'
        while (l ):
            if not len(lettres) :
                break
            l = lettres.pop(0)
            lettre_id += 1
            if self.score:
                break
            for y in range(self.grille_taille):
                for x in range(debut, self.grille_taille):
                    if l == ' ':
                        l = lettres.pop(0)
                        lettre_id += 1
                        self.nb_lettres_found += 1
                        debut = 0
                        break
                    if self.grille_yx[y][x] == ' ':
                        continue
                    if l == self.grille_yx[y][x]:
                        self.msg_positions.append([x, y])
                        (min_x, max_x, min_y, max_y) = self.score_matrix[lettre_id]
                        score_to_add = 0
                        if min_x <= x and max_x >= x and min_y <= y and max_y >= y:
                            score_to_add += self.grille_taille * 2
#                        elif min_x < x:
#                            score_to_add += int(self.grille_taille / 2) - min_x + x
#                        else :
#                            score_to_add += int(self.grille_taille / 2) - x + max_x
#                        if :
#                            score_to_add += self.grille_taille
#                        elif min_y < y:
#                            score_to_add += int(self.grille_taille / 2) - min_y + y
#                        else :
#                            score_to_add += int(self.grille_taille / 2) - y + max_y
                        else:
                            score_to_add += 10
                        self.score += score_to_add
                        for a in range(x-1, x+1):
                            for b in range(y-1, y+1):
                                if [a,b] in self.msg_positions:
                                    self.score -= 5
                        self.nb_lettres_found += 1
                        debut = x
                        if not len(lettres):
                            if self.nb_lettres_found >= len(self.message):
                                return True
                            return False
                        l = lettres.pop(0)
                        lettre_id += 1
            if self.iteration_nb > 10:
                break
        if self.nb_lettres_found < len(self.message):
            return False
        return True


    def print(self, is_premier=False):
        print("  " + "=" * self.grille_taille * 3 +" ")
        print("  " + str(self.getScore(is_premier)) +" " + str(len(self.message)))
        mot_presentations = []
        for y in range(self.grille_taille):
            presentation_x = []
            for x in range(self.grille_taille):
                if ([x, y] in self.msg_positions):
                    presentation_x.append("["+self.grille_yx[y][x]+"]")
                else:
                    presentation_x.append(" "+self.grille_yx[y][x]+" ")
            print(" ║" + "".join(presentation_x) + "║")
        print("  " + "=" * self.grille_taille * 3 +" ")

    def generation(mot_croise, i=1):
        un_mot_croise = copy.deepcopy(mot_croise)
        un_mot_croise.iteration_nb = i

        if (i > len(un_mot_croise.message)):
            return None
        if i % 4 == 0:
            un_mot_croise.print()
        current_score = un_mot_croise.getScore()
        for mot in un_mot_croise.mots:
            positions_mot = []
            need_new_mot = False
            for x in range(un_mot_croise.grille_taille):
                if need_new_mot:
                    break
                for y in range(un_mot_croise.grille_taille):
                    if need_new_mot:
                        break
                    for o in ['V', 'H']:
                        if un_mot_croise.isPositionOK(mot, x, y, o):
                            new_mc = copy.deepcopy(un_mot_croise)
                            new_mc.setPositionMot(mot, x, y, o)
                            new_mc.removeMot(mot)
                            score = new_mc.getScore()
                            if score > current_score:
                                new_mc.print()
                                positions_mot.append([copy.deepcopy(new_mc), score])
            positions_mot.sort(key=lambda x: x[1], reverse=True)
            i = 0
            for (new_mc, score) in positions_mot:
                if new_mc.identifyLettresMessage():
                    new_mc.print()
                    return new_mc
                new_mc = MotCroise.generation(new_mc, un_mot_croise.iteration_nb+1)
                if new_mc:
                    return new_mc
                if i > len(positions_mot) / 2:
                    break;
        return None

class MotCroiseGenerator:

    def __init__(self):
        self.mots = []
        self.message = ""
        self.mots_message = []

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

    def generate(self, taille):
        grille_yx = []
        for x in range(taille):
            grille_yx.append([' ' for y in range(taille)])

        self.mots_message.sort(key=lambda s: len(s), reverse=True)

        empty_mot_croise = MotCroise(grille_yx, self.mots_message, self.message)
        premier_mot_possibles = []
        for premier_mot in self.mots_message:
            mc = copy.deepcopy(empty_mot_croise)
            mc.setPositionMot(premier_mot, int(taille / 2) - int (len(premier_mot) / 2), int(taille / 2), 'H')
            mc.removeMot(premier_mot)
            score = mc.getScore(True)
            mc.print(True)
            premier_mot_possibles.append([copy.deepcopy(mc), mc.getScore(True)])
        premier_mot_possibles.sort(key=lambda x: x[1], reverse=True)
        premier_mot_possibles[0][0].print(True)
        for (mc, score) in premier_mot_possibles:
            grille = copy.deepcopy(mc)
            grille = grille.generation()
            if grille:
                return grille


if __name__ == "__main__":

    mot_secret="BONNE ANNEE JESUS"
    if len(sys.argv) > 1:
        mot_secret=sys.argv[1].upper()

    gene = MotCroiseGenerator()
    gene.loadJson("mots_principaux.json")
    gene.loadJson("mots_complementaires.json")
    gene.setMessage(mot_secret)
    mc = gene.generate(25)

    if mc.identifyLettresMessage():
        print("Lettre OK")
    print(mc.msg_positions)
    mc.print()
