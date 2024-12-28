import json
import random

import uvicorn

from uuid import uuid4
from fastapi import FastAPI, Response, Depends
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from asyncio import sleep
from fastapi.security import APIKeyHeader

from mancala import MancalaGame
from models import GameState, CreatedGame, JoinedGame

app = FastAPI()

app.games = {}

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

security = APIKeyHeader(name="Mancala-Key")


@app.post("/create_game")
async def create_game(game_name: str = None) -> CreatedGame:
    if len(app.games) > 9:
        return Response("Too many active games", status_code=507)

    game_id = str(uuid4())
    if game_name is not None:
        game_id = game_name

    if game_id in app.games and app.games[game_id].player2 is None:
        game = app.games[game_id]
        player_2 = str(uuid4())
        game.player2 = player_2
        return CreatedGame(
            game_id=game_id, player_info=JoinedGame(player=2, uuid=player_2)
        )

    elif game_id in app.games:
        return Response("Game already exists and is being played", status_code=400)

    player_1 = str(uuid4())
    app.games[game_id] = MancalaGame(
        player1=player_1,
    )

    print(app.games)

    return CreatedGame(game_id=game_id, player_info=JoinedGame(player=1, uuid=player_1))


@app.post("/join_game/{game_id}")
async def join_game(game_id: str) -> JoinedGame:
    if game_id not in app.games:
        return Response("Game not found", status_code=404)

    game: MancalaGame = app.games[game_id]

    if game.player2 is not None:
        return Response("Game is full", status_code=400)

    player_2 = str(uuid4())
    game.player2 = player_2

    return JoinedGame(player=2, uuid=player_2)


@app.post("/make_move/{game_id}")
async def make_move(
    game_id: str, pit_index: int, auth_key: str = Depends(security)
) -> GameState:
    if game_id not in app.games:
        return Response("Game not found", status_code=404)

    game: MancalaGame = app.games[game_id]

    if game.player1 != auth_key and game.player2 != auth_key:
        return Response("Unauthorized", status_code=401)

    if game.current_player == 1 and game.player1 != auth_key:
        return Response("It's not your turn", status_code=401)

    if game.current_player == 2 and game.player2 != auth_key:
        return Response("It's not your turn", status_code=401)

    try:
        await game.make_move(pit_index)
    except Exception as e:
        return Response(str(e), status_code=400)

    winner = await game.get_winner()
    if winner is not None:
        del app.games[game_id]

    return GameState(
        game_id=game_id,
        board=game.board,
        current_player=game.current_player,
        winner=await game.get_winner(),
    )
    
    
@app.get("/get_game/{game_id}")
async def get_game(game_id: str) -> GameState:
    if game_id not in app.games:
        return Response("Game not found", status_code=404)

    game: MancalaGame = app.games[game_id]

    return GameState(
        game_id=game_id,
        board=game.board,
        current_player=game.current_player,
        winner=await game.get_winner(),
    )


@app.get("/watch_game/{game_id}")
async def watch_game(game_id: str) -> GameState:
    if game_id not in app.games:
        return Response("Game not found", status_code=404)

    game: MancalaGame = app.games[game_id]

    async def game_watcher():
        while True:
            data = json.dumps(
                {
                    "game_id": game_id,
                    "game_board": game.board,
                    "current_player": game.current_player,
                    "winner": await game.get_winner(),
                }
            )

            yield f"data: {data}\n\n"

            await game.wait_for_event()
            if await game.is_game_over():
                data = json.dumps(
                    {
                        "winner": await game.get_winner(),
                        "player1_score": game.player1_score,
                        "player2_score": game.player2_score,
                    }
                )
                yield f"data: {data}\n\n"
                break

    return StreamingResponse(game_watcher(), media_type="text/event-stream")


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=9111)
