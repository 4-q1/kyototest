from flask import Flask, request, jsonify
from utils.optimizer import I_MASTER, get_list_name, solve_day

app = Flask(__name__)

@app.route("/optimize", methods=["POST"])
def optimize():
    data = request.json
    days = data.get("days")
    limits = data.get("time_limits")
    destinations = data.get("via")
    
    I = I_MASTER.copy()
    start = get_list_name("京都駅", I)
    results = []

    for t in range(days):
        goal = get_list_name(destinations[t], I)
        result = solve_day(t, start, goal, limits[t], I)
        results.append(result)
        start = goal

    return jsonify(results)
