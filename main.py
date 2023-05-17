import pygame
import math
import shelve

width, height = 1000, 1300
Out = False

# PENDULUM
length = 450  # length of the rope of the pendulum
angle = 290  # initial and max angle
vel = 0  # velocity
Aacc = 0  # acceleration
acc_change = 0.0005

# COLORS
white = (255, 255, 255)
black = (0, 0, 0)
pink = (220, 20, 60)

# BEFORE START
pygame.init()
background = pygame.display.set_mode((width, height))
clock = pygame.time.Clock()
block_image = pygame.image.load('Images/tower_block.png')
block_length = block_image.get_height()
score = 0
ground_level = height
hit_ground = False
elevation = 0
went_up = False
unbalance_limit = block_length * 0.6
font = pygame.font.Font('freesansbold.ttf', 20)
bg = pygame.image.load("Images/towers_background.jpeg")
screenUpdate = pygame.transform.scale(bg, (width, height))
death_screenUpdate = pygame.Surface((width, height))
death_screenUpdate.fill(pink)
kaboom_sound = pygame.mixer.Sound("Sounds/minecraft-tnt-explosion.mp3")
pygame.mixer.music.load('Sounds/Nighttime-Escape.mp3')
pygame.mixer.music.play(-1)

d = shelve.open('score.txt')
max_score = d['score']  # the score is read from disk
d.close()


class block_pendulum(object):

    def __init__(self, XY, length):
        self.x = XY[0]
        self.y = XY[1]
        self.length = length

    def draw(self, bg):
        pygame.draw.lines(bg, black, False, [(width / 2, 0), (self.x, self.y)], 2)
        background.blit(block_image, (self.x - self.length / 2, self.y))


class block(object):

    def __init__(self, XY, length, falling=True, score=1, elevation=1):
        self.x = XY[0]
        self.y = XY[1]
        self.falling = falling
        self.length = length
        self.score = score
        self.elevation = elevation

    def draw(self, bg):
        background.blit(block_image, (self.x - self.length / 2, self.y))

    def collided(self, block):
        if not block.falling:
            return False
        if block.x - block.length / 2 <= self.x - self.length / 2 <= block.x + block.length / 2 and self.y + \
                self.length >= block.y:
            self.score = block.score + 1
            self.elevation = block.elevation + 1
            return True
        if block.x - block.length / 2 <= self.x + self.length / 2 <= block.x + block.length / 2 and self.y + \
                self.length >= block.y:
            self.score = block.score + 1
            self.elevation = block.elevation + 1
            return True
        return False

class death_screen(object):

    def __init__(self, death=0):
        self.death = death
        self.transparency_x = 0
        self.transparency_y = 0
        self.death_animation = False

    def play_death(self):
        if self.death_animation:
            self.transparency_x += 0.5
            self.transparency_y = -abs(self.transparency_x - 5) + 10
            death_screenUpdate.set_alpha(23.00 * self.transparency_y)
            background.blit(death_screenUpdate, (0, 0))
            if self.transparency_x >= 15:
                self.transparency_x = 0
                self.death_animation = False

    def died(self):
        self.death += 1
        pygame.mixer.Sound.play(kaboom_sound)
        if self.death < 3:
            self.transparency_x = 0
            self.death_animation = True

def angle_Length():
    length = math.sqrt(math.pow(pendulum.x - width / 2, 2) + math.pow(pendulum.y - 50, 2))
    angle = math.asin((pendulum.x - width / 2) / length)
    return (angle, length)


def get_path(length):
    pendulum.x = round(width / 2 + length * math.sin(angle))
    pendulum.y = round(50 + length * math.cos(angle))


def draw_game_over_screen():
    background.fill(black)
    font = pygame.font.SysFont('arial', 40)
    title = font.render('Game Over', True, white)
    quit_button = font.render('Press any button to exit', True, white)
    background.blit(title, (width / 2 - title.get_width() / 2, height / 2 - title.get_height() / 3))
    background.blit(quit_button, (width / 2 - quit_button.get_width() / 2, height / 1.9 +
                                  quit_button.get_height()))
    pygame.display.update()


def draw_game_menu_screen():
    background.fill(black)
    font = pygame.font.SysFont('arial', 40)
    title = font.render('Select Difficulty:', True, white)
    easy = font.render('Press 1 to select Easy', True, white)
    medium = font.render('Press 2 to select Medium', True, white)
    hard = font.render('Press 3 to select Hard', True, white)
    background.blit(title, (width / 2 - title.get_width() / 2, height / 2 - title.get_height() / 3))
    background.blit(easy, [width / 2 - easy.get_width() / 2, height / 1.9 +
                           easy.get_height()])
    background.blit(medium, [width / 2 - medium.get_width() / 2, height / 1.9 +
                             medium.get_height() + easy.get_height() + 0.5])
    background.blit(hard, [width / 2 - hard.get_width() / 2, height / 1.9 +
                           hard.get_height() + medium.get_height() + easy.get_height() + 0.5])
    pygame.display.update()


def redraw():
    #pendulum
    background.blit(screenUpdate, (0, 0))
    pendulum.draw(background)

    #blocks
    for grass_block in blocks_falling:
        grass_block.draw(background)
    for grass_block in blocks_ground:
        grass_block.draw(background)

    #scores
    text = font.render("Score:" + str(score), True, black, white)
    text_rect = text.get_rect()
    background.blit(text, text_rect)
    text = font.render("Highest Score:" + str(max_score), True, black, white)
    text_rect = text.get_rect()
    text_rect.y = 21
    background.blit(text, text_rect)

    #death
    death.play_death()
    pygame.display.update()


pendulum = block_pendulum((5, -40), block_length)  # I start the class with some random coordinates
blocks_falling = []
blocks_ground = []

last = 0

mouse_click_limit = 500  # in ms

diff_found = False

death = death_screen()

while True:
    clock.tick(120)
    draw_game_menu_screen()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            Out = True
            pygame.quit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_1:
                acc_change = 0.0005
                diff_found = True
                break
            if event.key == pygame.K_2:
                acc_change = 0.0015
                diff_found = True
                break
            if event.key == pygame.K_3:
                acc_change = 0.0025
                diff_found = True
                break
    if diff_found or Out:
        break

if Out:
    pygame.quit()
    exit(0)

while True:
    clock.tick(120)

    quit_game = False

    if Out:
        draw_game_over_screen()

    for event in pygame.event.get():
        if Out:
            if event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                quit_game = True
                break
        if event.type == pygame.QUIT:
            Out = True
        if event.type == pygame.MOUSEBUTTONDOWN and pygame.time.get_ticks() - last >= mouse_click_limit:
            blocks_falling.append(block((pendulum.x, pendulum.y), block_length))
            last = pygame.time.get_ticks()
    if quit_game:
        break
    if Out:
        continue

    # PENDULUM
    Aacc = -acc_change * math.sin(angle)
    vel += Aacc
    angle += vel
    get_path(length)

    tmp_blocks_falling = []

    for fall_block in blocks_falling:
        fall_block.y += 5
        removed = False
        tmp_blocks_ground = []
        kaboom = False
        for ground_block in blocks_ground:
            if fall_block.collided(ground_block):
                tmp_blocks_ground.append(fall_block)
                elevation = max(elevation, fall_block.elevation)
                if abs(ground_block.x - fall_block.x) > unbalance_limit:
                    kaboom = True
                removed = True
                break

        if fall_block.y + fall_block.length >= ground_level and not removed:
            if not hit_ground:
                tmp_blocks_ground.append(fall_block)
                hit_ground = True
                elevation = max(elevation, fall_block.elevation)
                removed = True
            elif not went_up:
                death.died()
                removed = True

        if fall_block.y >= ground_level and not removed:
            death.died()
            removed = True

        if not removed:
            tmp_blocks_falling.append(fall_block)
        else:
            if not kaboom:
                for ground_block in tmp_blocks_ground:
                    score = max(score, ground_block.score)
                blocks_ground.extend(tmp_blocks_ground)
            else:
                death.died()

    blocks_falling = tmp_blocks_falling
    if death.death == 3:
        Out = True

    if elevation >= 5:
        elevation -= 1
        for ground_block in blocks_ground:
            ground_block.y += ground_block.length
            ground_block.elevation -= 1
        went_up = True
        blocks_ground.pop(0)

    redraw()

max_score = max(max_score, score)
d = shelve.open('score.txt')
d['score'] = max_score
d.close()
pygame.quit()
