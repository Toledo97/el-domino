import json
from random import randint as rand
import os

RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
MAGENTA = "\033[95m"
CYAN = "\033[96m"
RESET = "\033[0m"

class DominoGame:                  
    def __init__(self, defaultState = 0):
        self.playerId = 0
        self.gameState = defaultState
        self.players = []
        self.dominos = []
        self.head = None
        self.tail = None
        self.count = [0,0,0,0,0,0,0]
        self.gameover_ = False
        self.success = False
        self._loadDominos()
        self._addPlayers()    
                
    def _loadDominos(self):
        with open('./domino-data/dominos.json', 'r') as file:
            data = json.load(file)
            for domino in data['dominos']:
                self.dominos.append(self.DominoList(domino[0],domino[1]))
    
    def _makeDeck(self): 
        ct = 0
        deck = []
        while ct < 7:
            size = len(self.dominos)
            domino = self.dominos.pop(rand(0, size-1))
            deck.append(domino)
            ct = ct + 1
            
        deck.sort(key=lambda domino: domino.top, reverse=True)
        return deck
        # for domino in deck:
        #     print(domino.top, domino.bottom)

    def _addPlayers(self):
        for i in range(4):
            self._addPlayer(i)
        print(4, "Players Added!")

    def _addPlayer(self, id):
        if len(self.dominos) == 0:
            print("Player", id, "cannot play!")
            return
            
        player = self.Player(id)
        player.deck = self._makeDeck()
        self.players.append(player)
     
    def _updateDominoCounter(self, top, bottom):
        self.count[bottom] = self.count[bottom] + 1
        self.count[top] = self.count[top] + 1 if top != bottom else self.count[top]
                      
    def _addHead(self, id , idx):
        player = self.players[id]
        newDomino = player.deck[idx]  
        flag = newDomino.addDominoHead(self.head)
        self.success = False
        
        if flag != 0:
            self.head = newDomino
            self.success = True
            
            if self.tail == None:
                self.tail = self.head
            
            self._updateDominoCounter(newDomino.top, newDomino.bottom)
            
            player.removeDomino(idx)
            # print("backend size", len(player.deck))
            if flag == 2:
                return flag    
            
            self.head.dead = True if 7 == self.count[self.head.top] else False
            return -1 if 7 == self.count[self.tail.bottom] else flag  
    
    def _addTail(self, id, idx):
        player = self.players[id]
        newDomino = player.deck[idx]
        
        self.success = False
        flag = newDomino.addDominoTail(self.tail)  
        
        if flag != 0:
            self.tail = newDomino
            self.success = True
            
            if self.head == None:
                self.head = self.tail
            
            self._updateDominoCounter(newDomino.top, newDomino.bottom)

            player.removeDomino(idx)

            if flag == 2:
                return flag

            self.tail.dead = True if 7 == self.count[self.tail.bottom] else False
            return -1 if 7 == self.count[self.head.top] else flag

    def _pickDomino(self, id):
        player = self.players[id]
        head, tail = self.head, self.tail
        flag = 0
        
        for idx, domino in enumerate(player.deck):
            if head.top == domino.top or head.top == domino.bottom:
                flag =  self.ctrlPlayer(id, 0, idx)
                break
            elif tail.bottom == domino.top or tail.bottom == domino.bottom:
                flag = self.ctrlPlayer(id, 1, idx)
                break
            elif 1 == 0:
                flag = self.ctrlPlayer(id, 3)
                break
            
        self.ctrlPlayer(id, 2)
        
        os.system('clear')
        self.printDominosPlayed()
        return flag
        
    def returnPlayerDeck(self):
        deck = self.players[0].deck
        return deck, len(deck)  
    
    def nextTurn(self):
        # if self.playerId == 0: print("Ending Turn",self.playerId)
        self.playerId = self.playerId + 1
        self.playerId = self.playerId % 4
        self.success = False
    
    def start(self):
        player = 0

        while self.concedeCount < 4:
            flag = 0
            if player == 0:
                self.printPlayerDominos(player)
                choice = self.getAction()
                
                while choice > 3 and choice < 7:
                    flag = self.ctrlPlayer(player, choice)
                    # os.system('clear')
                    choice = self.getAction()
                
                os.system('clear')
                
                if choice < 2:
                    self.printPlayerDominos(player)
                    self.printDominosPlayed()
                    DominoNumber = self.getDomino()
                    flag = self.ctrlPlayer(player, choice, DominoNumber) 
                    self.printDominosPlayed()
                elif choice == 2:
                    continue
                else:
                    flag = self.ctrlPlayer(player, choice)
                         
            else: # ai makes a decision
                flag = self._pickDomino(player)
            
            if len(self.players[player].deck) == 0:
                os.system('clear')
                self.printDominosPlayed()
                print("Player", player, "Won!")
                break
            elif flag == -1: # no more moves, determine winner ; both deadends
                self.printDominosPlayed()
                print("Game Over!") 
                break
            
            player = (player + 1) % 4 
            
        else:
            self.printDominosPlayed()
            print("Game Over!")

    def gameOver(self):
        self.gameover_ = True
        self.gameState = -1
        print("Game Over!")

    def ctrlPlayer(self, action, dominoIdx = 0):
        selection = {0:"head", 1:"tail", 2:"skip", 3:"end"}
        
        match selection[action]:
            case "head":
                return self._addHead(self.playerId, dominoIdx)
            case "tail":
                return self._addTail(self.playerId, dominoIdx)
            case _:
                return
        
    class Player:
        def __init__(self, id):
            self.id = id
            self.concede = False
            self.deck = []
            self.score = 0
        
        def _concede(self):
            self.concede = True
        
        def viewDomino(self, idx):
            print(self.deck[idx])
            return self.deck[idx]
        
        def removeDomino(self, idx):
            domino = self.deck.pop(idx)            
            return domino
        
        def calcScore(self):
            for domino in self.deck:
                score = score + domino.top + domino.bottom        
            
    class DominoList:
        def __init__(self, top, bottom, prev = None, next = None):
            self.top = top
            self.bottom = bottom
            self.TopLink = next
            self.BottomLink = prev
            self.dead = False # deadend
            
        def _flipDomino(self):
            prev = self.top
            self.top = self.bottom
            self.bottom = prev
        
        def addDominoHead(self, head): ## add deadend logic
            if head == None: 
                return 2
            elif head.top == self.bottom:
                self.BottomLink = head
                head.TopLink = self
                return 1
            elif head.top == self.top:
                self.BottomLink = head
                head.TopLink = self
                self._flipDomino()
                return 1
            else:
                print(f'Cannot add [{self.top}, {self.bottom}] to Head')
                return 0
                
        def addDominoTail(self, tail): ## add deadend logic
            if tail == None:
                return 2
            elif tail.bottom == self.top:
                tail.BottomLink = self
                self.TopLink = tail
                return 1
            elif tail.bottom == self.bottom:
                tail.BottomLink = self
                self.TopLink = tail
                self._flipDomino()
                return 1
            else:
                print(f'Cannot add [{self.top}, {self.bottom}] to Tail')
                return 0    
       