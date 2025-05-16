from flask import Flask, request, jsonify
from flask_cors import CORS
from utils.optimizer import I_MASTER, get_list_name, solve_day

app = Flask(__name__)
CORS(app, origins=["https://4-q1.github.io"])

@app.route("/")
def index():
    return "running"

@app.route("/optimize", methods=["POST"])
def optimize():
    data = request.json
    days = data.get("days")
    limits = data.get("time_limits")
    destinations = data.get("via")

    # 入力チェック
    if not isinstance(days, int) or not isinstance(limits, list) or not isinstance(destinations, list):
        return jsonify({"status": "fail", "reason": "不正な形式です"}), 400
    if len(limits) != days or len(destinations) != days:
        return jsonify({"status": "fail", "reason": "日数と配列の長さが一致しません"}), 400

    I = I_MASTER.copy()
    start = get_list_name("京都駅", I)
    if start is None:
        return jsonify({"status": "fail", "reason": "京都駅が地点リストに存在しません"}), 500

    results = []

    for t in range(days):
        goal = get_list_name(destinations[t], I)
        if goal is None:
            return jsonify({"status": "fail", "reason": f"{destinations[t]} が地点リストに存在しません"}), 400

        result = solve_day(t, start, goal, limits[t], I)
        results.append(result)
        start = goal

    return jsonify(results)

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=8000)
