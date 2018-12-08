import entity


class Sensor:
    def __init__(self, sensor_type, sensor_map, sensor_aoe):
        self.sensor_type = sensor_type
        self.sensor_map = sensor_map
        self.sensor_aoe = sensor_aoe
        self.current_perception = [0 for _, x in self.sensor_map.items() for _ in x]

    def perception(self, player_position, map):
        dim = (len(map[0]), len(map))
        #tmp = []
        perception_result = []
        for receptor, offsets in self.sensor_map.items():
            aoe = self.sensor_aoe[receptor]
            for offset in offsets:
                x_pos, y_pos = (player_position[0] + offset[0], player_position[1] + offset[1])
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
