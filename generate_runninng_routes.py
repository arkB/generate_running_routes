import argparse
import random
import requests
import gpxpy
import re

# Graphhopper API KEY
MY_API_KEY = ""

# 入力
parser = argparse.ArgumentParser(description="走行経路用のGoogleマップURLを自動生成するプログラム")
parser.add_argument("lat", help="開始・終了地点の緯度")
parser.add_argument("lon", help="開始・終了地点の経度")
parser.add_argument("per", type=float, help="経路の長さ[km]")

args = parser.parse_args()

# 入力オプション
start_pos = f"{args.lat}, {args.lon}"  # ルート生成開始位置(緯度,軽度)
perimeter = f"{args.per * 1000}"  # 走行想定距離

# Graph Hopperから経路を取得するためのURL
url = f""

# 経路生成シード値の作成
new_route_flg = False
while not new_route_flg:
    # シード値の生成
    random.seed()
    seed = random.randint(0, 2 * 63 - 1)
    # 過去の生成履歴と照合
    with open("generator_seed_log.txt", "r") as f:
        for line in f:
            list = line.split(",")
            if (args.lat == list[0] and args.lon == list[1] and args.per == list[2] and seed == list[3]):
                break
        new_route_flg = True
    # 初めての経路であれば記録
    url = f"https://graphhopper.com/api/1/route?point={start_pos}&profile=car&ch.disable=true&pass_through=true&algorithm=round_trip&round_trip.distance={perimeter}&round_trip.seed={seed}&key={MY_API_KEY}&type=gpx"
    print(url)
    with open("generator_seed_log.txt", "a") as f:
        f.write(f"{args.lat},{args.lon},{args.per},{seed}\n")

res = requests.get(url)
gpx = gpxpy.parse(res.content)

# GPXファイルを変換
route = gpx.to_xml()
route = route.split("\n")

url = "https://google.co.jp/maps/dir/"

point = []
for line in route:
    lat = re.findall(r"lat=\"(.*)\" ", line)
    lon = re.findall(r"lon=\"(.*)\"", line)
    if len(lat) > 0 and len(lon) > 0:
        lat = lat[0]
        lon = lon[0]
        point.append({"lat": lat, "lon": lon})

# 経由地の数
waypoint = 9

pickup_idx = [int(i / (waypoint - 1) * (len(point) - 1)) for i in range(waypoint)]

for i in range(waypoint):
    url += point[pickup_idx[i]]["lat"] + "," + point[pickup_idx[i]]["lon"] + "/"


# 出力
print(url)
