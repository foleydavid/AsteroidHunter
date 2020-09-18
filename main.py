import pygame
import time
import random
from pygame import mixer

class AsteroidHunter:

   '''CLASS VARIABLES'''
   running = True                      #GAME IS BEING PLAYED
   sensitivity = 3                     #TO ADJUST FOR COMPUTER SPEED
   bulletSpeed = 0.4 * sensitivity     #BULLET SPEED
   thrust_power = 0.05 * sensitivity   #PLAYER ACCELERATION
   lower_bound = 736                   #PLAYER MOVEMENT CUTOFF

   num_asteroids = 8                   #ASTEROID COUNT
   max_ast_speed = 1 * sensitivity     #INITIAL MAX ASTEROID SPEED - INTEGER REQUIRED
   cutoff_speed = 7                    #MAX ASTEROID SPEED - INTEGER REQUIRED
   diff_curve = 0.05                   #ASTEROID ACCELERATION

   background_speed = 0.3 * sensitivity #BACKGROUND STARTING SPEED
   max_background_speed = 4 * sensitivity

   starting_bullets = 10               #BEGINNING BULLET AMOUNT
   ammo_pack_size = 5                  #BULLETS IN EACH AMMO PACK

   '''STORING ALL ASTEROID IMAGE FILES'''
   ast_images = [
       "ast1sm.png", "ast1md.png", "ast1lg.png", "ast1xl.png",
       "ast2sm.png", "ast2md.png", "ast2lg.png", "ast2xl.png",
       "ast3sm.png", "ast3md.png", "ast3lg.png", "ast3xl.png"
   ]


   '''SET UP FUNCTIONS'''
   def __init__(self, turn):
       #SETUP GAME INFORMATION
       pygame.init()
       self.turn = turn
       self.screen = pygame.display.set_mode((1000, 800))
       self.background = pygame.image.load("fullstars.jpg")
       self.largeFont = pygame.font.Font("freesansbold.ttf", 40)
       self.smallFont = pygame.font.Font("freesansbold.ttf", 32)
       pygame.display.set_caption("Asteroid Hunter")
       icon = pygame.image.load("small ship.png")
       pygame.display.set_icon(icon)
       mixer.music.load("Escape-electronic-new-age-track.mp3")
       mixer.music.play(-1)

       #SYSTEM INFORMATION
       self.start_time = int(time.time())
       self.background_x = 0
       self.backgroundTraveled = 0
       self.asteroidsDestroyed = 0
       self.total_size = 0
       self.size_destroyed = 0
       self.num_bullets = AsteroidHunter.starting_bullets
       self.progress = 0
       self.score = 0
       self.started = False

       #INITIALIZE OBJECTS IN THE GAME
       self.setup_player()
       self.setup_bullets()
       self.respawn_ammo()
       self.setup_asteroids()

   '''INITIALIZE ALL OBJECTS IN THE GAME'''
   def setup_player(self):
       self.playerImg = pygame.image.load("ship.png")
       self.destroyed = False

       #HORIZONTAL SETUP
       self.playerX = 460
       self.xSpeed = 0
       self.x_thrust = 0

       #VERTICAL SETUP
       self.playerY = 380
       self.ySpeed = 0
       self.y_thrust = 0

   def setup_asteroids(self):
       #INITIALIZE ALL ASTEROID PROPERTIES
       self.ast_Img = []
       self.ast_size = []
       self.ast_X = []
       self.ast_Y = []
       self.ast_Xspeed = []
       self.ast_Yspeed = []
       size_images = [32, 64, 128, 256]

       #FILL IN ALL ASTEROID PROPERTIES FOR GIVEN ASTEROID COUNT
       for i in range(AsteroidHunter.num_asteroids):
           rand_ind = random.randint(0, 11)
           self.ast_Img.append(pygame.image.load(AsteroidHunter.ast_images[rand_ind]))
           self.ast_size.append(size_images[rand_ind % 4])
           self.ast_X.append(random.randint(1000, 5000))
           self.ast_Y.append(random.randint(-50, 850))
           self.ast_Xspeed.append(random.randint(5, int(10 * AsteroidHunter.max_ast_speed)) / 10)
           self.ast_Yspeed.append(random.randint(1, int(3 * AsteroidHunter.max_ast_speed)) / 10)
           if random.choice([True, False]):
               self.ast_Yspeed[i] = -1 * self.ast_Yspeed[i]

   def setup_bullets(self):
       self.bulletImg = pygame.image.load("laser.png")
       self.bulletX = []
       self.bulletY = []

   def respawn_ammo(self):
       #BEGINNING OF GAME - LOAD IMAGE/X SPEED
       if self.backgroundTraveled < 10:
           self.ammoImg = pygame.image.load("battery.png")
           self.ammoXspeed = 1 * AsteroidHunter.sensitivity

       #INITIALIZE AMMO POSITION/VERTICAL DRIFT SPEED
       self.ammoX = 8000
       self.ammoY = 400
       self.ammoYspeed = random.randint(3, 10) / 10
       if random.choice([True, False]):
           self.ammoYspeed = -1 * self.ammoYspeed

   def find_total_size(self):
       for size in self.ast_size:
           self.total_size += size

   '''CHANGE POSITION (BACKGROUND/PLAYER/ASTEROIDS/BULLETS/AMMO)'''
   def scroll_background(self):
       self.background_x -= AsteroidHunter.background_speed
       self.backgroundTraveled += AsteroidHunter.background_speed
       if self.background_x <= -1000:
           self.background_x = 0
           self.background_speed += (0.1 * AsteroidHunter.sensitivity)
       if self.background_speed > AsteroidHunter.max_background_speed:
           self.background_speed = AsteroidHunter.max_background_speed

   def update_pos(self):
       #UPDATE NEW X-SPEED AND X-POSITION
       self.xSpeed += self.x_thrust
       self.playerX += self.xSpeed

       #UPDATE NEW Y-SPEED AND Y-POSITION
       self.ySpeed += self.y_thrust
       self.playerY += self.ySpeed

       #UPPER AND LOWER PLAYER BOUNDARIES
       if self.playerY < 0:
           self.playerY = 0
           self.ySpeed = 0
       elif self.playerY > AsteroidHunter.lower_bound:
           self.playerY = AsteroidHunter.lower_bound
           self.ySpeed = 0

       #LEFT AND RIGHT PLAYER BOUNDARIES
       if self.playerX < 0:
           self.playerX = 0
           self.xSpeed = 0
       elif self.playerX > 936:
           self.playerX = 936
           self.xSpeed = 0

   def update_ast_pos(self, i):
       #UPDATE HORIZONTAL-VERTICAL POSITION/"COME BACK" IF DRIFTS OFFSCREEN
       self.ast_X[i] -= self.ast_Xspeed[i]
       self.ast_Y[i] += self.ast_Yspeed[i]
       if self.ast_Y[i] < -50 or self.ast_Y[i] > 850:
           self.ast_Yspeed[i] = -1 * self.ast_Yspeed[i]

       #RESPAWN ASTEROIDS AFTER PASSED BY
       if self.ast_X[i] < -300:
           self.ast_X[i] = random.randint(1000, 1300)
           self.ast_Xspeed[i] = random.randint(5, int(10 * int(AsteroidHunter.max_ast_speed))) / 10
           self.ast_Y[i] = random.randint(-50, 850)
           self.ast_Yspeed[i] = random.randint(1, int(3 * AsteroidHunter.max_ast_speed)) / 10

           #LIMIT ASTEROID SPEED
           if self.ast_Xspeed[i] > AsteroidHunter.cutoff_speed:
               self.ast_Xspeed[i] = AsteroidHunter.cutoff_speed

           self.max_ast_speed += (AsteroidHunter.diff_curve * AsteroidHunter.sensitivity)

   def update_bullet_pos(self, i):
       #UPDATE BULLET POSITION
       self.bulletX[i] += self.bulletSpeed

       #DELETE BULLET AFTER SCREEN EXIT - SEND FLAG
       if self.bulletX[i] > 1000:
           del self.bulletX[i]
           del self. bulletY[i]
           return True

       #BULLET WAS NOT DELETED
       return False

   def update_ammo_pos(self):
       #UPDATE AMMO POSITON
       self.ammoX -= self.ammoXspeed
       self.ammoY += self.ammoYspeed

       #DRIFT BACK TOWARD CENTER IF AMMO OFF-SCREEN
       if self.ammoY < -50 or self.ammoY > 850:
           self.ammoYspeed = -1 * self.ammoYspeed

       #RESPAWN AMMO IF PASSED BY
       if self.ammoX < -50:
           self.respawn_ammo()

   def destroy(self, i, j):
       #BULLET COLLIDED WITH ASTEROID/REMOVE BULLET
       del self.bulletX[i]
       del self.bulletY[i]

       #FOR MED/LG/XL ASTEROIDS: ADD TWO MORE ASTEROIDS OFF SLIGHTLY SMALLER SIZE
       if self.ast_size[j] == 256:
           for count in range(2):
               choice = random.choice([2, 6, 10])
               self.ast_Img.append(pygame.image.load(AsteroidHunter.ast_images[choice]))
               self.ast_size.append(128)
       elif self.ast_size[j] == 128:
           for count in range(2):
               choice = random.choice([1, 5, 9])
               self.ast_Img.append(pygame.image.load(AsteroidHunter.ast_images[choice]))
               self.ast_size.append(64)
       elif self.ast_size[j] == 64:
           for count in range(2):
               choice = random.choice([0, 4, 8])
               self.ast_Img.append(pygame.image.load(AsteroidHunter.ast_images[choice]))
               self.ast_size.append(32)
       else:
           self.size_destroyed += 32

       #ASTEROID SPLIT PARAMETERS
       vertical_offset = 15
       seperate_speed = 0.7

       # FILL IN ALL OTHER VALUES OF NEW ASTEROIDS
       if self.ast_size[j] != 32:
           for sign in [-1, 1]:
               self.ast_X.append(self.ast_X[j])
               self.ast_Y.append(self.ast_Y[j] + (sign * vertical_offset))
               self.ast_Xspeed.append(self.ast_Xspeed[j])
               self.ast_Yspeed.append(self.ast_Yspeed[j] + (sign * seperate_speed))

       #DELETE ASTEROID THAT WAS HIT
       del self.ast_Img[j]
       del self.ast_size[j]
       del self.ast_X[j]
       del self.ast_Y[j]
       del self.ast_Xspeed[j]
       del self.ast_Yspeed[j]


   '''DRAW SPRITE (PLAYER/ASTEROIDS/BULLETS/AMMO)'''
   def draw_player(self):
       self.screen.blit(self.playerImg, (int(self.playerX), int(self.playerY)))

   def draw_asteroid(self, i):
       self.screen.blit(self.ast_Img[i], (int(self.ast_X[i]), int(self.ast_Y[i])))

   def draw_bullet(self, i):
       self.screen.blit(self.bulletImg, (int(self.bulletX[i]), int(self.bulletY[i])))

   def draw_ammo(self):
       self.screen.blit(self.ammoImg, (int(self.ammoX), int(self.ammoY)))


   '''COLLISION DETECTION (PLAYER-ASTEROID/BULLET-ASTEROID/PLAYER-AMMO)'''
   def is_collision(self, i):
       #REACH VALUES
       ast_reach = self.ast_size[i] / 2
       player_reach = 32
       player_buffer = 8

       #FIND OBJECT CENTERS
       ast_xCenter = self.ast_X[i] + ast_reach
       ast_yCenter = self.ast_Y[i] + ast_reach
       player_xCenter = self.playerX + player_reach
       player_yCenter = self.playerY + player_reach

       #DISTANCE BETWEEN BOTH OBJECTS
       dist = pow(ast_xCenter - player_xCenter, 2)
       dist += pow(ast_yCenter - player_yCenter, 2)
       dist = pow(dist, 0.5)

       #EVALUATE OBJECT PROXIMITY
       if dist < ast_reach + player_reach - player_buffer:
           return True
       return False

   def is_bullet_collision(self, i, j):
       #REACH VALUES
       bullet_reach = 32
       bullet_xCenter = self.bulletX[i] + bullet_reach
       bullet_yCenter = self.bulletY[i] + bullet_reach

       #FIND OBJECT CENTERS
       ast_reach = self.ast_size[j] / 2
       ast_buffer = 0.25 * ast_reach
       ast_xCenter = self.ast_X[j] + ast_reach
       ast_yCenter = self.ast_Y[j] + ast_reach

       #DISTANCE BETWEEN BOTH OBJECTS
       dist = pow(ast_xCenter - bullet_xCenter, 2)
       dist += pow(ast_yCenter - bullet_yCenter, 2)
       dist = pow(dist, 0.5)

       #EVALUATE OBJECT PROXIMITY
       if dist < ast_reach + bullet_reach - ast_buffer:
           return True
       return False

   def capture_ammo(self):
       #REACH VALUES
       ammo_reach = 32
       player_reach = 32
       player_buffer = 8

       #FIND OBJECT CENTERS
       ammo_xCenter = self.ammoX + ammo_reach
       ammo_yCenter = self.ammoY + ammo_reach
       player_xCenter = self.playerX + player_reach
       player_yCenter = self.playerY + player_reach

       #DISTANCE BETWEEN BOTH OBJECTS
       dist = pow(ammo_xCenter - player_xCenter, 2)
       dist += pow(ammo_yCenter - player_yCenter, 2)
       dist = pow(dist, 0.5)

       #EVALUATE OBJECT PROXIMITY
       if dist < ammo_reach + player_reach - player_buffer:
           return True
       return False

   '''USER ACTIONS'''
   def user_controls(self):
       #CHECK ALL USER INPUTS
       for event in pygame.event.get():

           #EVALUATE WHICH KEY HAS BEEN PRESSED DOWN/UPDATE
           if event.type == pygame.KEYDOWN:
               if event.key == pygame.K_DOWN:
                   self.y_thrust = AsteroidHunter.thrust_power
               elif event.key == pygame.K_UP:
                   self.y_thrust = -1 * AsteroidHunter.thrust_power
               elif event.key == pygame.K_RIGHT:
                   self.x_thrust = AsteroidHunter.thrust_power
               elif event.key == pygame.K_LEFT:
                   self.x_thrust = -1 * AsteroidHunter.thrust_power

           #EVALUATE WHICH KEY HAS BEEN RELEASED/UPDATE
           if event.type == pygame.KEYUP:
               if event.key == pygame.K_UP or event.key == pygame.K_DOWN:
                   self.y_thrust = 0
               elif event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT:
                   self.x_thrust = 0
               elif event.key == pygame.K_SPACE and self.num_bullets > 0:
                   self.fire_bullet()
                   self.num_bullets -= 1

           #EXIT BUTTON HAS BEEN SELECTED
           if event.type == pygame.QUIT:
               AsteroidHunter.running = False

   def fire_bullet(self):
       #PLAY SOUND
       bullet_sound = mixer.Sound("laser.wav")
       bullet_sound.play()

       #CREATE NEW BULLET
       self.bulletX.append(self.playerX + 16)
       self.bulletY.append(self.playerY + 16)

   '''RELAY INFO TO USER'''
   def show_engine_data(self):
       #UPDATE SCORE (CANNOT DECREASE) SHOW SCORE
       if not self.destroyed and self.progress != 100:
           last_score = self.score
           self.score = max(self.asteroidsDestroyed * 100 - (int(time.time()) - self.start_time), 0)
           if last_score > self.score:
               self.score = last_score
       score_text = self.smallFont.render(f"Score: {self.score}", True, (255, 255, 255))
       self.screen.blit(score_text, (10, 10))

       #SHOW BULLETS LEFT
       bullet_text = self.smallFont.render(f"Lasers: {self.num_bullets}", True, (255, 0, 0))
       self.screen.blit(bullet_text, (10, 50))

       #UPDATE/SHOW PROGRESS
       self.progress = 100 * self.size_destroyed // self.total_size
       progress_text = self.smallFont.render(f"{self.progress}%", True, (255, 255, 255))
       self.screen.blit(progress_text, (900, 730))

   def game_over(self):
       #CHECK FOR WIN/LOSS
       if self.progress == 100:
           completion_text = self.largeFont.render("YOU WIN!", True, (255, 255, 255))
       else:
           completion_text = self.largeFont.render("YOU LOSE!", True, (255, 255, 255))
           explosion_sound = mixer.Sound("explosion.wav")
           explosion_sound.play()

       #WAIT FOR PLAYER INPUT
       while self.running:
           for event in pygame.event.get():
               if event.type == pygame.QUIT:
                   AsteroidHunter.running = False
               elif event.type == pygame.KEYUP:
                   if event.key == pygame.K_SPACE:
                      self.running = False

           #SHOW BACKGROUND/STATS/INSTRUCTIONS
           final_text = self.smallFont.render("Press [SPACE BAR] to Continue", True, (255, 255, 255))
           self.screen.blit(self.background, (0, 0))
           self.show_engine_data()
           self.screen.blit(completion_text, (400, 340))
           self.screen.blit(final_text, (260, 390))

           pygame.display.update()

   def start_game(self):
       #WAIT FOR USER TO BEGIN GAME OR QUIT
       while not self.started and self.running:
           for event in pygame.event.get():
               if event.type == pygame.QUIT:
                   AsteroidHunter.running = False
               elif event.type == pygame.KEYUP:
                   if event.key == pygame.K_SPACE:
                       self.started = True

           #DISPLAY BACKGROUND AND INSTRUCTIONS
           self.screen.blit(self.background, (0, 0))
           start_title = self.largeFont.render("ASTEROID HUNTER", True, (255, 255, 255))
           self.screen.blit(start_title, (280, 340))
           start_text = self.smallFont.render("Press [SPACE BAR] to Continue", True, (255, 255, 255))
           self.screen.blit(start_text, (230, 380))

           pygame.display.update()

   '''PLAY THE GAME (MAIN FUNCTION)'''
   def play_game(self):
       #FIND TOTAL SIZE OF ALL ASTEROIDS
       self.find_total_size()

       #ON FIRST PLAY THROUGH SHOW TITLE PAGE
       if self.turn == 1:
           self.start_game()

       #PLAY THE GAME
       while self.running:
           #UPDATE SCREEN AND LOOK FOR USER INPUT
           self.screen.blit(self.background, (int(self.background_x), 0))
           self.scroll_background()
           self.user_controls()

           #CHECK IF PLAYER HAS BEEN HIT BY ASTEROID
           for astInd, astX in enumerate(self.ast_X):
               if self.is_collision(astInd):
                   self.destroyed = True
                   self.game_over()
                   break
               else:
                   self.update_ast_pos(astInd)
                   self.draw_asteroid(astInd)

               #CHECKS IF ASTEROID WAS HIT BY EACH BULLET, SKIPS WHEN BULLET REMOVED OFF SCREEN
               for bullInd, bullX in enumerate(self.bulletX):
                   bullet_destroyed = self.update_bullet_pos(bullInd)

                   if not bullet_destroyed:
                       if self.is_bullet_collision(bullInd, astInd):
                           self.destroy(bullInd, astInd)
                           self.asteroidsDestroyed += 1
                       elif len(self.bulletX) > 0:
                           self.draw_bullet(bullInd)

           #AMMO MOVEMENT/COLLISION DETECTION
           self.update_ammo_pos()
           if self.capture_ammo():
               battery_sound = mixer.Sound("battery.wav")
               battery_sound.play()
               self.respawn_ammo()
               self.num_bullets += AsteroidHunter.ammo_pack_size
           else:
               self.draw_ammo()

           #UPDATE/DRAW PLAYER
           if not self.destroyed:
               self.update_pos()
               self.draw_player()

           #SHOW ENGINE DATA DURING GAMEPLAY
           self.show_engine_data()

           #ALL ASTEROIDS HAVE BEEN DESTROYED
           if self.progress == 100:
               self.score += 5000
               self.game_over()

           pygame.display.update()

       return AsteroidHunter.running

'''BEGIN FUNCTION CALL'''
turn = 1
response = True
while response:
   game1 = AsteroidHunter(turn)
   response = game1.play_game()
   turn += 1
