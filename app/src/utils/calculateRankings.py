# calculateRankings.py - uses certain algorithms and data structures to sort and organize member points in the order to be displayed on the leaderboard

"""
Plan:
    - Query from database a custom table containing user name, user's username, and points for when Points.user_id == User.id; users can be filtered from a specific course,
      or everyone can just be given at once.
    - Maybe find some way to locally store that data somehow in records (also needs efficient fetch; may not require an ordered structure)?
    - Use a balanced binary (red-black) tree to sort users by points; the keys will be the points, while the values will be lists containing (references to?) people with
      those number of points.

Usage of the main Leaderboard class (export just this class from the file):
    - Leaderboard(courseID: optional int): 
        Instantiates a new leaderboard object out of a query of all users in the database, based on their points. If an integer course ID is provided, then the query is
        limited to users enrolled within that specific course. Once all users are obtained from the query, the leaderboard automatically calculates every user's rankings,
        based off of their associated points in the database. For multiple users with the same points, they are all considered under the same rank number N, while the user(s)
        with the next rank is simply placed at rank number (N + 1). 

    - Leaderboard.updateData():
        Updates the given leaderboard object with a new query of all database users, or a new one with all users within a specific course (if the leaderboard was created
        with a course ID integer). Users added to the database will be added to the rankings, while users deleted from the database will be removed from the rankings with
        the rankings adjusted accordingly. Users whose points data is changed (e.g. userA gains +100 points, raising their rank) will also be altered accordingly within
        the leaderboard.

        (...One possible oversight in this update function is if the user's name is somehow changed, since the queries only filter by username and points; therefore, 
        the leaderboard won't contain updated information on that specific user's name. Support should be added within the query comparisons if such a feature is added
        in the future.)
    
    - Leaderboard.getBottomRankNum() -> int:
        Returns the rank of the user(s) with the least amount of points on the leaderboard.

    - Leaderboard.getUsersByRank(rank: int) -> list[dict]:
        Given a specific rank integer (where rank >= 1 and rank <= Leaderboard.getBottomRankNum()), returns a list containing the information of 1 or more users placed
        at that rank. If a number outside of the above range is provided, then a UserDBError exception is thrown.
    
    - Leaderboard.getRankByUser(username: str) -> int:
        Given the username of a user within the leaderboard, returns an integer corresponding to the rank of the provided user. If no user exists with the given username,
        a UserDoesNotExistError exception is thrown.

    - Leaderboard.getTopUsers() -> list[dict]:    
        Returns a list of the user(s) ranked the highest on the leaderboard (most amount of points).

    - Leaderboard.getBottomUsers() -> list[dict]:   
        Returns a list of the user(s) ranked the lowest on the leaderboard (least amount of points).

    - Leaderboard.getAllUsers() -> dict:
        Returns an easily-convertible-to-JSON dictionary object with keys corresponding to rank numbers and values representing a list of users corresponding with 
        each rank. The structure is as follows:
            {
                <rank #>: [
                    {
                        "name": <user's name>,
                        "username": <user's username>,
                        "points": <user's point count>
                    }
                ]
            }

    - Leaderboard.getUsersByRankRange(topRank: int, bottomRank: int) -> dict:
        Returns a dictionary object in the same format above from Leaderboard.getAllUsers(), but instead limited to users from topRank up to bottomRank (inclusive).
        Note that the arguments must be passed such that topRank is smaller than bottomRank, topRank & bottomRank are at least 1, and topRank & bottomRank are less than
        or equal to the rank of the user with the least amount of points (to check, use Leaderboard.getBottomRankNum() to get this rank number).

"""

### Imports ###
from math import ceil
from enum import Enum
from app.src.models import User, user_course, Course, Points, db, Subject

### Custom Errors and Enum Classes ###
class UserDBError(Exception):
    pass

class UserDoesNotExistError(Exception):
    pass

class RBTreeColour(Enum):
    BLACK = "black"
    RED = "red"

### Auxiliary/minor classes used in main leaderboard ###
# A node part of a linked list, to be stored inside UserHashTable's list
class UserEntryNode:
    def __init__(self, name, username, points):
        self.name: str = name
        self.username: str = username  # Note: based on model, these are unique
        self.points: int = points
        self.nodeRef: PointsNode = None

        # Node attributes
        self.next: UserEntryNode = None

    def setPointsTree(self, pointsNode) -> None:
        self.nodeRef = pointsNode


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

    # Actual hashing function used; depends on Python's built-in siphash for strings, then modulo's the number to within the range of the data list's capacity
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

            self.__checkTableLoad()
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

            self.__checkTableLoad()

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

    # Checks if current load factor is still smaller than set upper load factor limit
    def __checkTableLoad(self) -> None:
        if (self.size / self.capacity) > self.loadFactor:
            self.__resizeTable()

    # Resizes internal list to double the size of the previous list/number of elements in previous list
    # Note: using a new prime number here for the new size would be ideal, but methods for obtaining it would have less than ideal time complexities and/or space 
    # complexities in practice alongside the O(n) resizing... (e.g. Sieve of Eratosthenes = O(n * log(log n))) time, and O(sqrt(N)) space for getting prime number N)
    def __resizeTable(self) -> None:
        # print("~UserHashTable Debug - resizing table")
        self.capacity = self.size * 2

        oldItems = self.items.copy()
        self.items = [None] * self.capacity

        for index, linkedList in enumerate(oldItems):
            if linkedList is None:
                continue

            userEntry: UserEntryNode = linkedList
            # print(f"linkedlist #{index}")

            while userEntry is not None:
                # print("Inserting ", userEntry.username, "...")
                nodeCopy = UserEntryNode(userEntry.name, userEntry.username, userEntry.points)
                self.insertUser(nodeCopy)
                userEntry = userEntry.next

    # For debug... remove in the future once leaderboard is fully integrated with other stuff
    def printContents(self) -> None:
        print("~~ UserHashTable Contents: ~~")
        for index, linkedList in enumerate(self.items):
            if linkedList is None:
                continue

            userEntry: UserEntryNode = linkedList
            print(f"{index}: [", end="")

            while userEntry is not None:
                print(f"{userEntry.username}, ", end="")
                userEntry = userEntry.next
            
            print("]")

class PointsNode:
    def __init__(self, points, userEntryRef):
        # -- General attributes for binary trees (renamed in the context of the leaderboard) --
        # Node key; if tree is init with length 0, then this is just None
        self.points: int = points
        self.userEntryRefs: list[UserEntryNode] = [userEntryRef]  # Node value(s), those being back-references to UserEntryNode objects in hashmap

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

# Represents a left-leaning red black tree; acts sort of like an "outer shell" of the tree only pointing to the root node of the tree 
# (successive nodes are accessed through other nodes)
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

    # Auxiliary functions for maintaining the R-B tree structure of the data
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

    # Given a points key, get list of all users stored in the node with that key
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
    
    # Returns a tuple of the lowest-scoring users currently in DB, along with their point count (points, users)
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

    # Given a rank (correlated to the position of a node in the tree), find all users within the node whose position corresponds to that rank.
    def getUsersByRank(self, rank: int) -> list[UserEntryNode]:
        if self.root is None or self.__treeSize(self.root) < rank or rank <= 0:
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

    # Self-explanatory from method name; used in conjunction with something else to get points from username/other user data
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

    # Adding a new user entry into rankings red-black tree
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

    # Node deletion from the rankings red-black tree
    def deleteUser(self, userEntry: UserEntryNode):
        self.deleteUserAux(self.root, userEntry)

    # -- DELETE HELPER FUNCTIONS BASED OFF FROM HERE: https://www.programiz.com/dsa/deletion-from-a-red-black-tree --
    # Aux function for deleteUser(); fixes RB tree after deleting original node and replacing with another suitable node within the tree
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

    # Aux function to deleteUser(); overwrites original to-be-deleted node with new suitable node within the tree
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

    # Aux function to deleteUser(); handles actual overwriting of old node and identifies new node to replace old node with
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
        rankingsOutput: dict = {}  # Format of dict is {<rank #>: [{name: <str>, username: <str>, points: <int>}]}

        self.__getAllUsersAux(
            rankingsOutput, self.root, self.__treeSize(self.root.right) + 1
        )

        return rankingsOutput

    # Aux function for getAllUsers()
    def __getAllUsersAux(self, rankingsOutput: dict, node: PointsNode, rank: int = 0):
        if node is None:
            return

        tempList = []

        # Traverse to right subtree first
        rightNodeRank = (
            (rank - self.__treeSize(node.right.left) - 1)
            if (node.right is not None)
            else rank
        )
        self.__getAllUsersAux(rankingsOutput, node.right, rightNodeRank)

        # "Visit" and register current node
        for userRef in node.userEntryRefs:
            tempEntry = {
                "name": userRef.name,
                "username": userRef.username,
                "points": userRef.points,
            }
            tempList.append(tempEntry)

        rankingsOutput[rank] = tempList

        # Traverse to left subtree last
        leftNodeRank = (
            (rank + self.__treeSize(node.left.right) + 1)
            if (node.left is not None)
            else rank
        )
        self.__getAllUsersAux(rankingsOutput, node.left, leftNodeRank)


"""
This is the main class other programs will interact with for the leaderboard. Ideally, this should be a group of functions 
interacting with the Leaderboard DB schema, instead of a large class storing data, but Mithun (who's in charge of creating that schema) hasn't gotten 
back to me yet on how he's designing it... for now, this is a temporary solution until he finishes his tasks and uploads a PR.
"""
class Leaderboard():
    """
    A class used to store and fetch the rankings of users within the entire database or within a specified Class database entry (if passed a courseID int during instantiation).

    The leaderboard is constructed into two primary parts: the rankings, and userInfo. The userInfo stores all relevant user info 
    within a special Node class of sorts (UserEntryNode), and each of these UserEntryNodes are stored within a hash table such that the 
    information is accessible by indexing with a user's unique username within O(1) average time. Rankings, on the other hand, is structured 
    as a red-black tree (where PointsTree = outer "container" class pointing to root, and PointsNode = individual tree nodes storing user points 
    as a key and 1 or more reference(s) to users/UserEntryNodes with those points). To find a user's ranking, we would need to get their 
    relevant points info using their username, then find its relevant PointsNode in the rankings R-B tree and determine their rank based 
    on the PointsNode's overall position in the structure.

    For updating the leaderboard, there is no need to manually append any sort of user to the leaderboard; instead, just
    change whatever relevant data within the database itself. By running Leaderboard.updateData(), the leaderboard will
    query the db and make any necessary additions or deletions to its data. Other methods also exist to obtain users or rank numbers in
    a variety of ways, such as filtering users by rank number, getting a user's rank given their username, getting top or bottom users in 
    the leaderboard, and 
    """
    def __init__(self, courseID: int = None):
        self.rankings: PointsTree = PointsTree()
        self.userInfo: UserHashTable = None
        self.userDBQuery = None
        self.courseID: int = courseID

        self.__setUpLeaderboard()

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
    def __setUpLeaderboard(self) -> None:
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
    def updateData(self) -> None:
        newQuery = self.__queryData()
        queryDiffAdded = newQuery.filter(~User.username.in_([user[1] for user in self.userDBQuery]))  # Checks if a user was added
        queryDiffRemoved = [user for user in self.userDBQuery if user not in newQuery.all()]          # Checks if a user was removed
        queryDiffChanged = newQuery.filter(
            User.username.in_([user[1] for user in self.userDBQuery])                                 # 1st filter: Get users that appear in both old and new queries
        ).filter( 
            ~User.points.has(Points.points.in_([user[2] for user in self.userDBQuery]))               # 2nd filter: Only keep users who have diff. # of points between old & new queries
        )                                                                                             # End result: Checks if a pre-existing user entry was modified (through points)

        dbEntriesAdded: list[tuple] = queryDiffAdded.all()
        dbEntriesRemoved: list[tuple] = queryDiffRemoved
        dbEntriesChanged: list[tuple] = queryDiffChanged.all()
        # dbEntriesChangedOld: list[tuple] = [oldEntry for oldEntry in self.userDBQuery if oldEntry[1] in [newEntry[1] for newEntry in dbEntriesChangedNew]]
        # ^^ NOT NECESSARY, ALREADY COUNTED WITHIN REMOVED LIST (for some reason...?) ^^

        # print(f"~calcRankings Debug - Added entries: {dbEntriesAdded}")
        # print(f"~calcRankings Debug - Removed entries: {dbEntriesRemoved}")
        # print(f"~calcRankings Debug - Changed entries (new): {dbEntriesChanged}")
        # print(f"~calcRankings Debug - Changed entries (old): {dbEntriesChangedOld}")

        # Add old versions of changed user data so that old leaderboard entry is erased 
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

        # Stores latest query for future use/comparisons
        self.userDBQuery = newQuery.all()
        print_tree(self.rankings)

    def getUsersByRank(self, rank: int) -> list[dict]:
        output = self.rankings.getUsersByRank(rank)
        return [{"name": userEntry.name, "username": userEntry.username, "points": userEntry.points} for userEntry in output]

    def getRankByUser(self, username: str) -> int:
        userEntry: UserEntryNode = self.userInfo.getUser(username)
        return self.rankings.getRankByPoints(userEntry.points)

    def getTopUsers(self) -> list[dict]:
        output = self.rankings.getMaxUsers()
        return [{"name": userEntry.name, "username": userEntry.username, "points": userEntry.points} for userEntry in output]
    
    def getBottomUsers(self) -> list[dict]:
        output = self.rankings.getMinUsers()
        return [{"name": userEntry.name, "username": userEntry.username, "points": userEntry.points} for userEntry in output]
    
    def getAllUsers(self) -> dict:
        return self.rankings.getAllUsers()
    
    def getUsersByRankRange(self, topRank: int, bottomRank: int) -> dict:
        output = {}

        if topRank > bottomRank or (topRank <= 0 or bottomRank <= 0) or (topRank > self.getBottomRankNum() or bottomRank > self.getBottomRankNum()):
            raise UserDBError("The given range of ranks is invalid! Ensure that both arguments are positive integers, topRank is less than or equal to bottomRank, and \
                              both ranks are less than or equal to the rank of the user with the least points.")
        
        for rank in range(topRank, bottomRank + 1):
            rankUsers = self.getUsersByRank(rank)
            output[rank] = rankUsers

        return output

    def getBottomRankNum(self) -> int:
        bottomRankUsers = self.getBottomUsers()
        return self.getRankByUser(bottomRankUsers[0]["username"])

##########
    
### WIP: Finish this function based off of Mithun's leaderboard database schema    
# Set up leaderboard and sort all user entries in it, then create a database entry for the leaderboard and return the corresponding ID/primary key value
# def setUpLeaderboard(courseID: int = None) -> int:
#     rankings: PointsTree = PointsTree()

#     if courseID is None:
#         userDBQuery = db.session.query(User.name, User.username, Points.points).distinct().filter(                
#             User.id == Points.user_id
#         )
#     else:
#         userDBQuery = db.session.query(User.name, User.username, Points.points).distinct().filter(
#             User.id == Points.user_id
#         ).filter(
#             user_course.c.course_id == courseID
#         )

#     dbEntries: list[tuple] = userDBQuery.all()
#     # print(dbEntries)

#     if dbEntries is not None:
#         # Create UserHashTable with necessary args and insert all database query entries inside
#         userInfo = UserHashTable(len(dbEntries), courseID)

#         for dbEntry in dbEntries:
#             userEntry = UserEntryNode(dbEntry[0], dbEntry[1], dbEntry[2])
#             userInfo.insertUser(userEntry)
#             rankings.insertUser(userEntry)

#         print_tree(rankings)
#         test = rankings.getAllUsers()

#         # <-- Here would be setup for the leaderboard database entry; TBD
#         return 0

#     else:
#         if courseID is not None:
#             raise UserDBError("Error creating leaderboard: no users exist that are taking the specified course!")
        
#         raise UserDBError("Error creating leaderboard: no users are registered within the database yet!")


##### DEBUG STUFF (maybe use some of these for future unit tests) #####

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

# Primary debug function for testing the leaderboard (PointsTree and HashMap functioning together)
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
    points = [50, 25, 60, 55, 90, 85]
    new_users = [debugAddUserAux(num, new_course, points[num]) for num in range(len(points))]

    #### CLASS TESTING ####
    testLeaderboard = Leaderboard(new_course.id)

    # Testing deletion and additions of users from course (and/or database)
    debugDeleteUserAux(new_users[3])
    points2 = [62, 52, 24, 90]
    new_users += [debugAddUserAux(num + len(new_users), new_course, points2[num]) for num in range(len(points2))]

    # Testing changing existing user points
    print(new_users[2].id)
    user2 = User.query.filter(User.id == new_users[2].id).filter(User.courses.contains(new_course)).first()
    print(user2.points.points)
    user2.points.points = 100
    db.session.commit()

    # This shows old existing user entry is still in leaderboard (updateData() should remove it and update with new entry that has 100 points)
    test = testLeaderboard.userInfo.getUser(user2.username)
    print(user2.username, test.name, test.points)

    testLeaderboard.updateData()

    print(f"Rank of user {new_users[1].username}: {testLeaderboard.getRankByUser(new_users[1].username)}")
    print("User(s) at rank 1: ", testLeaderboard.getUsersByRank(1))
    print("User(s) at rank 2: ", testLeaderboard.getUsersByRank(2))
    print("User(s) at rank 3: ", testLeaderboard.getUsersByRank(3))
    print("User(s) at rank 4: ", testLeaderboard.getUsersByRank(4))
    print("User(s) at rank 5: ", testLeaderboard.getUsersByRank(5))

    print("Entire leaderboard (as a dictionary/JSON format):\n", testLeaderboard.getAllUsers())
    print("Leaderboard rankings from rank 1 to 5:\n", testLeaderboard.getUsersByRankRange(1, 5))

    #### DATABASE TEAR DOWN ####
    db.session.query(Points).delete()
    db.session.query(User).delete()
    db.session.query(Course).delete()
    db.session.commit()

# Primary debug function for testing hash table's resizing capabilities
def debugHashTableResize():
    userEntry1 = UserEntryNode("Thor Odinson", "noobmaster69", 40)
    userEntry2 = UserEntryNode("John Doe", "johndoe1", 24)
    userEntry3 = UserEntryNode("John Doe Jr.", "johndoe2", 30)
    userEntry4 = UserEntryNode("John Doe Sr.", "johndoe3", 10)
    userEntry5 = UserEntryNode("Kahl Fan", "kahliscool", 35)
    userEntry6 = UserEntryNode("Janicki Worshipper", "janickiiscool", 30)
    userEntry7 = UserEntryNode("Moore Maniac", "mooreislife42", 42)
    userList = [userEntry1, userEntry2, userEntry3, userEntry4, userEntry5, userEntry6, userEntry7] 

    userStorage = UserHashTable(1)

    for entryNum, userEntry in enumerate(userList):
        print(f"Inserting user #{entryNum}...")
        userStorage.insertUser(userEntry)
        userStorage.printContents()
        print("Success!")

# Debug function for testing general capabilities of auxiliary classes used within the leaderboard
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


