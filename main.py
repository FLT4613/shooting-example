import itertools
import random

import numpy
import pyxel


class Point:
    def __init__(self, x, y):
        self._pos = numpy.array([x, y])

    def get(self):
        return self._pos

    def set(self, x, y):
        self._pos[0] = x
        self._pos[1] = y

    @property
    def x(self):
        return self._pos[0]

    @property
    def y(self):
        return self._pos[1]

    @x.setter
    def x(self, x):
        self._pos[0] = x

    @y.setter
    def y(self, y):
        self._pos[1] = y


class Circle:
    def __init__(self, x, y, r):
        self._pos = Point(x, y)
        self.r = r

    @property
    def center(self):
        return self._pos

    def set(self, x, y):
        self._pos.set(x, y)


class Line:
    def __init__(self, x1, y1, x2, y2):
        self._pos1 = Point(x1, y1)
        self._pos2 = Point(x2, y2)

    def set(self, x1, y1, x2, y2):
        self._pos1 = Point(x1, y1)
        self._pos2 = Point(x2, y2)
        if self._pos1 == self._pos2:
            raise ValueError

    def get(self):
        return [self._pos1, self._pos2]


def collide(self, a, b, callback):
    if not isinstance(a, list):
        a = [a]
    if not isinstance(b, list):
        b = [b]

    for obj_a, obj_b in itertools.product(a, b):
        hitboxes = set([type(obj_a.hitbox), type(obj_b.hitbox)])
        if hitboxes == set([Circle]):
            norm = numpy.linalg.norm(obj_b.pos - obj_a.pos)
            r = abs(obj_a.hitbox.r + obj_b.hitbox.r)
            if norm <= r:
                callback(obj_a, obj_b)
        else:
            raise TypeError


class Character:
    def __init__(self, x, y):
        self.pos = numpy.array([x, y])

    @property
    def x(self):
        return self.pos[0]

    @property
    def y(self):
        return self.pos[1]

    @x.setter
    def x(self, arg):
        self.pos[0] = arg

    @y.setter
    def y(self, arg):
        self.pos[1] = arg


class Player(Character):
    bullets = []

    def __init__(self, x, y):
        super().__init__(x, y)
        self.speed = 2
        self.r = 5
        self.hitbox = Circle(self.x, self.y, self.r)
        self.bullet_type = 'NORMAL'

    def update(self):
        if pyxel.btn(pyxel.KEY_W):
            self.y = max(self.y - self.speed, self.r)
        if pyxel.btn(pyxel.KEY_A):
            self.x = max(self.x - self.speed, self.r)
        if pyxel.btn(pyxel.KEY_S):
            self.y = min(self.y + self.speed, 120 - self.r)
        if pyxel.btn(pyxel.KEY_D):
            self.x = min(self.x + self.speed, 160 - self.r)
        if self.bullet_type == 'NORMAL':
            if pyxel.btnp(pyxel.KEY_M, 0, 5):
                self.bullets.append(Bullet(self.x, self.y, self.bullet_type))
        if self.bullet_type == 'RAPID':
            if pyxel.btnp(pyxel.KEY_M, 0, 2):
                self.bullets.append(Bullet(self.x, self.y, self.bullet_type))
        self.hitbox.set(self.x, self.y)
        for bullet in self.bullets:
            bullet.update()
            if bullet.x > 160 or bullet.y <= 0 or 120 <= bullet.y:
                self.bullets.remove(bullet)

    def draw(self):
        pyxel.circ(self.x, self.y, self.r, 9)
        for bullet in self.bullets:
            bullet.draw()


class Enemies:
    def __init__(self):
        self.members = []

    def draw(self):
        for enemy in self.members:
            enemy.draw()

    def update(self):
        if pyxel.frame_count % 60 == 0:
            self.members.append(Enemy(160, random.randint(5, 95)))

        for enemy in self.members:
            if enemy.x < 0:
                self.members.remove(enemy)

        for enemy in self.members:
            enemy.update()

    def add(self, x, y):
        self.members.append(Enemy(x, y))

    def remove(self, member):
        self.members.remove(member)


class Enemy(Character):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.r = 5
        self.hitbox = Circle(self.x, self.y, self.r)

    def update(self):
        self.x -= 1
        self.hitbox.set(self.x, self.y)

    def draw(self):
        pyxel.circ(self.x, self.y, self.r, 2)


class Bullet(Character):
    bullet_type = [
        'NORMAL',
        'RAPID',
        'LAZER'
    ]

    def __init__(self, x, y, bullet_type):
        super().__init__(x, y)
        self.property = bullet_type
        self.r = 5

        if self.property == 'NORMAL':
            self.hitbox = Circle(self.x, self.y, self.r)

        if self.property == 'RAPID':
            self.y += random.uniform(-5, 5)
            self.hitbox = Circle(self.x, self.y, 1)

    def draw(self):
        if self.property == 'NORMAL':
            pyxel.line(self.x, self.y, self.x+3, self.y, 10)
        if self.property == 'RAPID':
            pyxel.pix(self.x, self.y, 10)
        if self.property == 'LAZER':
            pyxel.line(self.x, self.y, self.x+100, self.y, 10)

    def update(self):
        if self.property == 'NORMAL':
            self.x += 3
            self.hitbox.set(self.x, self.y)
        if self.property == 'RAPID':
            self.x += 6
            self.hitbox.set(self.x, self.y)
        if self.property == 'LAZER':
            self.x += 10


class Item(Character):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.hitbox = Circle(self.x, self.y, 3)

    def draw(self):
        pyxel.circ(self.x, self.y, 3, 5)


class EffectManager:
    def __init__(self):
        self.targets = []

    def draw(self):
        for target in self.targets:
            target.draw()

    def update(self):
        for target in self.targets:
            target.update()

    def add(self, effect_class, x, y):
        self.targets.append(effect_class(x, y))


class Effect1(Character):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.start_frame = pyxel.frame_count
        self.end_frame = 10
        self.r = 0

    def draw(self):
        if pyxel.frame_count - self.start_frame < self.end_frame:
            pyxel.circ(self.x, self.y, self.r, 8)

    def update(self):
        self.r += 1


class Effect2(Character):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.start_frame = pyxel.frame_count
        self.end_frame = 10
        self.r = 0

    def draw(self):
        if pyxel.frame_count - self.start_frame < self.end_frame:
            pyxel.circb(self.x, self.y, self.r, 7)

    def update(self):
        self.r += 1


class UI:
    def __init__(self):
        pass

    def draw(self):
        pyxel.rect(0, 100, 160, 120, 0)
        pyxel.line(0, 100, 160, 100, 7)

    def update(self):
        pass


class BackGround:
    def __init__(self):
        self.stars = []

    def draw(self):
        for star in self.stars:
            pyxel.pix(star[0], star[1], 7)

    def update(self):
        # 生成
        if pyxel.frame_count % 10 == 0:
            stars = [
                [160, random.randint(5, 95), -random.uniform(0.8, 2)]
                for x in range(random.randint(3, 10))
            ]
            self.stars.extend(stars)

        # 移動
        for index in range(len(self.stars)):
            self.stars[index][0] += self.stars[index][2]

        for star in self.stars:
            if self.stars[index][0] < 0:
                self.stars.remove(star)


class App:
    def __init__(self):
        pyxel.init(160, 120)

        self.player = Player(10, 10)
        self.enemies = Enemies()
        self.items = []
        self.effects = EffectManager()
        self.ui = UI()
        self.bg = BackGround()
        pyxel.run(self.update, self.draw)

    def update(self):
        self.player.update()
        self.enemies.update()
        self.effects.update()
        self.ui.update()
        self.bg.update()

        def callback_enemy(a, b):
            self.effects.add(Effect1, b.x, b.y)
            self.enemies.remove(b)

        def callback_bullet_enemy(a, b):
            self.effects.add(Effect1, b.x, b.y)
            if a in self.player.bullets:
                self.player.bullets.remove(a)
            if b in self.enemies.members:
                self.enemies.remove(b)
            if random.random() < 0.2:
                self.items.append(Item(b.x, b.y))

        def callback_item(a, b):
            self.effects.add(Effect2, b.x, b.y)
            a.bullet_type = 'RAPID'
            self.items.remove(b)

        collide(self, a=self.player, b=self.enemies.members, callback=callback_enemy)
        collide(self, a=self.player, b=self.items, callback=callback_item)
        collide(self, a=self.player.bullets, b=self.enemies.members, callback=callback_bullet_enemy)

    def draw(self):
        pyxel.cls(0)
        self.bg.draw()

        self.player.draw()
        self.enemies.draw()
        for item in self.items:
            item.draw()
        self.effects.draw()
        self.ui.draw()


App()
