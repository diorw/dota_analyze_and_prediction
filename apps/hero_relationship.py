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
    conn = pymysql.connect(host = '120.55.167.182',user = 'root',password = 'wda20190707',port = 3306,database = 'dota')
    cursor = conn.cursor()
    max_update_ymd_sql = 'select max(update_ymd) from hero_relationship'
    cursor.execute(max_update_ymd_sql)
    max_update_ymd_list = cursor.fetchall()
    max_update_ymd = max_update_ymd_list[0]
    query = "select win_rate from hero_relationship where update_ymd = %s and hero_id = %s and target_hero_id = %s and match_count > 10"
    elements = [
        {
            'data': {'id': 'tian_hui', 'label': '天辉'}
        },
        {
            'data': {'id': 'ye_yan', 'label': '夜宴'}
        }
    ]
    def query_win_rate(hero_id,target_hero_id):
        cursor.execute(query,(max_update_ymd,hero_id,target_hero_id))
        win_rate = cursor.fetchall()
        #print(win_rate)
        if(len(win_rate)>0 and len(win_rate[0])> 0 and win_rate[0][0] is not None):
            if(win_rate[0][0]>0.6 or win_rate[0][0]<0.4):
                return win_rate[0][0]
            else:
                return None
        else:
            return None
    for i in range(10):
        data = {'id': str(i), 'label': id_to_name_dict[match_example[i]], 'parent': 'tian_hui' if i < 5 else 'ye_yan',
                'url':"C:\\Users\\wda\\PycharmProjects\\Kitti\\dota_analyze_and_prediction\\assets\\hero_icon\\"+id_to_name_dict[match_example[i]]+"_full.png"}
        position = {'x': 100 if i < 5 else 400, 'y':  100 * (i + 1) if i < 5 else 100*(i-4)}
        node = {'data': data, 'position': position,'classes':'countries'}
        elements.append(node)
    for i in range(5):
        for j in range(5, 10):
            data = {'source': str(i), 'target': str(j),'label':query_win_rate(match_example[i],match_example[j])}

            if(data['label'] is not None):
                if(data['label'] > 0.6):
                    edges = {'data': data, 'classes': 'tianhui_yeyan'}
                else:
                    edges = {'data': data, 'classes': 'yeyan_tianhui'}
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
                'selector': 'edge',
                'style': {
                    # The default curve style does not work with certain arrows
                    'curve-style': 'bezier'
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
            },
            {
                'selector':'.yeyan_tianhui',
                'style':{
                    'source-arrow-color': 'green',
                    'target-arrow-shape': 'vee',
                    'line-color': 'green',
                    'label':'data(label)'
                }
            },
            {
                'selector':'.tianhui_yeyan',
                'style':{
                    'source-arrow-color': 'red',
                    'target-arrow-shape': 'vee',
                    'line-color': 'red',
                    'label':'data(label)'
                }
            },

        ],
        elements = generate_elements(match_example)
    )
])

if __name__ == "__main__":

    app.run_server(debug=True)

