from visual_objects import Ray, Polygon, Edge, Point, get_angle, is_closer
from math import pi
from tree_ import Tree, Node


def get_intersections(ray: Ray, polygons: [Polygon]):
    output = []
    for polygon in polygons:
        output += [(ray.intersect(edge), edge)
                   for edge in polygon.edges if ray.intersect(edge)]
    return output


def get_initial_ray(point: Point, polygons: [Polygon]):
    a, b = polygons[0].points[:2]
    median = Point((a.x + b.x) / 2, (a.y + b.y) / 2)
    return Ray(point, median)


def init_tree(edges, ray) -> Tree:
    nodes = []
    for edge in edges:
        assert_edge(ray, edge)
        dist = ray.start.dist(ray.intersect(edge))
        nodes.append(Node(edge, dist))

    return Tree(nodes)


def sort_vertices(point: Point, ray_point: Point, polygons: [Polygon]):
    vertices = []
    for polygon in polygons:
        vertices += polygon.points

    vertices.sort(key=lambda p: get_angle(point, ray_point, p))
    return vertices


def add_bounds(point: Point, polygons: [Polygon]) -> Polygon:
    points = [point]
    for polygon in polygons:
        points += polygon.points
    
    max_x = max(points, key=lambda p: p.x).x + 20
    min_x = min(points, key=lambda p: p.x).x - 20
    max_y = max(points, key=lambda p: p.y).y + 20
    min_y = min(points, key=lambda p: p.y).y - 20
    polygon = Polygon([
        Point(min_x, min_y),
        Point(max_x, min_y),
        Point(max_x, max_y),
        Point(min_x, max_y),
    ], visible=False)
    return  polygons + [polygon]

def is_active_edge(point: Point, vertex: Point, edge: Edge):
    other = edge.get_other(vertex)
    return get_angle(point, vertex, other) >= pi

def sort_edges(ray, polygons):
    point = ray.start
    intersections = get_intersections(ray, polygons)
    intersections.sort(key=lambda inter: point.dist(inter[0]))
    edges = [edge for point, edge in intersections]
    return edges, intersections[0][0]

def assert_edge(ray: Ray, edge: Edge):
    if not ray.intersect(edge):
        raise ValueError(f"Ray[{ray.start}, {ray.end}] doesn't intersect {edge}")

def delete(tree: Tree, edge: Edge, ray: Ray):
    assert_edge(ray, edge)
    node = Node(edge, ray.intersect_dist(edge))
    tree.delete(node, ray)

def update(tree: Tree, old: Edge, new: Edge, ray: Ray):
    assert_edge(ray, old)
    assert_edge(ray, new)
    old = Node(old, ray.intersect_dist(old))
    new = Node(new, ray.intersect_dist(new))
    tree.update(old, new, ray)

def insert(tree: Tree, edge: Edge, ray: Ray):
    assert_edge(ray, edge)
    node = Node(edge, ray.intersect_dist(edge))
    tree.insert(node, ray)

# def construct_edge(output: [Edge], tree: Tree, leftmost: Node, ray: Ray):
#     vertex = ray.end
    
#     z = ray.intersect(leftmost.edge)
#     if z is None:
#         raise ValueError("No intersections")

#     output.append(Edge(z, vertex))

def construct_end_edge(output: [Edge], tree: Tree, leftmost: Node, ray: Ray):
    # insert, insert
    vertex = ray.end
    
    z = ray.intersect(leftmost.edge)
    if z is None:
        raise ValueError("No intersections")
    
    new_edge = Edge(z, vertex, visible=False)
    if leftmost.edge in output:
        output.remove(leftmost.edge)
        # finding right point for construct edge with point z
        x, y = leftmost.edge.get_points()
        n = x if get_angle(ray.start, ray.end, x) > get_angle(ray.start, ray.end, y) else y
        output.append(Edge(n, z, visible=leftmost.edge.visible))

    output.append(new_edge)
    

def construct_begin_edge(output: [Edge], tree: Tree, vertices: [Point], ray: Ray):
    vertex = ray.end
    leftmost = tree.leftmost

    z = ray.intersect(leftmost.edge)
    if z is None:
        raise ValueError("No intersections")

    # finding right point for construct edge with point z
    x, y = leftmost.edge.get_points()
    n = x if get_angle(ray.start, ray.end, x) < get_angle(ray.start, ray.end, y) else y

    partial_edge = Edge(n, z, visible=leftmost.edge.visible)
    new_node = Node(partial_edge)

    edge1, edge2 = n.edges
    if edge1 == leftmost.edge:
        edge1 = partial_edge
    else:
        edge2 = partial_edge
    n.edges = edge1, edge2

    tree.update(old=leftmost, new=new_node, ray=ray)

    new_edge = Edge(z, vertex, visible=False)
    output.append(new_edge)  


def update_output(tree: Tree, output: [Edge], leftmost: Edge):
    if leftmost and leftmost.edge not in output:
        output.append(leftmost.edge)


def asano_algorithm(point: Point, polygons: [Polygon]):
    polygons = add_bounds(point, polygons)
    ray = get_initial_ray(point, polygons)
    edges, first = sort_edges(ray, polygons)
    tree = init_tree(edges, ray)
    vertices = sort_vertices(point, first, polygons)

    output = []
    for vertex in vertices:
       
        edge1, edge2 = vertex.edges
        ray = Ray(point, vertex)
        leftmost = tree.leftmost
        update_output(tree, output, leftmost)

        if (is_active_edge(point, vertex, edge1) and is_active_edge(point, vertex, edge2)):
            
            delete(tree, edge1, ray)
            delete(tree, edge2, ray)
            if not tree.is_empty and leftmost != tree.leftmost:
                construct_begin_edge(output, tree, vertices, ray)
                #construct_edge(output, tree, tree.leftmost, ray)
            continue

        elif (is_active_edge(point, vertex, edge1) ^ is_active_edge(point, vertex, edge2)):
            
            active, not_active = edge1, edge2
            if not is_active_edge(point, vertex, edge1):
                active, not_active = edge2, edge1
            update(tree, active, not_active, ray)
            continue
            
        elif (not is_active_edge(point, vertex, edge1) and not is_active_edge(point, vertex, edge2)):
            
            first, second = (edge1, edge2) if is_closer(edge1, edge2, ray) else (edge2, edge1)

            insert(tree, second, ray)
            insert(tree, first, ray)
            
            if not tree.is_empty and leftmost != tree.leftmost:
                construct_end_edge(output, tree, leftmost, ray)
                #construct_edge(output, tree, leftmost, ray)

    update_output(tree, output, leftmost)
    return output 

if __name__ == "__main__":

    from tree_ import Tree, Node
    
    polygons = [
        Polygon([
            Point(234, 40),
            Point(190, 100), 
            Point(280, 300), 
            Point(300, 400), 
            Point(400, 70), 
        ]),
        
        Polygon([
            Point(130, 290),
            Point(110, 300),
            Point(250, 290),
            Point(150, 240)
        ])
    ]

    point = Point(50, 50)
    edges = asano_algorithm(point, polygons)
   
