import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import numpy as np
from dash.dependencies import Input, Output, State
from app import app
from apps import predict
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
html.Div([

    html.Div(
        children= html.Div(id="root",
            children= [
                  html.Div(
                           children= [
                                html.Div(
                                    children=[
                                        html.Div(children=[
                                            html.Div(
                                                html.A("预测",href="/predict"),
                                                className="navigation_text"
                                            )
                                        ],


                                        className="navigation_text_group")

                                    ],
                                    className="navigation_label"
                                )
                            ],
                            className="navigation_root"),

                html.Div(id='page-content')
                ],
            className = "ktYFlp"),

        className="body"
    )


]),

])
def generator_index():
    model = []
    for text in ['预测']:
        if(text == '预测'):
            href = predict
        model.append(html.Div(html.A(text,href=href),className="navigation_text"))
    return html.Div(children=model)

#目录页
index_page = html.Div([

    html.Div(
        children= html.Div(id="root",
            children= [
                  html.Div(
                           children= [
                                html.Div(
                                    children=[
                                        html.Div(children=[
                                            html.Div(
                                                html.A("预测",href="/predict"),
                                                className="navigation_text"
                                            )
                                        ],


                                        className="navigation_text_group")

                                    ],
                                    className="navigation_label"
                                )
                            ],
                            className="navigation_root"),


                ],
            className = "ktYFlp"),
        className="body")


])

# Update the index
@app.callback(Output('page-content', 'children'), [Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/':
        return index_page
    elif pathname == '/predict':
        return predict.predict_layout
    # elif pathname == '/app2':
    #     return app2.layout
    # else:
    #     return 'URL not found'


if __name__ == '__main__':
    #print(generator_index())
    app.run_server(debug=True)