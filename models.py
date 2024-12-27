from typing import List, Optional, Tuple

from pydantic import BaseModel


class JoinedGame(BaseModel):
    player: int = 1
    uuid: str


class CreatedGame(BaseModel):
    game_id: str
    player_info: JoinedGame


class GameState(BaseModel):
    game_id: str
    board: List[int] = [4] * 6 + [0] + [4] * 6 + [0]
    current_player: int
    winner: Optional[int] = None
