import copy
import pathlib
import pandas as pd
from dash.dependencies import Input, Output, State, ClientsideFunction
import dash_core_components as dcc
import dash_html_components as html
from app import app
from datetime import datetime
import plotly.graph_objects as go
import requests
import json
import pymysql
from dash.exceptions import PreventUpdate
PATH = pathlib.Path(__file__).parent.parent
DATA_PATH = PATH.joinpath("data").resolve()

conn = pymysql.connect(host='120.55.167.182', user='root', password='wda20190707', port=3306, database='dota')
df = pd.read_csv("C:\\Users\\wda\\PycharmProjects\\Kitti\\dota_analyze_and_prediction\\Dash App\\data\hero_stats.csv", header=None)
id_to_name_dict = {}
for index, items in df.iterrows():
    id_to_name_dict[str(items[0])] = items[3]
id_to_name_dict['118'] = '紫猫'
id_to_name_dict['128'] = '蜥蜴绝手'

team_df = pd.read_sql("select * from dota.team",conn)
team_df.columns = ['team_id','team_name','win','lose','logo_url','rating','team_member','team_member_name']
player_id_to_name = {}
for index,row in team_df.iterrows():
    team_player_id = row[6].split(",")
    team_player_name = row[7].split(",")
    for i in range(len(team_player_id)):
        player_id_to_name[team_player_id[i]]=team_player_name[i]


hero_stats_df = pd.read_sql("select id,hero_name_ch from dota.hero_stats",conn)
hero_stats_df.columns = ['id','hero_name_ch']


def get_options():
    options = []

    for index,item in team_df.iterrows():
        if(index == 0):
            init_value = item['team_id']
        elif(index == 1):
            init_value_2 = item['team_id']
        options.append( {"label":item['team_name'],"value":item['team_id']})

    return options,init_value,init_value_2

options,init_value,init_value_2 = get_options()

layout = dict(
    autosize=True,
    automargin=True,
    margin=dict(l=30, r=30, b=20, t=40),
    hovermode="closest",
    # plot_bgcolor="#F9F9F9",
    # paper_bgcolor="#F9F9F9",
    legend=dict(font=dict(size=10), orientation="h"),
    title="Satellite Overview",

)

@app.callback(
    [Output("team_member","options"),Output("team_member","value")],
    [Input("team_select","value")]
)
def get_team_member(team_id):
    conn = pymysql.connect(host='120.55.167.182', user='root', password='wda20190707', port=3306, database='dota')
    cursor = conn.cursor()
    cursor.execute("select team_member,team_member_name from dota.team where team_id = %s",(team_id) )
    data = cursor.fetchall()[0]
    if(data != None):
        options = []
        player_id_list = data[0].split(",")
        player_id_name_list = data[1].split(",")
        for i in range(len(player_id_list)):
            options.append(
                {"label":player_id_name_list[i],"value":player_id_list[i]}
            )
        cursor.close()
        conn.close()
        # print(player_id_list)
        return options,[player_id_list[0]]

@app.callback(
    [Output("team_member_oppo","options"),Output("team_member_oppo","value")],
    [Input("team_select_oppo","value")]
)
def get_team_member(team_id):
    conn = pymysql.connect(host='120.55.167.182', user='root', password='wda20190707', port=3306, database='dota')
    cursor = conn.cursor()
    cursor.execute("select team_member,team_member_name from dota.team where team_id = %s",(team_id) )
    data = cursor.fetchall()[0]
    if(data != None):
        options = []
        player_id_list = data[0].split(",")
        player_id_name_list = data[1].split(",")
        for i in range(len(player_id_list)):
            options.append(
                {"label":player_id_name_list[i],"value":player_id_list[i]}
            )
        cursor.close()
        conn.close()
        return options,[player_id_list[0]]

@app.callback(
    Output("match_graph","figure"),
    [Input("team_select","value"),Input("team_select_oppo","value")]
)
def get_match_info(team_id,oppo_team_id):
    url = "https://api.opendota.com/api/teams/"+str(team_id)+"/matches?"

    datas = requests.get(url).json()[:100]
    wins = losses = 0
    for data in datas:
        if(str(data['opposing_team_id'])==str(oppo_team_id)):
            if(data['radiant']==data['radiant_win']):
                wins = wins + 1
            else:
                losses = losses + 1
    team_name = team_df[team_df['team_id']==int(team_id)]['team_name'].values.tolist()[0]
    oppo_team_name = team_df[team_df['team_id']==int(oppo_team_id)]['team_name'].values.tolist()[0]
    data = [
        dict(
            type="pie",
            labels=[team_name , oppo_team_name],
            values=[wins, losses],
            name="战队交战情况",
            text=[
                team_name +" 胜利",
                oppo_team_name+" 胜利",
            ],
            hoverinfo="text+value+percent",
            textinfo="label+percent+name",
            hole=0.5,
            marker=dict(colors=["#fac1b7", "#a9bb95"]),
            # domain={"x": [0, 0.45], "y": [0.2, 0.8]},
        )
    ]
    pie_layout = dict(title ='双方近期交战概况' )
    figure = dict(data = data,layout = pie_layout)
    return figure
# Create app layout

@app.callback(
    Output("hero_graph","figure"),
    [Input("team_select","value"),Input("team_select_oppo","value")]
)
def get_team_hero(team_id,oppo_team_id):
    team_url = "https://api.opendota.com/api/teams/"+str(team_id)+"/heroes"
    oppo_team_url = "https://api.opendota.com/api/teams/"+str(oppo_team_id)+"/heroes"
    team_datas = requests.get(team_url).json()[:10]
    oppo_team_datas = requests.get(oppo_team_url).json()[:10]

    team_name = team_df[team_df['team_id'] == int(team_id)]['team_name'].values.tolist()[0]
    oppo_team_name = team_df[team_df['team_id'] == int(oppo_team_id)]['team_name'].values.tolist()[0]
    def get_data(team_datas):
        x = []
        y = []
        size = []
        for data in team_datas:
            x.append(id_to_name_dict[str(data['hero_id'])])
            y.append(data['games_played'])
            size.append(80*data['wins']/data['games_played'])
        return x,y,size
    x,y,size = get_data(team_datas)
    x2,y2,size2 = get_data(oppo_team_datas)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x = x,y = y,mode = 'markers',name = team_name,marker=dict(size = size,color = '#fac1b7')))
    fig.add_trace(go.Scatter(x=  x2, y = y2, mode='markers',name = oppo_team_name,marker=dict(size=size2,color = '#a9bb95')))

    fig.update_layout(title = '战队双方擅长英雄(前10名)',yaxis_title = "使用场次",xaxis_title = '英雄名称')
    return fig

@app.callback(
    Output("duration_graph","figure"),
    [Input("team_member","value"),Input("team_member_oppo","value"),
    Input("team_select", "value"), Input("team_select_oppo", "value")],
)
def get_player_time(team_member_list,team_member_oppo_list,team_id,oppo_team_id):
    if(team_member_oppo_list is None or team_member_list is None):
        raise PreventUpdate
    team_name = team_df[team_df['team_id'] == int(team_id)]['team_name'].values.tolist()[0]
    oppo_team_name = team_df[team_df['team_id'] == int(oppo_team_id)]['team_name'].values.tolist()[0]
    duration_record_team = []
    for player in team_member_list:
        url = 'https://api.opendota.com/api/players/'+str(player)+'/recentMatches'
        datas = requests.get(url).json()
        duration = 0
        for data in datas:
            duration+=data['duration']/60
        duration_record_team.append(duration)

    duration_record_oppo_team = []
    for player in team_member_oppo_list:
        url = 'https://api.opendota.com/api/players/'+str(player)+'/recentMatches'
        datas = requests.get(url).json()
        duration = 0
        for data in datas:
            duration+=int(data['duration']/60)
        duration_record_oppo_team.append(duration)
    fig = go.Figure()
    team_member_list = list(map(lambda x:player_id_to_name[x],team_member_list))
    team_member_oppo_list = list(map(lambda x: player_id_to_name[x], team_member_oppo_list))
    fig.add_trace(go.Bar(x=team_member_list,y=duration_record_team,name = team_name,marker_color='#fac1b7'))
    fig.add_trace(go.Bar(x=team_member_oppo_list, y=duration_record_oppo_team, name=oppo_team_name,marker_color = '#a9bb95'))
    fig.update_layout(title = '双方队员近期上线时长',xaxis_title = '队员名称',yaxis_title = '游戏时长(分钟)')
    return fig

@app.callback(
    [Output("team_win","children"),Output("team_lose","children"),Output("team_rating","children"),Output("team_rank","children")],
    [Input("team_select", "value")]
)
def get_team_info(team_id):
    conn = pymysql.connect(host='120.55.167.182', user='root', password='wda20190707', port=3306, database='dota')
    cursor = conn.cursor()
    cursor.execute("select win,lose,rating from dota.team where team_id = %s" % team_id)
    data = cursor.fetchone()
    team_win = data[0]
    team_lose = data[1]
    team_rating = data[2]
    df = pd.read_sql("select team_id from dota.team order by rating desc",conn)
    team_rank = '?'
    for index,rows in df.iterrows():
        if(str(rows[0])==str(team_id)):
            team_rank = index+1
    cursor.close()
    conn.close()
    return str(team_win),str(team_lose),str(team_rating),str(team_rank)

@app.callback(
    [Output("oppo_team_win","children"),Output("oppo_team_lose","children"),Output("oppo_team_rating","children"),Output("oppo_team_rank","children")],
    [Input("team_select_oppo", "value")]
)
def get_oppo_team_info(team_id):
    conn = pymysql.connect(host='120.55.167.182', user='root', password='wda20190707', port=3306, database='dota')
    cursor = conn.cursor()
    cursor.execute("select win,lose,rating from dota.team where team_id = %s" % team_id)
    data = cursor.fetchone()
    team_win = data[0]
    team_lose = data[1]
    team_rating = data[2]
    df = pd.read_sql("select team_id from dota.team order by rating desc",conn)
    team_rank = '?'
    for index,rows in df.iterrows():
        if(str(rows[0])==str(team_id)):
            team_rank = index+1
    cursor.close()
    conn.close()
    return str(team_win),str(team_lose),str(team_rating),str(team_rank)

@app.callback(
    Output("player_rank_graph","figure"),
    [Input("team_select", "value"), Input("team_select_oppo", "value")],
)
def get_player_rank(team_id,oppo_team_id):
    team_name = team_df[team_df['team_id'] == int(team_id)]['team_name'].values.tolist()[0]
    oppo_team_name = team_df[team_df['team_id'] == int(oppo_team_id)]['team_name'].values.tolist()[0]
    team_member = str(team_df[team_df['team_id'] == int(team_id)]['team_member'].values.tolist()[0]).split(",")
    oppo_team_member = str(team_df[team_df['team_id'] == int(oppo_team_id)]['team_member'].values.tolist()[0]).split(",")
    team_member_name = str(team_df[team_df['team_id'] == int(team_id)]['team_member_name'].values.tolist()[0]).split(",")
    oppo_team_member_name = str(team_df[team_df['team_id'] == int(oppo_team_id)]['team_member_name'].values.tolist()[0]).split(
        ",")
    rank1 = []
    rank2 = []
    print(team_member)
    for member in team_member:
        url = 'https://api.opendota.com/api/players/' + str(member)

        datas = requests.get(url).json()

        rank = datas['leaderboard_rank']
        rank1.append(rank)
    for member in oppo_team_member:
        url = 'https://api.opendota.com/api/players/' + str(member)
        datas = requests.get(url).json()
        rank_oppo = datas['leaderboard_rank']
        rank2.append(rank_oppo)
    print(rank1)
    print(rank2)
    fig = go.Figure()

    fig.add_trace(go.Bar(x=team_member_name,y=rank1,name = team_name,marker_color='#fac1b7'))
    fig.add_trace(go.Bar(x=oppo_team_member_name, y=rank2, name=oppo_team_name,marker_color = '#a9bb95'))
    fig.update_layout(title = '双方队员实力对比',xaxis_title = '队员名称',yaxis_title = '天梯排名')
    return fig

team_layout = html.Div(
    [
        # empty Div to trigger javascript file for graph resizing
        html.Div(
            [
                html.Div(
                    [
                        html.Div(
                            [
                                html.H3(
                                    "战队信息查询",
                                    style={"margin-bottom": "0px","color":"#FFFFFF"},
                                )
                            ]
                        )
                    ],
                    className="one-half column",
                    id="title",
                )
            ],
            id="header",
            className="row flex-display",
            style={"margin-bottom": "25px"},
            # 头
        ),
        html.Div(
            [
                html.Div(
                    [
                        html.P(
                            "战队名称",
                            className="control_label",
                        ),
                        dcc.Dropdown(
                            id="team_select",
                            options=options,
                            value = init_value,
                            className="dcc_control",
                        ),
                        html.P("战队成员", className="control_label"),
                        dcc.Checklist(
                            id="team_member",
                            labelStyle={"display": "inline-block"},
                            className="dcc_control",
                        ),

                        html.P(
                            "对手战队名称",
                            className="control_label",
                        ),
                        dcc.Dropdown(
                            id="team_select_oppo",
                            options = options,
                            value = init_value_2,

                            className="dcc_control",
                        ),
                        html.P("敌方战队成员", className="control_label"),
                        dcc.Checklist(
                            id="team_member_oppo",
                            labelStyle={"display": "inline-block"},
                            className="dcc_control",
                        )
                    ],
                    className="pretty_container four columns",
                    id="cross-filter-options"
                ),
                html.Div(
                    [
                        html.Div(
                            [
                                html.Div(
                                    [html.H6(id="team_win"), html.P("胜利场次")],
                                    id="wells",
                                    className="mini_container",
                                ),
                                html.Div(
                                    [html.H6(id="team_lose"), html.P("失败场次")],
                                    id="gas",
                                    className="mini_container",
                                ),
                                html.Div(
                                    [html.H6( id="team_rating"), html.P("战队rating")],
                                    id="oil",
                                    className="mini_container",
                                ),
                                html.Div(
                                    [html.H6(id="team_rank"), html.P("战队排名")],
                                    id="water",
                                    className="mini_container",
                                ),
                            ],
                            id="info-container",
                            className="row container-display",
                        ),
                        html.Div(
                            [
                                html.Div(
                                    [html.H6(id="oppo_team_win"), html.P("对手胜利场次")],
                                    id="wins",
                                    className="mini_container",
                                ),
                                html.Div(
                                    [html.H6(id="oppo_team_lose"), html.P("对手失败场次")],
                                    id="losses",
                                    className="mini_container",
                                ),
                                html.Div(
                                    [html.H6( id="oppo_team_rating"), html.P("对手战队rating")],
                                    id="rating",
                                    className="mini_container",
                                ),
                                html.Div(
                                    [html.H6(id="oppo_team_rank"), html.P("对手战队排名")],
                                    id="rank",
                                    className="mini_container",
                                ),
                            ],
                            id="info-container",
                            className="row container-display",
                        ),
                        # html.Div(
                        #
                        #     [dcc.Loading(id='count_graph_loading', type='default')
                        #      ],
                        #     id="countGraphContainer",
                        #     className="pretty_container"
                        #
                        # ),
                    ],
                    id="right-column",
                    className="eight columns",
                ),
            ],
            className="row flex-display",
        ),
        html.Div(
            [
                html.Div(
                    [dcc.Graph(id="match_graph")],
                    className="pretty_container five columns",
                )
                ,
                html.Div(
                    [dcc.Graph(id="hero_graph")],
                    className="pretty_container seven columns",
                ),
            ],
            className="row flex-display",
        ),
        html.Div(
            [
                html.Div(
                    [dcc.Graph(id="duration_graph")],
                    className="pretty_container five columns",
                )
                ,
                html.Div(
                    [dcc.Graph(id="player_rank_graph")],
                    className="pretty_container seven columns"

                ),
            ],
            className="row flex-display",
        ),
    ],
    id="mainContainer",
    style={"display": "flex", "flex-direction": "column"},
)


# Main
# if __name__ == "__main__":
#     app.run_server(debug=True)