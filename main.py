import pygame
import cv2
import mediapipe as mp
import random

# Initialize pygame
pygame.init()
pygame.mixer.init()

pygame.mixer.music.load("assets/music/woah.mp3")

WIDTH = 1080
HEIGHT = 720

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Reflexa")

font = pygame.font.SysFont("Arial", 40)
title_font = pygame.font.SysFont("Arial", 70)

# Load arrow images
arrow_images = {
    "UP": pygame.image.load("assets/arrow_up.png"),
    "DOWN": pygame.image.load("assets/arrow_down.png"),
    "RIGHT": pygame.image.load("assets/arrow_right.png"),
    "LEFT": pygame.image.load("assets/arrow_left.png"),
}

for key in arrow_images:
    arrow_images[key] = pygame.transform.scale(arrow_images[key], (300, 300))

# Initialize camera
cap = cv2.VideoCapture(0)

# Initialize MediaPipe
mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils

hands = mp_hands.Hands(
    max_num_hands=1,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7
)

# Gesture state variables
direction = "NONE"
current_hand_direction = "NONE"
fist_ready = False

def is_fist_closed(hand_landmarks):
    tips = [8, 12, 16, 20]
    folded = 0
    for tip in tips:
        tip_y = hand_landmarks.landmark[tip].y
        base_y = hand_landmarks.landmark[tip - 2].y
        if tip_y > base_y:
            folded += 1
    return folded >= 3


# ---------------- GAME SYSTEM ----------------

game_state = "MENU"

score = 0
arrow_direction = None

praise_text = ""
praise_timer = 0

beat_offset = 4500
beat_interval = 3400
hit_window = 1000

music_start_time = 0
next_beat_time = 0
current_beat_time = 0

clock = pygame.time.Clock()
running = True

while running:

    screen.fill((18, 18, 28))
    current_time = pygame.time.get_ticks()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # START BUTTON
        if game_state == "MENU":
            if event.type == pygame.MOUSEBUTTONDOWN:
                game_state = "COUNTDOWN"
                pygame.mixer.music.play()
                music_start_time = pygame.time.get_ticks()

        # RESTART BUTTON
        if game_state == "GAME_OVER":
            if event.type == pygame.MOUSEBUTTONDOWN:
                score = 0
                direction = "NONE"
                fist_ready = False
                praise_text = ""
                arrow_direction = None
                pygame.mixer.music.stop()
                game_state = "MENU"

    # Always read camera
    ret, frame = cap.read()
    if not ret:
        continue

    frame = cv2.flip(frame, 1)
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb_frame)

    # Gesture detection
    if results.multi_hand_landmarks:
        hand_landmarks = results.multi_hand_landmarks[0]
        mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

        if is_fist_closed(hand_landmarks):
            fist_ready = True
            direction = "READY"

        elif fist_ready:
            wrist = hand_landmarks.landmark[0]
            middle_tip = hand_landmarks.landmark[12]

            dx = middle_tip.x - wrist.x
            dy = middle_tip.y - wrist.y

            threshold = 0.12

            if abs(dx) > abs(dy):
                if dx > threshold:
                    direction = "RIGHT"
                    current_hand_direction = "RIGHT"
                    fist_ready = False
                elif dx < -threshold:
                    direction = "LEFT"
                    current_hand_direction = "LEFT"
                    fist_ready = False
            else:
                if dy > threshold:
                    direction = "DOWN"
                    current_hand_direction = "DOWN"
                    fist_ready = False
                elif dy < -threshold:
                    direction = "UP"
                    current_hand_direction = "UP"
                    fist_ready = False

    # Convert camera to pygame surface
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    frame = pygame.surfarray.make_surface(frame)
    frame = pygame.transform.rotate(frame, -90)
    frame = pygame.transform.scale(frame, (320, 240))
    screen.blit(frame, (WIDTH - 340, HEIGHT - 260))

    # ---------------- MENU ----------------
    if game_state == "MENU":
        title_surface = title_font.render("Reflexa", True, (120, 200, 255))
        screen.blit(title_surface, (WIDTH // 2 - 150, 150))

        start_surface = font.render("CLICK TO START", True, (0, 255, 200))
        screen.blit(start_surface, (WIDTH // 2 - 150, HEIGHT // 2))

    # ---------------- COUNTDOWN ----------------
    elif game_state == "COUNTDOWN":

        elapsed = current_time - music_start_time

        if elapsed < 1000:
            text = "Get Ready"
        elif elapsed < 2000:
            text = "3"
        elif elapsed < 3000:
            text = "2"
        elif elapsed < 4000:
            text = "1"
        else:
            game_state = "PLAYING"
            next_beat_time = music_start_time + beat_offset
            text = ""

        if text:
            count_surface = title_font.render(text, True, (255, 255, 255))
            screen.blit(count_surface, (WIDTH // 2 - 150, HEIGHT // 2))

    # ---------------- PLAYING ----------------
    elif game_state == "PLAYING":

        if current_time >= next_beat_time:

            arrow_direction = random.choice(["UP", "DOWN", "LEFT", "RIGHT"])
            current_beat_time = next_beat_time

            next_beat_time += beat_interval

        # Draw arrow
        if arrow_direction:
            selected_arrow = arrow_images[arrow_direction]
            screen.blit(
                selected_arrow,
                (WIDTH // 2 - selected_arrow.get_width() // 2,
                 HEIGHT // 2 - selected_arrow.get_height() // 2)
            )

        # Input check
        if arrow_direction:

            if current_hand_direction != arrow_direction:

                time_since_drop = current_time - current_beat_time

                if abs(time_since_drop) <= hit_window:

                    if direction != arrow_direction:
                        score += 1
                        praise_text = random.choice([
                            "Nice!",
                            "Keep Going!",
                            "You're Doing Great!",
                            "Smooth!",
                            "Perfect!"
                        ])
                        praise_timer = current_time
                        arrow_direction = None
                    else:
                        game_state = "GAME_OVER"
                        pygame.mixer.music.stop()

                elif time_since_drop > hit_window:
                    game_state = "GAME_OVER"
                    pygame.mixer.music.stop()

            direction = "NONE"

    # Praise display
    if praise_text:
        if current_time - praise_timer < 800:
            praise_surface = font.render(praise_text, True, (0, 255, 150))
            screen.blit(praise_surface, (WIDTH // 2 - 120, HEIGHT // 2 + 180))
        else:
            praise_text = ""

    # ---------------- GAME OVER ----------------
    if game_state == "GAME_OVER":
        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.set_alpha(120)
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))

        over_text = title_font.render("GAME OVER!", True, (255, 0, 0))
        screen.blit(over_text, (WIDTH // 2 - 200, HEIGHT // 2 - 50))

        restart_text = font.render("Click to Restart", True, (200, 200, 200))
        screen.blit(restart_text, (WIDTH // 2 - 150, HEIGHT // 2 + 30))

    # Score Display
    score_text = font.render(f"Score: {score}", True, (255, 255, 255))
    screen.blit(score_text, (30, 30))

    pygame.display.update()
    clock.tick(60)

cap.release()
pygame.quit()