#!/usr/bin/env python3

import os
import time
import random
import shutil
import sys

# ----------------------------
# Terminal helpers
# ----------------------------

def term_size():
    return shutil.get_terminal_size((80, 24))

WIDTH, HEIGHT = term_size()

def hide_cursor():
    print("\033[?25l", end="")

def show_cursor():
    print("\033[?25h", end="")

def move(x, y):
    return f"\033[{y};{x}H"

def clear():
    print("\033[2J", end="")

def color(text, c):
    return f"\033[38;5;{c}m{text}\033[0m"

GREEN_GRADIENT = [
    34,
    40,
    46,
    82,
    118,
    154,
    148,
    112,
    76,
    40,
]



def gradient(text, phase=0):

    if not text:
        return ""

    out = ""
    steps = len(GREEN_GRADIENT) - 1

    for i, ch in enumerate(text):

        # shift index using phase for shimmer
        pos = (i + phase) % len(text)
        index = int(pos * steps / max(len(text) - 1, 1))
        color_id = GREEN_GRADIENT[index]

        out += color(ch, color_id)

    return out




# ----------------------------
# Renderer
# ----------------------------

class Renderer:

    def __init__(self):
        self.buffer = {}

    def draw(self, x, y, text, c=None):

        if y < 1 or y > HEIGHT:
            return

        if x < 1 or x > WIDTH:
            return

        if c:
            text = color(text, c)

        self.buffer[(x, y)] = text

    def render(self):

        output = []

        for (x, y), text in self.buffer.items():
            output.append(move(x, y) + text)

        print("".join(output), end="", flush=True)

        self.buffer.clear()


# ----------------------------
# Shamrock object
# ----------------------------

SHAMROCK = [
"  .-.",
" (   )",
"(_' '_)",
"  /_\\"
]

import math

class Shamrock:

    def __init__(self):
        self.base_x = random.randint(1, WIDTH - 6)
        self.y = -len(SHAMROCK)
        self.speed = random.choice([1, 1, 1, 2])
        self.color = random.choice(GREEN_GRADIENT)

    def update(self):
        self.y += self.speed

    def draw_with_offset(self, r, offset):
        x = self.base_x + offset
        for i, line in enumerate(SHAMROCK):
            r.draw(x, self.y + i, line, self.color)

    def alive(self):
        return self.y < HEIGHT




# ----------------------------
# Confetti
# ----------------------------

class Confetti:
    SYMBOLS = ["☘️", "💰", "💚", "🍀"]

    def __init__(self, exclude=None):
        while True:
            self.x = random.randint(1, WIDTH)
            self.y = random.randint(1, HEIGHT)
            if exclude is None or not (
                exclude[0] <= self.x <= exclude[2] and
                exclude[1] <= self.y <= exclude[3]
            ):
                break
        self.symbol = random.choice(self.SYMBOLS)
        self.color = random.choice(GREEN_GRADIENT)

    def draw(self, r):
        r.draw(self.x, self.y, self.symbol, self.color)


# ----------------------------
# Floating message
# ----------------------------

MESSAGES = [
"environment lucky",
"works on my machine ¯\_(ツ)_/¯",
"reproducibility increased",
"flox magic ready",
"shell fortune +10",
"nix spirits pleased",
"legendary developer",
"+2 to debugging"
]

class Message:

    def __init__(self):
        self.text = random.choice(MESSAGES)
        self.x = random.randint(1, WIDTH - len(self.text))
        self.y = random.randint(3, HEIGHT - 3)
        self.life = 60
        self.max_life = self.life
        self.phase = random.randint(0, 20)

    def update(self):
        self.life -= 1
        self.phase += 1

    def draw_eased(self, r):

        # easing curve (fade in/out feel)
        progress = 1 - (self.life / self.max_life)

        offset_y = int(math.sin(progress * math.pi) * -1)

        r.draw(
            self.x,
            self.y + offset_y,
            gradient(self.text, self.phase)
        )

    def alive(self):
        return self.life > 0




# ----------------------------
# Slot machine intro
# ----------------------------

def slot_machine():

    symbols = ["🍀", "🌈", "⭐"]

    for i in range(20):

        clear()

        print(move(WIDTH//2 - 10, HEIGHT//2 - 2) +
              gradient("spinning the wheel"))

        roll = " ".join(random.choice(symbols) for _ in range(3))

        print(move(WIDTH//2 - 4, HEIGHT//2) +
              gradient(roll))

        time.sleep(0.07)

    clear()

    print(move(WIDTH//2 - 6, HEIGHT//2) +
          gradient("🍀 jackpot 🍀"))

    time.sleep(1)


# ----------------------------
# Main animation loop
# ----------------------------

def animation():

    r = Renderer()

    shamrocks = []
    messages = []

    start = time.time()
    frame = 0

    while time.time() - start < 8:

        print("\033[2J", end="")  # clear screen each frame

        # spawn shamrocks
        if random.random() < 0.08:
            shamrocks.append(Shamrock())

        # spawn messages
        if random.random() < 0.03:
            messages.append(Message())

        # update shamrocks with sway
        for s in shamrocks:
            s.update()
            sway = int(2 * math.sin(frame * 0.1 + s.y * 0.2))
            s.draw_with_offset(r, sway)

        # update messages with easing
        for m in messages:
            m.update()
            m.draw_eased(r)

        shamrocks[:] = [s for s in shamrocks if s.alive()]
        messages[:] = [m for m in messages if m.alive()]

        r.render()

        frame += 1
        time.sleep(0.05)


# ----------------------------
# Confetti finale
# ----------------------------

def finale():

    r = Renderer()

    msg = "Happy St. Patrick's Day from Flox"
    msg_x = WIDTH // 2 - 10
    msg_y = HEIGHT // 2
    exclude = (msg_x - 1, msg_y - 1, msg_x + len(msg) + 1, msg_y + 1)

    confetti = [Confetti(exclude=exclude) for _ in range(200)]

    for _ in range(30):

        for c in confetti:
            c.draw(r)

        print(move(WIDTH//2 - 10, HEIGHT//2) +
              gradient("Happy St. Patrick's Day from Flox"))

        r.render()

        time.sleep(0.1)

def luck_meter():

    meter_width = 30
    x = WIDTH // 2 - meter_width // 2
    y = HEIGHT // 2 - 2

    for i in range(meter_width + 1):

        filled = "█" * i
        empty = "░" * (meter_width - i)

        percent = int((i / meter_width) * 100)

        print("\033[2J", end="")

        print(move(x, y) +
              gradient("flox environment luck"))

        print(move(x, y + 1) +
              gradient(f"[{filled}{empty}] {percent}%", phase=i))

        time.sleep(0.04)

    time.sleep(0.4)

    print(move(x, y + 3) +
          gradient("status: LEGENDARY"))

    time.sleep(1.5)


FORTUNES = [
    "great builds await you",
    "your cache will always be warm",
    "your dependencies will align",
    "you will ship without bugs",
    "fortune favors reproducibility",
    "today is a lucky deploy day",
    "wisdom will guide your shell commands",
]

def fortune():

    print("\033[2J", end="")

    print(move(WIDTH//2 - 18, HEIGHT//2 - 2) +
          gradient("press enter to receive your fortune"))

    input()

    luck_meter()

    print("\033[2J", end="")

    f = random.choice(FORTUNES)

    print(move(WIDTH//2 - len(f)//2, HEIGHT//2) +
          gradient(f))

    print(move(WIDTH//2 - 10, HEIGHT//2 + 2) +
          gradient("🍀 good luck 🍀"))

    time.sleep(3)



# ----------------------------
# Run
# ----------------------------

def main():

    hide_cursor()
    clear()

    try:

        slot_machine()
        clear()

        animation()
        clear()

        finale()

        print(move(WIDTH//2 - 14, HEIGHT//2 + 2) +
              gradient("happy st patrick's day 🍀"))

        fortune()
        print("\n")

    finally:
        show_cursor()


if __name__ == "__main__":
    main()
