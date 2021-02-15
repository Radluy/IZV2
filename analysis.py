#!/usr/bin/env python3.8
# coding=utf-8

from matplotlib import pyplot as plt
import pandas as pd
import seaborn as sns
import numpy as np
import os
import pickle, gzip

regions = ['JHM', 'PHA', 'STC', 'HKK']
important_columns = ['region', 'date', 'p13a', 'p13b', 'p13c', 'p53', 'p16']


def get_dataframe(filename: str, verbose: bool = False) -> pd.DataFrame:
    '''
    Loads data and converts to categorical types.

            Parameters:
                    filename (str): name of file with data
                    verbose (bool): whether to print saved size

            Returns:
                    df (pd.DataFrame): Pandas DataFrame with data
    '''
    with gzip.open(filename, 'rb') as f:
        df = pickle.load(f)

    orig_size = round(df.memory_usage(deep=True).sum() / 1048576, 1)
    date = pd.to_datetime(df['p2a'])
    df['date'] = date
    for (name, data) in df.iteritems():
        if (name not in important_columns):
            df[name] = df[name].astype('category')
    new_size = round(df.memory_usage(deep=True).sum() / 1048576, 1)

    if verbose:
        print("orig_size= {} MB".format(orig_size))
        print("new_size= {} MB".format(new_size))

    return df


def plot_conseq(df: pd.DataFrame, fig_location: str = None,
                show_figure: bool = False):
    '''
    Plots consequences of car crashes.

            Parameters:
                    df (pd.DataFrame): DataFrame with data to plot
                    fig_location (str): File name to save figure
                    show_figure (bool): Whether to show figure

    '''
    sns.set(rc={'axes.facecolor': 'grey'})
    fig, axes = plt.subplots(4, 1, figsize=(8, 8))
    ax = axes.flatten()

    aggrmax = df.groupby('region')['p13a'].count()
    aggrmax = aggrmax.sort_values(ascending=False)
    sns.barplot(ax=ax[3], x=aggrmax.index, y=aggrmax.values,
                color="orange").set_title("Pocet nehod")

    aggr = df.groupby('region')['p13a'].sum()
    aggr = aggr.sort_values(ascending=False)
    sns.barplot(ax=ax[0], x=aggr.index, y=aggr.values,
                color="green", order=aggrmax.index).set_title("Umrtia")

    aggr = df.groupby('region')['p13b'].sum()
    aggr = aggr.sort_values(ascending=False)
    sns.barplot(ax=ax[1], x=aggr.index, y=aggr.values,
                color="blue", order=aggrmax.index).set_title("Tazke zranenia")

    aggr = df.groupby('region')['p13c'].sum()
    aggr = aggr.sort_values(ascending=False)
    sns.barplot(ax=ax[2], x=aggr.index, y=aggr.values,
                color="red", order=aggrmax.index).set_title("Lahke zranenia")

    for i in range(4):
        ax[i].set_xlabel('')

    plt.tight_layout()
    if (fig_location):
        plt.savefig(fig_location)

    if (show_figure):
        plt.show()


def plot_damage(df: pd.DataFrame, fig_location: str = None,
                show_figure: bool = False):
    '''
    Plots damage caused in car crashes.

            Parameters:
                    df (pd.DataFrame): DataFrame with data to plot
                    fig_location (str): File name to save figure
                    show_figure (bool): Whether to show figure

    '''
    sns.set(rc={'axes.facecolor': 'grey'})
    fig, axes = plt.subplots(2, 2, figsize=(12, 8))
    ax = axes.flatten()

    i = 0
    for region in regions:
        ax[i].set(yscale="log")
        jhm = df.loc[df['region'] == region]
        bins = pd.IntervalIndex.from_tuples([(99, 101), (200, 209),
                                            (300, 311), (400, 414),
                                            (500, 516), (600, 615)])
        labels = ["nezavineno", "rychlost", "predjizdeni",
                  "prednost", "zpusob jizdy", "zavada"]
        causes = pd.cut(jhm['p12'], bins=bins, labels=labels)
        bins = pd.IntervalIndex.from_tuples([(-2, 50), (50, 199), (200, 499),
                                            (500, 999), (1000, 1000000)])
        costs = pd.cut(jhm['p53'].div(10), bins=bins)
        frame = causes.to_frame()
        frame["cost"] = costs
        sns.countplot(data=frame, x="cost", hue="p12",
                      ax=ax[i]).set_title(region)
        ax[i].set_xlabel('Skoda[tisic KC]')
        ax[i].set_xticklabels(["<50", "50-200", "200-500",
                               "500-1000", ">1000"])
        ax[i].set_ylabel('Pocet')
        ax[i].get_legend().remove()
        i += 1
    handles, labelis = ax[3].get_legend_handles_labels()
    fig.legend(handles, labels, bbox_to_anchor=(1, 0.6))

    plt.tight_layout()
    plt.subplots_adjust(right=0.85)

    if (fig_location):
        plt.savefig(fig_location)

    if (show_figure):
        plt.show()


def plot_surface(df: pd.DataFrame, fig_location: str = None,
                 show_figure: bool = False):
    '''
    Plots the types of surfaces when car crashes happened.

            Parameters:
                    df (pd.DataFrame): DataFrame with data to plot
                    fig_location (str): File name to save figure
                    show_figure (bool): Whether to show figure

    '''
    sns.set(rc={'axes.facecolor': 'grey'})
    fig, axes = plt.subplots(2, 2, figsize=(12, 8))
    ax = axes.flatten()

    df_c = pd.DataFrame()
    df_c['date'] = df['date']
    df_c['p16'] = df['p16']
    df_c['region'] = df['region']

    new = pd.crosstab([df_c['region'], df_c['date']], df_c['p16'])
    new = new.reset_index()

    i = 0
    for region in regions:
        one = new.loc[new['region'] == region]
        two = one.groupby(pd.Grouper(key='date', freq='M')).sum().reset_index()
        sns.lineplot(data=two, ax=ax[i]).set_title(region)
        ax[i].set_xlabel('')
        ax[i].set_ylabel('Pocet')
        ax[i].get_legend().remove()
        i += 1
    labels = ["Iny stav", "Suchy neznecisteny", "Suchy znecisteny",
              "Mokry", "Blato", "Lad- posypane", "Lad- neposypane",
              "Rozliaty olej/nafta", "Snehova vrstva", "Nahla zmena"]
    handles, labelis = ax[3].get_legend_handles_labels()
    fig.legend(handles, labels, bbox_to_anchor=(1, 0.6))

    plt.tight_layout()
    plt.subplots_adjust(right=0.8)

    if (fig_location):
        plt.savefig(fig_location)

    if (show_figure):
        plt.show()


if __name__ == "__main__":
    df = get_dataframe("accidents.pkl.gz", True)
    plot_conseq(df, fig_location="01_nasledky.png", show_figure=True)
    plot_damage(df, "02_priciny.png", True)
    plot_surface(df, "03_stav.png", True)
