from random import randint


class Exeptions(Exception):
    pass


class BoardOutException(Exeptions):
    def __str__(self):
        return 'Вы пытаетесь выстрелить за доску'


class BoardUsedException(Exeptions):
    def __str__(self):
        return "Эти координаты выстрела уже были проверены"


class BoardWrongShipException(Exeptions):
    pass


class Dot:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __repr__(self):
        return f"Dot{self.x, self.y}"


class Ship:
    def __init__(self, ship_start, ship_lent, ship_direct):
        self.ship_start = ship_start
        self.ship_lent = ship_lent
        self.ship_direct = ship_direct
        self.lives = ship_lent

    @property
    def dots(self):
        ship_dots = []
        ship_coord_x = self.ship_start.x
        ship_coord_y = self.ship_start.y

        for i in range(self.ship_lent):
            ship_dots.append(Dot(ship_coord_x, ship_coord_y))

            if self.ship_direct == 0:
                ship_coord_x += 1

            elif self.ship_direct == 1:
                ship_coord_y += 1

        return ship_dots

    def shooten(self, shot):
        return shot in self.dots


class Board:
    def __init__(self, hid=False):
        self.hid = hid
        self.count = 0
        self.play_board = [['~ '] * 7 for _ in range(7)]
        self.board_ships = []
        self.live_ships = []
        self.busy = []
        self.busy_hid = []

    def __repr__(self):
        for dot in self.busy_hid:
            if not (self.out(dot)) and self.play_board[dot.x][dot.y] == '[]' and self.hid:
                self.play_board[dot.x][dot.y] = '~ '

        first_cord = [str(m) + '|' for m in range(1, 7)]
        second_cord = ' | 1| 2| 3| 4| 5| 6|'
        full_field = zip(first_cord, self.play_board[1:7])
        print(second_cord)
        for j, i in full_field:
            print(f"{j} {' '.join(i[1:7])}")
        return ''

    def add_ship(self, ship):
        for dot in ship.dots:
            if self.out(dot) or dot in self.busy:
                raise BoardWrongShipException
        for dot in ship.dots:
            self.play_board[dot.x][dot.y] = '[]'
            self.busy.append(dot)

        self.board_ships.append(ship)
        self.contour(ship)

    def contour(self, ship, verb = False):
        near = [
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1), (0, 0), (0, 1),
            (1, -1), (1, 0), (1, 1)
        ]

        for dot in ship.dots:
            for dot_x, dot_y in near:
                s_dot = Dot(dot.x + dot_x, dot.y + dot_y)
                if not (self.out(s_dot)) and s_dot not in self.busy:
                    if verb:
                        self.play_board[s_dot.x][s_dot.y] = "* "
                self.busy.append(s_dot)
                self.busy_hid.append(s_dot)

    def out(self, dot):
        return not ((0 < dot.x <= 6) and (0 < dot.y <= 6))

    def shot(self, dot):
        if self.out(dot):
            raise BoardOutException()

        if dot in self.busy:
            raise BoardUsedException()

        self.busy.append(dot)

        for ship in self.board_ships:
            if dot in ship.dots:
                ship.lives -= 1
                self.play_board[dot.x][dot.y] = "X "
                if ship.lives == 0:
                    self.count += 1
                    self.contour(ship, verb=True)
                    if not self.hid:
                        print(f"Ход компьютера: {dot.x} {dot.y}")
                    if self.count == 7:
                        print("Флот уничтожен!")
                    else:
                        print("Корабль уничтожен!")
                        print(f"Осталось {7 - self.count} кораблей")
                    return False
                else:
                    if not self.hid:
                        print(f"Ход компьютера: {dot.x} {dot.y}")
                    print("Корабль ранен!")
                    return True

        self.play_board[dot.x][dot.y] = "* "
        if not self.hid:
            print(f"Ход компьютера: {dot.x} {dot.y}")
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

    def move(self, ex):
        while True:
            try:
                target = self.ask()
                repeat = self.enemy.shot(target)
                return repeat
            except Exeptions as e:
                if ex:
                    print(e)
                else:
                    continue


class AI(Player):
    def ask(self):
        dot = Dot(randint(1, 6), randint(1, 6))
        return dot


class User(Player):
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

            return Dot(x, y)


class Game:
    def __init__(self, size=7):
        self.size = size
        pl = self.random_board()
        co = self.random_board()
        co.hid = True

        self.ai = AI(co, pl)
        self.us = User(pl, co)

    def random_board(self):
        board = None
        while board is None:
            board = self.random_place()
        return board

    def random_place(self):
        lens = [3, 2, 2, 1, 1, 1, 1]
        board = Board()
        attempts = 0
        for n in lens:
            while True:
                attempts += 1
                if attempts > 2000:
                    return None
                ship = Ship(Dot(randint(1, 6), randint(1, 6)), n, randint(0, 1))
                try:
                    board.add_ship(ship)
                    break
                except BoardWrongShipException:
                    pass
        board.begin()
        return board

    def greet(self):
        print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"
              '\n'
              "Добро пожаловать в игру Морской бой!"
              '\n'
              "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"
              '\n'
              "В Вашем флоте 4 катера, 2 эсминца и 1 линкор, столько же у Вашего противника!"
              '\n'
              "Чтобы победить врага, утопите все его корабли раньше, чем он утопит Ваши."
              '\n'
              "Чтобы выстрелить во вражеский флот, введите координаты выстрела в формате: x y")
        print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
        print("Удачи!")
        s = input("Если хотите начать игру, введите S: ")
        if s == "S":
            self.loop()
        else:
            print("До новых встреч!")

    def loop(self):
        num = 0
        while True:
            print("~" * 20)
            print("Доска пользователя:")
            print(self.us.board)
            print("~" * 20)
            print("Доска компьютера:")
            print(self.ai.board)
            if num % 2 == 0:
                print("~" * 20)
                print("Ходит пользователь!")
                repeat = self.us.move(ex=True)
            else:
                print("~" * 20)
                print("Ходит компьютер!")
                repeat = self.ai.move(ex=False)
            if repeat:
                num -= 1

            if self.ai.board.count == 7:
                print("~" * 20)
                print("Враг повержен! Победа за Вами!")
                break

            if self.us.board.count == 7:
                print("~" * 20)
                print("В этой битве соперник оказался сильнее")
                break
            num += 1

    def start(self):
        self.greet()


g = Game()
g.start()
