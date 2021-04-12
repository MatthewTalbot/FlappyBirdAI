import pygame
import neat
import time
import os
import random
pygame.font.init()

WIN_WIDTH = 500
WIN_HEIGHT = 800
BIRD_IMGS = [pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bird1.png"))), pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bird2.png"))), pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bird3.png")))]
PIPE_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "pipe.png")))
BASE_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "base.png")))
BG_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bg.png")))
STAT_FONT = pygame.font.SysFont("comicsans", 50)

class Bird:
  IMGS = BIRD_IMGS
  MAX_ROTATION = 25
  ROTATE_VEL = 20
  ANIMATION_TIME = 5

  def __init__(self, x, y):
    self.x = x
    self.y = y
    self.tilt = 0
    self.tick_count = 0
    self.vel = 0
    self.height = self.y
    self.img_count = 0
    self.img = self.IMGS[0]
  
  def jump(self):
    self.vel = -10.5
    self.tick_count = 0
    self.height = self.y
  
  def move(self):
    self.tick_count += 1

    displacement = self.vel*self.tick_count + 1.5*self.tick_count**2

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
        self.tilt -= self.ROTATE_VEL

  def draw(self, win):
    self.img_count += 1

    if self.img_count < self.ANIMATION_TIME:
      self.img = self.IMGS[0]
    elif self.img_count < self.ANIMATION_TIME*2:
      self.img = self.IMGS[1]
    elif self.img_count < self.ANIMATION_TIME*3:
      self.img = self.IMGS[2]
    elif self.img_count < self.ANIMATION_TIME*4:
      self.img = self.IMGS[1]
    elif self.img_count < self.ANIMATION_TIME*4 + 1:
      self.img = self.IMGS[0]
      self.img_count = 0
    
    if self.tilt <= -80:
      self.img = self.IMGS[1]
      self.img_count = self.ANIMATION_TIME*2
    
    rotated_img = pygame.transform.rotate(self.img, self.tilt)
    new_rect = rotated_img.get_rect(center = self.img.get_rect(topleft = (self.x, self.y)).center)
    win.blit(rotated_img, new_rect.topleft)
  
  def get_mask(self):
    return pygame.mask.from_surface(self.img)

class Pipe:
  def __init__(self, x, gap):
    self.x = x
    self.height = 0
    self.gap = gap
    self.top = 0
    self.bottom = 0
    self.PIPE_TOP = pygame.transform.flip(PIPE_IMG, False, True)
    self.PIPE_BOTTOM = PIPE_IMG

    self.passed = False
    self.set_height()
  
  def set_height(self):
    self.height = random.randrange(50,450)
    self.top = self.height - self.PIPE_TOP.get_height()
    self.bottom = self.height + self.gap

  def move(self, velocity):
    self.x -= velocity

  def draw(self, win):
    win.blit(self.PIPE_TOP, (self.x, self.top))
    win.blit(self.PIPE_BOTTOM, (self.x, self.bottom))
  
  def collision(self, bird):
    bird_mask = bird.get_mask()
    top_mask = pygame.mask.from_surface(self.PIPE_TOP)
    bottom_mask = pygame.mask.from_surface(self.PIPE_BOTTOM)

    top_offset = (self.x - bird.x, self.top - round(bird.y))
    bottom_offset = (self.x - bird.x, self.bottom - round(bird.y))

    bottom_point = bird_mask.overlap(bottom_mask, bottom_offset)
    top_point = bird_mask.overlap(top_mask, top_offset)

    if top_point or bottom_point:
      return True
    
    return False

class Base:
  WIDTH = BASE_IMG.get_width()
  IMG = BASE_IMG

  def __init__(self, y):
    self.y = y
    self.x1 = 0
    self.x2 = self.WIDTH

  def move(self, velocity):
    self.x1 -= velocity
    self.x2 -= velocity

    if self.x1 + self.WIDTH < 0:
      self.x1 = self.x2 + self.WIDTH
    
    if self.x2 + self.WIDTH < 0:
      self.x2 = self.x1 + self.WIDTH
  
  def draw(self, win):
    win.blit(self.IMG, (self.x1, self.y))
    win.blit(self.IMG, (self.x2, self.y))

class Game:
  def __init__(self):
    self.win = pygame.display.set_mode((WIN_WIDTH,WIN_HEIGHT))
    self.bird = Bird(220, 350)
    self.base = Base(730)
    self.gap = 500
    self.pipes = [Pipe(600, self.gap)]
    self.score = 0
    self.generation = 0
    self.end_game_score = 0
    self.velocity = 5
    self.clock = pygame.time.Clock()
    self.play_game = STAT_FONT.render("Play Game", 1, (255,255,255))
    self.genetic_ai = STAT_FONT.render("Genetic AI", 1, (255,255,255))
    self.play_again = STAT_FONT.render("Play Again", 1, (255,255,255))
    self.quit = STAT_FONT.render("Quit", 1, (255,255,255))
  
  def reset(self):
    self.clock = pygame.time.Clock()
    self.bird.y = 350
    self.bird.tilt = 0
    self.bird = Bird(220, 350)
    self.base = Base(730)
    self.gap = 500
    self.pipes = [Pipe(600, self.gap)]
    self.score = 0
    self.velocity = 5
    
  
  def ai_reset(self):
    self.clock = pygame.time.Clock()
    self.win = pygame.display.set_mode((WIN_WIDTH,WIN_HEIGHT))
    self.base = Base(730)
    self.gap = 500
    self.pipes = [Pipe(600, self.gap)]
    self.score = 0
    self.velocity = 5
    
  
  def is_play_game_hovered(self, mouse):
    if mouse[0] >= WIN_WIDTH/2 - self.play_game.get_width()/2 and mouse[0] <= WIN_WIDTH/2 - self.play_game.get_width()/2 + self.play_game.get_width() and mouse[1] >= 200 and mouse[1] <= 200 + self.play_game.get_height():
      return True
    return False
  
  def is_genetic_ai_hovered(self, mouse):
    if mouse[0] >= WIN_WIDTH/2 - self.genetic_ai.get_width()/2 and mouse[0] <= WIN_WIDTH/2 - self.genetic_ai.get_width()/2 + self.genetic_ai.get_width() and mouse[1] >= 250 and mouse[1] <= 250 + self.genetic_ai.get_height():
      return True
    return False
  
  def is_start_quit_hovered(self, mouse):
    if mouse[0] >= WIN_WIDTH/2 - self.quit.get_width()/2 and mouse[0] <= WIN_WIDTH/2 - self.quit.get_width()/2 + self.quit.get_width() and mouse[1] >= 300 and mouse[1] <= 300 + self.quit.get_height():
      return True
    return False
  
  def is_game_over_quit_hovered(self, mouse):
    if mouse[0] >= WIN_WIDTH/2 - self.quit.get_width()/2 and mouse[0] <= WIN_WIDTH/2 - self.quit.get_width()/2 + self.quit.get_width() and mouse[1] >= 250 and mouse[1] <= 250 + self.quit.get_height():
      return True
    return False
  
  def is_play_again_hovered(self, mouse):
    if mouse[0] >= WIN_WIDTH/2 - self.play_again.get_width()/2 and mouse[0] <= WIN_WIDTH/2 - self.play_again.get_width()/2 + self.play_again.get_width() and mouse[1] >= 200 and mouse[1] <= 200 + self.play_again.get_height():
      return True
    return False

  def draw_game_window(self):
    self.win.blit(BG_IMG, (0,0))
    for pipe in self.pipes:
      pipe.draw(self.win)
    text = STAT_FONT.render("Score: " + str(self.score), 1, (255,255,255))
    self.win.blit(text, (WIN_WIDTH - 10 - text.get_width(), 10))
    self.base.draw(self.win)
    self.bird.draw(self.win)
    pygame.display.update()
  
  def draw_genetic_ai_game_window(self, birds):
    self.win.blit(BG_IMG, (0,0))
    for pipe in self.pipes:
      pipe.draw(self.win)

    generation = STAT_FONT.render("Generation: " + str(self.generation), 1, (255,255,255))
    birds_remaining = STAT_FONT.render("Birds: " + str(len(birds)), 1, (255,255,255))
    score = STAT_FONT.render("Score: " + str(self.score), 1, (255,255,255))
    self.win.blit(score, (WIN_WIDTH - 10 - score.get_width(), 10))
    self.win.blit(generation, (10, 10))
    self.win.blit(birds_remaining, (11, 15 + birds_remaining.get_height()))
    for bird in birds:
      bird.draw(self.win)
    self.base.draw(self.win)
    pygame.display.update()

  def draw_start_screen_window(self, mouse):
    self.win.blit(BG_IMG, (0,0))
    
    self.play_game = STAT_FONT.render("Play Game", 1, (255,255,255))
    self.genetic_ai = STAT_FONT.render("Genetic AI", 1, (255,255,255))
    self.quit = STAT_FONT.render("Quit", 1, (255,255,255))
    game_name = STAT_FONT.render("Flappy Bird", 1, (255,255,255))

    if self.is_play_game_hovered(mouse):
      self.play_game = STAT_FONT.render("Play Game", 1, (100,100,100))
    if self.is_genetic_ai_hovered(mouse):
      self.genetic_ai = STAT_FONT.render("Genetic AI", 1, (100,100,100))
    if self.is_start_quit_hovered(mouse):
      self.quit = STAT_FONT.render("Quit", 1, (100,100,100))

    self.win.blit(game_name, (WIN_WIDTH/2 - game_name.get_width()/2, 100))
    self.win.blit(self.play_game, (WIN_WIDTH/2 - self.play_game.get_width()/2, 200))
    self.win.blit(self.genetic_ai, (WIN_WIDTH/2 - self.genetic_ai.get_width()/2, 250))
    self.win.blit(self.quit, (WIN_WIDTH/2 - self.quit.get_width()/2, 300))
    self.base.draw(self.win)
    self.bird.draw(self.win)
    pygame.display.update()
  
  def game_over_screen_window(self, mouse):
    self.win.blit(BG_IMG, (0,0))
    game_over = STAT_FONT.render("Game Over", 1, (255,255,255))
    score_text = STAT_FONT.render("Score: " + str(self.end_game_score), 1, (255,255,255))
    self.play_again = STAT_FONT.render("Play Again", 1, (255,255,255))
    self.quit = STAT_FONT.render("Quit", 1, (255,255,255))
    if self.is_game_over_quit_hovered(mouse):
      self.quit = STAT_FONT.render("Quit", 1, (100,100,100))
    if self.is_play_again_hovered(mouse):
      self.play_again = STAT_FONT.render("Play Again", 1, (100,100,100))

    self.win.blit(game_over, (WIN_WIDTH/2 - game_over.get_width()/2, 100))
    self.win.blit(score_text, (WIN_WIDTH/2 - score_text.get_width()/2, 150))
    self.win.blit(self.play_again, (WIN_WIDTH/2 - self.play_again.get_width()/2, 200))
    self.win.blit(self.quit, (WIN_WIDTH/2 - self.quit.get_width()/2, 250))
    
    self.base.draw(self.win)
    self.bird.draw(self.win)
    pygame.display.update()

  def set_difficulty(self):
    if self.score % 10 == 0 and self.score > 0:
        self.velocity += 1
        self.gap -= 60

    if self.velocity >= 10:
      self.velocity = 10

    if self.gap <= 200:
      self.gap = 200

  def generate_pipes(self):
    rem = []
    add_pipe = False
    for pipe in self.pipes:
      if pipe.collision(self.bird):
        self.end_game_score = self.score
        self.reset()
        self.game_over_screen()
      
      if pipe.x + pipe.PIPE_TOP.get_width() < 0:
        rem.append(pipe)
      
      if not pipe.passed and pipe.x < self.bird.x:
        pipe.passed = True
        add_pipe = True

      pipe.move(self.velocity)
    
    if add_pipe:
      self.score += 1
      self.set_difficulty()
      self.pipes.append(Pipe(600, self.gap))

    for r in rem:
      self.pipes.remove(r)

  def generate_ai_pipes(self, birds, nets, ge):
    rem = []
    add_pipe = False
    for pipe in self.pipes:
      for x, bird in enumerate(birds):
        if pipe.collision(bird):
          ge[x].fitness -= 1
          nets.pop(x)
          ge.pop(x)
          birds.pop(x)

        if not pipe.passed and pipe.x < bird.x:
          pipe.passed = True
          add_pipe = True

      if pipe.x + pipe.PIPE_TOP.get_width() < 0:
        rem.append(pipe)
          
      pipe.move(self.velocity)
    
    if add_pipe:
      self.score += 1
      self.set_difficulty()
      for g in ge:
        g.fitness += 5
      self.pipes.append(Pipe(600, self.gap))

    for r in rem:
      self.pipes.remove(r)

  def player_start_game(self):
    run = True
    while run:
      self.clock.tick(30)

      for event in pygame.event.get():
        if event.type == pygame.KEYDOWN:
          if event.key == pygame.K_SPACE or event.key == pygame.K_UP:
            self.bird.jump()
        if event.type == pygame.MOUSEBUTTONDOWN:
          self.bird.jump()

      self.bird.move()
      self.generate_pipes()
      if self.bird.y + self.bird.img.get_height() >= 730 or self.bird.y < 0:
        self.end_game_score = self.score
        self.reset()
        self.game_over_screen()
        
      self.base.move(self.velocity)
      self.draw_game_window()
  
  def genetic_ai_fitness(self, genomes, config):
    run = True
    birds = []
    nets = []
    ge = []
    self.ai_reset()
    self.generation += 1
    for _, g in genomes:
      net = neat.nn.FeedForwardNetwork.create(g, config)
      nets.append(net)
      birds.append(Bird(220, 350))
      g.fitness = 0
      ge.append(g)
    
    while run and len(birds) > 0:
      self.clock.tick(30)
      for event in pygame.event.get():
        if event.type == pygame.QUIT:
          quit()

      pipe_ind = 0
      if len(self.pipes) > 1 and birds[0].x > self.pipes[0].x + self.pipes[0].PIPE_TOP.get_width():
        pipe_ind = 1
      
      for x, bird in enumerate(birds):
        bird.move()
        ge[x].fitness += 0.1
        output = nets[x].activate((bird.y, abs(bird.y - self.pipes[pipe_ind].height), abs(bird.y - self.pipes[pipe_ind].bottom)))

        if output[0] > 0.5:
          bird.jump()
      
      
      self.generate_ai_pipes(birds, nets, ge)
      for x, bird in enumerate(birds):
        if bird.y + bird.img.get_height() >= 730 or bird.y < 0:
          nets.pop(x)
          ge.pop(x)
          birds.pop(x)
      
      if self.score == 500:
        break

      self.base.move(self.velocity)
      self.draw_genetic_ai_game_window(birds)
        
  def genetic_ai_start_game(self, config_path):
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction, neat.DefaultSpeciesSet, neat.DefaultStagnation, config_path)
    population = neat.Population(config)
    population.add_reporter(neat.StdOutReporter(True))
    population_stats = neat.StatisticsReporter()
    population.add_reporter(population_stats)
    winner = population.run(self.genetic_ai_fitness, 100)

    print("\nBest Bird!\n{!s}".format(winner))
    self.generation = 0
    self.start_screen()

  def load_config(self):
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, "genetic-config.txt")
    self.genetic_ai_start_game(config_path)

  def start_screen(self):
    run = True
    while run:
      self.clock.tick(30)
      mouse = pygame.mouse.get_pos()
      for event in pygame.event.get():
        if event.type == pygame.QUIT:
          quit()
        if event.type == pygame.MOUSEBUTTONDOWN and self.is_play_game_hovered(mouse):
          self.player_start_game()
        
        if event.type == pygame.MOUSEBUTTONDOWN and self.is_genetic_ai_hovered(mouse):
          self.load_config()
        
        if event.type == pygame.MOUSEBUTTONDOWN and self.is_start_quit_hovered(mouse):
          quit()
      self.base.move(self.velocity)
      self.draw_start_screen_window(mouse)

  def game_over_screen(self):
    run = True
    while run:
      self.clock.tick(30)
      mouse = pygame.mouse.get_pos()
      for event in pygame.event.get():
        if event.type == pygame.QUIT:
          run = False
          pygame.quit()
          quit()
        
        if event.type == pygame.MOUSEBUTTONDOWN and self.is_play_again_hovered(mouse):
          self.player_start_game()

        if event.type == pygame.MOUSEBUTTONDOWN and self.is_game_over_quit_hovered(mouse):
          quit()

      self.base.move(self.velocity)
      self.game_over_screen_window(mouse)
    

def main():
  game = Game()
  game.start_screen()

main()