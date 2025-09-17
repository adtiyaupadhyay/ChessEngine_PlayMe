"""
This Class is responsible for storing all the information about the current state of the chess game.
Also responsible for determining all the valid moves at the current state. It will also keep a move log
"""
import copy

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
        self.currentCastlingRights = CastlingRights(True, True, True, True)
        self.castlingRightsLogs = [CastlingRights(self.currentCastlingRights.wks, self.currentCastlingRights.bks,
                                                 self.currentCastlingRights.wqs, self.currentCastlingRights.bqs)]

    def makeMove(self, move):
        # Move the piece
        self.board[move.end_row][move.end_col] = move.piece_moved
        self.board[move.start_row][move.start_col] = "--"
        self.moveLog.append(move)

        # Update king's location if needed
        if move.piece_moved == "wK":
            self.whiteKingLocation = (move.end_row, move.end_col)
        elif move.piece_moved == "bK":
            self.blackKingLocation = (move.end_row, move.end_col)

        # Handle castling logic
        if move.isCastleMove:
            if move.end_col - move.start_col == 2:  # King-side castling
                self.board[move.end_row][move.end_col - 1] = self.board[move.end_row][move.end_col + 1]
                self.board[move.end_row][move.end_col + 1] = "--"
            else:  # Queen-side castling
                self.board[move.end_row][move.end_col + 1] = self.board[move.end_row][move.end_col - 2]
                self.board[move.end_row][move.end_col - 2] = "--"

        # Handle pawn promotion
        if move.isPawnPromotion:
            promoted_piece = move.piece_moved[0] + 'Q'  # Default to queen promotion
            self.board[move.end_row][move.end_col] = promoted_piece

        # Handle en-passant capture
        if move.isEnPassantMove:
            if self.whiteToMove:  # white capturing black pawn
                self.board[move.end_row + 1][move.end_col] = "--"
            else:  # black capturing white pawn
                self.board[move.end_row - 1][move.end_col] = "--"

        # Update en passant possible
        if move.piece_moved[1] == 'p' and abs(move.start_row - move.end_row) == 2:
            self.enpassantPossible = ((move.start_row + move.end_row) // 2, move.start_col)
        else:
            self.enpassantPossible = ()

        # Update castling rights
        self.updateCastlingRights(move)
        self.castlingRightsLogs.append(copy.deepcopy(self.currentCastlingRights))

        # Switch turn
        self.whiteToMove = not self.whiteToMove

    # -----------------------------
    # Undoing moves
    # -----------------------------
    def undoMove(self):
        if len(self.moveLog) != 0:  # make sure there is a move to undo
            move = self.moveLog.pop()
            self.board[move.start_row][move.start_col] = move.piece_moved
            self.board[move.end_row][move.end_col] = move.piece_captured
            self.whiteToMove = not self.whiteToMove

            # update king's position if needed
            if move.piece_moved == "wK":
                self.whiteKingLocation = (move.start_row, move.start_col)
            elif move.piece_moved == "bK":
                self.blackKingLocation = (move.start_row, move.start_col)

            # Handle en passant undo
            if move.isEnPassantMove:
                self.board[move.end_row][move.end_col] = "--"  # Remove the pawn that was captured
                if move.piece_moved[0] == 'w':  # white was capturing
                    self.board[move.end_row + 1][move.end_col] = 'bp'
                else:  # black was capturing
                    self.board[move.end_row - 1][move.end_col] = 'wp'

            # Restore en passant possibility
            if len(self.moveLog) > 0:
                prev_move = self.moveLog[-1]
                if prev_move.piece_moved[1] == 'p' and abs(prev_move.start_row - prev_move.end_row) == 2:
                    self.enpassantPossible = ((prev_move.start_row + prev_move.end_row) // 2, prev_move.start_col)
                else:
                    self.enpassantPossible = ()
            else:
                self.enpassantPossible = ()

            # undo castling rights
            self.castlingRightsLogs.pop()
            if len(self.castlingRightsLogs) > 0:
                self.currentCastlingRights = self.castlingRightsLogs[-1]
            else:
                self.currentCastlingRights = CastlingRights(True, True, True, True)

            # undo castle move
            if move.isCastleMove:
                if move.end_col - move.start_col == 2:  # kingside
                    # Move rook back to original position
                    self.board[move.end_row][move.end_col + 1] = self.board[move.end_row][move.end_col - 1]
                    self.board[move.end_row][move.end_col - 1] = "--"
                else:  # queenside
                    self.board[move.end_row][move.end_col - 2] = self.board[move.end_row][move.end_col + 1]
                    self.board[move.end_row][move.end_col + 1] = "--"

    # -----------------------------
    # Castling rights update
    # -----------------------------
    def updateCastlingRights(self, move):
        # If king moves, lose both castling rights
        if move.piece_moved == "wK":
            self.currentCastlingRights.wks = False
            self.currentCastlingRights.wqs = False
        elif move.piece_moved == "bK":
            self.currentCastlingRights.bks = False
            self.currentCastlingRights.bqs = False

        # If rook moves, lose that side's castling right
        elif move.piece_moved == "wR":
            if move.start_row == 7 and move.start_col == 0:  # left rook
                self.currentCastlingRights.wqs = False
            elif move.start_row == 7 and move.start_col == 7:  # right rook
                self.currentCastlingRights.wks = False
        elif move.piece_moved == "bR":
            if move.start_row == 0 and move.start_col == 0:  # left rook
                self.currentCastlingRights.bqs = False
            elif move.start_row == 0 and move.start_col == 7:  # right rook
                self.currentCastlingRights.bks = False

        # If a rook is captured, lose that castling right
        if move.piece_captured == "wR":
            if move.end_row == 7 and move.end_col == 0:
                self.currentCastlingRights.wqs = False
            elif move.end_row == 7 and move.end_col == 7:
                self.currentCastlingRights.wks = False
        elif move.piece_captured == "bR":
            if move.end_row == 0 and move.end_col == 0:
                self.currentCastlingRights.bqs = False
            elif move.end_row == 0 and move.end_col == 7:
                self.currentCastlingRights.bks = False

    def getValidMoves(self):
        tempEnPassantMove = self.enpassantPossible
        tempCastlingRights = CastlingRights(self.currentCastlingRights.wks, self.currentCastlingRights.bks,
                                            self.currentCastlingRights.wqs, self.currentCastlingRights.bqs)

        # First, check for pins and checks
        self.pins, self.checks = self.checkForPinsAndChecks()

        if self.whiteToMove:
            king_row, king_col = self.whiteKingLocation
        else:
            king_row, king_col = self.blackKingLocation

        if self.checks:
            if len(self.checks) == 1:  # Only one check - block or capture
                moves = self.getAllPossibleMoves()
                # Direction of the check
                check = self.checks[0]
                check_row, check_col, direction_row, direction_col = check
                piece_checking = self.board[check_row][check_col]

                # Squares that pieces can move to to block the check
                valid_squares = []
                if piece_checking[1] == 'N':  # Knight can't be blocked
                    valid_squares = [(check_row, check_col)]
                else:
                    for i in range(1, 8):
                        valid_square = (king_row + direction_row * i, king_col + direction_col * i)
                        valid_squares.append(valid_square)
                        if valid_square[0] == check_row and valid_square[1] == check_col:
                            break

                # Filter moves that don't block the check or capture the checking piece
                for i in range(len(moves) - 1, -1, -1):
                    if moves[i].piece_moved[1] != 'K':  # King moves are handled separately
                        if not (moves[i].end_row, moves[i].end_col) in valid_squares:
                            moves.remove(moves[i])
            else:  # Double check - king must move
                moves = []  # This line was missing - only king can move in double check
                self.getKingMoves(king_row, king_col, moves)
        else:
            moves = self.getAllPossibleMoves()

        # Filter out moves that put/leave the king in check
        # corrected filtering: remove moves that leave the mover's king in check
        for i in range(len(moves) - 1, -1, -1):
            move = moves[i]
            self.makeMove(move)
            # mover's color is the side that just moved (opposite of self.whiteToMove)
            mover_color = 'w' if not self.whiteToMove else 'b'
            # king location after the move (if king moved, use its new square; otherwise use saved king pos)
            if move.piece_moved[1] == 'K':
                king_r, king_c = move.end_row, move.end_col
            else:
                king_r, king_c = king_row, king_col
            # if mover's king is attacked now, move is illegal
            if self.squareUnderAttack(king_r, king_c, mover_color):
                moves.remove(move)
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
        self.currentCastlingRights = tempCastlingRights
        return moves

    def checkForPinsAndChecks(self):
        pins = []  # Squares where pinned pieces are and direction of pin
        checks = []  # Squares where enemy is applying check
        if self.whiteToMove:
            enemy_color = "b"
            ally_color = "w"
            start_row = self.whiteKingLocation[0]
            start_col = self.whiteKingLocation[1]
        else:
            enemy_color = "w"
            ally_color = "b"
            start_row = self.blackKingLocation[0]
            start_col = self.blackKingLocation[1]

        # Check outward from king for pins and checks
        directions = ((-1, 0), (0, -1), (1, 0), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1))
        for j in range(len(directions)):
            d = directions[j]
            possible_pin = ()  # Reset possible pin
            for i in range(1, 8):
                end_row = start_row + d[0] * i
                end_col = start_col + d[1] * i
                if 0 <= end_row < 8 and 0 <= end_col < 8:
                    end_piece = self.board[end_row][end_col]
                    if end_piece[0] == ally_color and end_piece[1] != 'K':
                        if possible_pin == ():  # First allied piece could be pinned
                            possible_pin = (end_row, end_col, d[0], d[1])
                        else:  # Second allied piece, so no pin or check possible in this direction
                            break
                    elif end_piece[0] == enemy_color:
                        type = end_piece[1]
                        # 5 possibilities here:
                        # 1) Orthogonally away from king and piece is a rook
                        # 2) Diagonally away from king and piece is a bishop
                        # 3) 1 square away diagonally from king and piece is a pawn
                        # 4) Any direction and piece is a queen
                        # 5) Any direction 1 square away and piece is a king (prevent king move to controlled square)
                        if (0 <= j <= 3 and type == 'R') or \
                                (4 <= j <= 7 and type == 'B') or \
                                (i == 1 and type == 'p' and (
                                        (enemy_color == 'w' and 6 <= j <= 7) or (
                                        enemy_color == 'b' and 4 <= j <= 5))) or \
                                (type == 'Q') or (i == 1 and type == 'K'):
                            if possible_pin == ():  # No piece blocking, so check
                                checks.append((end_row, end_col, d[0], d[1]))
                                break
                            else:  # Piece blocking, so pin
                                pins.append(possible_pin)
                                break
                        else:  # Enemy piece not applying check
                            break
                else:  # Off board
                    break

        # Check for knight checks
        knight_moves = ((-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1))
        for m in knight_moves:
            end_row = start_row + m[0]
            end_col = start_col + m[1]
            if 0 <= end_row < 8 and 0 <= end_col < 8:
                end_piece = self.board[end_row][end_col]
                if end_piece[0] == enemy_color and end_piece[1] == 'N':  # Enemy knight attacking king
                    checks.append((end_row, end_col, m[0], m[1]))

        return pins, checks

    def inCheck(self):
        """
        Returns True if the current player to move is in check.
        """
        if self.whiteToMove:
            king_row, king_col = self.whiteKingLocation
        else:
            king_row, king_col = self.blackKingLocation

        # call squareUnderAttack without passing a boolean; let it
        # determine ally color from self.whiteToMove
        return self.squareUnderAttack(king_row, king_col)

    def squareUnderAttack(self, r, c, ally_color=None):
        """
        Returns True if square (r, c) is attacked by the opponent.
        """
        if ally_color is None:
            ally_color = 'w' if self.whiteToMove else 'b'

        enemy_color = 'w' if ally_color == 'b' else 'b'
        directions = ((-1, 0), (0, -1), (1, 0), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1))

        # Check for attacks from sliding pieces (queen, rook, bishop)
        for j in range(len(directions)):
            d = directions[j]
            for i in range(1, 8):
                end_row = r + d[0] * i
                end_col = c + d[1] * i
                if 0 <= end_row < 8 and 0 <= end_col < 8:
                    end_piece = self.board[end_row][end_col]
                    if end_piece[0] == ally_color:  # No attack through allied piece
                        break
                    elif end_piece[0] == enemy_color:
                        type = end_piece[1]
                        # Check if the piece can attack in this direction
                        if (0 <= j <= 3 and type == 'R') or \
                                (4 <= j <= 7 and type == 'B') or \
                                (type == 'Q') or \
                                (i == 1 and type == 'K'):  # King can attack one square away
                            return True
                        else:  # Enemy piece not applying attack
                            break
                else:  # Off board
                    break

        # Check for knight attacks
        knight_moves = ((-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1))
        for m in knight_moves:
            end_row = r + m[0]
            end_col = c + m[1]
            if 0 <= end_row < 8 and 0 <= end_col < 8:
                end_piece = self.board[end_row][end_col]
                if end_piece[0] == enemy_color and end_piece[1] == 'N':
                    return True

        # Check for pawn attacks
        if ally_color == 'w':  # Black pawns attacking
            if r - 1 >= 0:
                if c - 1 >= 0:
                    if self.board[r - 1][c - 1] == 'bp':
                        return True
                if c + 1 < 8:
                    if self.board[r - 1][c + 1] == 'bp':
                        return True
        else:  # White pawns attacking
            if r + 1 < 8:
                if c - 1 >= 0:
                    if self.board[r + 1][c - 1] == 'wp':
                        return True
                if c + 1 < 8:
                    if self.board[r + 1][c + 1] == 'wp':
                        return True

        return False

    def getAllPossibleMoves(self, include_castles=True):
        moves = []
        for r in range(len(self.board)):
            for c in range(len(self.board[r])):
                turn = self.board[r][c][0]
                if (turn == 'w' and self.whiteToMove) or (turn == 'b' and not self.whiteToMove):
                    piece = self.board[r][c][1]
                    if piece == 'K':
                        # For king, we need to handle the include_castles parameter
                        self.getKingMoves(r, c, moves, include_castles)
                    else:
                        self.moveFunction[piece](r, c, moves)
        return moves

    def getPawnMoves(self, r, c, moves):
        piece_pinned = False
        pin_direction = ()
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piece_pinned = True
                pin_direction = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
                break

        if self.whiteToMove:  # White pawn moves
            if self.board[r - 1][c] == "--":  # 1 square move
                if not piece_pinned or pin_direction == (-1, 0):
                    moves.append(Move((r, c), (r - 1, c), self.board))
                    if r == 6 and self.board[r - 2][c] == "--":  # 2 square move from starting position
                        moves.append(Move((r, c), (r - 2, c), self.board))

            # Captures
            if c - 1 >= 0:  # Capture to left
                if not piece_pinned or pin_direction == (-1, -1):
                    if self.board[r - 1][c - 1][0] == 'b':  # Black piece to capture
                        moves.append(Move((r, c), (r - 1, c - 1), self.board))
            if c + 1 <= 7:  # Capture to right
                if not piece_pinned or pin_direction == (-1, 1):
                    if self.board[r - 1][c + 1][0] == 'b':  # Black piece to capture
                        moves.append(Move((r, c), (r - 1, c + 1), self.board))

            # En passant captures
            if self.enpassantPossible:
                if self.enpassantPossible[0] == r - 1 and self.enpassantPossible[1] == c - 1:
                    if not piece_pinned or pin_direction == (-1, -1):
                        moves.append(Move((r, c), (r - 1, c - 1), self.board, isEnPassantMove=True))
                if self.enpassantPossible[0] == r - 1 and self.enpassantPossible[1] == c + 1:
                    if not piece_pinned or pin_direction == (-1, 1):
                        moves.append(Move((r, c), (r - 1, c + 1), self.board, isEnPassantMove=True))

        else:  # Black pawn moves
            if self.board[r + 1][c] == "--":  # 1 square move
                if not piece_pinned or pin_direction == (1, 0):
                    moves.append(Move((r, c), (r + 1, c), self.board))
                    if r == 1 and self.board[r + 2][c] == "--":  # 2 square move from starting position
                        moves.append(Move((r, c), (r + 2, c), self.board))

            # Captures
            if c - 1 >= 0:  # Capture to left
                if not piece_pinned or pin_direction == (1, -1):
                    if self.board[r + 1][c - 1][0] == 'w':  # White piece to capture
                        moves.append(Move((r, c), (r + 1, c - 1), self.board))
            if c + 1 <= 7:  # Capture to right
                if not piece_pinned or pin_direction == (1, 1):
                    if self.board[r + 1][c + 1][0] == 'w':  # White piece to capture
                        moves.append(Move((r, c), (r + 1, c + 1), self.board))

            # En passant captures
            if self.enpassantPossible:
                if self.enpassantPossible[0] == r + 1 and self.enpassantPossible[1] == c - 1:
                    if not piece_pinned or pin_direction == (1, -1):
                        moves.append(Move((r, c), (r + 1, c - 1), self.board, isEnPassantMove=True))
                if self.enpassantPossible[0] == r + 1 and self.enpassantPossible[1] == c + 1:
                    if not piece_pinned or pin_direction == (1, 1):
                        moves.append(Move((r, c), (r + 1, c + 1), self.board, isEnPassantMove=True))

    def getRookMoves(self, r, c, moves):
        piece_pinned = False
        pin_direction = ()
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piece_pinned = True
                pin_direction = (self.pins[i][2], self.pins[i][3])
                if self.board[r][c][
                    1] != 'Q':  # Can't remove queen from pin on rook moves, only remove it on bishop moves
                    self.pins.remove(self.pins[i])
                break

        directions = ((-1, 0), (0, -1), (1, 0), (0, 1))
        enemy_color = 'b' if self.whiteToMove else 'w'
        for d in directions:
            for i in range(1, 8):
                end_row = r + d[0] * i
                end_col = c + d[1] * i
                if 0 <= end_row < 8 and 0 <= end_col < 8:
                    if not piece_pinned or pin_direction == d or pin_direction == (-d[0], -d[1]):
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
                else:
                    break

    def getBishopMoves(self, r, c, moves):
        piece_pinned = False
        pin_direction = ()
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piece_pinned = True
                pin_direction = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
                break

        directions = ((-1, -1), (-1, 1), (1, -1), (1, 1))
        enemy_color = 'b' if self.whiteToMove else 'w'
        for d in directions:
            for i in range(1, 8):
                end_row = r + d[0] * i
                end_col = c + d[1] * i
                if 0 <= end_row < 8 and 0 <= end_col < 8:
                    if not piece_pinned or pin_direction == d or pin_direction == (-d[0], -d[1]):
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
                else:
                    break

    def getKnightMoves(self, r, c, moves):
        piece_pinned = False
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piece_pinned = True
                self.pins.remove(self.pins[i])
                break

        if piece_pinned:
            return  # Knight can't move if pinned

        knight_moves = ((-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1))
        ally_color = 'w' if self.whiteToMove else 'b'
        for m in knight_moves:
            end_row = r + m[0]
            end_col = c + m[1]
            if 0 <= end_row < 8 and 0 <= end_col < 8:
                if not piece_pinned:
                    end_piece = self.board[end_row][end_col]
                    if end_piece[0] != ally_color:
                        moves.append(Move((r, c), (end_row, end_col), self.board))

    def getQueenMoves(self, r, c, moves):
        self.getRookMoves(r, c, moves)
        self.getBishopMoves(r, c, moves)

    def getKingMoves(self, r, c, moves, include_castles=True):
        # Kings can't be pinned, so no pin check needed
        king_moves = ((-1, -1), (-1, 0), (-1, 1),
                      (0, -1), (0, 1),
                      (1, -1), (1, 0), (1, 1))
        ally_color = "w" if self.whiteToMove else "b"
        for i in range(8):
            end_row = r + king_moves[i][0]
            end_col = c + king_moves[i][1]
            if 0 <= end_row < 8 and 0 <= end_col < 8:
                end_piece = self.board[end_row][end_col]
                if end_piece[0] != ally_color:  # not an ally piece
                    # Temporarily move king to the target square and check if it's attacked
                    original_white_king_loc = self.whiteKingLocation
                    original_black_king_loc = self.blackKingLocation

                    if ally_color == 'w':
                        self.whiteKingLocation = (end_row, end_col)
                    else:
                        self.blackKingLocation = (end_row, end_col)

                    # If the target square is not under attack, add the move
                    if not self.squareUnderAttack(end_row, end_col):
                        moves.append(Move((r, c), (end_row, end_col), self.board))

                    # Restore king location
                    self.whiteKingLocation = original_white_king_loc
                    self.blackKingLocation = original_black_king_loc

        # add castling moves only if allowed and requested
        if include_castles:
            self.getCastleMoves(r, c, moves, ally_color)

    def getCastleMoves(self, r, c, moves, ally_color):
        if self.squareUnderAttack(r, c):  # king in check, can't castle
            return

        if (self.whiteToMove and self.currentCastlingRights.wks) or \
                (not self.whiteToMove and self.currentCastlingRights.bks):
            self.getKingSideCastleMoves(r, c, moves, ally_color)

        if (self.whiteToMove and self.currentCastlingRights.wqs) or \
                (not self.whiteToMove and self.currentCastlingRights.bqs):
            self.getQueenSideCastleMoves(r, c, moves, ally_color)

    def getKingSideCastleMoves(self, r, c, moves, ally_color):
        # Check if squares between king and rook are empty
        if self.board[r][c + 1] == "--" and self.board[r][c + 2] == "--":
            # Check if squares king moves through are not under attack
            if not self.squareUnderAttack(r, c + 1, ally_color) and not self.squareUnderAttack(r, c + 2, ally_color):
                moves.append(Move((r, c), (r, c + 2), self.board, isCastleMove=True))

    def getQueenSideCastleMoves(self, r, c, moves, ally_color):
        # Check if squares between king and rook are empty
        if self.board[r][c - 1] == "--" and self.board[r][c - 2] == "--" and self.board[r][c - 3] == "--":
            # Check if squares king moves through are not under attack
            if not self.squareUnderAttack(r, c - 1, ally_color) and not self.squareUnderAttack(r, c - 2, ally_color):
                moves.append(Move((r, c), (r, c - 2), self.board, isCastleMove=True))

class CastlingRights:
    def __init__(self, wks, bks, wqs, bqs):
        self.wks = wks  # White king-side
        self.bks = bks  # Black king-side
        self.wqs = wqs  # White queen-side
        self.bqs = bqs  # Black queen-side


class Move:
    ranks_to_rows = {"1": 7, "2": 6, "3": 5, "4": 4,
                     "5": 3, "6": 2, "7": 1, "8": 0}
    rows_to_ranks = {v: k for k, v in ranks_to_rows.items()}
    files_to_cols = {"a": 0, "b": 1, "c": 2, "d": 3,
                     "e": 4, "f": 5, "g": 6, "h": 7}
    cols_to_files = {v: k for k, v in files_to_cols.items()}

    def __init__(self, start_sq, end_sq, board, isEnPassantMove=False, isCastleMove=False):
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

        # Castle move
        self.isCastleMove = isCastleMove

        self.move_id = self.start_row * 1000 + self.start_col * 100 + self.end_row * 10 + self.end_col

    def __eq__(self, other):
        if isinstance(other, Move):
            return self.move_id == other.move_id
        return False

    def get_chess_notation(self):
        return self.get_rank_file(self.start_row, self.start_col) + self.get_rank_file(self.end_row, self.end_col)

    def get_rank_file(self, r, c):
        return self.cols_to_files[c] + self.rows_to_ranks[r]
