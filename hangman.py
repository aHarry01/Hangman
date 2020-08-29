from tkinter import *
import PIL.Image, PIL.ImageTk
import time
import random

class Screen():
    def __init__(self):
        self.canvas = Canvas(root, height=600, width=600, relief=RAISED, bg="white")
        self.numPlayers = 1
        self.word  = ' '
        self.progress = 0 #progress tracks how much of the man is hanged, 0 is no man
        self.lettersList = [] #a list of Letter objects, one for each character in the word
        self.player1 = ""
        self.player2 = ""

        self.entry = Entry(root, bg = 'light grey',width=35)
        self.hangmanImg = PIL.ImageTk.PhotoImage(master = self.canvas, file = "images/empty.jpg")
        self.titleImg = PIL.ImageTk.PhotoImage(master=self.canvas, file = 'images/title.png')


    def setupStartScreen(self):
        root.title("Hangman")
        self.canvas.grid()

        self.canvas.create_image((150,270), image=self.hangmanImg)
        self.canvas.create_image((300,5), anchor = N, image=self.titleImg)

        quitButton = Button(root,text = "Quit",relief=RAISED,bg = 'grey80', font=('Arial',13),width = 6, command=root.destroy)
        quitButton_window = self.canvas.create_window(295, 575, anchor=E, window=quitButton)

        restartButton = Button(root,text = "Restart",width = 6, relief=RAISED, bg = 'grey80', font=('Arial',13),command=self.restart)
        restartButton_window = self.canvas.create_window(305, 575, anchor=W, window=restartButton)

        self.chooseNumPlayers()


    #if numPlayers = 2, the players' names and the word chosen by player 1 must be passed into this function
    #if numPlayers = 1, the function will call generateRandomWord() to choose a word automatically
    def setupMainGameScreen(self, numPlayers,player1Name = "", player2Name = "", word = "",tempCanvas=None):
        self.numPlayers = numPlayers
        self.canvas.delete(self.howManyPrompt)
        self.canvas.delete(self.player1Button)
        self.canvas.delete(self.player2Button)
        entry_window = self.canvas.create_window(300, 495,window=self.entry)

        if numPlayers == 1:
            generateRandomWord()
        else:
            self.player1 = player1Name
            self.player2 = player2Name
            self.word = word
            tempCanvas.destroy()

        
        self.missed = self.canvas.create_text(280, 125, font = ('Arial', 14), text = 'Missed Letters:',anchor=NW)
        self.canvas.create_text(300,450, font = ('Arial', 14), text = 'Guess a character', tag = 'prompt')
        self.enterButton = Button(root,text= 'Enter',bg = 'grey80', relief=RAISED,font=('Arial',13),command=lambda:checkGuess())
        enter_window = self.canvas.create_window(300,535,window=self.enterButton)
        self.displayLines()
    
        
    #prompts the user to choose singleplayer or 2 player mode
    def chooseNumPlayers(self):
        self.howManyPrompt = self.canvas.create_text(440, 225,font = ('Arial', 20),text = 'How many players?')
        onePlayer = Button(root,text = '1',font = ('Arial', 20),relief=RAISED,bg = 'grey80',command=lambda:self.setupMainGameScreen(1))
        twoPlayer = Button(root,text = '2',font = ('Arial', 20),relief=RAISED,bg = 'grey80',command=lambda:self.getPlayerNames())
        self.player1Button = self.canvas.create_window(390,300,window=onePlayer)
        self.player2Button = self.canvas.create_window(490,300,window=twoPlayer)

    #if 2 player game, set up player names and the word that player 2 will guess
    def getPlayerNames(self):
        self.canvas.delete(self.howManyPrompt)
        self.canvas.delete(self.player1Button)
        self.canvas.delete(self.player2Button)

        tempCanvas = Canvas(root, height=350, width=350, relief=RAISED, bg="white", highlightthickness = 0) #canvas just for the stuff to get player names, easy to delete everything at once this way
        tempCanvas.place(x=250,y=150)
        root.lift(tempCanvas) #make absolute sure that tempCanvas is on top & visible
        
        entryPlayerOneName = Entry(root, bg = 'light grey',width = 20)
        entryPlayerTwoName = Entry(root, bg = "light grey",width = 20)
        validationCmd = root.register(wordValidation)
        entryWordToGuess = Entry(root, bg = "light grey",width = 20, validate="key", validatecommand=(validationCmd, '%P'))

        tempCanvas.create_window(250, 25,window=entryPlayerOneName)
        tempCanvas.create_window(250, 150,window=entryPlayerTwoName)
        tempCanvas.create_window(250, 275,window=entryWordToGuess)

        tempCanvas.create_text(1, 25, font = ('Arial', 12), text = 'Player 1 Name:', anchor=W)
        tempCanvas.create_text(1, 150, font = ('Arial', 12), text = 'Player 2 Name:', anchor=W)
        tempCanvas.create_text(1, 275, font = ('Arial', 12), text = 'Word for P2 to Guess:', anchor=W)


        enterButton = Button(root,text = "Enter",relief=RAISED,bg = 'grey80', font=('Arial',13),width = 6,
                             command=lambda:self.setupMainGameScreen(2,entryPlayerOneName.get(), entryPlayerTwoName.get(), entryWordToGuess.get().lower(), tempCanvas))
        tempCanvas.create_window(175, 325, window=enterButton)


    #displays the empty lines of the word
    def displayLines(self):
        numOfChars = len(self.word)
        #fail safe in case user didn't put anything in the word box
        if numOfChars == 0:
            self.canvas.itemconfig('prompt', text= "", font=('Arial',25))#change guess a character text
            self.dispErrorMessage(self.player1 + " never entered a word for " + self.player2 + " to guess! Restarting...", duration=4)            
            self.restart()

        else:
            lineLength = (320.0/numOfChars) - ((320.0/numOfChars) * .15) #length of each line segment
            index = 0
            for char in self.word:
                if char != " ": #if the user inputs multiple words, don't want to make a blank line for a space
                    x1 = 280 + (320.0/numOfChars)*index
                    x2 = x1 + lineLength
                    newLetter = Letter(char,x1,300, x2)
                    self.lettersList.append(newLetter)

                index += 1

    #updates the missed letters on the screen
    #returns False if the given letter was already in the missed letters box, otherwise returns True
    def updateMissedLetters(self, letter):
        mLetters = screen.canvas.itemcget(self.missed, 'text') #get text in text object missed
        mLetters = mLetters[15:] #remove the first 15 because they are the title 'Missed Letters:'
        if letter in mLetters:
            return False
        else:
            missingText = "Missed Letters: " + mLetters + letter + ' '
            self.canvas.itemconfigure(self.missed, text = missingText)
            return True

    def addBodyPart(self):
        files = ['images/head.jpg','images/body.jpg','images/leg1.jpg','images/leg2.jpg','images/arm1.jpg',
                 'images/hangman.jpg','images/mouth.jpg', 'images/eye.jpg', 'images/dead.jpg']
        newFile = files[self.progress]
        self.progress += 1
        self.hangmanImg = PIL.ImageTk.PhotoImage(master=self.canvas,file = newFile)
        self.canvas.create_image((150,270),image=self.hangmanImg)

    #shows an error message on the screen for duration seconds, then erases it
    def dispErrorMessage(self, msg, duration=1):
        errorMessage = self.canvas.create_text(300,475, font = ('Arial', 14), text = msg)
        root.update_idletasks()
        time.sleep(duration)
        self.entry.delete(0,END)
        self.canvas.delete(errorMessage)

    def loseScreen(self):
        loseMessage = "YOU LOSE"
        if (self.player1 != ""):
            loseMessage = self.player1 + " won the game!"
        
        self.canvas.itemconfig('prompt', text= loseMessage, font=('Arial',25))#change guess a character text
        frgnd = screen.enterButton.cget('foreground')
        self.enterButton.config(state=DISABLED,disabledforeground=frgnd)
        self.canvas.create_text(440, 225,font = ('Arial', 15),text = 'Correct answer was ' + self.word)

    def winScreen(self):
        frgnd = screen.enterButton.cget('foreground')
        self.enterButton.config(state=DISABLED,disabledforeground=frgnd)
        winMessage = "YOU WIN"
        if (self.player2 != ""):
            winMessage = self.player2 + " won the game!"
        self.canvas.itemconfig('prompt', text= winMessage, font=('Arial',25))#change guess a character text

    def restart(self):
        self.canvas.destroy()
        global screen #if you don't use the global keyword, then it won't actually change the global screen variable in the next line
        screen = Screen() #make a brand new Screen object - starting from a blank slate here!!
        screen.setupStartScreen()


#a character in the world that is being guessed
class Letter():
    def __init__(self, char, x1, y, x2, visible = False, guessed = False):
        self.char = char
        self.x1 = x1
        self.y = y
        self.x2 = x2
        self.visible= visible
        self.guessed = guessed
        self.drawLine()

    #draw blank line on the screen with no letter above it
    def drawLine(self):
        screen.canvas.create_line(self.x1, self.y,self.x2,self.y)

    #draws the character on the screen in its proper position
    def drawLetter(self):
        self.visible = True
        middle = (self.x1 + self.x2)/2
        screen.canvas.create_text(middle,self.y, text = self.char, anchor=S, font=('Arial', 20))

def checkGuess():
    guessed = screen.entry.get().rstrip().lower()
    if len(guessed) > 1:
        screen.dispErrorMessage("Must be a single character")

    elif guessed not in screen.word:
        isAlreadyGuessed = screen.updateMissedLetters(guessed)
        
        if not isAlreadyGuessed: 
            screen.dispErrorMessage("Already guessed this character!")
        else:
            screen.addBodyPart()

    else:
        #find letter in lettersList
        index = 0
        for Letter in screen.lettersList:
            if Letter.char == guessed:
                if screen.lettersList[index].visible == True:
                    screen.dispErrorMessage("Already guessed this character!")
                    break #no need to keep going to look for other occurences of this character bc it was already guessed
                else:
                    screen.lettersList[index].drawLetter()
            index += 1
    screen.entry.delete(0,END)
    winLose()
    
#choose a random word from a text file of words and saves it in screen.word
def generateRandomWord():
        f = open("words.txt",'r')
        possibleWords = f.readlines()
        screen.word = random.choice(possibleWords).rstrip() #will end in \n so have to take out the rightmost white space
        while len(screen.word) > 15 or len(screen.word) < 3: #words longer than 15 letters are very hard to guess and, honestly, mess up the formatting
            screen.word = random.choice(possibleWords).rstrip()


#checks if game is won or lost and if so calls appropriate function
def winLose():
    if screen.progress == 9:
        screen.loseScreen()

    for letter in screen.lettersList:
        if letter.visible == False:
            return False
    #if it didn't return False during the loop, that means that all the letters are visible and the playwer won
    screen.winScreen()

#if new character is typed: checks to make sure that the word entered in a 2 player game is 15 or fewer characters
#TO DO if trying to enter, checks to make sure there is something there (not 0 letters)
#text = the string the user is trying to type into the entry box
def wordValidation(text):
    isTextTooLong = (len(text) > 15)
    if isTextTooLong:
        screen.dispErrorMessage("Word must have less than 15 characters.")
    return not isTextTooLong
    
   
root = Tk()
screen = Screen()
screen.setupStartScreen()

root.mainloop()
