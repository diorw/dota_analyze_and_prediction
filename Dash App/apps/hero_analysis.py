import pandas as pd
import plotly.graph_objects as go
match_example = ['114', '21', '96', '54', '68', '86', '98', '76', '8', '3']
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

    df = pd.read_csv("C:\\Users\\wda\\PycharmProjects\\Kitti\\dota_analyze_and_prediction\\Dash App\\data\\hero_stats.csv")
    id_to_name_dict = {}
    for index, items in df.iterrows():
        id_to_name_dict[str(items[0])] = items[3]
    df.columns = ["id",'pro_pick','pro_win','heor_name_ch','type']
    df['win_rate']=df['pro_win']/df['pro_pick']
    y = []
    for id in match_example:
        rate = df['win_rate'][df['id'] == int(id)].values.tolist()[0]
        y.append(rate)
    x1 = match_example[:5]
    x1 = list(map(lambda x:id_to_name_dict[x],x1))
    y1 = y[:5]
    x2 = match_example[5:]
    x2 = list(map(lambda x:id_to_name_dict[x],x2))
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