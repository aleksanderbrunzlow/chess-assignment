from __future__ import annotations

from abc import ABC, abstractmethod
import functools


class BoardMovements:
    @staticmethod
    def forward(position: str, color: str, squares: int = 1) -> str:
        col, row = position[0], int(position[1])
        new_row = row + squares if color == "BLACK" else row - squares
        if new_row in (0, 9):
            print("This piece has reached the boundary of the board.")
            return position
        return f"{col}{new_row}"

    @staticmethod
    def backward(position: str, color: str, squares: int = 1) -> str:
        col, row = position[0], int(position[1])
        new_row = row - squares if color == "BLACK" else row + squares
        if new_row in (0, 9):
            print("This piece has reached the boundary of the board.")
            return position
        return f"{col}{new_row}"

    @staticmethod
    def left(position: str, color: str, squares: int = 1) -> str:
        col, row = position[0], int(position[1])
        new_col_ord = ord(col) - squares if color == "BLACK" else ord(col) + squares
        new_col = chr(new_col_ord)
        if new_col < "a" or new_col > "h":
            print("This piece has reached the boundary of the board.")
            return position
        return f"{new_col}{row}"

    @staticmethod
    def right(position: str, color: str, squares: int = 1) -> str:
        col, row = position[0], int(position[1])
        new_col_ord = ord(col) + squares if color == "BLACK" else ord(col) - squares
        new_col = chr(new_col_ord)
        if new_col < "a" or new_col > "h":
            print("This piece has reached the boundary of the board.")
            return position
        return f"{new_col}{row}"

    # Diagonals (IMPORTANT: do NOT chain forward+right with squares again)
    @staticmethod
    def diagonally_forward_right(position: str, color: str, squares: int = 1) -> str:
        col, row = position[0], int(position[1])
        new_row = row + squares if color == "BLACK" else row - squares
        new_col_ord = ord(col) + squares if color == "BLACK" else ord(col) - squares
        new_col = chr(new_col_ord)
        if new_row in (0, 9) or new_col < "a" or new_col > "h":
            print("This piece has reached the boundary of the board.")
            return position
        return f"{new_col}{new_row}"

    @staticmethod
    def diagonally_forward_left(position: str, color: str, squares: int = 1) -> str:
        col, row = position[0], int(position[1])
        new_row = row + squares if color == "BLACK" else row - squares
        new_col_ord = ord(col) - squares if color == "BLACK" else ord(col) + squares
        new_col = chr(new_col_ord)
        if new_row in (0, 9) or new_col < "a" or new_col > "h":
            print("This piece has reached the boundary of the board.")
            return position
        return f"{new_col}{new_row}"

    @staticmethod
    def diagonally_backward_left(position: str, color: str, squares: int = 1) -> str:
        col, row = position[0], int(position[1])
        new_row = row - squares if color == "BLACK" else row + squares
        new_col_ord = ord(col) - squares if color == "BLACK" else ord(col) + squares
        new_col = chr(new_col_ord)
        if new_row in (0, 9) or new_col < "a" or new_col > "h":
            print("This piece has reached the boundary of the board.")
            return position
        return f"{new_col}{new_row}"

    @staticmethod
    def diagonally_backward_right(position: str, color: str, squares: int = 1) -> str:
        col, row = position[0], int(position[1])
        new_row = row - squares if color == "BLACK" else row + squares
        new_col_ord = ord(col) + squares if color == "BLACK" else ord(col) - squares
        new_col = chr(new_col_ord)
        if new_row in (0, 9) or new_col < "a" or new_col > "h":
            print("This piece has reached the boundary of the board.")
            return position
        return f"{new_col}{new_row}"


# decorators (module-level)
def print_movement(func):
    @functools.wraps(func)
    def wrapper(self, *args, **kwargs):
        print(f"Piece is currently at position {self.position}")
        result = func(self, *args, **kwargs)
        print(f"Piece is now at position {self.position}")
        return result

    return wrapper


def save_board(func):
    @functools.wraps(func)
    def wrapper(self, *args, **kwargs):
        result = func(self, *args, **kwargs)
        if getattr(self, "board", None) is not None:
            self.board.save_board()
        return result

    return wrapper


class BaseChessPiece(ABC, dict):
    def __init__(self, color: str, name: str, symbol: str, identifier: int):
        self.color = color
        self.symbol = symbol
        self.name = name
        self.identifier = identifier
        self.is_alive = True
        self.position = "None"
        self.board = None

        # for json serialization via dict
        dict.__init__(
            self,
            color=self.color,
            symbol=self.symbol,
            identifier=self.identifier,
            is_alive=self.is_alive,
            name=self.name,
            position=self.position,
        )

    def __str__(self):
        return f"{self.color} {self.name} {self.identifier}"

    __repr__ = __str__

    def set_initial_position(self, position: str):
        self.position = position
        self["position"] = self.position

    def define_board(self, board):
        self.board = board

    def reposition(self, new_square: str):
        # remove from old square
        self.board.squares[self.position] = None
        # update self
        self.position = new_square
        self["position"] = self.position
        # place on new square
        self.board.squares[self.position] = self

    def die(self):
        # remove from board
        if self.board is not None and self.position not in (None, "None"):
            self.board.squares[self.position] = None
        self.position = None
        self.is_alive = False
        self["is_alive"] = self.is_alive
        self["position"] = self.position
        print(f"{self} got killed.")

    @save_board
    @print_movement
    def move_to(self, new_square: str) -> bool:
        """Common movement onto the board. Children compute new_square and call this."""
        other_piece = self.board.get_piece(new_square)

        if other_piece is not None and other_piece.color == self.color:
            print("There is already a piece here, and it's the same colour as yours, so you can't move there.")
            return False

        if other_piece is not None and other_piece.color != self.color:
            print("There is already a piece here, we will kill it.")
            other_piece.die()

        self.reposition(new_square)
        return True

    @abstractmethod
    def move(self, *args, **kwargs):
        """Child pieces implement this and call self.move_to(new_square)."""
        raise NotImplementedError


class Pawn(BaseChessPiece):
    def __init__(self, color: str, identifier: int):
        super().__init__(color, "Pawn", "-", identifier)

    def move(self):
        new_square = BoardMovements.forward(self.position, self.color, 1)
        self.move_to(new_square)


class Rook(BaseChessPiece):
    def __init__(self, color: str, identifier: int):
        super().__init__(color, "Rook", "R", identifier)

    def move(self, direction: str, squares: int):
        if direction == "Left":
            new_square = BoardMovements.left(self.position, self.color, squares)
        elif direction == "Right":
            new_square = BoardMovements.right(self.position, self.color, squares)
        elif direction == "Forward":
            new_square = BoardMovements.forward(self.position, self.color, squares)
        elif direction == "Backward":
            new_square = BoardMovements.backward(self.position, self.color, squares)
        else:
            print("Invalid direction.")
            return
        self.move_to(new_square)


class Knight(BaseChessPiece):
    def __init__(self, color: str, identifier: int):
        super().__init__(color, "Knight", "N", identifier)

    def move(self, direction: str):
        if direction == "Left_Forward":
            new_square = BoardMovements.forward(BoardMovements.left(self.position, self.color, 2), self.color, 1)
        elif direction == "Right_Forward":
            new_square = BoardMovements.forward(BoardMovements.right(self.position, self.color, 2), self.color, 1)
        elif direction == "Left_Backward":
            new_square = BoardMovements.backward(BoardMovements.left(self.position, self.color, 2), self.color, 1)
        elif direction == "Right_Backward":
            new_square = BoardMovements.backward(BoardMovements.right(self.position, self.color, 2), self.color, 1)
        elif direction == "Backward_Right":
            new_square = BoardMovements.backward(BoardMovements.right(self.position, self.color, 1), self.color, 2)
        elif direction == "Backward_Left":
            new_square = BoardMovements.backward(BoardMovements.left(self.position, self.color, 1), self.color, 2)
        elif direction == "Forward_Right":
            new_square = BoardMovements.forward(BoardMovements.right(self.position, self.color, 1), self.color, 2)
        elif direction == "Forward_Left":
            new_square = BoardMovements.forward(BoardMovements.left(self.position, self.color, 1), self.color, 2)
        else:
            print("Invalid direction.")
            return
        self.move_to(new_square)


class Bishop(BaseChessPiece):
    def __init__(self, color: str, identifier: int):
        super().__init__(color, "Bishop", "B", identifier)

    def move(self, direction: str, squares: int):
        if direction == "Backward_Right":
            new_square = BoardMovements.diagonally_backward_right(self.position, self.color, squares)
        elif direction == "Backward_Left":
            new_square = BoardMovements.diagonally_backward_left(self.position, self.color, squares)
        elif direction == "Forward_Right":
            new_square = BoardMovements.diagonally_forward_right(self.position, self.color, squares)
        elif direction == "Forward_Left":
            new_square = BoardMovements.diagonally_forward_left(self.position, self.color, squares)
        else:
            print("Invalid direction.")
            return
        self.move_to(new_square)


class Queen(BaseChessPiece):
    def __init__(self, color: str, identifier: int):
        super().__init__(color, "Queen", "Q", identifier)

    def move(self, direction: str, squares: int):
        if direction == "Left":
            new_square = BoardMovements.left(self.position, self.color, squares)
        elif direction == "Right":
            new_square = BoardMovements.right(self.position, self.color, squares)
        elif direction == "Forward":
            new_square = BoardMovements.forward(self.position, self.color, squares)
        elif direction == "Backward":
            new_square = BoardMovements.backward(self.position, self.color, squares)
        elif direction == "Backward_Right":
            new_square = BoardMovements.diagonally_backward_right(self.position, self.color, squares)
        elif direction == "Backward_Left":
            new_square = BoardMovements.diagonally_backward_left(self.position, self.color, squares)
        elif direction == "Forward_Right":
            new_square = BoardMovements.diagonally_forward_right(self.position, self.color, squares)
        elif direction == "Forward_Left":
            new_square = BoardMovements.diagonally_forward_left(self.position, self.color, squares)
        else:
            print("Invalid direction.")
            return
        self.move_to(new_square)


class King(BaseChessPiece):
    def __init__(self, color: str, identifier: int):
        super().__init__(color, "King", "K", identifier)

    def move(self, direction: str):
        if direction == "Left":
            new_square = BoardMovements.left(self.position, self.color, 1)
        elif direction == "Right":
            new_square = BoardMovements.right(self.position, self.color, 1)
        elif direction == "Forward":
            new_square = BoardMovements.forward(self.position, self.color, 1)
        elif direction == "Backward":
            new_square = BoardMovements.backward(self.position, self.color, 1)
        elif direction == "Backward_Right":
            new_square = BoardMovements.diagonally_backward_right(self.position, self.color, 1)
        elif direction == "Backward_Left":
            new_square = BoardMovements.diagonally_backward_left(self.position, self.color, 1)
        elif direction == "Forward_Right":
            new_square = BoardMovements.diagonally_forward_right(self.position, self.color, 1)
        elif direction == "Forward_Left":
            new_square = BoardMovements.diagonally_forward_left(self.position, self.color, 1)
        else:
            print("Invalid direction.")
            return
        self.move_to(new_square)