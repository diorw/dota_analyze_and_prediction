import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.decomposition import PCA
from adjustText import adjust_text

import torch
import torch.autograd as autograd
import torch.nn as nn
import torch.optim as optim

def accuracy(model, dataloader, batch_size, gpu=False):
    if gpu and torch.cuda.is_available():
        model.cuda()
    model.eval()

    # number of total (context_heroes, center_hero)
    length = len(dataloader)*batch_size
    count = 0
    for teams, targets in dataloader:
        if gpu and torch.cuda.is_available():
            teams = teams.cuda()
            targets = targets.cuda()
        inputs = autograd.Variable(teams)
        targets = autograd.Variable(targets.view(-1))
        out = model(inputs)

        # idx is the index of the maximum value
        val, idx = torch.max(out, dim=1)

        # count how many predictions are right and convert to python int
        count += idx.eq(targets).sum().cpu().data
    return count/length

def make_plot_color(x, y, hero2ix):

    # divide heroes to their own categories/roles
    tank = set(['dva', 'orisa', 'reinhardt', 'roadhog', 'winston', 'zarya'])
    supporter = set(['ana', 'lucio', 'mercy', 'moira', 'symmetra', 'zenyatta'])
    # tank = set()
    # supporter = set()
    tanks, supporters, dps = [], [], []
    for name, idx in hero2ix.items():
        if idx > 113:
            continue
        if name in tank:
            tanks.append(idx)
        elif name in supporter:
            supporters.append(idx)
        else:
            dps.append(idx)

    # plot tank, dps, and supporters respectively
    att_x, att_y = x[tanks], y[tanks]
    den_x, den_y = x[supporters], y[supporters]
    con_x, con_y = x[dps], y[dps]
    fig = plt.figure(figsize=(48, 64), dpi = 400)
    ax = plt.subplot(111)
    marker_size = 200
    ax.scatter(att_x, att_y, c= 'tomato', s=marker_size)
    ax.scatter(den_x, den_y, c = 'darkcyan', s=marker_size)
    ax.scatter(con_x, con_y, c = 'royalblue', s=marker_size)

    # annotate each hero's name
    for name, i in hero2ix.items():
        if i > 113:
            continue
        ax.annotate(name, (x[i], y[i]), fontsize=12)
    plt.show()
    fig.savefig('./output/hero/hero_embddings_2d.png')

def make_plot_color_map(x, y, map2ix):

    # divide maps to their own categories
    attacks, defenses, controls = [], [], []
    for name, idx in map2ix.items():
        name = name.split('_')
        if name[1] == 'Attack':
            attacks.append(idx)
        elif name[1] == 'Defense':
            defenses.append(idx)
        else:
            controls.append(idx)

    # plot attack, defense, controls map respectively
    att_x, att_y = x[attacks], y[attacks]
    den_x, den_y = x[defenses], y[defenses]
    con_x, con_y = x[controls], y[controls]

    fig = plt.figure(figsize=(16, 12), dpi = 100)
    ax = plt.subplot(111)
    marker_size = 200
    ax.scatter(att_x, att_y, c= 'tomato', s=marker_size)
    ax.scatter(den_x, den_y, c = 'darkcyan', s=marker_size)
    ax.scatter(con_x, con_y, c = 'royalblue', s=marker_size)

    texts = []
    # annotate each map's name
    for name, i in map2ix.items():
        # ax.annotate(name, (x[i], y[i]))
        texts.append(ax.text(x[i], y[i], name))
    adjust_text(texts)
    plt.show()
    fig.savefig('./output/map/map_embddings_2d_adjusted.png')

def plot_embeddings(model, names):
    embeddings = model.embeddings.weight.cpu().data.numpy()

    #makes mean at 0
    embeddings -= np.mean(embeddings, axis=0)

    # run pca to reduce to 2 dimensions
    pca = PCA(n_components=2)
    embeddings_2d = pca.fit_transform(embeddings)
    x, y = embeddings_2d[:, 0], embeddings_2d[:, 1]
    make_plot_color(x, y, names)

def plot_embeddings_map(model, names):
    embeddings = model.map_embeddings.weight.cpu().data.numpy()

    #makes mean at 0
    embeddings -= np.mean(embeddings, axis=0)

    # run pca to reduce to 2 dimensions
    pca = PCA(n_components=2)
    embeddings_2d = pca.fit_transform(embeddings)
    x, y = embeddings_2d[:, 0], embeddings_2d[:, 1]
    make_plot_color_map(x, y, names)

def plot_loss(losses, directory):
    fig = plt.figure(figsize=(8, 6), dpi=100)
    ax = plt.subplot(111)
    ax.plot(losses[0],label = "Train loss")
    ax.plot(losses[1],label = "Dev loss")
    ax.plot(losses[2],label = "Train Top 10 Accuracy")
    ax.plot(losses[3],label = "Dev Top 10 Accuracy")
    ax.set_xlabel('Epochs', fontsize=24)
    ax.set_ylabel('Train_loss', fontsize=24)
    ax.legend()
    fig.savefig(directory)
    plt.close()

# import pickle

# pickle_dir = './output/hero/model.p'
# with open(pickle_dir, 'rb') as handle:
#     model = pickle.load(handle)



# # import DataFrame and hero2ix dictionary

# heroes_df_dota = pd.read_csv('teams.csv', index_col=0)

# heroes_df_dota = heroes_df_dota.dropna().reset_index(drop=True)
# with open('id_hero.json', 'r') as fp:
#     hero_id_dict = json.load(fp)
# print(hero_id_dict)
# hero2ix = hero_id_dict
# # heroes = hero2ix_df['hero'].values

# # train test split
# split = int(len(heroes_df_dota)*0.9)
# heroes_train_dota = heroes_df_dota.iloc[:split]
# heroes_test_dota = heroes_df_dota.iloc[split:]

# # build dataset generator
# train_gen = DataFrameIterator(heroes_train_dota, hero2ix)
# test_gen = DataFrameIterator(heroes_test_dota, hero2ix)

# # Use Dataloader class in pytorch to generate batched data
# batch_size = 16
# loader_train = DataLoader(train_gen, batch_size=batch_size,
#                             sampler=sampler.RandomSampler(train_gen),
#                             num_workers=4)
# loader_test = DataLoader(test_gen, batch_size=batch_size,
#                             sampler=sampler.SequentialSampler(test_gen),
#                             num_workers=4)