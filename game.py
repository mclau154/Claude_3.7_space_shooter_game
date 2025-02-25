import pygame
import random
import math
import sys
import os
from pygame import mixer 

# Initialize Pygame
pygame.init()
mixer.init()

# Set up the display
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Adventure")
last_bullet_time = 0

# Create directories for assets if they don't exist
if not os.path.exists('sounds'):
    os.makedirs('sounds')
if not os.path.exists('images'):
    os.makedirs('images')

# Load or create images
def create_ship_image():
    surface = pygame.Surface((50, 50), pygame.SRCALPHA)
    pygame.draw.polygon(surface, (0, 100, 255), [(25, 0), (0, 50), (50, 50)])
    pygame.draw.polygon(surface, (0, 200, 255), [(25, 10), (10, 40), (40, 40)])
    return surface

def create_enemy_image(color):
    surface = pygame.Surface((40, 40), pygame.SRCALPHA)
    pygame.draw.circle(surface, color, (20, 20), 20)
    pygame.draw.circle(surface, (50, 50, 50), (20, 20), 15)
    pygame.draw.circle(surface, (200, 200, 200), (10, 10), 5)
    return surface

def create_boss_image():
    surface = pygame.Surface((100, 100), pygame.SRCALPHA)
    pygame.draw.circle(surface, (255, 50, 50), (50, 50), 50)
    pygame.draw.circle(surface, (200, 0, 0), (50, 50), 40)
    pygame.draw.circle(surface, (255, 255, 0), (30, 30), 10)
    pygame.draw.circle(surface, (255, 255, 0), (70, 30), 10)
    pygame.draw.rect(surface, (150, 0, 0), (30, 70, 40, 10))
    return surface

def create_powerup_image(type_):
    surface = pygame.Surface((30, 30), pygame.SRCALPHA)
    if type_ == "shield":
        pygame.draw.circle(surface, (0, 150, 255), (15, 15), 15)
        pygame.draw.circle(surface, (100, 200, 255), (15, 15), 10)
    elif type_ == "rapid":
        pygame.draw.circle(surface, (255, 255, 0), (15, 15), 15)
        pygame.draw.rect(surface, (255, 150, 0), (10, 5, 10, 20))
    elif type_ == "multi":
        pygame.draw.circle(surface, (0, 255, 0), (15, 15), 15)
        pygame.draw.circle(surface, (150, 255, 150), (15, 15), 10)
        for angle in range(0, 360, 60):
            rad = math.radians(angle)
            x = int(15 + 12 * math.cos(rad))
            y = int(15 + 12 * math.sin(rad))
            pygame.draw.circle(surface, (0, 100, 0), (x, y), 3)
    return surface

def create_explosion_images():
    images = []
    for i in range(1, 9):
        size = i * 10
        surface = pygame.Surface((size, size), pygame.SRCALPHA)
        pygame.draw.circle(surface, (255, 200, 50), (size//2, size//2), size//2)
        pygame.draw.circle(surface, (255, 150, 0), (size//2, size//2), size//3)
        pygame.draw.circle(surface, (255, 255, 200), (size//2, size//2), size//4)
        images.append(surface)
    return images

def create_star_image():
    surface = pygame.Surface((3, 3), pygame.SRCALPHA)
    pygame.draw.circle(surface, (255, 255, 255), (1, 1), 1)
    return surface

# Load images
player_img = create_ship_image()
enemy_imgs = [create_enemy_image((255, 0, 0)), create_enemy_image((0, 255, 0)), create_enemy_image((255, 255, 0))]
boss_img = create_boss_image()
powerup_imgs = {
    "shield": create_powerup_image("shield"),
    "rapid": create_powerup_image("rapid"),
    "multi": create_powerup_image("multi")
}
explosion_imgs = create_explosion_images()
star_img = create_star_image()

# Create or load sound effects
# (In a real game, you'd have actual sound files)
shoot_sound = mixer.Sound(pygame.mixer.Sound(buffer=bytearray([i % 256 for i in range(8000)])))
explosion_sound = mixer.Sound(pygame.mixer.Sound(buffer=bytearray([(i * 10) % 256 for i in range(8000)])))
powerup_sound = mixer.Sound(pygame.mixer.Sound(buffer=bytearray([(i * 20) % 256 for i in range(8000)])))

# Set sound volumes
shoot_sound.set_volume(0.2)
explosion_sound.set_volume(0.3)
powerup_sound.set_volume(0.4)

# Game variables
class Player:
    def __init__(self):
        self.width = 50
        self.height = 50
        self.x = WIDTH // 2
        self.y = HEIGHT - 100
        self.speed = 7
        self.health = 100
        self.lives = 3
        self.shield = 0
        self.rapid_fire = False
        self.multi_shot = False
        self.powerup_time = 0
        self.invincible = False
        self.invincible_time = 0
        self.bullets = []
        
    def move(self, dx, dy):
        self.x = max(self.width//2, min(WIDTH - self.width//2, self.x + dx))
        self.y = max(self.height//2, min(HEIGHT - self.height//2, self.y + dy))
        
    def shoot(self, current_time):
        if self.multi_shot:
            return [
                Bullet(self.x, self.y - self.height//2, 0, -1),
                Bullet(self.x - 10, self.y - self.height//2, -0.3, -0.7),
                Bullet(self.x + 10, self.y - self.height//2, 0.3, -0.7)
            ]
        else:
            return [Bullet(self.x, self.y - self.height//2, 0, -1)]
            
    def draw(self):
        # Draw player
        screen.blit(player_img, (self.x - self.width//2, self.y - self.height//2))
        
        # Draw shield if active
        if self.shield > 0:
            pygame.draw.circle(screen, (0, 150, 255, 128), (self.x, self.y), self.width, 3)
            
        # Flash if invincible
        if self.invincible and pygame.time.get_ticks() % 200 < 100:
            s = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            s.fill((255, 255, 255, 128))
            screen.blit(s, (self.x - self.width//2, self.y - self.height//2))
            
    def hit(self, damage):
        if self.invincible:
            return False
            
        if self.shield > 0:
            self.shield -= damage
            if self.shield < 0:
                self.shield = 0
            return False
            
        self.health -= damage
        if self.health <= 0:
            self.lives -= 1
            if self.lives > 0:
                self.health = 100
                self.invincible = True
                self.invincible_time = pygame.time.get_ticks()
            return self.lives <= 0
        return False

class Bullet:
    def __init__(self, x, y, dx, dy):
        self.x = x
        self.y = y
        self.dx = dx
        self.dy = dy
        self.speed = 12
        self.size = 5
        
    def move(self):
        self.x += self.dx * self.speed
        self.y += self.dy * self.speed
        
    def draw(self):
        pygame.draw.circle(screen, (255, 255, 255), (int(self.x), int(self.y)), self.size)
        # Add a glow effect
        pygame.draw.circle(screen, (100, 100, 255, 128), (int(self.x), int(self.y)), self.size + 3)
        
    def off_screen(self):
        return self.y < -10 or self.y > HEIGHT + 10 or self.x < -10 or self.x > WIDTH + 10

class Enemy:
    def __init__(self, type_=0):
        self.type = type_
        self.width = 40
        self.height = 40
        self.x = random.randint(self.width, WIDTH - self.width)
        self.y = -self.height
        self.health = 10 + 10 * type_
        
        # Different movement patterns based on type
        if type_ == 0:  # Basic enemy, moves straight down
            self.dx = 0
            self.dy = 2 + random.random()
        elif type_ == 1:  # Zigzag enemy
            self.dx = random.choice([-1, 1]) * (1 + random.random())
            self.dy = 1.5 + random.random()
            self.zigzag_counter = 0
        elif type_ == 2:  # Homing enemy, slower but follows player
            self.dx = 0
            self.dy = 1 + random.random()
            self.tracking = True
        
    def move(self, player):
        # Type-specific movement
        if self.type == 1:  # Zigzag
            self.zigzag_counter += 1
            if self.zigzag_counter > 30:
                self.dx *= -1
                self.zigzag_counter = 0
                
        elif self.type == 2 and self.tracking:  # Homing
            if player.x > self.x:
                self.dx = min(self.dx + 0.1, 2)
            else:
                self.dx = max(self.dx - 0.1, -2)
        
        # Keep in bounds
        if self.x < self.width or self.x > WIDTH - self.width:
            self.dx *= -1
            
        self.x += self.dx
        self.y += self.dy
        
    def draw(self):
        screen.blit(enemy_imgs[self.type], (self.x - self.width//2, self.y - self.height//2))
        
    def off_screen(self):
        return self.y > HEIGHT + 50
        
    def hit(self, damage):
        self.health -= damage
        return self.health <= 0

class Boss:
    def __init__(self, level):
        self.width = 100
        self.height = 100
        self.x = WIDTH // 2
        self.y = -self.height
        self.health = 500 * level
        self.max_health = self.health
        self.level = level
        self.dx = 3
        self.shoot_timer = 0
        self.pattern = 0
        self.bullets = []
        
    def move(self):
        # Boss enters the screen
        if self.y < 100:
            self.y += 1
            return
            
        # Move side to side
        self.x += self.dx
        if self.x < self.width//2 or self.x > WIDTH - self.width//2:
            self.dx *= -1
            
        # Handle shooting
        self.shoot_timer += 1
        if self.shoot_timer >= 30:  # Shoot every half second
            self.shoot_timer = 0
            self.pattern = (self.pattern + 1) % 3
        
    def shoot(self):
        bullets = []
        
        if self.pattern == 0:  # Spread shot
            for angle in range(-60, 61, 20):
                rad = math.radians(angle + 90)
                dx = math.cos(rad)
                dy = math.sin(rad)
                bullets.append(Bullet(self.x, self.y + self.height//2, dx, dy))
                
        elif self.pattern == 1:  # Target player
            dx = (player.x - self.x) / math.sqrt((player.x - self.x)**2 + (player.y - self.y)**2)
            dy = (player.y - self.y) / math.sqrt((player.x - self.x)**2 + (player.y - self.y)**2)
            bullets.append(Bullet(self.x, self.y + self.height//2, dx, dy))
            bullets.append(Bullet(self.x - 30, self.y + self.height//2, dx, dy))
            bullets.append(Bullet(self.x + 30, self.y + self.height//2, dx, dy))
            
        elif self.pattern == 2:  # Spiral
            for i in range(8):
                angle = (self.shoot_timer * 10 + i * 45) % 360
                rad = math.radians(angle)
                dx = math.cos(rad)
                dy = math.sin(rad)
                bullets.append(Bullet(self.x, self.y + self.height//2, dx, dy))
        
        return bullets
    
    def draw(self):
        screen.blit(boss_img, (self.x - self.width//2, self.y - self.height//2))
        
        # Health bar
        bar_width = 200
        bar_height = 10
        bar_x = WIDTH//2 - bar_width//2
        bar_y = 20
        pygame.draw.rect(screen, (100, 100, 100), (bar_x, bar_y, bar_width, bar_height))
        health_width = int(bar_width * (self.health / self.max_health))
        pygame.draw.rect(screen, (255, 0, 0), (bar_x, bar_y, health_width, bar_height))
        
    def hit(self, damage):
        self.health -= damage
        return self.health <= 0

class PowerUp:
    def __init__(self, x, y):
        self.types = ["shield", "rapid", "multi"]
        self.type = random.choice(self.types)
        self.x = x
        self.y = y
        self.speed = 2
        self.width = 30
        self.height = 30
        
    def move(self):
        self.y += self.speed
        
    def draw(self):
        screen.blit(powerup_imgs[self.type], (self.x - self.width//2, self.y - self.height//2))
        
    def off_screen(self):
        return self.y > HEIGHT + 20

class Explosion:
    def __init__(self, x, y, size=1.0):
        self.x = x
        self.y = y
        self.frame = 0
        self.size = size
        self.max_frame = len(explosion_imgs) - 1
        
    def update(self):
        self.frame += 0.5
        return self.frame > self.max_frame
        
    def draw(self):
        idx = min(int(self.frame), self.max_frame)
        img = explosion_imgs[idx]
        width, height = img.get_size()
        scaled_img = pygame.transform.scale(img, (int(width * self.size), int(height * self.size)))
        screen.blit(scaled_img, (self.x - scaled_img.get_width()//2, self.y - scaled_img.get_height()//2))

class Star:
    def __init__(self):
        self.x = random.randint(0, WIDTH)
        self.y = random.randint(0, HEIGHT)
        self.speed = random.uniform(0.1, 1.0)
        self.size = random.uniform(0.5, 2.0)
        self.brightness = random.randint(100, 255)
        
    def move(self):
        self.y += self.speed
        if self.y > HEIGHT:
            self.y = 0
            self.x = random.randint(0, WIDTH)
            
    def draw(self):
        color = (self.brightness, self.brightness, self.brightness)
        pygame.draw.circle(screen, color, (int(self.x), int(self.y)), int(self.size))

class ParticleSystem:
    def __init__(self):
        self.particles = []
        
    def add_particle(self, x, y, color, size, life, dx=0, dy=0):
        self.particles.append({
            "x": x,
            "y": y,
            "color": color,
            "size": size,
            "life": life,
            "max_life": life,
            "dx": dx,
            "dy": dy
        })
        
    def update(self):
        for particle in self.particles[:]:
            particle["x"] += particle["dx"]
            particle["y"] += particle["dy"]
            particle["life"] -= 1
            
            if particle["life"] <= 0:
                self.particles.remove(particle)
                
    def draw(self):
        for particle in self.particles:
            alpha = int(255 * (particle["life"] / particle["max_life"]))
            color = particle["color"] + (alpha,)
            size = particle["size"] * (particle["life"] / particle["max_life"])
            
            s = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            pygame.draw.circle(s, color, (int(size), int(size)), int(size))
            screen.blit(s, (int(particle["x"] - size), int(particle["y"] - size)))

# Game variables
player = Player()
enemies = []
boss = None
power_ups = []
explosions = []
stars = [Star() for _ in range(100)]
particle_system = ParticleSystem()

# Game state
score = 0
level = 1
game_over = False
boss_fight = False
next_level_timer = 0
boss_killed = False
enemy_spawn_timer = 0
enemy_spawn_rate = 1000  # ms

# UI elements
clock = pygame.time.Clock()
font_large = pygame.font.SysFont(None, 72)
font_medium = pygame.font.SysFont(None, 36)
font_small = pygame.font.SysFont(None, 24)

# Game loop
running = True
last_time = pygame.time.get_ticks()
while running:
    current_time = pygame.time.get_ticks()
    delta_time = current_time - last_time
    last_time = current_time

    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r and game_over:
                # Reset game
                player = Player()
                enemies = []
                boss = None
                power_ups = []
                explosions = []
                score = 0
                level = 1
                game_over = False
                boss_fight = False
                next_level_timer = 0
                boss_killed = False
                enemy_spawn_timer = 0
            elif event.key == pygame.K_ESCAPE:
                running = False

    if not game_over:
        # Player movement
        keys = pygame.key.get_pressed()
        dx = 0
        dy = 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            dx -= player.speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            dx += player.speed
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            dy -= player.speed
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            dy += player.speed
        
        # Apply diagonal speed limit
        if dx != 0 and dy != 0:
            dx *= 0.7071  # 1/sqrt(2)
            dy *= 0.7071
            
        player.move(dx, dy)
        
        # Update powerup timers
        if player.rapid_fire or player.multi_shot:
            if current_time > player.powerup_time:
                player.rapid_fire = False
                player.multi_shot = False
                
        if player.invincible:
            if current_time > player.invincible_time + 2000:  # 2 second invincibility
                player.invincible = False
        
        # Shooting
        if keys[pygame.K_SPACE]:
            # Determine fire rate
            fire_rate = 150 if player.rapid_fire else 300
            
            # Check cooldown
            if current_time - last_bullet_time > fire_rate:
                player.bullets.extend(player.shoot(current_time))
                last_bullet_time = current_time
                shoot_sound.play()
                
                # Add muzzle flash particle effect
                for _ in range(5):
                    dx = random.uniform(-1, 1)
                    dy = random.uniform(-2, 0)
                    particle_system.add_particle(
                        player.x, player.y - player.height//2,
                        (255, 255, 150), random.uniform(2, 5),
                        random.randint(10, 20), dx, dy
                    )
        
        # Update bullets
        for bullet in player.bullets[:]:
            bullet.move()
            if bullet.off_screen():
                player.bullets.remove(bullet)
        
        # Spawn enemies if not in boss fight
        if not boss_fight:
            enemy_spawn_timer += delta_time
            if enemy_spawn_timer >= enemy_spawn_rate:
                enemy_spawn_timer = 0
                
                # Random enemy type based on level
                enemy_type = random.randint(0, min(level - 1, 2))
                enemies.append(Enemy(enemy_type))
                
                # Increase difficulty as level increases
                enemy_spawn_rate = max(300, 1000 - level * 50)
        
        # Check if it's time for boss
        if not boss_fight and score >= level * 1000:
            boss_fight = True
            enemies = []  # Clear normal enemies
            boss = Boss(level)
            
        # Update boss if active
        if boss:
            boss.move()
            if boss.shoot_timer == 0:
                boss_bullets = boss.shoot()
                for bullet in boss_bullets:
                    bullet.speed = 5  # Boss bullets are slower
                    particle_system.add_particle(
                        bullet.x, bullet.y,
                        (255, 100, 100), 3,
                        10, bullet.dx * 0.5, bullet.dy * 0.5
                    )
                player.bullets.extend(boss_bullets)
        
        # Update enemies
        for enemy in enemies[:]:
            enemy.move(player)
            if enemy.off_screen():
                enemies.remove(enemy)
            else:
                # Enemy-player collision
                if math.sqrt((enemy.x - player.x)**2 + (enemy.y - player.y)**2) < (enemy.width + player.width) / 2:
                    if player.hit(20):
                        game_over = True
                    
                    explosions.append(Explosion(enemy.x, enemy.y))
                    enemies.remove(enemy)
                    explosion_sound.play()
                
                # Enemy-bullet collision
                for bullet in player.bullets[:]:
                    if math.sqrt((enemy.x - bullet.x)**2 + (enemy.y - bullet.y)**2) < (enemy.width / 2 + bullet.size):
                        player.bullets.remove(bullet)
                        
                        if enemy.hit(10):
                            score += (enemy.type + 1) * 10
                            explosions.append(Explosion(enemy.x, enemy.y))
                            
                            # Chance to drop power-up
                            if random.random() < 0.2:
                                power_ups.append(PowerUp(enemy.x, enemy.y))
                                
                            enemies.remove(enemy)
                            explosion_sound.play()
                            
                            # Add particle effects
                            for _ in range(10):
                                angle = random.uniform(0, 2 * math.pi)
                                speed = random.uniform(1, 3)
                                dx = math.cos(angle) * speed
                                dy = math.sin(angle) * speed
                                particle_system.add_particle(
                                    enemy.x, enemy.y,
                                    (255, 200, 50), random.uniform(2, 5),
                                    random.randint(20, 40), dx, dy
                                )
                            break
        
        # Boss-bullet collision
        if boss:
            for bullet in player.bullets[:]:
                if (boss.x - boss.width//2 <= bullet.x <= boss.x + boss.width//2 and
                    boss.y - boss.height//2 <= bullet.y <= boss.y + boss.height//2):
                    if bullet in player.bullets:  # Check if bullet still exists
                        player.bullets.remove(bullet)
                        
                    if boss.hit(10):
                        score += level * 500
                        explosions.append(Explosion(boss.x, boss.y, 2.0))
                        boss = None
                        boss_killed = True
                        boss_fight = False
                        next_level_timer = current_time
                        explosion_sound.play()
                        
                        # Lots of particles!
                        for _ in range(50):
                            angle = random.uniform(0, 2 * math.pi)
                            speed = random.uniform(1, 5)
                            dx = math.cos(angle) * speed
                            dy = math.sin(angle) * speed
                            particle_system.add_particle(
                                boss.x if boss else WIDTH//2, boss.y if boss else HEIGHT//2,
                                (255, 100, 50), random.uniform(3, 8),
                                random.randint(30, 60), dx, dy
                            )
                        break
        
        # Update power-ups
        for power_up in power_ups[:]:
            power_up.move()
            if power_up.off_screen():
                power_ups.remove(power_up)
            elif math.sqrt((power_up.x - player.x)**2 + (power_up.y - player.y)**2) < (power_up.width + player.width) / 2:
                if power_up.type == "shield":
                    player.shield = 100
                elif power_up.type == "rapid":
                    player.rapid_fire = True
                    player.powerup_time = current_time + 10000  # 10 seconds
                elif power_up.type == "multi":
                    player.multi_shot = True
                    player.powerup_time = current_time + 8000  # 8 seconds
                
                power_ups.remove(power_up)
                powerup_sound.play()
                
                # Add particles
                for _ in range(20):
                    angle = random.uniform(0, 2 * math.pi)
                    speed = random.uniform(1, 3)
                    dx = math.cos(angle) * speed
                    dy = math.sin(angle) * speed
                    particle_system.add_particle(
                        player.x, player.y,
                        (100, 255, 100), random.uniform(2, 5),
                        random.randint(20, 40), dx, dy
                    )
        
        # Update explosions
        for explosion in explosions[:]:
            if explosion.update():
                explosions.remove(explosion)
        
        # Check for level completion
        if boss_killed and current_time - next_level_timer > 5000:  # 5 seconds between levels
            level += 1
            boss_killed = False
        
        # Update stars for parallax effect
        for star in stars:
            star.move()
        
        # Update particles
        particle_system.update()
    
    # Drawing
    screen.fill((0, 0, 30))  # Dark blue background
    
    # Draw stars
    for star in stars:
        star.draw()
    
    # Draw UI
    if not game_over:
        # Score and level
        score_text = font_medium.render(f"Score: {score}", True, (255, 255, 255))
        level_text = font_medium.render(f"Level: {level}", True, (255, 255, 255))
        screen.blit(score_text, (10, 10))
        screen.blit(level_text, (10, 50))
        
        # Lives
        lives_text = font_medium.render(f"Lives: {player.lives}", True, (255, 255, 255))
        screen.blit(lives_text, (WIDTH - 150, 10))
        
        # Health bar
        health_width = 150
        health_height = 20
        pygame.draw.rect(screen, (100, 100, 100), (WIDTH - 160, 50, health_width, health_height))
        pygame.draw.rect(screen, (0, 255, 0), (WIDTH - 160, 50, health_width * player.health / 100, health_height))
        
        # Shield bar if active
        if player.shield > 0:
            pygame.draw.rect(screen, (100, 100, 100), (WIDTH - 160, 75, health_width, health_height))
            pygame.draw.rect(screen, (0, 150, 255), (WIDTH - 160, 75, health_width * player.shield / 100, health_height))
        
        # Power-up indicators
        if player.rapid_fire:
            rapid_text = font_small.render("RAPID FIRE", True, (255, 255, 0))
            screen.blit(rapid_text, (WIDTH - 150, 100))
            
        if player.multi_shot:
            multi_text = font_small.render("MULTI SHOT", True, (0, 255, 0))
            screen.blit(multi_text, (WIDTH - 150, 125))
        
        # Level transition message
        if boss_killed:
            level_up_text = font_large.render(f"LEVEL {level} COMPLETE!", True, (255, 255, 255))
            screen.blit(level_up_text, (WIDTH//2 - level_up_text.get_width()//2, HEIGHT//2 - level_up_text.get_height()//2))
            
            if level < 10:  # Max 10 levels
                next_level_text = font_medium.render(f"PREPARE FOR LEVEL {level + 1}", True, (255, 255, 255))
                screen.blit(next_level_text, (WIDTH//2 - next_level_text.get_width()//2, HEIGHT//2 + 50))
            else:
                victory_text = font_medium.render("YOU'VE SAVED THE GALAXY!", True, (255, 255, 255))
                screen.blit(victory_text, (WIDTH//2 - victory_text.get_width()//2, HEIGHT//2 + 50))
        
        # Draw particles
        particle_system.draw()
        
        # Draw game objects
        for bullet in player.bullets:
            bullet.draw()
            
        for enemy in enemies:
            enemy.draw()
            
        if boss:
            boss.draw()
            
        for power_up in power_ups:
            power_up.draw()
            
        for explosion in explosions:
            explosion.draw()
            
        player.draw()
    else:
        # Game over screen
        game_over_text = font_large.render("GAME OVER", True, (255, 0, 0))
        final_score_text = font_medium.render(f"Final Score: {score}", True, (255, 255, 255))
        restart_text = font_medium.render("Press R to restart", True, (255, 255, 255))
        
        screen.blit(game_over_text, (WIDTH//2 - game_over_text.get_width()//2, HEIGHT//2 - 100))
        screen.blit(final_score_text, (WIDTH//2 - final_score_text.get_width()//2, HEIGHT//2))
        screen.blit(restart_text, (WIDTH//2 - restart_text.get_width()//2, HEIGHT//2 + 50))
    
    # Update display
    pygame.display.flip()
    clock.tick(60)  # 60 FPS

# Clean up
pygame.quit()
sys.exit()
