import json
from pieces import Pawn, Rook, Knight, Bishop, King, Queen


class Board(dict):
    """
    Text-based Chess Board (8x8).

    - squares: dict like {"a1": None, "a2": Pawn(...), ...}
    - setup_board(): places pieces in starting positions
    - print_board(): prints 8 rows
    - find_piece(): returns the piece object matching (symbol, identifier, color)
    - get_piece(), is_square_empty(), kill_piece()
    - save_board(): appends board state to board.txt
    - get_board_movements(): generator yielding saved states
    """

    def __init__(self):
        # squares: a1..h8
        self.squares = {
            f"{chr(col)}{row}": None
            for col in range(ord("a"), ord("i"))
            for row in range(1, 9)
        }

        self.setup_board()

        # attach board + initial positions to pieces
        for square, piece in self.squares.items():
            if piece is not None:
                piece.set_initial_position(square)
                piece.define_board(self)

        # optional: makes Board serializable-ish as dict({"squares": ...})
        dict.__init__(self, squares=self.squares)

    def setup_board(self):
        """Fill the board with the pieces in their starting positions."""
        # BLACK back rank (row 1)
        self.squares["a1"] = Rook("BLACK", 1)
        self.squares["b1"] = Knight("BLACK", 1)
        self.squares["c1"] = Bishop("BLACK", 1)
        self.squares["d1"] = Queen("BLACK", 1)
        self.squares["e1"] = King("BLACK", 1)
        self.squares["f1"] = Bishop("BLACK", 2)
        self.squares["g1"] = Knight("BLACK", 2)
        self.squares["h1"] = Rook("BLACK", 2)

        # BLACK pawns (row 2) — dict comprehension
        black_pawns = {
            f"{chr(col)}2": Pawn("BLACK", i + 1)
            for i, col in enumerate(range(ord("a"), ord("i")))
        }
        self.squares.update(black_pawns)

        # WHITE pawns (row 7) — dict comprehension
        white_pawns = {
            f"{chr(col)}7": Pawn("WHITE", i + 1)
            for i, col in enumerate(range(ord("a"), ord("i")))
        }
        self.squares.update(white_pawns)

        # WHITE back rank (row 8)
        self.squares["a8"] = Rook("WHITE", 1)
        self.squares["b8"] = Knight("WHITE", 1)
        self.squares["c8"] = Bishop("WHITE", 1)
        self.squares["d8"] = Queen("WHITE", 1)
        self.squares["e8"] = King("WHITE", 1)
        self.squares["f8"] = Bishop("WHITE", 2)
        self.squares["g8"] = Knight("WHITE", 2)
        self.squares["h8"] = Rook("WHITE", 2)

    def print_board(self):
        """Print the board row-by-row (1..8)."""
        rows = [
            [self.squares[f"{chr(col)}{row}"] for col in range(ord("a"), ord("i"))]
            for row in range(1, 9)
        ]
        for row in rows:
            print(row)

    @staticmethod
    def print_saved_board(board_state: dict):
        """Print a loaded board_state dict (from board.txt) in the same row format."""
        rows = [
            [board_state.get(f"{chr(col)}{row}") for col in range(ord("a"), ord("i"))]
            for row in range(1, 9)
        ]
        for row in rows:
            print(row)

    def find_piece(self, symbol: str, identifier: int, color: str):
        """Return the piece object matching (symbol, identifier, color)."""
        matches = [
            piece
            for piece in self.squares.values()
            if piece is not None
            and piece.symbol == symbol
            and piece.identifier == identifier
            and piece.color == color
        ]
        return matches[0]  # assumes it exists

    def get_piece(self, square: str):
        """Returns the piece that is on a specific square."""
        return self.squares[square]

    def is_square_empty(self, square: str):
        """Returns True if the square is empty, False otherwise."""
        return self.get_piece(square) is None

    def kill_piece(self, square: str):
        """Kills a piece by calling die()."""
        piece = self.get_piece(square)
        if piece is None:
            print("No piece on that square.")
            return
        piece.die()
        print(f"{piece} was killed.")

    def save_board(self, saved_file: str = "board.txt"):
        """
        Saves the board to a file (append mode).
        NOTE: pieces.py inherits dict, so json can serialize them.
        """
        with open(saved_file, "a", encoding="utf-8") as file:
            file.write(json.dumps(self.squares))
            file.write("\n")
        # optional print:
        # print(f"Saved board to txt file: {saved_file}.")
        return saved_file

    @staticmethod
    def get_board_movements(saved_file: str = "board.txt"):
        """Generator: yields one saved board state (dict) per line."""
        with open(saved_file, "r", encoding="utf-8") as file:
            for line in file:
                line = line.strip()
                if not line:
                    continue
                yield json.loads(line)