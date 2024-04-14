import tkinter as tk
from tkinter import ttk
import tkiteasy
from math import inf
import time


class FenetreSimulation(tk.Toplevel):
    
    col_ui={"gris foncé 1":"#18222D", "gris foncé 2": "#1E2A37",
                 "gris 1":"#475363", "gris 2":"#536173", "gris 3":"#606F82", 
                 "gris 4":"#5D6B7E", "vert 1":"#348A31", "vert 2":"#3B9738", 
                 "vert 3":"#46A543", "gris obs":"#7B98B6"}
    
    couleurs_persos=["yellow","blue","green","red"]
    
    def __init__(self, master, carte_obs, carte_persos, vitesse, dimensions):
        
        super().__init__(master) #on appelle le constructeur parent
        self.title("Simulation")
        self.resizable(False, False)
        self["bg"] = self.col_ui["gris foncé 1"]
        self.focus_force()
        
        #configure les styles des boutons et du scale
        self.configStyles()
        
        self.bind("<Destroy>", self.nettoyer)
        self.pause = False
        
        
        #la frame avec les boutons et le slider pour régler la vitesse et tout
        frame_droite = tk.Frame(self, bg=self.col_ui["gris foncé 2"],
                                highlightthickness=1, highlightcolor=self.col_ui["gris 1"],
                                highlightbackground=self.col_ui["gris 1"])
        frame_droite.pack(side=tk.RIGHT, fill=tk.Y, padx=[0,10], pady=10)
        
        self.bouton1 = ttk.Button(frame_droite, text="Pause", takefocus=False, 
                             command=self.mettreEnPause)
        self.bouton1.pack(side=tk.TOP, padx=10, pady=15)
        
        self.bind("<KeyPress-space>",func=lambda event: self.mettreEnPause())
        
        self.lab_slider = tk.Label(frame_droite, text=f"Vitesse : {vitesse}",
                              fg="white", bg=self.col_ui["gris foncé 2"])
        self.lab_slider.pack(side=tk.TOP, pady=10)
           
        bordures_slider = tk.Frame(frame_droite, bg=self.col_ui["gris 1"])
        bordures_slider.pack(side=tk.TOP, fill=tk.X, padx=10)
        
        self.slider = ttk.Scale(bordures_slider, from_=1, to=10, orient="horizontal",
                                command=self.recupererVitesse)
        self.slider.set(vitesse)
        self.slider.pack(expand=True, fill=tk.BOTH, padx=1, pady=1)
        
        self.lab_duree = tk.Label(frame_droite, text="", fg="white",
                                  bg=self.col_ui["gris foncé 2"], anchor=tk.W,
                                  justify=tk.LEFT)
        self.lab_duree.pack(side=tk.BOTTOM, fill=tk.BOTH, padx=5, pady=10)
        
        self.lab_tours = tk.Label(frame_droite, text="", fg="white",
                                  bg=self.col_ui["gris foncé 2"], anchor=tk.W,
                                  justify=tk.LEFT)
        self.lab_tours.pack(side=tk.BOTTOM, fill=tk.BOTH, padx=5, pady=5)

        ########################################################################
        #LE CANEVAS
        ########################################################################

        #création du canevas
        bordures_sim = tk.Frame(self, bg=self.col_ui["gris 1"])
        bordures_sim.pack(expand=True, padx=10, pady=10)
        
        x = dimensions[1]*10
        y = dimensions[0]*10
        self.sim = tkiteasy.Canevas(bordures_sim, x, y)
        self.sim.configure(highlightthickness=0)
        self.sim.pack(expand=True, padx=1, pady=1)
        
        self.sim.bind("<Button-1>", self.dessinerObstacles)
        self.sim.bind("<Button-3>", self.gomme)
        
        self.dim = dimensions
        
        #on dessine le fond et la grille
        self.sim.dessinerRectangle(0,0,x,y,self.col_ui["gris foncé 2"])

        for i in range(10,x,10):
            self.sim.dessinerLigne(i,0,i,y,"#2F3B4A")
            
        for i in range(10,y,10):
            self.sim.dessinerLigne(0,i,x,i,"#2F3B4A")
            
        self.sim.actualiser()
        
        #on setup la simulation
        self.cpt_tours = 0
        self.delai = 1000//(vitesse*10)
        
        self.obstacles = {} #dico qui contient les sprites des murs indexés par leur position
        for obs in carte_obs:
            l = obs[0]
            c = obs[1]
            if self.estDansPlateau((l,c)):
                rect = self.sim.dessinerRectangle(c*10 +1, l*10 +1, 9, 9, 
                                           self.col_ui["gris obs"])
                self.obstacles[(l,c)] = rect
            
        for perso in carte_persos:
            if perso[0] not in self.obstacles and perso[1] not in self.obstacles:
                if self.estDansPlateau(perso[0]) and self.estDansPlateau(perso[1]):
                    Personnage(self, perso[0], perso[1], perso[2])
            
        #c'est parti !!
        self.temps_debut = time.time()
        self.deplacerPersonnages(fini=False)
        
    
    
    
    def estDansPlateau(self,pos):
        if 0 <= pos[0] < self.dim[0] and 0 <= pos[1] < self.dim[1]:
            return True
        else:
            return False
        
    def nettoyer(self, event):
        Personnage.annuaire.clear()
        Personnage.pos_persos.clear()
    
    def deplacerPersonnages(self, fini):
        if not fini:
            if self.pause:
                pass
            else:
                fini = True
                for p in Personnage.annuaire:
                    if not p.arrive :
                        p.deplacer()
                        fini = False
                self.cpt_tours += 1
                self.sim.actualiser() 
            
            self.sim.after(self.delai, func=lambda: self.deplacerPersonnages(fini))
          
        else:
            self.simulationFinie()   
        
    def mettreEnPause(self):
        self.pause = not self.pause
        
        if self.pause:
            self.bouton1.configure(text="Reprendre")
        else:
            self.bouton1.configure(text="Pause")
            
    def dessinerObstacles(self, event):
        if self.sim.recupererFinClic() == None:
            pos = self.sim.recupererPosition()
            pos_l = pos.y //10
            pos_c = pos.x //10
            pos = (pos_l, pos_c)
            
            if self.estDansPlateau(pos) and pos not in self.obstacles and pos not in Personnage.pos_persos:
                rect = self.sim.dessinerRectangle(pos_c*10 +1,pos_l*10 +1, 9, 9, self.col_ui["gris obs"])
                self.obstacles[pos] = rect
            
            self.sim.after(1, lambda: self.dessinerObstacles("<Button-1>"))
            
    def gomme(self, event):
        if self.sim.recupererFinClic() == None:
            pos = self.sim.recupererPosition()
            pos_l = pos.y //10
            pos_c = pos.x //10
            pos = (pos_l, pos_c)
            
            if pos in self.obstacles:
                self.sim.supprimer(self.obstacles[pos])
                self.obstacles.pop(pos)
            
            self.sim.after(1, lambda: self.gomme("<Button-3>"))
            
    def simulationFinie(self):
        temps_fin = time.time()
        duree = "{: .3f}".format(temps_fin - self.temps_debut)
        self.lab_duree.configure(text=f"Durée simulation :\n{duree} secondes")
        
        self.lab_tours.configure(text=f"Nombre de tours :\n"
                                             f"{self.cpt_tours}")
        
        self.bouton1.configure(state="disabled")
        self.lab_slider.configure(state="disabled")
        self.slider.configure(state="disabled")
        
        self.title("Simulation (terminée)")
        
        self.unbind("<KeyPress-space>")
        self.sim.unbind("<ButtonPress-1>")
        self.sim.unbind("<ButtonPress-3>")
            
    def recupererVitesse(self, event): 
        vitesse = "{: .0f}".format(float(event))
        self.lab_slider.configure(text=f"Vitesse : {vitesse}")
        vitesse = int(vitesse)
        self.delai = 1000//(vitesse*10)
        
    def configStyles(self):
        style = ttk.Style(master=self)
        
        style.theme_use("default")
        
        #scale
        style.configure("TScale", background=self.col_ui["gris 1"], 
                        troughcolor=self.col_ui["gris foncé 1"], troughrelief="flat", 
                        sliderrelief="flat")
        style.map("TScale", background=[("disabled", self.col_ui["gris 1"]),
                                        ("pressed", self.col_ui["gris 3"]), 
                                         ("active", self.col_ui["gris 2"])])
        
        #boutons
        style.configure("TButton", background="#475363", relief="flat", foreground="white",
                        padding=[10,12] )
        style.map("TButton", background=[("pressed", self.col_ui["gris 4"]), 
                                         ("active", self.col_ui["gris 2"])],
                  relief=[("pressed", "sunken")])
        

#################################################################################
#CLASSE PERSONNAGE
#################################################################################

class Personnage():
    
    annuaire = []
    pos_persos = {} #(l,c):<nb de persos>
        
    def __init__(self, master, depart, destination, couleur="yellow"):
        self.master = master
        self.arrive = False
        self.pos = depart
        self.destination = destination
        self.prev_pos = set()
        self.couleur = couleur
        self.sprite = self.master.sim.dessinerRectangle(self.pos[1]*10 +1,self.pos[0]*10 +1, 9, 9, couleur)
        
        try : Personnage.pos_persos[depart] += 1
        except KeyError : Personnage.pos_persos[depart] = 1
        Personnage.annuaire.append(self)
        
    def distance(self,pos1,pos2): #retourne (le carré de) la distance entre les deux cases
        return (pos1[0] - pos2[0])**2 + (pos1[1] - pos2[1])**2
        
    def voisinage8(self,l,c): #retourne les cases accessibles autour de la case en entrée
        vois = []
        for dl in range(-1,2):
            for dc in range(-1,2):
                pos = (l+dl,c+dc)
                if self.master.estDansPlateau(pos):
                    if pos not in self.master.obstacles and pos not in Personnage.pos_persos:
                        vois.append(pos)
                    elif pos == self.destination:
                        vois.append(pos)
        return vois     
    
    def meilleurScore(self,case1,case2): #retourne la case la plus proche de la destination
        score1 = self.distance(case1,self.destination)
        score2 = self.distance(case2, self.destination)
        
        if score1 <= score2:
            return case1
        else:
            return case2
    
    def deplacer(self): #réalise un déplacement du personnage
        if self.pos != self.destination:
            
            voisinage = self.voisinage8(self.pos[0], self.pos[1])
            
            next_pos = (inf,inf)      
            for i in voisinage:
                if i not in self.prev_pos:
                    next_pos = self.meilleurScore(i,next_pos)

            
            if next_pos != (inf,inf):
                self.prev_pos.add(self.pos)
                
                if Personnage.pos_persos[self.pos] == 1:
                    Personnage.pos_persos.pop(self.pos)
                else:
                    Personnage.pos_persos[self.pos] -= 1
                
                dl = next_pos[0] - self.pos[0]
                dc = next_pos[1] - self.pos[1]
                #g.dessinerRectangle(self.col*10 +1,self.ligne*10 +1, 9, 9, "#83836C")
                self.pos = next_pos
            
                self.master.sim.deplacer(self.sprite, dc*10, dl*10)
                
                try : Personnage.pos_persos[self.pos] += 1
                except KeyError : Personnage.pos_persos[self.pos] = 1
            
            #si il n'y a aucune case dispo pour le perso, on vide le set des
            #positions précédentes
            else:
                self.prev_pos.clear()

        else:
            self.arrive = True       
        
        
        

