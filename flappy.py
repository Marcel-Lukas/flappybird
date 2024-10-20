from ursina import *
import random
import time

app = Ursina()

# Punktzahl initialisieren
score = 0
score_text = Text(text=f'Punkte: {score}', origin=(-0.5, 0.5), scale=2, position=(-0.85, 0.47))

# Timer initialisieren
start_time = time.time()
time_text = Text(text='Zeit: 0s', origin=(-0.5, 0.5), scale=2, position=(-0.85, 0.4))

def setup_game():
    global bird, pipes, coins, create_pipes_task, background, start_time
    # Sky()
    background = Entity(model='quad', texture='assets/hintergrund.png', scale=(40, 25), z=10)  # Hintergrund als Quad erstellen
    bird = Animation('assets/bird_blue', scale=2)
    bird.collider = BoxCollider(bird, center=(0, 0, 0), size=(0.8, 0.8, 0.8))  # Manuelle Anpassung der Hitbox
    camera.orthographic = True
    camera.fov = 22
    pipes = []
    coins = []

    create_pipes_task = invoke(create_pipes, delay=1)
    invoke(create_coin, delay=2)
    
    start_time = time.time()  # Setzt den Timer bei Spielstart zurück

def update():
    global score
    if bird.enabled:
        bird.y -= 0.005  # Schwerkraft
        
        if held_keys['space']:
            bird.y += 0.01  # Hochsteuern bei gedrückter Leertaste

        if held_keys['up arrow']:
            bird.y += 0.01  # Hochsteuern bei gedrückter Pfeil-hoch-Taste
            
        if held_keys['down arrow']:
            bird.y -= 0.01  # Runtersteuern bei gedrückter Pfeil-runter-Taste

        for pipe in pipes:  # Bewegt Röhren nach links
            pipe.x -= 0.02

        for coin in coins:  # Bewegt Münzen nach links und überprüft Kollision
            coin.x -= 0.02
            if bird.intersects(coin).hit:
                score += 80
                score_text.text = f'Punkte: {score}'
                if coin in coins:
                    coins.remove(coin)
                destroy(coin)

        # Aktualisiere den Timer
        elapsed_time = int((time.time() - start_time) * 1000)
        time_text.text = f'Zeit: {elapsed_time // 100}'

        # Prüft ob es zu einer Kollisionen gekommen ist oder ob sich der Vogel außerhalb des Bereichs befindet.           
        if bird.y < -10 or bird.y > 10 or bird.intersects().hit: 
            game_over()

def input(key):
    if key == 'space' and bird.enabled:
        bird.y += 1.1

    if key == 'enter' and not bird.enabled:
        restart_game()

def game_over():
    global game_over_text, restart_button
    game_over_text = Text(text='Game Over', origin=(0, 0), scale=7, color=color.white)
    restart_button = Button(text='Neustart', color=color.azure, scale=(0.2, 0.1), position=(0, -0.2))
    restart_button.on_click = restart_game
    bird.disable()
    for pipe in pipes:
        pipe.disable()
    for coin in coins:
        coin.disable()

def restart_game():
    global score
    score = 0
    score_text.text = f'Punkte: {score}'
    for pipe in pipes:
        destroy(pipe)
    pipes.clear()
    for coin in coins:
        destroy(coin)
    coins.clear()
    game_over_text.disable()
    restart_button.disable()
    setup_game()

def create_pipes():
    new_y = random.randint(4, 12)
    gap_size = random.randint(19, 23)  # Zufällige Lücke zwischen 19 und 23
    new_pipe_top = Entity(model='quad', 
                          texture='assets/rohroben.png',
                          position=(20, new_y),
                          scale=(3, 15, 1),
                          collider='box')
    new_pipe_bottom = Entity(model='quad', 
                             texture='assets/rohrunten.png',
                             position=(20, new_y - gap_size),   # Die Lücke zwischen den Röhren
                             scale=(3, 15, 1),
                             collider='box')
    pipes.append(new_pipe_top)
    pipes.append(new_pipe_bottom)
    
    # Erstellung der nächsten Röhren
    global create_pipes_task
    create_pipes_task = invoke(create_pipes, delay=random.uniform(1.5, 4))

def create_coin():
    new_y = random.uniform(-8, 8)
    new_coin = Entity(model='quad', 
                      texture='assets/coin.png',
                      position=(20, new_y),
                      scale=(1.5, 1.5),
                      collider='box')
    
    # Münze kollidiert nicht mit Röhren
    for pipe in pipes:
        if new_coin.intersects(pipe).hit:
            destroy(new_coin)
            invoke(create_coin, delay=0.1)
            return
    
    coins.append(new_coin)
    # Erstellung der nächsten Münze
    invoke(create_coin, delay=random.uniform(0.2, 1.9))

setup_game()
app.run()
