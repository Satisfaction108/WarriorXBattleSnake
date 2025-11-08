# WarriorX Battlesnake

A Battlesnake built with Python and Flask. Get started at [play.battlesnake.com](https://play.battlesnake.com).

![Battlesnake Logo](https://media.battlesnake.com/social/StarterSnakeGitHubRepos_Python.png)

## Technologies Used

This project uses [Python 3](https://www.python.org/) and [Flask](https://flask.palletsprojects.com/). It also comes with an optional [Dockerfile](https://docs.docker.com/engine/reference/builder/) to help with deployment.

## Run Your Battlesnake Locally

Install dependencies using pip

```sh
pip install -r requirements.txt
```

Start your Battlesnake

```sh
python main.py
```

You should see the following output once it is running

```sh
Running your Battlesnake at http://0.0.0.0:8000
 * Serving Flask app 'Battlesnake'
 * Debug mode: off
```

Open [localhost:8000](http://localhost:8000) in your browser and you should see

```json
{"apiversion":"1","author":"","color":"#888888","head":"default","tail":"default"}
```

## Deploy to Render.com

See [RENDER_DEPLOYMENT.md](RENDER_DEPLOYMENT.md) for step-by-step deployment instructions.

## Play a Game Locally

Install the [Battlesnake CLI](https://github.com/BattlesnakeOfficial/rules/tree/main/cli)
* You can [download compiled binaries here](https://github.com/BattlesnakeOfficial/rules/releases)
* or [install as a go package](https://github.com/BattlesnakeOfficial/rules/tree/main/cli#installation) (requires Go 1.18 or higher)

Command to run a local game

```sh
battlesnake play -W 11 -H 11 --name 'WarriorX' --url http://localhost:8000 -g solo --browser
```

## Next Steps

Continue with the [Battlesnake Quickstart Guide](https://docs.battlesnake.com/quickstart) to customize and improve your Battlesnake's behavior.

**Note:** To play games on [play.battlesnake.com](https://play.battlesnake.com) you'll need to deploy your Battlesnake to a live web server OR use a port forwarding tool like [ngrok](https://ngrok.com/) to access your server locally.

## Customization

Edit the `info()` function in `main.py` to customize your Battlesnake's appearance:
- `author`: Your Battlesnake username
- `color`: Hex color code (e.g., "#FF0000" for red)
- `head`: Choose from available head styles
- `tail`: Choose from available tail styles

Edit the `move()` function in `main.py` to implement your Battlesnake's strategy!

