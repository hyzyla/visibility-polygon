from visual_objects import Point, Edge, Ray, is_closer

class Node:
    def __init__(self, edge, distance=None):
        self.edge = edge

    def __eq__(self, other):
        return self.edge == other.edge

    def update(self, node):
        self.edge = node.edge

class Tree:

    def __init__(self, nodes: list):
        self.nodes = nodes

    @property
    def is_empty(self):
        return len(self.nodes) == 0

    @property
    def leftmost(self):
        if not self.nodes:
            return None
        return self.nodes[0]

    def insert(self, node: Node, ray: Ray):
        if not self.nodes:
            return
        first = self.nodes[0]
        if is_closer(node.edge, first.edge, ray):
            self.nodes[0:0] = [node]
            return

        for i, second in enumerate(self.nodes[1:]):
            if is_closer(first.edge, node.edge, ray) and is_closer(node.edge, second.edge, ray):
                self.nodes[i+1:i+1] = [node]
                return
            first = second
        else:
            self.nodes.append(node)
            

    def delete(self, node: Node, ray: Ray):
        for current in self.nodes:
            if current.edge == node.edge:
                self.nodes.remove(current)
                return 

    def update(self, old: Node, new: Node, ray: Ray):
        for current in self.nodes:
            if current.edge == old.edge:
                current.update(new)
                return

if __name__ == "__main__":
    ray = Ray(
        start=Point(1, 1),
        end=Point(2, 2))

    edges = [
        Edge(Point(3, 1), Point(1, 3)),
        Edge(Point(4, 2), Point(2, 4)),
        Edge(Point(5, 3), Point(3, 5)),
        
        Edge(Point(7, 5), Point(5, 7)),
        Edge(Point(8, 6), Point(6, 8)),
        Edge(Point(9, 7), Point(7, 9)),
        
    ]
    e = Edge(Point(6, 4), Point(4, 6))
    nodes = [Node(e, ray.intersect_dist(e)) for e in edges]
    tree = Tree(nodes)
    tree.insert(Node(e), ray)
    pass
