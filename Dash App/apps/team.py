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
PATH = pathlib.Path(__file__).parent.parent
DATA_PATH = PATH.joinpath("data").resolve()

conn = pymysql.connect(host='120.55.167.182', user='root', password='wda20190707', port=3306, database='dota')

team_df = pd.read_sql("select team_id,team_name from dota.team",conn)
team_df.columns = ['team_id','team_name']
print(team_df)

def get_options():
    options = []
    for index,item in team_df.iterrows():
        options.append( {"label":item['team_name'],"value":item['team_id']})
    return options

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
    Output("team_member","options"),
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
        return options

@app.callback(
    Output("team_member_oppo","options"),
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
        return options

@app.callback(
    Output("match_graph","figure"),
    [Input("team_select","value"),Input("team_select_oppo","value")]
)
def get_match_info(team_id,oppo_team_id):
    url = "https://api.opendota.com/api/teams/"+str(team_id)+"/matches?"

    datas = requests.get(url).json()[:40]
    wins = losses = 0
    for data in datas:
        print(str(data['opposing_team_id'])==str(oppo_team_id))
        if(str(data['opposing_team_id'])==str(oppo_team_id)):
            if(data['radiant']==data['radiant_win']):
                wins = wins + 1
            else:
                losses = losses + 1
    print([wins,losses])
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
                                    style={"margin-bottom": "0px"},
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
                            options=get_options(),
                            value='2586976',
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
                            options = get_options(),
                            value='15',
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
                                    [html.H6("565", id="team_win"), html.P("胜利场次")],
                                    id="wells",
                                    className="mini_container",
                                ),
                                html.Div(
                                    [html.H6("308", id="team_lose"), html.P("失败场次")],
                                    id="gas",
                                    className="mini_container",
                                ),
                                html.Div(
                                    [html.H6("1534", id="team_rating"), html.P("战队rating")],
                                    id="oil",
                                    className="mini_container",
                                ),
                                html.Div(
                                    [html.H6("1", id="team_rank"), html.P("战队排名")],
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
                                    [html.H6("1138", id="oppo_team_win"), html.P("对手胜利场次")],
                                    id="wins",
                                    className="mini_container",
                                ),
                                html.Div(
                                    [html.H6("745", id="oppo_team_lose"), html.P("对手失败场次")],
                                    id="losses",
                                    className="mini_container",
                                ),
                                html.Div(
                                    [html.H6("1439", id="oppo_team_rating"), html.P("对手战队rating")],
                                    id="rating",
                                    className="mini_container",
                                ),
                                html.Div(
                                    [html.H6("3", id="oppo_team_rank"), html.P("对手战队排名")],
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
                    [dcc.Graph(id="radiant_dire_graph")],
                    className="pretty_container five columns",
                )
                ,
                html.Div(
                    [dcc.Loading(id='_graph_loading', type='circle')],
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