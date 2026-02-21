import pygame
import cv2

pygame.init()

# Game Window
width = 800
height = 600

screen = pygame.display.set_mode((width,height))
pygame.display.set_caption("Reflexa")

cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Camera Not Detected")
    exit()

# Game loop variable
running = True

# Main game loop
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
               
    ret, frame = cap.read()
    if ret:
        frame = cv2.flip(frame, 1)
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame = pygame.surfarray.make_surface(frame)
        # Rotating frame to correc orientation
        frame = pygame.transform.rotate(frame, -90)

        frame = pygame.transform.scale(frame, (width,height))

        screen.blit(frame, (0, 0))

    pygame.display.update()

cap.release()
pygame.quit()