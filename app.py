from flask import Flask, render_template, request, jsonify
from pathfinding.core.diagonal_movement import DiagonalMovement
from pathfinding.core.grid import Grid
from pathfinding.finder.a_star import AStarFinder
from pymongo import MongoClient
import uuid
import time
import threading

app = Flask(__name__)

client = MongoClient(
    "mongodb+srv://King:kNK05AcfMXEmttfR@cluster0.hvhrx.mongodb.net/myFirstDatabase?retryWrites=true&w=majority")
db = client.Assemble
drones = db.drones
packages = db.packages


# View Drones
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
        drones.insert_one({'name': n['name'], 'fuel': 100, 'status': 'idle'})
    output = "Drone added successfully"
    return jsonify({"result": output})


# Add Packages
@app.route('/add/delivery', methods=['POST'])
def add_delivery():
    data = request.json
    i = 0
    while i < len(data):
        packages.insert_one(
            {'uid': str(uuid.uuid4()), 'name': data[i]['name'], 'weight': data[i]['weight'],
             'destination': data[i]['destination'], 'status': 'scheduled'})
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

        p_distance = len(path) - 1
        distance = p_distance * 2

        all_packages.append({'distance': f"{distance}km", 'name': package['name']})
    print(all_packages)
    return jsonify({'Packages': all_packages})


# Single Drone
@app.route('/<name>')
def view_one_drone(name):
    drone = drones.find_one({'name': name})

    if drone:
        output = {'name': drone['name']}
    else:
        output = 'No Drone Found'

    return jsonify({'Drone': output})


# @app.route('/assign')
# def assign():
#    all_drones = drones.find({"status": "idle"})
#    all_packages = packages.find({"status": "scheduled"})
#    droned = list(all_drones)
#    packaged = list(all_packages)
#    drone_packages = zip(droned, packaged)
#    dp = list(drone_packages)
#    i = 0
#    while i < len(dp):
#        print(drone_packages)
#        uid = packaged[i]['uid']
#        p_name = packaged[i]['name']
#        d_name = droned[i]['name']

#        drones.update_one(
#            {"status": "idle"},
#            {
#                "$set": {"package": packaged[i], "status": "active"},
#            }
#        )
#        packages.update_one({"uid": uid}, {"$set": {"status": "in-transit", "drone": d_name}})

#        drones.update_one({"package.name": p_name}, {"$set": {"package.status": "in-transit"}})

#        i += 1

#    return 'done'


@app.route('/check')
def check():
    drones.update_one({"package.name": "TV"}, {"$set": {"package.status": "in-transit"}})
    return 'done'


@app.route('/status')
def dev_status():
    packing = []

    for package in packages.find():
        print(package['drone'])
    return 'done'

# Assign Packages To Drones
def assigned():
    while True:
        idle_drones = drones.find({"status": "idle"})
        list_packages = packages.find({"status": "scheduled"})
        droned = list(idle_drones)
        packaged = list(list_packages)
        drone_packages = zip(droned, packaged)
        dp = list(drone_packages)
        i = 0
        while i < len(dp):
            print(drone_packages)
            uid = packaged[i]['uid']
            p_name = packaged[i]['name']
            d_name = droned[i]['name']

            drones.update_one(
                {"status": "idle"},
                {
                    "$set": {"package": packaged[i], "status": "active"},
                }
            )
            packages.update_one({"uid": uid}, {"$set": {"status": "in-transit", "drone": d_name}})

            drones.update_one({"package.name": p_name}, {"$set": {"package.status": "in-transit"}})

            i += 1

        time.sleep(10)


#   change package status
def package_status():
    while True:
        for pack in packages.find({"status": "in-transit"}):
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

            x = pack['destination'][0]
            y = pack['destination'][1]
            end = grid.node(x, y)
            finder = AStarFinder(diagonal_movement=DiagonalMovement.always)
            path, runs = finder.find_path(start, end, grid)

            p_distance = len(path) - 1
            distance = p_distance * 2

            in_speed = 80
            weight = pack['weight']
            numbers = ''.join(filter(lambda n: n.isdigit(), weight))
            number = int(numbers)
            travel_speed = in_speed - number * 2
            ta = distance / travel_speed
            eta = ta * 60
            eta_secs = eta * 60
            time.sleep(eta_secs)
            packages.update_one({"name": pack['name']}, {"$set": {"status": "delivered"}})
            drones.update_one({"package.name": pack['name']}, {"$unset": {"package": ""}})
            drones.update_one({"status": "active"}, {"$set": {"status": "idle"}})


threading.Thread(target=assigned).start()
threading.Thread(target=package_status).start()

if __name__ == '__main__':
    app.run()
