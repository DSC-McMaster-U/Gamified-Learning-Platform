# calculateRankings.py - uses certain algorithms and DS to sort and organize member points in the order to be displayed on the leaderboard

"""
Plan:
    - Query from database a custom table containing user name, user's username, and points for when Points.user_id == User.id; users can be filtered from a specific course,
      or everyone can just be given at once.
    - Maybe find some way to locally store that data somehow in records?
    - Use a balanced binary (red-black) tree to sort users by points; the keys will be the points, while the values will be lists containing (references to?) people with
      those number of points 
    - function getPlayerFromRank(rank) ->   
    - function compileLeaderboard()

"""

from math import ceil

class EmptyUserDBError(Exception):
    pass


class UserDoesNotExistError(Exception):
    pass


# A node part of a linked list, to be stored inside UserHashTable's list
class UserEntryNode():
    def __init__(self, name, username, points):
        self.name : str = name
        self.username : str = username         # Note: based on model, these are unique
        self.points : int = points
        self.nodeRef : PointsTree = None

        # Node attributes
        self.next : UserEntryNode = None

    def setPointsTree(self, pointsTree) -> None:
        self.nodeRef = pointsTree


# Hash table storing user info, using separate chaining
class UserHashTable():
    def __init__(self, numElems : int, courseID : int = None):
        self.courseID : int = None                     # Optional for if you have leaderboards within classes, remove if not needed
        self.size = 0                            # Num of elems current stored within the hash table
        self.loadFactor = 3                      # Average of two elements per self.items entry; load factor here considered as (<# items> / <capacity>) instead of (# of used slots / capacity)
        self.capacity = ceil(numElems * 1.2)     # Current size of the hash table (1.2 * the size of initially expected elem, for room for more elem; ^ capacity once table filled with average of <loadFactor> items per items entry)
        self.items = [None] * self.capacity

    def __hashingFunc(self, hashStrKey : str) -> int:
        return hash(hashStrKey) % self.capacity
    

    # Insert a new user into the leaderboard OR update a current user's info on the leaderboard (given the same username)
    def insertUser(self, userEntry : UserEntryNode) -> None:
        hashKey : str = userEntry.username
        hashIndex : int = self.__hashingFunc(hashKey)

        # No entry in hash table @ hashIndex yet...
        if self.items[hashIndex] == None:
            self.items[hashIndex] = userEntry
            self.size += 1

            self.checkTableLoad()
        else:    # If there are other nodes within this hashIndex already:
            currentNode : UserEntryNode = self.items[hashIndex]

            # Searching for an identical username entry already within this linked list, if user is already in the leaderboard...
            while currentNode != None:
                if currentNode.username == userEntry.username:
                    currentNode.name = userEntry.name
                    currentNode.points = userEntry.points
                    return
                
                currentNode = currentNode.next

            # User is not in the leaderboard; add in new linked list entry in the hash table at specified hash index
            userEntry.next = self.items[hashIndex]
            self.items[hashIndex] = userEntry
            self.size += 1

            self.checkTableLoad()

    def deleteUser(self, username : str):
        hashIndex : int = self.__hashingFunc(username) 
  
        currentNode : UserEntryNode = self.items[hashIndex]
        prevNode : UserEntryNode = None
  
        while currentNode != None: 
            if currentNode.username == username: 
                if prevNode != None: 
                    prevNode.next = currentNode.next
                else: 
                    self.items[hashIndex] = currentNode.next

                self.size -= 1
                return
            
            prevNode = currentNode 
            currentNode = currentNode.next
  
        raise UserDoesNotExistError("Cannot delete a user that doesn't exist with this username!")

    def getUser(self, username : str) -> UserEntryNode:
        hashIndex = self.__hashingFunc(username)
        currentNode : UserEntryNode = self.items[hashIndex]
  
        while currentNode != None: 
            if currentNode.username == username: 
                return currentNode
            
            currentNode = currentNode.next
  
        raise UserDoesNotExistError("The user you're trying to get doesn't exist!")

    def checkTableLoad(self):
        pass

    def resizeTable(self):
        pass


class PointsTree:
    def __init__(self):
        # General attributes for binary trees (renamed in the context of the leaderboard)
        self.points : int = None  # Node key; if tree is init with length 0, then this is just None
        self.users = []  # Node value(s)

        # Red-black tree attributes
        self.left : PointsTree = None
        self.right : PointsTree = None
        self.numChildren : int = 0   # Use this to determine index/ranking of users in nodes
        self.colour : bool = True    # for colour: true = red, false = black

        self.userEntryRef = None     # Back-reference to UserEntryNode object in hashmap

    def __treeSize(self):
        if self.points == None:
            return 0
        
        return self.numChildren

    def __isNodeRed(self):
        if self.points == None:
            return False
        
        return self.colour

    def getUsersByPoints(self, points : int) -> list:
        if self.points == None:
            return None
        
        if points > self.points:
            return self.right.getUsersByPoints(points)
        
        if points < self.points:
            return self.left.getUsersByPoints(points)
        
        return self.users
    
    # Returns a tuple of the highest-scoring users currently in DB, along with their point count (points, users)
    def getTopRankUsers(self) -> tuple[int, list]:
        if self.points == None:
            raise EmptyUserDBError("There are no users stored within the database yet! Register a user first.")
        
        if self.right == None:
            return (self.points, self.users)  
        
        return self.right.getTopRankUsers()
    
    def getRankByUsername(self, username : str):
        pass

    # Note to self: remember to set reference between both nodes after inserting
    def insertUser(self, userEntry : UserEntryNode) -> None:
        if self.points == None:
            self.userEntryRef = userEntry
            self.userEntryRef.setPointsTree(self)

            self.points = self.userEntryRef.points

        pass   # WIP

    def deleteUser(self, username : str):
        pass

    
