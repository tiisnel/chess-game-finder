# chess-game-finder

This project is inspired by chess.com annual quiz, where instead of memorization, it is important to find answers using all possible help.

One of the most reccuring question is to find chess games, based on a image of a position that occured in game.
Normally, those are from famous players over-the-board tournament games, that are easily found from online databases.
But sometimes, it is just some random game played on their site - last year there was such question, with only one hint, that it was played by american grandmaster
While other chess sites allow mass-downloading games easily, chess.com itself has strighter restrictions

# My solution

Chess.com has an API, that allows to download one user specific month games.
By assuming, that american = USA, I made a list of each player usernames, that I could google (names.csv).
Then, my program asks for fen board position data. Iterates over each file in games folder, and then asks API to download more games from csv to that folder(optional:specify time range)

# Usage

* Must have games folder(might be empty).
* Requires scid vs pc software for position checking. Especially tcscid.exe. Edit path in code test =send(p,'"C:\\Scid vs PC\\bin\\tcscid.exe"\n')
* Uses wexpect instead of subproccess module - So can be run from terminal but not from IDE
* delete = False - line prevents python from deleting files that did not match. Important, if same gameset is tested later against some other position. As chess.com API is slow: only allows serial requests, it is better to work with local games. However, if working with limited memory environment, it might be better to change it.
