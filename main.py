import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
import simulation
import dessinercarte

class FenetrePrincipale(tk.Tk):
    
    col_ui={"gris foncé 1":"#18222D", "gris foncé 2": "#1E2A37",
                 "gris 1":"#475363", "gris 2":"#536173", "gris 3":"#606F82", 
                 "gris 4":"#5D6B7E", "vert 1":"#348A31", "vert 2":"#3B9738", 
                 "vert 3":"#46A543"}
    couleurs_persos=["yellow","blue","green","red"]
    
    def __init__(self):
        
        #on génère la fenêtre
        super().__init__() #on appelle le constructeur parent
        self.geometry("800x600")
        self.title("Simulateur de foules")
        self["bg"] = self.col_ui["gris foncé 1"]
        self.focus_force()
        
        #configure les styles des boutons, scale, et notebook
        self.configStyles()
        
        #la carte qui va être utilisée pour la simulation constituée d'un set qui
        #contient les positions des murs et d'une liste qui contient les infos
        #(pos départ, pos arrivée, couleur) de chaque personnage. C'est la
        #carte sélectionnée par l'utilisateur
        self.carte_obs = set()
        self.carte_persos = []
        self.vitesse = 1
        self.dimensions = (60,80)
        

        self.text_lab1 = tk.StringVar(value="Nombre d'obstacles : 0")
        self.text_lab2 = tk.StringVar(value="Nombre de personnages : 0")
        self.text_lab3 = tk.StringVar(value="Dimensions : 60l x 80c")
        self.text_lab_attention = tk.StringVar()
        self.text_lab_slider = tk.StringVar(value="Vitesse de la simulation :\n1")
        
        #dicos qui contiennent les sprites des murs et des joueurs dans la preview,
        #indicés par leur position. Si plusieurs persos ont la même position,
        #un seul sprite y est ajouté car inutile de prendre en compte le nombre
        #de persos sur une case pour un simple affichage.
        self.preview_obj = {}
        #contient les objets graphiques qui forment la grille dans la preview
        self.grille = set()
        
        
        #######################################################################
        #LE NOTEBOOK
        #######################################################################
        
        #le notebook en question
        bordures_notebook = tk.Frame(self, bg=self.col_ui["gris 1"])
        bordures_notebook.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)
        
        notebook = ttk.Notebook(bordures_notebook)
        notebook.pack(padx=1, pady=1, fill=tk.Y, expand=True)
        
        #onglets 1 et 2
        onglet1 = tk.Frame(notebook, bg=self.col_ui["gris foncé 2"], relief="flat", borderwidth=0)
        onglet2 = tk.Frame(notebook, bg=self.col_ui["gris foncé 2"], relief="flat", borderwidth=0)
        onglet1.pack(fill=tk.BOTH, expand=True)
        onglet2.pack(fill=tk.BOTH, expand=True)
       
        notebook.add(onglet1, text = "  Obstacles  ")
        notebook.add(onglet2, text = "Personnages")
        
        
        #widgets de l'onglet 1
        
        #listbox des cartes obstacles
        self.listeO = tk.Listbox(onglet1, bg=self.col_ui["gris foncé 2"], fg="white", relief="flat",
                        selectbackground=self.col_ui["gris 4"], highlightcolor=self.col_ui["gris 1"],
                        highlightbackground=self.col_ui["gris 1"], activestyle = "none",
                        selectmode="single", exportselection=0)
        self.listeO.pack(expand=True, fill=tk.BOTH, padx=20, pady=10)
        
        self.listeO.bind("<ButtonRelease>", self.selectionnerCarteObstacles)

        #on récupère dans la liste des cartes obstacles le contenu à mettre dans
        #la listbox
        with open("data/liste cartes obstacles","r") as f:
            options = []
            nb_cartes = int(f.readline())
            for i in range(nb_cartes):
                options.append(f.readline().strip())
        
        for i in options:
            self.listeO.insert(tk.END, i)
            
        #sélectionne la carte vide par défaut
        self.listeO.select_set(0)

        
        #les boutons "supprimer" et "importer"
        button1 = ttk.Button(onglet1, text="Importer de nouvelles données",
                            takefocus=False, command=self.nouvelleCarteObstacles)
        button1.pack(side=tk.BOTTOM, padx=20 ,pady=[10,15], fill=tk.X)
        
        
        button2 = ttk.Button(onglet1, text="Supprimer", takefocus=False, 
                             command=self.supprimerCarteObstacles)
        button2.pack(side=tk.BOTTOM, padx=20, pady=[10,0], fill=tk.X)
        
        
        #widgets de l'onglet 2
        
        #listbox des cartes personnages
        self.listeP = tk.Listbox(onglet2, bg=self.col_ui["gris foncé 2"], fg="white", relief="flat",
                        selectbackground=self.col_ui["gris 4"], highlightcolor=self.col_ui["gris 1"],
                        highlightbackground=self.col_ui["gris 1"], activestyle = "none",
                        selectmode="single", exportselection=0)
        self.listeP.pack(expand=True, fill=tk.BOTH, padx=20, pady=10)
        
        self.listeP.bind("<ButtonRelease>", self.selectionnerCartePersonnages)

        #on récupère dans la liste des cartes personnages le contenu à mettre dans
        #la listbox
        with open("data/liste cartes personnages","r") as f:
            options = []
            nb_cartes = int(f.readline())
            for i in range(nb_cartes):
                options.append(f.readline().strip())
        
        for i in options:
            self.listeP.insert(tk.END, i)
            
        #sélectionne la carte vide par défaut
        self.listeP.select_set(0)
        
        #boutons "supprimer" et "importer"
        button3 = ttk.Button(onglet2, text="Importer de nouvelles données",
                            takefocus=False, command=self.nouvelleCartePersonnages)
        button3.pack(side=tk.BOTTOM, padx=20 ,pady=[10,15], fill=tk.BOTH)
        
        button4 = ttk.Button(onglet2, text="Supprimer", takefocus=False,
                             command=self.supprimerCartePersonnages)
        button4.pack(side=tk.BOTTOM, padx=20, pady=[10,0], fill=tk.BOTH)
        
        
        
        #######################################################################
        #FRAME "INFOS"
        #######################################################################
        
        frame_infos = tk.Frame(self, bg=self.col_ui["gris foncé 2"], 
                              highlightthickness=1, highlightbackground=self.col_ui["gris 1"], 
                              highlightcolor=self.col_ui["gris 1"])
        frame_infos.pack(side=tk.BOTTOM, padx=[0,10], pady=10, fill=tk.X)
        
        subframe_gauche = tk.Frame(frame_infos, bg=self.col_ui["gris foncé 2"])
        subframe_milieu = tk.Frame(frame_infos, bg=self.col_ui["gris foncé 2"])
        subframe_droite = tk.Frame(frame_infos, bg=self.col_ui["gris foncé 2"])
        subframe_bas = tk.Frame(frame_infos, bg=self.col_ui["gris foncé 2"])
        
        subframe_droite.pack(side=tk.RIGHT, fill=tk.Y)
        subframe_bas.pack(side=tk.BOTTOM, fill=tk.BOTH, pady=[0,10])
        subframe_gauche.pack(side=tk.LEFT)
        subframe_milieu.pack(expand=True)
        
        
        #subframe droite (boutons "démarrer" et "dessiner carte")
        button5 = ttk.Button(subframe_droite, text="Démarrer la simulation",
                             style="Vert.TButton", takefocus=False,
                             command=self.demarrerSim)
        button5.pack(side=tk.BOTTOM, padx=10, pady=[0,15], fill=tk.X)
        
        button6 = ttk.Button(subframe_droite, text="Dessiner une carte à la souris", 
                             takefocus=False, command=self.dessinerCarte)
        button6.pack(side=tk.TOP, padx=10, pady=15, fill=tk.X)
        
        
        #subframe gauche (nb osbstacles, nb persos, dimensions)
        lab1 = tk.Label(subframe_gauche, textvariable=self.text_lab1,
                       fg="white", bg=self.col_ui["gris foncé 2"], relief="flat", 
                       padx=10, pady=5, anchor=tk.W, width=22)
        lab1.pack(anchor=tk.NW, pady=[10,0])
        
        lab2 = tk.Label(subframe_gauche, textvariable=self.text_lab2,
                       fg="white", bg=self.col_ui["gris foncé 2"], relief="flat", 
                       padx=10, pady=5, anchor=tk.W, width=22)
        lab2.pack(anchor=tk.W)
        
        lab3 = tk.Label(subframe_gauche, textvariable=self.text_lab3,
                       fg="white", bg=self.col_ui["gris foncé 2"], relief="flat", 
                       padx=10, pady=5, anchor=tk.W, width=22)
        lab3.pack(anchor=tk.SW)
        
        
        #subframe bas (label "attention")
        lab_attention = tk.Label(subframe_bas, textvariable=self.text_lab_attention,
                                 fg="#EC472D", bg=self.col_ui["gris foncé 2"], 
                                 relief="flat", padx=10, pady=5)
        lab_attention.pack(side=tk.LEFT)
        
        
        #subframe milieu (slider vitesse)
        bordures_slider = tk.Frame(subframe_milieu, bg=self.col_ui["gris 1"])
        
        self.slider = ttk.Scale(bordures_slider, from_=1, to=10, orient="horizontal",
                                command=self.recupererVitesse)
        
        lab_slider = tk.Label(subframe_milieu, textvariable=self.text_lab_slider,
                              fg="white", bg=self.col_ui["gris foncé 2"])
        
        lab_slider.pack(side=tk.TOP, pady=[20,0])
        bordures_slider.pack(expand=True, fill=tk.X)
        self.slider.pack(expand=True, fill=tk.BOTH, padx=1, pady=1)
        
        
        #######################################################################
        #PREVIEW
        #######################################################################
        
        fond_framepreview = tk.Frame(self, bg=self.col_ui["gris foncé 1"])
        fond_framepreview.pack(expand=True, fill=tk.BOTH)
        
        fond_framepreview.columnconfigure(0, weight=1)
        fond_framepreview.rowconfigure(0, weight=1)
        
        #on peut pas changer la couleur de la bordure d'un vrai labelframe sur
        #tkinter donc j'ai juste superposé un frame et un label...
        #c'est du bricolage
        framepreview = tk.Frame(fond_framepreview, bg=self.col_ui["gris foncé 1"],
                                highlightbackground=self.col_ui["gris 1"],
                                highlightcolor=self.col_ui["gris 1"],
                                highlightthickness=1)
        framepreview.grid(row=0, padx=[0,10], pady=[15,0], sticky = tk.NSEW)
        
        lab_preview = tk.Label(fond_framepreview, text="Aperçu de la carte sélectionnée" ,
                               bg=self.col_ui["gris foncé 1"], fg="white")
        lab_preview.grid(row=0, column=0, padx=10, pady=5, sticky=tk.NW)
        
        #la preview en elle-même (un canvas)
        bordures_preview = tk.Frame(framepreview, background=self.col_ui["gris 1"])
        bordures_preview.pack(expand=True)
        
        self.preview = tk.Canvas(bordures_preview, width=320, height=240, 
                                 bg=self.col_ui["gris foncé 2"], highlightthickness=0)
        self.preview.pack(expand=True, padx=1, pady=1)
        
        #on dessine la grille
        for i in range(0,320,4):
            self.grille.add(self.preview.create_line(i,0,i,300 , fill="#253444",
                                                     cap='round', width=1))
        for i in range(0,240,4):
            self.grille.add(self.preview.create_line(0,i,400,i, fill="#253444",
                                                     cap='round', width=1))
        
        self.preview.update()
        
    
    ###########################################################################
    #METHODES ONGLET 1
    ###########################################################################    
    
    def selectionnerCarteObstacles(self,event):
        selected_index = self.listeO.curselection()
        if selected_index:
            index = selected_index[0]
            selected_item = self.listeO.get(index)
            try: self.importerCarteObstacles(selected_item)
            except FileNotFoundError: print("le fichier n'existe pas")
            except IndexError: print("mauvais format")
            except: print("erreur")
            else:
                self.updatePreview()
    
    def importerCarteObstacles(self,fichier):   
        self.carte_obs.clear()
        nb_obs = 0
        with open(f"data/cartes obstacles/{fichier}","r") as f:
            entete = f.readline().split(" ")
            largeur = int(entete[0])
            longueur = int(entete[1])
            
            for l in range(longueur):
                ligne = f.readline()
                ligne = list(ligne)
                for c in range(largeur):
                    if ligne[c] == "*":
                        self.carte_obs.add((l,c))
                        nb_obs += 1
        
        self.dimensions = (longueur,largeur)
        self.text_lab1.set(f"Nombre d'obstacles : {nb_obs}") 
        self.text_lab3.set(f"Dimensions : {longueur}l x {largeur}c")
    
    #supprime une carte de la liste des cartes obs
    def supprimerCarteObstacles(self):
        #on récupère la carte sélectionnée (qui va donc être supprimée)
        selected_index = self.listeO.curselection()
        if selected_index and selected_index[0] != 0:
            index = selected_index[0]
            selected_item = self.listeO.get(index)
            
            #on supprime la carte de la liste des cartes obstacles
            with open("data/liste cartes obstacles","r") as f:
                nb_cartes = int(f.readline())
                f.seek(0)
                data = f.read()
                data = data.replace(str(nb_cartes),str(nb_cartes -1))
                data = data.replace(selected_item+"\n", "")
                
            with open("data/liste cartes obstacles","w") as f:
                f.write(data)
            
            #on supprime la carte de la listbox
            self.listeO.delete(index)
            #on sélectionne automatiquement la carte d'avant
            self.listeO.select_set(index-1)
            self.selectionnerCarteObstacles("<KeyRelease>")
            
    
    #ajoute la nouvelle carte choisie au fichier "liste cartes obstacles"
    def nouvelleCarteObstacles(self):
        filename = tk.filedialog.askopenfilename(
                                         title="Choisissez une carte",
                                         filetypes=(("All files", "*.*"),
                                                    ("Text files", "*.txt*")))
        filename = filename.split("/")
        filename = filename[-1]
        
        if filename != "":
            #on augmente le nombre de cartes de 1 dans le fichier
            with open("data/liste cartes obstacles","r") as f:
                nb_cartes = int(f.readline())
                f.seek(0)
                data = f.read()
                data = data.replace(str(nb_cartes),str(nb_cartes +1))
            
            #puis on ajoute le nom de la nouvelle carte à la fin
            with open("data/liste cartes obstacles","w") as f:
                f.write(data)
                f.write(filename+"\n")
                
            self.listeO.insert(tk.END, filename)
                
            self.listeO.selection_clear(0, tk.END)
            self.listeO.selection_set(tk.END)
            self.selectionnerCarteObstacles("<KeyRelease>")
            
    ###########################################################################
    #METHODES ONGLET 2
    ###########################################################################
    
    def selectionnerCartePersonnages(self,event):
        selected_index = self.listeP.curselection()
        if selected_index:
            index = selected_index[0]
            selected_item = self.listeP.get(index)
            self.importerCartePersonnages(selected_item)
            self.updatePreview()
            
    def importerCartePersonnages(self,fichier):   
        self.carte_persos.clear()
        nb_persos = 0
        with open(f"data/cartes personnages/{fichier}","r") as f:
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
    
    #supprime une carte de la liste des cartes perso
    def supprimerCartePersonnages(self):
        #on récupère la carte sélectionnée (qui va donc être supprimée)
        selected_index = self.listeP.curselection()
        if selected_index and selected_index[0] != 0:
            index = selected_index[0]
            selected_item = self.listeP.get(index)
            
            #on supprime la carte de la liste des cartes obstacles
            with open("data/liste cartes personnages","r") as f:
                nb_cartes = int(f.readline())
                f.seek(0)
                data = f.read()
                data = data.replace(str(nb_cartes),str(nb_cartes -1))
                data = data.replace(selected_item+"\n", "")
                
            with open("data/liste cartes personnages","w") as f:
                f.write(data)
            
            #on supprime la carte de la listbox
            self.listeP.delete(index)
            #on sélectionne automatiquement la carte d'avant
            self.listeP.select_set(index-1)
            self.selectionnerCartePersonnages("<KeyRelease>")
            
    #ajoute la nouvelle carte choisie au fichier "liste cartes obstacles"
    def nouvelleCartePersonnages(self):
        filename = tk.filedialog.askopenfilename(
                                         title="Choisissez une carte",
                                         filetypes=(("All files", "*.*"),
                                                    ("Text files", "*.txt*")))
        filename = filename.split("/")
        filename = filename[-1]
        
        if filename != "":
            #on augmente le nombre de cartes de 1 dans le fichier
            with open("data/liste cartes personnages","r") as f:
                nb_cartes = int(f.readline())
                f.seek(0)
                data = f.read()
                data = data.replace(str(nb_cartes),str(nb_cartes +1))
            
            #puis on ajoute le nom de la nouvelle carte à la fin
            with open("data/liste cartes personnages","w") as f:
                f.write(data)
                f.write(f"{filename}\n")
                
            self.listeP.insert(tk.END, filename)
                
            self.listeP.selection_clear(0, tk.END)
            self.listeP.selection_set(tk.END)
            self.selectionnerCartePersonnages("<KeyRelease>")          
            
    ###########################################################################
    #LE RESTE
    ###########################################################################
    
    def estDansPlateau(self,pos):
        if 0 <= pos[0] < self.dimensions[0] and 0 <= pos[1] < self.dimensions[1]:
            return True
        else:
            return False
    
    def recupererVitesse(self, event):
        vitesse = "{: .0f}".format(float(event))
        self.text_lab_slider.set(f"Vitesse de la simulation :\n{vitesse}")
        self.vitesse = int(vitesse)
    
    def updatePreview(self):
        if self.dimensions != (int(self.preview["height"])//10, int(self.preview["width"])//10):
            longueur = self.dimensions[0]*10
            largeur = self.dimensions[1]*10
            
            for obj in self.grille:
                self.preview.delete(obj)
            self.grille.clear()
            
            self.preview.configure(width=(largeur*2)//5, height=(longueur*2)//5)
            
            for i in range(0,(largeur*2)//5,4):
                self.grille.add(self.preview.create_line(i,0,i,(longueur*2)//5 , fill="#253444",
                                                         cap='round', width=1))
            for i in range(0,(longueur*2)//5,4):
                self.grille.add(self.preview.create_line(0,i,(largeur*2)//5,i, fill="#253444",
                                                         cap='round', width=1))
        
        #on supprime les objets graphiques
        for obj in self.preview_obj.values():
            self.preview.delete(obj)
        self.preview_obj.clear()
        
        #obstacles
        for pos in self.carte_obs:
            l = pos[0]
            c= pos[1]
            self.preview_obj[(l,c)]=self.preview.create_rectangle(c*4 +1, l*4 +1,
                                                                  (c+1)*4, (l+1)*4,
                                                                  fill="#7B98B6", 
                                                                  width=0)
        #personnages        
        nb_persos_non_places = 0
        for infos in self.carte_persos:
            dl = infos[0][0]
            dc = infos[0][1]
            al = infos[1][0]
            ac = infos[1][1]
            col = infos[2]
            if (dl,dc) in self.carte_obs or (al,ac) in self.carte_obs:
                nb_persos_non_places += 1
            elif not self.estDansPlateau((dl,dc)) or not self.estDansPlateau((al,ac)):
                nb_persos_non_places += 1
            elif (dl,dc) not in self.preview_obj:
                self.preview_obj[(dl,dc)]=self.preview.create_rectangle(dc*4 +1, 
                                                                         dl*4 +1,
                                                                         (dc+1)*4, 
                                                                         (dl+1)*4,
                                                                         fill=col, 
                                                                         width=0)
        self.preview.update()
        
        #on modifie le texte qui s'affiche dans la frame "infos"
        nb_persos = len(self.carte_persos)  
        self.text_lab2.set(f"Nombre de personnages : "
                           f"{nb_persos-nb_persos_non_places}")
        
        if nb_persos_non_places > 0:
            self.text_lab_attention.set(f"Attention : {nb_persos_non_places}"
                                        " personnages n'ont pas pu être placés !")
        else:
            self.text_lab_attention.set("")
    
    def dessinerCarte(self):
        fenetre_dessin = dessinercarte.FenetreDessin(self)
        fenetre_dessin.grab_set()
        
    def demarrerSim(self):
        fenetre_sim = simulation.FenetreSimulation(self, self.carte_obs, self.carte_persos,
                                                   self.vitesse, self.dimensions)
        fenetre_sim.grab_set()
        
            
    def configStyles(self):
        style = ttk.Style()
        
        style.theme_use("default")
        
        #scale
        style.configure("TScale", background=self.col_ui["gris 1"], 
                        troughcolor=self.col_ui["gris foncé 1"], troughrelief="flat", 
                        sliderrelief="flat")
        style.map("TScale", background=[("pressed", self.col_ui["gris 3"]), 
                                         ("active", self.col_ui["gris 2"])])
        
        #notebook
        style.configure("TNotebook", background=self.col_ui["gris foncé 1"], borderwidth=0)
        style.configure("TNotebook.Tab", background=self.col_ui["gris foncé 1"], borderwidth=0,
                        foreground="white", padding=[26,10], focuscolor=self.col_ui["gris foncé 2"])
        style.map("TNotebook.Tab", background= [("selected", self.col_ui["gris foncé 2"])])
        
        #combobox (pour la fenetre dessin)
        style.configure("TCombobox", background=self.col_ui["gris 2"], relief="flat",
                        foreground="white", selectbackground=None, selectforeground=None)
        style.map("TCombobox", fieldbackground=[("readonly", self.col_ui["gris 2"])])
        
        self.option_add("*TCombobox*Listbox.background", self.col_ui["gris 1"])
        self.option_add("*TCombobox*Listbox.selectBackground", self.col_ui["gris 4"])
        self.option_add("*TCombobox*Listbox.foreground", "white")
        self.option_add("*TCombobox*Listbox.relief", "flat")
        
        #boutons
        style.configure("TButton", background=self.col_ui["gris 1"], relief="flat", foreground="white",
                        padding=[10,12])
        style.map("TButton", background=[("pressed", self.col_ui["gris 4"]), 
                                         ("active", self.col_ui["gris 2"])],
                  relief=[("pressed", "sunken")])
        
        #bouton vert
        style.configure("Vert.TButton", background="#348A31")
        style.map("Vert.TButton", background=[("pressed", "#46A543"), ("active", "#3B9738")])
        
        #boutons menu (pour la fenetre dessin)
        style.configure("M.TButton", relief="flat", foreground="white", 
                        padding=[10,5], width=18)
        style.map("M.TButton", background=[("pressed", self.col_ui["gris 4"]), 
                                         ("active", self.col_ui["gris 2"])],
                  relief=[("pressed", "flat")])
        
        



fenetre = FenetrePrincipale()
fenetre.mainloop()