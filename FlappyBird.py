import pygame
import neat
import os
import random
pygame.font.init()
#Sets the window width and height and loads in all the images that our game will use. Also loads in the font type as well
WIN_WIDTH = 500
WIN_HEIGHT = 800
BIRD_IMGS = [pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bird1.png"))), pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bird2.png"))), pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bird3.png")))]
PIPE_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "pipe.png")))
BASE_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "base.png")))
BG_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bg.png")))
STAT_FONT = pygame.font.SysFont("comicsans", 50)

#Creating our bird object class
class Bird:
  #Gets the bird images, sets the max rotation of the bird and the rate at which it takes to rotate as well as the animation time
  IMGS = BIRD_IMGS
  MAX_ROTATION = 25
  ROTATE_VEL = 20
  ANIMATION_TIME = 5

  #Sets the initial x, y position of the bird as well as the tilt, the image, velocity and tick_count(acts as frames)
  def __init__(self, x, y):
    self.x = x
    self.y = y
    self.tilt = 0
    self.tick_count = 0
    self.vel = 0
    self.height = self.y
    self.img_count = 0
    self.img = self.IMGS[0]
  
  #Bird can jump up at a rate -10.5
  #Screen starts at (0,0) which means max height is 0 which is why upwards velocity is negative
  def jump(self):
    self.vel = -10.5
    self.tick_count = 0
    self.height = self.y
  
  def move(self):
    self.tick_count += 1 #Keeping track of the frames

    displacement = self.vel*self.tick_count + 1.5*self.tick_count**2 #Physics movement formula

    if displacement >= 16: #If we reach a terminal velocity cap the movement speed at 16
      displacement = 16
    
    if displacement < 0: #Fall rate 
      displacement -= 2
    
    self.y = self.y + displacement #Adjest the height of the bird based on the displacement value

    if displacement < 0 or self.y < self.height + 50: #If we are moving up tilt bird up
      if self.tilt < self.MAX_ROTATION:
        self.tilt = self.MAX_ROTATION
    
    else:
      if self.tilt > -90: #If we are moving down tilt bird down
        self.tilt -= self.ROTATE_VEL

  def draw(self, win):
    self.img_count += 1 #How many frames have we shown one bird image for

    #Determines which flappy bird image to show. This is used to make the bird look animated as we play the game
    if self.img_count < self.ANIMATION_TIME: #If the image has been shown for less than 5 frames display first image
      self.img = self.IMGS[0]
    elif self.img_count < self.ANIMATION_TIME*2: #If the image count has been shown for more than 5 but less than 10 frames display second image
      self.img = self.IMGS[1]
    elif self.img_count < self.ANIMATION_TIME*3: #If the image count has been shown for more than 10 but less than 15 frames display third image
      self.img = self.IMGS[2]
    elif self.img_count < self.ANIMATION_TIME*4: #If the image count has been shown for more than 15 but less than 20 frames display fourth image
      self.img = self.IMGS[1]
    elif self.img_count == self.ANIMATION_TIME*4 + 1: #If the image count reaches 21 then reset image to first image and reset the image count
      self.img = self.IMGS[0]
      self.img_count = 0
    
    #If the bird is in a nose dive display the second image
    if self.tilt <= -80: 
      self.img = self.IMGS[1]
      self.img_count = self.ANIMATION_TIME*2
    
    #Rotates the image based on on the tilt of the bird
    rotated_img = pygame.transform.rotate(self.img, self.tilt)
    new_rect = rotated_img.get_rect(center = self.img.get_rect(topleft = (self.x, self.y)).center)
    win.blit(rotated_img, new_rect.topleft)
  
  #Returns the mask of the bird. Used for pixel perfect collision detection
  def get_mask(self):
    return pygame.mask.from_surface(self.img)

class Pipe:
  #Initialices the distance, gap between the pipes, images for the top and bottom pipe as well as their height values
  def __init__(self, x, gap):
    self.x = x
    self.height = 0
    self.gap = gap
    self.top = 0
    self.bottom = 0
    self.PIPE_TOP = pygame.transform.flip(PIPE_IMG, False, True)
    self.PIPE_BOTTOM = PIPE_IMG

    self.passed = False #If the bird has passed the pipe
    self.set_height()
  
  def set_height(self):
    self.height = random.randrange(50,450) #Chooses a number between 50 and 450
    self.top = self.height - self.PIPE_TOP.get_height() #Sets the top pipe height
    self.bottom = self.height + self.gap #Sets the bottom pipe height

  #Moves the pipe
  def move(self, velocity):
    self.x -= velocity 

  #Draws the pipe on the screen
  def draw(self, win):
    win.blit(self.PIPE_TOP, (self.x, self.top))
    win.blit(self.PIPE_BOTTOM, (self.x, self.bottom))
  
  #Pixel perfect collision detection
  def collision(self, bird):
    bird_mask = bird.get_mask()                                     #Gets the mask image of the bird
    top_mask = pygame.mask.from_surface(self.PIPE_TOP)              #Gets the mask image of the top pipe
    bottom_mask = pygame.mask.from_surface(self.PIPE_BOTTOM)        #Gets the mask image of the bottom pipe

    top_offset = (self.x - bird.x, self.top - round(bird.y))        #Calculates how far away the top bird pixel is from the top pipe
    bottom_offset = (self.x - bird.x, self.bottom - round(bird.y))  #Calculates how far away the top bird pixel is from the bottom pipe

    bottom_point = bird_mask.overlap(bottom_mask, bottom_offset)    #Calculates if the bottom bird pixel overlaps with the bottom pipe pixel
    top_point = bird_mask.overlap(top_mask, top_offset)             #Calculates if the top bird pixel overlaps with the top pipe pixel

    #If there was an overlap it means the bird has collided with the pipe
    if top_point or bottom_point: 
      return True
    
    return False

class Base:
  WIDTH = BASE_IMG.get_width()
  IMG = BASE_IMG
  #Initialize the height of the base on the screen and the width of the base
  def __init__(self, y):
    self.y = y
    self.x1 = 0
    self.x2 = self.WIDTH

  def move(self, velocity):
    #Move the image based on the velocity
    self.x1 -= velocity 
    self.x2 -= velocity

    #We generate two base images and place one behind the other to give it a scrolling effect
    #If the first base is entirely off the screen take it and place it behind the second image
    if self.x1 + self.WIDTH < 0:
      self.x1 = self.x2 + self.WIDTH
    #If the second image is entirely off the screen take it and place it behind the first image
    if self.x2 + self.WIDTH < 0:
      self.x2 = self.x1 + self.WIDTH

  #Draw the images on the screen
  def draw(self, win):
    win.blit(self.IMG, (self.x1, self.y))
    win.blit(self.IMG, (self.x2, self.y))

class Game:
  #Initializes all of the game variables we will need
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
    self.main_menu = STAT_FONT.render("Main Menu", 1, (255,255,255))
    self.quit = STAT_FONT.render("Quit", 1, (255,255,255))
  
  #If the player wants to play again reset all of the game values relevant to them
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
  
  #When the AI goes to the next generation reset the game values relevant to them
  def ai_reset(self):
    self.clock = pygame.time.Clock()
    self.win = pygame.display.set_mode((WIN_WIDTH,WIN_HEIGHT))
    self.base = Base(730)
    self.gap = 500
    self.pipes = [Pipe(600, self.gap)]
    self.score = 0
    self.velocity = 5
  
  #If certain text on the screen is hovered return true
  def is_play_game_hovered(self, mouse):
    if mouse[0] >= WIN_WIDTH/2 - self.play_game.get_width()/2 and mouse[0] <= WIN_WIDTH/2 - self.play_game.get_width()/2 + self.play_game.get_width() and mouse[1] >= 200 and mouse[1] <= 200 + self.play_game.get_height():
      return True
    return False
  
  def is_genetic_ai_hovered(self, mouse):
    if mouse[0] >= WIN_WIDTH/2 - self.genetic_ai.get_width()/2 and mouse[0] <= WIN_WIDTH/2 - self.genetic_ai.get_width()/2 + self.genetic_ai.get_width() and mouse[1] >= 250 and mouse[1] <= 250 + self.genetic_ai.get_height():
      return True
    return False
  
  def is_quit_hovered(self, mouse):
    if mouse[0] >= WIN_WIDTH/2 - self.quit.get_width()/2 and mouse[0] <= WIN_WIDTH/2 - self.quit.get_width()/2 + self.quit.get_width() and mouse[1] >= 300 and mouse[1] <= 300 + self.quit.get_height():
      return True
    return False
  
  def is_main_menu_hovered(self, mouse):
    if mouse[0] >= WIN_WIDTH/2 - self.main_menu.get_width()/2 and mouse[0] <= WIN_WIDTH/2 - self.main_menu.get_width()/2 + self.main_menu.get_width() and mouse[1] >= 250 and mouse[1] <= 250 + self.main_menu.get_height():
      return True
    return False
  
  def is_play_again_hovered(self, mouse):
    if mouse[0] >= WIN_WIDTH/2 - self.play_again.get_width()/2 and mouse[0] <= WIN_WIDTH/2 - self.play_again.get_width()/2 + self.play_again.get_width() and mouse[1] >= 200 and mouse[1] <= 200 + self.play_again.get_height():
      return True
    return False

  #Draw the game window for when a player is playing the game
  def draw_game_window(self):
    self.win.blit(BG_IMG, (0,0))
    for pipe in self.pipes:
      pipe.draw(self.win)
    text = STAT_FONT.render("Score: " + str(self.score), 1, (255,255,255))
    self.win.blit(text, (WIN_WIDTH - 10 - text.get_width(), 10))
    self.base.draw(self.win)
    self.bird.draw(self.win)
    pygame.display.update()
  
  #Draw the game window for when an ai is playing the game
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

  #Draws the menu screen for the game
  def draw_start_screen_window(self, mouse):
    self.win.blit(BG_IMG, (0,0))
    
    self.play_game = STAT_FONT.render("Play Game", 1, (255,255,255))
    self.genetic_ai = STAT_FONT.render("Genetic AI", 1, (255,255,255))
    self.quit = STAT_FONT.render("Quit", 1, (255,255,255))
    game_name = STAT_FONT.render("Flappy Bird", 1, (255,255,255))

    #IF the text is hovered we should change the color of the text
    if self.is_play_game_hovered(mouse):
      self.play_game = STAT_FONT.render("Play Game", 1, (100,100,100))
    if self.is_genetic_ai_hovered(mouse):
      self.genetic_ai = STAT_FONT.render("Genetic AI", 1, (100,100,100))
    if self.is_quit_hovered(mouse):
      self.quit = STAT_FONT.render("Quit", 1, (100,100,100))

    self.win.blit(game_name, (WIN_WIDTH/2 - game_name.get_width()/2, 100))
    self.win.blit(self.play_game, (WIN_WIDTH/2 - self.play_game.get_width()/2, 200))
    self.win.blit(self.genetic_ai, (WIN_WIDTH/2 - self.genetic_ai.get_width()/2, 250))
    self.win.blit(self.quit, (WIN_WIDTH/2 - self.quit.get_width()/2, 300))
    self.base.draw(self.win)
    self.bird.draw(self.win)
    pygame.display.update()
  
  #Draws the game over menu screen for the game
  def game_over_screen_window(self, mouse):
    self.win.blit(BG_IMG, (0,0))
    game_over = STAT_FONT.render("Game Over", 1, (255,255,255))
    score_text = STAT_FONT.render("Score: " + str(self.end_game_score), 1, (255,255,255))
    self.play_again = STAT_FONT.render("Play Again", 1, (255,255,255))
    self.main_menu = STAT_FONT.render("Main Menu", 1, (255,255,255))
    self.quit = STAT_FONT.render("Quit", 1, (255,255,255))

    #If the text is hovered change the color of the text
    if self.is_play_again_hovered(mouse):
      self.play_again = STAT_FONT.render("Play Again", 1, (100,100,100))
    if self.is_main_menu_hovered(mouse):
      self.main_menu = STAT_FONT.render("Main Menu", 1, (100,100,100))
    if self.is_quit_hovered(mouse):
      self.quit = STAT_FONT.render("Quit", 1, (100,100,100))
    

    self.win.blit(game_over, (WIN_WIDTH/2 - game_over.get_width()/2, 100))
    self.win.blit(score_text, (WIN_WIDTH/2 - score_text.get_width()/2, 150))
    self.win.blit(self.play_again, (WIN_WIDTH/2 - self.play_again.get_width()/2, 200))
    self.win.blit(self.main_menu, (WIN_WIDTH/2 - self.play_again.get_width()/2, 250))
    self.win.blit(self.quit, (WIN_WIDTH/2 - self.quit.get_width()/2, 300))
    
    self.base.draw(self.win)
    self.bird.draw(self.win)
    pygame.display.update()

  #Increases the difficulty of the game over time
  def set_difficulty(self):
    #Every 10th pipe we should: 
    if self.score % 10 == 0 and self.score > 0:
        self.velocity += 1  #Increase the velocity by 1
        self.gap -= 60      #Decrease the gap between the pipes by 60

    #If we reach a velocity of ten cap the velocity
    #Otherwise some pipes will be impossible to get through
    if self.velocity >= 10:
      self.velocity = 10

    #If the gap between pipes is less than 200 cap it
    #Otherwise the gap is too hard for birds to get through even with the AI
    if self.gap <= 200:
      self.gap = 200

  #Generates the pipes for the game
  def generate_pipes(self):
    rem = []
    add_pipe = False
    for pipe in self.pipes:
      #If we have collided with a pipe reset the game and go to the game over screen
      if pipe.collision(self.bird):
        self.end_game_score = self.score
        self.reset()
        self.game_over_screen()
      
      #If the pipe is not on the screen add it to a list to be removed
      if pipe.x + pipe.PIPE_TOP.get_width() < 0:
        rem.append(pipe)
      
      #If we passed the pipe set then we should add a new pipe
      if not pipe.passed and pipe.x < self.bird.x:
        pipe.passed = True
        add_pipe = True

      #Moves the pipe across the screen
      pipe.move(self.velocity)
    
    #If we passed the pipe we need to:
    if add_pipe:
      self.score += 1                         #Increase the score by 1
      self.set_difficulty()                   #Determine if we need to increase the difficulty 
      self.pipes.append(Pipe(600, self.gap))  #Generate a new pipe

    #Removes the pipes that are off the screen from the list
    for r in rem:
      self.pipes.remove(r)
  #Generates the pipes for the ai
  def generate_ai_pipes(self, birds, nets, ge):
    rem = []
    add_pipe = False
    for pipe in self.pipes:
      #Iterate through the list of birds
      #If a bird has collided we:
      for x, bird in enumerate(birds):
        if pipe.collision(bird):
          ge[x].fitness -= 1  #Reduce the fitness for this bird by 1
          nets.pop(x)         #Remove the NN for this bird
          ge.pop(x)           #Remove the Genome for this bird
          birds.pop(x)        #Remove the Bird from the list of birds

        #If we passed the pipe set these parameters
        if not pipe.passed and pipe.x < bird.x:
          pipe.passed = True
          add_pipe = True

      #If the pipe is not on the screen add it to a list to be removed
      if pipe.x + pipe.PIPE_TOP.get_width() < 0:
        rem.append(pipe)
      
      #Move the pipe based on the velocity
      pipe.move(self.velocity)
    
    #If we passed a pipe we should: 
    if add_pipe:
      self.score += 1                         #Increase the score
      self.set_difficulty()                   #Determine if we need to increase the difficulty
      for g in ge:                            #Reward the genomes of the birds that passed the pipe by 5
        g.fitness += 5
      self.pipes.append(Pipe(600, self.gap))  #Generate a new Pipe

    #Remove the pipes that are no longer on screen
    for r in rem:
      self.pipes.remove(r)

  #Start the game for a player
  def player_start_game(self):
    run = True
    while run:
      self.clock.tick(30) #Set the frame rate of our game to 30
      #Checks for player input
      for event in pygame.event.get():
        if event.type == pygame.KEYDOWN:
          #If player presses space or up arrow key then the bird should jump
          if event.key == pygame.K_SPACE or event.key == pygame.K_UP:
            self.bird.jump()
        #If the player clicks the left mouse button the bird should jump
        if event.type == pygame.MOUSEBUTTONDOWN:
          self.bird.jump()

      #Move the bird and generate pipes
      self.bird.move()
      self.generate_pipes()
      #If the bird hit the bottom or top of the screen then we should:
      if self.bird.y + self.bird.img.get_height() >= 730 or self.bird.y < 0:
        self.end_game_score = self.score  #Display end game score
        self.reset()                      #Reset the game
        self.game_over_screen()           #Display the game over screen
      
      #Move the base and draw the game window
      self.base.move(self.velocity)
      self.draw_game_window()
  
  #Start the game for the AI
  def genetic_ai_fitness(self, genomes, config):
    run = True
    birds = []
    nets = []
    ge = []
    self.ai_reset()       #Reset the values of the game relevant to the AI every time we are caleld
    self.generation += 1  #Increase the generation every time we are called

    #In order to setup our AI we need to:
    for _, g in genomes:
      net = neat.nn.FeedForwardNetwork.create(g, config)  #Create a feedforward NN for every bird
      nets.append(net)                                    #Add the NN to the nets array
      birds.append(Bird(220, 350))                        #Add new birds to the birds list
      g.fitness = 0                                       #Initialize the genome fitness score to 0
      ge.append(g)                                        #Add all the genomes to our genomes array

    #If we have no more birds in our list end the loop
    while run and len(birds) > 0:
      self.clock.tick(30) #Sets the frame rate for our game to 30

      #If we don't include this our OS will think the game has crashed and cause an error
      #This is the equivalent of a keep alive signal
      for event in pygame.event.get():
        if event.type == pygame.QUIT:
          quit()

      #There could be two pipes on the screen at the same time.
      #This calculates which pipe the bird should be looking at.
      pipe_ind = 0
      if len(self.pipes) > 1 and birds[0].x > self.pipes[0].x + self.pipes[0].PIPE_TOP.get_width():
        pipe_ind = 1
      
      #For each bird we should: 
      for x, bird in enumerate(birds):
        bird.move()           #Move the bird
        ge[x].fitness += 0.1  #Reward the bird for being alive
                              #Calculate if the bird should jump or not
        jump = nets[x].activate((bird.y, abs(bird.y - self.pipes[pipe_ind].height), abs(bird.y - self.pipes[pipe_ind].bottom)))

        #If the value of jump is greater than 0.5 than bird should jump
        if jump[0] > 0.5:
          bird.jump()
      
      #Generate the pipes for the game
      self.generate_ai_pipes(birds, nets, ge)
      #For each bird we should:
      for x, bird in enumerate(birds):
        if bird.y + bird.img.get_height() >= 730 or bird.y < 0: #Check if the bird crashed into the top or bottom of the screen
          ge[x].fitness -= 1  #Reduce the fitness of that genome by 1
          nets.pop(x)         #Remove the NN for this bird
          ge.pop(x)           #Remove the genome for this bird
          birds.pop(x)        #Remove this bird from the list of birds
      
      #If the AI reaches a score of 500 we assume it will go on forever and break to start the next generation
      if self.score == 500:
        break
      
      #Move the base and draw the game for the AI
      self.base.move(self.velocity)
      self.draw_genetic_ai_game_window(birds)

  #Loads in the config file from load_config and uses it to start the game with those parameters  
  def genetic_ai_start_game(self, config_path):
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction, neat.DefaultSpeciesSet, neat.DefaultStagnation, config_path) #Extracts the config contents
    population = neat.Population(config)                  #Sets how many birds will be run at the same time
    population.add_reporter(neat.StdOutReporter(True))    #Displays stats to the console
    population_stats = neat.StatisticsReporter()          #Records the stats of how each generation does
    population.add_reporter(population_stats)             #Adds the population stats to the reporter
    winner = population.run(self.genetic_ai_fitness, 100) #Runs the ai fitness function a set amount of times and records the best bird

    print("\nBest Bird!\n{!s}".format(winner))            #Prints the best bird stats to the console
    self.generation = 0                                   #Resets the generation when the AI is done running through all generations
    self.start_screen()                                   #Return to the start screen of our game when the AI is done running

  #Finds the path to the config file
  def load_config(self):
    local_dir = os.path.dirname(__file__)                       #Gets the directory we are in
    config_path = os.path.join(local_dir, "genetic-config.txt") #Creates a string of the path to the file
    self.genetic_ai_start_game(config_path)                     #Sends the config to the AI

  #Start screen of our game
  def start_screen(self):
    run = True
    while run:
      self.clock.tick(30)             #Sets the frame rate of the game to 30
      mouse = pygame.mouse.get_pos()  #Records our mouse position
      #Checking for player input
      for event in pygame.event.get():
        if event.type == pygame.QUIT:
          quit()
        #If the player clicks play game, the game starts
        if event.type == pygame.MOUSEBUTTONDOWN and self.is_play_game_hovered(mouse):
          self.player_start_game()
        
        #If the player clicks on the AI, the AI plays the game
        if event.type == pygame.MOUSEBUTTONDOWN and self.is_genetic_ai_hovered(mouse):
          self.load_config()
        
        #If the player Quits the game, end the program
        if event.type == pygame.MOUSEBUTTONDOWN and self.is_quit_hovered(mouse):
          quit()

      #Move the base and draw the game start screen
      self.base.move(self.velocity)
      self.draw_start_screen_window(mouse)

  def game_over_screen(self):
    run = True
    while run:
      self.clock.tick(30)             #Sets the frame rate of the game to 30
      mouse = pygame.mouse.get_pos()  #Records the mouse position
      for event in pygame.event.get():
        if event.type == pygame.QUIT:
          quit()
        
        #If the player clicks play again restart the game
        if event.type == pygame.MOUSEBUTTONDOWN and self.is_play_again_hovered(mouse):
          self.player_start_game()
        
        #If the main menu is clicked return to the start screen of the game
        if event.type == pygame.MOUSEBUTTONDOWN and self.is_main_menu_hovered(mouse):
          self.start_screen()

        #If the player clicks on quit end the program
        if event.type == pygame.MOUSEBUTTONDOWN and self.is_quit_hovered(mouse):
          quit()

      #Move the base and draw the game over screen
      self.base.move(self.velocity)
      self.game_over_screen_window(mouse)

#Runs the entire game
def main():
  game = Game()
  game.start_screen()

if __name__ == "__main__":
  main()