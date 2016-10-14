#!/usr/bin/python
import praw
import pdb
import re
import os
import pickle
from config_bot import *

# implementing minimax algorithm for tic tac toe, following online guide
def isWin(gameboard):
    for i in range(3):
        if len(set(gameboard[i * 3 : i * 3 + 3])) is 1 and gameboard[i * 3] is not '-':
            return True
    # cols
    for i in range(3):
       if (gameboard[i] is gameboard[i + 3]) and (gameboard[i] is gameboard[i + 6]) and gameboard[i] is not '-':
           return True
    # diagonals
    if gameboard[0] is gameboard[4] and gameboard[4] is gameboard[8] and gameboard[4] is not '-':
        return True
    if gameboard[2] is gameboard[4] and gameboard[4] is gameboard[6] and gameboard[4] is not '-':
        return True
    return False


def nextMove(gameboard, player): # returns predicted outcome and index of next move
    if len(set(gameboard)) == 1:
        return 0, 4

    nextPlayer = "X" if player is "O" else "O"
    if isWin(gameboard):
        if player is 'X':
            return -1, -1
        else:
            return 1, -1
    results = [] # list for appending the result
    spaceCount = gameboard.count('-')
    if spaceCount is 0: # if gameboard is filled but not in a winning state
        return 0, -1
    spaces = [] # list for storing the indices of spaces
    for i in range(9):
        if gameboard[i] is "-":
            spaces.append(i)

    for i in spaces:
        gameboard[i] = player # check possibility
        outcome, move = nextMove(gameboard, nextPlayer)
        results.append(outcome)
        gameboard[i] = "-" # restore gameboard
    if player is "X":
        best = max(results)
        return best, spaces[results.index(best)]
    else:
        best = min(results)
        return best, spaces[results.index(best)]
# END AI ---------------------------------------------------------------------------------


# Check that the file that contains our username exists
if not os.path.isfile("config_bot.py"):
    print("You must create a config file with your username and password.")
    print("Please see config_skele.py")
    exit(1)

# Create the Reddit instance
user_agent = ("TicTacToe Bot 0.1")
r = praw.Reddit(user_agent = user_agent)

# and login
r.login(REDDIT_USERNAME, REDDIT_PASS, disable_warning=True)

# Have we run this code before? If not, create an empty list
if not os.path.isfile("posts_replied_to.txt"):
    posts_replied_to = []

# If we have run the code before, load the list of posts we have replied to
else:
    # Read the file into a list and remove any empty values
    with open("posts_replied_to.txt", "r") as f:
        posts_replied_to = f.read()
        posts_replied_to = posts_replied_to.split("\n")
        posts_replied_to = list(filter(None, posts_replied_to))

if not os.path.isfile("current_games.p"):
    current_games = dict()

elif os.path.getsize("current_games.p") > 0:
    with open("current_games.p", "rb") as f:
        current_games = pickle.load(f)

else:
    current_games = dict()

# command to request bot
trigger = "!tictactoe"

# Get the top 5 values from subreddit
subreddit = r.get_subreddit("tttbottest")
for submission in subreddit.get_hot(limit=10):
    # print submission.title
    flat_comments = praw.helpers.flatten_tree(submission.comments)
    for comment in flat_comments:
        # If we haven't replied to this comment before
        if comment.id not in posts_replied_to:

            # Do a case insensitive search
            if re.search(trigger, comment.body, re.IGNORECASE):
                body = comment.body
                before, key, after = body.partition(trigger)
                if key == trigger:
                    afterWords = re.findall(r"[\w']+", after)
                    if len(afterWords) != 0:
                        position = afterWords[0]
                        if len(position) == 2:
                            row = int(position[0])
                            col = int(position[1])
                            madeValidMove = False
                            # if input is valid
                            if (row >= 0) and (row <= 2) and (col >= 0) and (col <= 2):
                                # if player is already in a game
                                if comment.author.name in current_games:
                                    gameboard = current_games[comment.author.name]
                                    # if space is open
                                    if gameboard[row * 3 + col] == "-":
                                        madeValidMove = True
                                        gameboard[row * 3 + col] = "X"
                                        result, move = nextMove(gameboard, "O")
                                        if move != -1:
                                            gameboard[move] = "O"
                                        r2, m2 = nextMove(gameboard, "X")
                                        print(gameboard)
                                # if player is starting new game
                                else:
                                    madeValidMove = True
                                    gameboard = ["-", "-", "-", "-", "-", "-", "-", "-", "-"]
                                    gameboard[row * 3 + col] = "X"
                                    result, move = nextMove(gameboard, "O")
                                    gameboard[move] = "O"
                                    r2, m2 = nextMove(gameboard, "X")
                                    print(gameboard)

                                if madeValidMove:
                                    # Reply to the post
                                    output = ""
                                    for i in range(3):
                                        output += "    " + gameboard[i * 3] + gameboard[i * 3 + 1] + gameboard[i * 3 + 2] + "\n"
                                    if m2 is -1 and r2 is 0:
                                        output = "It's a draw!\n" + output
                                        del current_games[comment.author.name]
                                    elif m2 is -1 and r2 is -1:
                                        output = "I won!\n\n" + output
                                        del current_games[comment.author.name]
                                    comment.reply(output + "\n\n--------------------------------------\n\nSyntax: call bot followed row and column number. E.g. 00 is top left, 21 is bottom middle, etc")

                                    print("Bot replying to : ", comment.id)

                                    # Store the current id into our list
                                    posts_replied_to.append(comment.id)

                                    if m2 is not -1:
                                        # Store user and game to list
                                        current_games[comment.author.name] = gameboard








# Write our updated list back to the file
with open("posts_replied_to.txt", "w") as f:
    for post_id in posts_replied_to:
        f.write(post_id + "\n")

with open("current_games.p", "wb") as f:
    pickle.dump(current_games, f)


