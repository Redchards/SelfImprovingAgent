class PlayerState:
    def __init__(self, speed, max_health, quantized_level_num, position):
        self.speed = speed
        self.max_health = max_health
        self.position = position
        self.alive = True

        self.current_health = max_health
        self.quantized_level_num = quantized_level_num
        self.quantized_step = self.max_health / self.quantized_level_num
        self.current_health_level = quantized_level_num - 1

    def take_damage(self, damage):
        self.current_health -= damage
        if self.current_health < 0:
            self.current_health = 0
            self.alive = False

        self.update_level()

    def heal(self, number):
        self.current_health += number
        if self.current_health > self.max_health:
            self.current_health = self.max_health

        self.update_level()

    def update_level(self):
        self.current_health_level = int(self.current_health // self.quantized_step)
        if self.current_health_level == self.quantized_level_num:
            self.current_health_level = self.quantized_level_num - 1
        elif self.current_health_level < 0:
            self.current_health_level = 0
            self.alive = False
