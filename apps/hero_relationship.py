import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import numpy as np
import pandas as pd
import pymysql
import dash_cytoscape as cyto
from PIL import Image
import matplotlib.pyplot as plt
df = pd.read_csv("../../dota_hero_stats.csv", header=None)
id_to_name_dict = {}
for index, items in df.iterrows():
    id_to_name_dict[str(items[1])] = items[0][14:]
# test
match_example = ['16', '107', '93', '56', '27', '8', '26', '14', '101', '41']


def generate_elements(match_example):
    elements = [
        {
            'data': {'id': 'tian_hui', 'label': '天辉'}
        },
        {
            'data': {'id': 'ye_yan', 'label': '夜宴'}
        }
    ]

    for i in range(10):
        data = {'id': str(i), 'label': id_to_name_dict[match_example[i]], 'parent': 'tian_hui' if i < 5 else 'ye_yan',
                'url':"C:\\Users\\wda\\PycharmProjects\\Kitti\\dota_analyze_and_prediction\\assets\\hero_icon\\"+id_to_name_dict[match_example[i]]+"_full.png"}
        position = {'x': 100 if i < 5 else 400, 'y':  100 * (i + 1) if i < 5 else 100*(i-4)}
        node = {'data': data, 'position': position,'classes':'countries'}
        elements.append(node)
    for i in range(5):
        for j in range(5, 10):
            data = {'source': str(i), 'target': str(j)}
            edges = {'data': data, 'classes': 'cities'}
            elements.append(edges)

            data_op = {'source': str(j), 'target': str(i)}
            edges = {'data': data_op, 'classes': 'cities'}
            elements.append(edges)

    return elements


app = dash.Dash(__name__)
app.layout = html.Div([
    cyto.Cytoscape(
        id='cytoscape-compound',
        layout={'name': 'preset'},
        style={'width': '100%', 'height': '800px'},
        stylesheet = [
            {
                'selector': 'node',
                'style': {
                    'content': 'data(label)'
                }
            },
            {
                'selector': '.terminal',
                'style': {
                    'width': 90,
                    'height': 80,
                    'background-fit': 'cover',
                    'background-image': 'data(url)'
                }
            }
        ],
        elements = generate_elements(match_example)
    )
])

if __name__ == "__main__":

    app.run_server(debug=True)

