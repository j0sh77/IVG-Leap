class Node(object):

    def __init__(self, data, prev, next):
        self.data = data
        self.prev = prev
        self.next = next


class MenuItem(object):

    name = "Unnamed"
    size = 0
    parent = None
    head = None
    tail = None
    cur = None

    def __init__(self, name, *args):
        self.name = name
        if len(args) is 0:
            return

        prev = None
        for i in range(0, len(args)):
            if isinstance(args[i], MenuItem):
                args[i].setParent(self)
            if self.head is None:
                self.head = Node(args[i], None, None)
                self.tail = self.head
                self.cur = self.head
                prev = self.head
            else:
                newNode = Node(args[i], None, None)
                newNode.prev = prev
                prev.next = newNode
                self.tail = newNode
                prev = newNode

    def next(self):
        if self.cur.next is None:
            self.cur = self.head
        else:
            self.cur = self.cur.next

        return self.cur

    def prev(self):
        if self.cur.prev is None:
            self.cur = self.tail
        else:
            self.cur = self.cur.prev

        return self.cur

    def getCursor(self):
        return self.cur

    def show(self):
        print "Head: %s" % (self.head.data)
        print "Tail: %s" % (self.tail.data)
        print "Show list data:"
        currentNode = self.head
        while currentNode is not None:
            print currentNode.prev.data if hasattr(currentNode.prev, "data") else None,
            print currentNode.data,
            print currentNode.next.data if hasattr(currentNode.next, "data") else None

            currentNode = currentNode.next
        print "*"*50

    def getName(self):
        return self.name

    def setName(self, newName):
        self.name = newName

    def getParent(self):
        return self.parent

    def setParent(self, newParent):
        self.parent = newParent

    def getNodeNames(self):
        if self.cur is None:
            return ""
        item = self.cur.data if not isinstance(self.cur.data, MenuItem) else self.cur.data.getName()
        ret = "\033[7m%s\033[0m" % (item)
        cursor = self.cur
        self.next()
        while self.cur is not cursor:
            item = self.cur.data if not isinstance(self.cur.data, MenuItem) else self.cur.data.getName()
            ret = "%s, %s" % (ret, item)
            self.next()
        return ret
