import pandas as pd
import matplotlib.pyplot as plt
import lightgbm as lgb
import plotly
import numpy as np
from pyecharts.charts import Radar


def plot_radar(series_radiant,series_dire):
    c_schema = [{"name": "控制", "max": 15, "min": 0},
                {"name": "核心", "max": 15, "min": 0},
                {"name": "辅助", "max": 15, "min": 0},
                {"name": "逃生", "max": 15, "min": 0},
                {"name": "爆发", "max": 15, "min": 0},
                {"name": "先手", "max": 15, "min": 0},
                {"name": "耐久", "max": 15, "min": 0},
                {"name": "推进", "max": 15, "min": 0}]
    radar = Radar()
    radar.add_schema(
        schema=c_schema
    )
    radar.add("radiant", series_radiant,color="#f9713c")
    radar.add("dire", series_dire,color = "#b3e4a1")
    radar.render("Rader.html")


def get_row_to_list(df, columns, row_index):
    var = df[row_index:row_index+1][columns]
    var2 = var.values.flatten()
    result_list = [var2.tolist()]
    return result_list


temp_df = pd.read_csv("../input/temp.csv")
attribute = ['kongzhi', 'hexin', 'fuzhu', 'taosheng', 'baofa', 'xianshou', 'naijiu', 'tuijin']
player_columns = []

for i in range(10):
    player_columns.append("player_"+str(i)+"_hero_id")

attribute_columns = ["target"]
for i in range(8):
    attribute_columns.append("radiant_"+attribute[i])
    attribute_columns.append("dire_"+attribute[i])

columns = [None] + player_columns + attribute_columns

temp_df.columns = columns

hero_df = temp_df[player_columns]

attr_df = temp_df[attribute_columns]
print(attr_df.head(5))

target = attr_df['target']
del attr_df['target']

# 画雷达图
# radient = list(map(lambda x:"radiant_"+x,attribute))
# radient_example_list = get_row_to_list(attr_df,radient,1)
# dire = list(map(lambda x:"dire_"+x,attribute))
# dire_example_list = get_row_to_list(attr_df,dire,1)
# plot_radar(radient_example_list,dire_example_list)

for dim in attribute:
    attr_df[dim+"_diff"] = attr_df["radiant_"+dim]-attr_df["dire_"+dim]





