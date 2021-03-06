import os
import dash_core_components as dcc
import dash_html_components as html
from app import app
from dash.dependencies import Input, Output,State
import numpy as np
import keras
from keras.models import load_model
import dash
import pandas as pd
import copy
import pymysql
import dash_cytoscape as cyto
import requests
import plotly.graph_objects as go

# keras.backend.clear_session()  # 计算图清空，防止越来越慢
headers = {'Accept': 'text/html, application/xhtml+xml, image/jxr, */*',
           'Accept - Encoding': 'gzip, deflate',
           'Accept-Language': 'zh-Hans-CN, zh-Hans; q=0.5',
           'Connection': 'Keep-Alive',
           'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                         'Chrome/52.0.2743.116 Safari/537.36 Edge/15.15063'}
hero_id_max = 129
model_saved_path = "C:\\Users\\wda\\PycharmProjects\\Kitti\\dota_analyze_and_prediction\\Dash App\\data\\568213_2020_03_07_LSTM.h5"

hero_stats_df = pd.read_csv("C:\\Users\\wda\\PycharmProjects\\Kitti\\dota_analyze_and_prediction\\Dash App\\data\\hero_stats.csv",header = None)
hero_stats_df.columns = ["id", 'pro_pick', 'pro_win', 'heor_name_ch', 'type']
hero_stats_df['win_rate'] = hero_stats_df['pro_win'] / hero_stats_df['pro_pick']
id_to_name_dict = {}
for index, items in hero_stats_df.iterrows():
    id_to_name_dict[str(items[0])] = items[3]
# print(id_to_name_dict)
conn = pymysql.connect(host='120.55.167.182', user='root', password='wda20190707', port=3306, database='dota')
player_id_list = ['152461420', '205144888', '143182355', '89115202', '140973920', '255319952', '129365110', '260241404',
                  '207212099', '187938206']



hero_stats_en_df = pd.read_csv("C:\\Users\\wda\\PycharmProjects\\Kitti\\dota_analyze_and_prediction\\Dash App\\data\\hero_stats_en.csv",header = None)
Enname_to_id_dict = {}
id_to_Enname = {}
for index, items in hero_stats_en_df.iterrows():
    Enname_to_id_dict[str(items[0])] = items[1]
    id_to_Enname[str(items[1])] = items[0]



layout = dict(
    autosize=True,
    automargin=True,
    margin=dict(l=30, r=30, b=20, t=40),
    hovermode="closest",
    # plot_bgcolor="#F9F9F9",
    # paper_bgcolor="#F9F9F9",
    # legend=dict(font=dict(size=8), orientation="h"),
    title="Satellite Overview",

)


def generate_select(hero_name = None):
    files = os.listdir("assets/hero_icon")
    model = []
    for file in files:
        imgsrc = "assets/hero_icon/"+file
        if hero_name is not None and not str(file).startswith(hero_name) :
            continue
        hero_block = html.Div(className="gZpUvw",
                              children = [
                                  html.Div(className="name-overlay",
                                           children=[
                                               html.Div(str(file).split("_full.png")[0],className="name"),
                                               html.Div("A",className="team-indicator team-a"),
                                               html.Div("B",className="team-indicator team-b")
                                           ]),
                                  html.Img(src=imgsrc),
                                  html.Div(className="ts-container ",
                                           children=[
                                            html.Div("Add To Team A",id = str(file).split("_full.png")[0]+"_A",className="ts ts-left",role="button",tabIndex="0"),
                                            html.Div("Add To Team B",id = str(file).split("_full.png")[0]+"_B", className="ts ts-right", role="button",
                                                        tabIndex="0")
                                           ])
                              ]
                            )
        model.append(hero_block)
    return model


def generate_no_select_button(*args):
    model = []
    A_or_B = args[0]
    for i in range(5):
        model.append(html.Div(id = str(i)+"_"+A_or_B+"_no_select",className="no-select",role="button",tabIndex="0"))

    return html.Div(children=model,id = A_or_B+"_no_select_button")

def generate_placeholder(*args):
    model = []
    A_or_B = args[0]
    for i in range(5):
        model.append(html.Img(id = str(i)+"_"+A_or_B,className="hero-placeholder hero-img",role="button",src= 'assets/timg.png'))

    return html.Div(children=model,id = A_or_B+"_placeholder")

def generate_input(*args):
    model = []
    A_or_B = args[0]
    for i in range(5):
        if(A_or_B == "A"):
            model.append(dcc.Input(id = str(i)+"_playerid_"+A_or_B,className="player-input hero-img",value = player_id_list[i]))
        else:
            model.append(dcc.Input(id=str(i) + "_playerid_" + A_or_B, className="player-input hero-img",value=player_id_list[i+5])
                         )

    return html.Div(children=model)

predict_layout = html.Div(
            children=html.Div(
                className="main-section",
                    children = html.Div(className="fWisXZ",
                            children= html.Div(className="dnZKxn",
                                        children=[html.Div(
                                            [html.Span("英雄阵容组合",className="title"),
                                            html.Span("选取特定的英雄阵容，分析双方阵容优劣，并预测胜率",className="subtitle")]
                                            ,className="clNgdz"
                                        ),
                                        html.Div(
                                            children=
                                            [
                                                html.Div(className="gZpUvw",
                                                    id = "hero_list",
                                                    children = generate_select(None)
                                            )
                                            ],className="iyjHnf"
                                        ),
                                        html.Div(
                                            children= [
                                                html.Div(
                                                    id = 'query_div',
                                                    className = "query_div",
                                                    children= [
                                                        # html.Div(
                                                        #     "英雄筛选",
                                                        #     className= "query_hint"
                                                        # ),
                                                        # input
                                                        dcc.Input(id = "query_input",type="text",className="query_input",placeholder="英雄筛选")


                                                    ]
                                                )
                                            ],
                                            className = "query_body"
                                        ),
                                        html.Div(className="TBDUn",
                                                 children=[
                                                     html.Div(className="team-container",children=
                                                        [html.Div("Team A",className="team-title team-a"),
                                                         generate_placeholder("A"),
                                                         dcc.Input(id = 'hidden_A',type='text',style={"display":"none"},value = "0,0,0,0,0")
                                                            # value = "114,21,96,54,68"
                                                         ]

                                                        ),

                                                     html.Div("vs.",className="seperator"),
                                                     html.Div(className="team-container",
                                                              children=[html.Div("Team B",className="team-title team-b"),
                                                                        generate_placeholder("B"),
                                                                        dcc.Input(id='hidden_B',type='text',style={"display":"none"},value = "0,0,0,0,0"
                                                                                 )
                                                              ])

                                                 ]
                                                 ),
                                            html.Div(className="TBDUn",
                                                     children=[
                                                         html.Div(className="team-container", children=
                                                         [
                                                          generate_no_select_button("A"),
                                                          ]

                                                                  ),
                                                         html.Div("取消选择", className="seperator"),
                                                         html.Div(className="team-container",
                                                                  children=[

                                                                      generate_no_select_button("B"),
                                                                      ])

                                                     ]
                                                     ),
                                        html.Div(className="TBDUn",
                                                 children=[
                                                     html.Div(className="team-container",children=
                                                        [
                                                         generate_input("A"),

                                                         ]

                                                        ),

                                                     html.Div("   ", className="seperator"),
                                                     html.Div(className="team-container",
                                                              children=[
                                                                        generate_input("B"),

                                                              ])

                                                 ]
                                                 ),
                                        html.Div(
                                            children=
                                                html.Div(
                                                    className="submit_block",
                                                    children = html.Button(id = 'submit_query',className="submit_button",tabIndex="0",type="button",
                                                            children= html.Div(
                                                                children=html.Div(
                                                                    className="submit_button_div",
                                                                    children=html.Span("提交",className="submit_button_div_span")
                                                                )
                                                            )
                                                        )
                                                    ),
                                            className = "submit_section"
                                        ),
                                            html.Div(className="TBDUn",
                                                 children=[
                                                     html.Div(children="20%",id = 'win_rate', className="seperator"),
                                                 ]
                                            ),
                                            html.Div(
                                                [
                                                    html.Div(
                                                        [dcc.Graph(id = 'hero_relationship_graph')],
                                                        className="pretty_container five columns",
                                                    )
                                                    ,
                                                    html.Div(
                                                        [dcc.Graph(id="hero_win_rate_graph")],
                                                        className="pretty_container seven columns",
                                                    ),
                                                ],
                                                className="row flex-display",
                                            ),
                                            html.Div(
                                                [
                                                    html.Div(
                                                        [dcc.Graph(id="radar_graph")],
                                                        className="pretty_container five columns",
                                                    )
                                                    ,
                                                    html.Div(
                                                        [dcc.Graph(id="player_win_rate_graph")],
                                                        className="pretty_container seven columns",
                                                    ),
                                                ],
                                                className="row flex-display",
                                            ),
                                        ]
                            )
                    )
                ),
        className = "ktYFlp" )


# class 属性变为className
# style 属性是一个字典
# style内的属性是驼峰格式的
# 像素值的px可以省略
@app.callback(
    Output(component_id='hero_list', component_property='children'),
    [Input(component_id='query_input', component_property='value')]
)
def update_output_div(input_value):
    return generate_select(input_value)

@app.callback(
    Output(component_id="win_rate",component_property="children"),
    [Input(component_id="submit_query", component_property='n_clicks')],
     [State(component_id='hidden_A', component_property='value'),
     State(component_id='hidden_B', component_property='value')]

)
def inference(n_clicks,radiant,dire):
    if(n_clicks == 0):
        return "请选择英雄和玩家"

    # try:
    sample_in = []
    radiant_list = list(map(int, radiant.split(',')))
    dire_list = list(map(int, dire.split(',')))
    radiant_vector = np.zeros(hero_id_max)
    dire_vector = np.zeros(hero_id_max)
    for item in radiant_list:
        if(int(item)==0):
            return "天辉方阵容不完整"
        radiant_vector[int(item) - 1] = 1
    for item in dire_list:
        if(int(item)==0):
            return "夜魇方阵容不完整"
        dire_vector[int(item) - 1] = 1

    sample_in.append([radiant_vector, dire_vector])
    sample_in = np.array(sample_in).reshape(len(sample_in),2,hero_id_max)
    keras.backend.clear_session()
    model = load_model(model_saved_path)
    out0 = model.predict(sample_in)
    return "预测天辉方胜率为 "+str(round(out0[0][0]*100,2))+"%"
    # except Exception:
    #     print(Exception)
    #     raise dash.exceptions.PreventUpdate

@app.callback(
    Output(component_id="hero_win_rate_graph",component_property="figure"),
    [Input(component_id="submit_query", component_property='n_clicks')],
    [State(component_id='hidden_A', component_property='value'),
     State(component_id='hidden_B', component_property='value'),
     ]

)
def make_hero_win_rate_figure(n_clicks,radiant,dire):
    try:

        radiant_list = list(map(int, radiant.split(',')))
        dire_list = list(map(int, dire.split(',')))
        y = []
        for id in radiant_list:
            rate = hero_stats_df['win_rate'][hero_stats_df['id'] == int(id)].values.tolist()[0]
            y.append(rate)
        for id in dire_list:
            rate = hero_stats_df['win_rate'][hero_stats_df['id'] == int(id)].values.tolist()[0]
            y.append(rate)

        x1 = list(map(lambda x: id_to_name_dict[str(x)], radiant_list))
        y1 = y[:5]
        x2 = list(map(lambda x: id_to_name_dict[str(x)], dire_list))
        y2 = y[5:]
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=x1,y=y1,name = '天辉',mode = 'markers',marker_color = 'rgba(152,0,0,.8)'))
        fig.add_trace(go.Scatter(x=x2,y=y2,name = '夜魇',mode = 'markers',marker_color = 'rgba(52,0, 0,.8)'))
        fig.update_layout(xaxis_title="英雄名称",yaxis_title='英雄全局胜率',title = '双方英雄全局胜率对比')
        return fig
    except:
        raise dash.exceptions.PreventUpdate

State_A = [State(component_id=str(i)+"_playerid_"+"A", component_property='value') for i in range(5)]
State_B = [State(component_id=str(i)+"_playerid_"+"B", component_property='value') for i in range(5)]
@app.callback(
    Output(component_id="player_win_rate_graph",component_property="figure"),
    [Input(component_id="submit_query", component_property='n_clicks')],

    [
    State(component_id='hidden_A', component_property='value'),
    State(component_id='hidden_B', component_property='value'),
    ]+State_A+State_B
)
def make_player_hero_figure(n_clicks,radiant,dire,*args):
    try:
        match_count = []
        win = []
        radiant_list = list(map(int, radiant.split(',')))
        dire_list = list(map(int, dire.split(',')))
        conn.ping()

        player_id_list = list(args)
        for i in range(10):
            player_id = player_id_list[i]
            if(i<5):
                hero_id = radiant_list[i]
            else:
                hero_id = dire_list[i-5]

            cursor = conn.cursor()
            cursor.execute("select games,games_win from player_hero where account_id = %s and hero_id = %s",(player_id,hero_id))
            result = cursor.fetchone()
            if(result!=None and len(result)>0):
                match_count.append(result[0])
                win.append(result[1])
            else:
                re = requests.get("https://api.opendota.com/api/players/"+player_id+"/heroes?hero_id="+str(hero_id),headers = headers)
              #  print("https://api.opendota.com/api/players/"+player_id+"/heroes?hero_id="+str(hero_id))
                if(re.status_code==200):
                    json = re.json()[0]
                    win_counts = json['win']
                    games = json['games']
                    win.append(win_counts)
                    match_count.append(games)
        x = list(map(lambda x: id_to_name_dict[str(x)], radiant_list+dire_list))
        fig = go.Figure()
        fig.add_trace(go.Bar(x = x,y = match_count,name = '使用场次'))
        fig.add_trace(go.Bar(x = x,y = win,name = '胜利场次'))
        fig.update_layout(xaxis_title="英雄名称",yaxis_title='玩家使用场次及胜利场次',title = '双方玩家英雄胜率对比')
        return fig
    except:
        raise dash.exceptions.PreventUpdate

A_Input = [Input(component_id =str(file).split("_full.png")[0]+"_A",component_property='n_clicks') for file in os.listdir("assets/hero_icon")]
B_Input = [Input(component_id =str(file).split("_full.png")[0]+"_B",component_property='n_clicks') for file in os.listdir("assets/hero_icon")]

@app.callback(
    Output(component_id="A_placeholder",component_property="children"),
    A_Input,
    [State(component_id='hidden_A', component_property='value'),
     State(component_id='hidden_B', component_property='value'),
     ]
)
def A_placeholder(*args):
    ctx = dash.callback_context
    if not ctx.triggered:
        raise dash.exceptions.PreventUpdate
    if(args[-2] is None):
        radiant_list = []
    else:
        radiant_list = list(map(int, args[-2].split(',')))
    if (args[-1] is None):
        dire_list = []
    else:

        dire_list = list(map(int, args[-1].split(',')))
    print("dire_list_A")
    print(dire_list)
    print("radiant_list_A")
    print(radiant_list)
    btn_id = int(Enname_to_id_dict[str(ctx.triggered[0]['prop_id'].split('.')[0]).split("_A")[0]])

    def check(l):
        for i in l:
            if(i==0):
                return True
        return False
    # 如果该英雄已经选择了，不更新
    if(btn_id in radiant_list or btn_id in dire_list):
        raise dash.exceptions.PreventUpdate
    elif check(radiant_list)==False:
        raise dash.exceptions.PreventUpdate
    else:
        for i in range(5):
            if(radiant_list[i]==0):
                radiant_list[i]=btn_id
                break


    figure = []
    for i in range(len(radiant_list)):
        if(radiant_list[i]!=0):
            figure.append(html.Img(id=str(i) + "_A",src = 'assets/hero_icon/'+id_to_Enname[str(radiant_list[i])]+"_full.png", className="hero-placeholder hero-img"))
        else:
            figure.append(html.Img(id=str(i) + "_A", className="hero-placeholder hero-img",src= 'assets/timg.png'))

    return figure

@app.callback(
    Output(component_id="B_placeholder",component_property="children"),
    B_Input,
    [State(component_id='hidden_A', component_property='value'),
     State(component_id='hidden_B', component_property='value'),
     ]
)
def B_place_holder(*args):
    ctx = dash.callback_context
    if not ctx.triggered:
        raise dash.exceptions.PreventUpdate
    if(args[-2] is None):
        radiant_list = []
    else:
        radiant_list = list(map(int, args[-2].split(',')))
    if (args[-1] is None):
        dire_list = []
    else:

        dire_list = list(map(int, args[-1].split(',')))
    print("dire_list_B")
    print(dire_list)
    print("radiant_list_B")
    print(radiant_list)
    btn_id = int(Enname_to_id_dict[str(ctx.triggered[0]['prop_id'].split('.')[0]).split("_B")[0]])

    def check(l):
        for i in l:
            if(i==0):
                return True
        return False
    # 如果该英雄已经选择了，不更新
    if(btn_id in radiant_list or btn_id in dire_list):
        raise dash.exceptions.PreventUpdate
    elif check(dire_list)==False:
        raise dash.exceptions.PreventUpdate
    else:
        for i in range(5):
            if(dire_list[i]==0):
                dire_list[i]=btn_id
                break


    figure = []
    for i in range(len(dire_list)):
        if(dire_list[i]!=0):
            figure.append(html.Img(id=str(i) + "_B",src = 'assets/hero_icon/'+id_to_Enname[str(dire_list[i])]+"_full.png", className="hero-placeholder hero-img"))
        else:
            figure.append(html.Img(id=str(i) + "_B", className="hero-placeholder hero-img",src = 'assets/timg.png'))


    return figure


for i in range(5):
    for team in ["A","B"]:
        @app.callback(
            dash.dependencies.Output(str(i)+"_"+team, 'src'),
            [dash.dependencies.Input(str(i)+"_"+team+"_no_select", 'n_clicks')]
        )

        def remove(n_clicks):
            ctx = dash.callback_context
            if not ctx.triggered:
                raise dash.exceptions.PreventUpdate
            else:
                return "assets/timg.png"


@app.callback(
    Output(component_id="hero_relationship_graph",component_property="figure"),
    [Input(component_id="submit_query", component_property='n_clicks')],
    [State(component_id='hidden_A', component_property='value'),
     State(component_id='hidden_B', component_property='value'),
     ]

)
def make_hero_relationship_figure(n_clicks,radiant,dire):
    radiant_list = list(map(int,radiant.split(',')))
    dire_list = list(map(int,dire.split(',')))
    if(0 in radiant_list or 0 in dire_list):
        raise dash.exceptions.PreventUpdate
    conn = pymysql.connect(host='120.55.167.182', user='root', password='wda20190707', port=3306, database='dota')
    conn.ping()
    cursor = conn.cursor()
    max_update_ymd_sql = 'select max(update_ymd) from hero_relationship'
    cursor.execute(max_update_ymd_sql)
    max_update_ymd_list = cursor.fetchall()
    max_update_ymd = max_update_ymd_list[0]
    query = "select win_rate from hero_relationship where update_ymd = %s and hero_id = %s and target_hero_id = %s"

    def query_win_rate(hero_id, target_hero_id):
        cursor.execute(query, (max_update_ymd, hero_id, target_hero_id))
        win_rate = cursor.fetchall()
        if (len(win_rate) > 0 and len(win_rate[0]) > 0 and win_rate[0][0] is not None):
            return win_rate[0][0]
        else:
            return 0
    z = []
    x = list(map(lambda x:id_to_name_dict[str(x)],radiant_list))
    y = list(map(lambda x:id_to_name_dict[str(x)],dire_list))
    for i in range(5):
        tmp_z = []
        for j in range(5):
            tmp_z.append(query_win_rate(radiant_list[i], dire_list[j]))
        z.append(tmp_z)
    fig = go.Figure()
    fig.add_trace(go.Heatmap(x=x,y=y,z=z,colorscale='Viridis'))
    fig.update_layout(title='英雄相对胜率',xaxis_title = '天辉方英雄名称',yaxis_title='夜魇方英雄名称')
    return fig

@app.callback(
    Output(component_id="radar_graph",component_property="figure"),
    [Input(component_id="submit_query", component_property='n_clicks')],
    [State(component_id='hidden_A', component_property='value'),
     State(component_id='hidden_B', component_property='value'),
     ]

)
def make_dimension_graph(n_clicks,radiant,dire):
    radiant_list = radiant.split(',')
    dire_list = dire.split(',')
    dimension_graph_layout = copy.deepcopy(layout)
    categories  = ["控制","核心", "辅助", "逃生", "爆发", "先手", "耐久","推进"]
    conn = pymysql.connect(host='120.55.167.182', user='root', password='wda20190707', port=3306, database='dota')
    cursor = conn.cursor()
    cursor.execute("select sum(kong_zhi),sum(he_xin),sum(fu_zhu),sum(tao_sheng),sum(bao_fa),sum(xian_shou),sum(nai_jiu),sum(tui_jin) from dota.hero_stats "
                   +" where id = %s or id = %s or id = %s or id = %s or id = %s",(radiant_list[0],radiant_list[1],radiant_list[2],radiant_list[3],radiant_list[4]))
    radiant_dimension = list(cursor.fetchall()[0])
    cursor.execute("select sum(kong_zhi),sum(he_xin),sum(fu_zhu),sum(tao_sheng),sum(bao_fa),sum(xian_shou),sum(nai_jiu),sum(tui_jin) from dota.hero_stats "
                   +" where id = %s or id = %s or id = %s or id = %s or id = %s",(dire_list[0],dire_list[1],dire_list[2],dire_list[3],dire_list[4]))
    dire_dimension = list(cursor.fetchall()[0])

    data = [
        dict(
            type = 'scatterpolar',
            r=radiant_dimension,
            theta=categories,
            fill='toself',
            name='天辉'
        ),
        dict(
            type='scatterpolar',
            r=dire_dimension,
            theta=categories,
            fill='toself',
            name='夜魇'
        )
    ]
    dimension_graph_layout['title'] = '阵容能力维度分析'
    return dict(data = data,layout = dimension_graph_layout)

@app.callback(
    Output('hidden_A','value'),
    [Input('A_placeholder','children'),Input('1_A','src'),
     Input('0_A','src'),Input('2_A','src'),Input('3_A','src'),Input('4_A','src')]
)
def place_holder_to_hidden(*args):
    tmp = []
    for arg in args[0]:
        place_holder = arg['props']
        print(place_holder['src'])
        if(place_holder['src']=='assets/timg.png'):
            tmp.append("0")
        else:
            hero_name = (place_holder['src'].split("/")[-1]).split("_full.png")[0]
        # {'id': '0_A', 'children': None, 'className': 'hero-placeholder hero-img', 'src': 'assets/hero_icon/abaddon_full.png'}
            tmp.append(str(Enname_to_id_dict[hero_name]))
    return ",".join(tmp)

@app.callback(
    Output('hidden_B','value'),
    [Input('B_placeholder','children'),Input('1_B','src'),
     Input('0_B','src'),Input('2_B','src'),Input('3_B','src'),Input('4_B','src')]
)
def place_holder_to_hidden(*args):
    tmp = []
    for arg in args[0]:
        place_holder = arg['props']
        if(place_holder['src']=='assets/timg.png'):
            tmp.append("0")
        else:
            hero_name = (place_holder['src'].split("/")[-1]).split("_full.png")[0]
            tmp.append(str(Enname_to_id_dict[hero_name]))
    print(",".join(tmp))
    return ",".join(tmp)
if __name__ == "__main__":
    app.run_server(debug=False)