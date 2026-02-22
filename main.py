import pygame
import cv2
import mediapipe as mp
import random

# Initialize pygame
pygame.init()

arrow_images = {
    "UP": pygame.image.load("assets/arrow_up.png"),
    "DOWN": pygame.image.load("assets/arrow_down.png"),
    "RIGHT": pygame.image.load("assets/arrow_right.png"),
    "LEFT": pygame.image.load("assets/arrow_left.png"),
}
for key in arrow_images:
    arrow_images[key] = pygame.transform.scale(arrow_images[key], (200, 200))

title_font = pygame.font.SysFont("Ariel", 60)

WIDTH = 1080
HEIGHT = 720

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Reflexa")

font = pygame.font.SysFont("Arial", 40)

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
fist_ready = False

# Function to detect closed fist
def is_fist_closed(hand_landmarks):

    tips = [8, 12, 16, 20]
    folded = 0

    for tip in tips:
        tip_y = hand_landmarks.landmark[tip].y
        base_y = hand_landmarks.landmark[tip - 2].y

        if tip_y > base_y:
            folded += 1

    return folded >= 3

arrow_direction = None
arrow_spawn_time = 0
arrow_duration = 1500

score = 0
game_over = False

clock = pygame.time.Clock()

# Game loop
screen.fill((18, 18, 28))
title_surface = title_font.render("Reflexa", True, (120, 200, 255))
screen.blit(title_surface, (WIDTH // 2 - 150, 20))

running = True

while running:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False

    ret, frame = cap.read()

    if not ret:
        continue

    # Mirrored image
    frame = cv2.flip(frame, 1)

    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb_frame)

    # Draw landmarks and detect gesture
    if results.multi_hand_landmarks:

        hand_landmarks = results.multi_hand_landmarks[0]

        mp_draw.draw_landmarks(
            frame,
            hand_landmarks,
            mp_hands.HAND_CONNECTIONS
        )

        # Get wrist and palm positions
        wrist = hand_landmarks.landmark[0]
        palm = hand_landmarks.landmark[9]

        h, w, _ = frame.shape

        wrist_x = int(wrist.x * w)
        wrist_y = int(wrist.y * h)

        palm_x = int(palm.x * w)
        palm_y = int(palm.y * h)

        # Draw palm center
        cv2.circle(frame, (palm_x, palm_y), 10, (0, 255, 0), -1)

        # Closed fist (READY state)
        if is_fist_closed(hand_landmarks):

            fist_ready = True
            direction = "READY"

        # Direction Detection
        elif fist_ready:

            wrist = hand_landmarks.landmark[0]
            middle_tip = hand_landmarks.landmark[12]

            dx = middle_tip.x - wrist.x
            dy = middle_tip.y - wrist.y

            threshold = 0.12

            if abs(dx) > abs(dy):
                if dx > threshold:
                    direction = "RIGHT"
                    fist_ready = False
                elif dx < -threshold:
                    direction = "LEFT"
                    fist_ready = False
            else:
                if dy > threshold:
                    direction = "DOWN"
                    fist_ready = False
                elif dy < -threshold:
                    direction = "UP"
                    fist_ready = False

    # Convert frame to pygame surface
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    frame = pygame.surfarray.make_surface(frame)
    frame = pygame.transform.rotate(frame, -90)
    camera_width = 320
    camera_height = 240
    frame = pygame.transform.scale(frame, (camera_width, camera_height))

    screen.blit(frame, (WIDTH - camera_width - 20, HEIGHT - camera_height - 20))

    # Arrow Spawn System
    current_time = pygame.time.get_ticks()
    if arrow_direction is None and not game_over:
        arrow_direction = random.choice(["UP", "DOWN", "RIGHT", "LEFT"])
        arrow_spawn_time = current_time
    # Arrow Timeout
    if arrow_direction is not None and not game_over:
        if direction == arrow_direction:
            game_over = True
        elif direction in ["UP", "DOWN", "LEFT", "RIGHT"] and not fist_ready:
            score += 1
            arrow_direction = None
            direction = "NONE"

    text_surface = font.render(direction, True, (0, 255, 0))
    screen.blit(text_surface, (30, 30))

    # Displaying Arrow
    if arrow_direction is not None:
        selected_image = arrow_images[arrow_direction]
        screen.blit(selected_image, (WIDTH // 2 - 100, HEIGHT // 2 - 100))
    # Display Score
    score_text = font.render(f"Score: {score}", True, (255, 255, 255))
    screen.blit(score_text, (30, 30))
    # Game Over Display
    if game_over:
        over_text = font.render("GAME OVER!", True, (255, 0, 0))
        screen.blit(over_text, (WIDTH // 2 - 120, HEIGHT // 2))

    pygame.display.update()
    clock.tick(60)

cap.release()
pygame.quit()