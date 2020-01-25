import dash
import os
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import numpy as np
import dash_html_components as html
from app import app


def generate_select():
    files = os.listdir("assets/hero_icon")
    model = []
    for file in files:
        imgsrc = "assets/hero_icon/"+file
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

def generate_placeholder(A_or_B):
    model = []
    for i in range(5):
        model.append(html.Div(id = str(i)+"_"+A_or_B,className="hero-placeholder hero-img"))

    return html.Div(children=model)

predict_layout = html.Div(
            children=html.Div(
                className="main-section",
                    children = html.Div(className="fWisXZ",
                            children= html.Div(className="dnZKxn",children=
                                        [html.Div(
                                            [html.Span("Hero Combos",className="title"),
                                            html.Span("Search for hero combinations in public and professional matches",className="subtitle")]
                                            ,className="clNgdz"
                                        ),
                                        html.Div(
                                            children=
                                            [
                                                html.Div(className="gZpUvw",
                                                    children = generate_select()
                                            )
                                            ],className="iyjHnf"
                                        ),
                                        html.Div(
                                            children= [
                                                html.Div(
                                                    className = "query_div",
                                                    children= [
                                                        html.Div(
                                                            "英雄筛选",
                                                            className= "query_hint"
                                                        ),
                                                        # input
                                                        dcc.Input(id = "query_input",type="text",className="query_input")


                                                    ]
                                                ),
                                                html.Button("X",className="reset_button",role = "button",tabIndex="0")

                                            ],
                                            className = "query_body"
                                        ),
                                        html.Div(className="TBDUn",
                                                 children=[
                                                     html.Div(className="team-container",children=
                                                        [html.Div("Team A",className="team-title team-a"),
                                                         generate_placeholder("A")
                                                         ]),
                                                     html.Div("vs.",className="seperator"),
                                                     html.Div(className="team-container",
                                                              children=[html.Div("Team B",className="team-title team-b"),
                                                                        generate_placeholder("B")
                                                              ])

                                                 ]
                                                 )
                                        ]
                            )
                    )
                ),
        className = "ktYFlp" )


# class 属性变为className
# style 属性是一个字典
# style内的属性是驼峰格式的
# 像素值的px可以省略

if __name__ == "__main__":
    #generate_select()
    app.run_server(debug=False)