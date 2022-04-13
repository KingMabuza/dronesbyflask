from flask import Flask, render_template, request, jsonify
from pathfinding.core.diagonal_movement import DiagonalMovement
from pathfinding.core.grid import Grid
from pathfinding.finder.a_star import AStarFinder
from pymongo import MongoClient

app = Flask(__name__)

client = MongoClient(
    "mongodb+srv://King:kNK05AcfMXEmttfR@cluster0.hvhrx.mongodb.net/myFirstDatabase?retryWrites=true&w=majority")
db = client.Assemble
drones = db.drones
packages = db.packages


# all drones
@app.route('/')
def view_all_drones():
    all_drones = []

    for drone in drones.find():
        all_drones.append({'name': drone['name']})
    return jsonify({'Drones': all_drones})


# Add Drone
@app.route('/add/drone', methods=['POST'])
def add_drone():
    name = request.json
    for n in name:
        drones.insert_one({'name': n['name']})
    output = "Drone added successfully"
    return jsonify({"result": output})


# Add Packages
@app.route('/add/delivery', methods=['POST'])
def add_delivery():
    data = request.json
    i = 0
    while i < len(data):
        packages.insert_one(
            {'name': data[i]['name'], 'weight': data[i]['weight'], 'destination': data[i]['destination']})
        i += 1
    output = "Delivery scheduled successfully"
    return jsonify({"result": output})


# View Packages
@app.route('/packages')
def view_deliveries():
    all_packages = []

    for package in packages.find():
        matrix = [
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
        ]

        grid = Grid(matrix=matrix)

        start = grid.node(0, 0)

        x = package['destination'][0]
        y = package['destination'][1]
        end = grid.node(x, y)
        finder = AStarFinder(diagonal_movement=DiagonalMovement.always)
        path, runs = finder.find_path(start, end, grid)
        print(path)

        distance = len(path) * 2
        # add distance
        all_packages.append({'name': package['name'], 'distance': f"{distance}km"})
    print(all_packages)
    return jsonify({'Drones': all_packages})


# Single Drone
@app.route('/<name>')
def view_one_drone(name):
    drone = drones.find_one({'name': name})

    if drone:
        output = {'name': drone['name']}
    else:
        output = 'No Drone Found'

    return jsonify({'Drone': output})


if __name__ == '__main__':
    app.run()
