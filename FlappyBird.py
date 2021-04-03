import pygame
import neat
import time
import os
import random

WIN_WIDTH = 500
WIN_HEIGHT = 800
BIRD_IMGS = [pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bird1.png"))), pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bird2.png"))), pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bird3.png")))]
PIPE_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "pipe.png")))
BASE_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "base.png")))
BG_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bg.png")))

class Bird:
  def __init__(self,x,y):
    self.imgs = BIRD_IMGS
    self.max_rotation = 25
    self.rot_vel = 20
    self.animation_time = 5
    self.x = x
    self.y = y
    self.tilt = 0
    self.tick_count = 0
    self.vel = 0
    self.height = self.y #Rename self.height to self.current_height?
    self.img_count = 0 #This is to see multiple birds
    self.img = self.imgs[0]
  

  def jump(self):
    self.vel = -10.5
    self.tick_count = 0
    self.height = self.y

  def move(self):
    self.tick_count += 1
    displacement = self.vel*self.tick_count + 1.5*self.tick_count**2 #Physics formula for movement

    if displacement >= 16: #Terminal velocity
      displacement = 16

    if displacement < 0:
      displacement -= 2 #Nice number for jump. Can fine tune later

    self.y = self.y + displacement

    #Animating the tilt of the bird
    if displacement < 0 or self.y < self.height + 50:
      if self.tilt < self.max_rotation:
        self.tilt = self.max_rotation
    else:
      if self.tilt > -90:
        self.tilt -= self.rot_vel
  
  def draw(self, win):
    self.img_count += 1

    #Checks which flappy bird image to show
    if self.img_count < self.animation_time:
      self.img = self.imgs[0]
    elif self.img_count < self.animation_time*2:
      self.img = self.imgs[1]
    elif self.img_count < self.animation_time*3:
      self.img = self.imgs[2]
    elif self.img_count < self.animation_time*4:
      self.img = self.imgs[1]
    elif self.img_count == self.animation_time*4 + 1:
      self.img = self.imgs[0]
      self.img_count = 0
    
    if self.tilt <= -80:
      self.img = self.imgs[1]
      self.img_count = self.animation_time*2

    #Rotating the image based on the tilt of the bird
    rotated_img = pygame.transform.rotate(self.img, self.tilt)
    new_rect = rotated_img.get_rect(center = self.img.get_rect(topleft = (self.x, self.y)).center)
    win.blit(rotated_img, new_rect.topleft)

  def get_mask(self):
    return pygame.mask.from_surface(self.img)

def draw_window(win, bird):
  win.blit(BG_IMG, (0,0))
  bird.draw(win)
  pygame.display.update()
def main():
  bird = Bird(200, 200)
  win = pygame.display.set_mode((WIN_WIDTH,WIN_HEIGHT))
  clock = pygame.time.Clock()
  run = True

  while run:
    clock.tick(30) #Sets the frame rate
    for event in pygame.event.get():
      if event.type == pygame.QUIT: #End if we click the x at the top right of the screen
        run = False

    bird.move()
    draw_window(win, bird)
  pygame.quit()
  quit()

main()

