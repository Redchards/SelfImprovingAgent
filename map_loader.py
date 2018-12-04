import entity
import csv
import numpy.random as random

class MapLoader:
    def __init__(self):
        self.entities = [entity.PlayerAgent, entity.EnemyAgent, entity.Food, entity.Obstacle]
        self.entity_dict = {e.symbol: e for e in self.entities}

    def parse_map(self, filename):
        with open(filename, newline='') as f:
            mapreader = csv.reader(f, delimiter=',')

            nb_food = 0
            map = []
            current_ids = {e.symbol: 1 for e in self.entities}
            init = False
            for row in mapreader:
                if not init:
                    nb_food = int(row[0])
                    init = True
                    continue

                map.append([])
                for elem in row:
                    if elem == '#':
                        map[-1].append(entity.EmptyEntity())
                    else:
                        map[-1].append(self.entity_dict[elem](current_ids[elem]))
                        current_ids[elem] += 1

            dim = (len(map[0]), len(map))
            # add the food
            success = False
            for _ in range(nb_food):
                success = False
                while not success:
                    x, y = random.randint(0, dim[0] - 1), random.randint(0, dim[1] - 1)
                    if map[y][x].type == 'empty':
                        map[y][x] = entity.Food(current_ids[entity.Food.symbol])
                        success = True

            return map
