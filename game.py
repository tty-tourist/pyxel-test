import pyxel
from collections import deque

JUMP = 30
BOXHEIGHT = 16
BOXWIDTH = 16

JUMPING = deque([0, 0, 0, 0, 1, 1, 1, 1])
WALK_L = deque([3, 4])
WALK_R = deque([2, 0])


class App:
    def __init__(self):

        pyxel.init(80, 80, title="Test!", display_scale=6)
        pyxel.load("res.pyxres")
        self.reset()
        pyxel.run(self.update, self.draw)

    def reset(self):
        self.me_x = (pyxel.width // 2) - (BOXWIDTH // 2)
        self.me_y = pyxel.height - BOXHEIGHT
        self.base = pyxel.height - BOXHEIGHT
        self.jumping = False
        self.falling = False
        self.expression = JUMPING

        self.bullet_x = -10
        self.bullet_y = 70
        self.bullet_left = True
        self.direction_y = deque([0, 0, 0])

        self.dead = False

        self.explosion_col = deque([8, 4, 10])

        self.points = 0

    def update(self):
        if not self.dead:
            self.update_direction()
            self.jump()

            self.shoot_bullet()

            self.intersects()
        else:
            self.explosion()

        if pyxel.btnp(pyxel.KEY_R):
            self.reset()


    def draw(self):
        pyxel.cls(0)
        self.bullet()
        pyxel.blt(
            self.me_x,
            self.me_y,
            0,
            0,
            self.expression[0] * BOXHEIGHT,
            BOXWIDTH,
            BOXHEIGHT,
            12,
        )

        self.bullet()

        pyxel.text(5, 5, str(self.points), 7)

        if self.dead:
            pyxel.text(22, 25, "GAME OVER!", 8)
            pyxel.circ(self.bullet_x, self.bullet_y, 7, self.explosion_col[0])
            pyxel.circ(self.bullet_x, self.bullet_y, 4, self.explosion_col[1])
            pyxel.circ(self.bullet_x, self.bullet_y, 2, self.explosion_col[2])


    def update_direction(self):
        if pyxel.btn(pyxel.KEY_LEFT) and self.me_x > 0:
            self.me_x += -1

            if self.jumping or self.falling:
                self.expression = deque([3])
            else:
                self.expression = WALK_L
                self.expression.append(self.expression.popleft())
        elif pyxel.btn(pyxel.KEY_RIGHT) and self.me_x < 65:
            self.me_x += 1

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
        if self.jumping and self.me_y == self.base - JUMP:
            self.jumping = False
            self.falling = True
        elif self.falling and self.me_y == self.base:
            self.jumping = False
            self.falling = False

        if self.jumping and self.me_y > self.base - JUMP:
            self.me_y -= 1
        elif self.falling and self.me_y < self.base:
            self.me_y += 1

        if self.jumping or self.falling:
            self.expression.append(self.expression.popleft())

    def bullet(self):
        # pyxel.rect(self.bullet_x, 70, 6, 6, 2)


        pyxel.blt(self.bullet_x, self.bullet_y, 0, 17, 11, 7, 5)

    def shoot_bullet(self):
        
        if self.bullet_x in (-11, 90):
            self.bullet_left = not self.bullet_left
            self.points += 1

        direction_x = 1 if self.bullet_left else -1

        self.bullet_x += direction_x

        if not self.direction_y:
            if self.bullet_y <= 50:
                self.direction_y = deque([1, 1 , 1])
            elif self.bullet_y >= 75:
                self.direction_y = deque([-1, -1 , -1])
            else:
                self.direction_y = deque([pyxel.rndi(-1, 1)] * 3)

        self.bullet_y += self.direction_y.pop()

    def intersects(self):

        # charecter rects minus arms and legs

        me_top_right_x = self.me_x + BOXWIDTH - 4
        me_top_right_y = self.me_y + 3
        me_bottom_left_x = self.me_x + 3
        me_bottom_left_y = self.me_y + BOXHEIGHT - 4

        bullet_top_right_x = self.bullet_x + 7
        bullet_top_right_y = self.bullet_y
        bullet_bottom_left_x = self.bullet_x
        bullet_bottom_left_y = self.bullet_y + 5

        if not (me_top_right_x < bullet_bottom_left_x or me_bottom_left_x > bullet_top_right_x or me_top_right_y > bullet_bottom_left_y or me_bottom_left_y < bullet_top_right_y):
            self.dead = True

    def explosion(self):
        self.explosion_col.append(self.explosion_col.popleft())



App()

