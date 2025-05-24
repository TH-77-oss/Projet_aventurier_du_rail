class Route:
    def __init__(self, city1, city2, color, length):
        self.city1 = city1
        self.city2 = city2
        self.color = color
        self.length = length
        self.claimed_by = None

    # DEBUG
    '''def get_roads(self):
        routes = []

        with open('data/routes.txt', 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue

                # Regex pour extraire les données
                match = re.match(r"(.+?) to (.+?) \((\d+)\)", line)
                if match:
                    city_from = match.group(1).strip()
                    city_to = match.group(2).strip()
                    points = int(match.group(3))
                    routes.append({
                        "city1": city_from,
                        "city2": city_to,
                        "length": points
                    })

        # Écriture en JSON
        with open("destinations.json", "w", encoding='utf-8') as f:
            json.dump(routes, f, indent=4)'''

