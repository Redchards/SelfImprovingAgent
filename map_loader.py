import entity
import csv

class MapLoader:
    def __init__(self):
        self.entities = [entity.PlayerAgent, entity.EnemyAgent, entity.Food, entity.Obstacle]
        self.entity_dict = {e.type: e for e in self.entities}

    def parse_map(self, filename):
        with open(filename, newline='') as f:
            mapreader = csv.reader(f, delimiter=',')

            map = []
            current_ids = {e.type: 1 for e in self.entities}
            for row in mapreader:
                map.append([])
                for elem in row:
                    if elem == '#':
                        map[-1].append(entity.EmptyEntity())
                    else:
                        map[-1].append(self.entity_dict[elem](current_ids[elem]))
                        current_ids[elem] += 1

            return map
