# ultimatexo
An ultimate noughts and crosses game.

## Why?
Because ultimate noughts and crosses is fun, and I had never built a GUI
python application before.

## Shouldn't it be ultimateox?
Shh. I still pronounce it "ultimate noughts and crosses".

## You shouldn't have done X
Probably. Fix it and submit a pull request.

## TODO
* Refactor main.py a lot
  * Move all the gameboard canvas operations into one or more new classes in a new file
  * Move the different windows into their own files
  * Make it a bit easier to read

* Add player names to interface

* Possibly add a detailed game log (rather than just latest status being shown)

* Permit colours to be customised, why not

* Store a better record of the course of a game, something like:
  
  ```JavaScript
  { /* JSON */
    "id": "(guid)",
    "x": "Michelle", /* player name */
    "o": "Michael", /* player name */
    "moves": [
      {
        "seq": 0, /* sequential; useful for network play and "rewind to X" */
        "player": "x",
        "board": [0, 0], /* row, col */
        "square": [0, 0], /* row, col */
      },
      /* ... */
    ]
  }
  ```
  
* Once we have a good record of the course of a game, we can do other cool stuff:
  * Undo last move
  * Keep a record of the game in a list box and replay the game
  * Save and load games (because obviously that's so important)
  * Network play (we could even [add chat](https://www.gnu.org/software/emacs/))
