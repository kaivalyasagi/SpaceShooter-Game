import pygame
import random

#Initialize pygame
pygame.init()
pygame.font.init()

#Load images
player_ship = pygame.image.load("B:\\Space Shooter\\space shooter\\images\\player.png")

enemy_red = pygame.image.load("B:\\Space Shooter\\space shooter\\images\\shipred.png")
enemy_yellow = pygame.image.load("B:\\Space Shooter\\space shooter\\images\\yellowship.png")
enemy_green = pygame.image.load("B:\\Space Shooter\\space shooter\\images\\greenship.png")

red_laser = pygame.image.load("B:\\Space Shooter\\space shooter\\images\\pixel_laser_red.png")
green_laser = pygame.image.load("B:\\Space Shooter\\space shooter\\images\\pixel_laser_green.png")
yellow_laser = pygame.image.load("B:\\Space Shooter\\space shooter\\images\\pixel_laser_yellow.png")
player_laser = pygame.image.load("B:\\Space Shooter\\space shooter\\images\\pixel_laser_blue.png")

# Display setup
back = pygame.image.load("B:\\Space Shooter\\space shooter\\images\\space.jpg") 
display_width, display_height = 1440, 860
display_screen = pygame.display.set_mode((display_width, display_height))
pygame.display.set_caption("Space Shooter!")
pygame.display.set_icon(player_ship)

#Laser class
class Laser:
    def __init__(self, x, y, img):
        self.x = x
        self.y = y
        self.img = img
        self.mask = pygame.mask.from_surface(self.img)

    def draw(self, window):
        window.blit(self.img, (self.x, self.y))

    def move(self, velocity):
        self.y += velocity

    def off_screen(self):
        return not (0 <= self.y <= display_height)
    
    def collide(self, obj):
        offset_x = obj.x - self.x
        offset_y = obj.y - self.y
        return self.mask.overlap(obj.mask, (offset_x, offset_y)) is not None
    

#Ship
class Ship:
    COOLDOWN = 30

    def __init__(self, x, y, health=100):
        self.x = x
        self.y = y
        self.health = health
        self.ship_img = None
        self.laser_img = None
        self.lasers = []
        self.cooldown_counter = 0

    def draw(self, window):
        window.blit(self.ship_img, (self.x, self.y))
        for laser in self.lasers:
            laser.draw(window)
    def collide(self, obj):
        offset_x = obj.x - self.x
        offset_y = obj.y - self.y
        return self.mask.overlap(obj.mask, (offset_x, offset_y)) is not None
    def move_lasers(self, velocity, objs):
        self.cooldown()
        for laser in self.lasers[:]:
            laser.move(velocity)
            if laser.off_screen():
                self.lasers.remove(laser)
            else:
                for obj in objs:
                    if laser.collide(obj):
                        objs.remove(obj)
                        if laser in self.lasers:
                            self.lasers.remove(laser)
                        if obj.health<=10:
                            objs.remove(obj)

    def cooldown(self):
        if self.cooldown_counter>=self.COOLDOWN:
            self.cooldown_counter=0
        elif self.cooldown_counter>0:
            self.cooldown_counter+=1

    def shoot(self):
        if self.cooldown_counter == 0:
            laser = Laser(self.x + self.get_width() // 2 - self.laser_img.get_width() // 2, self.y, self.laser_img)
            self.lasers.append(laser)
            self.cooldown_counter = 1

    def get_width(self):
        return self.ship_img.get_width()

    def get_height(self):
        return self.ship_img.get_height()
    

#Player 
class Player(Ship):
    def __init__(self, x, y, health=100):
        super().__init__(x, y, health)
        self.ship_img = player_ship
        self.laser_img = player_laser
        self.mask = pygame.mask.from_surface(self.ship_img)
        self.max_health = health
    def health_bar(self,window):
        pygame.draw.rect(window,(255,0,0),(self.x,self.y+self.ship_img.get_height()+10,self.ship_img.get_width(),10))
        pygame.draw.rect(window,(0,255,0),(self.x,self.y+self.ship_img.get_height()+10,self.ship_img.get_width()*(self.health/self.max_health),10))
    def draw(self,window):
        super().draw(window)
        self.health_bar(window)
#Enemy 
class Enemy(Ship):
    COLOR_MAP = {
        "red": (enemy_red, red_laser),
        "yellow": (enemy_yellow, yellow_laser),
        "green": (enemy_green, green_laser)
    }

    def __init__(self, x, y, color, health=100):
        super().__init__(x, y, health)
        self.ship_img, self.laser_img = self.COLOR_MAP[color]
        self.mask = pygame.mask.from_surface(self.ship_img)

    def move(self, velocity):
        self.y += velocity

    def move_lasers(self, velocity, player):
        self.cooldown()
        for laser in self.lasers[:]:
            laser.move(velocity)
            if laser.off_screen():
                self.lasers.remove(laser)
            elif laser.collide(player):
                player.health -= 10
                self.lasers.remove(laser)

#main
def main():
    run = True
    fps = 60
    clock = pygame.time.Clock()
    level = 0
    lives = 5
    main_font = pygame.font.SysFont("sans", 35)
    lost_font = pygame.font.SysFont("sans", 50)

    enemies = []
    wave_length = 5
    enemy_velocity = 1
    laser_velocity = 3
    player_velocity = 5
    player = Player(300, 650)

    lost = False
    lost_count = 0

    def redraw_window():
        display_screen.blit(back, (0, 0))
        for enemy in enemies:
            enemy.draw(display_screen)

        if lost:
            lost_label = lost_font.render("YOU LOST !!!", 1, (255, 0, 0))
            display_screen.blit(lost_label, (display_width / 2 - lost_label.get_width() / 2, 430))

        level_label = main_font.render(f"Level: {level}", 1, "white")
        lives_label = main_font.render(f"Lives: {lives}", 1, "white")
        display_screen.blit(lives_label, (10, 50))
        display_screen.blit(level_label, (display_width - level_label.get_width() - 10, 50))

        player.draw(display_screen)
        pygame.display.update()

    while run:
        clock.tick(fps)
        redraw_window()

        if lives <= 0 or player.health <= 0:
            lost = True
            lost_count += 1

        if lost:
            if lost_count > fps * 5:
                run = False
            else:
                continue

        if len(enemies) == 0:
            level += 1
            wave_length += 5
            for i in range(wave_length):
                enemy = Enemy(random.randrange(50, display_width - 100), random.randrange(-1500, -100), random.choice(["red", "yellow", "green"]))
                enemies.append(enemy)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

        keys = pygame.key.get_pressed()
        if keys[pygame.K_a] and player.x - player_velocity > 0:
            player.x -= player_velocity
        if keys[pygame.K_d] and player.x + player_velocity + player.get_width() < display_width:
            player.x += player_velocity
        if keys[pygame.K_s] and player.y + player_velocity + player.get_height() < display_height:
            player.y += player_velocity
        if keys[pygame.K_w] and player.y - player_velocity > 0:
            player.y -= player_velocity
        if keys[pygame.K_q]:
            player.shoot()

        for enemy in enemies[:]:
            enemy.move(enemy_velocity)
            enemy.move_lasers(laser_velocity, player)
            if random.randrange(0,2*60)==1:
                enemy.shoot()
            if enemy.collide(player):
                player.health-=10
                enemies.remove(enemy)
            if enemy.y + enemy.get_height() > display_height:
                enemies.remove(enemy)
                lives -= 1
        player.move_lasers(-laser_velocity, enemies)
#Main menu
def menu():
    run=True
    title_font=pygame.font.SysFont("Sans",50)
    while run:
        display_screen.blit(back,(0,0))
        title_label=title_font.render("Press Mouse To Begin!",1,(255,255,255))
        display_screen.blit(title_label,(display_width/2 - title_label.get_width()/2,430))
        pygame.display.update()
        for event in pygame.event.get():
            if event.type==pygame.QUIT:
                run=False
            if event.type==pygame.MOUSEBUTTONDOWN:
                main()
    pygame.quit()

menu()
