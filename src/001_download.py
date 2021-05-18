import json
import argparse
import yaml
import requests
import datetime
import os

import requests
import shutil

def download_img(url, file_name):
    r = requests.get(url, stream=True)
    if r.status_code == 200:
        with open(file_name, 'wb') as f:
            r.raw.decode_content = True
            shutil.copyfileobj(r.raw, f)

url = "https://hi-ut.github.io/dataset/iiif/collection/nishikie_hi.json"

df = requests.get(url).json()

opath = url.replace("https://hi-ut.github.io/dataset/iiif", "../iiif")

odir = os.path.dirname(opath)
os.makedirs(odir, exist_ok=True)

with open(opath, mode='wt', encoding='utf-8') as file:
    json.dump(df, file, ensure_ascii=False, indent=2)

manifests = df["manifests"]

fields = ["pid", "label", "order", "layout", "collection", "thumbnail", "full"] # "manifest", 

items = []

count = 0

for i in range(len(manifests)):
    m = manifests[i]

    uri = m["@id"]
    opath2 = uri.replace("https://hi-ut.github.io/dataset/iiif", "../iiif")

    if not os.path.exists:
        df2 = requests.get(uri).json()
        odir2 = os.path.dirname(opath2)
        os.makedirs(odir2, exist_ok=True)
        with open(opath2, mode='wt', encoding='utf-8') as file:
            json.dump(df2, file, ensure_ascii=False, indent=2)

    m = json.load(open(opath2, 'r'))

    id = str(i+1).zfill(4)

    map = {
        "pid": id,
        "order" : id,
        "layout" : "nishikie_item",
        "collection" : "qatar",
    }

    metadata = m["metadata"]

    for obj in metadata:
        f = obj["label"]
        v = obj["value"]

        map[f] = v

    map["label"] = map["題名"]

    items.append(map)

    

    ### 画像

    canvases = m["sequences"][0]["canvases"]

    for j in range(len(canvases)):
        url = canvases[j]["images"][0]["resource"]["@id"]
        opath3 = "../_data/raw_images/qatar/" + id + "/" + str(j+1).zfill(3) + ".jpg"

        if os.path.exists(opath3):
            continue
        odir3 = os.path.dirname(opath3)
        os.makedirs(odir3, exist_ok=True)
        download_img(url, opath3)

    path = "../img/derivatives/iiif/images/{}_001/info.json".format(id)
    # path = "../img/derivatives/simple/{}_001/thumbnail.jpg".format(id)

    

    if os.path.exists(path):
        # info = json.load(open(info_path, 'r'))

        
        map["thumbnail"] = "/img/derivatives/iiif/images/{}_001/full/250,/0/default.jpg".format(id)
        map["manifest"] = "/img/derivatives/iiif/{}/manifest.json".format(id)
        map["full"] = "/img/derivatives/iiif/images/{}_001/full/1140,/0/default.jpg".format(id)
        '''

        map["thumbnail"] = thumb_path.replace("../", "/")
        map["manifest_"] = uri
        map["full"] = "/img/derivatives/simple/{}_001/fullwidth.jpg".format(id)
        '''

    else:
        count += 1
        print("not exist", path, count)

    ### 最後。フィールドの取得。

    for f in map:
        if f not in fields:
            fields.append(f)

rows = []
row = []
for f in fields:
    row.append(f)

rows.append(row)

for item in items:
    row = []

    for f in fields:
        value = ""
        if f in item:
            value = item[f]
        row.append(value)

    rows.append(row)

import csv

with open('../_data/qatar.csv', 'w') as f:
    writer = csv.writer(f, lineterminator='\n') # 改行コード（\n）を指定しておく
    writer.writerows(rows) # 2次元配列も書き込める