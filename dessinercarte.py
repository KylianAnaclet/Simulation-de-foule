import tkinter as tk
from tkinter import ttk
import tkiteasy
import simulation

class FenetreDessin(tk.Toplevel):
    
    col_ui={"gris foncé 1":"#18222D", "gris foncé 2": "#1E2A37",
                 "gris 1":"#475363", "gris 2":"#536173", "gris 3":"#606F82", 
                 "gris 4":"#617084", "vert 1":"#348A31", "vert 2":"#3B9738", 
                 "vert 3":"#46A543", "gris obs":"#7B98B6"}
    
    couleurs_persos=["yellow","blue","green","red"]
    
    def __init__(self,master):
        
        super().__init__(master)
        self.master = master
        self.title("Créateur de cartes")
        self["bg"] = self.col_ui["gris foncé 1"]
        self.geometry("1000x660")
        self.focus_force()
        
        #caractéristiques carte
        self.carte_obs = set()
        self.carte_persos = []
        self.dimensions = (60,80)
        
        #pour le canevas
        self.canevas_obj = {} #contient les obj graphiques des perso et obstacles indexés par leur position
        self.grille = set() #contient les obj graphiques de la grille et du fond
        
        #est-ce que'on est en mode "placer des personnages" ou pas
        self.mode_persos = False
        
        #########################################################################
        #MENU (en haut)
        #########################################################################
        
        menu = tk.Frame(self, bg=self.col_ui["gris 1"], highlightthickness=0,
                        height=50)
        menu.pack(side=tk.TOP, fill=tk.X)
        
        bouton1 = ttk.Button(menu, style="M.TButton",text="Nouveau", 
                             takefocus=False, command=self.nouvelleCarte)
        bouton2 = ttk.Button(menu, style="M.TButton", text="Ouvrir", 
                             takefocus=False, command=self.ouvrirCarte)
        bouton3 = ttk.Button(menu, style="M.TButton", text="Enregistrer sous",
                             takefocus=False, command=self.enregistrerSous)
        bouton4 = ttk.Button(menu, style="M.TButton", text="Redimensionner", 
                             takefocus=False, command=self.redimensionner)
        bouton5 = ttk.Button(menu, style="M.TButton", text="Lancer la simulation",
                             takefocus=False, command=self.demarrerSim)
        
        bouton1.pack(side=tk.LEFT)
        bouton2.pack(side=tk.LEFT)
        bouton3.pack(side=tk.LEFT)
        bouton4.pack(side=tk.LEFT)
        bouton5.pack(side=tk.LEFT)
        
        self.bind("<Return>", lambda event: self.demarrerSim())
        
        
        
        frame_droite = tk.Frame(self, bg=self.col_ui["gris foncé 2"],
                                highlightthickness=1, highlightcolor=self.col_ui["gris 1"],
                                highlightbackground=self.col_ui["gris 1"])
        frame_droite.pack(side=tk.RIGHT, fill=tk.Y, padx=[0,10], pady=10)
        
        self.bouton = ttk.Button(frame_droite, text="Placer personnages", takefocus=False, command=self.commandeBouton)
        self.bouton.pack(side=tk.TOP, padx=10, pady=15)
        
        lab_choix_couleurs = tk.Label(frame_droite, text="Couleur du personnage",
                                      bg=self.col_ui["gris foncé 2"], fg="white")
        lab_choix_couleurs.pack(side=tk.TOP, padx=10)
        
        self.choix_couleurs = ttk.Combobox(frame_droite, state="readonly")
        self.choix_couleurs["values"] = ["jaune","bleu","vert","rouge"]
        self.choix_couleurs.set("jaune")
        self.choix_couleurs.pack(side=tk.TOP, fill=tk.X, padx=10, pady=10)
        

        
        #########################################################################
        #CANEVAS
        #########################################################################
        
        bordures_canevas = tk.Frame(self, bg=self.col_ui["gris 1"])
        bordures_canevas.pack(expand=True, padx=10, pady=10)
        
        self.canevas = tkiteasy.Canevas(bordures_canevas, 800, 600)
        self.canevas.configure(highlightthickness=0)
        self.canevas.pack(expand=True, padx=1, pady=1)
        self.canevas.bind("<Button-3>", self.gomme)
        self.canevas.bind("<Button-1>", self.dessinerObstacles)
        
        #on dessine le fond et la grille
        self.grille.add(self.canevas.dessinerRectangle(0,0,800,600,self.col_ui["gris foncé 2"]))

        for i in range(10,800,10):
            self.grille.add(self.canevas.dessinerLigne(i,0,i,600,"#2F3B4A"))
            
        for i in range(10,800,10):
            self.grille.add(self.canevas.dessinerLigne(0,i,800,i,"#2F3B4A"))
            
        self.canevas.actualiser()

    #############################################################################
    #METHODES MENU
    #############################################################################

    def nouvelleCarte(self):
        self.importerCartes("Aucun obstacle", "Aucun personnage")
        self.updateCanevas()
        
    def ouvrirCarte(self):
        fenetre = FenetreOuvrirCarte(self)
        fenetre.grab_set()
        
    def enregistrerSous(self):
        fenetre = FenetreEnregistrer(self)
        fenetre.grab_set()
    
    def redimensionner(self):
        fenetre = FenetreRedimensionner(self)
        fenetre.grab_set()
        
    def demarrerSim(self):
        self.mode_persos = False
        fenetre_sim = simulation.FenetreSimulation(self, self.carte_obs, self.carte_persos,
                                                   1, self.dimensions)
        fenetre_sim.grab_set()
        self.canevas.bind_all("<Key>", self.canevas.evenementClavier)
    
    
    #############################################################################
    #METHODES DESSIN
    #############################################################################
    
    def dessinerObstacles(self, event):
        if self.canevas.recupererFinClic() == None:
            pos = self.canevas.recupererPosition()
            pos_l = pos.y //10
            pos_c = pos.x //10
            pos = (pos_l, pos_c)
            
            if self.estDansPlateau(pos) and pos not in self.canevas_obj:
                rect = self.canevas.dessinerRectangle(pos_c*10 +1,pos_l*10 +1, 9, 9,
                                                      self.col_ui["gris obs"])
                self.canevas_obj[pos] = rect
                self.carte_obs.add(pos)
            
            self.canevas.after(1, lambda: self.dessinerObstacles("<Button-1>"))
            
    def commandeBouton(self):
        self.mode_persos = not self.mode_persos
        
        if self.mode_persos:
            self.bouton.configure(text="   Placer obstacles   ")
            self.canevas.unbind("<Button-1>")
            self.canevas.bind("<Button-1>", self.canevas.evenementClicG)
            self.dessinerPersonnages()
        else:
            self.bouton.configure(text="Placer personnages")
            self.canevas.unbind("<Button-1>")
            self.canevas.bind("<Button-1>", self.dessinerObstacles)
            
            
    def dessinerPersonnages(self, pt_depart=None, pt_arrivee=None, pt_depart_en_place=False, pt_arrivee_en_place=False, case_depart=None, case_arrivee=None, col_perso="yellow"):
        if self.mode_persos:
            clic = self.canevas.recupererClicG()
            touche = self.canevas.recupererTouche()
            
            if touche == "space" and pt_depart_en_place and pt_arrivee_en_place:
                self.canevas.supprimer(case_arrivee)
                self.canevas_obj[pt_depart] = case_depart
                self.carte_persos.append((pt_depart,pt_arrivee,col_perso))
                
                pt_depart = None
                pt_arrivee = None
                pt_depart_en_place = False
                pt_arrivee_en_place = False
                case_depart = None
                case_arrivee = None
                
            
            if clic != None:
                
                clic_l = clic.y //10
                clic_c = clic.x //10
                
                if not pt_depart_en_place :
                    if (clic_l,clic_c) not in self.carte_obs and self.estDansPlateau((clic_l,clic_c)):
                        col_perso = self.choix_couleurs.current()
                        col_perso = self.couleurs_persos[self.choix_couleurs.current()]
                        case_depart = self.canevas.dessinerRectangle(clic_c*10 +1,
                                                                     clic_l*10 +1, 
                                                                     9, 9, 
                                                                     col_perso)
                        pt_depart = (clic_l,clic_c)
                        pt_depart_en_place = True
                
                elif not pt_arrivee_en_place :
                    if (clic_l,clic_c) not in self.carte_obs and self.estDansPlateau((clic_l,clic_c)):
                        case_arrivee = self.canevas.dessinerRectangle(clic_c*10 +1,
                                                                      clic_l*10 +1,
                                                                      9, 9, "white")
                        pt_arrivee = (clic_l,clic_c)
                        pt_arrivee_en_place = True
                    
                else:
                    pt_depart_en_place = False
                    pt_arrivee_en_place = False
                    self.canevas.supprimer(case_depart)
                    self.canevas.supprimer(case_arrivee)
            
            self.canevas.after(1, lambda: 
                               self.dessinerPersonnages(pt_depart, pt_arrivee, 
                                                        pt_depart_en_place, 
                                                        pt_arrivee_en_place,
                                                        case_depart, case_arrivee,
                                                        col_perso))
        
        else:
            try: self.canevas.supprimer(case_depart)
            except: pass
            try: self.canevas.supprimer(case_arrivee)
            except: pass
            self.canevas.recupererFinClic() #pour etre sur que lastfinclic = None
            
    def gomme(self, event):
        finclic = self.canevas.recupererFinClic()
        if finclic == None:
            pos = self.canevas.recupererPosition()
            pos_l = pos.y //10
            pos_c = pos.x //10
            pos = (pos_l, pos_c)
            
            if pos in self.canevas_obj:
                self.canevas.supprimer(self.canevas_obj[pos])
                self.canevas_obj.pop(pos)
            
            if pos in self.carte_obs:
                self.carte_obs.remove(pos)
            
            persos_a_enlever = []
            for perso in self.carte_persos:
                if perso[0] == pos:
                    persos_a_enlever.append(perso)
            for perso in persos_a_enlever:
                self.carte_persos.remove(perso)
            
            self.canevas.after(1, lambda: self.gomme("<Button-3>"))
    
    
    ############################################################################
    #LE RESTE
    ############################################################################      
    
    def importerCartes(self,fichier_obs, fichier_persos):  
        #carte obstacles
        self.carte_obs.clear()
        with open(f"data/cartes obstacles/{fichier_obs}","r") as f:
            entete = f.readline().split(" ")
            largeur = int(entete[0])
            longueur = int(entete[1])
            
            for l in range(longueur):
                ligne = f.readline()
                ligne = list(ligne)
                for c in range(largeur):
                    if ligne[c] == "*":
                        self.carte_obs.add((l,c))
        
        self.dimensions = (longueur,largeur)
    
        #carte personnages
        self.carte_persos.clear()
        nb_persos = 0
        with open(f"data/cartes personnages/{fichier_persos}","r") as f:
            nb_persos = int(f.readline())
            
            for i in range(nb_persos):
                ligne = f.readline().strip().split(" ")
                dl = int(ligne[1])
                dc = int(ligne[0])
                al = int(ligne[3])
                ac = int(ligne[2])
                pos_depart = (dl,dc)
                pos_arrivee = (al,ac)
                col = self.couleurs_persos[int(ligne[4])]
                self.carte_persos.append((pos_depart, pos_arrivee, col))
                
    def updateCanevas(self):
        if self.dimensions != (int(self.canevas["height"])//10, int(self.canevas["width"])//10):
            longueur = self.dimensions[0]*10
            largeur = self.dimensions[1]*10
            
            for obj in self.grille:
                self.canevas.supprimer(obj)
            self.grille.clear()
            
            self.canevas.configure(width=largeur, height=longueur)
            
            self.grille.add(self.canevas.dessinerRectangle(0,0,largeur,longueur,
                                                           self.col_ui["gris foncé 2"]))
            
            for i in range(0,largeur,10):
                self.grille.add(self.canevas.dessinerLigne(i,0,i,longueur,"#2F3B4A"))
            for i in range(0,longueur,10):
                self.grille.add(self.canevas.dessinerLigne(0,i,largeur,i,"#2F3B4A"))
        
        #on supprime les objets graphiques
        for obj in self.canevas_obj.values():
            self.canevas.supprimer(obj)
        self.canevas_obj.clear()
        
        #obstacles
        for pos in self.carte_obs:
            l = pos[0]
            c= pos[1]
            self.canevas_obj[(l,c)]=self.canevas.dessinerRectangle(c*10 +1, l*10 +1,
                                                                   9, 9, 
                                                                   self.col_ui["gris obs"])
        #personnages        
        for infos in self.carte_persos:
            dl = infos[0][0]
            dc = infos[0][1]
            al = infos[1][0]
            ac = infos[1][1]
            col = infos[2]
            if (dl,dc) in self.carte_obs or (al,ac) in self.carte_obs:
                pass
            elif not self.estDansPlateau((dl,dc)) or not self.estDansPlateau((al,ac)):
                pass
            elif (dl,dc) not in self.canevas_obj:
                self.canevas_obj[(dl,dc)]=self.canevas.dessinerRectangle(dc*10 +1, 
                                                                         dl*10 +1,
                                                                         9, 9, col)
        self.canevas.update() 

    def estDansPlateau(self,pos):
        if 0 <= pos[0] < self.dimensions[0] and 0 <= pos[1] < self.dimensions[1]:
            return True
        else:
            return False           


################################################################################
#FENETRE "OUVRIR CARTE"
################################################################################        

class FenetreOuvrirCarte(tk.Toplevel):
    
    def __init__(self, master):
        super().__init__(master)
        self.title("Ouvrir")
        self["bg"] = master.col_ui["gris foncé 1"]
        self.resizable(False, False)
        self.master = master
        self.focus_force()
        
        self.bind("<Return>", lambda event: self.confirmer())
        
        #combobox cartes obstacles
        self.comboboxO = ttk.Combobox(self, state="readonly")
        
        with open("data/liste cartes obstacles","r") as f:
            options = []
            nb_cartes = int(f.readline())
            for i in range(nb_cartes):
                options.append(f.readline().strip())
                
        self.comboboxO["values"] = options
        self.comboboxO.set("Aucun obstacle")
        
        #combobox cartes personnages
        self.comboboxP = ttk.Combobox(self, state="readonly")
        
        with open("data/liste cartes personnages","r") as f:
            options = []
            nb_cartes = int(f.readline())
            for i in range(nb_cartes):
                options.append(f.readline().strip())
        
        self.comboboxP["values"] = options
        self.comboboxP.set("Aucun personnage")
        
        #labels
        self.lab_obs = tk.Label(self, text="Carte obstacles :", relief="flat",
                              bg=self.master.col_ui["gris foncé 1"], fg="white")
        self.lab_persos = tk.Label(self, text="Carte personnages :", relief="flat",
                              bg=self.master.col_ui["gris foncé 1"], fg="white")
        
        self.lab_obs.pack(expand=True, pady=[10,0])
        self.comboboxO.pack(expand=True, pady=[0,10])
        self.lab_persos.pack(expand=True)
        self.comboboxP.pack(expand=True, pady=[0,10])
        
        #boutons "annuler" et "confirmer"
        bouton_annuler = ttk.Button(self, text="Annuler", takefocus=False,
                                    command=self.destroy, style="M.TButton")
        bouton_confirmer = ttk.Button(self, text="Confirmer", takefocus=False,
                                      command=self.confirmer, style="M.TButton")
        
        bouton_annuler.pack(side=tk.LEFT, padx=10, pady=10)
        bouton_confirmer.pack(side=tk.RIGHT, padx=10, pady=10)
        
        
    def confirmer(self):
        fichier_obs = self.comboboxO.get()
        fichier_persos = self.comboboxP.get()
        self.master.importerCartes(fichier_obs, fichier_persos)
        self.master.updateCanevas()
        self.destroy()        


################################################################################
#FENETRE "ENREGISTRER SOUS"
################################################################################

class FenetreEnregistrer(tk.Toplevel):

    def __init__(self, master):
        super().__init__(master)
        self.title("Enregistrer sous")
        self["bg"] = master.col_ui["gris foncé 1"]
        self.resizable(False, False)
        self.master = master
        self.focus_force()
        
        self.bind("<Return>", lambda event: self.confirmer())

        #labels
        self.lab_obs = tk.Label(self, text="Nom carte obstacles :", relief="flat",
                              bg=self.master.col_ui["gris foncé 1"], fg="white")
        self.lab_persos = tk.Label(self, text="Nom carte personnages :", relief="flat",
                              bg=self.master.col_ui["gris foncé 1"], fg="white")
        
        #entrées
        self.entry_obs = tk.Entry(self, bg=self.master.col_ui["gris 2"], fg="white", relief="flat")
        self.entry_persos = tk.Entry(self, bg=self.master.col_ui["gris 2"], fg="white", relief="flat")

        self.lab_obs.pack(expand=True, pady=[10,0])
        self.entry_obs.pack(expand=True, pady=[0,10])
        self.lab_persos.pack(expand=True)
        self.entry_persos.pack(expand=True, pady=[0,10])

        #boutons "annuler" et "confirmer"
        bouton_annuler = ttk.Button(self, text="Annuler", takefocus=False,
                                    command=self.destroy, style="M.TButton")
        bouton_confirmer = ttk.Button(self, text="Confirmer", takefocus=False,
                                      command=self.confirmer, style="M.TButton")
        
        bouton_annuler.pack(side=tk.LEFT, padx=10, pady=10)
        bouton_confirmer.pack(side=tk.RIGHT, padx=10, pady=10)
        
        
    def enregistrerCarte(self):
        filename_obs = self.entry_obs.get().strip()
        filename_persos = self.entry_persos.get().strip()
        
        #on crée le fichier obstacles
        with open(f"data/cartes obstacles/{filename_obs}","w") as f:
            longueur = self.master.dimensions[0]
            largeur = self.master.dimensions[1]
            f.write(f"{largeur} {longueur}\n")
            for l in range(longueur):
                for c in range(largeur):
                    if (l,c) in self.master.carte_obs:
                        f.write("*")
                    else:
                        f.write("_")
                f.write("\n")
        
        #on crée le fichier personnage
        with open(f"data/cartes personnages/{filename_persos}","w") as f:
            nb_persos = len(self.master.carte_persos)
            f.write(f"{nb_persos}\n")
            for perso in self.master.carte_persos:
                dl = perso[0][0]
                dc = perso[0][1]
                al = perso[1][0]
                ac = perso[1][1]
                col = self.master.couleurs_persos.index(perso[2])
                f.write(f"{dc} {dl} {ac} {al} {col}\n")
        
        #on ajoute les cartes aux listes des cartes
        for i in ["obstacles","personnages"]:
            with open(f"data/liste cartes {i}","r") as f:
                nb_cartes = int(f.readline())
                f.seek(0)
                data = f.read()
                data = data.replace(str(nb_cartes),str(nb_cartes +1))
            
            with open(f"data/liste cartes {i}","w") as f:
                f.write(data)
                if i == "obstacles":
                    f.write(f"{filename_obs}\n")
                else:
                    f.write(f"{filename_persos}\n")
                    
        #on ajoute les cartes aux listbox de la  fenetre principale
        self.master.master.listeO.insert(tk.END, filename_obs)
        self.master.master.listeP.insert(tk.END, filename_persos)
            
        
    
    def confirmer(self):
        try: self.enregistrerCarte()
        except: print("Erreur")
        else: self.destroy()
            
        
################################################################################
#FENETRE "REDIMENSIONNER"
################################################################################

class FenetreRedimensionner(tk.Toplevel):
    
    def __init__(self, master):
        super().__init__(master)
        self.title("Redimensionner")
        self["bg"] = master.col_ui["gris foncé 1"]
        self.resizable(False, False)
        self.master = master
        self.focus_force()
        
        self.bind("<Return>", lambda event: self.confirmer())
        
        #labels
        self.lab_l = tk.Label(self, text="Nombre de lignes :",
                              bg=self.master.col_ui["gris foncé 1"], fg="white", relief="flat")
        self.lab_c = tk.Label(self, text="Nombre de colonnes :",
                              bg=self.master.col_ui["gris foncé 1"], fg="white", relief="flat")
        
        #entrées
        self.entry_l = tk.Entry(self, bg=self.master.col_ui["gris 2"], fg="white", relief="flat")
        self.entry_c = tk.Entry(self, bg=self.master.col_ui["gris 2"], fg="white", relief="flat")
        
        
        self.lab_l.pack(expand=True, pady=[10,0])
        self.entry_l.pack(expand=True, pady=[0,10])
        self.lab_c.pack(expand=True)
        self.entry_c.pack(expand=True, pady=[0,10])
        
        #boutons "annuler" et "confirmer"
        bouton_annuler = ttk.Button(self, text="Annuler", takefocus=False,
                                    command=self.destroy, style="M.TButton")
        bouton_confirmer = ttk.Button(self, text="Confirmer", takefocus=False,
                                      command=self.confirmer, style="M.TButton")
        
        bouton_annuler.pack(side=tk.LEFT, padx=10, pady=10)
        bouton_confirmer.pack(side=tk.RIGHT, padx=10, pady=10)
        
        
    def confirmer(self):
        try: 
            l = int(self.entry_l.get())
            c = int(self.entry_c.get())
        except ValueError:
            print("entrez un nombre entier svp")
        else:
            self.master.dimensions = (l,c)
            self.master.updateCanevas()
        self.destroy()

        
