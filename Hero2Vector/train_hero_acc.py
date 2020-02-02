import sys
import pickle
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from model.hero2vec import *
from utils.evaluation import *
from utils.dataset import DataFrameIterator
from acc import *

import torch
import torch.autograd as autograd
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
from torch.utils.data import sampler
from torch.utils.data import Dataset
import json


def train(model, dataloader, devloader,loss_function=nn.CrossEntropyLoss(),
          init_lr=0.1, epochs=100, lr_decay_epoch = 30,
          print_epoch = 10, gpu=False):

    # Cuda is not critical for this task with low dimensionol inputs
    losses = []
    train_accs_top10 = []
    dev_losses = []
    dev_accs_top10 = []
    for epoch in range(epochs):

        # learning rate decay
        div, mod = divmod(epoch, lr_decay_epoch)
        if mod == 0:
            optimizer = optim.SGD(model.parameters(), lr=init_lr*(0.1)**div)

        total_loss = torch.Tensor([0])
        total_dev_loss = torch.Tensor([0])

        # iterate the dataset to load context heroes(team) and center hero(target)
        for teams, targets in dataloader:

            if gpu and torch.cuda.is_available():
                teams = teams.cuda()
                targets = targets.cuda()

            # wrap the embeddings of the team and target center hero to Variable
            inputs = autograd.Variable(teams)
            targets = autograd.Variable(targets.view(-1))

            # zero out the accumulated gradients
            model.zero_grad()

            # Run the forward pass
            out = model(inputs)
            # Compute your loss function.
            loss = loss_function(out, targets)

            # backpropagate and update the embeddings
            loss.backward()
            optimizer.step()

            # record total loss in this epoch
            total_loss += loss.cpu().data
            print(total_loss)
        acc_train_top10 = accuracy_in_train(model,dataloader,batch_size=16)
        train_accs_top10.append(acc_train_top10)
        print("total_loss is %s"%total_loss)
        print("total_train_acc is %s"%acc_train_top10)

        for teams, targets in devloader:

            if gpu and torch.cuda.is_available():
                teams = teams.cuda()
                targets = targets.cuda()

            # wrap the embeddings of the team and target center hero to Variable
            inputs = autograd.Variable(teams)
            targets = autograd.Variable(targets.view(-1))

            # zero out the accumulated gradients
            # model.zero_grad()

            # Run the forward pass
            out = model(inputs)

            # Compute your loss function.
            dev_loss = loss_function(out, targets)
            # print("dev_loss is %s"%dev_loss)

            # # backpropagate and update the embeddings
            # loss.backward()
            # optimizer.step()

            # record total loss in this epoch
            total_dev_loss += dev_loss.cpu().data 
        print("total_dev_loss is %s"%total_dev_loss)
        acc_dev_top10 = accuracy_in_train(model,devloader,batch_size=16)
        print("total_dev_acc is %s"%acc_dev_top10)

        dev_accs_top10.append(acc_dev_top10)
        if epoch % print_epoch == 0:
            print('epoch: %d, loss: %.3f' % (epoch, total_loss/len(dataloader)))
            print("dev loss:%s"%str(total_dev_loss/len(devloader)))
           

        losses.append(total_loss/len(dataloader))
        dev_losses.append(total_dev_loss/len(devloader))
    # return losses for plot
    return np.array(losses),np.array(dev_losses),np.array(train_accs_top10),np.array(dev_accs_top10)

def save_embeddings(model, filename = 'embeddings.npy'):
    embeddings = model.embeddings.weight.cpu().data.numpy()
    np.save(file = filename, arr=embeddings)


# python train_hero.py teams.csv id_hero.json
def main():

    data_dir = "E:/dota_prediction/Hero2vecModel-master/Hero2vecModel-master/teams.csv"
    hero2ix_dir = "E:/dota_prediction/Hero2vecModel-master/Hero2vecModel-master/id_hero.json"

    # import DataFrame and hero2ix dictionary
    heroes_df_dota = pd.read_csv(data_dir, index_col=0)
    heroes_df_dota = heroes_df_dota.dropna().reset_index(drop=True)

    with open(hero2ix_dir, 'r') as fp:
        hero2ix = json.load(fp)

    print(len(heroes_df_dota))
    # train test split
    split_1 = int(len(heroes_df_dota)*0.8)
    split_2 = int(len(heroes_df_dota)*0.9)
    heroes_train_dota = heroes_df_dota.iloc[:split_1]
    heroes_dev_dota = heroes_df_dota.iloc[split_1:split_2]
    heroes_test_dota = heroes_df_dota.iloc[split_2:]

    # build dataset generator
    train_gen = DataFrameIterator(heroes_train_dota, hero2ix)
    dev_gen = DataFrameIterator(heroes_dev_dota, hero2ix)
    test_gen = DataFrameIterator(heroes_test_dota, hero2ix)

    # Use Dataloader class in pytorch to generate batched data
    batch_size = 16
    loader_train = DataLoader(train_gen, batch_size=batch_size,
                              sampler=sampler.RandomSampler(train_gen),num_workers=4
                              )
    loader_dev = DataLoader(dev_gen, batch_size=batch_size,
                              sampler=sampler.RandomSampler(dev_gen),num_workers=4
                              )

    loader_test = DataLoader(test_gen, batch_size=batch_size,
                              sampler=sampler.SequentialSampler(test_gen),num_workers=4
                              )

    # define model, totally three models in hetor2vec.py
    # model = CBOHBilayer(embedding_dim=20, heropool_size=len(hero2ix))
    model = CBOHBilayer(embedding_dim=20, heropool_size=len(hero2ix),hidden_dim=20)

    # define loss function
    loss_function = nn.CrossEntropyLoss()

    # run train
    losses = train(model=model, dataloader=loader_train,devloader=loader_dev,loss_function=loss_function,
                   init_lr=0.1, epochs=20, lr_decay_epoch=8, print_epoch=2, gpu=True)

    # check test accuracy
    print('Top3, Top5 and Top 10 accuracy: ', accuracy_in_train(model, dataloader=loader_test,
                                 batch_size=batch_size, gpu=False))

    # save embeddings as numpy arrays
    output_dir = './output/hero/hero_embeddings.npy'
    save_embeddings(model, filename=output_dir)

    # pickle model
    pickle_dir = './output/hero/model.p'
    pickle.dump(obj=model, file=open(pickle_dir, 'wb'))
    # np.save('loss0',losses[0])
    # np.save('loss1',losses[1])
    # np.save('loss2',losses[2])
    # np.save('loss3',losses[3])

# # plot loss vs epoch
    plot_loss(losses, './output/hero/loss_hitory.png')

    # project embeddings to 2d plane
    plot_embeddings(model, hero2ix)

if __name__ == '__main__':
    main()
