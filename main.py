# Игра "Морской бой" v1.0

from random import randint
from colorama import init

init()

CR0, CR1, CR2, CR3 = '\033[90m', '\033[91m', '\033[92m', '\033[93m'
CR4, CBG, CED = '\033[94m', '\033[40m', '\033[0m'
LET = 'abcdefghik'  # Буквы для названия строк поля

# Создаёт все возможные ходы для компьютера
ai_move_coords = []
for i in range(10):
    for j in range(10):
        c = (i, j)
        ai_move_coords.append(c)
    j = 0


# Собственные классы исключений
class BoardException(Exception):
    pass


class BoardOutException(BoardException):
    def __str__(self):
        return f'{CR1}Вы стреляете за пределы игровой доски{CED}'


class BoardUsedException(BoardException):
    def __str__(self):
        return f'{CR1}Вы уже стреляли в эту клетку{CED}'


class BoardWrongShipException(BoardException):
    pass


# Точка
class Dot:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __repr__(self):
        return f"Dot({self.x}, {self.y})"


# Корабль
class Ship:
    def __init__(self, bow, l, o):
        self.bow = bow
        self.l = l
        self.o = o
        self.lives = l

    # Рисует корабль в указанных координатах
    @property
    def dots(self):
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

    # Проверка попадания в корабль
    def shooten(self, shot):
        return shot in self.dots


# Поле
class Board:
    def __init__(self, hid=False, size=10):
        self.hid = hid
        self.size = size
        self.count = 0
        self.field = [[f'{CR0}·{CED}'] * size for _ in range(size)]
        self.busy = []
        self.ships = []

    def __str__(self):
        res = ''
        res += '   1  2  3  4  5  6  7  8  9  10 '
        for i, row in enumerate(self.field):
            res += f'\n{LET[i].upper()} {CBG} ' + \
                   f'{CBG}  '.join(row) + f'{CBG} {CED}'

        # Заменяет символы корабля на пустые клетки
        if self.hid:
            res = res.replace(f'{CR4}■{CED}', f'{CR0}·{CED}')
        return res

    # Проверка нахождения точки за пределами доски
    def out(self, d):
        return not ((0 <= d.x < self.size) and (0 <= d.y < self.size))

    # Контур корабля
    def contour(self, ship, verb=False):
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
                        # Рисует контур вокруг подбитого корабля
                        self.field[cur.x][cur.y] = f'{CR3}×{CED}'
                    self.busy.append(cur)

    # Добавление корабля на поле
    def add_ship(self, ship):
        for d in ship.dots:
            if self.out(d) or d in self.busy:
                raise BoardWrongShipException()
        for d in ship.dots:
            self.field[d.x][d.y] = f'{CR4}■{CED}'
            self.busy.append(d)

        self.ships.append(ship)
        self.contour(ship)

    # Стрельба по полю
    def shot(self, d):
        if self.out(d):
            raise BoardOutException()

        if d in self.busy:
            raise BoardUsedException()

        self.busy.append(d)

        for ship in self.ships:
            if ship.shooten(d):
                ship.lives -= 1
                
                # Рисует крестик на клетке подбитого корабля
                self.field[d.x][d.y] = f'{CR1}╳{CED}'
                if ship.lives == 0:
                    self.count += 1
                    self.contour(ship, verb=True)
                    print(f'{CR3}Корабль уничтожен!{CED}')
                    return False
                else:
                    print(f'{CR3}Корабль ранен!{CED}')
                    return True

        self.field[d.x][d.y] = f'{CR3}×{CED}'
        print(f'{CR3}Мимо!{CED}')
        return False

    def begin(self):
        self.busy = []

    def defeat(self):
        return self.count == len(self.ships)


# Игрок
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


# Игрок "Компьютер"
class AI(Player):
    def ask(self):
        r = randint(0, len(ai_move_coords) - 1)
        m = ai_move_coords.pop(r)
        d = Dot(m[0], m[1])
        coord1 = LET[d.x].upper()
        print(f'Ход компьютера:{CR2} {coord1} {d.y + 1}{CED}')
        return d


# Игрок "Пользователь"
class User(Player):
    def ask(self):
        while True:
            cords = input('Ваш ход: ').split()

            if len(cords) != 2:
                print(f'{CR1}Введите через пробел 2 координаты!{CED}')
                continue

            x, y = cords

            if not x.isalpha() or x.lower() not in LET:
                print(f'{CR1}Первым значением координат должна быть '
                      f'буква из "{CR3}{LET.upper()}{CR1}"{CED}')
                continue

            for i, v in enumerate(LET):
                if x.lower() == v:
                    x = i + 1
                    break

            if not y.isdigit():
                print(f'{CR1}Вторым значением координат '
                      f'должно быть число от {CR3}1-10{CED}')
                continue

            x, y = int(x), int(y)

            return Dot(x - 1, y - 1)


# Игра
class Game:
    def __init__(self, size=10):
        self.lens = [4, 3, 3, 2, 2, 2, 1, 1, 1, 1]
        self.size = size
        pl = self.random_board()
        co = self.random_board()
        co.hid = True
        self.ai = AI(co, pl)
        self.us = User(pl, co)

    def try_board(self):
        board = Board(size=self.size)
        attempts = 0
        for l in self.lens:
            while True:
                attempts += 1
                if attempts > 2000:
                    return None
                ship = Ship(Dot(randint(0, self.size), randint(0, self.size)),
                            l, randint(0, 1))
                try:
                    board.add_ship(ship)
                    break
                except BoardWrongShipException:
                    pass

        board.begin()
        return board

    # Генерация доски
    def random_board(self):
        board = None
        while board is None:
            board = self.try_board()
        return board

    # Приветствие игры
    def greet(self):
        print(f'\n  {CR3}Приветсвуем вас в игре "{CR2}Морской Бой{CR3}"{CED}  ')
        print()
        print(f'  формат хода: {CR2}x y{CED} ')
        print(f'  {CR2}x{CED} - буква строки  ')
        print(f'  {CR2}y{CED} - номер столбца ')

    def print_boards(self):
        print(f'{CR0}-{CED}' * 50)
        print('Поле пользователя:')
        print(self.us.board)
        print()
        print('Поле компьютера:')
        print(self.ai.board)
        print(f'{CR0}-{CED}' * 50)

    # Игровой цикл
    def loop(self):
        num = 0
        while True:
            self.print_boards()
            if num % 2 == 0:
                print(f'{CR3}Ходит пользователь!{CED}')
                repeat = self.us.move()
            else:
                print(f'{CR3}Ходит компьютер!{CED}')
                repeat = self.ai.move()
            if repeat:
                num -= 1

            if self.ai.board.defeat():
                self.print_boards()
                print(f'{CR2}УРА! Пользователь выиграл!{CED}')
                break

            if self.us.board.defeat():
                self.print_boards()
                print(f'{CR2}... В этот раз победил компьютер!{CED}')
                break
            num += 1

    # Старт
    def start(self):
        self.greet()
        self.loop()


g = Game()
g.start()
