from collections import defaultdict
from math import sqrt
# import gmplot package
# import gmplot
# Shortest path to all coordinates from any node
# Coordinates must be provided as a list containing lists of
# x/y pairs. ie [[23.2321, 58.3123], [x.xxx, y.yyy]]


def distance_between_coords(x1, y1, x2, y2):
    distance = sqrt(((x2 - x1) ** 2) + ((y2 - y1) ** 2))
    return distance


# Adds "names" to coordinates to use as keys for edge detection
def name_coords(coords):
    coord_count = 0
    for coord in coords:
        coord_count += 1
        coord.append(coord_count)
    return coords


# Creates a weighted and undirected graph
# Returns named coordinates and their connected edges as a dictonary
def graph(coords):
    coords = name_coords(coords)
    graph = defaultdict(list)
    edges = {}
    for current in coords:
        for comparer in coords:
            if comparer == current:
                continue
            else:
                weight = distance_between_coords(current[0], current[1],
                                                 comparer[0], comparer[1])
                graph[current[2]].append(comparer[2])
                edges[current[2], comparer[2]] = weight
    return coords, edges


# Returns a path to all nodes with least weight as a list of names
# from a specific node
def shortest_path(node_list, edges, start):
    neighbor = 0
    unvisited = []
    visited = []
    total_weight = 0
    current_node = start
    for node in node_list:
        if node[2] == start:
            visited.append(start)
        else:
            unvisited.append(node[2])
    while unvisited:
        for index, neighbor in enumerate(unvisited):
            if index == 0:
                current_weight = edges[start, neighbor]
                current_node = neighbor
            elif edges[start, neighbor] < current_weight:
                current_weight = edges[start, neighbor]
                current_node = neighbor
        total_weight += current_weight
        unvisited.remove(current_node)
        visited.append(current_node)
    return visited, total_weight


def driver(coords):
    coords, edges = graph(coords)
    shortest_path(coords, edges, 3)
    shortest_path_taken = []
    shortest_path_weight = 0

    for index, node in enumerate(coords):
        path, weight = shortest_path(coords, edges, index + 1)
        print('--------------------------------------')
        print("Path", index + 1, "=", path)
        print("Weight =", weight)
        if index == 0:
            shortest_path_weight = weight
            shortest_path_taken = path
        elif weight < shortest_path_weight:
            shortest_path_weight = weight
            shortest_path_taken = path
    print('--------------------------------------')
    print("The shortest path to all nodes is:", shortest_path_taken)
    print("The weight of the path is:", shortest_path_weight)
    return {
        "path":shortest_path_taken,
        "weight":shortest_path_weight
    }
  
    # latitude_list = [ 30.3358376, 30.307977, 30.3216419 ]
    # longitude_list = [ 77.8701919, 78.048457, 78.0413095 ]
    
    # gmap5 = gmplot.GoogleMapPlotter(30.3164945,78.03219179999999, 13)
    
    # gmap5.scatter( latitude_list, longitude_list, '#FF0000',size = 40, marker = False)
    
    # # polygon method Draw a polygon with
    # # the help of coordinates
    # gmap5.polygon(latitude_list, longitude_list,color = 'cornflowerblue')
    
    # gmap5.draw( "map15.html" )


# coords = [[16.4258806,81.6564862],[16.4300793,81.6562287],[16.4302027,81.6534821],[16.4425732,81.6280264]]
    
# driver(coords)








