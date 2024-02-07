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
from enum import Enum
from app.src.models import User, user_course, Course, Points, db, Subject
# from app.src.auth import db
# from app.src.app import app
from sqlalchemy import text

class UserDBError(Exception):
    pass


class UserDoesNotExistError(Exception):
    pass


class RBTreeColour(Enum):
    BLACK = "black"
    RED = "red"


# A node part of a linked list, to be stored inside UserHashTable's list
class UserEntryNode:
    def __init__(self, name, username, points):
        self.name: str = name
        self.username: str = username  # Note: based on model, these are unique
        self.points: int = points
        self.nodeRef: PointsTree = None

        # Node attributes
        self.next: UserEntryNode = None

    def setPointsTree(self, pointsTree) -> None:
        self.nodeRef = pointsTree


# Hash table storing user info, using separate chaining
class UserHashTable:
    def __init__(self, numElems: int, courseID: int = None):
        self.courseID: int = None  # Optional for if you have leaderboards within classes, remove if not needed
        self.size = 0  # Num of elems current stored within the hash table
        self.loadFactor = 3  # Average of two elements per self.items entry; load factor here considered as (<# items> / <capacity>) instead of (# of used slots / capacity)
        self.capacity = ceil(
            numElems * 1.2
        )  # Current size of the hash table (1.2 * the size of initially expected elem, for room for more elem; ^ capacity once table filled with average of <loadFactor> items per items entry)
        self.items = [None] * self.capacity

    def __hashingFunc(self, hashStrKey: str) -> int:
        return hash(hashStrKey) % self.capacity

    # Insert a new user into the leaderboard OR update a current user's info on the leaderboard (given the same username), returns None if inserting new user or old points (int) if updating current user's points
    def insertUser(self, userEntry: UserEntryNode) -> int:
        hashKey: str = userEntry.username
        hashIndex: int = self.__hashingFunc(hashKey)

        # No entry in hash table @ hashIndex yet...
        if self.items[hashIndex] is None:
            self.items[hashIndex] = userEntry
            self.size += 1

            self.checkTableLoad()
        else:  # If there are other nodes within this hashIndex already:
            currentNode: UserEntryNode = self.items[hashIndex]

            # Searching for an identical username entry already within this linked list, if user is already in the leaderboard...
            while currentNode is not None:
                if currentNode.username == userEntry.username:
                    oldPoints = currentNode.points
                    currentNode.name = userEntry.name
                    currentNode.points = userEntry.points

                    if currentNode.points != oldPoints:
                        return oldPoints  # Return previous points in order to search through RB tree, delete previous entry, and recalculate rankings

                    return None  # No change in points; return None

                currentNode = currentNode.next

            # User is not in the leaderboard; add in new linked list entry in the hash table at specified hash index
            userEntry.next = self.items[hashIndex]
            self.items[hashIndex] = userEntry
            self.size += 1

            self.checkTableLoad()

            return None

    def deleteUser(self, username: str) -> None:
        hashIndex: int = self.__hashingFunc(username)

        currentNode: UserEntryNode = self.items[hashIndex]
        prevNode: UserEntryNode = None

        while currentNode is not None:
            if currentNode.username == username:
                if prevNode is not None:
                    prevNode.next = currentNode.next
                else:
                    self.items[hashIndex] = currentNode.next

                self.size -= 1
                return

            prevNode = currentNode
            currentNode = currentNode.next

        raise UserDoesNotExistError(
            "Cannot delete a user that doesn't exist with this username!"
        )

    def getUser(self, username: str) -> UserEntryNode:
        hashIndex = self.__hashingFunc(username)
        currentNode: UserEntryNode = self.items[hashIndex]

        while currentNode is not None:
            if currentNode.username == username:
                return currentNode

            currentNode = currentNode.next

        raise UserDoesNotExistError("The user you're trying to get doesn't exist!")

    # Implement these
    def checkTableLoad(self):
        pass

    def resizeTable(self):
        pass


class PointsNode:
    def __init__(self, points, userEntryRef):
        # -- General attributes for binary trees (renamed in the context of the leaderboard) --
        # Node key; if tree is init with length 0, then this is just None
        self.points: int = points
        self.userEntryRefs: list[UserEntryNode] = [
            userEntryRef
        ]  # Node value(s), those being back-references to UserEntryNode objects in hashmap

        # -- Red-black tree attributes --
        self.left: PointsNode = None
        self.right: PointsNode = None
        self.parent: PointsNode = None  # Added in later, mostly used for only deletion
        self.numNodes: int = 1          # Number of nodes within current tree; use this to determine index/ranking of users in nodes
        self.colour: RBTreeColour = RBTreeColour.RED

    def addUserEntry(self, userEntry: UserEntryNode) -> None:
        usernamesRef = [entry.username for entry in self.userEntryRefs]

        if userEntry.username in usernamesRef:
            index = usernamesRef.index(userEntry.username)
            self.userEntryRefs[index] = userEntry
        else:
            self.userEntryRefs.append(userEntry)


class PointsTree:
    def __init__(self):
        self.root: PointsNode = None

    def __treeSize(self, node: PointsNode) -> int:
        if node is None:
            return 0

        return node.numNodes

    def isNodeRed(self, node: PointsNode) -> bool:
        if node is None:
            return False

        return node.colour == RBTreeColour.RED

    def __insertRotateLeft(self, node: PointsNode) -> PointsNode:
        rightNode: PointsNode = node.right

        node.right = rightNode.left
        if node.right is not None:
            node.right.parent = node
        rightNode.left = node
        rightNode.parent = node.parent
        node.parent = rightNode

        rightNode.colour = node.colour
        node.colour = RBTreeColour.RED
        node.numNodes = rightNode.numNodes
        rightNode.numNodes = (
            self.__treeSize(rightNode.left) + self.__treeSize(rightNode.right) + 1
        )

        return rightNode

    def __insertRotateRight(self, node: PointsNode) -> PointsNode:
        leftNode: PointsNode = node.left

        node.left = leftNode.right
        if node.left is not None:
            node.left.parent = node
        leftNode.right = node
        leftNode.parent = node.parent
        node.parent = leftNode

        leftNode.colour = node.colour
        node.colour = RBTreeColour.RED
        leftNode.numNodes = node.numNodes
        node.numNodes = self.__treeSize(node.left) + self.__treeSize(node.right) + 1

        return leftNode

    def __insertFlipColours(self, node: PointsNode) -> None:
        node.colour = RBTreeColour.RED
        node.left.colour = RBTreeColour.BLACK
        node.right.colour = RBTreeColour.BLACK

    def getUsersByPoints(self, points: int) -> list:
        return self.__getUsersByPointsAux(self.root, points)

    def __getUsersByPointsAux(self, node: PointsNode, points: int) -> list:
        if node is None:
            return None

        if points > node.points:
            return self.__getUsersByPointsAux(node.right, points)

        if points < node.points:
            return self.__getUsersByPointsAux(node.left, points)

        return node.userEntryRefs

    # Returns a tuple of the highest-scoring users currently in DB, along with their point count (points, users)
    def getMaxUsers(self, subTreeRoot=None) -> PointsNode:
        if subTreeRoot is None:
            subTreeRoot = self.root

        return self.__getMaxUsersAux(subTreeRoot)

    def __getMaxUsersAux(self, node: PointsNode) -> PointsNode:
        if node is None:
            raise UserDBError(
                "There are no users stored within the database yet! Register a user first."
            )

        if node.right is None:
            return node

        return self.__getMaxUsersAux(node.right)
    
    # Returns a tuple of the highest-scoring users currently in DB, along with their point count (points, users)
    def getMinUsers(self, subTreeRoot=None) -> PointsNode:
        if subTreeRoot is None:
            subTreeRoot = self.root
        
        return self.__getMinUsersAux(subTreeRoot)

    def __getMinUsersAux(self, node: PointsNode) -> PointsNode:
        if node is None:
            raise UserDBError(
                "There are no users stored within the database yet! Register a user first."
            )

        if node.left is None:
            return node

        return self.__getMinUsersAux(node.left)    

    def getUsersByRank(self, rank: int) -> list[UserEntryNode]:
        if self.root is None or self.__treeSize(self.root) < rank:
            raise UserDBError(
                f"The rank <{rank}> is out of range from the number of users currently stored in the leaderboard (<{self.__treeSize(self.root)}>)!"
            )

        currentNode: PointsNode = self.root
        tempRank: int = (
            self.__treeSize(self.root.right) + 1
        )  # Rank of the root node in the tree

        while currentNode is not None:
            if rank > tempRank:  # Larger rank -> left subtree
                currentNode = currentNode.left
                tempRank += self.__treeSize(currentNode.right) + 1

            elif rank < tempRank:  # Smaller rank -> right subtree
                currentNode = currentNode.right
                tempRank -= self.__treeSize(currentNode.left) + 1
            else:
                return currentNode.userEntryRefs

        raise UserDBError(
            "There's an issue with the given rank number or the tree structure (currentNode = None when it wasn't supposed to); further debugging is probably needed."
        )

    # Used in conjunction with something else to get points from username/other user data
    def getRankByPoints(self, points: int) -> int:
        if self.root is None:
            return 0

        currentNode: PointsNode = self.root
        tempRank: int = (
            self.__treeSize(self.root.right) + 1
        )  # Rank of the root node in the tree

        while currentNode is not None:
            if points < currentNode.points:
                currentNode = currentNode.left
                tempRank += self.__treeSize(currentNode.right) + 1

            elif points > currentNode.points:
                currentNode = currentNode.right
                tempRank -= self.__treeSize(currentNode.left) + 1
            else:
                return tempRank

        raise UserDBError(
            "No user is currently stored with the given amount of points!"
        )

    def insertUser(self, userEntry: UserEntryNode) -> None:
        self.root = self.__insertUserAux(self.root, userEntry)
        self.root.colour = RBTreeColour.BLACK

    def __insertUserAux(self, node: PointsNode, userEntry: UserEntryNode) -> PointsNode:
        # Adding in / modifying values in R-B tree
        if node is None:
            newNode = PointsNode(userEntry.points, userEntry)
            userEntry.setPointsTree(newNode)
            return newNode

        if userEntry.points < node.points:
            node.left = self.__insertUserAux(node.left, userEntry)
            node.left.parent = node

        elif userEntry.points > node.points:
            node.right = self.__insertUserAux(node.right, userEntry)
            node.right.parent = node

        else:
            node.addUserEntry(userEntry)

        # Maintaining R-B tree properties
        # Case 1: Current node has a right red-linked child -- left rotate
        if self.isNodeRed(node.right) and not self.isNodeRed(node.left):
            node = self.__insertRotateLeft(node)

        # Case 2: Current node and its left child both have left red-linked children -- right rotate
        if node.left is not None and all([self.isNodeRed(child) for child in [node.left, node.left.left]]):
            node = self.__insertRotateRight(node)

        # Case 3: Current node has both left and right children as red-linked -- colour-flip
        if all([self.isNodeRed(child) for child in [node.left, node.right]]):
            self.__insertFlipColours(node)

        # Recalculate numNodes
        node.numNodes = self.__treeSize(node.left) + self.__treeSize(node.right) + 1
        return node

    def deleteUser(self, userEntry: UserEntryNode):
        self.deleteUserAux(self.root, userEntry)

    # -- DELETE HELPER FUNCTIONS BASED OFF FROM HERE: https://www.programiz.com/dsa/deletion-from-a-red-black-tree --
    def deleteRBTreeFix(self, node):
        # Keeps on looping and fixing until node reaches the root of the entire tree (and is black)
        while node != self.root and node.colour == RBTreeColour.BLACK:
            # Case 1: node is left child of parent node
            if node == node.parent.left:
                siblingNode: PointsNode = node.parent.right

                # Case 1A: sibling node is red
                if siblingNode.colour == RBTreeColour.RED:
                    # Swap colours of sibling and parent
                    siblingNode.colour = RBTreeColour.BLACK
                    node.parent.colour = RBTreeColour.RED

                    # Left rotate parent
                    self.__insertRotateLeft(node.parent)
                    siblingNode = node.parent.right  # ...probably not needed

                # Case 1B: sibling has child nodes and both are black
                if (
                    all([child is not None for child in [siblingNode.left, siblingNode.right]])
                    and siblingNode.left.colour == RBTreeColour.BLACK
                    and siblingNode.right.colour == RBTreeColour.BLACK
                ):
                    # Set sibling to red and move node pointer to node's parent
                    siblingNode.colour = RBTreeColour.RED
                    node = node.parent

                # Case 1C and 1D
                else:
                    # Case 1C: sibling right child is black, but sibling left child is red
                    if siblingNode.right is not None and siblingNode.right.colour == RBTreeColour.BLACK:
                        # Swap colours of sibling and its left child to red and black, respectively
                        siblingNode.left.colour = RBTreeColour.BLACK
                        siblingNode.colour = RBTreeColour.RED

                        # Rotate sibling node (so former left child becomes new root) and assign new root of subtree as sibling node
                        siblingNode = self.__insertRotateRight(siblingNode)
                        # Note: After Case 1C, ends up in the configuration for 1D; we therefore run that case directly afterwards

                    # Case 1D (default/last case): sibling right child is red, sibling left child is black
                    siblingNode.colour = node.parent.colour  # Set sibling colour to parents colour
                    
                    # Set parent and right child of sibling to black
                    node.parent.colour = RBTreeColour.BLACK
                    siblingNode.right.colour = RBTreeColour.BLACK

                    # Left rotate node's parent, and RB fixing is finished; set node to root of tree to end while loop
                    self.__insertRotateLeft(node.parent)
                    node = self.root

            # Case 2: node is right child of parent node (same as case 1, but left <-> right)
            else:
                siblingNode = node.parent.left

                # Case 2A: sibling node is red
                if siblingNode.colour == RBTreeColour.RED:
                    # Swap colours of sibling and parent
                    siblingNode.colour = RBTreeColour.BLACK
                    node.parent.colour = RBTreeColour.RED

                    # Right rotate parent
                    self.__insertRotateRight(node.parent)
                    siblingNode = node.parent.left  # ...probably not needed

                # Case 2B: sibling has child nodes and both are black
                if (
                    all([child is not None for child in [siblingNode.left, siblingNode.right]])
                    and siblingNode.right.colour == RBTreeColour.BLACK
                    and siblingNode.left.colour == RBTreeColour.BLACK
                ):
                    # Set sibling to red and move node pointer to node's parent
                    siblingNode.colour = RBTreeColour.RED
                    node = node.parent

                # Case 2C and 2D:
                else:
                    # Case 1C: sibling left child is black, but sibling right child is red
                    if siblingNode.left is not None and siblingNode.left.colour == RBTreeColour.BLACK:
                        # Swap colours of sibling and its right child to red and black, respectively
                        siblingNode.right.colour = RBTreeColour.BLACK
                        siblingNode.colour = RBTreeColour.RED

                        # Rotate sibling node (so former right child becomes new root) and assign new root of subtree as sibling node
                        self.__insertRotateLeft(siblingNode)
                        siblingNode = node.parent.left
                        # Note: After Case 1C, ends up in the configuration for 1D; we therefore run that case directly afterwards


                    # Case 1D (default/last case): sibling right child is red, sibling left child is black
                    siblingNode.colour = node.parent.colour  # Set sibling colour to parents colour
                    
                    # Set parent and left child of sibling to black
                    node.parent.colour = RBTreeColour.BLACK
                    siblingNode.left.colour = RBTreeColour.BLACK                    

                    # Left rotate node's parent, and RB fixing is finished; set node to root of tree to end while loop
                    self.__insertRotateRight(node.parent)
                    node = self.root

        node.colour = RBTreeColour.BLACK


    def __RBOverwriteNode(self, oldNode: PointsNode, newNode: PointsNode):
        if oldNode.parent is None:
            self.root = newNode

        elif oldNode == oldNode.parent.left:
            oldNode.parent.left = newNode

        else:
            oldNode.parent.right = newNode

        # If to-be-deleted oldNode has children (newNode), then swap parents; if not, forgo this step
        if newNode is not None:
            newNode.parent = oldNode.parent

    # Node deletion
    def deleteUserAux(self, node: PointsNode, userEntry: UserEntryNode):
        tempNode: PointsNode = None

        # Search for the node in question using points keys (binary search)
        while node is not None:
            if node.points < userEntry.points:
                node = node.right

            elif node.points > userEntry.points:
                node = node.left
            
            else:
                tempNode = node
                break

        # If user entry doesn't exist anywhere, raise an error
        if tempNode is None or (userEntry.username not in [user.username for user in tempNode.userEntryRefs]):
            raise UserDBError(
                "There are no users to delete, or the user does not exist! Insert a user first."
            )

        # If to-be-deleted user shares points with another user, just delete the former and exit
        if len(tempNode.userEntryRefs) > 1:
            indexDelete = [user.username for user in tempNode.userEntryRefs].index(userEntry.username)
            tempNode.userEntryRefs.pop(indexDelete)
            return

        # If to-be-deleted user has its own node, delete it and replace it with the next appropriate node from the tree, then fix the RB Tree structure (if to-be-deleted node was originally black)
        nodeToDelete : PointsNode = tempNode
        nodeToDeleteColour : RBTreeColour = nodeToDelete.colour

        if tempNode.left is None:
            nodeToFix = tempNode.right
            self.__RBOverwriteNode(tempNode, tempNode.right)
        elif tempNode.right is None:
            nodeToFix = tempNode.left
            self.__RBOverwriteNode(tempNode, tempNode.left)
        else:
            # print(f"Min Users: {tempNode.right.points}")
            nodeToDelete = self.getMinUsers(tempNode.right)
            print(nodeToDelete.points)
            nodeToDeleteColour = nodeToDelete.colour
            nodeToFix = nodeToDelete.right

            if nodeToDelete.parent == tempNode and nodeToFix is not None:
                nodeToFix.parent = nodeToDelete
            else:
                self.__RBOverwriteNode(nodeToDelete, nodeToDelete.right)

                if tempNode.right is not None:
                    nodeToDelete.right = tempNode.right
                    nodeToDelete.right.parent = nodeToDelete

            self.__RBOverwriteNode(tempNode, nodeToDelete)

            nodeToDelete.left = tempNode.left
            nodeToDelete.left.parent = nodeToDelete
            nodeToDelete.colour = tempNode.colour
            
        # If original deleted node's colour was black and there is a replacement node (nodeToFix) to take its spot, then fix the RB tree
        if nodeToDeleteColour == RBTreeColour.BLACK and nodeToFix is not None:
            self.deleteRBTreeFix(nodeToFix)

    # Returns a dictionary structure for all ranks and their associated user data, using a modified in-order traversal on the R-B tree.
    def getAllUsers(self):
        rankings: dict = {}  # Format of dict is {<rank #>: [{name: <str>, username: <str>, points: <int>}]}

        self.__getAllUsersAux(
            rankings, self.root, self.__treeSize(self.root.right) + 1
        )

        return rankings

    def __getAllUsersAux(self, rankings: dict, node: PointsNode, rank: int = 0):
        if node is None:
            return

        tempList = []

        # Traverse to right subtree first
        rightNodeRank = (
            (rank - self.__treeSize(node.right.left) - 1)
            if (node.right is not None)
            else rank
        )
        self.__getAllUsersAux(rankings, node.right, rightNodeRank)

        # "Visit" and register current node
        for userRef in node.userEntryRefs:
            tempEntry = {
                "name": userRef.name,
                "username": userRef.username,
                "points": userRef.points,
            }
            tempList.append(tempEntry)

        rankings[rank] = tempList

        # Traverse to left subtree last
        leftNodeRank = (
            (rank + self.__treeSize(node.left.right) + 1)
            if (node.left is not None)
            else rank
        )
        self.__getAllUsersAux(rankings, node.left, leftNodeRank)


# Temporary solution until Mithun finishes his leaderboard database schema
class Leaderboard():
    def __init__(self, courseID: int = None):
        self.rankings: PointsTree = PointsTree()
        self.userInfo: UserHashTable = None
        self.userDBQuery = None
        self.courseID: int = courseID

        self.setUpLeaderboard()

    # Query from database a custom table containing user name, user's username, and points for when Points.user_id == User.id; users can be filtered from a specific course,
    # or everyone can just be given at once.
    def __queryData(self):
        if self.courseID is None:
            return db.session.query(User.name, User.username, Points.points).distinct().filter(                
                User.id == Points.user_id
            )
        else:
            return db.session.query(User.name, User.username, Points.points).distinct().filter(
                User.id == Points.user_id
            ).filter(
                user_course.c.course_id == self.courseID
            )

    # This takes a lot of time to run, due to database queries...
    def setUpLeaderboard(self):
        self.userDBQuery = self.__queryData().all()
        dbEntries: list[tuple] = self.userDBQuery
        # print(dbEntries)

        if dbEntries is not None:
            # Create UserHashTable with necessary args and insert all database query entries inside
            self.userInfo = UserHashTable(len(dbEntries), self.courseID)

            for dbEntry in dbEntries:
                userEntry = UserEntryNode(dbEntry[0], dbEntry[1], dbEntry[2])
                self.userInfo.insertUser(userEntry)
                self.rankings.insertUser(userEntry)

            print_tree(self.rankings)

        else:
            if self.courseID is not None:
                raise UserDBError("Error creating leaderboard: no users exist that are taking the specified course!")
            
            raise UserDBError("Error creating leaderboard: no users are registered within the database yet!")

    # This takes a lot of time to run, due to database queries...
    def updateLeaderboard(self):
        newQuery = self.__queryData()
        queryDiffAdded = newQuery.filter(~User.username.in_([user[1] for user in self.userDBQuery]))     # Checks if a user was added
        queryDiffRemoved = [user for user in self.userDBQuery if user not in newQuery.all()]             # Checks if a user was removed
        queryDiffChanged = newQuery.filter(
            User.username.in_([user[1] for user in self.userDBQuery])
        ).filter( 
            ~User.points.has(Points.points.in_([user[2] for user in self.userDBQuery]))
        )                                                                                                # Checks if a pre-existing user entry was modified (through points)

        dbEntriesAdded: list[tuple] = queryDiffAdded.all()
        dbEntriesRemoved: list[tuple] = queryDiffRemoved
        dbEntriesChanged: list[tuple] = queryDiffChanged.all()
        # dbEntriesChangedOld: list[tuple] = [oldEntry for oldEntry in self.userDBQuery if oldEntry[1] in [newEntry[1] for newEntry in dbEntriesChangedNew]]

        # print(f"~calcRankings Debug - Added entries: {dbEntriesAdded}")
        # print(f"~calcRankings Debug - Removed entries: {dbEntriesRemoved}")
        # print(f"~calcRankings Debug - Changed entries (new): {dbEntriesChanged}")
        # print(f"~calcRankings Debug - Changed entries (old): {dbEntriesChangedOld}")

        # Add old versions of changed user data so that old leaderboard entry is erased -- NOT NECESSARY, ALREADY IN REMOVED LIST (for some reason...?)
        # dbEntriesRemoved += dbEntriesChangedOld 

        # Add new versions of changed user data so that new leaderboard entry is added  
        dbEntriesAdded += dbEntriesChanged     

        # Checks if length of all lists here are 0; if so, then absolutely no change to leaderboard from last update/creation
        if (len(dbEntriesAdded) + len(dbEntriesRemoved)) == 0:      
            print("No users in this course were added or removed in the database from the last leaderboard update.")
        else:            
            if len(dbEntriesRemoved) > 0:
                for dbEntry in dbEntriesRemoved:
                    userEntry = self.userInfo.getUser(dbEntry[1])
                    self.userInfo.deleteUser(dbEntry[1])
                    self.rankings.deleteUser(userEntry)

            if len(dbEntriesAdded) > 0:
                for dbEntry in dbEntriesAdded:
                    userEntry = UserEntryNode(dbEntry[0], dbEntry[1], dbEntry[2])
                    self.userInfo.insertUser(userEntry)
                    self.rankings.insertUser(userEntry)

        self.userDBQuery = newQuery.all()
        print_tree(self.rankings)

    def getUsersByRank(self, rank: int):
        output = self.rankings.getUsersByRank(rank)
        return [userEntry.username for userEntry in output]

    def getRankByUser(self, username: str):
        userEntry: UserEntryNode = self.userInfo.getUser(username)
        return self.rankings.getRankByPoints(userEntry.points)

##########
    
### WIP: Finish this function based off of Mithun's leaderboard database schema    
# Set up leaderboard and sort all user entries in it, then create a database entry for the leaderboard and return the corresponding ID/primary key value
def setUpLeaderboard(courseID: int = None) -> int:
    rankings: PointsTree = PointsTree()

    if courseID is None:
        userDBQuery = db.session.query(User.name, User.username, Points.points).distinct().filter(                
            User.id == Points.user_id
        )
    else:
        userDBQuery = db.session.query(User.name, User.username, Points.points).distinct().filter(
            User.id == Points.user_id
        ).filter(
            user_course.c.course_id == courseID
        )

    dbEntries: list[tuple] = userDBQuery.all()
    # print(dbEntries)

    if dbEntries is not None:
        # Create UserHashTable with necessary args and insert all database query entries inside
        userInfo = UserHashTable(len(dbEntries), courseID)

        for dbEntry in dbEntries:
            userEntry = UserEntryNode(dbEntry[0], dbEntry[1], dbEntry[2])
            userInfo.insertUser(userEntry)
            rankings.insertUser(userEntry)

        print_tree(rankings)
        test = rankings.getAllUsers()

        # Here would be setup for the leaderboard database entry; TBD
        return 0

    else:
        if courseID is not None:
            raise UserDBError("Error creating leaderboard: no users exist that are taking the specified course!")
        
        raise UserDBError("Error creating leaderboard: no users are registered within the database yet!")


##########

# For debugging, taken from https://stackoverflow.com/questions/34012886/print-binary-tree-level-by-level-in-python; delete later
def print_tree(tree, points="points", left="left", right="right"):
    def display(root, points=points, left=left, right=right):
        """Returns list of strings, width, height, and horizontal coordinate of the root."""
        # No child.
        if getattr(root, right) is None and getattr(root, left) is None:
            line = "%s" % getattr(root, points)
            width = len(line)
            height = 1
            middle = width // 2
            return [line], width, height, middle

        # Only left child.
        if getattr(root, right) is None:
            lines, n, p, x = display(getattr(root, left))
            s = "%s" % getattr(root, points)
            u = len(s)
            first_line = (x + 1) * " " + (n - x - 1) * "_" + s
            second_line = x * " " + "/" + (n - x - 1 + u) * " "
            shifted_lines = [line + u * " " for line in lines]
            return [first_line, second_line] + shifted_lines, n + u, p + 2, n + u // 2

        # Only right child.
        if getattr(root, left) is None:
            lines, n, p, x = display(getattr(root, right))
            s = "%s" % getattr(root, points)
            u = len(s)
            first_line = s + x * "_" + (n - x) * " "
            second_line = (u + x) * " " + "\\" + (n - x - 1) * " "
            shifted_lines = [u * " " + line for line in lines]
            return [first_line, second_line] + shifted_lines, n + u, p + 2, u // 2

        # Two children.
        left, n, p, x = display(getattr(root, left))
        right, m, q, y = display(getattr(root, right))
        s = "%s" % getattr(root, points)
        u = len(s)
        first_line = (x + 1) * " " + (n - x - 1) * "_" + s + y * "_" + (m - y) * " "
        second_line = (
            x * " " + "/" + (n - x - 1 + u + y) * " " + "\\" + (m - y - 1) * " "
        )
        if p < q:
            left += [n * " "] * (q - p)
        elif q < p:
            right += [m * " "] * (p - q)
        zipped_lines = zip(left, right)
        lines = [first_line, second_line] + [a + u * " " + b for a, b in zipped_lines]
        return lines, n + m + u, max(p, q) + 2, n + u // 2

    print("~calcRankings Debug - Display Rankings R-B Tree:\n")

    lines, *_ = display(tree.root, points, left, right)
    for line in lines:
        print(line)


def debugQuery():
    new_user1 = User(
        email="testboard20@gmail.com", 
        username="test-board20", 
        name="Test1 Board",
        age=50
    )

    new_user2 = User(
        email="testboards20@gmail.com", 
        username="test-boards20", 
        name="Test2 Board",
        age=60
    )

    new_user1.set_password("Test-12345")
    new_user2.set_password("Test-12345")

    db.session.add(new_user1)
    db.session.add(new_user2)
    db.session.commit()


    # testDiff = db.session.query(User.name, User.username).select_from(test2).filter(test2. .username.in_(test1))
    # print(testDiff.all())

    db.session.query(User).delete()
    db.session.commit()

# Used for quick user and points registration within the course "course" in debugLeaderboard()
def debugAddUserAux(uniqueNum, course, points):
    new_user = User(
        email=f"testboards{uniqueNum}@gmail.com", 
        username=f"test-boards{uniqueNum}", 
        name=f"Test{uniqueNum} Board",
        age=19
    )

    new_user.set_password("Test-12345")
    course.users.append(new_user)
    db.session.add(new_user)
    db.session.commit()
    
    new_user_points = Points(
        user_id=new_user.id, 
        points=points
    )

    new_user.points = new_user_points

    db.session.add(new_user_points)
    db.session.commit()

    return new_user

# Used for quick user deletion in debugLeaderboard()
def debugDeleteUserAux(new_user):
    db.session.query(Points).filter(Points.user_id == new_user.id).delete()
    db.session.query(User).filter(User.id == new_user.id).delete()
    db.session.commit()

def debugLeaderboard():
    # This will become outdated (using the Leaderboard class), change in the future
    #### DATABASE SET UP ####
    new_course = Course(
        name="Organic Chemistry",
        subject_type=Subject.CHEMISTRY
    )

    db.session.add(new_course)
    db.session.commit()

    # Add in a whole bunch of users with different points
    new_user1 = debugAddUserAux(1, new_course, 50)
    new_user2 = debugAddUserAux(2, new_course, 25)
    new_user3 = debugAddUserAux(3, new_course, 60)   
    new_user4 = debugAddUserAux(4, new_course, 55)   
    new_user5 = debugAddUserAux(5, new_course, 90)   
    new_user6 = debugAddUserAux(6, new_course, 85)   

    #### CLASS TESTING ####
    testLeaderboard = Leaderboard(new_course.id)

    # Testing deletion and additions of users from course (and/or database)
    debugDeleteUserAux(new_user4)
    new_user7 = debugAddUserAux(7, new_course, 62)   
    new_user8 = debugAddUserAux(8, new_course, 52)   
    new_user9 = debugAddUserAux(9, new_course, 24)   
    new_user10 = debugAddUserAux(10, new_course, 90)   

    # Testing changing existing user points
    print(new_user3.id)
    user3 = User.query.filter(User.id == new_user3.id).filter(User.courses.contains(new_course)).first()
    print(user3.points.points)
    user3.points.points = 100
    db.session.commit()

    # This shows old existing user entry is still in leaderboard (updateLeaderboard() should remove it and update with new entry that has 100 points)
    test = testLeaderboard.userInfo.getUser(user3.username)
    print(user3.username, test.name, test.points)

    testLeaderboard.updateLeaderboard()

    print(testLeaderboard.getRankByUser(new_user2.username))
    print(testLeaderboard.getUsersByRank(1))
    print(testLeaderboard.getUsersByRank(2))

    #### DATABASE TEAR DOWN ####
    db.session.query(Points).delete()
    db.session.query(User).delete()
    db.session.query(Course).delete()
    db.session.commit()


def debugAuxClasses():
    # Rough debugging tests -- expand on this and convert this over to pytest format in the future
    userEntry1 = UserEntryNode("Thor Odinson", "noobmaster69", 40)
    userEntry2 = UserEntryNode("John Doe", "johndoe1", 24)
    userEntry3 = UserEntryNode("John Doe Jr.", "johndoe2", 30)
    userEntry4 = UserEntryNode("John Doe Sr.", "johndoe3", 10)
    userEntry5 = UserEntryNode("Kahl Fan", "kahliscool", 35)
    userEntry6 = UserEntryNode("Janicki Worshipper", "janickiiscool", 30)
    userList = [userEntry1, userEntry2, userEntry3, userEntry4, userEntry5, userEntry6]

    userStorage = UserHashTable(5)
    pointsTree = PointsTree()

    ##### HASH TABLE TESTS #####
    # Test inserting into hash table
    for user in userList:
        userStorage.insertUser(user)

    test = userStorage.getUser("noobmaster69")
    print(test.name)

    # Test deletion from hash table
    userStorage.deleteUser("johndoe1")
    try:
        test = userStorage.getUser("johndoe1")
        print("Failure in deletion...")
    except:
        print("Success for deletion!")

    ##### R-B TABLE TESTS #####
    # Testing insertion of elements into points red-black tree
    print("~~ Red-black tree insertion test: ~~")
    for user in userList:
        pointsTree.insertUser(user)
        print(f"Inserted {user.username}:")
        print_tree(pointsTree)

    print("\n~~~~~~~~~~")

    # Testing getting users by rank
    test = pointsTree.getUsersByRank(2)
    print(test[0].username)
    print("^  Results of getting back users through their rank  ^\n")

    # Getting back rankings in dict format
    rankings = pointsTree.getAllUsers()
    print(rankings)
    print("^  Results of getting back all users in the rankings  ^")

    # Deletion of a node in the tree
    nodeToDelete = pointsTree.getUsersByRank(1)[0]
    pointsTree.deleteUser(nodeToDelete)
    print("\nDeletion of user successful!")
    print_tree(pointsTree)
    rankings = pointsTree.getAllUsers()
    print(rankings)

    # Deletion of a node NOT in the tree that has its own points value
    try:
        pointsTree.deleteUser(nodeToDelete)
    except UserDBError as e:
        print("\nDeletion of non-existant user (with own unique points value) failed successfully!")
        print_tree(pointsTree)
        rankings = pointsTree.getAllUsers()
        print(rankings)

    # Deletion of a node NOT in the tree that shares a points value with another entry in the tree
    nodeToDelete.points = 35
    try:
        pointsTree.deleteUser(nodeToDelete)
    except UserDBError as e:
        print("\nDeletion of non-existant user (with points shared with another user in the tree) failed successfully!")
        print_tree(pointsTree)
        rankings = pointsTree.getAllUsers()
        print(rankings)


####################

if __name__ == "__main__":  
    debugLeaderboard()


