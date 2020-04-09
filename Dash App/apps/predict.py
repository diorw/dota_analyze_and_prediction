import os
import dash_core_components as dcc
import dash_html_components as html
from app import app
from dash.dependencies import Input, Output,State
import numpy as np
import keras
from keras.models import load_model

hero_id_max = 129
model_saved_path = "C:\\Users\\wda\\PycharmProjects\\Kitti\\dota_analyze_and_prediction\\Dash App\\data\\568213_2020_03_07_LSTM.h5"
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
                                               html.Div(str(file).rstrip("_full.png"),className="name"),
                                               html.Div("A",className="team-indicator team-a"),
                                               html.Div("B",className="team-indicator team-b")



                                           ]),
                                  html.Img(src=imgsrc),
                                  html.Div(className="ts-container ",
                                           children=[
                                            html.Div("Add To Team A",id = str(file).rstrip("_full.png")+"_A",className="ts ts-left",role="button",tabIndex="0"),
                                            html.Div("Add To Team B",id = str(file).rstrip("_full.png")+"_B", className="ts ts-right", role="button",
                                                        tabIndex="0")
                                           ])
                              ]
                            )
        model.append(hero_block)
    return model

def generate_placeholder(*args):
    model = []
    A_or_B = args[0]
    for i in range(5):
        model.append(html.Img(id = str(i)+"_"+A_or_B,className="hero-placeholder hero-img"))

    return html.Div(children=model)

def generate_input(*args):
    model = []
    A_or_B = args[0]
    for i in range(5):
        model.append(dcc.Input(id = str(i)+"_playerid_"+A_or_B,className="player-input hero-img"))

    return html.Div(children=model)

predict_layout = html.Div(
            children=html.Div(
                className="main-section",
                    children = html.Div(className="fWisXZ",
                            children= html.Div(className="dnZKxn",
                                        children=[html.Div(
                                            [html.Span("Hero Combos",className="title"),
                                            html.Span("Search for hero combinations in public and professional matches",className="subtitle")]
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
                                                         dcc.Input(id = 'hidden_A',type='text')
                                                         ]

                                                        ),

                                                     html.Div("vs.",className="seperator"),
                                                     html.Div(className="team-container",
                                                              children=[html.Div("Team B",className="team-title team-b"),
                                                                        generate_placeholder("B"),
                                                                        dcc.Input(id='hidden_B',type='text'
                                                                                 )
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
    [Input(component_id="submit_query", component_property='n_clicks'),
     Input(component_id='hidden_A', component_property='value'),
     Input(component_id='hidden_B', component_property='value')]

)
def inference(n_clicks,radiant,dire):
    sample_in = []
    radiant_list = list(map(int, radiant.split(',')))
    dire_list = list(map(int, dire.split(',')))
    radiant_vector = np.zeros(hero_id_max)
    dire_vector = np.zeros(hero_id_max)
    print(radiant_list)
    print(dire_list)
    for item in radiant_list:
        radiant_vector[int(item) - 1] = 1
    for item in dire_list:
        dire_vector[int(item) - 1] = 1

    sample_in.append([radiant_vector, dire_vector])
    sample_in = np.array(sample_in).reshape(len(sample_in),2,hero_id_max)
    keras.backend.clear_session()    # 计算图清空，防止越来越慢
    model = load_model(model_saved_path)
    out0 = model.predict(sample_in)
    return "预测天辉方胜率为 "+str(round(out0[0][0]*100,2))+"%"



if __name__ == "__main__":
    app.run_server(debug=False)