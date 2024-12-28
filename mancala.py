import asyncio


class InvalidMoveError(Exception): ...


class NoStonesError(Exception): ...


class MancalaGame:
    """
    Class representing a game of Mancala.
    """

    def __init__(self, player1: str = None, player2: str = None):
        """
        Initialize the Mancala game.
        """
        # Initialize the board with 4 stones in each pit
        self.board = [4] * 14
        # Set the first player's Mancala pit to 0 stones
        self.board[6] = 0
        # Set the second player's Mancala pit to 0 stones
        self.board[13] = 0
        # Start with the first player
        self.current_player = 1

        self.player1 = player1
        self.player2 = player2

        self.event = asyncio.Event()

    def __str__(self):
        """
        Return a string representation of the Mancala game.
        """

        top_row = " ".join([f"{self.board[i]:2}" for i in range(12, 6, -1)])
        bottom_row = " ".join([f"{self.board[i]:2}" for i in range(6)])
        player1_store = f"{self.board[6]:2}"
        player2_store = f"{self.board[13]:2}"

        return "\n".join(
            [
                f"        Player 2",
                f"   {top_row}",
                f"{player2_store}{' ' * 18} {player1_store}",
                f"   {bottom_row}",
                f"        Player 1",
            ]
        )

    def __repr__(self):
        return self.__str__()

    @property
    def player1_score(self):
        return self.board[6]

    @property
    def player2_score(self):
        return self.board[13]

    async def wait_for_event(self):
        await self.event.wait()
        self.event.clear()

    async def make_move(self, pit_index: int) -> None:
        """
        Make a move in the Mancala game.

        Args:
            pit_index (int): The index of the pit to make a move from.
        """
        # Disallow moves from empty pits
        if self.board[pit_index] == 0:
            raise NoStonesError("Cannot move from an empty pit.")

        # Disallow moves from pits 6 and 13
        if pit_index == 6 or pit_index == 13:
            raise InvalidMoveError("Cannot move from Mancala pit.")
        
        # Disallow moves from the opponent's pits
        if self.current_player == 1 and pit_index > 5:
            raise InvalidMoveError("Cannot move from opponent's pit.")
        if self.current_player == 2 and pit_index < 7:
            raise InvalidMoveError("Cannot move from opponent's pit.")

        # Get the number of stones in the selected pit
        stones = self.board[pit_index]
        # Remove all stones from the selected pit
        self.board[pit_index] = 0

        while stones > 0:
            # Move to the next pit
            pit_index = (pit_index + 1) % 14
            if pit_index == 6 and self.current_player == 2:
                # Skip the opponent's Mancala pit
                continue
            if pit_index == 13 and self.current_player == 1:
                # Skip the opponent's Mancala pit
                continue

            # Place a stone in the current pit
            self.board[pit_index] += 1
            stones -= 1

        # If the last stone is placed in their own store,
        # the player gets another turn
        if self.current_player == 1 and pit_index == 6:
            self.event.set()
            return
        elif self.current_player == 2 and pit_index == 13:
            self.event.set()
            return
        else:
            # Switch to the other player
            self.current_player = 3 - self.current_player
        self.event.set()

    async def is_game_over(self) -> bool:
        """
        Check if the game is over.

        Returns:
            bool: True if the game is over, False otherwise.
        """
        player1_pits = self.board[0:6]
        player2_pits = self.board[7:13]
        return sum(player1_pits) == 0 or sum(player2_pits) == 0

    async def end_game(self) -> None:
        """
        End the game by moving all remaining stones into their respective store.
        """
        if await self.is_game_over():
            # Move stones from player 1's pits to their store
            for i in range(6):
                self.board[6] += self.board[i]
                self.board[i] = 0

            # Move stones from player 2's pits to their store
            for i in range(7, 13):
                self.board[13] += self.board[i]
                self.board[i] = 0

    async def get_winner(self) -> int:
        """
        Get the winner of the game.

        Returns:
            int: The player number of the winner (1 or 2), or 0 if it's a tie.
        """
        if not await self.is_game_over():
            return None

        await self.end_game()

        if self.player1_score > self.player2_score:
            return 1
        elif self.player2_score > self.player1_score:
            return 2
        else:
            return 0
