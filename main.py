'''
import json

# Load the data
file_path = "C:\Student Handout\Input data\level1a.json"

with open(file_path, 'r') as file:
    data = json.load(file)

# Extract data
n_neighbourhoods = data['n_neighbourhoods']
neighborhoods = data['neighbourhoods']
vehicle_capacity = data['vehicles']['v0']['capacity']
restaurant_distances = data['restaurants']['r0']['neighbourhood_distance']
orders = {neighborhood: details['order_quantity'] for neighborhood, details in neighborhoods.items()}

dist_matrix = []

# Add distances from restaurant to neighborhoods
dist_matrix.append([0] + restaurant_distances)
# Add distances between neighborhoods
for i in range(n_neighbourhoods):
    dist_row = [neighborhoods[f'n{i}']['distances'][j] for j in range(n_neighbourhoods)]
    dist_row.insert(0,restaurant_distances[i])
    #dist_row.append(n_neighbourhoods[i])
    dist_matrix.append(dist_row)


# Function to find the nearest neighborhood
def find_nearest(current_location, unvisited, distances):
    nearest = None
    min_distance = float('inf')
    for n in unvisited:
        if distances[current_location][int(n[1:])] < min_distance:
            min_distance = distances[current_location][int(n[1:])]
            nearest = n
    return nearest

# Create delivery slots
delivery_slots = []
current_slot = []
current_capacity = 0

for neighborhood, details in neighborhoods.items():
    order_quantity = details['order_quantity']
    if current_capacity + order_quantity <= vehicle_capacity:
        current_slot.append(neighborhood)
        current_capacity += order_quantity
    else:
        delivery_slots.append(current_slot)
        current_slot = [neighborhood]
        current_capacity = order_quantity

if current_slot:
    delivery_slots.append(current_slot)

# Optimize each delivery slot with a simple TSP solution (Nearest Neighbor)
optimized_slots = []
for slot in delivery_slots:
    route = ['r0']  # Start at the restaurant
    unvisited = set(slot)
    while unvisited:
        current_location = int(route[-1][1:]) if route[-1] != 'r0' else 0
        next_stop = find_nearest(current_location, unvisited, dist_matrix)
        route.append(next_stop)
        unvisited.remove(next_stop)
    route.append('r0')  # Return to the restaurant
    optimized_slots.append(route)

output = {"v0": {}}
for i, slot in enumerate(optimized_slots, start=1):
    output["v0"][f"path{i}"] = slot

# Convert to JSON format
output_json = json.dumps(output, indent=2)
print("Optimized Delivery Slots in JSON format:")
print(output_json)

with open("level1a_output.json", "w") as outfile:
    outfile.write(output_json)


#BINPACKING AND VEHICLE ROUTING
from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp
def first_fit_decreasing(orders, capacity):
    # Sort the orders in decreasing order by quantity
    sorted_orders = sorted(orders, key=lambda x: x[1], reverse=True)

    bins = []
    for order in sorted_orders:
        placed = False
        for bin in bins:
            if sum([o[1] for o in bin]) + order[1] <= capacity:
                bin.append(order)
                placed = True
                break

        if not placed:
            bins.append([order])

    return bins
#bins = first_fit_decreasing(orders, vehicle_capacity)
def solve_vrp(neighborhoods, dist_matrix, vehicle_capacity):
    delivery_slots = []
    current_slot = []
    current_capacity = 0

    for neighborhood, details in neighborhoods.items():
        order_quantity = details['order_quantity']
        if current_capacity + order_quantity <= vehicle_capacity:
            current_slot.append(neighborhood)
            current_capacity += order_quantity
        else:
            delivery_slots.append(current_slot)
            current_slot = [neighborhood]
            current_capacity = order_quantity

    if current_slot:
        delivery_slots.append(current_slot)

    optimized_slots = {}
    for i, slot in enumerate(delivery_slots, start=1):
        route = ['r0']
        unvisited = set(slot)
        while unvisited:
            current_location = int(route[-1][1:]) if route[-1] != 'r0' else 0
            next_stop = find_nearest(current_location, unvisited, dist_matrix)
            route.append(next_stop)
            unvisited.remove(next_stop)
        route.append('r0')
        optimized_slots[f'path{i}'] = route

    return optimized_slots

optimized_routes = solve_vrp(neighborhoods, dist_matrix, vehicle_capacity)

# Format the output
output = {"v0": optimized_routes}
output_json = json.dumps(output, indent=2)
print("Optimized Delivery Routes:")
print(output_json)
with open("level1a_output.json", "w") as outfile:
    outfile.write(output_json)


import json

def first_fit_decreasing(orders, capacity):
    sorted_orders = sorted(orders, key=lambda x: x[1], reverse=True)
    bins = []
    for order in sorted_orders:
        placed = False
        for bin in bins:
            if sum(o[1] for o in bin) + order[1] <= capacity:
                bin.append(order)
                placed = True
                break
        if not placed:
            bins.append([order])
    return bins

def find_nearest(current_location, unvisited, distances):
    nearest = None
    min_distance = float('inf')
    for n in unvisited:
        dist = distances[current_location][int(n[1:])]
        if dist < min_distance:
            min_distance = dist
            nearest = n
    return nearest

def solve_vrp(orders, dist_matrix, vehicle_capacity):
    bins = first_fit_decreasing(orders, vehicle_capacity)
    optimized_routes = {}

    for i, bin in enumerate(bins, start=1):
        route = ['r0']
        unvisited = set(n[0] for n in bin)
        while unvisited:
            current_location = int(route[-1][1:]) if route[-1] != 'r0' else 0
            next_stop = find_nearest(current_location, unvisited, dist_matrix)
            route.append(next_stop)
            unvisited.remove(next_stop)
        route.append('r0')
        optimized_routes[f'path{i}'] = route

    return optimized_routes

# Load the data
file_path = "path_to_your_file.json"
with open(f"C:\Student Handout\Input data\level1a.json", 'r') as file:
    data = json.load(file)

# Parse data
n_neighbourhoods = data['n_neighbourhoods']
neighborhoods = data['neighbourhoods']
restaurant_distances = data['restaurants']['r0']['neighbourhood_distance']
vehicle_capacity = data['vehicles']['v0']['capacity']

# Create distance matrix
dist_matrix = [[0] * (n_neighbourhoods + 1) for _ in range(n_neighbourhoods + 1)]
dist_matrix[0] = [0] + restaurant_distances
for i in range(n_neighbourhoods):
    dist_matrix[i + 1] = [restaurant_distances[i]] + neighborhoods[f'n{i}']['distances']

# Create orders list
orders = [(f'n{i}', neighborhoods[f'n{i}']['order_quantity']) for i in range(n_neighbourhoods)]

# Solve VRP
optimized_routes = solve_vrp(orders, dist_matrix, vehicle_capacity)

# Format and output results
output = {"v0": optimized_routes}
output_json = json.dumps(output, indent=2)
print(output_json)
with open("level1a_output.json", "w") as outfile:
    outfile.write(output_json)
'''

import json
import itertools

def first_fit_decreasing(orders, capacity):
    sorted_orders = sorted(orders, key=lambda x: x[1], reverse=True)
    bins = []
    for order in sorted_orders:
        placed = False
        for bin in bins:
            if sum(o[1] for o in bin) + order[1] <= capacity:
                bin.append(order)
                placed = True
                break
        if not placed:
            bins.append([order])
    return bins

def calculate_total_distance(route, dist_matrix):
    total_dist = 0
    for i in range(len(route) - 1):
        total_dist += dist_matrix[int(route[i][1:])][int(route[i+1][1:])]
    return total_dist

def find_optimal_route(slot, dist_matrix):
    min_route = None
    min_distance = float('inf')
    for perm in itertools.permutations(slot):
        current_route = ['r0'] + list(perm) + ['r0']
        current_distance = calculate_total_distance(current_route, dist_matrix)
        if current_distance < min_distance:
            min_distance = current_distance
            min_route = current_route
    return min_route

def solve_vrp(orders, dist_matrix, vehicle_capacity):
    bins = first_fit_decreasing(orders, vehicle_capacity)
    optimized_routes = {}

    for i, bin in enumerate(bins, start=1):
        slot = [n[0] for n in bin]
        optimized_route = find_optimal_route(slot, dist_matrix)
        optimized_routes[f'path{i}'] = optimized_route

    return optimized_routes

# Load the data
file_path = "C:\Student Handout\Input data\level1a.json"
with open(file_path, 'r') as file:
    data = json.load(file)

# Parse data
n_neighbourhoods = data['n_neighbourhoods']
neighborhoods = data['neighbourhoods']
restaurant_distances = data['restaurants']['r0']['neighbourhood_distance']
vehicle_capacity = data['vehicles']['v0']['capacity']

# Create distance matrix
dist_matrix = [[0] * (n_neighbourhoods + 1) for _ in range(n_neighbourhoods + 1)]
dist_matrix[0] = [0] + restaurant_distances
for i in range(n_neighbourhoods):
    dist_matrix[i + 1] = [restaurant_distances[i]] + neighborhoods[f'n{i}']['distances']

# Create orders list
orders = [(f'n{i}', neighborhoods[f'n{i}']['order_quantity']) for i in range(n_neighbourhoods)]

# Solve VRP
optimized_routes = solve_vrp(orders, dist_matrix, vehicle_capacity)

# Format and output results
output = {"v0": optimized_routes}
output_json = json.dumps(output, indent=2)
print(output_json)
with open("level1a_output.json", "w") as outfile:
    outfile.write(output_json)