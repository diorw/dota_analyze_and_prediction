import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import pymysql
match_example = ['16', '107', '93', '56', '27', '8', '26', '14', '101', '41']
if __name__ == "__main__":
    # conn = pymysql.connect()
    # cursor = conn.cursor()
    # query_sql = 'select id,pro_pick,pro_ban,pro_win from hero_stats'
    # cursor.execute(query_sql)
    # datalist = cursor.fetchall()
    # datalist = list(map(list,datalist))
    # df = pd.DataFrame(datalist,columns = ['id','pro_pick','pro_ban','pro_win'])
    # df['win_rate'] = df['pro_win']/df['pro_pick']
    # df.to_csv("../assets/hero_stats.csv")

    df = pd.read_csv("../assets/hero_stats.csv")
    y = []
    for id in match_example:
        rate = df['win_rate'][df['id'] == int(id)].values.tolist()[0]
        y.append(rate)
    print(y)

    x1 = match_example[:5]
    y1 = y[:5]

    x2 = match_example[5:]
    y2 = y[5:]
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=x1, y=y1,
        name='天辉',
        mode='markers',
        marker_color='rgba(152, 0, 0, .8)'
    ))
    #
    fig.add_trace(go.Scatter(
        x=x2, y=y2,
        name='夜魇',
        marker_color='rgba(255, 182, 193, .9)'
    ))
    #
    # # Set options common to all traces with fig.update_traces
    fig.update_traces(mode='markers', marker_line_width=2, marker_size=10)
    fig.update_layout(title='Styled Scatter',
                      yaxis_zeroline=False, xaxis_zeroline=False)

    fig.show()