import pickle
import copy
import pathlib
import dash
import math
import datetime as dt
import pandas as pd
from dash.dependencies import Input, Output, State, ClientsideFunction
import dash_core_components as dcc
import dash_html_components as html
from app import app
from datetime import datetime
# # Multi-dropdown options

#
# # get relative data folder
PATH = pathlib.Path(__file__).parent
DATA_PATH = PATH.joinpath("data").resolve()
# print(DATA_PATH)
#
#
# Create controls
# county_options = [
#     {"label": str(COUNTIES[county]), "value": str(county)} for county in COUNTIES
# ]
#
# well_status_options = [
#     {"label": str(WELL_STATUSES[well_status]), "value": str(well_status)}
#     for well_status in WELL_STATUSES
# ]
#
# well_type_options = [
#     {"label": str(WELL_TYPES[well_type]), "value": str(well_type)}
#     for well_type in WELL_TYPES
# ]
#
#
# # Load data
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


layout = dict(
    autosize=True,
    automargin=True,
    margin=dict(l=30, r=30, b=20, t=40),
    hovermode="closest",
    plot_bgcolor="#F9F9F9",
    paper_bgcolor="#F9F9F9",
    legend=dict(font=dict(size=10), orientation="h"),
    title="Satellite Overview",

)

# Create app layout
app.layout = html.Div(
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
                        html.P("版本", className="control_label"),
                        #
                        # dcc.Dropdown(
                        #     id="well_types",
                        #     options=well_type_options,
                        #     multi=True,
                        #     value=list(WELL_TYPES.keys()),
                        #     className="dcc_control",
                        # ),
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
                ),
                html.Div(
                    [
                        html.Div(
                            [
                                html.Div(
                                    [html.H6("2",id="data_total"), html.P("有效数据数")],
                                    id="wells",
                                    className="mini_container",
                                ),
                                html.Div(
                                    [html.H6("15",id="data_today"), html.P("今日爬取有效数据")],
                                    id="gas",
                                    className="mini_container",
                                ),
                                html.Div(
                                    [html.H6("13",id="data_curmonth"), html.P("本月爬取有效数据")],
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
                            [dcc.Graph(id="count_graph")],
                            id="countGraphContainer",
                            className="pretty_container",
                        ),
                    ],
                    id="right-column",
                    className="eight columns",
                ),
            ],
            className="row flex-display",
        ),
        #,
        # html.Div(
        #     [
        #         html.Div(
        #             [dcc.Graph(id="main_graph")],
        #             className="pretty_container seven columns",
        #         ),
        #         html.Div(
        #             [dcc.Graph(id="individual_graph")],
        #             className="pretty_container five columns",
        #         ),
        #     ],
        #     className="row flex-display",
        # ),
        html.Div(
            [
                html.Div(
                    [dcc.Graph(id="pie_graph")],
                    className="pretty_container seven columns",
                )
                ,
                html.Div(
                    [dcc.Graph(id="aggregate_graph")],
                    className="pretty_container five columns",
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
    Output("aggregate_graph", "figure"),
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
    data = [

        dict(
            type="bar",
            x=start.index,
            y=start['count'],
            name="比赛时长",
        )
    ]
    figure = dict(data=data, layout=layout_aggregate)
    return figure
#
# # def produce_individual(api_well_num):
# #     try:
# #         points[api_well_num]
# #     except:
# #         return None, None, None, None
# #
# #     index = list(
# #         range(min(points[api_well_num].keys()), max(points[api_well_num].keys()) + 1)
# #     )
# #     gas = []
# #     oil = []
# #     water = []
# #
# #     for year in index:
# #         try:
# #             gas.append(points[api_well_num][year]["Gas Produced, MCF"])
# #         except:
# #             gas.append(0)
# #         try:
# #             oil.append(points[api_well_num][year]["Oil Produced, bbl"])
# #         except:
# #             oil.append(0)
# #         try:
# #             water.append(points[api_well_num][year]["Water Produced, bbl"])
# #         except:
# #             water.append(0)
# #
# #     return index, gas, oil, water
#
#
# # def produce_aggregate(selected, year_slider):
# #
# #     index = list(range(max(year_slider[0], 1985), 2016))
# #     gas = []
# #     oil = []
# #     water = []
# #
# #     for year in index:
# #         count_gas = 0
# #         count_oil = 0
# #         count_water = 0
# #         for api_well_num in selected:
# #             try:
# #                 count_gas += points[api_well_num][year]["Gas Produced, MCF"]
# #             except:
# #                 pass
# #             try:
# #                 count_oil += points[api_well_num][year]["Oil Produced, bbl"]
# #             except:
# #                 pass
# #             try:
# #                 count_water += points[api_well_num][year]["Water Produced, bbl"]
# #             except:
# #                 pass
# #         gas.append(count_gas)
# #         oil.append(count_oil)
# #         water.append(count_water)
# #
# #     return index, gas, oil, water
#
#
# # Create callbacks
# app.clientside_callback(
#     ClientsideFunction(namespace="clientside", function_name="resize"),
#     Output("output-clientside", "children"),
#     [Input("count_graph", "figure")],
# )
#
#
# @app.callback(
#     Output("aggregate_data", "data"),
#     [
#         Input("well_statuses", "value"),
#         Input("well_types", "value"),
#         Input("year_slider", "value"),
#     ],
# )
# def update_production_text(well_statuses, well_types, year_slider):
#
#     dff = filter_dataframe(df, well_statuses, well_types, year_slider)
#     selected = dff["API_WellNo"].values
#     index, gas, oil, water = produce_aggregate(selected, year_slider)
#     return [human_format(sum(gas)), human_format(sum(oil)), human_format(sum(water))]
#
#
# # Radio -> multi
# @app.callback(
#     Output("well_statuses", "value"), [Input("well_status_selector", "value")]
# )
# def display_status(selector):
#     if selector == "all":
#         return list(WELL_STATUSES.keys())
#     elif selector == "active":
#         return ["AC"]
#     return []
#
#
# # Radio -> multi
# @app.callback(Output("well_types", "value"), [Input("well_type_selector", "value")])
# def display_type(selector):
#     if selector == "all":
#         return list(WELL_TYPES.keys())
#     elif selector == "productive":
#         return ["GD", "GE", "GW", "IG", "IW", "OD", "OE", "OW"]
#     return []
#
#
# # Slider -> count graph
# @app.callback(Output("year_slider", "value"), [Input("count_graph", "selectedData")])
# def update_year_slider(count_graph_selected):
#
#     if count_graph_selected is None:
#         return [1990, 2010]
#
#     nums = [int(point["pointNumber"]) for point in count_graph_selected["points"]]
#     return [min(nums) + 1960, max(nums) + 1961]
#
#
# # Selectors -> well text
# @app.callback(
#     Output("well_text", "children"),
#     [
#         Input("well_statuses", "value"),
#         Input("well_types", "value"),
#         Input("year_slider", "value"),
#     ],
# )
# def update_well_text(well_statuses, well_types, year_slider):
#
#     dff = filter_dataframe(df, well_statuses, well_types, year_slider)
#     return dff.shape[0]
#
#
# @app.callback(
#     [
#         Output("gasText", "children"),
#         Output("oilText", "children"),
#         Output("waterText", "children"),
#     ],
#     [Input("aggregate_data", "data")],
# )
# def update_text(data):
#     return data[0] + " mcf", data[1] + " bbl", data[2] + " bbl"
#
#
# # Selectors -> main graph
# @app.callback(
#     Output("main_graph", "figure"),
#     [
#         Input("well_statuses", "value"),
#         Input("well_types", "value"),
#         Input("year_slider", "value"),
#     ],
#     [State("lock_selector", "value"), State("main_graph", "relayoutData")],
# )
# def make_main_figure(
#     well_statuses, well_types, year_slider, selector, main_graph_layout
# ):
#
#     dff = filter_dataframe(df, well_statuses, well_types, year_slider)
#
#     traces = []
#     for well_type, dfff in dff.groupby("Well_Type"):
#         trace = dict(
#             type="scattermapbox",
#             lon=dfff["Surface_Longitude"],
#             lat=dfff["Surface_latitude"],
#             text=dfff["Well_Name"],
#             customdata=dfff["API_WellNo"],
#             name=WELL_TYPES[well_type],
#             marker=dict(size=4, opacity=0.6),
#         )
#         traces.append(trace)
#
#     # relayoutData is None by default, and {'autosize': True} without relayout action
#     if main_graph_layout is not None and selector is not None and "locked" in selector:
#         if "mapbox.center" in main_graph_layout.keys():
#             lon = float(main_graph_layout["mapbox.center"]["lon"])
#             lat = float(main_graph_layout["mapbox.center"]["lat"])
#             zoom = float(main_graph_layout["mapbox.zoom"])
#             layout["mapbox"]["center"]["lon"] = lon
#             layout["mapbox"]["center"]["lat"] = lat
#             layout["mapbox"]["zoom"] = zoom
#
#     figure = dict(data=traces, layout=layout)
#     return figure
#
#
# # Main graph -> individual graph
# @app.callback(Output("individual_graph", "figure"), [Input("main_graph", "hoverData")])
# def make_individual_figure(main_graph_hover):
#
#     layout_individual = copy.deepcopy(layout)
#
#     if main_graph_hover is None:
#         main_graph_hover = {
#             "points": [
#                 {"curveNumber": 4, "pointNumber": 569, "customdata": 31101173130000}
#             ]
#         }
#
#     chosen = [point["customdata"] for point in main_graph_hover["points"]]
#     index, gas, oil, water = produce_individual(chosen[0])
#
#     if index is None:
#         annotation = dict(
#             text="No data available",
#             x=0.5,
#             y=0.5,
#             align="center",
#             showarrow=False,
#             xref="paper",
#             yref="paper",
#         )
#         layout_individual["annotations"] = [annotation]
#         data = []
#     else:
#         data = [
#             dict(
#                 type="scatter",
#                 mode="lines+markers",
#                 name="Gas Produced (mcf)",
#                 x=index,
#                 y=gas,
#                 line=dict(shape="spline", smoothing=2, width=1, color="#fac1b7"),
#                 marker=dict(symbol="diamond-open"),
#             ),
#             dict(
#                 type="scatter",
#                 mode="lines+markers",
#                 name="Oil Produced (bbl)",
#                 x=index,
#                 y=oil,
#                 line=dict(shape="spline", smoothing=2, width=1, color="#a9bb95"),
#                 marker=dict(symbol="diamond-open"),
#             ),
#             dict(
#                 type="scatter",
#                 mode="lines+markers",
#                 name="Water Produced (bbl)",
#                 x=index,
#                 y=water,
#                 line=dict(shape="spline", smoothing=2, width=1, color="#92d8d8"),
#                 marker=dict(symbol="diamond-open"),
#             ),
#         ]
#         layout_individual["title"] = dataset[chosen[0]]["Well_Name"]
#
#     figure = dict(data=data, layout=layout_individual)
#     return figure
#
#
# # Selectors, main graph -> aggregate graph
# @app.callback(
#     Output("aggregate_graph", "figure"),
#     [
#         Input("well_statuses", "value"),
#         Input("well_types", "value"),
#         Input("year_slider", "value"),
#         Input("main_graph", "hoverData"),
#     ],
# )
# def make_aggregate_figure(well_statuses, well_types, year_slider, main_graph_hover):
#
#     layout_aggregate = copy.deepcopy(layout)
#
#     if main_graph_hover is None:
#         main_graph_hover = {
#             "points": [
#                 {"curveNumber": 4, "pointNumber": 569, "customdata": 31101173130000}
#             ]
#         }
#
#     chosen = [point["customdata"] for point in main_graph_hover["points"]]
#     well_type = dataset[chosen[0]]["Well_Type"]
#     dff = filter_dataframe(df, well_statuses, well_types, year_slider)
#
#     selected = dff[dff["Well_Type"] == well_type]["API_WellNo"].values
#     index, gas, oil, water = produce_aggregate(selected, year_slider)
#
#     data = [
#         dict(
#             type="scatter",
#             mode="lines",
#             name="Gas Produced (mcf)",
#             x=index,
#             y=gas,
#             line=dict(shape="spline", smoothing="2", color="#F9ADA0"),
#         ),
#         dict(
#             type="scatter",
#             mode="lines",
#             name="Oil Produced (bbl)",
#             x=index,
#             y=oil,
#             line=dict(shape="spline", smoothing="2", color="#849E68"),
#         ),
#         dict(
#             type="scatter",
#             mode="lines",
#             name="Water Produced (bbl)",
#             x=index,
#             y=water,
#             line=dict(shape="spline", smoothing="2", color="#59C3C3"),
#         ),
#     ]
#     layout_aggregate["title"] = "Aggregate: " + WELL_TYPES[well_type]
#
#     figure = dict(data=data, layout=layout_aggregate)
#     return figure
#
#
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
            domain={"x": [0, 0.45], "y": [0.2, 0.8]},
        )
        # dict(
        #     type="pie",
        #     labels=[WELL_TYPES[i] for i in aggregate.index],
        #     values=aggregate["API_WellNo"],
        #     name="Well Type Breakdown",
        #     hoverinfo="label+text+value+percent",
        #     textinfo="label+percent+name",
        #     hole=0.5,
        #     marker=dict(colors=[WELL_COLORS[i] for i in aggregate.index]),
        #     domain={"x": [0.55, 1], "y": [0.2, 0.8]},
        # ),
    ]
    layout_pie["title"] = "Production Summary: {} to {}".format(
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
    Output("count_graph", "figure"),
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

    # colors = []
    # for i in range(20, 100):
    #     if i >= int(match_duration[0]) and i < int(match_duration[1]):
    #         colors.append("rgb(123, 199, 255)")
    #     else:
    #         colors.append("rgba(123, 199, 255, 0.2)")

    data = [
        # dict(
        #     type="scatter",
        #     mode="markers",
        #     x=g.index,
        #     y=g["API_WellNo"],
        #     name="All Wells",
        #     opacity=0,
        #     hoverinfo="skip",
        # ),
        dict(
            type="bar",
            x=start.index,
            y=start['count'],
            name="比赛日期",
            #marker=dict(color=colors),
        ),
    ]

    layout_count["title"] = "比赛日期"
    layout_count["dragmode"] = "select"
    layout_count["showlegend"] = False
    layout_count["autosize"] = True

    figure = dict(data=data, layout=layout_count)
    return figure


# Main
if __name__ == "__main__":
    app.run_server(debug=True)