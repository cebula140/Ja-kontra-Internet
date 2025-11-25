# library.py
import os
import json

# Pliki konfiguracyjne
SETTINGS_FILE = "settings.json"
SCORES_FILE = "scores.json"
PROGRESS_FILE = "progress.json"
ASSETS_DIR = "assets"

# Domyślne ustawienia (po polsku)
_default_settings = {
    "SCREEN_WIDTH": 1280,
    "SCREEN_HEIGHT": 720,
    "CRT": True,
    "SHOW_FPS": False,
    "VOLUME_ALL": 1.0,
    "VOLUME_MUSIC": 0.6,
    "VOLUME_SFX": 0.8,
    "EDU_ALWAYS_ON": True
}

def load_settings():
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                s = json.load(f)
        except Exception:
            s = _default_settings.copy()
    else:
        s = _default_settings.copy()

    # uzupełnij brakujące pola
    for k, v in _default_settings.items():
        if k not in s:
            s[k] = v
    return s

def save_settings(settings):
    with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
        json.dump(settings, f, ensure_ascii=False, indent=2)

# scores
def load_scores():
    if os.path.exists(SCORES_FILE):
        try:
            with open(SCORES_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []
    return []

def save_scores(scores):
    with open(SCORES_FILE, "w", encoding="utf-8") as f:
        json.dump(scores, f, ensure_ascii=False, indent=2)

def record_score(score):
    s = load_scores()
    s.append(score)
    save_scores(s)

def high_score():
    s = load_scores()
    if not s:
        return 0
    return max(s)

# progress
def load_progress():
    if os.path.exists(PROGRESS_FILE):
        try:
            with open(PROGRESS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {"quizzes_completed": 0, "knowledge_level": 0}

def save_progress(progress):
    with open(PROGRESS_FILE, "w", encoding="utf-8") as f:
        json.dump(progress, f, ensure_ascii=False, indent=2)


def load_assets_paths(assets_dir=ASSETS_DIR):
    assets = {}
    assets["assets_dir"] = assets_dir
    assets["music_path"] = os.path.join(assets_dir, "music.mp3")
    assets["jas_sprite_path"] = os.path.join(assets_dir, "jas.png")
    assets["pixel_font_path"] = os.path.join(assets_dir, "pixel_font.ttf")
    assets["bomb_sound_path"] = os.path.join(assets_dir, "bomb.wav")
    assets["sfx_hit_path"] = os.path.join(assets_dir, "sfx_hit.wav")
    # sprawdź istnienie plików, jeśli nie istnieją -> ustaw None
    for k in list(assets.keys()):
        if k.endswith("_path"):
            if not os.path.exists(assets[k]):
                assets[k] = None
    return assets
