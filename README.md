# Mancala Server
A game server for playing games of Mancala

## How to play:

1. Start the server with `docker compose up`

2. Read the docs at [http://localhost:8000/docs](http://localhost:8000/docs)

3. Create a game with [http://localhost:8000/create_game](http://localhost:8000/create_game)

    A game_name can optionally be provided [http://localhost:8000/create_game?game_name=my_game](http://localhost:8000/create_game?game_name=my_game)

4. A game will be created and the follow response will be returned

```json
{
  "game_id": "string",
  "player_info": {
    "player": 1,
    "uuid": "string"
  }
}
```

5. The `game_id` will be a randomly generated UUID, or the `game_name` that was provided to the endpoint. 
`player_info` will include a `player` and `uuid`. `player` is whichever player you are, `uuid` is the ID 
you will use to authenticate with the game

6. Include your `uuid` in the headers where `Mancala-Key` = `uuid`

7. Make a move with [http://localhost:8000/make_move/{game_id}?pit_index={pit_index}](http://localhost:8000/make_move/{game_id}?pit_index={pit_index})
