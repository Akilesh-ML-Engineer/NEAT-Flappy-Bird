import os
import random
import sys
import time
import pygame


pygame.init()
pygame.font.init()

SCREEN_WIDTH = 550
SCREEN_HEIGHT = 800
FLOOR = 740
TEXT_FONT = pygame.font.SysFont('Comic Sans MS', 30)


WIN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Flappy Bird")

# Loading the asserts
pipe_img = pygame.transform.scale2x(pygame.image.load(os.path.join("asserts", "pipe.png")))
bg_img = pygame.transform.scale2x(pygame.image.load(os.path.join("asserts", "bg.png")))
bird_img = [ pygame.transform.scale2x(pygame.image.load(os.path.join("asserts", "bird" + str(x) + ".png"))) for x in range(1, 4) ]
base_img = pygame.transform.scale2x(pygame.image.load(os.path.join("asserts", "base.png")))

def blitRotateCenter(surf, image, topleft, angle):
    rotated_image = pygame.transform.rotate(image, angle)
    new_rect = rotated_image.get_rect(center = image.get_rect(topleft = topleft).center)

    surf.blit(rotated_image, new_rect.topleft)

def draw_window(win, bird, base, pipes, screen_score):
    win.blit(bg_img, (0,0))
    for pipe in pipes:
        pipe.draw(win)
    bird.draw(win)
    base.draw(win)
    text = TEXT_FONT.render("Score: " + str(screen_score), 1, (255, 255, 255))
    win.blit(text, (SCREEN_WIDTH - 10 - text.get_width(), 10))
    pygame.display.update()

class Bird:
    MAX_ROTATION = 25       # the maximum angle (in degrees) that the bird can tilt upwards.
    ROT_VEL = 20            # the speed at which the bird tilts downwards when it starts falling.
    IMG = bird_img
    ANIMATION_TIME = 5

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.tilt = 0
        self.tick_count = 0
        self.vel = 0
        self.height = self.y
        self.img_count = 0
        self.img = self.IMG[0]

    def jump(self):
        self.vel = -10.5
        self.tick_count = 0
        self.height = self.y

    def move(self):
        self.tick_count += 1

        displacement  = self.vel*self.tick_count + 0.5*3*self.tick_count**2         # s = ut + 1/2at^2

        if displacement >= 16:
            displacement = 16
        if displacement < 0:
            displacement -= 2

        self.y = self.y + displacement

        if displacement < 0 or self.y < self.height + 50:
            if self.tilt < self.MAX_ROTATION:
                self.tilt = self.MAX_ROTATION
        else:
            if self.tilt > -90:
                self.tilt -= self.ROT_VEL

    def draw(self, win):
        self.img_count += 1

        # Animating the bird
        if self.img_count < self.ANIMATION_TIME:
            self.img = self.IMG[0]
        elif self.img_count < self.ANIMATION_TIME*2:
            self.img = self.IMG[1]
        elif self.img_count < self.ANIMATION_TIME*3:
            self.img = self.IMG[2]
        elif self.img_count < self.ANIMATION_TIME*4:
            self.img = self.IMG[1]
        elif self.img_count == self.ANIMATION_TIME*4 + 1:
            self.img = self.IMG[0]
            self.img_count = 0

        if self.tilt <= -80:
            self.img = self.IMG[1]
            self.img_count = self.ANIMATION_TIME*2

        # win.blit(self.img, (self.x, self.y))
        blitRotateCenter(win, self.img, (self.x, self.y), self.tilt)

    def get_mask(self):
        return pygame.mask.from_surface(self.img)

class Pipe:
    GAP = 200
    VEL = 5

    def __init__(self, x):
        self.x = x
        self.height = 0
        self.gap = 100
        self.top = 0
        self.bottom = 0
        self.PIPE_TOP = pygame.transform.flip(pipe_img, False, True)
        self.PIPE_BOTTOM = pipe_img
        self.passed = False
        self.set_height()

    def set_height(self):
        self.height =random.randrange(50, 450)
        self.top = self.height - self.PIPE_TOP.get_height()
        self.bottom = self.height + self.GAP

    def move(self):
        self.x -= self.VEL

    def draw(self, win):
        win.blit(self.PIPE_TOP, (self.x, self.top))
        win.blit(self.PIPE_BOTTOM, (self.x, self.bottom))

    def collide(self, bird):
        bird_mask = bird.get_mask()
        top_mask = pygame.mask.from_surface(self.PIPE_TOP)
        bottom_mask = pygame.mask.from_surface(self.PIPE_BOTTOM)

        top_offset = (self.x - bird.x, self.top - round(bird.y))
        bottom_offset = (self.x - bird.x, self.bottom - round(bird.y))

        b_point = bird_mask.overlap(bottom_mask, bottom_offset)
        t_point = bird_mask.overlap(top_mask, top_offset)

        if t_point or b_point:
            return True

        return False

class Base:
    VEL = 5
    WIDTH = base_img.get_width()
    IMG = base_img

    def __init__(self, y):
        self.y = y
        self.x1 = 0
        self.x2 = self.WIDTH

    def move(self):
        self.x1 -= self.VEL
        self.x2 -= self.VEL

        if self.x1 + self.WIDTH < 0:
            self.x1 = self.x2 + self.WIDTH

        if self.x2 + self.WIDTH < 0:
            self.x2 = self.x1 + self.WIDTH

    def draw(self, win):
        win.blit(self.IMG, (self.x1, self.y))
        win.blit(self.IMG, (self.x2, self.y))

def main():
    bird = Bird(230, 350)
    base = Base(730)

    pipes = [ Pipe(700) ]
    clock = pygame.time.Clock()

    score = 0
    add_pipe = False
    add_score = False

    run = True
    while run:
        clock.tick(30)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                sys.exit()

        # bird.move()
        base.move()
        removed = []
        for pipe in pipes:
            if pipe.collide(bird):
                pass

            if pipe.x + pipe.PIPE_TOP.get_width() < 0:
                removed.append(pipe)

            if not pipe.passed and pipe.x < bird.x:
                pipe.passed = True
                add_pipe = True
                add_score = True

            pipe.move()

        if add_pipe:
            pipes.append(Pipe(600))
        add_pipe = False

        if add_score:
            score += 1
            add_score = False

        for r in removed:
            pipes.remove(r)

        if bird.y + bird.img.get_height() >= 730:
            pass
            
        draw_window(WIN, bird, base, pipes, score)

    pygame.quit()
    quit()

if __name__ == "__main__":
    main()