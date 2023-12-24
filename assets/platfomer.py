import os
import random
import math
import pygame
import sys
import pygame.font
from os import listdir
from os.path import isfile, join

pygame.init()

pygame.display.set_caption("UEH Journey")
icon = pygame.image.load('C:\\Users\\ADMIN\\OneDrive\\Pictures\\Saved Pictures\\Logo_UEH_xanh.png')
pygame.display.set_icon(icon)
WIDTH, HEIGHT = 1500, 800
FPS = 60
PLAYER_VEL = 5

window = pygame.display.set_mode((WIDTH, HEIGHT))



def flip(sprites):
    return [pygame.transform.flip(sprite, True, False) for sprite in sprites]


def load_sprite_sheets(dir1, dir2, width, height, direction=False):
    path = join("assets", dir1, dir2)
    images = [f for f in os.listdir(path) if isfile(join(path, f))]

    all_sprites = {}

    for image in images:
        sprite_sheet = pygame.image.load(join(path, image)).convert_alpha()

        sprites = []
        for i in range(sprite_sheet.get_width() // width):
            surface = pygame.Surface((width, height), pygame.SRCALPHA, 32)
            rect = pygame.Rect(i * width, 0, width, height)
            surface.blit(sprite_sheet, (0, 0), rect)
            sprites.append(pygame.transform.scale2x(surface))

        if direction:
            all_sprites[image.replace(".png", "") + "_right"] = sprites
            all_sprites[image.replace(".png", "") + "_left"] = flip(sprites)
        else:
            all_sprites[image.replace(".png", "")] = sprites

    return all_sprites


def get_block(size):
    path = join("assets", "Terrain", "Terrain.png")
    image = pygame.image.load(path)
    surface = pygame.Surface((size, size), 32)
    rect = pygame.Rect(10, 0, size, size)
    surface.blit(image, (0, 0), rect) 
    return pygame.transform.scale2x(surface)


class Player(pygame.sprite.Sprite):
    COLOR = (255, 0, 0)
    GRAVITY = 1
    SPRITES = load_sprite_sheets("" "MainCharacters", "Virtual", 32, 32, True)
    ANIMATION_DELAY = 3

    def __init__(self, x, y, width, height):
        super().__init__()
        self.rect = pygame.Rect(x, y, width, height)
        self.x_vel = 0
        self.y_vel = 0
        self.mask = None
        self.direction = "left"
        self.animation_count = 0
        self.fall_count = 0
        self.jump_count = 0
        self.hit = False
        self.hit_count = 0
        self.lifepoints = 5
        self.bullet_direction = "right"  # Hướng mặc định cho đạn
        self.bullet_vel = 10  # Tốc độ mặc định cho đạn
        self.point = 0

    def giam_lifepoints(self):
        if not self.hit:
            self.lifepoints -= 1
            self.make_hit()
        if self.lifepoints <= 0:
            pygame.quit()
            sys.exit()


    def jump(self):
        self.y_vel = -self.GRAVITY * 8
        self.animation_count = 0
        self.jump_count += 1
        if self.jump_count == 1:
            self.fall_count = 0

    def move(self, dx, dy):
        self.rect.x += dx
        self.rect.y += dy

    def make_hit(self):
        self.hit = True

    def move_left(self, vel):
        self.x_vel = -vel
        self.bullet_direction = "left"
        if self.direction != "left":
            self.direction = "left"
            self.animation_count = 0

    def move_right(self, vel):
        self.x_vel = vel
        self.bullet_direction = "right"
        if self.direction != "right":
            self.direction = "right"
            self.animation_count = 0

    def loop(self, fps, enemy_sprites):
        self.y_vel += min(1, (self.fall_count / fps) * self.GRAVITY)
        self.move(self.x_vel, self.y_vel)
        if pygame.sprite.spritecollide(self, enemy_sprites, False):
            self.giam_lifepoints()
        collisions = pygame.sprite.spritecollide(self, enemy_sprites, False)
        if collisions:
            self.giam_lifepoints

        if self.hit:
            self.hit_count += 1
        if self.hit_count > fps * 2:
            self.hit = False
            self.hit_count = 0

        self.fall_count += 1
        self.update_sprite()

    def landed(self):
        self.fall_count = 0
        self.y_vel = 0
        self.jump_count = 0

    def hit_head(self):
        self.count = 0
        self.y_vel *= -1

    def update_sprite(self):
        sprite_sheet = "idle"
        if self.hit:
            sprite_sheet = "hit"
        elif self.y_vel < 0:
            if self.jump_count == 1:
                sprite_sheet = "jump"
            elif self.jump_count == 2:
                sprite_sheet = "double_jump"
        elif self.y_vel > self.GRAVITY * 2:
            sprite_sheet = "fall"
        elif self.x_vel != 0:
            sprite_sheet = "run"

        sprite_sheet_name = sprite_sheet + "_" + self.direction
        sprites = self.SPRITES[sprite_sheet_name]
        sprite_index = (self.animation_count //
                        self.ANIMATION_DELAY) % len(sprites)
        self.sprite = sprites[sprite_index]
        self.animation_count += 1
        self.update()

    def update(self):
        self.rect = self.sprite.get_rect(topleft=(self.rect.x, self.rect.y))
        self.mask = pygame.mask.from_surface(self.sprite)

    def draw(self, win, offset_x):
        win.blit(self.sprite, (self.rect.x - offset_x, self.rect.y))

    def get_bullet_direction_and_vel(self):
        return self.bullet_direction, self.bullet_vel


class Object(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, name=None):
        super().__init__()
        self.rect = pygame.Rect(x, y, width, height)
        self.image = pygame.Surface((width, height), pygame.SRCALPHA)
        self.width = width
        self.height = height
        self.name = name

    def draw(self, win, offset_x):
        win.blit(self.image, (self.rect.x - offset_x, self.rect.y))


class Block(Object):
    def __init__(self, x, y, size):
        super().__init__(x, y, size, size)
        block = get_block(size)
        self.image.blit(block, (0, 0))
        self.mask = pygame.mask.from_surface(self.image)


class Fire(Object):
    ANIMATION_DELAY = 3

    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height, "fire")
        self.fire = load_sprite_sheets("Traps", "Fire", width, height)
        self.image = self.fire["off"][0]
        self.mask = pygame.mask.from_surface(self.image)
        self.animation_count = 0
        self.animation_name = "off"

    def on(self):
        self.animation_name = "on"

    def off(self):
        self.animation_name = "off"

    def loop(self):
        sprites = self.fire[self.animation_name]
        sprite_index = (self.animation_count //
                        self.ANIMATION_DELAY) % len(sprites)
        self.image = sprites[sprite_index]
        self.animation_count += 1

        self.rect = self.image.get_rect(topleft=(self.rect.x, self.rect.y))
        self.mask = pygame.mask.from_surface(self.image)
        

        if self.animation_count // self.ANIMATION_DELAY > len(sprites):
            self.animation_count = 0





class Enemy1(pygame.sprite.Sprite):
    COLOR = (0, 0, 255)
    SPRITES = load_sprite_sheets("MainCharacters", "Black_Werewolf", 127, 128, True)
    ANIMATION_DELAY = 8

    def __init__(self, x, y, width, height):
        super().__init__()
        self.rect = pygame.Rect(x , y, width, height)
        self.x_vel = 1
        self.y_vel = 0
        self.mask = None
        self.direction = "left"
        self.animation_count = 0
        self.respawn_time = 0
        self.hit_count = 0  # Biến đếm số lần bị trúng
        self.is_hurt = False  # Biến đánh dấu việc bị tấn công
        self.is_attack = False
        self.sprite = None  # Khởi tạo sprite

    def move(self, dx, dy):
        self.rect.x += dx
        self.rect.y += dy

    def update_sprite(self):
        sprite_sheet = "Jump"
        if self.is_hurt:
            sprite_sheet = "Run+Attack"
        


        sprite_sheet_name = sprite_sheet + "_" + self.direction
        sprites = self.SPRITES[sprite_sheet_name]
        sprite_index = (self.animation_count //
                        self.ANIMATION_DELAY) % len(sprites)
        self.sprite = sprites[sprite_index]
        self.animation_count += 1

    def hurt(self):
        self.is_hurt = True

    def update(self, player):
        # Truy đuổi player
        if player.rect.x > self.rect.x:
            self.direction = "right"
            self.x_vel = 2
        else:
            self.direction = "left"
            self.x_vel = -2

        self.move(self.x_vel, 0)
        self.update_sprite()

    def draw(self, win, offset_x):
        if self.alive:
            win.blit(self.sprite, (self.rect.x - offset_x , self.rect.y - 200))

    def hit(self):
        self.hit_count += 1
        self.hurt()  # Gọi phương thức hurt khi bị tấn công
        if self.hit_count >= 2:  # Hủy enemy sau khi bị trúng 5 lần
            self.kill()

class Enemy2(pygame.sprite.Sprite):
    COLOR = (0, 255, 0)
    SPRITES = load_sprite_sheets("MainCharacters", "Karasu_tengu", 128, 129, True)
    ANIMATION_DELAY = 3
    FLYING_SPEED = 1

    def __init__(self, x, y, width, height):
        super().__init__()
        self.rect = pygame.Rect(x, y, width, height)
        self.x_vel = 0
        self.y_vel = 0
        self.mask = None
        self.direction = "left"
        self.animation_count = 0
        self.respawn_time = 0
        self.hit_count = 0

    def move(self, dx, dy):
        self.rect.x += dx
        self.rect.y += dy

    def update_sprite(self):
        sprite_sheet_name = "Jump_" + self.direction
        sprites = self.SPRITES[sprite_sheet_name]
        sprite_index = (self.animation_count //
                        self.ANIMATION_DELAY) % len(sprites)
        self.sprite = sprites[sprite_index]
        self.animation_count += 1

    def update(self, player):
        # Truy đuổi player
        if player.rect.x > self.rect.x:
            self.direction = "right"
            self.x_vel = self.FLYING_SPEED
        else:
            self.direction = "left"
            self.x_vel = -self.FLYING_SPEED

        if player.rect.y < self.rect.y:
            self.y_vel = -self.FLYING_SPEED
        elif player.rect.y > self.rect.y:
            self.y_vel = self.FLYING_SPEED
        else:
            self.y_vel = 0

        self.move(self.x_vel, self.y_vel)
        self.update_sprite()
    def hit(self):
        self.hit_count += 1
        if self.hit_count >= 1:  # Hủy enemy sau khi bị trúng 5 lần
            self.kill()  

    def draw(self, win, offset_x):
        if self.alive:
          win.blit(self.sprite, (self.rect.x - offset_x, self.rect.y - 225))

class Enemy3(pygame.sprite.Sprite):
    COLOR = (0, 0, 255)
    SPRITES = load_sprite_sheets("MainCharacters", "Yamabushi_tengu", 128, 129, True)
    ANIMATION_DELAY = 100

    def __init__(self, x, y, width, height):
        super().__init__()
        self.rect = pygame.Rect(x -2000 , y, width, height)
        self.x_vel = 1
        self.y_vel = 0
        self.mask = None
        self.direction = "left"
        self.animation_count = 0
        self.respawn_time = 0
        self.hit_count = 0  # Biến đếm số lần bị trúng
        self.is_hurt = False  # Biến đánh dấu việc bị tấn công
        self.is_attack = False
        self.sprite = None  # Khởi tạo sprite

    def move(self, dx, dy):
        self.rect.x += dx
        self.rect.y += dy

    def update_sprite(self):
        sprite_sheet = "Run"
        if self.is_hurt:
            sprite_sheet = "Hurt"
        


        sprite_sheet_name = sprite_sheet + "_" + self.direction
        sprites = self.SPRITES[sprite_sheet_name]
        sprite_index = (self.animation_count //
                        self.ANIMATION_DELAY) % len(sprites)
        self.sprite = sprites[sprite_index]
        self.animation_count += 1

    def hurt(self):
        self.is_hurt = True

    def update(self, player):
        # Truy đuổi player
        if player.rect.x > self.rect.x:
            self.direction = "right"
            self.x_vel = 1
        else:
            self.direction = "left"
            self.x_vel = -1

        self.move(self.x_vel, 0)
        self.update_sprite()

    def draw(self, win, offset_x):
        if self.alive:
            scaled_sprite = pygame.transform.scale2x(self.sprite)
            win.blit(scaled_sprite, (self.rect.x - offset_x, self.rect.y - 450))

    def hit(self):
        self.hit_count += 1
        self.hurt()  # Gọi phương thức hurt khi bị tấn công
        if self.hit_count >= 5:  # Hủy enemy sau khi bị trúng 5 lần
            self.kill()






def get_background(name):
    image = pygame.image.load(join("assets", "Background", name))
    _, _, width, height = image.get_rect()
    tiles = []

    for i in range(WIDTH // width + 1):
        for j in range(HEIGHT // height + 1):
            pos = (i * width, j * height)
            tiles.append(pos)

    return tiles, image





def handle_vertical_collision(player, objects, dy):
    collided_objects = []
    for obj in objects:
        if pygame.sprite.collide_mask(player, obj):
            if dy > 0:
                player.rect.bottom = obj.rect.top
                player.landed()
            elif dy < 0:
                player.rect.top = obj.rect.bottom
                player.hit_head()

            collided_objects.append(obj)

    return collided_objects


def collide(player, objects, dx):
    player.move(dx, 0)
    player.update()
    collided_object = None
    for obj in objects:
        if pygame.sprite.collide_mask(player, obj):
            collided_object = obj
            break

    player.move(-dx, 0)
    player.update()
    return collided_object

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, direction, vel):
        super().__init__()
        self.rect = pygame.Rect(x, y, width, height)
        self.x_vel = vel if direction == "right" else -vel  # Đặt tốc độ dựa trên hướng

    def move(self):
        self.rect.x += self.x_vel

    def draw(self, win, offset_x):
        pygame.draw.rect(win, (255, 255, 255), (self.rect.x - offset_x, self.rect.y, self.rect.width, self.rect.height))
    
    def collide_with_enemy(self, enemy):
        return pygame.sprite.collide_rect(self, enemy)


def handle_move(player, objects):
    keys = pygame.key.get_pressed()

    player.x_vel = 0
    collide_left = collide(player, objects, -PLAYER_VEL * 2)
    collide_right = collide(player, objects, PLAYER_VEL * 2)

    if keys[pygame.K_LEFT] and not collide_left:
        player.move_left(PLAYER_VEL)
    if keys[pygame.K_RIGHT] and not collide_right:
        player.move_right(PLAYER_VEL)

    vertical_collide = handle_vertical_collision(player, objects, player.y_vel)
    to_check = [collide_left, collide_right, *vertical_collide]

    for obj in to_check:
        if obj and obj.name == "fire":
            player.make_hit()

#   hàm draw để có khả năng chứa nhiều hơn 6 object
def draw(window, background, bg_image, offset_x, player, *objects_to_draw, ban_cat = None):
    for tile in background:
        window.blit(bg_image, tile)
    player.draw(window, offset_x)

    for obj in objects_to_draw:
        obj.draw(window, offset_x)
    
    if ban_cat:
        ban_cat.draw(window, offset_x)

    pygame.display.update()

enemy_sprites = pygame.sprite.Group()

font = pygame.font.Font(None, 36)
enemy_count = 0
def main(window):
    clock = pygame.time.Clock()
    background, bg_image = get_background("_9d8b7719-9392-4635-8ff5-79c9e12f3207.jpg")
    start_time = pygame.time.get_ticks()
    game_over = False
    fall_start_time = None  # Thêm một biến để theo dõi thời điểm bắt đầu rơi

    block_size = 96

    player = Player(100, 100, 50, 50)
    fire = Fire(100, HEIGHT - block_size - 64, 16, 32)
    fire.on()
    floor = [Block(i * block_size, HEIGHT - block_size, block_size)
             for i in range(-WIDTH // block_size, (WIDTH * 2) // block_size)]
    objects = [*floor, Block(0, HEIGHT - block_size * 2, block_size),
               Block(block_size * 3, HEIGHT - block_size * 4, block_size), fire]

    text_position = (10, 10)
    text_color = (255, 255, 255)

    font = pygame.font.Font(None, 36)

    enemy_sprites = pygame.sprite.Group()

    bullets = []  # Danh sách các đạn
    bullet_cooldown = 0  # Thời gian cooldown giữa các lần bắn
    BULLET_COOLDOWN_MAX = 15  # Thời gian cooldown tối đa

    offset_x = 0
    scroll_area_width = 200

    enemy_count = 0  # Thêm biến để theo dõi số enemy đã hạ

    run = True
    while run:
        clock.tick(FPS)

        current_time = pygame.time.get_ticks()
        elapsed_time = (current_time - start_time) / 1000  # Chuyển đổi thời gian thành giây

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break
            if player.lifepoints <= 0:
                game_over = True

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 3 and player.jump_count < 2:  # Kiểm tra chuột phải
                player.jump()

            if event.type == pygame.MOUSEBUTTONUP and event.button == 1 and bullet_cooldown <= 0:
                bullet_direction, bullet_vel = player.get_bullet_direction_and_vel()
                # Tạo một viên đạn mới ở vị trí của người chơi
                bullet_x = player.rect.x + player.rect.width // 2
                bullet_y = player.rect.y + player.rect.height // 2
                bullet_width = 8
                bullet_height = 8
                bullet = Bullet(bullet_x, bullet_y, bullet_width, bullet_height, bullet_direction, bullet_vel)
                bullets.append(bullet)
                bullet_cooldown = BULLET_COOLDOWN_MAX

        player.loop(FPS, enemy_sprites)
        fire.loop()

        bullets_to_remove = []
        if game_over:
            run = False
            break

        for bullet in bullets:
            bullet.move()
            for enemy in enemy_sprites:
                if bullet.collide_with_enemy(enemy):
                    bullets_to_remove.append(bullet)
                    if hasattr(enemy, 'hit') and callable(getattr(enemy, 'hit')):
                        enemy.hit()
                        enemy_count += 1  # Tăng số enemy đã hạ

        # Loại bỏ đạn từ danh sách
        bullets = [bullet for bullet in bullets if bullet not in bullets_to_remove]

        if bullet_cooldown > 0:
            bullet_cooldown -= 1

        handle_move(player, objects)
        enemy_sprites.update(player)
        draw(window, background, bg_image, offset_x, player, *objects, *bullets, *enemy_sprites)

        if ((player.rect.right - offset_x >= WIDTH - scroll_area_width) and player.x_vel > 0) or (
                (player.rect.left - offset_x <= scroll_area_width) and player.x_vel < 0):
            offset_x += player.x_vel

        if player.rect.top > HEIGHT:  # Nếu player rơi xuống màn hình
            if fall_start_time is None:
                fall_start_time = current_time
            else:
                elapsed_fall_time = (current_time - fall_start_time) / 1000
                if elapsed_fall_time > 3:
                    game_over = True
        else:
            fall_start_time = None  # Đặt lại thời điểm bắt đầu rơi khi player không rơi

        if game_over:
            run = False

        if fire.rect.colliderect(player.rect):
            player.giam_lifepoints()

        # Tạo enemy mới mỗi 5 giây
        if elapsed_time > 5:
                enemy1 = Enemy1(800, HEIGHT - block_size - 60, 32, 32)
                enemy2 = Enemy2(800, HEIGHT - block_size - 50, 32, 32)
                enemy3 = Enemy3(800, HEIGHT - block_size - 60, 32, 32)
                enemy_sprites.add(enemy1, enemy2, enemy3)
                start_time = current_time  # Cập nhật thời điểm bắt đầu cho enemy tiếp theo

        for enemy in enemy_sprites:
            enemy.update(player)
            enemy.draw(window, offset_x)

        # Vẽ số mạng
        text = font.render(f'Life: {player.lifepoints}', True, text_color)
        window.blit(text, text_position)

        # Vẽ số enemy đã hạ
        text2_position = (10, 50)
        text2 = font.render(f'Point: {enemy_count}', True, text_color)
        window.blit(text2, text2_position)

        pygame.display.flip()

    pygame.quit()
    quit()

if __name__ == "__main__":
    pygame.init()
    WIDTH, HEIGHT = 1500, 800  
    window = pygame.display.set_mode((WIDTH, HEIGHT))
    main(window)

