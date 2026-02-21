import pygame
import cv2
import mediapipe as mp

# Initialize pygame
pygame.init()

WIDTH = 800
HEIGHT = 600

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Reflexa")

# Initialize camera
cap = cv2.VideoCapture(0)

# Initialize mediapipe
mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils

hands = mp_hands.Hands(
    max_num_hands=1,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7
)

running = True

while running:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    ret, frame = cap.read()

    if not ret:
        continue

    # Flip for mirror view
    frame = cv2.flip(frame, 1)
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb_frame)

    # Draw hand landmarks directly on frame
    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:

            mp_draw.draw_landmarks(
                frame,
                hand_landmarks,
                mp_hands.HAND_CONNECTIONS
            )
            h, w, _ = frame.shape
            palm = hand_landmarks.landmark[9]

            cx = int(palm.x * w)
            cy = int(palm.y * h)

            # Draw center point
            cv2.circle(frame, (cx, cy), 10, (0, 255, 0), -1)

    # Converting frame to pygame surface
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    frame = pygame.surfarray.make_surface(frame)
    frame = pygame.transform.rotate(frame, -90)
    frame = pygame.transform.scale(frame, (WIDTH, HEIGHT))

    screen.blit(frame, (0, 0))

    pygame.display.update()

cap.release()
pygame.quit()