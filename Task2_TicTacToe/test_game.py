import unittest
import random
from game import TicTacToeGame

class TestTicTacToeGame(unittest.TestCase):
    def setUp(self):
        self.game = TicTacToeGame()

    def test_win_conditions(self):
        # Row win
        board = [
            'X', 'X', 'X',
            'O', ' ', 'O',
            ' ', ' ', ' '
        ]
        self.assertEqual(self.game.check_winner(board), 'X')

        # Column win
        board = [
            'O', 'X', ' ',
            'O', 'X', ' ',
            'O', ' ', ' '
        ]
        self.assertEqual(self.game.check_winner(board), 'O')

        # Diagonal win
        board = [
            'X', ' ', 'O',
            ' ', 'X', ' ',
            'O', ' ', 'X'
        ]
        self.assertEqual(self.game.check_winner(board), 'X')

    def test_draw_condition(self):
        # Tie board
        board = [
            'X', 'O', 'X',
            'X', 'O', 'O',
            'O', 'X', 'X'
        ]
        self.assertEqual(self.game.check_winner(board), 'Tie')

        # Ongoing board
        board = [
            'X', 'O', 'X',
            'X', 'O', 'O',
            'O', 'X', ' '
        ]
        self.assertIsNone(self.game.check_winner(board))

    def test_first_move_optimization(self):
        # Verify first move targets center or corner
        empty_board = [' '] * 9
        move = self.game.get_ai_move(empty_board, 'X', 'unbeatable')
        self.assertIn(move, [4, 0, 2, 6, 8])

    def test_immediate_win_ai(self):
        # AI (O) has immediate win
        board = [
            'O', 'O', ' ',
            'X', 'X', ' ',
            ' ', ' ', ' '
        ]
        move = self.game.get_ai_move(board, 'O', 'unbeatable')
        self.assertEqual(move, 2)

    def test_immediate_block_ai(self):
        # Human (X) has immediate win, AI (O) must block
        board = [
            'X', 'X', ' ',
            'O', ' ', ' ',
            ' ', ' ', ' '
        ]
        move = self.game.get_ai_move(board, 'O', 'unbeatable')
        self.assertEqual(move, 2)

    def test_ai_unbeatable(self):
        """Simulates multiple complete games where AI plays Expert/Unbeatable vs Random Human. AI must never lose."""
        for _ in range(50):
            board = [' '] * 9
            ai_symbol = 'O'
            human_symbol = 'X'
            
            # Randomize who starts
            current_turn = random.choice(['human', 'ai'])
            
            while self.game.check_winner(board) is None:
                if current_turn == 'human':
                    # Simulated random human move
                    empty_spots = self.game.get_empty_indices(board)
                    move = random.choice(empty_spots)
                    board[move] = human_symbol
                    current_turn = 'ai'
                else:
                    # Unbeatable AI move
                    move = self.game.get_ai_move(board, ai_symbol, 'unbeatable')
                    board[move] = ai_symbol
                    current_turn = 'human'
            
            winner = self.game.check_winner(board)
            # AI must win or tie, but NEVER lose
            self.assertIn(winner, [ai_symbol, 'Tie'])

if __name__ == "__main__":
    unittest.main()
