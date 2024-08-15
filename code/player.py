from settings import *

class Player(pygame.sprite.Sprite):
    def __init__(self, pos, groups, collision_sprites):
        super().__init__(groups)

        self.frames = {'left': [
            join('images', 'player', 'left', '0.png'),
            join('images', 'player', 'left', '1.png'),
            join('images', 'player', 'left', '2.png'),
            join('images', 'player', 'left', '3.png'),
        ], 'right': [], 'up': [], 'down': []}

        self.state = 'down'
        self.frame_index = 0
        self.image = pygame.image.load(join('images', 'player', 'down', '0.png')).convert_alpha()
        self.rect = self.image.get_frect(center = pos)
        self.hitbox_rect = self.rect.inflate(-60, -90)

        # movement
        self.direction = pygame.Vector2()
        self.speed = 500
        self.collision_sprites = collision_sprites

    def load_images(self):
        self.frames = {'left': [], 'right': [], 'up': [], 'down': []}

        for state in self.frames.keys():
            for folder_path, sub_folders, file_names in walk(join('images', 'player', state)):
                if file_names:
                    for file_name in sorted(file_names, key= lambda name: int(name.split('.')[0])):
                        full_path = join(folder_path, file_name)
                        surf = pygame.image.load(full_path).convert_alpha()
                        self.frames[state].append(surf)

    def move(self, dt):
        keys = pygame.key.get_pressed()

        # 좌우 움직임 처리
        move_right = keys[pygame.K_d]
        move_left = keys[pygame.K_a]
        self.direction.x = int(move_right - move_left)

        # 상하 움직임 처리
        move_down = keys[pygame.K_s]
        move_up = keys[pygame.K_w]
        self.direction.y = int(move_down - move_up)

        # 대각선 이동 시 속도 정규화
        if self.direction.length() > 0:
            self.direction = self.direction.normalize()

        self.hitbox_rect.x += self.direction.x * self.speed * dt
        self.collision('horizontal')

        self.hitbox_rect.y += self.direction.y * self.speed * dt
        self.collision('vertical')

        self.rect.center = self.hitbox_rect.center

    def collision(self, direction):
        for sprite in self.collision_sprites:
            if sprite.rect.colliderect(self.hitbox_rect):
                if direction == 'horizontal':
                    if self.direction.x > 0:
                        self.hitbox_rect.right = sprite.rect.left
                    if self.direction.x < 0:
                        self.hitbox_rect.left = sprite.rect.right
                else:
                    if self.direction.y < 0:
                        self.hitbox_rect.top = sprite.rect.bottom
                    if self.direction.y > 0:
                        self.hitbox_rect.bottom = sprite.rect.top

    def animate(self, dt):
        if self.direction.x != 0:
            if self.direction.x > 0:
                self.state = 'right'
            else:
                self.state = 'left'
        if self.direction.y != 0:
            if self.direction.y > 0:
                self.state = 'down'
            else:
                self.state = 'up'

        # animate
        if self.direction:
            self.frame_index = int(self.frame_index + dt * 5)
        else:
            self.frame_index = 0

        self.image = self.frames[self.state][self.frame_index % len(self.frames[self.state])]

    def update(self, dt):
        self.move(dt)
        self.animate(dt)