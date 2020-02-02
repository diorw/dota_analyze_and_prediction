import sys
import pickle
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.decomposition import PCA

from model.hero2vec import *
from utils.evaluation import *
from utils.dataset import DataFrameIterator

import torch
import torch.autograd as autograd
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
from torch.utils.data import sampler
from torch.utils.data import Dataset
import json

import pickle

# pickle_dir = './output/hero/model.p'
# # pickle_dir = './output/hero/model_500.p'
#
# with open(pickle_dir, 'rb') as handle:
#     model = pickle.load(handle)
# print(model)
#
#
# # import DataFrame and hero2ix dictionary
#
# heroes_df_dota = pd.read_csv('teams.csv', index_col=0)
#
# heroes_df_dota = heroes_df_dota.dropna().reset_index(drop=True)
# with open('id_hero.json', 'r') as fp:
#     hero_id_dict = json.load(fp)
# # print(hero_id_dict)
# hero2ix = hero_id_dict
# # heroes = hero2ix_df['hero'].values
#
# # train test split
# split = int(len(heroes_df_dota)*0.9)
# heroes_train_dota = heroes_df_dota.iloc[:split]
# heroes_test_dota = heroes_df_dota.iloc[split:]
#
# # build dataset generator
# train_gen = DataFrameIterator(heroes_train_dota, hero2ix)
# test_gen = DataFrameIterator(heroes_test_dota, hero2ix)
#
# # Use Dataloader class in pytorch to generate batched data
# batch_size = 16
# loader_train = DataLoader(train_gen, batch_size=batch_size,
#                             sampler=sampler.RandomSampler(train_gen),
#                             num_workers=4)
# loader_test = DataLoader(test_gen, batch_size=batch_size,
#                             sampler=sampler.SequentialSampler(test_gen),
#                             num_workers=4)

# print(heroes_df_dota)

# def evaluate_in_train(model,,targets,dataloader,batch_size):
#     model.eval()
#     # out = torch.nn.functional.softmax(out, dim=1).data
#     length = len(dataloader)*batch_size
#     count = 0.0
#     for batch_idx in range(0,batch_size):
#     rank = 1
#     for i in range(0,117):
#         targetIdx = targets[batch_idx].item()
#         # print('targetIdx is %s'%targetIdx)
#         # print('%s th item is %s'%(i,out[0][i].item()))
#         # print('target val is%s'%(out[0][targetIdx].item()))
#         if (out[batch_idx][i].item() > out[batch_idx][targetIdx].item()):
#             rank = rank + 1
#     if rank <= 10:
#         count = count + 1
    
#     return count/length


def accuracy_in_train(model, dataloader, batch_size, gpu=False):
    if gpu and torch.cuda.is_available():
        model.cuda()
    model.eval()
    nonprint = True
    # number of total (context_heroes, center_hero)
    length = len(dataloader)*batch_size
    count_3 = 0.0
    count_5 = 0.0
    count_10 = 0.0
    for teams, targets in dataloader:
        if gpu and torch.cuda.is_available():
            teams = teams.cuda()
            targets = targets.cuda()
        inputs = autograd.Variable(teams)
        targets = autograd.Variable(targets.view(-1))
        out = model(inputs)
        out = torch.nn.functional.softmax(out, dim=1).data


        # print(type(out))
        # idx is the index of the maximum value
        val, idx = torch.max(out, dim=1)

        # count how many predictions are right and convert to python int
        # count += idx.eq(targets).sum().cpu().data
        # count += idx.eq(targets).sum().item()
        # for batch_idx in range(0,batch_size):
        #     targetIdx = targets[batch_idx].item()
        #     maxIdx = idx[batch_idx]
        #     # print("true prob is %s"%out[batch_idx][maxIdx].item())
        #     # print("pred prob is %s"%out[batch_idx][targetIdx].item())
        #     count = count + out[batch_idx][targetIdx].item() /out[batch_idx][maxIdx].item()



        for batch_idx in range(0,batch_size):
            rank = 1
            for i in range(0,117):
                targetIdx = targets[batch_idx].item()
                # print('targetIdx is %s'%targetIdx)
                # print('%s th item is %s'%(i,out[0][i].item()))
                # print('target val is%s'%(out[0][targetIdx].item()))
                if (out[batch_idx][i].item() > out[batch_idx][targetIdx].item()):
                    rank = rank + 1
            if rank <= 10:
                count_10 = count_10 + 1
            if rank <= 5:
                count_5 = count_5 + 1
            if rank <= 3:
                count_3 = count_3 + 1



        nonprint = False

    return count_3/length,count_5/length,count_10/length


def show_embeddings(model, names):
    embeddings = model.embeddings.weight.cpu().data.numpy()
    # print(np.mean(embeddings, axis=0))
    #makes mean at 0
    embeddings -= np.mean(embeddings, axis=0)
    # print(embeddings.shape)
    np.save('hero_embeddings', embeddings)
    # print(embeddings[116])
    pca = PCA(n_components=2)
    embeddings_2d = pca.fit_transform(embeddings)
    x, y = embeddings_2d[:, 0], embeddings_2d[:, 1]
    for name, i in names.items():
        if i > 113:
            continue
        if i == 1:
            print(name)
            print(x[i])
            print(y[i])
            print(names[name])
    # print(embeddings)
    # print(hero2ix)

    # run pca to reduce to 2 dimensions
    # pca = PCA(n_components=2)
    # embeddings_2d = pca.fit_transform(embeddings)
    # x, y = embeddings_2d[:, 0], embeddings_2d[:, 1]
    # make_plot_color(x, y, names)

# print('Top3, Top5 and Top 10 accuracy: ', accuracy_in_train(model, dataloader=loader_test,
#                                  batch_size=16, gpu=False))

# show_embeddings(model, hero2ix)
# print(model)


