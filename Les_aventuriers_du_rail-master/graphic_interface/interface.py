import tkinter as tk
from tkinter import messagebox
from collections import Counter
from PIL import Image, ImageTk
from tkinter import PhotoImage
from game import Game
import math
import json


class GameApp:
    def __init__(self, root, players):
        self.root = root
        self.root.title("Les Aventuriers du Rail - USA")
        self.width = 1100
        self.height = 580
        self.larg_left_col = 250
        self.width_canvas = self.width - self.larg_left_col
        self.height_canvas = self.height
        self.root.geometry(f"{self.width}x{self.height}")
        #self.root.minsize(self.width, self.height)

        self.selected_cities = []

        with open("data/villes.json", "r", encoding="utf-8") as f:
            self.villes = json.load(f)

        with open("data/destinations.json", "r", encoding="utf-8") as f:
            self.routes = json.load(f)

        self.game = Game(players)
        self.game.start_game()
        self.bg_image_tk = None  # Stockage image fond

        self.setup_ui()

    def setup_ui(self):
        # 🧱 Cadre principal horizontal
        main_frame = tk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # ⬅️ Colonne gauche : Infos joueur
        # Canvas défilant à gauche
        left_canvas = tk.Canvas(main_frame, width=self.larg_left_col)
        left_canvas.pack(side=tk.LEFT, fill=tk.Y)
        left_canvas.pack_propagate(False)

        scrollbar = tk.Scrollbar(main_frame, orient="vertical", command=left_canvas.yview)
        scrollbar.pack(side=tk.LEFT, fill=tk.Y)

        # Frame contenant tous les éléments
        left_frame = tk.Frame(left_canvas)
        left_canvas.create_window((0, 0), window=left_frame, anchor="nw")
        left_canvas.configure(yscrollcommand=scrollbar.set)

        # Mise à jour du scroll lorsque le contenu change
        def on_configure(event):
            left_canvas.configure(scrollregion=left_canvas.bbox("all"))

        left_frame.bind("<Configure>", on_configure)

        # Activer le scroll avec la molette
        def _on_mousewheel(event):
            left_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        left_canvas.bind_all("<MouseWheel>", _on_mousewheel)

        # ➡️ Colonne droite : Carte
        right_frame = tk.Frame(main_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # 🧑‍💼 Joueur actuel
        self.player_label = tk.Label(left_frame, text="", font=("Helvetica", 14, "bold"))
        self.player_label.pack(pady=10)

        # 🎮 Boutons d'action
        actions_frame = tk.Frame(left_frame)
        actions_frame.pack(pady=15)

        tk.Button(actions_frame, text="Piocher wagon", command=self.draw_card).pack(pady=2)
        tk.Button(actions_frame, text="Piocher objectif", command=self.draw_objectives).pack(pady=2)
        tk.Button(actions_frame, text="Passer tour", command=self.next_turn).pack(pady=2)

        # 🎴 Cartes wagon
        self.hand_label = tk.Label(left_frame, text="Cartes en main :", font=("Helvetica", 12))
        self.hand_label.pack()
        self.cards_frame = tk.Frame(left_frame)
        self.cards_frame.pack(pady=5)

        # 🎯 Objectifs
        self.objectives_label = tk.Label(left_frame, text="Objectifs :", font=("Helvetica", 12))
        self.objectives_label.pack(pady=10)
        self.objectives_frame = tk.Frame(left_frame)
        self.objectives_frame.pack()

        # Objectifs réussis
        self.accomplished_label = tk.Label(left_frame, text="Objectifs atteints :", font=("Helvetica", 12))
        self.accomplished_label.pack(pady=10)
        self.accomplished_frame = tk.Frame(left_frame)
        self.accomplished_frame.pack()

        # 🃏 Cartes visibles
        self.visible_label = tk.Label(left_frame, text="Cartes visibles :", font=("Helvetica", 12))
        self.visible_label.pack(pady=10)
        self.visible_frame = tk.Frame(left_frame)
        self.visible_frame.pack()

        # 🗺️ Canvas carte (grande zone)
        self.canvas = tk.Canvas(right_frame, width=self.width_canvas, height=self.height_canvas, bg="white")
        self.canvas.pack(padx=5, pady=5, fill=tk.BOTH, expand=True)

        # Initialisation
        self.draw_graph()
        self.update_turn_display()
        self.update_hand_display()
        self.update_objectives_display()
        # self.update_visible_cards()

        #image des wagons
        self.card_images = {
            "blue": PhotoImage(file="data/blue.jpg"),
            "red": PhotoImage(file="data/red.jpg"),
            "green": PhotoImage(file="data/green.jpg"),
            "yellow": PhotoImage(file="data/yellow.jpg"),
            "black": PhotoImage(file="data/black.jpg"),
            "white": PhotoImage(file="data/white.jpg"),
            "orange": PhotoImage(file="data/orange.jpg"),
            "purple": PhotoImage(file="data/purple.jpg"),
            "Locomotive": PhotoImage(file="data/locomotive.jpg"),
        }

    import math

    def draw_graph(self):
        city_coords = {
            entry["city"]: (
                entry["i"] / 100 * self.width_canvas,
                self.height_canvas - entry["j"] / 100 * self.height_canvas
            )
            for entry in self.villes
        }

        self.canvas.delete("all")

        image = Image.open("data/USA_map.jpg").resize((int(self.width_canvas), int(self.height_canvas)))
        self.bg_image_tk = ImageTk.PhotoImage(image)
        self.canvas.create_image(0, 0, image=self.bg_image_tk, anchor="nw")

        # Regrouper manuellement les routes par paire de villes
        route_groups = []
        for route in self.routes:
            found = False
            for group in route_groups:
                if sorted([route["city1"], route["city2"]]) == sorted([group[0]["city1"], group[0]["city2"]]):
                    group.append(route)
                    found = True
                    break
            if not found:
                route_groups.append([route])

        for group in route_groups:
            route = group[0]
            city1 = route["city1"]
            city2 = route["city2"]

            if city1 in city_coords and city2 in city_coords:
                x1, y1 = city_coords[city1]
                x2, y2 = city_coords[city2]
                dx, dy = x2 - x1, y2 - y1
                length = math.hypot(dx, dy)
                offset_x, offset_y = -dy / length * 6, dx / length * 6  # perpendiculaire

                for i, route in enumerate(group):
                    shift = (i - (len(group) - 1) / 2)  # pour centrer
                    ox = offset_x * shift
                    oy = offset_y * shift

                    color = route.get("color", "gray")
                    points = route["length"]

                    # Vérifie si cette route est revendiquée
                    claimed = None
                    for player in self.game.players:
                        if (route["city1"], route["city2"]) in player.routes or (
                        route["city2"], route["city1"]) in player.routes:
                            color = player.color
                            claimed = player
                            break

                    self.canvas.create_line(x1 + ox, y1 + oy, x2 + ox, y2 + oy, fill=color, width=4)

                    if not claimed:
                        mx, my = (x1 + x2) / 2 + ox, (y1 + y2) / 2 + oy
                        self.canvas.create_text(mx, my, text=str(points), font=("Helvetica", 8), fill="darkred")

        # Villes
        for city, (x, y) in city_coords.items():
            self.canvas.create_oval(x - 5, y - 5, x + 5, y + 5, fill="lightblue", outline="black")
            self.canvas.create_text(x, y - 10, text=city, font=("Helvetica", 11, 'bold'), fill="black")

        self.city_coords = city_coords
        self.canvas.bind("<Button-1>", self.on_canvas_click)
        self.selected_cities = []

    # ---------------------------------- INTERACTION CARTE --------------------------------------------
    def on_canvas_click(self, event):
        # Déterminer quelle ville est cliquée
        for city, (x, y) in self.city_coords.items():
            if abs(event.x - x) < 8 and abs(event.y - y) < 8:
                self.selected_cities.append(city)

                # Ajouter un cercle rouge temporaire
                self.canvas.create_oval(x - 8, y - 8, x + 8, y + 8, outline="red", width=2)
                break

        if len(self.selected_cities) == 2:
            city1, city2 = self.selected_cities

            self.selected_cities.clear()

            # Tenter de revendiquer la route
            self.attempt_claim_route(city1, city2)
            self.update()

    def attempt_claim_route(self, city1, city2):
        if (city1, city2) in self.game.current_player.routes:
            return
        for route in self.routes:
            if {route["city1"], route["city2"]} == {city1, city2}:
                answer = tk.messagebox.askyesno("Revendiquer la route", f"{city1} ↔ {city2} ?")
                if answer:
                    self.claim_route(city1, city2, route)
                return

    def claim_route(self, city1, city2, route):
        player = self.game.current_player
        length = route["length"]
        route_color = route.get("color", "gray")

        # Cas spécial : les routes grises peuvent être prises avec n'importe quelle couleur (à condition d'en avoir assez)
        if route_color == "gray":
            # Compter les cartes par couleur (hors locomotives)
            color_counts = {}
            loco_count = 0
            for card in player.train_cards:
                if card == "Locomotive":
                    loco_count += 1
                else:
                    color_counts[card] = color_counts.get(card, 0) + 1

            # Trouver une couleur avec suffisamment de cartes OU compléter avec locomotives
            valid_color = None
            for color, count in color_counts.items():
                if count + loco_count >= length:
                    valid_color = color
                    break

            if not valid_color:
                messagebox.showwarning("Pas assez de cartes",
                                       f"{player.name} n’a pas assez de cartes d’une couleur (ou de locomotives) pour prendre la route.")
                return

            # Supprimer les cartes : priorité aux cartes de couleur, puis locomotives si besoin
            removed = 0
            new_hand = []
            for card in player.train_cards:
                if removed < length and card == valid_color:
                    removed += 1
                elif removed < length and card == "Locomotive":
                    removed += 1
                    messagebox.showinfo("Locomotive utilisée",
                                        f"{player.name} utilise une locomotive pour compléter la route.")
                else:
                    new_hand.append(card)
            player.train_cards = new_hand



        else:

            # Compter les cartes et locomotives

            color_counts = {}

            loco_count = 0

            for card in player.train_cards:

                if card == "Locomotive":

                    loco_count += 1

                else:

                    color_counts[card] = color_counts.get(card, 0) + 1

            if color_counts.get(route_color, 0) + loco_count < length:
                messagebox.showwarning("Pas assez de cartes", f"{player.name} n’a pas {length} cartes {route_color}.")

                return

            # Supprimer les bonnes cartes : d’abord couleur, puis locomotives

            removed = 0
            new_hand = []
            for card in player.train_cards:
                if removed < length and card == route_color:
                    removed += 1
                elif removed < length and card == "Locomotive":
                    removed += 1
                    messagebox.showinfo("Locomotive utilisée",
                                        f"{player.name} utilise une locomotive pour compléter la route.")
                else:
                    new_hand.append(card)
            player.train_cards = new_hand

        player.routes.append((city1, city2))
        player.score += self.game.SCORE_TABLE.get(length, length)
        messagebox.showinfo("Route revendiquée", f"{player.name} a pris la route {city1} ↔ {city2} !")
        self.update_objectif_accompli()

    def update(self):
        self.update_hand_display()
        self.update_turn_display()
        self.update_objectives_display()
        self.update_accomplished_display()  # Très important pour affichage joueur actuel
        self.draw_graph()

    # -------------------------------------- TIRAGE -----------------------------------------------
    def draw_objectives(self):
        drawn = self.game.draw_destination_cards(3)

        if not drawn:
            tk.messagebox.showinfo("Objectifs", "Il n'y a plus d'objectifs à piocher.")
            return

        player = self.game.current_player

        # Interface temporaire de sélection (prend toutes les cartes pour l’instant)
        msg = "Objectifs tirés :\n" + "\n".join(
            f"{c['city1']} → {c['city2']} ({c['length']} pts)" for c in drawn
        )
        tk.messagebox.showinfo("Nouveaux objectifs", msg)

        for card in drawn:
            player.add_destination_card(card)

        self.update_objectives_display()

    def draw_card(self):
        self.game.player_draw_cards(1)
        self.update_hand_display()

    def visible_card_draw(self, index):
        self.game.visible_card_draw(index)
        self.update_hand_display()

    # -------------------------------------- UPDATE -----------------------------------------------
    def update_hand_display(self):
        for widget in self.cards_frame.winfo_children():
            widget.destroy()

        current = self.game.current_player
        max_per_row = 4  # nombre de cartes par ligne

        for i, card in enumerate(current.train_cards):
            row = i // max_per_row
            col = i % max_per_row
            card_label = tk.Label(self.cards_frame, text=card, relief=tk.RIDGE, borderwidth=2, padx=5, pady=2)
            card_label.grid(row=row, column=col, padx=2, pady=2, sticky="w")

    def get_color_hex(self, color):
        color_map = {
            "red": "#d9534f",
            "blue": "#0275d8",
            "green": "#5cb85c",
            "yellow": "#f0ad4e",
            "black": "#292b2c",
            "white": "#f7f7f7",
            "purple": "#613d7c",
            "orange": "#f26522",
            "joker": "#cccccc",
            "gray": "#aaaaaa"
        }
        return color_map.get(color.lower(), "lightgray")

    def update_objectives_display(self):
        for widget in self.objectives_frame.winfo_children():
            widget.destroy()

        current = self.game.current_player
        max_per_row = 2  # par exemple : 2 objectifs par ligne

        for i, obj in enumerate(current.destination_cards):
            row = i // max_per_row
            col = i % max_per_row
            obj_text = f"{obj['city1']} → {obj['city2']} ({obj['length']} pts)"
            obj_label = tk.Label(self.objectives_frame, text=obj_text, relief=tk.SOLID, borderwidth=1, padx=4, pady=2)
            obj_label.grid(row=row, column=col, padx=3, pady=3, sticky="w")

    def update_objectif_accompli(self):
        current = self.game.current_player
        accomplished = []

        for obj in current.destination_cards[:]:
            if self.is_objective_completed(obj):
                current.destination_cards.remove(obj)
                current.accomplished_objectives.append(obj)

        self.update_objectives_display()
        self.update_accomplished_display()

    def is_objective_completed(self, objective):
        from collections import deque

        graph = {}
        for c1, c2 in self.game.current_player.routes:
            graph.setdefault(c1, []).append(c2)
            graph.setdefault(c2, []).append(c1)

        start = objective['city1']
        target = objective['city2']
        visited = set()
        queue = deque([start])

        while queue:
            city = queue.popleft()
            if city == target:
                return True
            if city not in visited:
                visited.add(city)
                queue.extend(graph.get(city, []))

        return False

    def update_accomplished_display(self):
        for widget in self.accomplished_frame.winfo_children():
            widget.destroy()

        self.update_objectives_display()

        current = self.game.current_player
        for i, obj in enumerate(current.accomplished_objectives):
            obj_text = f"{obj['city1']} → {obj['city2']} ({obj['length']} pts)"
            obj_label = tk.Label(self.accomplished_frame, text=obj_text, relief=tk.GROOVE, bg="lightgreen", padx=4,
                                 pady=2)
            obj_label.pack(padx=2, pady=2, anchor="w")

    def update_turn_display(self):
        current = self.game.current_player
        self.player_label.config(text=f"Joueur : {current.name}")

    def update_hand_display(self):
        for widget in self.cards_frame.winfo_children():
            widget.destroy()

        current = self.game.current_player
        max_per_row = 5  # nombre de cartes par ligne

        for i, card in enumerate(current.train_cards):
            row = i // max_per_row
            col = i % max_per_row
            card_label = tk.Label(self.cards_frame, text=card, relief=tk.RIDGE, borderwidth=2, padx=5, pady=2)
            card_label.grid(row=row, column=col, padx=2, pady=2)



    def afficher_main_cartes(self, player):
        for widget in self.cards_frame.winfo_children():
            widget.destroy()

        counts = Counter(player.train_cards)

        for color, count in counts.items():
            frame = tk.Frame(self.cards_frame)
            frame.pack(side="top", pady=5)

            img_label = tk.Label(frame, image=self.card_images[color])
            img_label.image = self.card_images[color]
            img_label.pack(side="left")

            count_label = tk.Label(frame, text=f"x{count}", font=("Arial", 12))
            count_label.pack(side="left", padx=5)

    def next_turn(self):
        self.game.next_turn()
        self.update_turn_display()
        self.update_hand_display()
        self.update_objectives_display()
        self.update_accomplished_display()