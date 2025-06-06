import streamlit as st
import pygame
import random
import time
from pygame.locals import *

# Game constants
GAME_WIDTH = 700
GAME_HEIGHT = 700
SPACE_SIZE = 50
SPEED = 50
BODY_PARTS = 3
SNAKE_COLOR = (0, 255, 0)
FOOD_COLOR = (255, 0, 0)
BACKGROUND_COLOR = (0, 0, 0)
TEXT_COLOR = (255, 255, 255)

class Snake:
    def __init__(self):
        self.body_size = BODY_PARTS
        self.coordinates = []
        self.direction = 'down'
        
        for i in range(0, BODY_PARTS):
            self.coordinates.append([0, 0])

class Food:
    def __init__(self, snake):
        self.coordinates = self.generate_food(snake)
        
    def generate_food(self, snake):
        while True:
            x = random.randint(0, (GAME_WIDTH // SPACE_SIZE) - 1) * SPACE_SIZE
            y = random.randint(0, (GAME_HEIGHT // SPACE_SIZE) - 1) * SPACE_SIZE
            
            # Make sure food doesn't spawn on snake
            if [x, y] not in snake.coordinates:
                return [x, y]

def find_direction(snake, food):
    """Calculate next direction based on snake and food position"""
    snake_x, snake_y = snake.coordinates[0]
    food_x, food_y = food.coordinates

    possible_directions = []

    if snake_x < food_x:
        possible_directions.append("right")
    if snake_x > food_x:
        possible_directions.append("left")
    if snake_y < food_y:
        possible_directions.append("down")
    if snake_y > food_y:
        possible_directions.append("up")

    for direction in possible_directions:
        if is_safe_direction(snake, direction):
            return direction

    for direction in ["up", "down", "left", "right"]:
        if is_safe_direction(snake, direction):
            return direction

    return None

def is_safe_direction(snake, direction):
    """Check if a direction is safe (won't hit wall or self)"""
    x, y = snake.coordinates[0]

    if direction == "up":
        y -= SPACE_SIZE
    elif direction == "down":
        y += SPACE_SIZE
    elif direction == "left":
        x -= SPACE_SIZE
    elif direction == "right":
        x += SPACE_SIZE

    # Check wall collision
    if x < 0 or x >= GAME_WIDTH or y < 0 or y >= GAME_HEIGHT:
        return False

    # Check self collision
    for body_part in snake.coordinates:
        if x == body_part[0] and y == body_part[1]:
            return False

    return True

def check_collision(snake):
    x, y = snake.coordinates[0]

    if x < 0 or x >= GAME_WIDTH:
        return True
    elif y < 0 or y >= GAME_HEIGHT:
        return True

    for body_part in snake.coordinates[1:]:
        if x == body_part[0] and y == body_part[1]:
            return True

    return False

def main():
    st.title("Snake Game")
    
    # Initialize game state in session state
    if 'game_state' not in st.session_state:
        st.session_state.game_state = {
            'snake': Snake(),
            'food': None,
            'score': 0,
            'game_over': False,
            'auto_mode': True,
            'last_update': 0,
            'direction': 'down'
        }
        st.session_state.game_state['food'] = Food(st.session_state.game_state['snake'])
    
    # Create a placeholder for the game
    game_placeholder = st.empty()
    
    # Initialize Pygame
    pygame.init()
    screen = pygame.Surface((GAME_WIDTH, GAME_HEIGHT))
    pygame.display.set_caption("Snake Game")
    
    # Control buttons
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("Up"):
            if st.session_state.game_state['direction'] != 'down':
                st.session_state.game_state['direction'] = 'up'
    with col2:
        if st.button("Left"):
            if st.session_state.game_state['direction'] != 'right':
                st.session_state.game_state['direction'] = 'left'
        if st.button("Right"):
            if st.session_state.game_state['direction'] != 'left':
                st.session_state.game_state['direction'] = 'right'
    with col3:
        if st.button("Down"):
            if st.session_state.game_state['direction'] != 'up':
                st.session_state.game_state['direction'] = 'down'
    
    # Auto mode toggle
    st.session_state.game_state['auto_mode'] = st.checkbox("Auto Mode", value=True)
    
    # Game loop
    while not st.session_state.game_state['game_over']:
        current_time = time.time() * 1000  # Convert to milliseconds
        
        # Only update at the specified speed
        if current_time - st.session_state.game_state['last_update'] > SPEED:
            st.session_state.game_state['last_update'] = current_time
            
            snake = st.session_state.game_state['snake']
            food = st.session_state.game_state['food']
            
            # Auto mode direction calculation
            if st.session_state.game_state['auto_mode']:
                new_direction = find_direction(snake, food)
                if new_direction is not None:
                    st.session_state.game_state['direction'] = new_direction
            
            # Move snake
            x, y = snake.coordinates[0]
            
            if st.session_state.game_state['direction'] == 'up':
                y -= SPACE_SIZE
            elif st.session_state.game_state['direction'] == 'down':
                y += SPACE_SIZE
            elif st.session_state.game_state['direction'] == 'left':
                x -= SPACE_SIZE
            elif st.session_state.game_state['direction'] == 'right':
                x += SPACE_SIZE
            
            snake.coordinates.insert(0, [x, y])
            
            # Check food collision
            if x == food.coordinates[0] and y == food.coordinates[1]:
                st.session_state.game_state['score'] += 1
                st.session_state.game_state['food'] = Food(snake)
            else:
                snake.coordinates.pop()
            
            # Check collision
            if check_collision(snake):
                st.session_state.game_state['game_over'] = True
                break
            
            # Draw everything
            screen.fill(BACKGROUND_COLOR)
            
            # Draw snake
            for coord in snake.coordinates:
                pygame.draw.rect(screen, SNAKE_COLOR, 
                                (coord[0], coord[1], SPACE_SIZE, SPACE_SIZE))
            
            # Draw food
            pygame.draw.rect(screen, FOOD_COLOR, 
                            (food.coordinates[0], food.coordinates[1], SPACE_SIZE, SPACE_SIZE))
            
            # Convert Pygame surface to image and display in Streamlit
            pygame.image.save(screen, "temp.png")
            game_placeholder.image("temp.png", caption=f"Score: {st.session_state.game_state['score']}")
    
    # Game over display
    if st.session_state.game_state['game_over']:
        screen.fill(BACKGROUND_COLOR)
        font = pygame.font.SysFont('consolas', 70)
        text = font.render("GAME OVER", True, (255, 0, 0))
        text_rect = text.get_rect(center=(GAME_WIDTH/2, GAME_HEIGHT/2))
        screen.blit(text, text_rect)
        pygame.image.save(screen, "temp.png")
        game_placeholder.image("temp.png", caption=f"Final Score: {st.session_state.game_state['score']}")
        
        if st.button("Play Again"):
            # Reset game state
            st.session_state.game_state = {
                'snake': Snake(),
                'food': None,
                'score': 0,
                'game_over': False,
                'auto_mode': True,
                'last_update': 0,
                'direction': 'down'
            }
            st.session_state.game_state['food'] = Food(st.session_state.game_state['snake'])
            st.rerun()

if __name__ == "__main__":
    main()
