"""
This Class is responsible for storing all the information about the current state of the chess game.
Also responsible for determining all the valid moves at the current state. It will also keep a move log
"""

class GameState():
    def __init__(self):
        self.board = [
            ["bR","bN","bB","bQ","bK","bB","bN","bR"],
            ["bp","bp","bp","bp","bp","bp","bp","bp"],
            ["--","--","--","--","--","--","--","--"],
            ["--","--","--","--","--","--","--","--"],
            ["--","--","--","--","--","--","--","--"],
            ["--","--","--","--","--","--","--","--"],
            ["wp","wp","wp","wp","wp","wp","wp","wp"],
            ["wR","wN","wB","wQ","wK","wB","wN","wR"],
        ]
        self.moveFunction = {'p':self.getPawnMoves, 'R':self.getRookMoves, 'K':self.getKingMoves,
                             'Q':self.getQueenMoves, 'B':self.getBishopMoves, 'N':self.getKnightMoves}
        self.whiteToMove = True
        self.moveLog = []
        self.whiteKingLocation = (7, 4)
        self.blackKingLocation = (0, 4)
        self.checkMate = False
        self.stalemate = False
        self.pins = []
        self.checks = []
        self.enpassantPossible = ()  # coordinates for the square where an en-passant capture is possible

    def makeMove(self, move):
        self.board[move.start_row][move.start_col] = "--"
        self.board[move.end_row][move.end_col] = move.piece_moved
        self.moveLog.append(move)
        self.whiteToMove = not self.whiteToMove

        if move.piece_moved == 'wK':
            self.whiteKingLocation = (move.end_row, move.end_col)
        elif move.piece_moved == 'bK':
            self.blackKingLocation = (move.end_row, move.end_col)

        # Pawn Promotion move
        if move.isPawnPromotion:
            self.board[move.end_row][move.end_col] = move.piece_moved[0] + 'Q'

        # En passant move - CORRECTED
        if move.isEnPassantMove:
            # Remove the captured pawn (which is on the same row as the starting position)
            if move.piece_moved[0] == 'w':  # white pawn captured black
                self.board[move.start_row][move.end_col] = '--'
            else:  # black pawn captured white
                self.board[move.start_row][move.end_col] = '--'

        # Update enpassantPossible variable
        if move.piece_moved[1] == 'p' and abs(move.start_row - move.end_row) == 2:  # only on 2 square pawn advances
            self.enpassantPossible = ((move.start_row + move.end_row) // 2, move.start_col)
        else:
            self.enpassantPossible = ()

    def undoMove(self):
        if len(self.moveLog) != 0:
            move = self.moveLog.pop()
            self.board[move.start_row][move.start_col] = move.piece_moved
            self.board[move.end_row][move.end_col] = move.piece_captured
            self.whiteToMove = not self.whiteToMove  # switch turn

            if move.piece_moved == 'wK':
                self.whiteKingLocation = (move.start_row, move.start_col)
            elif move.piece_moved == 'bK':
                self.blackKingLocation = (move.start_row, move.start_col)

            # Undo en passant
            if move.isEnPassantMove:
                self.board[move.end_row][move.end_col] = '--'  # Remove the pawn that moved
                # Restore the captured pawn
                if move.piece_moved[0] == 'w':  # white captured black
                    self.board[move.end_row + 1][move.end_col] = 'bp'
                else:  # black captured white
                    self.board[move.end_row - 1][move.end_col] = 'wp'

            # Undo a 2-square pawn advance
            if move.piece_moved[1] == 'p' and abs(move.start_row - move.end_row) == 2:
                self.enpassantPossible = ()

    def getValidMoves(self):
        tempEnPassantMove = self.enpassantPossible
        moves = self.getAllPossibleMoves()

        # Filter out moves that put/leave the king in check
        for i in range(len(moves) - 1, -1, -1):
            self.makeMove(moves[i])
            self.whiteToMove = not self.whiteToMove
            if self.inCheck():
                moves.remove(moves[i])
            self.whiteToMove = not self.whiteToMove
            self.undoMove()

        if len(moves) == 0:
            if self.inCheck():
                self.checkMate = True
            else:
                self.stalemate = True
        else:
            self.checkMate = False
            self.stalemate = False

        self.enpassantPossible = tempEnPassantMove
        return moves

    def inCheck(self):
        if self.whiteToMove:
            return self.squareUnderAttack(self.whiteKingLocation[0], self.whiteKingLocation[1])
        else:
            return self.squareUnderAttack(self.blackKingLocation[0], self.blackKingLocation[1])

    def squareUnderAttack(self, r, c):
        self.whiteToMove = not self.whiteToMove
        oppMoves = self.getAllPossibleMoves()
        self.whiteToMove = not self.whiteToMove
        for move in oppMoves:
            if move.end_row == r and move.end_col == c:  # Square is under attack
                return True
        return False

    def getAllPossibleMoves(self):
        moves = []
        for r in range(len(self.board)):
            for c in range(len(self.board[r])):
                turn = self.board[r][c][0]
                if (turn == 'w' and self.whiteToMove) or (turn == 'b' and not self.whiteToMove):
                    piece = self.board[r][c][1]
                    self.moveFunction[piece](r, c, moves)
        return moves

    def getPawnMoves(self, r, c, moves):
        if self.whiteToMove:  # White pawn moves
            if self.board[r-1][c] == "--":  # 1 square move
                moves.append(Move((r, c), (r-1, c), self.board))
                if r == 6 and self.board[r-2][c] == "--":  # 2 square move from starting position
                    moves.append(Move((r, c), (r-2, c), self.board))

            # Captures
            if c-1 >= 0:  # Capture to left
                if self.board[r-1][c-1][0] == 'b':  # Black piece to capture
                    moves.append(Move((r, c), (r-1, c-1), self.board))
                elif (r-1, c-1) == self.enpassantPossible:  # En passant capture
                    moves.append(Move((r, c), (r-1, c-1), self.board, isEnPassantMove=True))

            if c+1 <= 7:  # Capture to right
                if self.board[r-1][c+1][0] == 'b':  # Black piece to capture
                    moves.append(Move((r, c), (r-1, c+1), self.board))
                elif (r-1, c+1) == self.enpassantPossible:  # En passant capture
                    moves.append(Move((r, c), (r-1, c+1), self.board, isEnPassantMove=True))

        else:  # Black pawn moves
            if self.board[r+1][c] == "--":  # 1 square move
                moves.append(Move((r, c), (r+1, c), self.board))
                if r == 1 and self.board[r+2][c] == "--":  # 2 square move from starting position
                    moves.append(Move((r, c), (r+2, c), self.board))

            # Captures
            if c-1 >= 0:  # Capture to left
                if self.board[r+1][c-1][0] == 'w':  # White piece to capture
                    moves.append(Move((r, c), (r+1, c-1), self.board))
                elif (r+1, c-1) == self.enpassantPossible:  # En passant capture
                    moves.append(Move((r, c), (r+1, c-1), self.board, isEnPassantMove=True))

            if c+1 <= 7:  # Capture to right
                if self.board[r+1][c+1][0] == 'w':  # White piece to capture
                    moves.append(Move((r, c), (r+1, c+1), self.board))
                elif (r+1, c+1) == self.enpassantPossible:  # En passant capture
                    moves.append(Move((r, c), (r+1, c+1), self.board, isEnPassantMove=True))

    def getRookMoves(self, r, c, moves):
        directions = ((-1, 0), (0, -1), (1, 0), (0, 1))
        enemy_color = 'b' if self.whiteToMove else 'w'
        for d in directions:
            for i in range(1, 8):
                end_row = r + d[0] * i
                end_col = c + d[1] * i
                if 0 <= end_row < 8 and 0 <= end_col < 8:
                    end_piece = self.board[end_row][end_col]
                    if end_piece == "--":
                        moves.append(Move((r, c), (end_row, end_col), self.board))
                    elif end_piece[0] == enemy_color:
                        moves.append(Move((r, c), (end_row, end_col), self.board))
                        break
                    else:
                        break
                else:
                    break

    def getBishopMoves(self, r, c, moves):
        directions = ((-1, -1), (-1, 1), (1, -1), (1, 1))
        enemy_color = 'b' if self.whiteToMove else 'w'
        for d in directions:
            for i in range(1, 8):
                end_row = r + d[0] * i
                end_col = c + d[1] * i
                if 0 <= end_row < 8 and 0 <= end_col < 8:
                    end_piece = self.board[end_row][end_col]
                    if end_piece == "--":
                        moves.append(Move((r, c), (end_row, end_col), self.board))
                    elif end_piece[0] == enemy_color:
                        moves.append(Move((r, c), (end_row, end_col), self.board))
                        break
                    else:
                        break
                else:
                    break

    def getKnightMoves(self, r, c, moves):
        knight_moves = ((-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1))
        ally_color = 'w' if self.whiteToMove else 'b'
        for m in knight_moves:
            end_row = r + m[0]
            end_col = c + m[1]
            if 0 <= end_row < 8 and 0 <= end_col < 8:
                end_piece = self.board[end_row][end_col]
                if end_piece[0] != ally_color:
                    moves.append(Move((r, c), (end_row, end_col), self.board))

    def getQueenMoves(self, r, c, moves):
        self.getRookMoves(r, c, moves)
        self.getBishopMoves(r, c, moves)

    def getKingMoves(self, r, c, moves):
        king_moves = ((-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1))
        ally_color = 'w' if self.whiteToMove else 'b'
        for i in range(8):
            end_row = r + king_moves[i][0]
            end_col = c + king_moves[i][1]
            if 0 <= end_row < 8 and 0 <= end_col < 8:
                end_piece = self.board[end_row][end_col]
                if end_piece[0] != ally_color:
                    moves.append(Move((r, c), (end_row, end_col), self.board))


class Move:
    ranks_to_rows = {"1": 7, "2": 6, "3": 5, "4": 4,
                     "5": 3, "6": 2, "7": 1, "8": 0}
    rows_to_ranks = {v: k for k, v in ranks_to_rows.items()}
    files_to_cols = {"a": 0, "b": 1, "c": 2, "d": 3,
                     "e": 4, "f": 5, "g": 6, "h": 7}
    cols_to_files = {v: k for k, v in files_to_cols.items()}

    def __init__(self, start_sq, end_sq, board, isEnPassantMove=False):
        self.start_row = start_sq[0]
        self.start_col = start_sq[1]
        self.end_row = end_sq[0]
        self.end_col = end_sq[1]
        self.piece_moved = board[self.start_row][self.start_col]
        self.piece_captured = board[self.end_row][self.end_col]
        self.isPawnPromotion = False

        # Pawn promotion
        if (self.piece_moved == 'wp' and self.end_row == 0) or (self.piece_moved == 'bp' and self.end_row == 7):
            self.isPawnPromotion = True

        # En passant
        self.isEnPassantMove = isEnPassantMove
        if self.isEnPassantMove:
            if self.piece_moved[0] == 'w':  # White capturing black
                self.piece_captured = 'bp'
            else:  # Black capturing white
                self.piece_captured = 'wp'

        self.move_id = self.start_row * 1000 + self.start_col * 100 + self.end_row * 10 + self.end_col

    def __eq__(self, other):
        if isinstance(other, Move):
            return self.move_id == other.move_id
        return False

    def get_chess_notation(self):
        return self.get_rank_file(self.start_row, self.start_col) + self.get_rank_file(self.end_row, self.end_col)

    def get_rank_file(self, r, c):
        return self.cols_to_files[c] + self.rows_to_ranks[r]
