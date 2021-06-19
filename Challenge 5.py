#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from neobase import NeoBase
from flask import Flask, request, jsonify

#usamos los ficheros sin registros repetidos
bookings_path = "/home/dsc/data/challenge/bookings_clean.csv"

df_acum = pd.DataFrame()
chunksize = 100000 #10?
reader = pd.read_csv(bookings_path,
                     memory_map = True, 
                     error_bad_lines = False, 
                     usecols=["arr_port","pax"], 
                     chunksize=chunksize)    

for chunk in reader:  
    chunk["arr_port"] = chunk["arr_port"].str.strip()
    chunk = chunk[chunk["arr_port"].str.len() == 3]
    curr = chunk.groupby(by="arr_port").sum()
    df_acum = df_acum.append(curr)

b = NeoBase()
result = df_acum.groupby(by="arr_port").sum().sort_values(by="pax", ascending=False)[0:10]
result = result.astype({"pax": int})
result["City"] = result.index.map(lambda x: b.get(x, "city_name_list")[0])
result["arr_port"] = result.index

#ahora crear una aplicación básica usando flask


app = Flask(__name__)


@app.route("/get_nth_destination", methods=["GET"])
def get_nth_destination():
    try:
        n = request.args.get("n", type=int)
        row = result.iloc[n]
        return (row.to_json())
    except:
        return jsonify({"message": "something went wrong"})
    
if __name__ == '__main__':
    app.run(host='127.0.0.1', debug=False, port=5000)