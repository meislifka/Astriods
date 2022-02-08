import pygame
import os
import time
import random
pygame.font.init()

#https://youtu.be/Q-__8Xw9KTM?t=1389 

WIDTH,HEIGHT = 1500,800
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Shooter")

#load images
RED_SHIP = pygame.image.load(os.path.join("assets", "pixel_ship_red_small.png"))
GREEN_SHIP = pygame.image.load(os.path.join("assets", "pixel_ship_green_small.png"))
BLUE_SHIP = pygame.image.load(os.path.join("assets", "pixel_ship_blue_small.png"))

#Player ship
YELLOW_SHIP = pygame.image.load(os.path.join("assets", "pixel_ship_yellow.png"))

#Asteroid
ASTEROID = pygame.image.load(os.path.join("assets", "asteroid.png"))

# Lasers
RED_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_red.png"))
GREEN_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_green.png"))
BLUE_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_blue.png"))
YELLOW_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_yellow.png"))

# Background
BG = pygame.transform.scale(pygame.image.load(os.path.join("assets", "background-black.png")), (WIDTH, HEIGHT))

#logo
logo = pygame.image.load(os.path.join("assets", "z.png"))

class Laser: 
    def __init__(self, x,y,img):
        self.x = x
        self.y = y
        self.img = img
        self.mask = pygame.mask.from_surface(self.img)

    def draw(self, window):
        window.blit(self.img,(self.x,self.y))
    
    def move(self,vel):
        self.y +=vel
    

    def off_screen(self,height):
        return not(self.y<=height and self.y >=0)
    
    def collision(self, obj):
        return collide(obj,self)
    
class Ship:
    COOLDOWN = 30 #1/2 a second
    def __init__(self,x,y,health = 100):
        self.x = x
        self.y = y
        self.health = health
        self.ship_img = None
        self.laser_img = None
        self.astroid_img = None
        self.lasers = []
        self.cool_down_counter = 0

    def draw(self,window):
        window.blit(self.ship_img,(self.x,self.y))
        for laser in self.lasers:
            laser.draw(window)

    def move_lasers(self, vel,obj): #when move laser, check for collosion with player
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)
            elif laser.collision(obj):
                obj.health -=10
                self.lasers.remove(laser)

    def cooldown(self):
        if self.cool_down_counter >= self.COOLDOWN:
            self.cool_down_counter =0
        elif self.cool_down_counter > 0:
            self.cool_down_counter +=1

    def shoot(self):
        if self.cool_down_counter ==0:
            laser = Laser(self.x,self.y, self.laser_img) #create new laser and add to laser list
            self.lasers.append(laser)
            self.cool_down_counter = 1
    
    def get_width(self):
        return self.ship_img.get_width()
    
    def get_height(self):
        return self.ship_img.get_height()

class Player(Ship):
    def __init__(self,x,y,health = 100):
        super().__init__(x,y,health) #super is parent class ship and use initalization method from ship
        self.ship_img = YELLOW_SHIP
        self.laser_img = YELLOW_LASER   

        #mask which allows perfect pixel collision
        self.mask = pygame.mask.from_surface(self.ship_img)
        self.max_health = health

    def move_lasers(self, vel,objs): #when move laser, check for collosion any ship
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)
            else:
                for obj  in objs:
                    if laser.collision(obj): #if laser colided with that object remove the object and laser
                        objs.remove(obj)
                        if laser in self.lasers:
                            self.lasers.remove(laser)     
    #overriding draw 
    def draw(self,window):
        super().draw(window)
        self.healthbar(window)

    def healthbar(self,window):
        pygame.draw.rect(window, (255,0,0), (self.x, self.y + self.ship_img.get_height() + 10, self.ship_img.get_width(), 10)) #makes sure healthbar is below player
        pygame.draw.rect(window, (0,255,0), (self.x, self.y + self.ship_img.get_height() + 10, self.ship_img.get_width() * (self.health/self.max_health), 10)) #drawing green over the red rectangle and covers a percentage

class Enemy(Ship):
    COLOR_MAP = {
                "red": (RED_SHIP,RED_LASER),
                "green": (GREEN_SHIP,GREEN_LASER),
                "blue": ( BLUE_SHIP,BLUE_LASER),
                
    }

    def __init__(self,x,y,color,health = 100):
        super().__init__(x,y,health)
        self.ship_img, self.laser_img = self.COLOR_MAP[color]
        self.mask = pygame.mask.from_surface(self.ship_img)

    def move(self,vel):
        self.y += vel
    
    def shoot(self):
        if self.cool_down_counter ==0:
            laser = Laser(self.x-5,self.y-16, self.laser_img) #create new laser and add to laser list
            self.lasers.append(laser)
            self.cool_down_counter = 1

def collide(obj1,obj2):
    #based on top left hand corner

    #distance between obj1 and obj2
    offset_x = obj2.x - obj1.x
    offset_y = obj2.y - obj1.y

    #if masks are overlapping based on offset
    return obj1.mask.overlap(obj2.mask, (offset_x, offset_y)) != None

class Astroid(Ship):
    COLOR_MAP = {
                "red": (RED_SHIP,RED_LASER),
                "green": (GREEN_SHIP,GREEN_LASER),
                "blue": ( BLUE_SHIP,BLUE_LASER),
                "asteroid": (ASTEROID, BLUE_LASER)
                
    }

    def __init__(self,x,y,color,health = 100):
        super().__init__(x,y,health)
        self.ship_img, self.laser_img = self.COLOR_MAP[color]
        self.mask = pygame.mask.from_surface(self.ship_img)

    def move(self,vel):
        self.y += vel
    
    def shoot(self):
        None
    
    def moveAstL(self,vel):
        self.y +=vel
        self.x -=10

    def moveAstR(self,vel):
        self.y +=vel
        self.x +=10

        


def main():
    run = True
    FPS = 60
    level = 0
    lives = 3
    main_font = pygame.font.SysFont("comicsans",35)
    lost_font = pygame.font.SysFont("comicsnas",60)
    won_font =  pygame.font.SysFont("comicsnas",60)

    enemies = []
    wave_length = 5 #every level generate new wave
    enemy_vel = 1 #speed enemy moves down screen

    asts = []
    asteroid_vel = 1


    player_vel = 8 #player moves 5 pixels everytime key is pressed
    laser_vel = 8

    player = Player(300,630)
    clock = pygame.time.Clock()

    lost = False
    lost_count = 0

    won = False
    won_count = 0

    def redraw_window(): 
        WIN.blit(BG,(0,0)) #blit draws a surface on the window at location specificed 
        #draw text
        lives_label = main_font.render(f"Lives:{lives}",1,(255,0,0))
        level_label = main_font.render(f"Level:{level}",1,(255,255,255))
        WIN.blit(lives_label,(10,10))
        WIN.blit(level_label,(WIDTH - level_label.get_width()-10,10))

        #drawing enemies
        for enemy in enemies:
            enemy.draw(WIN)
        
        #drawing asteroids
        for ast in asts:
            ast.draw(WIN)
        
            

        player.draw(WIN)

        #lost screen
        if lost:
            lost_label = lost_font.render("You lost",1,(255,255,255))
            WIN.blit(lost_label, (WIDTH/2 - lost_label.get_width()/2, 350))

        #won screen
        if won:
            won_label = won_font.render("You won! The code is:",1,(255,255,255))
            code_label = won_font.render("2",1,(0,255,0))
            WIN.blit(won_label, (WIDTH/2 - won_label.get_width()/2, 350))
            WIN.blit(code_label, (WIDTH/2 - (won_label.get_width()/2) + won_label.get_width()+5, 350))
            for event in pygame.event.get(): # checking if an event occurs checks 60 times per second
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
        
        pygame.display.update()



    while run:
        clock.tick(FPS)
        redraw_window()
        #if we lost 
        if lives <=0 or player.health<=0:
            lost = True
            lost_count +=1
        
        if lost:
            if lost_count > FPS * 3: #shows for 3 seconds
                run = False
            else:
                continue #dont do anything below 
        
        if level ==3:
            won = True
            won_count +=1
        
        if won:
            if lost_count > FPS * 3: #shows for 3 seconds
                run = False
            else:
                continue #dont do anything below     
  

        if len(enemies) ==0:
            level +=1
            wave_length +=5 #adding more enemies each level

            for i in range(wave_length):
                #random positions to make it look like enemies are coming at different times
                enemy = Enemy(random.randrange(50,WIDTH-100),random.randrange(-1500,-100),random.choice(["red","blue","green"]))
                enemies.append(enemy)
                ast = Astroid(random.randrange(50,WIDTH-100),random.randrange(-1500,-100),random.choice(["asteroid"]))
                asts.append(ast)
        
    
                
            
           
        for event in pygame.event.get(): # checking if an event occurs checks 60 times per second
            if event.type == pygame.QUIT:
               pygame.quit()
               exit()
        keys = pygame.key.get_pressed()
        if keys[pygame.K_a] and player.x + player_vel >0: #left
            player.x -=player_vel
        if keys[pygame.K_d] and player.x + player_vel +player.get_width() <WIDTH: #right
            player.x +=player_vel
        if keys[pygame.K_w] and player.y - player_vel - 20>0: #up
            player.y -=player_vel
        if keys[pygame.K_s] and player.y + player_vel+player.get_height() +15 <HEIGHT: #down
            player.y +=player_vel
        if keys[pygame.K_RETURN]: #shoot
            player.shoot()

        for ast in asts[:]:
            left = random.randint(0,1)
            if(left == 1):
                ast.moveAstL(asteroid_vel)
            else:
                ast.moveAstR(asteroid_vel)
            if collide(ast,player): #if collides with enemy removes enemy and reduces health
                player.health -=10
                asts.remove(ast)
            elif ast.y + ast.get_height()> HEIGHT:
                
                asts.remove(ast)


        for enemy in enemies[:]:
            enemy.move(enemy_vel)
            enemy.move_lasers(laser_vel, player) #moves velocity and checks if it player

            if random.randrange(0,2*FPS ) ==1: #50 percent chance enemy will shoot a bullet (every 2 seconds)
                enemy.shoot()
           
            if collide(enemy,player): #if collides with enemy removes enemy and reduces health
                player.health -=10
                enemies.remove(enemy)
            elif enemy.y + enemy.get_height()> HEIGHT:
                lives -=1
                enemies.remove(enemy)

            
        player.move_lasers(-laser_vel, enemies)

def main_menu():
    title_font = pygame.font.SysFont("comicsans", 70)
    run = True
    while run:
        WIN.blit(BG, (0,0))
        title_label = title_font.render("Press Space bar to begin...", 1, (255,255,255))
        WIN.blit(title_label, (WIDTH/2 - title_label.get_width()/2, 350))
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            
        keys = pygame.key.get_pressed()
        if keys[pygame.K_SPACE]:
            main()
    pygame.quit()
        
main_menu() 