import tkinter as tk
import random
import string
import math
import pygame

# Define a mapping of color names to hex values
color_map = {
    "pink": "#FFC0CB",
    "lightblue": "#ADD8E6",
    "lightgreen": "#90EE90",
    "lavender": "#E6E6FA",
    "yellow": "#FFFF00",
    "orange": "#FFA500"
}

def adjust_color(hex_color, factor):
    """Adjust a hex color by a multiplication factor for RGB components."""
    hex_color = hex_color.lstrip('#')
    r = int(hex_color[0:2], 16)
    g = int(hex_color[2:4], 16)
    b = int(hex_color[4:6], 16)
    r = max(0, min(255, int(r * factor)))
    g = max(0, min(255, int(g * factor)))
    b = max(0, min(255, int(b * factor)))
    return f'#{r:02x}{g:02x}{b:02x}'

def draw_gradient_balloon(x1, y1, x2, y2, base_color, steps=10):
    """Draw a balloon with a gradient effect to simulate a 3D look."""
    dark_factor = 0.8  # outer color multiplier
    light_factor = 1.2  # inner color multiplier
    gradient_colors = []
    for i in range(steps):
        factor = dark_factor + (light_factor - dark_factor) * (i / (steps - 1))
        gradient_colors.append(adjust_color(base_color, factor))
    
    for i in range(steps):
        dx = (x2 - x1) / (2 * steps)
        dy = (y2 - y1) / (2 * steps)
        current_x1 = x1 + i * dx
        current_y1 = y1 + i * dy
        current_x2 = x2 - i * dx
        current_y2 = y2 - i * dy
        canvas.create_oval(current_x1, current_y1, current_x2, current_y2,
                           fill=gradient_colors[i], outline="")

def get_random_letter():
    """Return a random uppercase letter."""
    return random.choice(string.ascii_uppercase)

def draw_balloon():
    """Draw a gradient 3D-looking balloon with a letter and start its floating animation."""
    global current_letter, balloon_dx, balloon_dy, move_balloon_id
    # Cancel any existing floating animation
    if move_balloon_id is not None:
        root.after_cancel(move_balloon_id)
        move_balloon_id = None

    canvas.delete("all")
    current_letter = get_random_letter()
    base_color_name = random.choice(list(color_map.keys()))
    base_color = color_map[base_color_name]
    draw_gradient_balloon(100, 100, 300, 300, base_color, steps=12)
    canvas.create_text(200, 200, text=current_letter, font=("Helvetica", 80), fill="black")
    # Set a slower random floating speed
    balloon_dx = random.choice([-2, -1, 1, 2])
    balloon_dy = random.choice([-2, -1, 1, 2])
    move_balloon()

def move_balloon():
    """Continuously move the balloon around the canvas, bouncing off edges."""
    global balloon_dx, balloon_dy, move_balloon_id
    items = canvas.find_all()
    if not items:
        return
    coords = canvas.bbox(items[0])
    if not coords:
        return
    x1, y1, x2, y2 = coords
    canvas_width = int(canvas['width'])
    canvas_height = int(canvas['height'])
    
    if x1 + balloon_dx < 0 or x2 + balloon_dx > canvas_width:
        balloon_dx = -balloon_dx
    if y1 + balloon_dy < 0 or y2 + balloon_dy > canvas_height:
        balloon_dy = -balloon_dy

    canvas.move("all", balloon_dx, balloon_dy)
    
    if game_state == "playing":
        move_balloon_id = root.after(100, move_balloon)

def pop_balloon():
    """Simulate a vibrant balloon pop with moving confetti pieces."""
    # Cancel the current floating animation when the balloon is popped
    global move_balloon_id
    if move_balloon_id is not None:
        root.after_cancel(move_balloon_id)
        move_balloon_id = None
    canvas.delete("all")
    confetti_items = []
    center_x, center_y = 200, 200
    for i in range(20):
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(5, 15)
        dx = speed * math.cos(angle)
        dy = speed * math.sin(angle)
        size = random.randint(3, 7)
        color = random.choice(["red", "yellow", "blue", "green", "purple", "orange", "pink", "cyan"])
        item = canvas.create_oval(center_x - size, center_y - size,
                                  center_x + size, center_y + size,
                                  fill=color, outline="")
        confetti_items.append((item, dx, dy))
    animate_confetti(confetti_items, 0)

def animate_confetti(confetti_items, step):
    """Animate confetti pieces by moving them outward; then clear canvas and draw a new balloon."""
    if step < 20:
        for item, dx, dy in confetti_items:
            canvas.move(item, dx, dy)
        root.after(50, lambda: animate_confetti(confetti_items, step + 1))
    else:
        canvas.delete("all")
        new_balloon()

def new_balloon():
    """Clear any messages and draw a new balloon."""
    message_label.config(text="")
    draw_balloon()

def update_timer():
    """Update the countdown timer every second."""
    global remaining_time, game_state
    if game_state == "playing":
        if remaining_time > 0:
            timer_label.config(text=f"Time: {remaining_time} sec")
            remaining_time -= 1
            root.after(1000, update_timer)
        else:
            end_game()

def end_game():
    """End the game, update high score, and show the Game Over screen."""
    global game_state, high_score
    game_state = "game_over"
    if score > high_score:
        high_score = score
    main_frame.pack_forget()
    game_over_label.config(text="Game Over!", bg="black", fg="white")
    final_score_label.config(text=f"Your Score: {score}\nHigh Score: {high_score}", bg="black", fg="white")
    retry_label.config(text="Press R to retry", bg="black", fg="white")
    game_over_frame.pack(padx=20, pady=20)

def restart_game():
    """Reset game variables and UI elements to start a new game."""
    global score, remaining_time, game_state
    score = 0
    remaining_time = 60
    game_state = "playing"
    score_label.config(text=f"Score: {score}")
    timer_label.config(text=f"Time: {remaining_time} sec")
    message_label.config(text="")
    game_over_frame.pack_forget()
    main_frame.pack(padx=20, pady=20)
    draw_balloon()
    update_timer()

def key_pressed(event):
    """Handle key presses based on the game state."""
    global score
    if game_state == "playing":
        if event.char.upper() == current_letter:
            score += 1
            score_label.config(text=f"Score: {score}")
            if correct_sound is not None:
                correct_sound.play()
            else:
                print("Sound file not loaded.")
            pop_balloon()
        else:
            message_label.config(text="Try again!", fg="red")
    elif game_state == "game_over":
        if event.char.upper() == "R":
            restart_game()

# Initialize pygame mixer for sound playback
pygame.mixer.init()
try:
    correct_sound = pygame.mixer.Sound("correct.wav")
except Exception as e:
    print("Error loading sound file:", e)
    correct_sound = None

# Global game variables
score = 0
high_score = 0
remaining_time = 60
current_letter = ""
game_state = "playing"  # "playing" or "game_over"
balloon_dx = 0
balloon_dy = 0
move_balloon_id = None  # to keep track of the scheduled after() call

# Create the main window with a black background
root = tk.Tk()
root.title("Typing Game for Kids")
root.configure(bg="black")

# Main game frame (visible during play)
main_frame = tk.Frame(root, bg="black")
main_frame.pack(padx=20, pady=20)

instruction_label = tk.Label(main_frame, text="Press the key that matches the letter in the balloon", 
                             font=("Helvetica", 20), bg="black", fg="white")
instruction_label.pack(pady=10)

# Canvas to display the balloon with a black background
canvas = tk.Canvas(main_frame, width=400, height=400, bg="black", highlightthickness=0)
canvas.pack(pady=10)

# Feedback message label
message_label = tk.Label(main_frame, text="", font=("Helvetica", 30), bg="black", fg="white")
message_label.pack(pady=10)

# Score and timer labels
score_label = tk.Label(main_frame, text=f"Score: {score}", font=("Helvetica", 24), bg="black", fg="white")
score_label.pack(pady=5)

timer_label = tk.Label(main_frame, text=f"Time: {remaining_time} sec", font=("Helvetica", 24), bg="black", fg="white")
timer_label.pack(pady=5)

# Game Over frame (hidden during play) with a black background
game_over_frame = tk.Frame(root, bg="black")
game_over_label = tk.Label(game_over_frame, text="", font=("Helvetica", 40), bg="black", fg="white")
game_over_label.pack(pady=20)
final_score_label = tk.Label(game_over_frame, text="", font=("Helvetica", 30), bg="black", fg="white")
final_score_label.pack(pady=10)
retry_label = tk.Label(game_over_frame, text="", font=("Helvetica", 24), bg="black", fg="white")
retry_label.pack(pady=10)

# Bind key events to the main window
root.bind("<Key>", key_pressed)

# Start the game by drawing the first balloon and starting the timer
draw_balloon()
update_timer()

# Start the Tkinter event loop
root.mainloop()
