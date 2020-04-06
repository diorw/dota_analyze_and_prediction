import pickle
import copy
import pathlib
import pandas as pd
from dash.dependencies import Input, Output, State, ClientsideFunction
import dash_core_components as dcc
import dash_html_components as html
from app import app
import pymysql
import dash_table
from datetime import datetime
# # Multi-dropdown options
import plotly.graph_objects as go
PATH = pathlib.Path(__file__).parent.parent
DATA_PATH = PATH.joinpath("data").resolve()
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
conn = pymysql.connect(host='120.55.167.182', user='root', password='wda20190707', database='dota', port=3306)
cursor = conn.cursor()
cursor.execute("select max(train_ymd) from model")
update_ymd = cursor.fetchall()[0]
cursor.execute("select * from model where train_ymd = %s",(update_ymd))
datalist = cursor.fetchall()
model = datalist[0]

model_list = pd.read_sql("select train_ymd,accuracy_60,accuracy_75,accuracy_80 from model order by train_ymd asc",con=conn)
model_list.columns = ['train_ymd','accuracy_60','accuracy_75','accuracy_80']


accuracy_60 = model[2]
accuracy_75 = model[3]
accuracy_80 = model[4]
datacounts = int(model[5])
TP = int(model[9])/datacounts
FN = int(model[10])/datacounts
FP = int(model[11])/datacounts
TN = int(model[12])/datacounts

history = pd.read_csv("C:\\Users\\wda\\PycharmProjects\\Kitti\\dota_analyze_and_prediction\\Dash App\\data\\568213_2020_03_01_LSTM_history.csv")
match_log = pd.read_csv("C:\\Users\\wda\\PycharmProjects\\Kitti\\dota_analyze_and_prediction\\Dash App\\data\\568213_2020_03_07_LSTM_match.csv",header = None,nrows=15)
train_loss = history['loss'].values.tolist()
val_loss = history['val_loss'].values.tolist()
epoch = history.index
match_log.columns = ['hero_1','hero_2','hero_3','hero_4','hero_5','hero_6','hero_7','hero_8','hero_9','hero_10','predict','win']
match_log = match_log[(match_log['win']==1) | (match_log['win']==0) ]
df = pd.read_csv("C:\\Users\\wda\\PycharmProjects\\Kitti\\dota_analyze_and_prediction\\Dash App\\data\hero_stats.csv", header=None)
id_to_name_dict = {}
for index, items in df.iterrows():
    id_to_name_dict[str(items[0])] = items[3]
id_to_name_dict['118'] = '紫猫'
id_to_name_dict['128'] = '蜥蜴绝手'
for i in match_log.columns:
    if(i.startswith("hero")):
        match_log[i] = match_log[i].apply(lambda x:id_to_name_dict[str(int(x))])
print(match_log)


def get_match_data():
    data = match_log.to_dict('records')
    return data

def make_TPFN_figure():
    TPFN_layout = copy.deepcopy(layout)
    TPFN_layout['title'] = '分类结果混淆矩阵'
    data = [
        dict(
            x=["T", "F"],
            y = ["P","N"],
            z = [[TP,TN],[FP,FN]],
            type = 'heatmap',
            colorscale='Viridis'
        )
    ]
    figure = dict(data=data,layout = TPFN_layout)
    return figure

def make_accuracy_figure():
    count_layout = copy.deepcopy(layout)
    count_layout['title'] = '历史模型准确率'
    x = model_list['train_ymd'].values.tolist()
    acc_60 = model_list['accuracy_60'].values.tolist()
    acc_75 = model_list['accuracy_75'].values.tolist()
    acc_80 = model_list['accuracy_80'].values.tolist()
    data = [
        dict(
            x = x,
            y = acc_60,
            type = 'line',
            mode='lines+markers',
            name='>60% 准确率'
        ),
        dict(
            x=x,
            y=acc_75,
            type='line',
            mode='lines+markers',
            name='>75% 准确率'
        ),
        dict(
            x = x,
            y = acc_80,
            type = 'line',
            mode='lines+markers',
            name='>80% 准确率'
        ),
    ]


    fig = dict(data = data,layout=count_layout)

    return fig

def make_loss_figure():
    loss_layout = copy.deepcopy(layout)
    loss_layout['title'] = '训练损失函数'
    data = [
        dict(
            type = 'line',
            x = epoch,
            y = train_loss,
            name = '训练损失',
            mode='lines',
            line_shape='spline'
        ),
        dict(
            type='line',
            x=epoch,
            y=val_loss,
            name='交叉验证损失',
            mode='lines',
            line_shape='spline'
        ),

    ]
    figure = dict(data = data,layout=loss_layout)
    return figure

model_layout = html.Div(
    [
        # empty Div to trigger javascript file for graph resizing
        html.Div(
            [
                html.Div(
                    [
                        html.Div(
                            [
                                html.H3(
                                    "模型情况概览",
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
                    [dcc.Graph(id='loss',figure=make_loss_figure())],
                    className="pretty_container four columns",
                    id="cross-filter-options",
                ),
                html.Div(
                    [
                        html.Div(
                            [
                                html.Div(
                                    [html.H6(accuracy_60,id="acc_60"), html.P(">60% 准确率")],
                                    id="wells",
                                    className="mini_container",
                                ),
                                html.Div(
                                    [html.H6(accuracy_75,id="acc_70"), html.P(">70% 准确率")],
                                    id="gas",
                                    className="mini_container",
                                ),
                                html.Div(
                                    [html.H6(accuracy_80,id="acc_80"), html.P(">80% 准确率")],
                                    id="oil",
                                    className="mini_container",
                                ),
                                html.Div(
                                    [html.H6("41",id="model_update_time"), html.P("模型对应版本")],
                                    id="water",
                                    className="mini_container",
                                ),
                            ],
                            id="info-container",
                            className="row container-display",
                        ),
                        # ,
                        # # 每日数据量
                        html.Div(
                            dash_table.DataTable(
                                id = 'match_data',
                                columns = [{"name":i,"id":i} for i in match_log.columns],
                                data = get_match_data()
                            ),
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
        html.Div(
            [
                html.Div(
                    [dcc.Graph(id="main_graph",figure=make_TPFN_figure())],
                    className="pretty_container five columns",
                )
                ,
                html.Div(
                    [dcc.Graph(id="count_graph",figure=make_accuracy_figure())],
                    className="pretty_container seven columns",
                ),
            ],
            className="row flex-display",
        ),
        html.Div(
            [
                # html.Div(
                #     [dcc.Graph(id="pie_graph")],
                #     className="pretty_container five columns",
                # )
                # ,
                html.Div(
                    html.Img(src="assets/hero_embdding.png",style={"text-align":"center"}),
                    className="pretty_container",
                ),
            ],
            className="row flex-display",
        ),
    ],
    id="mainContainer",
    style={"display": "flex", "flex-direction": "column"},
)

# @app.callback(
#     Output("loss","figure"),
#     [Input("model_update_time","value")]
# )


# @app.callback(
#     Output("main_graph","figure"),
#     [Input("model_update_time","value")]
# )

#
# @app.callback(
#     Output("match_data","data"),
#     [Input("model_update_time","value")]
# )
# def get_match_data(update_ymd):
#     data = match_log.to_dict('records')
#     return data

# Main
# @app.callback(
#     Output("count_graph", "figure"),
#     [Input("model_update_time","value")]
# )

# if __name__ == "__main__":
#     app.run_server(debug=True)