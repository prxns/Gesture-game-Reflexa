import pygame
import cv2
import mediapipe as mp

# Initialize pygame
pygame.init()

WIDTH = 800
HEIGHT = 600

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


# Game loop
running = True

while running:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
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
    frame = pygame.transform.scale(frame, (WIDTH, HEIGHT))

    screen.blit(frame, (0, 0))

    text_surface = font.render(direction, True, (0, 255, 0))
    screen.blit(text_surface, (30, 30))

    pygame.display.update()

cap.release()
pygame.quit()