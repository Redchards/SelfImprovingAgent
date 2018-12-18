import entity


class Sensor:
    def __init__(self, sensor_type, sensor_list, sensor_map, sensor_aoe):
        self.sensor_type = sensor_type
        self.sensor_list = sensor_list
        self.sensor_map = sensor_map
        self.sensor_aoe = sensor_aoe
        self.current_perception = [0 for _, x in self.sensor_map.items() for _ in x]

    def perception(self, player_position, map):
        dim = (len(map[0]), len(map))
        #tmp = []
        perception_result = []
        for idx, s in enumerate(self.sensor_list):
            receptor = next((k for k, l in self.sensor_map.items() if idx in l))
            aoe = self.sensor_aoe[receptor]
            x_pos, y_pos = (player_position[0] + self.sensor_list[idx][0], player_position[1] + self.sensor_list[idx][1])
            activated = False
            for cell_x, cell_y in aoe:
                if y_pos + cell_y >= dim[1] or y_pos + cell_y < 0 \
                        or x_pos + cell_x >= dim[0] or x_pos + cell_x < 0:
                    continue
                #print(y_pos + cell_y, x_pos + cell_x)
                #print(dim)
                if map[y_pos + cell_y][x_pos + cell_x].type == self.sensor_type:
                    perception_result.append(1)
                    activated = True
                    #tmp.append(offset)
                    break
            if not activated:
                perception_result.append(0)

        #print(perception_result)
        #print(tmp)
        self.current_perception = perception_result
        return perception_result
