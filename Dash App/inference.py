import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import numpy as np
import keras
from keras.models import load_model
hero_id_max = 129

model_saved_path = "C:\\Users\\wda\\PycharmProjects\\Kitti\\dota_analyze_and_prediction\\Dash App\\data\\568213_2020_03_07_LSTM.h5"   # 模型保存路径
radiant =['114', '21', '96', '54', '68']
dire = [ '86', '98', '76', '8', '3']


def inference(radiant,dire,hero_id_max,model_saved_path):
    sample_in = []
    radiant_vector = np.zeros(hero_id_max)
    dire_vector = np.zeros(hero_id_max)
    assert len(radiant)==5
    for item in radiant:
        assert int(item) <= hero_id_max
        radiant_vector[int(item) - 1] = 1
    assert len(dire)==5
    for item in dire:
        assert int(item) <= hero_id_max
        dire_vector[int(item) - 1] = 1

    sample_in.append([radiant_vector, dire_vector])
    sample_in = np.array(sample_in).reshape(len(sample_in),2,hero_id_max)
    keras.backend.clear_session()    # 计算图清空，防止越来越慢
    model = load_model(model_saved_path)
    out0 = model.predict(sample_in)
    return out0[0][0]

inference(radiant,dire,hero_id_max,model_saved_path)