import copy
import pathlib
import pandas as pd
from dash.dependencies import Input, Output, State, ClientsideFunction
import dash_core_components as dcc
import dash_html_components as html
from app import app
from datetime import datetime
import plotly.graph_objects as go
PATH = pathlib.Path(__file__).parent.parent
DATA_PATH = PATH.joinpath("data").resolve()
df = pd.read_csv(DATA_PATH.joinpath("match_new.csv"), low_memory=False,header = None)
columns = [	"match_id" ,
	"player_1_id",
	"player_1_hero_id",
	"player_2_id",
	"player_2_hero_id",
	"player_3_id",
	"player_3_hero_id",
	"player_4_id",
	"player_4_hero_id",
	"player_5_id",
	"player_5_hero_id",
	"player_6_id",
	"player_6_hero_id",
	"player_7_id",
	"player_7_hero_id",
	"player_8_id",
	"player_8_hero_id",
	"player_9_id",
	"player_9_hero_id",
	"player_10_id",
	"player_10_hero_id",
	"win",
	"game_mode",
	"start_time",
	"duration",
	"version"]

df.columns = columns
df = df.sort_values(by = 'duration',inplace=False)
df = df[df['start_time'] > 0]

relation_df = pd.read_csv(DATA_PATH.joinpath("hero_relationship.csv"), low_memory=False,header = None)
relation_df_columns = ['hero_id','target_hero_id','win_rate','update_ymd']
relation_df.columns = relation_df_columns
hero_id_list = list(relation_df['hero_id'].values)
hero_id_list = list(set(hero_id_list))

hero_stats_df = pd.read_csv(DATA_PATH.joinpath("hero_stats.csv"), low_memory=False,header = None)
hero_stats_df_columns = ['hero_id','pro_pick','pro_win','hero_name_ch','type']
hero_stats_df.columns = hero_stats_df_columns
hero_stats_df['win_rate'] = hero_stats_df['pro_win']/hero_stats_df['pro_pick']
hero_df = hero_stats_df.sort_values("win_rate",inplace=False)

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

def produce_individual():
    layout_individual = copy.deepcopy(layout)
    data = [
        dict (
            type = 'bar',
            x = hero_df['hero_name_ch'],
            y = hero_df['win_rate'],
            name = '英雄胜率',
            showarrow=False
        )
    ]
    layout_individual['title'] = '近期英雄胜率'
    layout_individual["showlegend"] = False
    layout_individual["autosize"] = True
    layout_individual['xaxis'] = dict(
        showticklabels = False
    )
    figure = dict(data = data,layout = layout_individual)

    return figure

def produce_main():
    result = []
    for i in hero_id_list:
        z = []
        for j in hero_id_list:
            if (i == j):
                z.append(None)
            else:
                win_rate = relation_df[(relation_df['hero_id'] == i) & (relation_df['target_hero_id'] == j)][
                    'win_rate'].values.tolist()

                if (win_rate != []):
                    z.append(win_rate[0])
                else:
                    z.append(None)
        result.append(z)
    layout_main = copy.deepcopy(layout)
    fig = go.Figure()
    fig.add_trace(go.Heatmap(x=hero_id_list,y = hero_id_list,z = result,colorscale='Viridis'))
    fig.update_layout(title = '英雄相对胜率热力图',xaxis_title = '英雄ID',yaxis_title='英雄ID')
    return fig

# Create app layout
crawl_layout = html.Div(
    [
        # empty Div to trigger javascript file for graph resizing
        html.Div(
            [
                html.Div(
                    [
                        html.Div(
                            [
                                html.H3(
                                    "近期数据爬取情况概览",
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
                            "比赛时间范围",
                            className="control_label",
                        ),
                        dcc.RangeSlider(
                            id="match_duration_slider",
                            min=20,
                            max=100,
                            value=[25, 45],
                            className="dcc_control",
                        ),
                        html.P("比赛类型", className="control_label"),
                        dcc.RadioItems(
                            id="match_type_selector",
                            options=[
                                {"label": "所有比赛", "value": "all"},
                                {"label": "全英雄选择 ", "value": "22"},
                                {"label": "随机征召 ", "value": "3"},
                            ],
                            value="all",
                            labelStyle={"display": "inline-block"},
                            className="dcc_control",
                        )

                    ],
                    className="pretty_container four columns",
                    id="cross-filter-options",
                    style = {"padding-bottom":250}
                ),
                html.Div(
                    [
                        html.Div(
                            [
                                html.Div(
                                    [html.H6("30596",id="data_total"), html.P("有效数据数")],
                                    id="wells",
                                    className="mini_container",
                                ),
                                html.Div(
                                    [html.H6("0",id="data_today"), html.P("今日爬取有效数据")],
                                    id="gas",
                                    className="mini_container",
                                ),
                                html.Div(
                                    [html.H6("0",id="data_curmonth"), html.P("本月爬取有效数据")],
                                    id="oil",
                                    className="mini_container",
                                ),
                                html.Div(
                                    [html.H6("2019-11-29",id="model_update_time"), html.P("模型最新更新时间")],
                                    id="water",
                                    className="mini_container",
                                ),
                            ],
                            id="info-container",
                            className="row container-display",
                        ),
                        # 每日数据量
                        html.Div(
                            
                            [ dcc.Loading(id = 'count_graph_loading',type = 'default')
                            ],
                            id="countGraphContainer",
                            className="pretty_container"

                        ),
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
                    [dcc.Graph(id="main_graph",figure = produce_main())],
                    className="pretty_container five columns",
                )
                ,
                html.Div(
                    [dcc.Graph(id="individual_graph",figure = produce_individual())],
                    className="pretty_container seven columns",
                ),
            ],
            className="row flex-display",
        ),
        html.Div(
            [
                html.Div(
                    [dcc.Graph(id="pie_graph")],
                    className="pretty_container five columns",
                )
                ,
                html.Div(
                    [dcc.Loading(id = 'aggregate_graph_loading',type = 'circle')],
                    className="pretty_container seven columns"

                ),
            ],
            className="row flex-display",
        ),
    ],
    id="mainContainer",
    style={"display": "flex", "flex-direction": "column"},
)


# 比赛时长 、 比赛类型
def filter_dataframe(df, match_duration, match_type):
    if match_type != 'all':
        dff = df[df["game_mode"] == int(match_type)]
    else:
        dff = df
    dff_result = dff[
        (df["duration"] > match_duration[0])
        & (df["duration"] < match_duration[1])
    ]
    return dff_result

@app.callback(
    Output("aggregate_graph_loading", "children"),
    [
        Input("match_duration_slider", "value"),
        Input("match_type_selector", "value"),
    ],

)
def produce_aggregate(match_duration,match_type):
    layout_aggregate = copy.deepcopy(layout)

    dff = filter_dataframe(df, match_duration, match_type)
    g = dff[["duration", "start_time"]]
    g['start_time'] = g.apply(lambda row: format_starttime(row['start_time']), axis=1)
    g['duration'] = g.apply(lambda row:int(row['duration']),axis = 1)
    start = g.groupby("duration").count()
    start.columns = ['count']
    layout_aggregate["title"] = "比赛时长分布"

    colors = []
    for i in range(20, 100):
        if i >= int(match_duration[0]) and i < int(match_duration[1]):
            colors.append("rgb(123, 199, 255)")
        else:
            colors.append("rgba(123, 199, 255, 0.2)")
    data = [

        dict(
            type="bar",
            x=start.index,
            y=start['count'],
            name="比赛时长",
            marker=dict(color=colors),
        )
    ]
    figure = dict(data=data, layout=layout_aggregate)
    return dcc.Graph(id = 'aggregate_graph',figure=figure)

# Selectors, main graph -> pie graph
@app.callback(
    Output("pie_graph", "figure"),
    [
        Input("match_duration_slider", "value"),
        Input("match_type_selector", "value"),
    ],
)
def make_pie_figure(match_duration, match_type):

    layout_pie = copy.deepcopy(layout)

    dff = filter_dataframe(df, match_duration, match_type)
    aggregate = dff.groupby(["win"]).count()
    tianhui = aggregate['match_id'].iloc[0]
    yeyan = aggregate['match_id'].iloc[1]
    data = [
        dict(
            type="pie",
            labels=["天辉", "夜魇"],
            values=[tianhui,yeyan],
            name="天辉夜魇胜率分布",
            text=[
                "天辉胜利",
                "夜魇胜利",
            ],
            hoverinfo="text+value+percent",
            textinfo="label+percent+name",
            hole=0.5,
            marker=dict(colors=["#fac1b7", "#a9bb95"]),
            # domain={"x": [0, 0.45], "y": [0.2, 0.8]},
        )
    ]
    layout_pie["title"] = "Match duration: {} to {}".format(
        match_duration[0], match_duration[1]
    )
    layout_pie["font"] = dict(color="#777777")
    layout_pie["legend"] = dict(
        font=dict(color="#CCCCCC", size="10"), orientation="h", bgcolor="rgba(0,0,0,0)"
    )

    figure = dict(data=data, layout=layout_pie)
    return figure


def format_starttime(start_time):

    d = datetime.fromtimestamp(int(start_time),None)
    start_time = d.strftime("%Y-%m-%d")
    return start_time

# Selectors -> count graph
@app.callback(
    Output("count_graph_loading", "children"),
    [
        Input("match_duration_slider", "value"),
        Input("match_type_selector", "value"),
    ],
)
def make_count_figure(match_duration, match_type):

    layout_count = copy.deepcopy(layout)

    dff = filter_dataframe(df,match_duration,match_type)
    g = dff[["duration", "start_time"]]
    g['start_time'] = g.apply(lambda row:format_starttime(row['start_time']),axis=1)
    start = g.groupby("start_time").count()
    start.columns = ['count']


    data = [
        dict(
            type="line",
            x=start.index,
            y=start['count'],
            name="比赛日期",
            mode='lines',
            line_shape='spline'
            #marker=dict(color=colors),
        ),
    ]

    layout_count["title"] = "比赛日期"
    layout_count["dragmode"] = "select"
    layout_count["showlegend"] = False
    layout_count["autosize"] = True

    figure = dict(data=data, layout=layout_count)
    return dcc.Graph(id = 'count_graph',figure=figure)


# Main
# if __name__ == "__main__":
#     app.run_server(debug=True)