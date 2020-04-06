import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import numpy as np
import pymysql
import requests
import plotly.graph_objects as go
headers = {'Accept': 'text/html, application/xhtml+xml, image/jxr, */*',
           'Accept - Encoding': 'gzip, deflate',
           'Accept-Language': 'zh-Hans-CN, zh-Hans; q=0.5',
           'Connection': 'Keep-Alive',
           'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                         'Chrome/52.0.2743.116 Safari/537.36 Edge/15.15063'}
if __name__ == "__main__":
    player_id_list = ['152461420','205144888','143182355','89115202','140973920','255319952','129365110','260241404','207212099','187938206']
    match_example = ['114','21','96','54','68','86','98','76','8','3']
    df = pd.read_csv("C:\\Users\\wda\\PycharmProjects\\Kitti\\dota_analyze_and_prediction\\Dash App\\data\\hero_stats.csv")
    id_to_name_dict = {}
    for index, items in df.iterrows():
        id_to_name_dict[str(items[0])] = items[3]
    match_count = []
    win = []
    conn = pymysql.connect(host='120.55.167.182', user='root', password='wda20190707', port=3306, database='dota')

    for i in range(10):
        player_id = player_id_list[i]
        hero_id = match_example[i]

        cursor = conn.cursor()
        cursor.execute("select games,games_win from player_hero where account_id = %s and hero_id = %s",(player_id,hero_id))
        result = cursor.fetchone()
        if(result!=None and len(result)>0):
            print(result)
            match_count.append(result[0])
            win.append(result[1])
        else:
            re = requests.get("https://api.opendota.com/api/players/"+player_id+"/heroes?hero_id="+str(hero_id),headers = headers)
            if(re.status_code==200):
                json = re.json()[0]
                win_counts = json['win']
                games = json['games']
                win.append(win_counts)
                match_count.append(games)

    x = list(map(lambda x:id_to_name_dict[x],match_example))
    figure = go.Figure(data=[
        go.Bar(name='使用场次',x=x,y=match_count),
        go.Bar(name='胜利场次',x=x,y=win)
    ])
    figure.update_layout(barmode='stack')
    figure.show()



