from visual_objects import Point, Edge, Ray, is_closer

class Node:
    def __init__(self, edge, distance):
        self.edge = edge
        self.d = distance
        self.right = None
        self.left = None

    def update(self, node: 'Node'):
        self.edge = node.edge
        self.d = node.d

class Tree:

    def __init__(self, nodes):
        self.root = self.__from_sorted(0, len(nodes) - 1,  nodes)
      

    def __from_sorted(self, start, end, nodes):
        if start > end:
            return None

        mid = (start + end) // 2
        node = nodes[mid]
        node.left = self.__from_sorted(start,   mid - 1,  nodes)
        node.right  = self.__from_sorted(mid + 1, end,      nodes)

        return node

    def update_dist(self, node, ray):
        if node is None:return

        point = ray.intersect(node.edge)
        if point is None:
            raise ValueError(f"Strange situation Ray[{ray.start}, {ray.end}] and {node.edge} doesn't have intersection point")

        node.d = ray.start.dist(point)
    
    @property
    def is_empty(self):
        return self.root is None

    @property
    def leftmost(self):
        if self.root is None:
            return None
        return self.__leftmost(self.root)

    def __leftmost(self, node):
        if not node.left:
            return node
        return self.__leftmost(node.left)

    def insert(self, node: Node, ray: Ray):
        if self.root is  None:
            self.root = node
        else:
            self.__insert(node, self.root, ray)
    
    def __insert(self, node: Node, root: Node, ray: Ray):
        #self.update_dist(node, ray)
        #self.update_dist(root, ray)

        if is_closer(node.edge, root.edge, ray):
            if root.left is None:
                root.left = node
            else:
                self.__insert(node, root.left, ray)
        else:
            if root.right is None:
                root.left = node
            else:
                self.__insert(node, root.right, ray)

    def delete(self, node: Node, ray: Ray):
        self.root = self.__delete(node, self.root, ray)

    def __delete(self, node: Node, root: Node, ray: Ray):
        self.update_dist(node, ray)
        self.update_dist(root, ray)

        if root is None:
            return root

        if node.edge == root.edge:
            if root.left is None:
                return root.right
            elif root.right is None:
                return root.left
            
            root.edge = self.__leftmost(root.right).edge
            root.right = self.__delete(node, root.right, ray)
        
        elif node.d < root.d:
            root.right = self.__delete(node, root.right, ray)
        elif node.left:
            root.left = self.__delete(node, root.left, ray)
        return root

    def update(self, old: Node, new: Node, ray: Ray):
        self.__update(old, new, self.root, ray)

    def __update(self, old: Node, new: Node, root: Node, ray: Ray):
        #self.update_dist(old, ray)
        #self.update_dist(new, ray)
        #self.update_dist(root, ray)


        if root is None:
            return
        
        if root.edge == old.edge:
            return root.update(new)
            
        if is_closer(old.edge, root.edge, ray) and root.left:
            self.__update(old, new, root.left, ray)
        elif not is_closer(old.edge, root.edge, ray) and root.right:
            self.__update(old, new, root.right, ray)

if __name__ == "__main__":
    ray = Ray(
        start=Point(1, 1),
        end=Point(2, 2))
        
    edges = [
        Edge(Point(3, 1), Point(1, 3)),
        Edge(Point(4, 2), Point(2, 4)),
        Edge(Point(5, 3), Point(3, 5)),
        Edge(Point(6, 4), Point(4, 6)),
        Edge(Point(7, 5), Point(5, 7)),
        Edge(Point(8, 6), Point(6, 8)),
        Edge(Point(9, 7), Point(7, 9)),
    ]

    nodes = [Node(e, ray.intersect_dist(e)) for e in edges]
    tree = Tree(nodes)
    print(tree.leftmost.edge)
