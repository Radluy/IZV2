#!/usr/bin/env python3.8
# coding=utf-8

from matplotlib import pyplot as plt
import pandas as pd
import seaborn as sns
import numpy as np
import os
import pickle, gzip
# muzete pridat libovolnou zakladni knihovnu ci knihovnu predstavenou na prednaskach
# dalsi knihovny pak na dotaz

# Ukol 1: nacteni dat
def get_dataframe(filename: str, verbose: bool = False) -> pd.DataFrame:
    with gzip.open(filename, 'rb') as f:
        df = pickle.load(f)
    #pd.read_pickle
    orig_size = round(df.memory_usage(deep=True).sum() / 1048576, 1)
    date = pd.to_datetime(df['p2a'])
    df['date'] = date
    for (name, data) in df.iteritems():
        if (name != 'region' and name != 'date' and name != 'p13a' and name != 'p13b' and name != 'p13c' and name != 'p53'):
            df[name] = df[name].astype('category')
    new_size = round(df.memory_usage(deep=True).sum() / 1048576, 1)

    if verbose:
        print("orig_size= {} MB".format(orig_size))
        print("new_size= {} MB".format(new_size))
    
    return df
        

# Ukol 2: následky nehod v jednotlivých regionech
def plot_conseq(df: pd.DataFrame, fig_location: str = None,
                show_figure: bool = False):
    sns.set(rc={'axes.facecolor':'grey'})
    fig, axes=plt.subplots(4, 1, figsize=(8, 8))
    ax = axes.flatten()

    aggr = df.groupby('region')['p13a'].sum()
    aggr = aggr.sort_values(ascending=False)
    sns.barplot(ax=ax[0], x=aggr.index, y=aggr.values, color="green").set_title("Umrtia")

    aggr = df.groupby('region')['p13b'].sum()
    aggr = aggr.sort_values(ascending=False)
    sns.barplot(ax=ax[1], x=aggr.index, y=aggr.values, color="blue").set_title("Tazke zranenia")

    aggr = df.groupby('region')['p13c'].sum()
    aggr = aggr.sort_values(ascending=False)
    sns.barplot(ax=ax[2], x=aggr.index, y=aggr.values, color="red").set_title("Lahke zranenia")

    aggr = df.groupby('region')['p13a'].count()
    aggr = aggr.sort_values(ascending=False)
    sns.barplot(ax=ax[3], x=aggr.index, y=aggr.values, color="orange").set_title("Pocet nehod")

    if (fig_location):
        plt.savefig(fig_location)

    plt.tight_layout()
    if (show_figure):
        plt.show()
        

# Ukol3: příčina nehody a škoda
def plot_damage(df: pd.DataFrame, fig_location: str = None,
                show_figure: bool = False):
    sns.set(rc={'axes.facecolor':'grey'})
    fig, axes=plt.subplots(2, 2, figsize=(8, 8))
    #axes.set(yscale="log")
    ax = axes.flatten()

    jhm = df.loc[df['region'] == 'JHM']
    bins = pd.IntervalIndex.from_tuples([(99, 101), (200, 209), (300, 311),
                                         (400, 414), (500, 516), (600, 615)])
    labels = ["nezavineno", "rychlost", "predjizdeni", 
              "prednost", "zpusob", "zavada"]                                        
    causes = pd.cut(jhm['p12'], bins=bins, labels=labels)
    #new_df = pd.DataFrame(cut)
    jhm['p53'] = jhm['p53'] / 10
    bins = pd.IntervalIndex.from_tuples([(-2, 50), (50, 199), (200, 499),
                                         (500, 999), (1000, 1000000)])
    costs = pd.cut(jhm['p53'], bins=bins)
    frame = causes.to_frame()
    frame["cost"] = costs
    a = sns.countplot(data=frame, x="cost", hue="p12", ax=ax[0]).set_title("JHM")
    plt.tight_layout()
    if (show_figure):
        plt.show()
                           

# Ukol 4: povrch vozovky
def plot_surface(df: pd.DataFrame, fig_location: str = None,
                 show_figure: bool = False):
    pass


if __name__ == "__main__":
    pass
    # zde je ukazka pouziti, tuto cast muzete modifikovat podle libosti
    # skript nebude pri testovani pousten primo, ale budou volany konkreni ¨
    # funkce.
    df = get_dataframe("accidents.pkl.gz")
    #plot_conseq(df, fig_location="01_nasledky.png", show_figure=True)
    plot_damage(df, "02_priciny.png", True)
    plot_surface(df, "03_stav.png", True)
