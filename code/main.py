import pygame
import random
import os
import math

# 초기화
pygame.init()

# 색상 정의
GREEN = (34, 139, 34)
BLACK = (0, 0, 0)  # 총알 색상

# 게임 설정
# 게임 월드 크기 설정
WORLD_WIDTH = 2560
WORLD_HEIGHT = 1440
WIDTH = 1280
HEIGHT = 720
TILE_SIZE = 64
PLAYER_SIZE = 64  # 플레이어 크기를 타일 크기와 동일하게 설정

# 화면 설정
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("뱀파이어 서바이버즈 - 빵형의 개발도상국")

# 이미지 로드 함수
def load_images(path):
    images = []
    for i in range(4):  # 0.png에서 3.png까지
        img = pygame.image.load(os.path.join(path, f"{i}.png")).convert_alpha()
        images.append(img)
    return images

# 플레이어 이미지 로드
player_images = {
    'up': load_images(os.path.join('images', 'player', 'up')),
    'down': load_images(os.path.join('images', 'player', 'down')),
    'left': load_images(os.path.join('images', 'player', 'left')),
    'right': load_images(os.path.join('images', 'player', 'right'))
}

enemy_images = {
    'bat': load_images(os.path.join('images', 'enemies', 'bat')),
    'blob': load_images(os.path.join('images', 'enemies', 'blob')),
    'skeleton': load_images(os.path.join('images', 'enemies', 'skeleton'))
}

# 장애물 이미지 로드
obstacle_images = [
    pygame.image.load(os.path.join('data', 'graphics', 'objects', 'green_tree_small.png')).convert_alpha(),
    pygame.image.load(os.path.join('data', 'graphics', 'objects', 'grassrock1.png')).convert_alpha(),
]

# 총알 클래스
class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, direction):
        super().__init__()
        self.image = pygame.Surface((16, 16))
        self.image.fill(BLACK)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.speed = 10
        self.direction = direction
        self.world_rect = pygame.Rect(0, 0, WORLD_WIDTH, WORLD_HEIGHT)
        self.lifetime = 0.5
        self.dtt = 0

    def update(self, dt):
        self.dtt += dt
        self.rect.x += self.direction[0] * self.speed
        self.rect.y += self.direction[1] * self.speed

        # 총알 제거
        # if not self.world_rect.collidepoint(self.rect.centerx, self.rect.centery):
        if self.dtt > self.lifetime:
            self.kill()

# 카메라 클래스
class Camera:
    def __init__(self):
        self.camera = pygame.Rect(0, 0, WORLD_WIDTH, WORLD_HEIGHT)

    def apply(self, entity):
        return entity.rect.move(self.camera.topleft)

    def update(self, player):
        x = WIDTH // 2 - player.rect.centerx
        y = HEIGHT // 2 - player.rect.centery
        # 왼쪽 위 제한
        x = min(0, x)
        y = min(0, y)
        # 오른쪽 아래 제한
        x = max(-WIDTH, x)
        y = max(-HEIGHT, y)
        self.camera = pygame.Rect(x, y, WORLD_WIDTH, WORLD_HEIGHT)

# 플레이어 클래스
class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.images = player_images
        self.state = 'down'
        self.direction = pygame.Vector2()
        self.animation_index = 0
        self.image = self.images[self.state][self.animation_index]
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.speed = 5
        self.animation_speed = 0.2
        self.animation_time = 0
        self.last_movement = (0, 0)
        self.shoot_timer = 0
        self.shoot_delay = 1000  # 1초마다 발사

    def move(self, dx, dy):
        if dx != 0 or dy != 0:
            self.last_movement = (dx, dy)
            if dx > 0:
                self.state = 'right'
            elif dx < 0:
                self.state = 'left'
            elif dy > 0:
                self.state = 'down'
            elif dy < 0:
                self.state = 'up'

        self.direction.x = dx
        self.direction.y = dy

        if self.direction.length() > 0:
            self.direction = self.direction.normalize()

        self.rect.x += self.direction.x * self.speed
        self.rect.y += self.direction.y * self.speed

    def update(self, dt):
        if self.direction.length() > 0:  # 마지막 움직임이 있었을 때만 애니메이션 업데이트
            self.animation_time += dt
            if self.animation_time >= self.animation_speed:
                self.animation_time = 0
                self.animation_index = (self.animation_index + 1) % 4
                self.image = self.images[self.state][self.animation_index]
        else:
            # 움직이지 않을 때는 첫 번째 프레임으로 리셋
            self.animation_index = 0
            self.image = self.images[self.state][self.animation_index]

    def stop(self):
        self.last_movement = (0, 0)

    def shoot(self):
        bullets = []
        for angle in range(0, 360, 45):  # 8방향
            state = (math.cos(math.radians(angle)), math.sin(math.radians(angle)))
            bullet = Bullet(self.rect.centerx, self.rect.centery, state)
            bullets.append(bullet)
        return bullets


# 적 클래스
class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, enemy_type):
        super().__init__()
        self.enemy_type = enemy_type
        self.images = enemy_images[enemy_type]
        self.image = self.images[0]
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.direction = pygame.Vector2()
        self.animation_index = 0
        self.animation_speed = 0.2
        self.animation_time = 0
        self.speed = 2  # 적의 이동 속도 추가

    def update(self, dt, player, obstacles):
        # 애니메이션 업데이트
        self.animation_time += dt
        if self.animation_time >= self.animation_speed:
            self.animation_time = 0
            self.animation_index = (self.animation_index + 1) % 4
            self.image = self.images[self.animation_index]

        # 이전 위치 저장
        old_pos = self.rect.center

        # 플레이어 방향으로 이동
        dx = player.rect.centerx - self.rect.centerx
        dy = player.rect.centery - self.rect.centery

        dist = math.hypot(dx, dy)
        if dist != 0:
            dx, dy = dx / dist, dy / dist  # 정규화
            self.rect.x += dx * self.speed
            self.rect.y += dy * self.speed

        # 충돌 체크
        if pygame.sprite.spritecollide(self, obstacles, False):
            self.rect.center = old_pos + pygame.Vector2(1, 1)  # 충돌 시 이전 위치로 되돌림

# 적 스폰 함수
def spawn_enemy():
    enemy_type = random.choice(['bat', 'blob', 'skeleton'])
    x = random.randint(0, WORLD_WIDTH)
    y = random.randint(0, WORLD_HEIGHT)
    return Enemy(x, y, enemy_type)

# 장애물 클래스
class Obstacle(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        obscale_image = random.choice(obstacle_images)
        self.image = obscale_image
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

# 스프라이트 그룹 생성
all_sprites = pygame.sprite.Group()
obstacles = pygame.sprite.Group()
bullets = pygame.sprite.Group()
enemies = pygame.sprite.Group()

# 플레이어 생성 (월드의 중앙에 위치)
player = Player(WORLD_WIDTH // 2, WORLD_HEIGHT // 2)
all_sprites.add(player)

# 장애물 생성
for _ in range(20):
    x = random.randint(0, WORLD_WIDTH - TILE_SIZE)
    y = random.randint(0, WORLD_HEIGHT - TILE_SIZE)
    obstacle = Obstacle(x, y)
    all_sprites.add(obstacle)
    obstacles.add(obstacle)

# 초기 적 생성 (예: 10마리)
for _ in range(10):
    enemy = spawn_enemy()
    all_sprites.add(enemy)
    enemies.add(enemy)

# 카메라 생성
camera = Camera()

# 게임 루프 수정
running = True
clock = pygame.time.Clock()

while running:
    dt = clock.tick(60) / 1000  # 델타 타임 (초 단위)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # 플레이어 이동
    keys = pygame.key.get_pressed()
    dx = keys[pygame.K_d] - keys[pygame.K_a]
    dy = keys[pygame.K_s] - keys[pygame.K_w]
    player.move(dx, dy)

    # 충돌 체크 (플레이어와 장애물)
    if pygame.sprite.spritecollide(player, obstacles, False):
        player.rect.x -= dx * player.speed
        player.rect.y -= dy * player.speed
        player.stop()

    # 총알 발사
    player.shoot_timer += dt * 1000
    if player.shoot_timer >= player.shoot_delay:
        player.shoot_timer = 0
        new_bullets = player.shoot()
        bullets.add(new_bullets)
        all_sprites.add(new_bullets)

    # 총알과 적 충돌 체크
    for bullet in bullets:
        hit_enemies = pygame.sprite.spritecollide(bullet, enemies, True)
        if hit_enemies:
            bullet.kill()
            for enemy in hit_enemies:
                all_sprites.remove(enemy)

    # TODO: 사용자와 적 충돌 체크 (게임오버)

    # 새로운 적 스폰 (예: 3초마다)
    if random.random() < dt / 1:
        new_enemy = spawn_enemy()
        all_sprites.add(new_enemy)
        enemies.add(new_enemy)

    # 스프라이트 업데이트
    player.update(dt)
    bullets.update(dt)
    for enemy in enemies:
        enemy.update(dt, player, obstacles)  # obstacles 전달

    # 카메라 업데이트
    camera.update(player)

    # 화면 그리기
    screen.fill(GREEN)
    # all_sprites.draw(screen)
    for sprite in all_sprites:
        screen.blit(sprite.image, camera.apply(sprite))

    pygame.display.flip()

pygame.quit()