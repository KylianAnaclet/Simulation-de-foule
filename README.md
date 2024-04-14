Le programme est découpé en trois fichiers:

1 - main.py
C'est ici que se trouve le menu principal. A gauche, il y a un notebook avec deux onglets : le premier permet de 
sélectionner le fichier (qu'on appelle "carte") obstacles et l'autre le fichier personnages que l'utilisateur 
souhaite utiliser. Ce seront les données utilisées pour la simulation. Les cartes sont dans 
le dossier data. Il y a deux fichiers "liste cartes personnages" et "liste cartes obstacles" dans lesquels 
se trouve les noms des cartes enregistrées. Il y a deux boutons par onglet. Le premier permet de supprimer une 
carte. L'autre d'ajouter une carte à la liste.

En bas, une frame avec des infos diverses sur les cartes sélectionnées, l'option de changer la vitesse de 
la simulation et deux boutons. Le premier permet de lancer la simulation directement (appelle simulation.py)
avec les données sélectionnées, l'autre de lancer une autre fenêtre pour dessiner une carte à la souris.

En haut à gauche, un aperçu des cartes sélectionnées.

2 - fenetredessin.py
permet de dessiner une carte à la souris.
-(maintenir) Clic gauche pour effacer
-(maintenir) Clic droit pour poser des obstacles
-appuyer sur le bouton à droite pour passer en mode 'poser des obstacles' : premier clic pose le départ, deuxième
l'arrivée, le troisième annule tout, et appuyer sur espace confirme.

plusieurs options dans le menu en haut:
-Nouvelle carte : met une carte vide
-ouvrir : permet d'ouvrir pour modifier une carte existante
-enregistrer sous : enregistre la carte dessinée
-redimensionner 
-lancer la simulation (appelle simulation.py)

3 - simulation.py
lance la simulation. plusieurs options :
-mettre en pause en appuyant sur le bouton ou la touche espace
-poser des murs en temps réel avec clic gauche
-effacer des murs en temps réel avec clic droit
-régler la vitesse en temps réel

comment ça marche ?
la simulation prend en entrée un set qui contient les positions des murs et une liste qui contient un tuple par perso
(pos depart, pos arrivée, couleur). Pour chaque élément de ces structures, on crée un obstacle/perso.
Les personnages sont des instances de la classe Personnage. Attributs de classe : un annuaire qui contient tous
les persos crées, et un dico des positions occupées par les persos avec le nombre de persos par position.
La simulation consiste en une boucle qui appelle la méthode "déplacer" pour chaque personnage.
Pour se déplacer, ils regardent autour d'eux les cases libres de leur voisinage, puis ils choisissent pour leur
prochain déplacement la case la plus proche de leur destination. Ils ont chacun une liste de leurs positions 
précédentes qu'ils utilisent pour ne pas revenir sur leurs pas. Lorsqu'ils sont coincés (aucune options de 
déplacements) ils vident leur liste de positions précédentes.
