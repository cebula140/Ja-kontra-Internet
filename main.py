# main.py
# Wymagania: pygame
import pygame
import random
import sys
import math
import os

from library import (
    load_settings, save_settings,
    load_assets_paths,
    load_progress, save_progress,
    record_score, high_score
)

pygame.init()
pygame.font.init()
pygame.mixer.init()

# Ustawienia i pliki
settings = load_settings()
progress = load_progress()
assets_paths = load_assets_paths("assets")

SCREEN_WIDTH = settings["SCREEN_WIDTH"]
SCREEN_HEIGHT = settings["SCREEN_HEIGHT"]

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Jaś kontra Internet")
clock = pygame.time.Clock()

# Pomocnicza funkcja do czcionki
def get_font(size):
    if assets_paths.get("pixel_font_path"):
        try:
            return pygame.font.Font(assets_paths["pixel_font_path"], size)
        except Exception:
            pass
    return pygame.font.SysFont(None, size)

# Ladowanie muzyki i dzwiekow
music_loaded = False
if assets_paths.get("music_path"):
    try:
        pygame.mixer.music.load(assets_paths["music_path"])
        music_loaded = True
    except Exception:
        music_loaded = False

assets = {}
if assets_paths.get("bomb_sound_path"):
    try:
        assets["bomb_sound"] = pygame.mixer.Sound(assets_paths["bomb_sound_path"])
    except Exception:
        assets["bomb_sound"] = None
else:
    assets["bomb_sound"] = None

if assets_paths.get("sfx_hit_path"):
    try:
        assets["sfx_hit"] = pygame.mixer.Sound(assets_paths["sfx_hit_path"])
    except Exception:
        assets["sfx_hit"] = None
else:
    assets["sfx_hit"] = None

jas_sprite_img = None
if assets_paths.get("jas_sprite_path"):
    try:
        jas_sprite_img = pygame.image.load(assets_paths["jas_sprite_path"]).convert_alpha()
    except Exception:
        jas_sprite_img = None

def apply_volume_settings():
    vol_all = float(settings.get("VOLUME_ALL", 1.0))
    vol_music = float(settings.get("VOLUME_MUSIC", 0.6))
    vol_sfx = float(settings.get("VOLUME_SFX", 0.8))
    pygame.mixer.music.set_volume(max(0.0, min(1.0, vol_all * vol_music)))
    if assets.get("bomb_sound"):
        assets["bomb_sound"].set_volume(max(0.0, min(1.0, vol_all * vol_sfx)))
    if assets.get("sfx_hit"):
        assets["sfx_hit"].set_volume(max(0.0, min(1.0, vol_all * vol_sfx)))

apply_volume_settings()
if music_loaded:
    pygame.mixer.music.play(-1)

# Zmienne globalne gry
mode = "title"
move_amount = 10
count = 0
new_score = 0
key_pressed = False
current_subtitle = ""

# Przyciski UI
def center_ui():
    return {
        "button_play": pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 20, 200, 56),
        "button_edu": pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 90, 200, 56),
        "button_quit": pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 160, 200, 56),
        "button_resume": pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 - 60, 200, 56),
        "button_exit": pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 20, 200, 56),
        "button_settings": pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 90, 200, 56),
    }

ui = center_ui()

# Przyciski rozdzielczosci
resolution_buttons = [
    (pygame.Rect(60, 120 + i*60, 220, 48), w, h)
    for i, (w, h) in enumerate([(1920,1080),(1600,900),(1280,720),(800,600)])
]

# Kontrolki dzwieku
crt_toggle_rect = pygame.Rect(SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 + 40, 300, 40)
fps_toggle_rect = pygame.Rect(SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 + 90, 300, 40)
vol_all_minus = pygame.Rect(SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 + 150, 32, 32)
vol_all_plus  = pygame.Rect(SCREEN_WIDTH // 2 + 118, SCREEN_HEIGHT // 2 + 150, 32, 32)
vol_music_minus = pygame.Rect(SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 + 200, 32, 32)
vol_music_plus  = pygame.Rect(SCREEN_WIDTH // 2 + 118, SCREEN_HEIGHT // 2 + 200, 32, 32)
vol_sfx_minus = pygame.Rect(SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 + 250, 32, 32)
vol_sfx_plus  = pygame.Rect(SCREEN_WIDTH // 2 + 118, SCREEN_HEIGHT // 2 + 250, 32, 32)
button_back = pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 320, 200, 56)

# Gracz
player = pygame.Rect(SCREEN_WIDTH // 2 - 16, SCREEN_HEIGHT // 2 - 16, 32, 32)

# Klasy pociskow
class RectBullet:
    def __init__(self, rect, vx, vy, color=(255,0,0)):
        self.rect = rect
        self.vx = vx
        self.vy = vy
        self.color = color
    def update(self):
        self.rect.x += self.vx
        self.rect.y += self.vy
    def offscreen(self):
        return (self.rect.y > SCREEN_HEIGHT + 200 or self.rect.x > SCREEN_WIDTH + 200
                or self.rect.y < -200 or self.rect.x < -200)

class SpiralBullet:
    def __init__(self, x, y, angle):
        self.x = x
        self.y = y
        self.angle = angle + random.uniform(-8, 8)
        self.speed = 3.5 + random.uniform(-0.6, 1.0)
    def update(self):
        rad = math.radians(self.angle)
        self.x += math.cos(rad) * self.speed
        self.y += math.sin(rad) * self.speed
    def draw(self):
        pygame.draw.circle(screen, (0,200,255), (int(self.x), int(self.y)), 6)

class ZigZagBullet:
    def __init__(self, x, y):
        self.x = x + random.uniform(-8, 8)
        self.y = y + random.uniform(-8, 8)
        self.speed = 2 + random.uniform(-1.0, 1.0)
        self.direction = random.choice([1, -1])
        self.timer = 0
        self.w = 12
        self.h = 12
    def update(self):
        self.y += self.speed
        self.x += self.direction * (3 + random.uniform(-0.8, 0.8))
        self.timer += 1
        if self.timer % (18 + random.randint(-4, 6)) == 0:
            self.direction *= -1
    def draw(self):
        pygame.draw.rect(screen, (255, 180, 0), pygame.Rect(int(self.x), int(self.y), self.w, self.h))

class HomingBlueBullet:
    def __init__(self, x, y):
        self.x = x + random.uniform(-10, 10)
        self.y = y + random.uniform(-10, 10)
        angle = random.uniform(0, 360)
        speed = 2.2 + random.uniform(-0.4, 0.8)
        rad = math.radians(angle)
        self.vx = math.cos(rad) * speed
        self.vy = math.sin(rad) * speed
        self.speed_base = speed
        self.turn_strength = 0.06 + random.uniform(-0.02, 0.03)
        self.color = (80, 160, 255)
        self.radius = 6
        self.spawn_time = pygame.time.get_ticks()
        self.life_ms = 5000
    def update(self):
        dx = player.centerx - self.x
        dy = player.centery - self.y
        dist = math.hypot(dx, dy) if (dx != 0 or dy != 0) else 1
        desired_vx = (dx / dist) * self.speed_base
        desired_vy = (dy / dist) * self.speed_base
        blend = self.turn_strength
        self.vx = (1 - blend) * self.vx + blend * desired_vx
        self.vy = (1 - blend) * self.vy + blend * desired_vy
        self.x += self.vx
        self.y += self.vy
    def draw(self):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)
    def offscreen(self):
        alive_time = pygame.time.get_ticks() - self.spawn_time
        if alive_time > self.life_ms:
            return True
        return not (-120 < self.x < SCREEN_WIDTH + 120 and -120 < self.y < SCREEN_HEIGHT + 120)

class Square:
    def __init__(self, x, y, size=20):
        self.x = x
        self.y = y
        self.color = (255,255,0)
        self.angle = 0
        self.size = size
        self.original = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        self.original.fill(self.color)
        self.image = self.original
        self.rect = self.image.get_rect(center=(x, y))
        dx = SCREEN_WIDTH // 2 - x
        dy = SCREEN_HEIGHT // 2 - y
        dist = math.hypot(dx, dy) if not (dx == 0 and dy == 0) else 1
        self.dx = dx / dist
        self.dy = dy / dist
    def move(self):
        self.x += self.dx * 2
        self.y += self.dy * 2
        self.image = pygame.transform.rotate(self.original, self.angle)
        self.rect = self.image.get_rect(center=(self.x, self.y))
    def draw(self):
        screen.blit(self.image, self.rect)

class ExplosionWave:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.r = 1
        self.alive = True
    def update(self):
        self.r += 22
        if self.r > max(SCREEN_WIDTH, SCREEN_HEIGHT) * 0.7:
            self.alive = False

# Listy obiektow
bullets = []
bulletsHorizontal = []
spiral_bullets = []
zigzag_bullets = []
homing_blue = []
squares = []
explosions = []


# Materialy edukacyjne
edu_readings = [
    "Internet dziala w oparciu o przesylanie pakietow. Dane sa dzielone na male fragmenty i wedruja roznymi trasami do adresata.",
    "Adres IP identyfikuje urzadzenie w sieci. Publiczny IP jest widoczny w internecie, prywatny dziala tylko w sieci lokalnej.",
    "HTTPS szyfruje polaczenie, dzieki czemu nikt po drodze nie moze podejrzec przesylanych danych.",
    "Phishing to proba wyludzenia danych, czesto poprzez falszywe wiadomosci lub strony logowania.",
    "Silne haslo powinno miec przynajmniej 12 znakow, uzywac wielkich i malych liter, cyfr oraz symboli.",
    "VPN tworzy zaszyfrowany tunel miedzy Twoim urzadzeniem a serwerem, chroniac Twoja prywatnosc w sieci.",
    "Firewall to system zabezpieczen, ktory kontroluje ruch sieciowy i blokuje nieautoryzowane polaczenia."
]

edu_quiz = [
    {"q": "Co zapewnia HTTPS?", "a": ["Szyfrowanie danych", "Wieksza predkosc", "Darmowe Wi-Fi"], "correct": 0},
    {"q": "Czym jest phishing?", "a": ["Podszywaniem sie w celu wyludzenia danych", "Nowym protokolem", "Typem oprogramowania"], "correct": 0},
    {"q": "Co poprawia bezpieczenstwo konta?", "a": ["Unikatowe, dlugie haslo", "Udostepnianie hasla znajomym", "Logowanie przez publiczne Wi-Fi"], "correct": 0},
    {"q": "Co to jest VPN?", "a": ["Szyfrowane polaczenie przez internet", "Program antywirusowy", "Router Wi-Fi"], "correct": 0},
    {"q": "Jakie haslo jest najbezpieczniejsze?", "a": ["Kombinacja liter, cyfr i symboli", "Data urodzenia", "Imie psa"], "correct": 0},
    {"q": "Do czego sluzy dwuetapowa weryfikacja?", "a": ["Dodatkowej ochrony konta", "Szybszego logowania", "Usuwania wirusow"], "correct": 0},
    {"q": "Co to jest firewall?", "a": ["System kontrolujacy ruch sieciowy", "Program do czyszczenia komputera", "Rodzaj antywirusa"], "correct": 0}
]

# Zmienne dla trybu EDU
edu_current = 0
edu_selected_answer = None
edu_show_result = False
edu_result_text = ""
edu_result_timer = 0
edu_reward = None
edu_state = "reading"
max_lives = 5
max_bombs = 3

# Przyciski odpowiedzi w quizie
edu_answer_buttons = []

def start_edu_lesson(index=None):
    global edu_current, edu_selected_answer, edu_show_result, edu_result_text, edu_result_timer, edu_reward, edu_state, edu_answer_buttons
    edu_current = random.randrange(len(edu_readings)) if index is None else index % len(edu_readings)
    edu_selected_answer = None
    edu_show_result = False
    edu_result_text = ""
    edu_reward = None
    edu_state = "reading"
    edu_answer_buttons = []

def start_edu_quiz():
    global edu_state, edu_answer_buttons
    edu_state = "quiz"
    edu_current = random.randrange(len(edu_quiz))
    edu_answer_buttons = []

def check_edu_answer():
    global edu_show_result, edu_result_text, edu_result_timer, edu_reward, progress, bombs, lives
    
    q = edu_quiz[edu_current]
    correct = q["correct"]
    
    if edu_selected_answer == correct:
        edu_result_text = "POPRAWNA ODPOWIEDZ! +10 do wiedzy"
        progress["knowledge_level"] = min(100, progress.get("knowledge_level",0) + 10)
        
        edu_reward = random.choice(["bomb", "life"])
        if edu_reward == "bomb":
            if bombs < max_bombs:
                bombs += 1
                edu_result_text += " \\n+1 BOMBA!"
            else:
                edu_result_text += " \\nMasz juz maksymalna liczbe bomb!"
        elif edu_reward == "life":
            if lives < max_lives:
                lives += 1
                edu_result_text += " \\n+1 ZYCIE!"
            else:
                edu_result_text += " \\nMasz juz maksymalna liczbe zyc!"
            
        if assets.get("sfx_hit"):
            try:
                assets["sfx_hit"].play()
            except Exception:
                pass
    else:
        edu_result_text = f"BLEDNA ODPOWIEDZ! Poprawna: {q['a'][correct]}"
        progress["knowledge_level"] = max(0, progress.get("knowledge_level",0) - 5)
    
    edu_show_result = True
    edu_result_timer = pygame.time.get_ticks() + 4000
    progress["quizzes_completed"] = progress.get("quizzes_completed",0) + 1
    save_progress(progress)

# Funkcje tekstowe
def draw_text(text, size, color, pos, font_name=None):
    f = get_font(size)
    surf = f.render(str(text), True, color)
    screen.blit(surf, pos)

def draw_wrapped_text(text, pos, max_width, size, color):
    font = get_font(size)
    words = text.split(" ")
    line = ""
    y = pos[1]
    for word in words:
        test = line + (word + " ")
        if font.size(test)[0] < max_width:
            line = test
        else:
            screen.blit(font.render(line, True, color), (pos[0], y))
            line = word + " "
            y += size + 6
    screen.blit(font.render(line, True, color), (pos[0], y))

# Sterowanie
mouse_cooldown_until = 0
MOUSE_COOLDOWN_MS = 180

def handle_keys(keys):
    global move_amount, bombs, bomb_key_pressed
    dx = keys[pygame.K_d] - keys[pygame.K_a]
    dy = keys[pygame.K_s] - keys[pygame.K_w]
    move_amount = 5 if keys[pygame.K_LSHIFT] else 10

    if dx != 0 or dy != 0:
        length = math.hypot(dx, dy)
        dx /= length
        dy /= length
        boost = 1.02
        player.x += dx * move_amount * boost
        player.y += dy * move_amount * boost

    player.clamp_ip(screen.get_rect())

    if keys[pygame.K_SPACE]:
        if not globals().get("bomb_key_pressed", False) and globals().get("bombs", 0) > 0:
            globals()["bomb_key_pressed"] = True
            use_bomb(player.centerx, player.centery)
    else:
        globals()["bomb_key_pressed"] = False

def handle_pause_key(keys):
    global mode, key_pressed
    if keys[pygame.K_ESCAPE]:
        if not key_pressed:
            key_pressed = True
            if mode == "game":
                mode = "pause"
            elif mode == "pause":
                mode = "game"
            elif mode == "settings":
                mode = "pause"
            elif mode == "edu":
                mode = "title"
    else:
        key_pressed = False

def apply_new_resolution(w, h):
    global SCREEN_WIDTH, SCREEN_HEIGHT, screen
    SCREEN_WIDTH = w; SCREEN_HEIGHT = h
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

# Stan gry
lives = 1
iframes = 0
IFRAME_TIME = 60
bombs = 0
bomb_key_pressed = False

def reset_game():
    global bullets, bulletsHorizontal, spiral_bullets, zigzag_bullets, homing_blue, squares, explosions
    global count, bombs, lives, current_subtitle
    bullets.clear(); bulletsHorizontal.clear(); spiral_bullets.clear(); zigzag_bullets.clear()
    homing_blue.clear(); squares.clear(); explosions.clear()
    count = 0; bombs = 0; lives = 1
    player.centerx = SCREEN_WIDTH // 2
    player.centery = SCREEN_HEIGHT // 2
    current_subtitle = random.choice(["wersja alfa - lataj buga", "znaleziono 3 README i 1 kotka", "debug: ON - nie mow nikomu"])

def use_bomb(x, y):
    global bombs, iframes
    if bombs <= 0:
        return
    bombs -= 1
    explosions.append({"x": x, "y": y, "r": 1, "alive": True})
    if assets.get("bomb_sound"):
        try:
            assets["bomb_sound"].play()
        except Exception:
            pass
    iframes = IFRAME_TIME // 2

# Logika pociskow
def handle_bullets():
    global count
    difficulty = 1.0 + (count // 900) * 0.07 + (progress.get("knowledge_level",0) / 100.0) * 0.15

    for b in bullets: b.update()
    bullets[:] = [b for b in bullets if not b.offscreen()]
    for b in bulletsHorizontal: b.update()
    bulletsHorizontal[:] = [b for b in bulletsHorizontal if not b.offscreen()]

    if random.randint(1, max(20, int(100 / max(1.0, difficulty)))) == 1:
        x = random.randint(0, SCREEN_WIDTH)
        y = random.randint(0, SCREEN_HEIGHT)
        base = random.randint(0, 360)
        for i in range(12):
            angle = base + i * (360 / 12) + random.uniform(-6,6)
            spiral_bullets.append(SpiralBullet(x, y, angle))

    if random.randint(1, max(20, int(100 / difficulty))) == 1:
        x = random.randint(0, SCREEN_WIDTH)
        vy = 4 + random.uniform(-1.2, 1.6) + count * 0.0005
        rect = pygame.Rect(x, -40, 30, 50)
        bullets.append(RectBullet(rect, 0, vy, color=(255,0,0)))
    if random.randint(1, max(20, int(120 / difficulty))) == 1:
        y = random.randint(0, SCREEN_HEIGHT)
        vx = 4 + random.uniform(-1.0, 1.4) + count * 0.0005
        rect = pygame.Rect(-50, y, 50, 20)
        bulletsHorizontal.append(RectBullet(rect, vx, 0, color=(0,255,0)))

    if random.randint(1, 260) == 1:
        zigzag_bullets.append(ZigZagBullet(random.randint(0, SCREEN_WIDTH), -20))

    hue_spawn_roll = random.randint(1, max(200, int(800 / difficulty)))
    if hue_spawn_roll == 1:
        side = random.choice(["top","bottom","left","right"])
        margin = 30
        if side == "top":
            x0 = random.randint(-100, SCREEN_WIDTH+100); y0 = -margin
        elif side == "bottom":
            x0 = random.randint(-100, SCREEN_WIDTH+100); y0 = SCREEN_HEIGHT + margin
        elif side == "left":
            x0 = -margin; y0 = random.randint(-100, SCREEN_HEIGHT+100)
        else:
            x0 = SCREEN_WIDTH + margin; y0 = random.randint(-100, SCREEN_HEIGHT+100)
        homing_blue.append(HomingBlueBullet(x0, y0))

    if random.randint(1, 8000) == 1:
        rx = player.centerx + random.randint(-240, 240)
        ry = player.centery + random.randint(-180, 180)
        rx = max(-100, min(SCREEN_WIDTH+100, rx)); ry = max(-100, min(SCREEN_HEIGHT+100, ry))
        homing_blue.append(HomingBlueBullet(rx, ry))

    for hb in homing_blue: hb.update()
    homing_blue[:] = [hb for hb in homing_blue if not hb.offscreen()]

    for sb in spiral_bullets: sb.update()
    spiral_bullets[:] = [sb for sb in spiral_bullets if -40 < sb.x < SCREEN_WIDTH+40 and -40 < sb.y < SCREEN_HEIGHT+40]

    for z in zigzag_bullets: z.update()
    zigzag_bullets[:] = [z for z in zigzag_bullets if -60 < z.x < SCREEN_WIDTH+60 and -60 < z.y < SCREEN_HEIGHT+60]

    for s in squares: s.move()
    if random.randint(1, 240) == 1:
        create_square()

    for ex in list(explosions):
        ex["r"] += 22
        clear_radius = ex["r"]
        bullets[:] = [b for b in bullets if math.hypot(b.rect.centerx - ex["x"], b.rect.centery - ex["y"]) > clear_radius]
        bulletsHorizontal[:] = [b for b in bulletsHorizontal if math.hypot(b.rect.centerx - ex["x"], b.rect.centery - ex["y"]) > clear_radius]
        spiral_bullets[:] = [sb for sb in spiral_bullets if math.hypot(sb.x - ex["x"], sb.y - ex["y"]) > clear_radius]
        zigzag_bullets[:] = [z for z in zigzag_bullets if math.hypot(z.x + z.w/2 - ex["x"], z.y + z.h/2 - ex["y"]) > clear_radius]
        homing_blue[:] = [hb for hb in homing_blue if math.hypot(hb.x - ex["x"], hb.y - ex["y"]) > clear_radius]
        squares[:] = [s for s in squares if math.hypot(s.x - ex["x"], s.y - ex["y"]) > clear_radius]
        if ex["r"] > max(SCREEN_WIDTH, SCREEN_HEIGHT) * 0.7:
            explosions.remove(ex)

def create_square():
    side = random.choice(["top", "bottom", "left", "right"])
    if side == "top":
        x = random.randint(0, SCREEN_WIDTH); y = -20
    elif side == "bottom":
        x = random.randint(0, SCREEN_WIDTH); y = SCREEN_HEIGHT + 20
    elif side == "left":
        x = -20; y = random.randint(0, SCREEN_HEIGHT)
    else:
        x = SCREEN_WIDTH + 20; y = random.randint(0, SCREEN_HEIGHT)
    squares.append(Square(x, y))

# Kolizje
def check_collisions():
    global lives, iframes, new_score, mode
    if iframes > 0:
        return
    hit = False
    rect_list = [b.rect for b in bullets]
    if player.collidelist(rect_list) != -1:
        hit = True
    rect_h = [b.rect for b in bulletsHorizontal]
    if player.collidelist(rect_h) != -1:
        hit = True
    if any(player.colliderect(sq.rect) for sq in squares):
        hit = True
    for sb in spiral_bullets:
        if pygame.Rect(int(sb.x)-4, int(sb.y)-4, 8, 8).colliderect(player):
            hit = True; break
    for zb in zigzag_bullets:
        if pygame.Rect(int(zb.x), int(zb.y), zb.w, zb.h).colliderect(player):
            hit = True; break
    for hb in homing_blue:
        if pygame.Rect(int(hb.x - hb.radius), int(hb.y - hb.radius), hb.radius*2, hb.radius*2).colliderect(player):
            hit = True; break

    if hit:
        lives -= 1
        iframes = IFRAME_TIME
        if assets.get("sfx_hit"):
            try: assets["sfx_hit"].play()
            except Exception: pass
        if lives <= 0:
            new_score = count
            record_score(new_score)
            save_progress(progress)
            reset_game()
            mode = "lose"

# Rysowanie
def draw_unity_grid():
    grid_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    grid_size = 32
    color = (255,255,255,8)
    for x in range(0, SCREEN_WIDTH, grid_size):
        pygame.draw.line(grid_surf, color, (x,0), (x,SCREEN_HEIGHT))
    for y in range(0, SCREEN_HEIGHT, grid_size):
        pygame.draw.line(grid_surf, color, (0,y), (SCREEN_WIDTH,y))
    screen.blit(grid_surf, (0,0))

def draw_crt_shader():
    scan = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    for y in range(0, SCREEN_HEIGHT, 3):
        pygame.draw.line(scan, (0,0,0,18), (0,y), (SCREEN_WIDTH,y))
    tint = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    tint.fill((6,10,20,10))
    screen.blit(tint, (0,0))
    screen.blit(scan, (0,0))

def draw():
    screen.fill((10,10,14))
    draw_unity_grid()

    if mode == "game":
        if jas_sprite_img:
            img = pygame.transform.scale(jas_sprite_img, (player.width, player.height))
            screen.blit(img, player.topleft)
        else:
            if iframes > 0 and (iframes // 6) % 2 == 0:
                player_color = (255,255,120)
            else:
                player_color = (150,0,200)
            cx, cy = player.center
            pygame.draw.circle(screen, player_color, (cx, cy), player.width//2)

        for b in bullets: pygame.draw.rect(screen, b.color, b.rect)
        for b in bulletsHorizontal: pygame.draw.rect(screen, b.color, b.rect)
        for sb in spiral_bullets: sb.draw()
        for z in zigzag_bullets: z.draw()
        for hb in homing_blue: hb.draw()
        for s in squares: s.draw()

        for ex in explosions:
            alpha = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            pygame.draw.circle(alpha, (255,120,0,40), (int(ex["x"]), int(ex["y"])), int(ex["r"]))
            screen.blit(alpha, (0,0))

        hx = 14; heart_w = 18; heart_h = 14
        for i in range(max_lives):
            if i < lives:
                pygame.draw.rect(screen, (200,30,40), pygame.Rect(hx, 12, heart_w, heart_h))
            else:
                pygame.draw.rect(screen, (80,80,80), pygame.Rect(hx, 12, heart_w, heart_h), 2)
            hx += (heart_w + 6)

        bomb_x = 14; bomb_y = 36
        pygame.draw.circle(screen, (40,40,40), (bomb_x, bomb_y), 10)
        pygame.draw.circle(screen, (200,60,0), (bomb_x, bomb_y), 7)
        draw_text(f"x {bombs}", 20, (255,255,255), (bomb_x + 22, bomb_y - 8))
        draw_text(f"Wynik: {count}", 26, (255,255,255), (10, 70))
        if settings.get("SHOW_FPS", False):
            fps = int(clock.get_fps())
            draw_text(f"FPS: {fps}", 20, (200,200,200), (SCREEN_WIDTH - 120, 10))
        if settings.get("CRT", True):
            draw_crt_shader()

    elif mode == "title":
        draw_text("Jas zagglebia sie w glebe internetu", 64, (255,255,255), (SCREEN_WIDTH//6, SCREEN_HEIGHT//6))
        subtitle = "Podroz pelna nauki - rozwiazuj quizy i zdobywaj power-upy"
        draw_text(subtitle, 18, (190,190,220), (SCREEN_WIDTH//2 - 240, SCREEN_HEIGHT//6 + 80))
        pygame.draw.rect(screen, (255,255,255), ui["button_play"])
        draw_text("GRAJ", 28, (0,0,0), (ui["button_play"].x + 72, ui["button_play"].y + 12))
        pygame.draw.rect(screen, (0,255,0), ui["button_edu"])
        draw_text("NAUKA", 28, (0,0,0), (ui["button_edu"].x + 66, ui["button_edu"].y + 12))
        pygame.draw.rect(screen, (180,180,180), ui["button_quit"])
        draw_text("WYJDZ", 28, (0,0,0), (ui["button_quit"].x + 66, ui["button_quit"].y + 12))
        draw_text(current_subtitle, 14, (170,170,190), (SCREEN_WIDTH//2 - 170, SCREEN_HEIGHT//6 + 110))

    elif mode == "pause":
        draw_text("PAUZA", 70, (255,255,255), (SCREEN_WIDTH//2 - 120, SCREEN_HEIGHT//6))
        pygame.draw.rect(screen, (0,0,255), ui["button_resume"])
        draw_text("WZNOW", 28, (255,255,255), (ui["button_resume"].x + 64, ui["button_resume"].y + 12))
        pygame.draw.rect(screen, (255,0,0), ui["button_exit"])
        draw_text("WYJDZ DO MENU", 20, (255,255,255), (ui["button_exit"].x + 18, ui["button_exit"].y + 16))
        pygame.draw.rect(screen, (0,255,0), ui["button_settings"])
        draw_text("USTAWIENIA", 20, (0,0,0), (ui["button_settings"].x + 46, ui["button_settings"].y + 16))

    elif mode == "lose":
        draw_text("KONIEC GRY", 64, (255,255,255), (SCREEN_WIDTH//2 - 200, 60))
        draw_text(f"Wynik: {new_score}", 36, (255,255,255), (SCREEN_WIDTH//2 - 80, 140))
        draw_text(f"Rekord: {high_score()}", 28, (255,255,255), (SCREEN_WIDTH//2 - 90, 190))
        pygame.draw.rect(screen, (255,255,255), ui["button_play"])
        draw_text("ZAGRAJ PONOWNIE", 22, (0,0,0), (ui["button_play"].x + 18, ui["button_play"].y + 14))

    elif mode == "settings":
        draw_text("USTAWIENIA", 44, (255,255,255), (SCREEN_WIDTH//2 - 120, 20))
        for rect, w, h in resolution_buttons:
            pygame.draw.rect(screen, (40,60,200), rect)
            draw_text(f"{w} x {h}", 20, (255,255,255), (rect.x + 12, rect.y + 11))
        pygame.draw.rect(screen, (100,100,100), crt_toggle_rect)
        crt_status = "TAK" if settings.get("CRT", True) else "NIE"
        draw_text(f"Efekt CRT: {crt_status}", 18, (255,255,255), (crt_toggle_rect.x + 12, crt_toggle_rect.y + 8))
        pygame.draw.rect(screen, (100,100,100), fps_toggle_rect)
        fps_status = "TAK" if settings.get("SHOW_FPS", False) else "NIE"
        draw_text(f"Pokaz FPS: {fps_status}", 18, (255,255,255), (fps_toggle_rect.x + 12, fps_toggle_rect.y + 8))
        draw_text("Glosnosc (calosc):", 18, (220,220,220), (vol_all_minus.x + 44, vol_all_minus.y - 6))
        pygame.draw.rect(screen, (160,160,160), vol_all_minus); draw_text("-", 22, (0,0,0), (vol_all_minus.x+8, vol_all_minus.y-2))
        pygame.draw.rect(screen, (160,160,160), vol_all_plus); draw_text("+", 22, (0,0,0), (vol_all_plus.x+8, vol_all_plus.y-2))
        draw_text(f"{int(settings.get('VOLUME_ALL',1.0)*100)}%", 18, (200,200,200), (vol_all_minus.x + 56, vol_all_minus.y - 2))
        draw_text("Glosnosc muzyki:", 18, (220,220,220), (vol_music_minus.x + 44, vol_music_minus.y - 6))
        pygame.draw.rect(screen, (160,160,160), vol_music_minus); draw_text("-", 22, (0,0,0), (vol_music_minus.x+8, vol_music_minus.y-2))
        pygame.draw.rect(screen, (160,160,160), vol_music_plus); draw_text("+", 22, (0,0,0), (vol_music_plus.x+8, vol_music_plus.y-2))
        draw_text(f"{int(settings.get('VOLUME_MUSIC',0.6)*100)}%", 18, (200,200,200), (vol_music_minus.x + 56, vol_music_minus.y - 2))
        draw_text("Glosnosc efektow:", 18, (220,220,220), (vol_sfx_minus.x + 44, vol_sfx_minus.y - 6))
        pygame.draw.rect(screen, (160,160,160), vol_sfx_minus); draw_text("-", 22, (0,0,0), (vol_sfx_minus.x+8, vol_sfx_minus.y-2))
        pygame.draw.rect(screen, (160,160,160), vol_sfx_plus); draw_text("+", 22, (0,0,0), (vol_sfx_plus.x+8, vol_sfx_plus.y-2))
        draw_text(f"{int(settings.get('VOLUME_SFX',0.8)*100)}%", 18, (200,200,200), (vol_sfx_minus.x + 56, vol_sfx_minus.y - 2))
        pygame.draw.rect(screen, (255,255,255), button_back)
        draw_text("WROC", 24, (0,0,0), (button_back.x + 72, button_back.y + 14))

    elif mode == "edu":
        screen.fill((20,20,30))
        draw_text("LEKCJA - Cyberbezpieczenstwo", 44, (255,255,255), (SCREEN_WIDTH//2 - 220, 60))
        
        if edu_state == "reading":
            draw_wrapped_text(edu_readings[edu_current], (SCREEN_WIDTH//2 - 350, 150), 700, 24, (220,220,220))
            draw_text("Nacisnij SPACJE aby przejsc do quizu", 22, (160,160,170), (SCREEN_WIDTH//2 - 200, 400))
            
        elif edu_state == "quiz":
            if not edu_show_result:
                q = edu_quiz[edu_current]
                draw_wrapped_text(q["q"], (SCREEN_WIDTH//2 - 300, 150), 600, 32, (255,255,255))
                
                # Tworzenie przycisków odpowiedzi
                edu_answer_buttons.clear()
                for i, ans in enumerate(q["a"]):
                    button_rect = pygame.Rect(SCREEN_WIDTH//2 - 280, 220 + i*60, 560, 50)
                    edu_answer_buttons.append(button_rect)
                    
                    # Kolor przycisku
                    if i == edu_selected_answer:
                        color = (255,255,0)  # Zolty dla wybranej odpowiedzi
                    else:
                        color = (100,100,100)  # Szary dla niewybranych
                    
                    pygame.draw.rect(screen, color, button_rect)
                    
                    # Tekst odpowiedzi
                    text_color = (0,0,0) if i == edu_selected_answer else (255,255,255)
                    draw_text(f"{i+1}. {ans}", 28, text_color, (button_rect.x + 20, button_rect.y + 10))
                
                draw_text("Wybierz odpowiedz: 1, 2, 3 lub kliknij przycisk", 22, (160,160,170), (SCREEN_WIDTH//2 - 220, 400))
            else:
                result_color = (0,255,0) if "POPRAWNA" in edu_result_text else (255,0,0)
                lines = edu_result_text.split(" \\n")
                for i, line in enumerate(lines):
                    draw_text(line, 32, result_color, (SCREEN_WIDTH//2 - 300, 200 + i*40))
                
                if edu_reward:
                    reward_color = (255,215,0)
                    if edu_reward == "bomb":
                        draw_text("Nagroda: +1 BOMBA", 28, reward_color, (SCREEN_WIDTH//2 - 150, 320))
                    elif edu_reward == "life":
                        draw_text("Nagroda: +1 ZYCIE", 28, reward_color, (SCREEN_WIDTH//2 - 150, 320))
                
                draw_text("Powrot za chwile...", 22, (160,160,170), (SCREEN_WIDTH//2 - 120, 380))
        
        pygame.draw.rect(screen, (100,100,100), button_back)
        draw_text("WROC", 24, (255,255,255), (button_back.x + 72, button_back.y + 14))

    draw_text(f"Postep: {progress.get('quizzes_completed',0)}  |  Wiedza: {progress.get('knowledge_level',0)}%", 14, (180,180,200), (SCREEN_WIDTH - 420, 12))

# Optymalizacja
def optimize():
    global bullets, bulletsHorizontal, spiral_bullets, zigzag_bullets, homing_blue, squares
    bullets[:] = [b for b in bullets if not b.offscreen()]
    bulletsHorizontal[:] = [b for b in bulletsHorizontal if not b.offscreen()]
    spiral_bullets[:] = [sb for sb in spiral_bullets if -50 < sb.x < SCREEN_WIDTH+50 and -50 < sb.y < SCREEN_HEIGHT+50]
    zigzag_bullets[:] = [z for z in zigzag_bullets if -100 < z.x < SCREEN_WIDTH+100 and -100 < z.y < SCREEN_HEIGHT+100]
    homing_blue[:] = [hb for hb in homing_blue if not hb.offscreen()]
    squares[:] = [s for s in squares if -50 < s.x < SCREEN_WIDTH + 50 and -50 < s.y < SCREEN_HEIGHT + 50]

# Obsluga zdarzen
def handle_events():
    global mode, count, new_score, lives, iframes, bombs, mouse_cooldown_until, edu_selected_answer, edu_show_result, edu_result_timer, edu_state
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            save_settings(settings)
            save_progress(progress)
            pygame.quit(); sys.exit()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse = pygame.mouse.get_pos()
            click = True
            if mode == "title":
                if ui["button_play"].collidepoint(mouse) and click:
                    reset_game(); mode = "game"
                if ui["button_edu"].collidepoint(mouse) and click:
                    start_edu_lesson()
                    mode = "edu"
                if ui["button_quit"].collidepoint(mouse) and click:
                    save_settings(settings); save_progress(progress); pygame.quit(); sys.exit()
            elif mode == "pause":
                if ui["button_resume"].collidepoint(mouse) and click:
                    mode = "game"
                if ui["button_exit"].collidepoint(mouse) and click:
                    mode = "title"
                if ui["button_settings"].collidepoint(mouse) and click:
                    mode = "settings"
            elif mode == "lose":
                if ui["button_play"].collidepoint(mouse) and click:
                    reset_game(); mode = "game"
            elif mode == "settings":
                for rect, w, h in resolution_buttons:
                    if rect.collidepoint(mouse) and click:
                        settings["SCREEN_WIDTH"] = w; settings["SCREEN_HEIGHT"] = h
                        save_settings(settings); apply_new_resolution(w,h)
                if crt_toggle_rect.collidepoint(mouse) and click:
                    settings["CRT"] = not settings.get("CRT", True); save_settings(settings)
                if fps_toggle_rect.collidepoint(mouse) and click:
                    settings["SHOW_FPS"] = not settings.get("SHOW_FPS", False); save_settings(settings)
                if vol_all_minus.collidepoint(mouse) and click:
                    settings["VOLUME_ALL"] = max(0.0, settings.get("VOLUME_ALL",1.0) - 0.05); save_settings(settings); apply_volume_settings()
                if vol_all_plus.collidepoint(mouse) and click:
                    settings["VOLUME_ALL"] = min(1.0, settings.get("VOLUME_ALL",1.0) + 0.05); save_settings(settings); apply_volume_settings()
                if vol_music_minus.collidepoint(mouse) and click:
                    settings["VOLUME_MUSIC"] = max(0.0, settings.get("VOLUME_MUSIC",0.6) - 0.05); save_settings(settings); apply_volume_settings()
                if vol_music_plus.collidepoint(mouse) and click:
                    settings["VOLUME_MUSIC"] = min(1.0, settings.get("VOLUME_MUSIC",0.6) + 0.05); save_settings(settings); apply_volume_settings()
                if vol_sfx_minus.collidepoint(mouse) and click:
                    settings["VOLUME_SFX"] = max(0.0, settings.get("VOLUME_SFX",0.8) - 0.05); save_settings(settings); apply_volume_settings()
                if vol_sfx_plus.collidepoint(mouse) and click:
                    settings["VOLUME_SFX"] = min(1.0, settings.get("VOLUME_SFX",0.8) + 0.05); save_settings(settings); apply_volume_settings()
                if button_back.collidepoint(mouse) and click:
                    mode = "pause"
            elif mode == "edu":
                if edu_state == "quiz" and not edu_show_result:
                    # Sprawdzanie klikniecia w przyciski odpowiedzi
                    for i, button_rect in enumerate(edu_answer_buttons):
                        if button_rect.collidepoint(mouse):
                            edu_selected_answer = i
                            check_edu_answer()
                            break
                if button_back.collidepoint(mouse) and click:
                    mode = "title"
        elif event.type == pygame.KEYDOWN:
            if mode == "edu":
                if edu_state == "reading" and event.key == pygame.K_SPACE:
                    start_edu_quiz()
                elif edu_state == "quiz" and not edu_show_result:
                    if event.key in (pygame.K_1, pygame.K_2, pygame.K_3):
                        edu_selected_answer = {pygame.K_1:0, pygame.K_2:1, pygame.K_3:2}[event.key]
                        check_edu_answer()
    keys = pygame.key.get_pressed()
    if mode == "game":
        handle_keys(keys)
        handle_pause_key(keys)
    global iframes
    if iframes > 0:
        iframes -= 1

# Petla glowna
def main():
    global count, mode, edu_show_result, edu_result_timer, current_subtitle
    running = True
    current_subtitle = random.choice(["wersja alfa - lataj buga",
        "znaleziono 3 README i 1 kotka", 
        "debug: ON - nie mow nikomu",
        "404 - humor nie znaleziony",
        "CTRL+Z nie dziala w zyciu",
        "wszystkie bledy sa funkcjami",
        "coffee empty, regrets full",
        "to nie bug, to feature!",
        "dzis nie ma deadline'u... chyba",
        "commit: 'dziala, nie pytaj jak'",
        "wypilem eliksir na dzialanie kodu, jak to widzisz to eliksir dziala" ])
    while running:
        handle_events()
        if mode == "game":
            handle_bullets()
            check_collisions()
            count += 1
        elif mode == "edu" and edu_show_result:
            if pygame.time.get_ticks() > edu_result_timer:
                edu_show_result = False
                mode = "title"
        draw()
        optimize()
        pygame.display.flip()
        clock.tick(60)
    save_settings(settings)
    save_progress(progress)
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
