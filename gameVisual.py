import pyglet 
from pyglet import shapes, text
from pyglet.window import mouse
import numpy as np

from dominoGame import DominoGame

bgStream = open('img/gamebg.jpg', 'rb')
bgImage = pyglet.image.load('img/gamebg.jpg', file=bgStream)

background = pyglet.graphics.Group(order=0)
foreground = pyglet.graphics.Group(order=1)
playDeckLayer = pyglet.graphics.Group(order=2)
gameHUD = pyglet.graphics.Group(order=3)

windowDim = 750
frameDim = 500
frameDim2 = 370
off = 15
off2 = 65
deckStartIdx = 55

boardScale = 0.22
deckScale = 0.66

new_window = pyglet.window.Window(windowDim, windowDim) 
batch = pyglet.graphics.Batch()

selectedDomino = None
playerDeck = None
boardDominos = None
controls  = None
action = -1
success = False 

headPosition = [ (windowDim-200)//2, (windowDim-200)//2 ]
# TailPosition = [ 375, 300 ]

class Title:
    def __init__(self, x, y, label):
        self.x = x
        self.y = y

        self.title = pyglet.text.Label(label,
                          font_name='Times New Roman',
                          font_size=36,
                          anchor_x="center",
                          anchor_y="center",
                          x=x, y=y, group=foreground, batch=batch)

    def draw(self):
        self.rectangle.draw()
        self.label.draw()
    
class Button:
    def __init__(self, x, y, width, height, label_text, color, borderColor, on_click_callback):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.label = text.Label(label_text, font_size=20, x=x + width // 2, y=y + height // 2,
                                anchor_x='center', anchor_y='center')
        self.rectangle = shapes.BorderedRectangle(x, y, width, height, 10, color, borderColor, group=gameHUD)
        self.on_click_callback = on_click_callback

    def draw(self):
        self.rectangle.draw()
        self.label.draw()

    def is_clicked(self, mx, my):
        return self.x <= mx <= self.x + self.width and \
               self.y <= my <= self.y + self.height

class DominoShape:
    def __init__(self, topNum, bottomNum, step, count, on_click_callback):
        self.x = step * 90.5 + (windowDim - (count) * 90.5)//2
        self.y = 15
        self.width = 82.5
        self.height = 166.67
        self.topNum = topNum
        self.bottomNum = bottomNum
        self.dominoStream = open(f'img/dominos/{topNum}_{bottomNum}.png', 'rb')
        self.dominoImage = pyglet.image.load(f'img/dominos/{topNum}_{bottomNum}.png', file=self.dominoStream)
        self.dominoSprite = pyglet.sprite.Sprite(img=self.dominoImage, group=playDeckLayer, x= self.x, y=self.y)
        self.on_click_callback = on_click_callback

    def playedDomino(self, position):
        # print("top:", self.topNum, "bottom:", self.bottomNum)
        self.x = position[0]
        self.y = position[1]
        self.on_click_callback = None
        self.width = self.width * 0.22
        self.height = self.height * 0.22

    def is_clicked(self, mx, my):
        return self.x <= mx <= self.x + self.width and \
            self.y <= my <= self.y + self.height
            
    def draw(self):
        self.dominoSprite.scale = deckScale
        self.dominoSprite.draw()
        
    def drawBoard(self, idx, lastTop, lastBottom):
        
        self.dominoSprite = pyglet.sprite.Sprite(img=self.dominoImage, group=playDeckLayer, x= self.x + ((idx * 50) if idx < 5 else 200), y=self.y + ((idx * 50) if (idx >= 5 and idx < 10) else self.y ))
        self.dominoSprite.scale = boardScale
        
        # if action == 1 and self.topNum == lastTop and self.bottomNum != lastBottom:
        self.dominoSprite.rotation = -90 
        
        # elif action == 0 and self.bottomNum == lastTop:
        if action == 1 and (self.bottomNum == lastBottom):
            # print("lastTop:", lastTop, "lastBottom:", lastBottom, "currentTop:", self.topNum, "currentBottom:", self.bottomNum)
            self.bottomNum = lastBottom
            self.topNum = lastTop
            self.dominoSprite.rotation = 90
        #     self.dominoSprite.rotation = 90
        
        self.dominoSprite.draw()
            
class DominoShapes:
    def __init__(self, playerDeck):
        self.playerDeck =  np.array(playerDeck, dtype=np.dtype(DominoShape))
        self.count = len(self.playerDeck)
    
    def updateList(self, idx):
        self.playerDeck[idx].dominoSprite.delete()
        card = self.playerDeck[idx]
        mask = np.ones(self.count, dtype=bool)
        mask[[idx]] = False
        self.playerDeck = self.playerDeck[mask,...]
        self.count = self.count - 1
        return card
    
    def draw(self):
        for dominoShape in self.playerDeck:
            dominoShape.draw()

class Board:
    def __init__(self):
        self.boardDominos = np.array([], dtype=np.dtype(DominoShape))
        self.count = 0
        
    def addDomino(self, direction, domino: DominoShape):
        if direction == 1:
            self.boardDominos = np.append(self.boardDominos, domino) # 'numpy.ndarray' object has no attribute 'append'
        else:
            self.boardDominos = np.append(domino, self.boardDominos)
            
        self.count = self.count + 1
        
    def draw(self):
        lastDomino = self.boardDominos[0]
        for idx, dominoShape in enumerate(self.boardDominos):
            dominoShape.drawBoard(idx, lastDomino.topNum, lastDomino.bottomNum)
            lastDomino = dominoShape

class DominoTable:
    def __init__(self, on_click_callback=None):

        self.frame = shapes.Box(x = 125, y = 125, width=frameDim, height=frameDim, color=(130, 53, 31), thickness=15, batch = batch, group=foreground)
        self.innerPanel = shapes.Box(x = 125 + off, y = 125 + off, width=frameDim-2*off, height=frameDim-2*off, color=(93, 41, 6), thickness=50, batch = batch, group=foreground)
        self.frame2 = shapes.Box(x = 125 + off2, y = 125 + off2, width=frameDim2, height=frameDim2, color=(130, 53, 31), thickness=10, batch = batch, group=foreground)
        self.bottomLeftCup = shapes.Circle(170, 170, 24, color=(0, 0, 0), batch=batch, group=foreground)
        self.bottomRightCup = shapes.Circle(580, 170, 24, color=(0, 0, 0), batch=batch, group=foreground)
        self.topRightCup = shapes.Circle(580, 210 + frameDim2, 24, color=(0, 0, 0), batch=batch, group=foreground)
        self.topLeftCup = shapes.Circle(170, 210 + frameDim2, 24, color=(0, 0, 0), batch=batch, group=foreground)

        self.leftStand = shapes.Line((windowDim-frameDim2-20)//2, 450, (windowDim-frameDim2-20)//2, 300, 5, color=(130, 53, 31, 255), batch=batch, group=foreground)
        self.rightStand = shapes.Line((windowDim+frameDim2+20)//2, 450, (windowDim+frameDim2+20)//2, 300, 5, color=(130, 53, 31, 255), batch=batch, group=foreground)
        self.topStand = shapes.Line( 475, (windowDim+frameDim2+20)//2, 275, (windowDim+frameDim2+20)//2, 5, color=(130, 53, 31, 255), batch=batch, group=foreground)
        self.bottomStand = shapes.Line( 475, 180, 275, 180, 5, color=(130, 53, 31, 255), batch=batch, group=foreground)

        self.flatformImg = pyglet.sprite.Sprite(img=bgImage, batch=batch, group=background, x=125, y=125)
        self.flatformImg.scale = 0.66
        
        self.on_click_callback = on_click_callback
        
title = Title(375, (windowDim - 90), 'El Dominó')
dominoTable = DominoTable()

gameInstance = DominoGame()


def visualRefresh():
    new_window.clear() 
    batch.draw()    # Draw all shapes in the batch

def initializeGame():
    global gameInstance
    global controls
    global action
    global playerDeck
    global boardDominos
    global selectedDomino
    
    if gameInstance.gameState == -1:
        gameInstance = DominoGame(1)
    else:
        gameInstance.gameState = 1
            
    action = -1
    selectedDomino = -1
            
    [ dirtyDeck, count ] = gameInstance.returnPlayerDeck()
    cleanedDeck = [ DominoShape(x.top, x.bottom, idx, count, gameInstance.ctrlPlayer) for idx, x in enumerate(dirtyDeck) ]
    playerDeck = DominoShapes(cleanedDeck)
    boardDominos = Board()
    
    controls = [
        Button(25, 250, 80, 80, "Left", (0, 78, 241), (0, 78, 241), gameInstance.ctrlPlayer),
        Button(645, 250, 80, 80, "Right", (137, 207, 240), (137, 207, 240), gameInstance.ctrlPlayer),
        Button(25, 350, 80, 80, "Skip", (255, 128, 0), (150, 128, 0), gameInstance.nextTurn),
        Button(645, 350, 80, 80, "Quit", (200,0,0), (100,0,0), gameInstance.gameOver)
    ]

startButton = Button((windowDim-200)//2, (windowDim-100)//2, 200, 80, "Start Game", (200,0,0), (100,0,0), initializeGame)
restartButton = Button((windowDim-200)//2, (windowDim-100)//2, 200, 80, "Try Again!", (200,0,0), (100,0,0), initializeGame)

@new_window.event 
def on_draw(): 
    global gameInstance
    global boardDominos
    global playerDeck
    global action
    global selectedDomino
    global success
    
    visualRefresh()   # Draw all shapes in the batch
    
    match gameInstance.gameState:
        case 0: 
            startButton.draw()
        case 1:
            for button in controls:
                button.draw()
            
            playerDeck.draw()
            if boardDominos.count > 0:
                boardDominos.draw()   
            
            if selectedDomino != -1:
                match action:
                    case 0:
                        # print("status:", success, "head")
                        action = -1
                        success = False
                        selectedDomino = -1
                    case 1:
                        # print("status:", success, "tail")
                        action = -1
                        success = False
                        selectedDomino = -1
                    case _:
                        # print("other")
                        pass
        case -1:
            restartButton.draw()
   
def update(dt):
    # TODO: deck load animation
    # TODO: update deck visual (on click)
    global gameInstance
    global boardDominos
    global playerDeck
    global action
    global selectedDomino
    global success

    visualRefresh() 
    
    if not gameInstance:
        return
    if not playerDeck:
        return

    if gameInstance.gameover_:
        pass
    elif gameInstance.playerId != 0:
        gameInstance.nextTurn()
        pass
    elif success:
        gameInstance.nextTurn()
        # print("Front Size:", len(playerDeck.playerDeck), "Board Size:", len(boardDominos.boardDominos))
        pass
        
    playerDeck.draw()
    
    if boardDominos.count > 0:
        boardDominos.draw()
        
            
@new_window.event
def on_mouse_press(x, y, button, modifiers):
    global playerDeck
    global boardDominos
    global selectedDomino
    global action
    global success

    if button == mouse.LEFT:
        match gameInstance.gameState:
            case -1:
                if restartButton.is_clicked(x,y):
                    restartButton.on_click_callback()
            case 0:
                if startButton.is_clicked(x, y):
                    startButton.on_click_callback()                
            case 1:   
                for idx, selection in enumerate(controls):
                    if selection.is_clicked(x, y):
                        match idx:                                
                            case 2:
                                if gameInstance.playerId != 0:
                                    return
                                selection.on_click_callback()
                                
                            case 3: # quit
                                selection.on_click_callback()                                
                            case _: 
                                if gameInstance.playerId != 0:
                                    gameInstance.nextTurn()
                                    return
                                if selectedDomino != -1:
                                    
                                    selection.on_click_callback(idx, selectedDomino)
                                    success = gameInstance.success
                                                                    
                                    action = idx if success else -1
                                    selectedDomino = -1 if not success else selectedDomino
                                 
                
        # TODO: handle domino clicked (selected)
        if gameInstance.gameState == 1 and gameInstance.playerId == 0:
            for idx, domino in enumerate(playerDeck.playerDeck):
                if domino.is_clicked(x,y):
                    selectedDomino = idx
                    print("Selected Domino:", selectedDomino)
                    if boardDominos.count == 0:
                        domino.on_click_callback(0, idx)
                        success = gameInstance.success
                        action = 0
                        pass
        
        if success:
            addedDomino = playerDeck.updateList(selectedDomino)
            addedDomino.playedDomino(headPosition)
            boardDominos.addDomino(action, addedDomino)
        

pyglet.clock.schedule_interval(update, 1/60.0) # Update 60 times per second

pyglet.app.run()