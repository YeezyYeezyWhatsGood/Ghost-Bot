import discord
import asyncio

client = discord.Client()
token = "INSERT YOUR TOKEN HERE"
prefix = "ghost."

@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')

@client.event
async def on_message(message):
    if message.content.startswith(prefix + "help"):
        await client.send_message(message.channel, "Type ghost.makeGame to get started.")
    elif message.content.startswith(prefix + "makeGame"):
        timer = 45
        minWordSize = 4
        finishedSettings = False
        await client.send_message(message.channel, "You have just created a GHOST game, " + message.author.mention + ". First, you can configure the rules. Try ghost.editTimer seconds and ghost.editMinWordSize size. Type ghost.finishedRules when you are done configuring the rules. Then, you can invite other players (or me!) to the game. You can invite other players by typing ghost.invite @Foobar, or you can invite me by typing ghost.inviteAI. Finally, you can start the game by typing ghost.start.")
        while (not finishedSettings):
            await client.send_message(message.channel, "Here are the current settings: ")
            await client.send_message(message.channel, "timer: " + str(timer) + " seconds per move")
            await client.send_message(message.channel, "the minimum size for a word is: " + str(minWordSize) + " letters. This means that you can type out words that contain less than " + str(minWordSize) + " letters for no penalty.")
            msg = await client.wait_for_message(author = message.author, channel = message.channel)
            while (not msg.content.startswith("ghost.editTimer") and not msg.content.startswith("ghost.editMinWordSize") and not msg.content.startswith("ghost.finishedRules")):
                msg = await client.wait_for_message(author = message.author, channel = message.channel)
            if (msg.content.startswith("ghost.editTimer")):
                timer = int(msg.content[16:])
            elif (msg.content.startswith("ghost.editMinWordSize")):
                minWordSize = int(msg.content[22:])
            elif (msg.content.startswith("ghost.finishedRules")):
                finishedSettings = True
        partyMembers = [message.author]
        await client.send_message(message.channel, "Finished setting the rules! Now invite some people to that party.")
        msg = await client.wait_for_message(author=message.author, channel=message.channel)
        while (not msg.content.startswith("ghost.start")):
            while (not msg.content.startswith("ghost.invite") and not msg.content.startswith("ghost.inviteAI") and not msg.content.startswith("ghost.start")):
                if (msg.content.startswith(prefix)):
                    await client.send_message(message.channel, "Wrong command, try ghost.invite, ghost.inviteAI, or ghost.start")
                msg = await client.wait_for_message(author=message.author, channel=message.channel)
            if (msg.content.startswith("ghost.invite")):
                await client.send_message(message.channel, "Hey, " + msg.mentions[0].mention + "! " + message.author.mention + " has invited you to a game of ghost! Reply 'accept' to accept or reply 'decline' to decline.")
                inviteReply = await client.wait_for_message(author = msg.mentions[0], channel = message.channel)
                while (not inviteReply.content == "accept" and not inviteReply.content == "decline"):
                    await client.send_message(message.channel, "Not a valid response. Please reply with 'accept' or 'decline'.")
                    inviteReply = await client.wait_for_message(author=msg.mentions[0], channel=message.channel)
                if (inviteReply.content == "accept"):
                    await client.send_message(message.channel, "Welcome to the lobby, " + msg.mentions[0].mention + "! The game of GHOST will start when party owner " + message.author.mention + " types ghost.start")
                    partyMembers.append(msg.mentions[0])
                else:
                    await client.send_message(message.channel, "Sorry to hear that " + msg.mentions[0].mention + " :(")
            elif (msg.content.startswith(prefix + "inviteAI")):
                await client.send_message(message.channel, "Sorry, but that feature is still being developed. Make sure to complain to Benjacook about this as much as possible, he's a lazy bum.")
            msg = await client.wait_for_message(author=message.author, channel=message.channel)
        if (msg.content.startswith(prefix + "start")):
            await client.send_message(message.channel, "Starting the game!")
            turn = 0
            moveNumber = 0
            challengeMoveNumber = 0
            currentLetters = ""
            gameOver = False
            score = {}
            for member in partyMembers:
                score[member] = ""
            messageNumber = -1
            challengeMessageNumber = -1
            timerMessages = []
            while (not gameOver):
                file = open("wordlist.txt", "r")
                foundWord = False
                for line in file:
                    if (currentLetters == line[:-1] and len(line[:-1]) >= minWordSize):
                        foundWord = True
                if (foundWord):
                    prevTurn = 0
                    if (turn == 0):
                        prevTurn = len(partyMembers) - 1
                    else:
                        prevTurn = turn - 1
                    await client.send_message(message.channel, "Oh no, " + partyMembers[prevTurn].mention + "! '" + currentLetters + "' is a word.")
                    if (len(score[partyMembers[prevTurn]]) >= 4):
                        await client.send_message(message.channel, "You got GHOST and are eliminated!")
                        partyMembers.remove(partyMembers[prevTurn])
                        currentLetters = ""
                    else:
                        ghost = "GHOST"
                        numCurrentLetters = len(score[partyMembers[prevTurn]])
                        score[partyMembers[prevTurn]] = ghost[0:numCurrentLetters + 1]
                        currentLetters = ""
                for member in partyMembers:
                    if (score[member] == "GHOST"):
                        await client.send_message(message.channel, "Sorry, " + partyMembers[member].mention + ", but you have GHOST and have been eliminated!")
                        partyMembers.remove(partyMembers[member])
                        currentLetters = ""
                def newMoveNumber():
                    return moveNumber
                messageNumber = messageNumber + 1
                moveNumber = moveNumber + 1
                await client.send_message(message.channel, "Scoreboard:")
                for member in partyMembers:
                    await client.send_message(message.channel, member.mention + " is at: " + score[member])
                await client.send_message(message.channel, "It's your turn, " + partyMembers[turn].mention + "! If you are playing the first letter, type 'ghost.first letter'. Make sure to replace 'letter' with your actual letter. Otherwise, type 'ghost.left letter' to add a letter to the left or 'ghost.right letter' to add a letter to the right. If you want to challenge the previous player, type ghost.challenge.")
                await client.send_message(message.channel, "The word so far: " + currentLetters)
                timeLeft = timer
                timerMessages.append(await client.send_message(message.channel, "You have " + str(timeLeft) + " seconds left to place a letter!"))
                async def editTimer(timeLeft, messageNumber, timerMessages, moveNumber):
                    doneRunning = False
                    while (timeLeft >= 0 and not doneRunning):
                        await client.edit_message(timerMessages[messageNumber],"You have " + str(timeLeft) + " seconds left to place a letter!")
                        timeLeft = timeLeft - 1
                        asyncio.sleep(1)
                        if (moveNumber != newMoveNumber()):
                            doneRunning = True

                client.loop.create_task(editTimer(timeLeft, messageNumber, timerMessages, moveNumber))
                playerMove = await client.wait_for_message(author = partyMembers[turn], channel = message.channel, timeout=timer)
                if (playerMove == None):
                    await client.send_message(message.channel, "You have ran out of time!")
                    #add a letter to that person
                    ghost = "GHOST"
                    numCurrentLetters = len(score[partyMembers[turn]])
                    score[partyMembers[turn]] = ghost[0:numCurrentLetters+1]
                    #make it the next player's turn
                    if (turn == len(partyMembers) - 1):
                        turn = 0
                    else:
                        turn = turn + 1
                    currentLetters = ""
                    continue
                playerHasntMoved = True
                waitedFlag = False
                while (playerHasntMoved):
                    while (not playerMove.content.startswith("ghost.first") and not playerMove.content.startswith("ghost.left") and not playerMove.content.startswith("ghost.right") and not playerMove.content.startswith("ghost.challenge")):
                        await client.send_message(message.channel, "Invalid command.")
                        playerMove = await client.wait_for_message(author=partyMembers[turn], channel=message.channel, timeout = timer)
                        if (playerMove == None):
                            await client.send_message(message.channel, "You have ran out of time!")
                            # add a letter to that person
                            ghost = "GHOST"
                            numCurrentLetters = len(score[partyMembers[turn]])
                            score[partyMembers[turn]] = ghost[0:numCurrentLetters + 1]
                            # make it the next player's turn
                            if (turn == len(partyMembers) - 1):
                                turn = 0
                            else:
                                turn = turn + 1
                            waitedFlag = True
                            break
                    if (waitedFlag):
                        currentLetters = ""
                        break
                    if (playerMove.content.startswith("ghost.first")):
                        if (len(currentLetters) != 0):
                            await client.send_message(message.channel, "You may only use the 'ghost.first' command to place down the first letter.")
                        else:
                            currentLetters = playerMove.content[12].lower()
                            if (turn < (len(partyMembers) - 1)):
                                turn = turn + 1
                            else:
                                turn = 0
                            playerHasntMoved = False
                    elif (playerMove.content.startswith("ghost.left")):
                        if (len(currentLetters) == 0):
                            await client.send_message(message.channel, "You must use the 'ghost.first' command to place down the first letter")
                        else:
                            currentLetters = playerMove.content[11].lower() + currentLetters
                            if (turn < (len(partyMembers) - 1)):
                                turn = turn + 1
                            else:
                                turn = 0
                            playerHasntMoved = False
                    elif (playerMove.content.startswith("ghost.right")):
                        if (len(currentLetters) == 0):
                            await client.send_message(message.channel, "You must use the 'ghost.first' command to place down the first letter")
                        else:
                            currentLetters = currentLetters + playerMove.content[12].lower()
                            if (turn < (len(partyMembers) - 1)):
                                turn = turn + 1
                            else:
                                turn = 0
                            playerHasntMoved = False
                    elif (playerMove.content.startswith("ghost.challenge")):
                        personToChallenge = 0
                        if (turn > 0):
                            personToChallenge = turn - 1
                        else:
                            personToChallenge = len(partyMembers) - 1
                        await client.send_message(message.channel, partyMembers[personToChallenge].mention + " must type in 'ghost.word exampleWord', replacing exampleWord with a word that contains the letters: " + currentLetters)
                        challengeTimeLeft = timer
                        challengeTimerMessages = []
                        def newChallengeMoveNumber():
                            return challengeMoveNumber
                        challengeMessageNumber = challengeMessageNumber + 1
                        challengeMoveNumber = challengeMoveNumber + 1
                        challengeTimerMessages.append(await client.send_message(message.channel, "You have " + str(challengeTimeLeft) + " seconds left to type in a word"))

                        async def challengeEditTimer(challengeTimeLeft, challengeMessageNumber, challengeTimerMessages, challengeMoveNumber):
                            doneRunning = False
                            while (challengeTimeLeft >= 0 and not doneRunning):
                                await client.edit_message(challengeTimerMessages[-1], "You have " + str(challengeTimeLeft) + " seconds left to place a letter!")
                                challengeTimeLeft = challengeTimeLeft - 1
                                asyncio.sleep(1)
                                if (challengeMoveNumber != newChallengeMoveNumber()):
                                    doneRunning = True

                        client.loop.create_task(challengeEditTimer(challengeTimeLeft, challengeMessageNumber, challengeTimerMessages, challengeMoveNumber))
                        challengedPlayerMove = await client.wait_for_message(author=partyMembers[personToChallenge], channel=message.channel, timeout=timer)
                        if (challengedPlayerMove == None):
                            await client.send_message(message.channel, "You have ran out of time!")
                            # add a letter to that person
                            ghost = "GHOST"
                            numCurrentLetters = len(score[partyMembers[personToChallenge]])
                            score[partyMembers[personToChallenge]] = ghost[0:numCurrentLetters + 1]
                            # make it the next player's turn
                            if (turn == len(partyMembers) - 1):
                                turn = 0
                            else:
                                turn = turn + 1
                            playerHasntMoved = False
                            currentLetters = ""
                            continue
                        challengedPlayerHasntMoved = True
                        challengeWaitedFlag = False
                        while (challengedPlayerHasntMoved):
                            while (not challengedPlayerMove.content.startswith("ghost.word")):
                                await client.send_message(message.channel, "Invalid command.")
                                challengedPlayerMove = await client.wait_for_message(author=partyMembers[personToChallenge],channel=message.channel, timeout=timer)
                                if (challengedPlayerMove == None):
                                    await client.send_message(message.channel, "You have ran out of time!")
                                    # add a letter to that person
                                    ghost = "GHOST"
                                    numCurrentLetters = len(score[partyMembers[personToChallenge]])
                                    score[partyMembers[personToChallenge]] = ghost[0:numCurrentLetters + 1]
                                    # make it the next player's turn
                                    if (turn == len(partyMembers) - 1):
                                        turn = 0
                                    else:
                                        turn = turn + 1
                                    challengeWaitedFlag = True
                                    break
                            if (challengeWaitedFlag):
                                currentLetters = ""
                                break
                            elif (challengedPlayerMove.content.startswith("ghost.word")):
                                file = open("wordlist.txt", "r")
                                foundWord = False
                                for line in file:
                                    if (challengedPlayerMove.content[11:] == line[:-1] and len(line[:-1]) >= minWordSize and currentLetters in line[:-1]):
                                        foundWord = True
                                if (foundWord == False):
                                    await client.send_message(message.channel, challengedPlayerMove.content[11:] + " is not a valid word! You get a letter")
                                    # add a letter to that person
                                    ghost = "GHOST"
                                    numCurrentLetters = len(score[partyMembers[personToChallenge]])
                                    score[partyMembers[personToChallenge]] = ghost[0:numCurrentLetters + 1]
                                    # make it the next player's turn
                                    if (turn == len(partyMembers) - 1):
                                        turn = 0
                                    else:
                                        turn = turn + 1
                                else:
                                    await client.send_message(message.channel, challengedPlayerMove.content[11:] + " is a word! " + partyMembers[turn].mention + "gets a letter!")
                                    # add a letter to that person
                                    ghost = "GHOST"
                                    numCurrentLetters = len(score[partyMembers[turn]])
                                    score[partyMembers[turn]] = ghost[0:numCurrentLetters + 1]
                                    # make it the next player's turn
                                    if (turn == len(partyMembers) - 1):
                                        turn = 0
                                    else:
                                        turn = turn + 1
                                challengedPlayerHasntMoved = False
                                playerHasntMoved = False
                                currentLetters = ""







client.run(token)