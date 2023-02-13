from random import *


class BoardException(Exception):
    pass


class BoardOutException(BoardException):
    def __str__(self):
        return "Вы пытаетесь выстрелить за доску!"


class BoardUsedException(BoardException):
    def __str__(self):
        return "Вы уже стреляли в эту клетку"


class BoardWrongShipException(BoardException):
    """Исключение для размещения кораблей"""
    pass


class Dot:
    def __init__(self, x, y):
        """Класс точнек на доске с координатами x и y"""
        self.x = x
        self.y = y

    def __eq__(self, other):
        """Метод проверки точек на равенство"""
        return self.x == other.x and self.y == other.y

    def __repr__(self):
        """Метод выводящий точки в консоль"""
        return f"({self.x}, {self.y})"


class Ship:
    """Корабль на игровом поле"""

    def __init__(self, bow, l, o):
        self.bow = bow  # длина корабля
        self.l = l  # точка, где размещен нос корабля
        self.o = o  # вертикальное/горизонтальное направление корабля
        self.lives = l  # количество неподбитых точек

    @property
    def dots(self):
        """Метод возвращающий список всех точек корабля"""
        ship_dots = []
        for i in range(self.l):
            cur_x = self.bow.x
            cur_y = self.bow.y

            if self.o == 0:
                cur_x += i

            elif self.o == 1:
                cur_y += i

            ship_dots.append(Dot(cur_x, cur_y))

        return ship_dots

    def shooten(self, shot):
        """Метод показывающий попали ли мы в корабль"""
        return shot in self.dots


class Board:
    """Игровое поле"""

    def __init__(self, size=10, hid=False):
        self.size = size
        self.hid = hid
        self.count = 0  # количество пораженных кораблей
        self.field = [["☖"] * size for _ in range(size)]  # сетка состояний
        self.busy = []  # занятая точка, или точка, куда сделали выстрел
        self.ships = []  # список кораблей доски

    def __str__(self):
        res = ""
        res += "  | 1  | 2 | 3 | 4 |  5 | 6 |"
        for i, row in enumerate(self.field):
            res += f"\n{i + 1} | " + " | ".join(row) + " |"

        if self.hid:
            res = res.replace("☗", "☖")
        return res

    def out(self, d):
        """Находится ли точка в пределах доски"""
        return not ((0 <= d.x < self.size) and (0 <= d.y < self.size))

    def contour(self, ship, verb=False):
        """Метод позволяющий разместить "корабли" так, чтобы они не соприкасались друг с другом"""
        near = [
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1), (0, 0), (0, 1),
            (1, -1), (1, 0), (1, 1)
        ]
        for d in ship.dots:
            for dx, dy in near:
                cur = Dot(d.x + dx, d.y + dy)
                if not (self.out(cur)) and cur not in self.busy:
                    if verb:
                        self.field[cur.x][cur.y] = "."
                    self.busy.append(cur)

    def add_ship(self, ship):
        """Метод для размещения корабля"""
        for d in ship.dots:
            if self.out(d) or d in self.busy:
                raise BoardWrongShipException()
        for d in ship.dots:
            self.field[d.x][d.y] = "☗"
            self.busy.append(d)

        self.ships.append(ship)
        self.contour(ship)

    def shot(self, d):
        if self.out(d):
            raise BoardOutException()

        if d in self.busy:
            raise BoardUsedException()

        self.busy.append(d)

        for ship in self.ships:
            if ship.shooten(d):
                ship.lives -= 1
                self.field[d.x][d.y] = "X"
                if ship.lives == 0:
                    self.count += 1
                    self.contour(ship, verb=True)
                    print("Корабль уничтожен!")
                    return False
                else:
                    print("Корабль ранен!")
                    return True

        self.field[d.x][d.y] = "."
        print("Мимо!")
        return False

    def begin(self):
        self.busy = []


class Player:
    def __init__(self, board, enemy):
        self.board = board
        self.enemy = enemy

    def ask(self):
        raise NotImplementedError()

    def move(self):
        while True:
            try:
                target = self.ask()
                repeat = self.enemy.shot(target)
                return repeat
            except BoardException as e:
                print(e)


class AI(Player):
    """Класс компьютера"""
    def ask(self):
        d = Dot(randint(0, 5), randint(0, 5))
        print(f"Ход компьютера: {d.x + 1} {d.y + 1}")
        return d


class User(Player):
    """Класс игрока"""

    def ask(self):
        while True:
            cords = input("Ваш ход: ").split()
            if len(cords) != 2:
                print(" Введите 2 координаты! ")
                continue
            x, y = cords
            if not (x.isdigit()) or not (y.isdigit()):
                print(" Введите числа! ")
                continue
            x, y = int(x), int(y)
            return Dot(x - 1, y - 1)


class Game:
    """Класс игры"""

    def __init__(self, size=6):
        self.size = size
        user = self.random_board()  # доска игрока
        comp = self.random_board()  # доска компьютера
        comp.hid = True  # скрываем ли доску компьютера

        self.ai = AI(comp, user)
        self.us = User(user, comp)

    def random_board(self):
        board = None
        while board is None:
            board = self.random_place()
        return board

    def random_place(self):
        lens = [4, 3, 2, 2, 1, 1, 1]
        board = Board(size=self.size)
        attempts = 0
        for l in lens:
            while True:
                attempts += 1
                if attempts > 2000:
                    return None
                ship = Ship(Dot(randint(0, self.size), randint(0, self.size)), l, randint(0, 1))
                try:
                    board.add_ship(ship)
                    break
                except BoardWrongShipException:
                    pass
        board.begin()
        return board

    def greet(self):
        print("=" * 27, "|")
        print("       Приветсвуем вас      |")
        print("           в игре           |")
        print("         морской бой        |")
        print("=" * 27, "|")
        print("      формат ввода: x y     |")
        print("      x - номер строки      |")
        print("      y - номер столбца     |")
        print("=" * 27, "|")

    def loop(self):
        num = 0
        while True:
            print("     Доска пользователя:")
            print(self.us.board)
            print("=" * 29)
            print("     Доска компьютера:")
            print(self.ai.board)
            if num % 2 == 0:
                print("=" * 29)
                print("Ходит пользователь!")
                repeat = self.us.move()
            else:
                print("=" * 29)
                print("Ходит компьютер!")
                repeat = self.ai.move()
            if repeat:
                num -= 1

            if self.ai.board.count == 7:
                print("=" * 20)
                print("Пользователь выиграл!")
                print(self.ai.board)
                break

            if self.us.board.count == 7:
                print("=" * 20)
                print("Компьютер выиграл!")
                print(self.us.board)
                break
            num += 1

    def start(self):
        self.greet()
        self.loop()


g = Game()
g.start()
