from board import Board

board = Board()
board.print_board()

bishop = board.find_piece("B", 1, "BLACK")
bishop.move("Forward_Right", 2)

board.print_board()