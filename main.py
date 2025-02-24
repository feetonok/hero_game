import os
import pygame
import sys

pygame.init()

FPS = 50
clock = pygame.time.Clock()
WIDTH = 550
HEIGHT = 550
screen = pygame.display.set_mode((WIDTH, HEIGHT))

all_sprites = pygame.sprite.Group()
walls = pygame.sprite.Group()
player_group = pygame.sprite.Group()


def terminate():
    pygame.quit()
    sys.exit()


def load_image(name, color_key=None):
    fullname = os.path.join('data', name)
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pygame.image.load(fullname)
    return image


def start_screen():
    intro_text = ['Перемещение Героя', '', 'Герой перемещается', 'Карта не двигается']
    background = pygame.transform.scale(load_image('fon.jpg'), (WIDTH, HEIGHT))
    screen.blit(background, (0, 0))
    font = pygame.font.Font(None, 40)
    text_coord = 100
    for line in intro_text:
        string_rendered = font.render(line, 1, pygame.Color('black'))
        intro_rect = string_rendered.get_rect()
        text_coord += 15
        intro_rect.top = text_coord
        intro_rect.x = 50
        text_coord += intro_rect.height
        screen.blit(string_rendered, intro_rect)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                return
        pygame.display.flip()
        clock.tick(FPS)


def load_level(filename):
    try:
        with open('data/' + filename, 'r') as mapFile:
            level_map = [line.strip() for line in mapFile]

        max_width = max(map(len, level_map))
        return list(map(lambda x: x.ljust(max_width, '#'), level_map))
    except FileNotFoundError as e:
        print(f'Cannot open level file: {filename}')
        print(e)
        sys.exit()


tile_image = {
    'wall': load_image('box.png'),
    'road': load_image('grass.png'),
    'player': load_image('mar.png')
}

tile_width = tile_height = 50


class Tile(pygame.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y):
        super().__init__(all_sprites)
        self.image = tile_image[tile_type]
        self.rect = self.image.get_rect().move(tile_width * pos_x, tile_height * pos_y)
        if tile_type == 'wall':
            self.add(walls)


class Player(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(player_group)
        self.image = tile_image['player']
        self.rect = self.image.get_rect().move(tile_width * pos_x + 15, tile_height * pos_y + 5)


class Camera:
    def __init__(self):
        self.dx = 0
        self.dy = 0

    def apply(self, obj):
        obj.rect.x += self.dx
        obj.rect.y += self.dy

    def update(self, target):
        self.dx = -(target.rect.x + target.rect.w // 2 - WIDTH // 2)
        self.dy = -(target.rect.y + target.rect.h // 2 - HEIGHT // 2)


def generate_map(level):
    player = None
    for y in range(len(level)):
        for x in range(len(level[y])):
            if level[y][x] == '.':
                Tile('road', x, y)
            elif level[y][x] == '#':
                Tile('wall', x, y)
            elif level[y][x] == '@':
                Tile('road', x, y)
                player = Player(x, y)
    return player


start_screen()
level_file = input("Введите имя файла с уровнем (Доступные: level1.txt, level2.txt, level3.txt): ")
cur_level = load_level(level_file)
player = generate_map(cur_level)

camera = Camera()

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            terminate()
        elif event.type == pygame.KEYDOWN:
            new_rect = player.rect.copy()
            if event.key == pygame.K_LEFT:
                new_rect.x -= tile_width
            elif event.key == pygame.K_RIGHT:
                new_rect.x += tile_width
            elif event.key == pygame.K_UP:
                new_rect.y -= tile_height
            elif event.key == pygame.K_DOWN:
                new_rect.y += tile_height

            if not pygame.sprite.spritecollideany(player, walls,
                                                  collided=lambda spr, wall: new_rect.colliderect(wall.rect)):
                player.rect = new_rect

    camera.update(player)
    for sprite in all_sprites:
        camera.apply(sprite)
    for sprite in player_group:
        camera.apply(sprite)

    screen.fill((0, 0, 0))
    all_sprites.draw(screen)
    player_group.draw(screen)
    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()