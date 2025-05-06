from geopy.distance import geodesic
from math import floor
from pulp import *
import numpy as np

I_MASTER = [
    {"name": "京都駅", "point": 0, "pos": (34.98612252336533, 135.75900713517134), "genre": "", "time": 0},
    {"name": "清水寺", "point": 90.8, "pos": (34.994896155999626, 135.78505762495345), "genre": "", "time": 60},
    {"name": "伏見稲荷大社", "point": 88.8, "pos": (34.969657129060096, 135.7728481514741), "genre": "", "time": 30},
    {"name": "金閣寺", "point": 80.1, "pos": (35.03950268978778, 135.72921464464062), "genre": "", "time": 60},
    {"name": "竹林の小径", "point": 78.3, "pos": (35.01715832791134, 135.671708995212), "genre": "", "time": 10},
    {"name": "平等院", "point": 75.3, "pos": (34.88950964016094, 135.80770835137878), "genre": "", "time": 60},
    {"name": "四条大橋", "point": 72.4, "pos": (35.00402959513937, 135.77151686364257), "genre": "", "time": 10},
    {"name": "安井金比羅宮", "point": 71.7, "pos": (35.000297139304465, 135.7757950694608), "genre": "", "time": 30},
    {"name": "蓮華王院三十三間堂", "point": 69.7, "pos": (34.98788621088889, 135.77170305309815), "genre": "", "time": 30},
    {"name": "貴船神社", "point": 66.7, "pos": (35.121676473625904, 135.76299618835696), "genre": "", "time": 60},
    {"name": "高台寺", "point": 63.7, "pos": (35.00050406291363, 135.78121155032383), "genre": "", "time": 40},
    {"name": "産寧坂", "point": 61.2, "pos": (34.99634489550947, 135.78087739044003), "genre": "", "time": 15},
    {"name": "銀閣寺", "point": 60.5, "pos": (35.0270195964566, 135.79820352715907), "genre": "", "time": 60},
    {"name": "八坂神社", "point": 60.4, "pos": (35.003654801479, 135.77854736493805), "genre": "", "time": 20},
    {"name": "六波羅蜜寺", "point": 57.7, "pos": (34.997089418655754, 135.7733547141133), "genre": "", "time": 60},
    {"name": "京都御苑", "point": 57.5, "pos": (35.02302337108377, 135.7632801310468), "genre": "", "time": 60},
    {"name": "京都水族館", "point": 56.9, "pos": (34.98758902582941, 135.7476901197847), "genre": "", "time": 120},
    {"name": "天龍寺", "point": 56.6, "pos": (35.015810260550616, 135.67374401049895), "genre": "", "time": 30},
    {"name": "龍安寺", "point": 55.9, "pos": (35.03449382527828, 135.7182727249501), "genre": "", "time": 40},
    {"name": "御金神社", "point": 55.0, "pos": (35.01183577228355, 135.7550087267501), "genre": "", "time": 30},
    {"name": "京都府立植物園", "point": 55.0, "pos": (35.04872809703605, 135.76273539706312), "genre": "", "time": 60},
    {"name": "錦市場", "point": 54.7, "pos": (35.00498282888796, 135.76485812587416), "genre": "", "time": 60},
    {"name": "東福寺", "point": 54.7, "pos": (34.976058374855825, 135.77377661564265), "genre": "", "time": 60},
    {"name": "保津川下り", "point": 53.0, "pos": (35.02164660034919, 135.65578582447614), "genre": "", "time": 90},
    {"name": "京都国際マンガミュージアム", "point": 52.8, "pos": (35.01186574974091, 135.75946509043564), "genre": "", "time": 60},
    {"name": "嵯峨野トロッコ列車", "point": 52.1, "pos": (35.0185516104631, 135.68094142918588), "genre": "", "time": 120},
    {"name": "金剛寺八坂庚申堂", "point": 52.0, "pos": (34.99837213881018, 135.77873977740873), "genre": "", "time": 20},
    {"name": "渡月橋", "point": 49.9, "pos": (35.01285294993274, 135.6777523499701), "genre": "", "time": 10},
    {"name": "京都タワー", "point": 49.7, "pos": (34.98753165483453, 135.75931530680995), "genre": "", "time": 60},
    {"name": "南禅寺", "point": 46.5, "pos": (35.01140922690811, 135.79448106816488), "genre": "", "time": 60},
    {"name": "壬生寺", "point": 44.0, "pos": (35.001668797487646, 135.74337793070052), "genre": "", "time": 60},
    {"name": "花見小路通", "point": 42.5, "pos": (35.00549053173945, 135.77524293530766), "genre": "", "time": 20},
    {"name": "漢字ミュージアム", "point": 40.1, "pos": (35.00341892370984, 135.77661680871813), "genre": "", "time": 60},
    {"name": "京都国立近代美術館", "point": 39.3, "pos": (35.01236292263256, 135.7822085772071), "genre": "", "time": 60}
]

# 距離行列の作成
def create_distance_matrix(I):
    d = {}
    for i in I:
        for j in I:
            if i["name"] == j["name"]:
                d[i["name"], j["name"]] = 0
            else:
                dist_km = geodesic(i["pos"], j["pos"]).km
                speed_kmpm = 5 / 60  # 5 km/h = 0.083 km/min
                d[i["name"], j["name"]] = int(dist_km / speed_kmpm)
    return d

# 名前から観光地情報を取得
def get_list_name(name, I):
    for i in I:
        if i["name"] == name:
            return i
    return None

# 経路を再帰的に求める
def out_path(s, i, I, x):
    retstr = s["name"]
    for j in I:
        if i != j and value(x[i["name"], j["name"]]) == 1:
            retstr += "→" + j["name"]
            return retstr + out_path(s, j, I, x)
    return retstr

# 観光地ルート最適化
def solve_day(t, s, g, T, I):
    d = create_distance_matrix(I)
    a = {i["name"]: i["point"] for i in I}
    b = {i["name"]: i["time"] for i in I}
    x, y, f = {}, {}, {}
    n = len(I)

    if s != g:
        T += d[s["name"], g["name"]]

    prob = LpProblem("KyotoTour", sense=LpMaximize)

    for i in I:
        y[i['name']] = LpVariable(f"y({i['name']})", 0, 1, LpBinary)
        for j in I:
            if i != j:
                x[i['name'], j['name']] = LpVariable(f"x({i['name']},{j['name']})", 0, 1, LpBinary)
                f[i['name'], j['name']] = LpVariable(f"f({i['name']},{j['name']})", 0, None, LpInteger)

    # 目的関数
    prob += lpSum(y[i["name"]] * a[i["name"]] for i in I)

    # 時間制限
    prob += lpSum(d[i['name'], j['name']] * x[i['name'], j['name']] for i in I for j in I if i != j) + \
            lpSum(b[k['name']] * y[k['name']] for k in I) <= T

    # 出入りは1回
    for i in I:
        prob += lpSum(x[i['name'], j['name']] for j in I if i != j) == y[i['name']]
        prob += lpSum(x[j['name'], i['name']] for j in I if i != j) == y[i['name']]

    # フロー制約
    for i in I:
        if i != s:
            prob += lpSum(f[h['name'], i['name']] for h in I if i != h) + y[i['name']] == \
                    lpSum(f[i['name'], j['name']] for j in I if i != j)

    for i in I:
        for j in I:
            if i != j:
                prob += f[i['name'], j['name']] <= n * x[i['name'], j['name']]  # フロー制約の強化

    prob += y[s["name"]] == 1
    if s != g:
        prob += y[g["name"]] == 1
        prob += x[g["name"], s["name"]] == 1

    for j in I:
        if j != s:
            prob += f[s["name"], j['name']] == 0

    result = prob.solve()

    # プロブレムの状態を確認
    if result == 1:  # 成功した場合
        used_time = floor(value(lpSum(d[i['name'], j['name']] * x[i['name'], j['name']] for i in I for j in I if i != j) +
                                 lpSum(b[k['name']] * y[k['name']] for k in I)))
        route = out_path(s, s, I, x)[:-4]
        if s != g:
            used_time -= d[s["name"], g["name"]]
        else:
            route += "→" + g["name"]
        return {
            "status": "success",
            "day": t + 1,
            "route": route,
            "time_used": used_time,
            "score": value(prob.objective)
        }
    else:
        return {"status": "fail", "reason": "時間が不足しているか、解が存在しません"}

# 実行例
start = I_MASTER[0]  # 出発地点
goal = I_MASTER[-1]  # 最終地点
time_limit = 360  # 時間制限（分）

result = solve_day(0, start, goal, time_limit, I_MASTER)
print(result)
