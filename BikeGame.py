
# https://pygame-zero.readthedocs.io/en/stable/resources.html
# https://pygame-zero.readthedocs.io/en/stable/introduction.html
import pgzrun

WIDTH = 1280
HEIGHT = 720

moon = Actor('moon_lat0_long0_resized720p.png')
moon.pos = (WIDTH // 2, HEIGHT // 2)
moon.angle = 0

landerPosition = (0, HEIGHT // 2)
landerVelocity = (10, 0)

thrustLevel = 0
fuelRemaining = 100

def initalize():
    music.play('rocketman')

def draw():
    global landerPosition, fuelRemaining

    screen.clear()
    moon.draw()
    screen.draw.circle(landerPosition, 30, 'white')

    if fuelRemaining < 0:
        screen.draw.text("Game Over", (WIDTH // 2 - 100, HEIGHT // 2))
    else:
        screen.draw.text(f"Fuel: {fuelRemaining}%", (10, 10))

def update_fuel(thrustLevel):
    global fuelRemaining, landerPosition

    if keyboard.up and thrustLevel > 0 and fuelRemaining > 0:
        sounds.thrust.play()
        fuelRemaining -= 1
        landerPosition = (landerPosition[0]*(thrustLevel * 10), landerPosition[1])
        draw()

    if keyboard.down or thrustLevel == 0 or fuelRemaining <= 0:
        sounds.thrust.stop()
        draw()

def on_mouse_down(pos, button):
    if button == mouse.LEFT:
        print(f"You click left button at {pos}")


def update():
    global thrustLevel

    if keyboard.k_1:
        thrustLevel = 0
    elif keyboard.k_2:
        thrustLevel = 1
    elif keyboard.k_3:
        thrustLevel = 2

    print(f"Thrust Level: {thrustLevel}")

    update_fuel(thrustLevel)
    #clock.schedule_unique(update_fuel, 0.250)


pgzrun.go()
