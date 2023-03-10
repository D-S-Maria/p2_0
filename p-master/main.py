import csv
import os
import sys
from random import randint, choice, random

import pygame
import pygame_textinput


def load_image(name, color_key=None):
    fullname = os.path.join('data', name)
    image = pygame.image.load(fullname).convert()

    if color_key is not None:
        if color_key == -1:
            color_key = image.get_at((0, 0))
        image.set_colorkey(color_key)
    else:
        image = image.convert_alpha()
    return image


is_paused = False
pygame.init()
pygame.mixer.init()
size = width, height = 600, 600
screen = pygame.display.set_mode(size)
FPS = 60
all_sprites = pygame.sprite.Group()
patron_sprites = pygame.sprite.Group()
meteor_sprites = pygame.sprite.Group()
mons_sprites = pygame.sprite.Group()
particle_count = 500
with open('data/levels.csv', encoding="utf8") as csvfile:
    reader = csv.DictReader(csvfile, delimiter=';', quotechar='"')
    LEVELS = sorted(reader, key=lambda x: int(x['lev']))
LEV = 0


class Player(pygame.sprite.Sprite):
    player_im = load_image('Armature_shoot_up_1.png', -1)

    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = Player.player_im
        self.rect = self.player_im.get_rect()
        self.rect.x = width // 2
        self.rect.y = height - self.rect.height - 50
        self.life = 300

    def update(self):
        keystate = pygame.key.get_pressed()  # ????????
        if keystate[pygame.K_LEFT]:
            self.rect.x -= 4
        if keystate[pygame.K_RIGHT]:
            self.rect.x += 4
        if keystate[pygame.K_UP]:
            self.rect.y -= 2
        if keystate[pygame.K_DOWN]:
            self.rect.y += 2
        if self.rect.x > width - 105:
            self.rect.x = width - 105
        if self.rect.x < 0:
            self.rect.x = 0
        if self.rect.y > height - 84:
            self.rect.y = height - 84
        if self.rect.y < 0:
            self.rect.y = 0

    def buh(self):
        buh = Bum(self.rect.x + self.rect.width // 3, self.rect.y)
        all_sprites.add(buh)
        patron_sprites.add(buh)


class Bum(pygame.sprite.Sprite):
    bum_im = load_image('bum1.png', -1)

    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = Bum.bum_im
        self.rect = self.bum_im.get_rect()
        self.rect.x = x
        self.rect.y = y

    def update(self):
        self.rect.y += -2

class AnimatedSprite(pygame.sprite.Sprite):
    def __init__(self, sheet, columns, rows, x, y):
        super().__init__(all_sprites)
        self.frames = []
        self.cut_sheet(sheet, columns, rows)
        self.cur_frame = 0
        self.image = self.frames[self.cur_frame]
        self.rect = self.rect.move(x, y)

    def cut_sheet(self, sheet, columns, rows):
        self.rect = pygame.Rect(0, 0, sheet.get_width() // columns, sheet.get_height() // rows)
        for j in range(rows):
            for i in range(columns):
                frame_location = (self.rect.w * i, self.rect.h * j)
                self.frames.append(sheet.subsurface(pygame.Rect(frame_location, self.rect.size)))

    def update(self):
        self.cur_frame = (self.cur_frame + 1) % len(self.frames)
        self.image = self.frames[self.cur_frame]



class Monster(pygame.sprite.Sprite):
    def __init__(self, img, lf):
        pygame.sprite.Sprite.__init__(self)
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.x = width // 4
        self.rect.y = 3
        self.life = lf
        self.dead = False

    def update(self):
        self.rect = self.rect.move(randint(-1, 1), randint(-1, 1))
        if self.life == 0:
            self.create_particles(self.rect.x, self.rect.y)
            self.kill()
            self.dead = True

    def create_particles(self, x, y):
        for _ in range(particle_count):
            Particle((x, y), choice(range(-50, 50)), choice(range(10, 50)))


class Particle(pygame.sprite.Sprite):
    fire = [load_image("star.png", -1)]
    for scale in (2, 5, 10, 20):
        fire.append(pygame.transform.scale(fire[0], (scale, scale)))

    def __init__(self, pos, dx, dy):
        super().__init__(all_sprites)
        self.image = choice(self.fire)
        self.rect = self.image.get_rect()
        self.velocity = [dx, dy]
        self.rect.x, self.rect.y = pos
        self.gravity = random()

    def update(self):
        self.velocity[1] += self.gravity
        self.rect.x += self.velocity[0]
        self.rect.y += self.velocity[1]
        if not self.rect.colliderect(0, 0, width, height):
            self.kill()


class Mini_monsters(pygame.sprite.Sprite):
    met_im = load_image('air-002-Novaram_48x48.png', -1)

    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = Mini_monsters.met_im
        self.rect = self.met_im.get_rect()
        self.rect.x = randint(0, width - self.rect.width)
        self.rect.y = 0
        self.x = randint(-3, 3)
        self.y = randint(1, 2)

    def update(self):
        self.rect.x += self.x
        self.rect.y += self.y
        if self.rect.x > width - self.rect.width or self.rect.x < 0 or self.rect.y > height - self.rect.height:
            self.rect.x = randint(0, width - self.rect.width)
            self.rect.y = 0
            self.x = randint(-3, 3)
            self.y = randint(1, 5)


def terminate():
    pygame.quit()
    sys.exit()


def rec_table(screen, nm, bill):
    data = {'name': nm, 'bill': bill}
    with open('data/records.csv', 'a', newline='', encoding="utf8") as f:
        writer = csv.DictWriter(
            f, fieldnames=list(data.keys()),
            delimiter=';', quoting=csv.QUOTE_NONNUMERIC)
        writer.writerow(data)
    with open('data/records.csv', encoding="utf8") as csvfile:
        reader = csv.DictReader(csvfile, delimiter=';', quotechar='"')
        b = sorted(reader, key=lambda x: int(x['bill']), reverse=True)
    table = [f'{list(i.values())[0]}  {list(i.values())[1]}' for i in b]
    clock = pygame.time.Clock()
    intro_text = table[:10]
    fon = pygame.transform.scale(load_image('nightskycolor.png'), (size))
    screen.blit(fon, (0, 0))
    font = pygame.font.Font('cd2f1-36d91_sunday.ttf', 20)
    text_coord = 130
    for line in intro_text:
        string_rendered = font.render(line, 2, pygame.Color('white'))
        intro_rect = string_rendered.get_rect()
        text_coord += 10
        intro_rect.top = text_coord
        intro_rect.x = 130
        text_coord += intro_rect.height
        screen.blit(string_rendered, intro_rect)
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN or \
                    event.type == pygame.MOUSEBUTTONDOWN:
                return
        pygame.display.flip()
        clock.tick(FPS)


def finish_screen(screen, w=False, bill=0):
    textinput = pygame_textinput.TextInputVisualizer()
    textinput.font_color = (255, 255, 255)
    textinput.cursor_color = (200, 200, 200)

    clock = pygame.time.Clock()
    if w:
        intro_text = ["????????????!", f"?????? ????????: {bill}", "?????????????? ???????? ??????:"]
    else:
        intro_text = ["Game over!", ]
    while True:
        fon = pygame.transform.scale(load_image('nightskycolor.png'), (size))
        screen.blit(fon, (0, 0))
        font = pygame.font.Font('beer-money12.ttf', 36)
        text_coord = 180
        for line in intro_text:
            string_rendered = font.render(line, 2, pygame.Color('white'))
            intro_rect = string_rendered.get_rect()
            text_coord += 10
            intro_rect.top = text_coord
            intro_rect.x = 30
            text_coord += intro_rect.height
            screen.blit(string_rendered, intro_rect)
        events = pygame.event.get()
        if w:
            textinput.update(events)
            screen.blit(textinput.surface, (330, 310))
        for event in events:
            if event.type == pygame.QUIT:
                exit()
            if w:
                if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                    rec_table(screen, textinput.value, bill)  # ???????????????? ?????????????????? ??????????????

        pygame.display.flip()
        clock.tick(FPS)


def start_screen(screen):
    clock = pygame.time.Clock()
    intro_text = ["2250 ??????...",
                  "???? ?????????????? ?????????? ?????????????????? ??????????????????!!!",
                  "???????? ???????????? ???????????? ???????? ??????????????!",
                  "?????????? ?????????? ??????????????...",
                  "...?? ???????????????? ??????????..."
                  ]
    fon = pygame.transform.scale(load_image('nightskycolor.png'), (size))
    screen.blit(fon, (0, 0))
    font = pygame.font.Font('cd2f1-36d91_sunday.ttf', 20)
    text_coord = 180
    for line in intro_text:
        string_rendered = font.render(line, 2, pygame.Color('white'))
        intro_rect = string_rendered.get_rect()
        text_coord += 10
        intro_rect.top = text_coord
        intro_rect.x = 30
        text_coord += intro_rect.height
        screen.blit(string_rendered, intro_rect)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN or \
                    event.type == pygame.MOUSEBUTTONDOWN:
                return
        pygame.display.flip()
        clock.tick(FPS)


def pause_screen(screen):
    clock = pygame.time.Clock()
    pause = pygame.Surface((size), pygame.SRCALPHA)
    pause.fill((0, 0, 255, 127))
    screen.blit(pause, (0, 0))
    font = pygame.font.Font('cd2f1-36d91_sunday.ttf', 36)
    text_coord = 180
    intro_text = ["??????????",
                  "?????? ?????????????????????? ??????????????",
                  "?????????????? 'P'"
                  ]
    for line in intro_text:
        string_rendered = font.render(line, 2, pygame.Color('white'))
        intro_rect = string_rendered.get_rect()
        text_coord += 10
        intro_rect.top = text_coord
        intro_rect.x = 30
        text_coord += intro_rect.height
        screen.blit(string_rendered, intro_rect)
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    return
        pygame.display.flip()
        clock.tick(FPS)


def new_level_screen(screen):
    clock = pygame.time.Clock()
    pause = pygame.Surface((size), pygame.SRCALPHA)
    pause.fill((0, 0, 255, 127))
    screen.blit(pause, (0, 0))
    font = pygame.font.Font('cd2f1-36d91_sunday.ttf', 36)
    text_coord = 180
    intro_text = [f"Level {LEV + 1}",
                  "?????? ?????????????????????? ??????????????",
                  "?????????????? 'Enter'"
                  ]
    for line in intro_text:
        string_rendered = font.render(line, 2, pygame.Color('white'))
        intro_rect = string_rendered.get_rect()
        text_coord += 10
        intro_rect.top = text_coord
        intro_rect.x = 30
        text_coord += intro_rect.height
        screen.blit(string_rendered, intro_rect)
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    return
        pygame.display.flip()
        clock.tick(FPS)


def main():
    global LEV
    pygame.display.set_caption("?????????????????????? ??????????!")
    clock = pygame.time.Clock()
    back = load_image('2070.jpg')
    back = pygame.transform.scale(back, (600, 600))
    back_size = back.get_rect()
    Win = False
    pl = Player()
    all_sprites.add(pl)
    m_sh = Monster(load_image(LEVELS[LEV]['monster'], -1), int(LEVELS[LEV]['monster_life']))
    m_sh_2 = Monster(load_image(LEVELS[LEV + 1]['monster'], -1), int(LEVELS[LEV + 1]['monster_life']))
    m_sh_3 = Monster(load_image(LEVELS[LEV + 2]['monster'], -1), int(LEVELS[LEV + 2]['monster_life']))
    mons_sprites.add(m_sh)
    monsters = [m_sh, m_sh_2, m_sh_3]
    all_sprites.add(m_sh)
    bill = 0
    h_im = 0
    for i in range(5):
        met = Mini_monsters()
        all_sprites.add(met)
        meteor_sprites.add(met)
    background_music = pygame.mixer.Sound(LEVELS[LEV]['sound'])
    start_screen(screen)

    running = True
    LEV = 0
    health = pygame.image.load('data\heartshealth.png')
    while running:
        background_music.play()
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    pl.buh()
                elif event.key == pygame.K_p:
                    pause_screen(screen)

        hits = pygame.sprite.groupcollide(meteor_sprites, patron_sprites, True, True)
        for _ in hits:
            met = Mini_monsters()
            all_sprites.add(met)
            meteor_sprites.add(met)
            bill += 1
        hits = pygame.sprite.spritecollide(pl, meteor_sprites, False)
        if hits:
            pl.life -= 1
            h_im = (5 - pl.life // 60) * 42
            if pl.life <= 0:
                finish_screen(screen)
                running = False

        hits = pygame.sprite.spritecollide(monsters[LEV], patron_sprites, False)
        if hits:
            monsters[LEV].life -= 1
            hits = pygame.sprite.groupcollide(patron_sprites, mons_sprites, True, False)

        screen.fill(pygame.Color("black"))
        all_sprites.draw(screen)
        all_sprites.update()
        screen.blit(back, back_size)
        all_sprites.draw(screen)
        screen.blit(health, (360, 550), (0, h_im, 283, 42))
        f1 = pygame.font.Font('beer-money12.ttf', 28)
        text1 = f1.render(f"????????: {bill}", True, (240, 240, 0))
        screen.blit(text1, (10, 10))
        text2 = f1.render(f"??????????????: {LEV + 1}", True, (240, 240, 0))
        screen.blit(text2, (450, 10))
        if monsters[LEV].dead:
            LEV += 1
            if LEV < 3:
                new_level_screen(screen)
                all_sprites.add(monsters[LEV])
                background_music.stop()
                background_music = pygame.mixer.Sound(LEVELS[LEV]['sound'])
                background_music.play()

            else:
                Win = True
                background_music.stop()
                finish_screen(screen, Win, bill)
                running = False

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()


if __name__ == "__main__":
    main()

    # ????????????
# icon = pygame.image.load("data/pics/icon32.png").convert()
# icon.set_colorkey(WHITE)
# # pygame.display.set_icon(icon)
