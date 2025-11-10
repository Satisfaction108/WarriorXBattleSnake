import logging
import os
import typing

from flask import Flask
from flask import request


def run_server(handlers: typing.Dict):
    app = Flask("Battlesnake")

    @app.get("/")
    def on_info():
        print("📡 INFO REQUEST")
        return handlers["info"]()

    @app.post("/start")
    def on_start():
        game_state = request.get_json()
        print(f"🎮 GAME START - Game ID: {game_state.get('game', {}).get('id', 'unknown')}")
        handlers["start"](game_state)
        return "ok"

    @app.post("/move")
    def on_move():
        game_state = request.get_json()
        turn = game_state.get("turn", "?")
        game_id = game_state.get("game", {}).get("id", "unknown")
        print(f"\n🎯 MOVE REQUEST - Game: {game_id}, Turn: {turn}")
        try:
            response = handlers["move"](game_state)
            print(f"✅ SERVER SENDING RESPONSE: {response}")
            return response
        except Exception as e:
            print(f"🚨🚨🚨 EXCEPTION IN MOVE HANDLER: {e}")
            import traceback
            traceback.print_exc()

            # Try to find a safe move instead of defaulting to "up"
            try:
                my_head = game_state["you"]["body"][0]
                board_width = game_state["board"]["width"]
                board_height = game_state["board"]["height"]

                # Try each direction to find a safe one
                for direction in ["right", "left", "down", "up"]:
                    new_pos = {"x": my_head["x"], "y": my_head["y"]}
                    if direction == "up":
                        new_pos["y"] += 1
                    elif direction == "down":
                        new_pos["y"] -= 1
                    elif direction == "left":
                        new_pos["x"] -= 1
                    elif direction == "right":
                        new_pos["x"] += 1

                    # Check if move is within bounds
                    if 0 <= new_pos["x"] < board_width and 0 <= new_pos["y"] < board_height:
                        # Check if not hitting own body
                        is_safe = True
                        for segment in game_state["you"]["body"][:-1]:
                            if segment["x"] == new_pos["x"] and segment["y"] == new_pos["y"]:
                                is_safe = False
                                break

                        if is_safe:
                            print(f"⚠️  EMERGENCY FALLBACK: Using {direction}")
                            return {"move": direction, "shout": "ERROR!"}
            except:
                pass

            # Last resort - return up
            print(f"⚠️  LAST RESORT: Returning 'up'")
            return {"move": "up", "shout": "ERROR!"}

    @app.post("/end")
    def on_end():
        game_state = request.get_json()
        handlers["end"](game_state)
        return "ok"

    @app.after_request
    def identify_server(response):
        response.headers.set(
            "server", "battlesnake/github/starter-snake-python"
        )
        return response

    host = "0.0.0.0"
    port = int(os.environ.get("PORT", "5000"))

    logging.getLogger("werkzeug").setLevel(logging.ERROR)

    print(f"\nRunning Battlesnake at http://{host}:{port}")
    app.run(host=host, port=port)

