from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import random


game_over = False

# Spaceship positions
bottom_spaceship_x = 400
bottom_spaceship_y = 50
top_spaceship_x = 400
top_spaceship_y = 750

# Bullet properties
bullet_radius = 5
bullet_speed = 20
bullet_cooldown = 10
bottom_bullet_cooldown = 0
top_bullet_cooldown = 0

# Spaceship sizes
spaceship_width = 80
spaceship_height = 20
circle_radius = 20


# Health variables
bottom_spaceship_health = 100
top_spaceship_health = 100

# Box properties
box_width = 40
box_height = 40
box_spawn_timer = 0
box_spawn_interval = 10000  # 10 seconds in milliseconds
box_position = None

# Button properties
button_width = 30
button_height = 30


# Update Button Positions
pause_button_x = 735
pause_button_y = 770
close_button_x = 770
close_button_y = 770

# Bullet lists
bottom_bullets = []
top_bullets = []

# Keyboard states
key_states = {'a': False, 'd': False, 'left': False,
              'right': False, 'w': False, 'up': False}

# Pause state
is_game_paused = False


def draw_pixel(x, y):
    glPointSize(5.0)
    glBegin(GL_POINTS)
    glVertex2i(x, y)
    glEnd()


def circlePoints(x, y, x0, y0):
    draw_pixel(x + x0, y + y0)
    draw_pixel(y + x0, x + y0)
    draw_pixel(y + x0, -x + y0)
    draw_pixel(x + x0, -y + y0)
    draw_pixel(-x + x0, -y + y0)
    draw_pixel(-y + x0, -x + y0)
    draw_pixel(-y + x0, x + y0)
    draw_pixel(-x + x0, y + y0)


def midpointCircle(radius, x0, y0):
    d = 1 - radius
    x = 0
    y = radius

    circlePoints(x, y, x0, y0)

    while x < y:
        if d < 0:
            d = d + 2*x + 3
            x += 1
        else:
            d = d + 2*x - 2*y + 5
            x += 1
            y = y - 1

        circlePoints(x, y, x0, y0)


def drawMidpointLine(x1, y1, x2, y2):
    dx = abs(x2 - x1)
    dy = abs(y2 - y1)
    sx = 1 if x1 < x2 else -1
    sy = 1 if y1 < y2 else -1
    err = dx - dy

    while x1 != x2 or y1 != y2:
        draw_pixel(x1, y1)
        e2 = 2 * err
        if e2 > -dy:
            err -= dy
            x1 += sx
        if e2 < dx:
            err += dx
            y1 += sy
        draw_pixel(x1, y1)


def draw_rectangle(x1, y1, x2, y2):
    drawMidpointLine(x1, y1, x2, y1)
    drawMidpointLine(x2, y1, x2, y2)
    drawMidpointLine(x2, y2, x1, y2)
    drawMidpointLine(x1, y2, x1, y1)


def draw_spaceships():
    glColor3f(0.0, 0.65, 0.0)  #  green
    draw_rectangle(
        bottom_spaceship_x - spaceship_width // 2,
        bottom_spaceship_y,
        bottom_spaceship_x + spaceship_width // 2,
        bottom_spaceship_y + spaceship_height
    )
    midpointCircle(circle_radius, bottom_spaceship_x, bottom_spaceship_y)

    glColor3f(0.0, 0.0, 0.8)  #  blue
    draw_rectangle(
        top_spaceship_x - spaceship_width // 2,
        top_spaceship_y - spaceship_height,
        top_spaceship_x + spaceship_width // 2,
        top_spaceship_y
    )
    midpointCircle(circle_radius, top_spaceship_x, top_spaceship_y)


def draw_bullets():
    
    for bullet in bottom_bullets:
        glColor3f(0.2, 0.6, 0.2)
        midpointCircle(bullet_radius, bullet[0], bullet[1])

    
    for bullet in top_bullets:
        glColor3f(0.2, 0.2, 0.6)
        midpointCircle(bullet_radius, bullet[0], bullet[1])


def update_bullets():
    global bottom_bullet_cooldown, top_bullet_cooldown

    if is_game_paused:
        return  

    # Update bottom bullets
    if bottom_bullet_cooldown > 0:
        bottom_bullet_cooldown -= 1

    # Update top bullets
    if top_bullet_cooldown > 0:
        top_bullet_cooldown -= 1

    # Move bottom bullets
    for i, bullet in enumerate(bottom_bullets):
        bottom_bullets[i] = (bullet[0], bullet[1] + bullet_speed)

    # Move top bullets
    for i, bullet in enumerate(top_bullets):
        top_bullets[i] = (bullet[0], bullet[1] - bullet_speed)


def update_spaceships():
    global bottom_spaceship_x, top_spaceship_x

    # Move the bottom spaceship
    if key_states['a']:
        bottom_spaceship_x = max(bottom_spaceship_x - 10, 0)
    if key_states['d']:
        bottom_spaceship_x = min(bottom_spaceship_x + 10, 800)

    # Move the top spaceship
    if key_states['left']:
        top_spaceship_x = max(top_spaceship_x - 10, 0)
    if key_states['right']:
        top_spaceship_x = min(top_spaceship_x + 10, 800)




def check_game_over():
    global game_over, top_spaceship_health, bottom_spaceship_health
    if top_spaceship_health <= 0 or bottom_spaceship_health <= 0:
        game_over = True


def draw_game_over():
    global top_spaceship_health, bottom_spaceship_health

    if top_spaceship_health > bottom_spaceship_health:
        winner_str = "Top Player Wins!"
    elif bottom_spaceship_health > top_spaceship_health:
        winner_str = "Bottom Player Wins!"
    else:
        winner_str = "It's a Draw!"

    glColor3f(1.0, 0.0, 0.0)  # Red color for game over text
    glRasterPos2i(200, 400)
    game_over_str = f"Game Over! {winner_str} Press 'r' to restart."
    
    # Display the game over message
    for char in game_over_str:
        glutBitmapCharacter(GLUT_BITMAP_9_BY_15, ord(char))



def restart_game():
    global game_over, top_spaceship_health, bottom_spaceship_health
    game_over = False
    top_spaceship_health = 100
    bottom_spaceship_health = 100



def draw_button(x, y, width, height):

    draw_rectangle(x, y, x + width, y + height)


def draw_icons():

    glColor3f(1.0, 1.0, 0.0) # yellow
    draw_button(pause_button_x, pause_button_y,
                        button_width, button_height)
    
    

    glPointSize(2.0)  # Set point size
    glColor3f(1.0, 0.0, 0.0)  # Set color to red
    drawMidpointLine(800, 800, 770, 770)
    drawMidpointLine(770, 800, 800, 770)
    
    

    glColor3f(1.0, 0.0, 0.0) # red 
    draw_button(close_button_x, close_button_y,
                        button_width, button_height)

    # print("Pause Button Coordinates:", pause_button_x, pause_button_y)
    # print("Close Button Coordinates:", close_button_x, close_button_y)
    glPointSize(2.0)  # Set point size
    glColor3f(1.0, 1.0, 0.0)  # Set color to red
    drawMidpointLine(765, 800, 736, 785)
    drawMidpointLine(736, 785, 765, 770)


def mouse_click(button, state, x, y):
    global is_game_paused

    # Convert window coordinates to OpenGL coordinates
    ogl_y = 800 - y

    if button == GLUT_LEFT_BUTTON and state == GLUT_DOWN:
        if is_game_paused:
            is_game_paused = False
        else:
            if (
                pause_button_x <= x <= pause_button_x + button_width and
                pause_button_y <= ogl_y <= pause_button_y + button_height
            ):
                is_game_paused = not is_game_paused
            if (
                close_button_x <= x <= close_button_x + button_width and
                close_button_y <= ogl_y <= close_button_y + button_height
            ):
                
                glutLeaveMainLoop()

    glutPostRedisplay()


def draw_paused():
    glColor3f(0.0, 0.0, 0.0)  #  black

    glRasterPos2i(225, 400)  
    paused_str = "Game Paused. Click anywhere to resume or press 'p'"
    for char in paused_str:
        glutBitmapCharacter(GLUT_BITMAP_9_BY_15, ord(char))


def draw_box():
    glColor3f(1.0, 0.0, 1.0)  #  pink 

    if box_position:
        draw_rectangle(
            box_position[0] - box_width // 2,
            box_position[1] - box_height // 2,
            box_position[0] + box_width // 2,
            box_position[1] + box_height // 2
        )


def update_box():
    global box_spawn_timer, box_position, bottom_spaceship_x, top_spaceship_x

    if is_game_paused:
        return  

    if box_spawn_timer <= 0:
        midpoint = (bottom_spaceship_x + top_spaceship_x) // 2
        box_position = (random.randint(midpoint - 200, midpoint + 200),
                        random.randint(bottom_spaceship_y, top_spaceship_y))
        box_spawn_timer = box_spawn_interval
    else:
        box_spawn_timer -= 16  # Decrease timer every frame (16 milliseconds)


def check_collision_with_box(bullet_x, bullet_y, is_top_bullet):
    global box_position, box_width, box_height, top_spaceship_health, bottom_spaceship_health

    if box_position:
        box_x, box_y = box_position
        if (
            bullet_x > box_x - box_width // 2 and
            bullet_x < box_x + box_width // 2 and
            bullet_y > box_y - box_height // 2 and
            bullet_y < box_y + box_height // 2
        ):
            # Collision with box
            if is_top_bullet:
                top_spaceship_health += 20
            else:
                bottom_spaceship_health += 20
            box_position = None  # Remove the box
            return True

    return False


def keyboard(key, x, y):
    global key_states, bottom_bullet_cooldown, top_bullet_cooldown, is_game_paused

    global game_over
    key = key.decode("utf-8")

    if key == 'r' and game_over:
        restart_game()

    if key == 'p':
        is_game_paused = not is_game_paused  
    elif key == '\x1b':  # Esc key
        glutLeaveMainLoop()  # Close the window
    elif key in key_states and not is_game_paused:
        key_states[key] = True
        if key == 'w' and bottom_bullet_cooldown == 0:
            bottom_bullets.append(
                (bottom_spaceship_x, bottom_spaceship_y + spaceship_height + bullet_radius))
            bottom_bullet_cooldown = bullet_cooldown
        elif key == 'up' and top_bullet_cooldown == 0:
            top_bullets.append(
                (top_spaceship_x, top_spaceship_y - spaceship_height - bullet_radius))
            top_bullet_cooldown = bullet_cooldown

    glutPostRedisplay()


def keyboard_up(key, x, y):
    global key_states

    key = key.decode("utf-8")

    if key in key_states:
        key_states[key] = False

    glutPostRedisplay()


def specialKeys(key, x, y):
    global key_states, is_game_paused, top_bullet_cooldown

    if key == GLUT_KEY_LEFT and not is_game_paused:
        key_states['left'] = True
    elif key == GLUT_KEY_RIGHT and not is_game_paused:
        key_states['right'] = True
    elif key == GLUT_KEY_UP and not is_game_paused:
        key_states['up'] = True
        if top_bullet_cooldown == 0:
            top_bullets.append(
                (top_spaceship_x, top_spaceship_y - spaceship_height - bullet_radius))
            top_bullet_cooldown = bullet_cooldown

    glutPostRedisplay()


def specialKeysUp(key, x, y):
    global key_states

    if key == GLUT_KEY_LEFT:
        key_states['left'] = False
    elif key == GLUT_KEY_RIGHT:
        key_states['right'] = False
    elif key == GLUT_KEY_UP:
        key_states['up'] = False

    glutPostRedisplay()


def check_collision():
    global bottom_bullets, top_bullets, bottom_spaceship_x, bottom_spaceship_y, top_spaceship_x, top_spaceship_y
    global bottom_spaceship_health, top_spaceship_health
    global bottom_bullets, top_bullet

    # Check collision between bottom bullets and top spaceship
    for bullet in bottom_bullets:
        if (
            top_spaceship_x - spaceship_width // 2 < bullet[0] < top_spaceship_x + spaceship_width // 2 and
            top_spaceship_y - spaceship_height < bullet[1] < top_spaceship_y
        ):
            # print("Top spaceship hit")
            bottom_bullets.remove(bullet)  # Remove the bullet upon hit
            top_spaceship_health -= 5  # Decrease top spaceship health

        # Check collision with box for top spaceship
        if check_collision_with_box(bullet[0], bullet[1], False):
            bottom_bullets.remove(bullet)

    # Check collision between top bullets and bottom spaceship
    for bullet in top_bullets:
        if (
            bottom_spaceship_x - spaceship_width // 2 < bullet[0] < bottom_spaceship_x + spaceship_width // 2 and
            bottom_spaceship_y < bullet[1] < bottom_spaceship_y +
                spaceship_height
        ):
            # print("Bottom spaceship hit")
            top_bullets.remove(bullet)  # Remove the bullet upon hit
            bottom_spaceship_health -= 5  # Decrease bottom spaceship health

        # Check collision with box for bottom spaceship
        if check_collision_with_box(bullet[0], bullet[1], True):
            top_bullets.remove(bullet)


def draw_health():
    global bottom_spaceship_health, top_spaceship_health

    glColor3f(0.0, 0.0, 0.0)  # black

    glRasterPos2i(30, 20)
    health_str_bottom = f"Health: {bottom_spaceship_health}"
    for char in health_str_bottom:
        glutBitmapCharacter(GLUT_BITMAP_9_BY_15, ord(char))

    glRasterPos2i(30, 780)
    health_str_top = f"Health: {top_spaceship_health}"
    for char in health_str_top:
        glutBitmapCharacter(GLUT_BITMAP_9_BY_15, ord(char))


def update(frame):
    update_bullets()
    update_spaceships()
    update_box()
    check_collision()  
    check_game_over()
    glutTimerFunc(16, update, 0)
    glutPostRedisplay()


def reshape(w, h):
    glViewport(0, 0, GLsizei(w), GLsizei(h))
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluOrtho2D(0.0, GLdouble(w), 0.0, GLdouble(h))
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()


def display():
    glClear(GL_COLOR_BUFFER_BIT)
    if game_over:
        draw_game_over()
    elif is_game_paused:
        draw_paused()
    else:
        draw_spaceships()
        draw_bullets()
        draw_box()  
        draw_health()
        draw_icons()  

    glutSwapBuffers()


def main():
    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB)  
    glutInitWindowSize(800, 800)
    glutCreateWindow(b"1V1 SpaceShip Battle")
    glutDisplayFunc(display)
    glutReshapeFunc(reshape)
    glutKeyboardFunc(keyboard)
    glutKeyboardUpFunc(keyboard_up)
    glutSpecialFunc(specialKeys)  
    glutSpecialUpFunc(specialKeysUp)
    glutMouseFunc(mouse_click)  
    glClearColor(0.53, 0.81, 0.92, 0.0)
    gluOrtho2D(0.0, 800.0, 0.0, 800.0)
    glutTimerFunc(16, update, 0)  
    glutMainLoop()


if __name__ == "__main__":
    main()
