import sys
import json
import copy
import time
import os

class GrilleNotFoundException(Exception):
    pass

class GrilleTimeoutException(Exception):
    pass

class MotCroise:

    def __init__(self, grille_yx, mots_possibles, message, nb_mot=0):
        self.grille_yx = grille_yx.copy()
        self.grille_taille = len(grille_yx)
        self.mots = mots_possibles.copy()
        self.definitions = {}
        self.message = message
        self.msg_positions = []
        self.msg_mot_id = {}
        self.mots_selectionnes = []
        self.mots_nb = nb_mot
        self.score = -1
        self.nb_lettres_found = 0
        self.score_matrix = [0] * len(self.message)
        self.iteration_nb = 0
        self.profondeur = 0
        self.initScoreMatrix()

    def initScoreMatrix(self):
        x = 0
        min_y = 0
        mots = self.message.split( )
        for mot in mots:
            max_y = min_y + int(self.grille_taille / (len(mots) + 1))
            min_x = 0
            for lettre in list(mot):
                max_x = min_x + int(self.grille_taille / (len(mot) + 1))
                self.score_matrix[x] = [min_x, max_x, min_y, max_y]
                min_x = max_x + 1
                x += 1
            x += 1
            min_y = max_y + 2

    def addDefinition(self, definitions):
        self.definitions = definitions

    def removeMot(self, mot):
        self.mots.remove(mot)

    def setPositionMot(self, mot, position_x, position_y, orientation):
        self.mots_selectionnes.append([position_y * self.grille_taille + position_x, mot, position_x, position_y])
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
        return self.score / (len(self.message) * 50)

    def identifyLettresMessage(self, is_premier=False, debug=False):
        lettres = list(self.message)
        self.score = 0
        self.nb_lettres_found = 0
        self.msg_positions = []
        self.msg_mot_id = {}
        debut = 0
        lettre_id = -1
        mot_id = 1
        if (is_premier):
            lettre_id = int(len(lettres)/2) - 2
            lettres = lettres[int(len(lettres)/2) - 1:]
        l = 'X'
        while (l):
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
                        mot_id += 1
                        lettre_id += 1
                        self.nb_lettres_found += 1
                        debut = 0
                        break
                    if self.grille_yx[y][x] == ' ':
                        continue
                    if l == self.grille_yx[y][x]:
                        self.msg_positions.append([x, y])
                        self.msg_mot_id[(x, y)] = mot_id
                        (min_x, max_x, min_y, max_y) = self.score_matrix[lettre_id]
                        score_to_add = 0
                        if min_x <= x and max_x >= x and min_y <= y and max_y >= y:
                            score_to_add += self.grille_taille * 2
                        else:
                            diff = 0
                            if min_x <= x and max_x >= x:
                                if max_y < y:
                                    diff += y - max_y
                                if min_y > y:
                                    diff += min_y - y
                            if min_y <= y and max_y >= y:
                                if max_x < x:
                                    diff += x - max_x
                                if min_x > x:
                                    diff += min_x - x
                            score_to_add += int(self.grille_taille / 2) - diff
                        score_penalite = 0
                        for a in [x-1, x+1]:
                            if [a,y] in self.msg_positions:
                                score_penalite -= score_to_add
                        for b in [y-1, y+1]:
                            if [x,b] in self.msg_positions:
                                score_penalite -= score_to_add
                        self.score += score_to_add + score_penalite
                        if debug:
                            print({'lettre': l, 'min_x': min_x, 'x': x, 'max_x': max_x, 'min_y': min_y, 'y': y, 'max_y': max_y, 'score_to_add': score_to_add, 'score_penalite': score_penalite, 'score': self.score})
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
        print("  " + str(self.getScore(is_premier)) +" " + str(len(self.message)) + " " + str(self.iteration_nb) + "["+self.message+"]")
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

    def generation(mot_croise, ttl=5, iteration=0):

        if ttl < 1:
            return (mot_croise, mot_croise.iteration_nb)

        un_mot_croise = copy.deepcopy(mot_croise)
        un_mot_croise.profondeur += 1
        un_mot_croise.iteration_nb = iteration

        if (un_mot_croise.profondeur > len(un_mot_croise.message)):
            return (None, un_mot_croise.iteration_nb)
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
                                positions_mot.append([copy.deepcopy(new_mc), score])
            positions_mot.sort(key=lambda x: x[1], reverse=True)
            i = 0
            for (new_mc, score) in positions_mot:
                if new_mc.identifyLettresMessage():
                    return (new_mc, new_mc.iteration_nb)
                (new_mc, ite) = MotCroise.generation(new_mc, ttl - 1, un_mot_croise.iteration_nb+1)
                un_mot_croise.iteration_nb = ite
                if not (un_mot_croise.iteration_nb % 50) and (un_mot_croise.profondeur > 5):
                    return (None, un_mot_croise.iteration_nb)
                if new_mc:
                    return (new_mc, new_mc.iteration_nb)
                if i > len(positions_mot) / 2:
                    break;
        return (None, un_mot_croise.iteration_nb)

    def exportGrilleToSvg(self, filename):
        cellule_taille = 50
        margin = 50
        global_size = self.grille_taille * cellule_taille + 2 * margin

        svg_content = f'''<?xml version="1.0" encoding="UTF-8" standalone="no"?>
        <svg width="{global_size}" height="{global_size + 50}" xmlns="http://www.w3.org/2000/svg">
            <style>
                .cell {{ stroke: black; stroke-width: 1; fill: white; }}
                .black {{ fill: #333; }}
                .letter {{ font-family: Arial; font-size: 28px; font-weight: bold; text-anchor: middle; }}
                // .secret {{ fill: #FF6B00; }}
                .mot1 {{ fill: red; }}
                .mot2 {{ fill: blue; }}
                .mot3 {{ fill: green; }}
                .mot4 {{ fill: orange; }}
                .mot5 {{ fill: pink; }}
                .normal {{ fill: white; }}
                .number {{ font-family: Arial; font-size: 12px; fill: #666; }}
                .title {{ font-family: Arial; font-size: 24px; font-weight: bold; text-anchor: middle; }}
            </style>

            <text x="{global_size/2}" y="30" class="title">Mots Croisés</text>
        '''

        numeros_mots = {}
        self.mots_selectionnes.sort(key=lambda x:x[0])
        for i in range(len(self.mots_selectionnes)):
            numeros_mots[(self.mots_selectionnes[i][2], self.mots_selectionnes[i][3])] = i + 1

        # Dessiner la grille
        for gx in range(self.grille_taille):
            for gy in range(self.grille_taille):
                x = margin + gx * cellule_taille
                y = margin + gy * cellule_taille + 40  # Décalage pour le titre
                cellule = self.grille_yx[gy][gx]
                est_lettre_secrete = [gx, gy] in self.msg_positions

                # Case
                cell_class = "cell black" if cellule == ' ' else "cell"
                svg_content += f'    <rect x="{x}" y="{y}" width="{cellule_taille}" height="{cellule_taille}" class="{cell_class}"/>\n'

                if cellule != ' ':
                    # Numéro
                    if (gx, gy) in numeros_mots:
                        num = numeros_mots[(gx, gy)]
                        svg_content += f'    <text x="{x + 5}" y="{y + 15}" class="number">{num}</text>\n'

                    # Lettre
                    letter_x = x + cellule_taille / 2
                    letter_y = y + cellule_taille / 2 + 10
                    letter_class = "letter secret mot"+str(self.msg_mot_id[(gx, gy)]) if est_lettre_secrete else "letter normal"
                    svg_content += f'    <text x="{letter_x}" y="{letter_y}" class="{letter_class}">{cellule}</text>\n'

        # Légende
        svg_content += '</svg>'

        with open(filename, 'w', encoding='utf-8') as f:
            f.write(svg_content)

    def exportDefinitionToJSON(self, filename):
        self.mots_selectionnes.sort(key=lambda x:x[0])
        json_data = []
        for i in range(len(self.mots_selectionnes)):
            json_data.append({'mot_id': i, 'mot': self.mots_selectionnes[i][1], 'definition': self.definitions.get(self.mots_selectionnes[i][1], "ma définition")})
        with open(filename, 'w') as f:
            json.dump(json_data, f)

class MotCroiseGenerator:

    def __init__(self):
        self.mots = []
        self.message = ""
        self.mots_message = []
        self.definitions = {}
        self.start_time = 0
        self.end_time =  0


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
                    self.definitions[mot] = definition
                    break;

    def generate(self, taille):
        grille_yx = []
        self.start_time = time.time()
        self.end_time = 0
        for x in range(taille):
            grille_yx.append([' ' for y in range(taille)])

        self.mots_message.sort(key=lambda s: len(s), reverse=True)

        empty_mot_croise = MotCroise(grille_yx, self.mots_message, self.message)
        premier_mot_possibles = []
        for premier_mot in self.mots_message:
            mc = copy.deepcopy(empty_mot_croise)
            mc.setPositionMot(premier_mot, int(taille / 2) - int (len(premier_mot) / 2), int(taille / 2), 'H')
            mc.removeMot(premier_mot)
            premier_mot_possibles.append([copy.deepcopy(mc), 0])

        premier_mot_possibles.sort(key=lambda x: x[0].getScore(True), reverse=True)

        pas = 10
        for i in range (0, len(premier_mot_possibles), pas):
            generations = premier_mot_possibles[i:i+pas-1]

            premiere_passe = 0
            while len(generations):
                new_generations = []
                for (grille, ite) in generations:
                    (grille, i) = grille.generation(3, ite)
                    if grille:
                        if grille.identifyLettresMessage() and grille.getScore() > 0.65:
                            grille.addDefinition(self.definitions)
                            self.end_time = time.time()
                            return grille

                        new_generations.append([grille, i])

                new_generations.sort(key=lambda x: x[0].getScore(), reverse=True)
                generations = new_generations[:pas - premiere_passe * int(pas / 10)]
                premiere_passe = 1
                if self.getExecutionTime() > 1:
                    print(['Timeout', taille, (generations[0][0].identifyLettresMessage()), generations[0][0].getScore()])
                    raise GrilleTimeoutException()
        raise GrilleNotFoundException()

    def getExecutionTime(self):
        end = self.end_time
        if not end:
            end = time.time()
        return (end - self.start_time) / 60


if __name__ == "__main__":

    mot_secret="BONNE ANNEE JESUS"
    file_prefixe = ''
    if len(sys.argv) > 2:
        file_prefixe=sys.argv[2].upper()
    if len(sys.argv) > 1:
        mot_secret=sys.argv[1].upper()

    gene = MotCroiseGenerator()
    gene.loadJson("mots_principaux.json")
    gene.loadJson("mots_complementaires.json")
    gene.setMessage(mot_secret)

    mc = None
    size = 25
    while (not mc):
        try:
            mc = gene.generate(size)
        except GrilleNotFoundException:
            print(["Not found"])
            mc = None
        except GrilleTimeoutException:
            print(["Timeout", gene.getExecutionTime()])
            mc = None
        size += 1

    print([mot_secret, mc.getScore()])

    mc.exportGrilleToSvg(file_prefixe +"grille.svg")
    mc.exportDefinitionToJSON(file_prefixe +"grille_mots_definitions.json")
