import random

class TicTacToeGame:
    WINNING_COMBINATIONS = [
        (0, 1, 2), (3, 4, 5), (6, 7, 8), # Rows
        (0, 3, 6), (1, 4, 7), (2, 5, 8), # Columns
        (0, 4, 8), (2, 4, 6)             # Diagonals
    ]

    def __init__(self):
        pass

    def check_winner(self, board: list[str]) -> str | None:
        """
        Checks if the board has a winner or is a tie.
        Returns:
            - 'X' or 'O': if there is a winner.
            - 'Tie': if there are no empty spots left.
            - None: if the game is still active.
        """
        for combo in self.WINNING_COMBINATIONS:
            if board[combo[0]] != ' ' and board[combo[0]] == board[combo[1]] == board[combo[2]]:
                return board[combo[0]]
        
        if ' ' not in board:
            return 'Tie'
            
        return None

    def get_empty_indices(self, board: list[str]) -> list[int]:
        return [i for i, cell in enumerate(board) if cell == ' ']

    def get_ai_move(self, board: list[str], ai_symbol: str, difficulty: str = "unbeatable") -> int:
        """
        Calculates the best move for the AI depending on the difficulty.
        Returns:
            - int: index (0-8) where the AI wants to play.
        """
        empty_spots = self.get_empty_indices(board)
        if not empty_spots:
            raise ValueError("No empty spots left on the board.")

        human_symbol = 'O' if ai_symbol == 'X' else 'X'
        difficulty = difficulty.lower()

        # 1. Easy Difficulty: Pure Random Moves
        if difficulty == "easy":
            return random.choice(empty_spots)

        # 2. Medium Difficulty: 50% Optimal Minimax / 50% Random Play
        elif difficulty == "medium":
            # 50% chance of making an error (random play)
            if random.random() < 0.4:
                return random.choice(empty_spots)
            # Otherwise play minimax to block or win
            return self._get_best_minimax_move(board, ai_symbol, human_symbol)

        # 3. Unbeatable Difficulty: Pure Minimax with Alpha-Beta Pruning
        else:
            return self._get_best_minimax_move(board, ai_symbol, human_symbol)

    def _get_best_minimax_move(self, board: list[str], ai_symbol: str, human_symbol: str) -> int:
        """Calculates the optimal move using the minimax algorithm."""
        best_score = float('-inf')
        best_move = -1
        
        # Optimize first move on empty board to save computation time (corners or center)
        empty_spots = self.get_empty_indices(board)
        if len(empty_spots) == 9:
            # First turn: center (4) or a random corner (0, 2, 6, 8) is optimal
            return random.choice([4, 0, 2, 6, 8])

        for move in empty_spots:
            # Make simulated move
            board[move] = ai_symbol
            # Calculate score
            score = self._minimax(board, 0, False, float('-inf'), float('inf'), ai_symbol, human_symbol)
            # Revert move
            board[move] = ' '
            
            if score > best_score:
                best_score = score
                best_move = move
                
        return best_move

    def _minimax(self, board: list[str], depth: int, is_maximizing: bool, alpha: float, beta: float, ai_symbol: str, human_symbol: str) -> int:
        """
        Minimax algorithm with Alpha-Beta pruning.
        Returns evaluation score.
        """
        winner = self.check_winner(board)
        
        if winner == ai_symbol:
            return 10 - depth  # Prefer faster wins
        elif winner == human_symbol:
            return depth - 10  # Prefer delayed losses
        elif winner == 'Tie':
            return 0

        empty_spots = self.get_empty_indices(board)

        if is_maximizing:
            max_eval = float('-inf')
            for move in empty_spots:
                board[move] = ai_symbol
                eval_score = self._minimax(board, depth + 1, False, alpha, beta, ai_symbol, human_symbol)
                board[move] = ' '
                max_eval = max(max_eval, eval_score)
                alpha = max(alpha, eval_score)
                if beta <= alpha:
                    break  # Beta cut-off
            return max_eval
        else:
            min_eval = float('inf')
            for move in empty_spots:
                board[move] = human_symbol
                eval_score = self._minimax(board, depth + 1, True, alpha, beta, ai_symbol, human_symbol)
                board[move] = ' '
                min_eval = min(min_eval, eval_score)
                beta = min(beta, eval_score)
                if beta <= alpha:
                    break  # Alpha cut-off
            return min_eval
