import pyxel
from collections import deque
import pickle

JUMP = 30
BOXHEIGHT = 16
BOXWIDTH = 16

JUMPING = deque([0, 0, 0, 0, 1, 1, 1, 1])
WALK_L = deque([3, 4])
WALK_R = deque([2, 0])


class App:
    def __init__(self):

        pyxel.init(80, 80, title="Test!", display_scale=6)
        pyxel.load("res/res.pyxres")
        self.reset()
        pyxel.run(self.update, self.draw)

    def reset(self):
        self.me = {
            'x': (pyxel.width // 2) - (BOXWIDTH // 2),
            'y': pyxel.height - BOXHEIGHT
        }

        self.base = pyxel.height - BOXHEIGHT
        self.jumping = False
        self.falling = False
        self.expression = JUMPING

        self.direction_y = deque([0, 0, 0])

        self.dead = False

        self.explosion_col = deque([8, 4, 10])

        self.points = 0
        self.hs_saved = False

        self.level = 1
        self.level_up(self.level)

        try:
            with open('res/hs.pickle', 'rb') as handle:
                self.highscore = pickle.load(handle)
        except Exception:
            self.highscore = 0

    def update(self):
        if not self.dead:
            self.update_direction()
            self.jump()

            self.shoot_bullet()

            self.intersects()
        else:
            self.explosion()
            if not self.hs_saved and self.points > self.highscore:
                with open('res/hs.pickle', 'wb') as handle:
                    pickle.dump(self.points,
                                handle,
                                protocol=pickle.HIGHEST_PROTOCOL)
                    self.hs_saved = True

        if pyxel.btnp(pyxel.KEY_R):
            self.reset()

    def draw(self):
        pyxel.cls(0)
        pyxel.blt(
            self.me['x'],
            self.me['y'],
            0,
            0,
            self.expression[0] * BOXHEIGHT,
            BOXWIDTH,
            BOXHEIGHT,
            12,
        )

        self.bullet_draw()

        score_string = str(self.points) + ' / ' + str(self.highscore)
        score_col = 10 if self.highscore < self.points else 7

        # pyxel.text(6, 6, score_string, 13)
        pyxel.text(5, 5, score_string, score_col)
        pyxel.text(5, 13, f'Level {self.level}', score_col)


        if self.dead:
            pyxel.text(22, 21, "GAME OVER!", 8)
            pyxel.circ(self.bullet['x'], self.bullet['y'], 7, self.explosion_col[0])
            pyxel.circ(self.bullet['x'], self.bullet['y'], 4, self.explosion_col[1])
            pyxel.circ(self.bullet['x'], self.bullet['y'], 2, self.explosion_col[2])

    def update_direction(self):
        if (pyxel.btn(pyxel.KEY_LEFT) or pyxel.btn(pyxel.GAMEPAD1_BUTTON_LEFTSHOULDER)) and self.me['x'] > 0:
            self.me['x'] += -1

            if self.jumping or self.falling:
                self.expression = deque([3])
            else:
                self.expression = WALK_L
                self.expression.append(self.expression.popleft())
        elif pyxel.btn(pyxel.KEY_RIGHT) and self.me['x'] < 65:
            self.me['x'] += 1

            if self.jumping or self.falling:
                self.expression = deque([2])
            else:
                self.expression = WALK_R
                self.expression.append(self.expression.popleft())

        if pyxel.btn(pyxel.KEY_SPACE) or pyxel.btn(pyxel.KEY_UP):
            if not self.jumping and not self.falling:
                self.jumping = True
                self.expression = JUMPING

    def jump(self):
        if self.jumping and self.me['y'] == self.base - JUMP:
            self.jumping = False
            self.falling = True
        elif self.falling and self.me['y'] == self.base:
            self.jumping = False
            self.falling = False

        if self.jumping and self.me['y'] > self.base - JUMP:
            self.me['y'] -= 1
        elif self.falling and self.me['y'] < self.base:
            self.me['y'] += 1

        if self.jumping or self.falling:
            self.expression.append(self.expression.popleft())

    def bullet_draw(self):
        # pyxel.rect(self.bullet['x'], 70, 6, 6, 2)
        pyxel.blt(self.bullet['x'],
                  self.bullet['y'],
                  0,
                  self.bullet_face['x'],
                  self.bullet_face['y'],
                  7,
                  5)

    def shoot_bullet(self):
        
        if self.bullet['x'] in (-11, 90):
            self.bullet_left = not self.bullet_left
            self.points += 1
            if self.level == 1 and self.points >= 10:
                self.level = 2
                self.level_up(self.level)

        direction_x = 1 if self.bullet_left else -1

        self.bullet['x'] += direction_x

        if self.level == 1:
            if self.bullet['y'] == self.bullet_max:
                self.up = not self.up
            elif self.bullet['y'] == self.bullet_min:
                self.up = not self.up

            self.bullet['y'] += -1 if self.up else 1

        elif self.level == 2:
            if not self.direction_y:
                if self.bullet['y'] <= self.bullet_max:
                    self.direction_y = deque([1, 1, 1])
                elif self.bullet['y'] >= self.bullet_min:
                    self.direction_y = deque([-1, -1, -1])
                else:
                    self.direction_y = deque(self.bullet_moves[pyxel.rndi(0, 2)])

            self.bullet['y'] += self.direction_y.pop()

    def intersects(self):

        # charecter rects minus arms and legs

        me_top_right_x = self.me['x'] + BOXWIDTH - 4
        me_top_right_y = self.me['y'] + 3
        me_bottom_left_x = self.me['x'] + 3
        me_bottom_left_y = self.me['y'] + BOXHEIGHT - 4

        bullet_top_right_x = self.bullet['x'] + 7
        bullet_top_right_y = self.bullet['y']
        bullet_bottom_left_x = self.bullet['x']
        bullet_bottom_left_y = self.bullet['y'] + 5

        if not (me_top_right_x < bullet_bottom_left_x or me_bottom_left_x > bullet_top_right_x or me_top_right_y > bullet_bottom_left_y or me_bottom_left_y < bullet_top_right_y):
            self.dead = True

    def explosion(self):
        self.explosion_col.append(self.explosion_col.popleft())

    def level_up(self, num):
        if num == 1:
            self.bullet = {
                'x': -10,
                'y': 70
            }

            self.bullet_left = True

            self.bullet_face = {
                'x': 25,
                'y': 11
            }

            self.bullet_min = 75
            self.bullet_max = 50

            self.bullet_moves = [
                [-1],
                [0, 0, 0],
                [1]
            ]

            self.up = True

        elif num == 2:
            # self.bullet = {
            #     'x': -10,
            #     'y': 70
            # }

            # self.bullet_left = True

            self.bullet_face = {
                'x': 17,
                'y': 11
            }

            self.bullet_min = 75
            self.bullet_max = 50

            self.bullet_moves = [
                [-1, -1, -1],
                [0, 0, 0],
                [1, 1, 1]
            ]


App()
