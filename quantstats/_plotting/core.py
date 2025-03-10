#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#
# Quantreturns: Portfolio analytics for quants
# https://github.com/ranaroussi/quantreturns
#
# Copyright 2019 Ran Aroussi
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import pandas as pd
import numpy as np
from KDEpy import FFTKDE
import plotly.graph_objs as go
from plotly.subplots import make_subplots
import plotly
import plotly.figure_factory as ff
import matplotlib.pyplot as _plt
import plotly.express as px

try:
    _plt.rcParams["font.family"] = "Arial"
except Exception:
    pass

import matplotlib.dates as _mdates
from matplotlib.ticker import (
    FormatStrFormatter as _FormatStrFormatter,
    FuncFormatter as _FuncFormatter
)

import pandas as _pd
import numpy as _np
import seaborn as _sns
from .. import (
    stats as _stats, utils as _utils,
)

_sns.set(font_scale=1.1, rc={
    'figure.figsize': (10, 6),
    'axes.facecolor': 'white',
    'figure.facecolor': 'white',
    'grid.color': '#dddddd',
    'grid.linewidth': 0.5,
    "lines.linewidth": 1.5,
    'text.color': '#333333',
    'xtick.color': '#666666',
    'ytick.color': '#666666'
})

_FLATUI_COLORS = ["#fedd78", "#348dc1", "#af4b64",
                  "#4fa487", "#9b59b6", "#808080"]
_GRAYSCALE_COLORS = ['silver', '#222222', 'gray'] * 3


def _get_colors(grayscale):
    colors = _FLATUI_COLORS
    ls = '-'
    alpha = .8
    if grayscale:
        colors = _GRAYSCALE_COLORS
        ls = '-'
        alpha = 0.5
    return colors, ls, alpha


def plot_returns_bars(returns, benchmark=None,
                      returns_label="Strategy",
                      hline=None, hlw=None, hlcolor="red", hllabel="",
                      resample="A", title="Returns", match_volatility=False,
                      log_scale=False, figsize=(10, 6),
                      grayscale=False, fontname='Arial', ylabel=True,
                      subtitle=True, savefig=None, show=True):
    if match_volatility and benchmark is None:
        raise ValueError('match_volatility requires passing of '
                         'benchmark.')
    if match_volatility and benchmark is not None:
        bmark_vol = benchmark.loc[returns.index].std()
        returns = (returns / returns.std()) * bmark_vol

    # ---------------
    colors, _, _ = _get_colors(grayscale)
    df = _pd.DataFrame(index=returns.index, data={returns_label: returns})
    if isinstance(benchmark, _pd.Series):
        df['Benchmark'] = benchmark[benchmark.index.isin(returns.index)]
        df = df[['Benchmark', returns_label]]

    df = df.dropna()
    if resample is not None:
        df = df.resample(resample).apply(
            _stats.comp).resample(resample).last()
    # ---------------

    fig = go.Figure()
    # fig, ax = _plt.subplots(figsize=figsize)
    # ax.spines['top'].set_visible(False)
    # ax.spines['right'].set_visible(False)
    # ax.spines['bottom'].set_visible(False)
    # ax.spines['left'].set_visible(False)

    # use a more precise date string for the x axis locations in the toolbar
    fig.update_layout(title=title + "\n")
    # fig.suptitle(title+"\n", y=.99, fontweight="bold", fontname=fontname,
    #              fontsize=14, color="black")

    if subtitle:
        fig.update_layout(title=title + "\n" + "\n%s - %s                   " % (
            df.index.date[:1][0].strftime('%Y'),
            df.index.date[-1:][0].strftime('%Y')))
        fig.update_xaxes(title_text=str(df.index.date[:1][0].strftime('%Y')))
        # ax.set_title("\n%s - %s                   " % (
        #     df.index.date[:1][0].strftime('%Y'),
        #     df.index.date[-1:][0].strftime('%Y')
        # ), fontsize=12, color='gray')

    if benchmark is None:
        colors = colors[1:]
    # print(df)
    fig.add_trace(go.Bar(
        x=df.index, y=df['Strategy'], width=[0.2]
    ))
    fig.update_yaxes(tickformat="%")
    # df.plot(kind='bar', ax=ax, color=colors)

    # fig.set_facecolor('white')
    # ax.set_facecolor('white')

    try:
        fig.update_layout(xaxis=dict(
            tickmode='linear',
            tick0=df.index.year[0],
            dtick=df.index.year
        ))
        # ax.set_xticklabels(df.index.year)
        years = sorted(list(set(df.index.year)))
    except AttributeError:
        # ax.set_xticklabels(df.index)
        fig.update_layout(xaxis=dict(
            tickmode='linear',
            tick0=df.index[0],
            dtick=df.index
        ))
        years = sorted(list(set(df.index)))

    # ax.fmt_xdata = _mdates.DateFormatter('%Y-%m-%d')
    # years = sorted(list(set(df.index.year)))
    if len(years) > 10:
        mod = int(len(years) / 10)
        # _plt.xticks(_np.arange(len(years)), [
        #     str(year) if not i % mod else '' for i, year in enumerate(years)])

    # rotate and align the tick labels so they look better
    # fig.autofmt_xdate()

    if hline:
        if grayscale:
            hlcolor = 'gray'
        # ax.axhline(hline, ls="--", lw=hlw, color=hlcolor,
        #            label=hllabel, zorder=2)

    # ax.axhline(0, ls="--", lw=1, color="#000000", zorder=2)
    fig.add_hline(y=0)

    if isinstance(benchmark, _pd.Series) or hline:
        pass
        # ax.legend(fontsize=12)

    # _plt.yscale("symlog" if log_scale else "linear")

    fig.update_layout(xaxis_title='')
    # ax.set_xlabel('')

    if ylabel:
        fig.update_layout(yaxis_label="Returns")
        # ax.set_ylabel("Returns", fontname=fontname,
        #               fontweight='bold', fontsize=12, color="black")
        # ax.yaxis.set_label_coords(-.1, .5)

    # ax.yaxis.set_major_formatter(_FuncFormatter(format_pct_axis))

    # try:
    #     _plt.subplots_adjust(hspace=0, bottom=0, top=1)
    # except Exception:
    #     pass
    #
    # try:
    #     fig.tight_layout()
    # except Exception:
    #     pass
    #
    # if savefig:
    #     if isinstance(savefig, dict):
    #         _plt.savefig(**savefig)
    #     else:
    #         _plt.savefig(savefig)

    if show:
        # _plt.show(block=False)
        fig.show()

    # _plt.close()

    if not show:
        return fig

    return None


def plot_timeseries(returns, benchmark=None,
                    title="Returns", compound=False, cumulative=True,
                    fill=False, returns_label="Strategy",
                    hline=None, hlw=None, hlcolor="red", hllabel="",
                    percent=True, match_volatility=False, log_scale=False,
                    resample=None, lw=1.5, figsize=(10, 6), ylabel="",
                    grayscale=False, fontname="Arial",
                    subtitle=True, savefig=None, show=True):
    colors, ls, alpha = _get_colors(grayscale)

    returns.fillna(0, inplace=True)
    if isinstance(benchmark, _pd.Series):
        benchmark.fillna(0, inplace=True)

    if match_volatility and benchmark is None:
        raise ValueError('match_volatility requires passing of '
                         'benchmark.')
    if match_volatility and benchmark is not None:
        bmark_vol = benchmark.std()
        returns = (returns / returns.std()) * bmark_vol

    # ---------------
    if compound is True:
        if cumulative:
            returns = _stats.compsum(returns)
            if isinstance(benchmark, _pd.Series):
                benchmark = _stats.compsum(benchmark)
        else:
            returns = returns.cumsum()
            if isinstance(benchmark, _pd.Series):
                benchmark = benchmark.cumsum()

    if resample:
        returns = returns.resample(resample)
        returns = returns.last() if compound is True else returns.sum()
        if isinstance(benchmark, _pd.Series):
            benchmark = benchmark.resample(resample)
            benchmark = benchmark.last(
            ) if compound is True else benchmark.sum()
    # ---------------

    fig = go.Figure()
    # fig, ax = _plt.subplots(figsize=figsize)
    # ax.spines['top'].set_visible(False)
    # ax.spines['right'].set_visible(False)
    # ax.spines['bottom'].set_visible(False)
    # ax.spines['left'].set_visible(False)
    fig.update_layout(title=title + "\n")
    # fig.suptitle(title+"\n", y=.99, fontweight="bold", fontname=fontname,
    #              fontsize=14, color="black")

    if subtitle:
        fig.update_layout(title=title + "\n" + "\n%s - %s                  " % (
            returns.index.date[:1][0].strftime('%e %b \'%y'),
            returns.index.date[-1:][0].strftime('%e %b \'%y')
        ))
        # ax.set_title("\n%s - %s                  " % (
        #     returns.index.date[:1][0].strftime('%e %b \'%y'),
        #     returns.index.date[-1:][0].strftime('%e %b \'%y')
        # ), fontsize=12, color='gray')

    # fig.set_facecolor('white')
    # ax.set_facecolor('white')

    # TODO: fix this
    if isinstance(benchmark, _pd.Series):
        # ax.plot(benchmark, lw=lw, ls=ls, label="Benchmark", color=colors[0])
        pass

    alpha = .25 if grayscale else 1
    df = pd.DataFrame()
    df['date'] = returns.index
    df['value'] = returns.tolist()
    if title == 'Underwater Plot':
        fig.add_trace(go.Scatter(x=df['date'], y=df['value'], fill='tozeroy'))
    else:
        fig.add_trace(go.Scatter(x=df['date'], y=df['value']))
    # ax.plot(returns, lw=lw, label=returns_label, color=colors[1], alpha=alpha)

    # if fill:
    #     ax.fill_between(returns.index, 0, returns, color=colors[1], alpha=.25)

    # rotate and align the tick labels so they look better
    # fig.autofmt_xdate()
    fig.update_yaxes(tickformat="%")

    # use a more precise date string for the x axis locations in the toolbar
    # ax.fmt_xdata = _mdates.DateFormatter('%Y-%m-%d')

    if hline:
        hlcolor = 'black'
        if grayscale:
            hlcolor = 'red'
        fig.add_hline(y=hline, line_dash='dot')
        # ax.axhline(hline, ls="--", lw=hlw, color=hlcolor,
        #            label=hllabel, zorder=2)

    # ax.axhline(0, ls="-", lw=1,
    #            color='gray', zorder=1)
    # ax.axhline(0, ls="--", lw=1,
    #            color='white' if grayscale else 'black', zorder=2)
    fig.add_hline(y=0, line_dash="solid")

    if isinstance(benchmark, _pd.Series) or hline:
        pass
        # ax.legend(fontsize=12)

    # _plt.yscale("symlog" if log_scale else "linear")

    if percent:
        pass
        # ax.yaxis.set_major_formatter(_FuncFormatter(format_pct_axis))
        # ax.yaxis.set_major_formatter(_plt.FuncFormatter(
        #     lambda x, loc: "{:,}%".format(int(x*100))))

    # ax.set_xlabel('')
    fig.update_layout(xaxis_title='')
    if ylabel:
        fig.update_layout(yaxis_title=ylabel, font=dict(family=fontname, size=12, color="black"))
        # ax.set_ylabel(ylabel, fontname=fontname,
        #               fontweight='bold', fontsize=12, color="black")
    # ax.yaxis.set_label_coords(-.1, .5)

    # try:
    #     _plt.subplots_adjust(hspace=0, bottom=0, top=1)
    # except Exception:
    #     pass
    #
    # try:
    #     fig.tight_layout()
    # except Exception:
    #     pass

    if savefig:
        pass
        # if isinstance(savefig, dict):
        #     _plt.savefig(**savefig)
        # else:
        #     _plt.savefig(savefig)

    if show:
        fig.show()
        # _plt.show(block=False)

    # _plt.close()

    if not show:
        return fig

    return None


def plot_histogram(returns, resample="M", bins=20,
                   fontname='Arial', grayscale=False,
                   title="Returns", kde=True, figsize=(10, 6),
                   ylabel=True, subtitle=True, compounded=True,
                   savefig=None, show=True):
    colors = ['#348dc1', '#003366', 'red']
    if grayscale:
        colors = ['silver', 'gray', 'black']

    apply_fnc = _stats.comp if compounded else _np.sum
    returns = returns.fillna(0).resample(resample).apply(
        apply_fnc).resample(resample).last()

    # fig = go.Figure()
    fig = make_subplots(rows=1, cols=1, shared_xaxes=True, shared_yaxes=True)
    # fig, ax = _plt.subplots(figsize=figsize)
    # ax.spines['top'].set_visible(False)
    # ax.spines['right'].set_visible(False)
    # ax.spines['bottom'].set_visible(False)
    # ax.spines['left'].set_visible(False)

    fig.update_layout(title=title + "\n")
    # fig.suptitle(title + "\n", y=.99, fontweight="bold", fontname=fontname,
    #              fontsize=14, color="black")

    if subtitle:
        fig.update_layout(title=title + "\n" + "\n%s - %s                   " % (
            returns.index.date[:1][0].strftime('%Y'),
            returns.index.date[-1:][0].strftime('%Y')
        ))
        # ax.set_title("\n%s - %s                   " % (
        #     returns.index.date[:1][0].strftime('%Y'),
        #     returns.index.date[-1:][0].strftime('%Y')
        # ), fontsize=12, color='gray')

    # fig.set_facecolor('white')
    # ax.set_facecolor('white')
    # ax.axvline(returns.mean(), ls="--", lw=1.5,
    #            color=colors[2], zorder=2, label="Average")
    df = pd.DataFrame()
    df['date'] = returns.index
    df['value'] = returns.tolist()
    # print(df['date'])
    x, y1 = FFTKDE(bw="silverman").fit(np.array(df['value'].values.tolist())).evaluate(2 ** 10)
    df['maxY'] = max(y1)
    fig.add_trace(
        go.Bar(x=df['value'], y=df['maxY'], name="Monthly Returns"), row=1, col=1
    )
    fig.add_trace(
        go.Scatter(
            x=x, y=y1, name="KDE Scatter"
        ),
        row=1, col=1
    )
    # _sns.histplot(returns, bins=bins,
    #               color=colors[0],
    #               alpha=1,
    #               kde=kde,
    #               stat="density",
    #               ax=ax)
    # _sns.kdeplot(returns, color='black', linewidth=1.5)
    #
    # ax.xaxis.set_major_formatter(_plt.FuncFormatter(
    #     lambda x, loc: "{:,}%".format(int(x * 100))))
    fig.add_vline(x=returns.mean(), line_dash="dash", line_color=colors[2], annotation_text="Average",
                  annotation_position="top left", row=1, col=1)
    fig.add_hline(y=0.01, line_color="#000000")
    # ax.axhline(0.01, lw=1, color="#000000", zorder=2)
    fig.add_vline(x=0, line_color="#000000")
    # ax.axvline(0, lw=1, color="#000000", zorder=2)

    fig.update_layout(xaxis_title='')
    fig.update_xaxes(tickformat="%")
    # ax.set_xlabel('')
    if ylabel:
        fig.update_layout(yaxis_title="Occurrences")
        # ax.set_ylabel("Occurrences", fontname=fontname,
        #               fontweight='bold', fontsize=12, color="black")
        # ax.yaxis.set_label_coords(-.1, .5)

    # ax.legend(fontsize=12)

    # fig.autofmt_xdate()

    # try:
    #     _plt.subplots_adjust(hspace=0, bottom=0, top=1)
    # except Exception:
    #     pass
    #
    # try:
    #     fig.tight_layout()
    # except Exception:
    #     pass
    #
    # if savefig:
    #     if isinstance(savefig, dict):
    #         _plt.savefig(**savefig)
    #     else:
    #         _plt.savefig(savefig)
    #     pass

    if show:
        fig.show()

    # _plt.close()

    if not show:
        return fig

    return fig


def plot_rolling_stats(returns, benchmark=None, title="",
                       returns_label="Strategy",
                       hline=None, hlw=None, hlcolor="red", hllabel="",
                       lw=1.5, figsize=(10, 6), ylabel="",
                       grayscale=False, fontname="Arial", subtitle=True,
                       savefig=None, show=True):
    colors, _, _ = _get_colors(grayscale)

    fig = go.Figure()
    # fig, ax = _plt.subplots(figsize=figsize)
    # ax.spines['top'].set_visible(False)
    # ax.spines['right'].set_visible(False)
    # ax.spines['bottom'].set_visible(False)
    # ax.spines['left'].set_visible(False)

    df = _pd.DataFrame(index=returns.index, data={returns_label: returns})
    # print(df)
    # if isinstance(benchmark, _pd.Series):
    #     df['Benchmark'] = benchmark[benchmark.index.isin(returns.index)]
    #     df = df[['Benchmark', returns_label]].dropna()
    #     ax.plot(df['Benchmark'], lw=lw, label="Benchmark",
    #             color=colors[0], alpha=.8)

    fig.add_trace(go.Scatter(
        x=df.index, y=df[returns_label].dropna()
    ))
    # ax.plot(df[returns_label].dropna(), lw=lw,
    #         label=returns_label, color=colors[1])

    # rotate and align the tick labels so they look better
    # fig.autofmt_xdate()

    # use a more precise date string for the x axis locations in the toolbar
    # ax.fmt_xdata = _mdates.DateFormatter('%Y-%m-%d')
    fig.update_layout(title=title + "\n")
    # fig.suptitle(title + "\n", y=.99, fontweight="bold", fontname=fontname,
    #              fontsize=14, color="black")

    if subtitle:
        fig.update_layout(title=title + "\n" + "\n%s - %s                   " % (
            df.index.date[:1][0].strftime('%e %b \'%y'),
            df.index.date[-1:][0].strftime('%e %b \'%y')
        ))
        # ax.set_title("\n%s - %s                   " % (
        #     df.index.date[:1][0].strftime('%e %b \'%y'),
        #     df.index.date[-1:][0].strftime('%e %b \'%y')
        # ), fontsize=12, color='gray')

    if hline:
        if grayscale:
            hlcolor = 'black'
            fig.add_hline(y=hline, line_color=hlcolor)
        # ax.axhline(hline, ls="--", lw=hlw, color=hlcolor,
        #            label=hllabel, zorder=2)

    fig.add_hline(y=0, line_color="#000000")
    # ax.axhline(0, ls="--", lw=1, color="#000000", zorder=2)

    if ylabel:
        fig.update_layout(yaxis_title=ylabel)
        # ax.set_ylabel(ylabel, fontname=fontname,
        #               fontweight='bold', fontsize=12, color="black")
        # ax.yaxis.set_label_coords(-.1, .5)

    # ax.yaxis.set_major_formatter(_FormatStrFormatter('%.2f'))

    # ax.legend(fontsize=12)

    # try:
    #     _plt.subplots_adjust(hspace=0, bottom=0, top=1)
    # except Exception:
    #     pass
    #
    # try:
    #     fig.tight_layout()
    # except Exception:
    #     pass
    #
    # if savefig:
    #     if isinstance(savefig, dict):
    #         _plt.savefig(**savefig)
    #     else:
    #         _plt.savefig(savefig)
    if show:
        fig.show()

    # _plt.close()

    if not show:
        return fig

    return None


def plot_rolling_beta(returns, benchmark,
                      window1=126, window1_label="",
                      window2=None, window2_label="",
                      title="", hlcolor="red", figsize=(10, 6),
                      grayscale=False, fontname="Arial", lw=1.5,
                      ylabel=True, subtitle=True, savefig=None, show=True):
    colors, _, _ = _get_colors(grayscale)

    fig, ax = _plt.subplots(figsize=figsize)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_visible(False)
    ax.spines['left'].set_visible(False)

    fig.suptitle(title + "\n", y=.99, fontweight="bold", fontname=fontname,
                 fontsize=14, color="black")

    if subtitle:
        ax.set_title("\n%s - %s                   " % (
            returns.index.date[:1][0].strftime('%e %b \'%y'),
            returns.index.date[-1:][0].strftime('%e %b \'%y')
        ), fontsize=12, color='gray')

    beta = _stats.rolling_greeks(returns, benchmark, window1)['beta']
    ax.plot(beta, lw=lw, label=window1_label, color=colors[1])

    if window2:
        ax.plot(_stats.rolling_greeks(returns, benchmark, window2)['beta'],
                lw=lw, label=window2_label, color="gray", alpha=0.8)
    mmin = min([-100, int(beta.min() * 100)])
    mmax = max([100, int(beta.max() * 100)])
    step = 50 if (mmax - mmin) >= 200 else 100
    ax.set_yticks([x / 100 for x in list(range(mmin, mmax, step))])

    hlcolor = 'black' if grayscale else hlcolor
    ax.axhline(beta.mean(), ls="--", lw=1.5,
               color=hlcolor, zorder=2)

    ax.axhline(0, ls="--", lw=1, color="#000000", zorder=2)

    fig.autofmt_xdate()

    # use a more precise date string for the x axis locations in the toolbar
    ax.fmt_xdata = _mdates.DateFormatter('%Y-%m-%d')

    if ylabel:
        ax.set_ylabel("Beta", fontname=fontname,
                      fontweight='bold', fontsize=12, color="black")
        ax.yaxis.set_label_coords(-.1, .5)

    ax.legend(fontsize=12)
    try:
        _plt.subplots_adjust(hspace=0, bottom=0, top=1)
    except Exception:
        pass

    try:
        fig.tight_layout()
    except Exception:
        pass

    if savefig:
        if isinstance(savefig, dict):
            _plt.savefig(**savefig)
        else:
            _plt.savefig(savefig)

    if show:
        _plt.show(block=False)

    _plt.close()

    if not show:
        return fig

    return None


def plot_longest_drawdowns(returns, periods=5, lw=1.5,
                           fontname='Arial', grayscale=False,
                           log_scale=False, figsize=(10, 6), ylabel=True,
                           subtitle=True, compounded=True,
                           savefig=None, show=True):
    colors = ['#348dc1', '#003366', 'red']
    if grayscale:
        colors = ['#000000'] * 3

    dd = _stats.to_drawdown_series(returns.fillna(0))
    # print(dd)
    dddf = _stats.drawdown_details(dd)
    # print(dddf)
    longest_dd = dddf.sort_values(
        by='days', ascending=False, kind='mergesort')[:periods]

    fig = go.Figure()
    # fig, ax = _plt.subplots(figsize=figsize)
    # ax.spines['top'].set_visible(False)
    # ax.spines['right'].set_visible(False)
    # ax.spines['bottom'].set_visible(False)
    # ax.spines['left'].set_visible(False)
    fig.update_layout(title="Top %.0f Drawdown Periods\n" %
                            periods)
    fig.update_yaxes(tickformat="%")
    # fig.suptitle("Top %.0f Drawdown Periods\n" %
    #              periods, y=.99, fontweight="bold", fontname=fontname,
    #              fontsize=14, color="black")
    if subtitle:
        fig.update_layout(title="Top %.0f Drawdown Periods\n" %
                                periods + "\n%s - %s                   " % (
                                    returns.index.date[:1][0].strftime('%e %b \'%y'),
                                    returns.index.date[-1:][0].strftime('%e %b \'%y')
                                ))
        # ax.set_title("\n%s - %s                   " % (
        #     returns.index.date[:1][0].strftime('%e %b \'%y'),
        #     returns.index.date[-1:][0].strftime('%e %b \'%y')
        # ), fontsize=12, color='gray')

    # fig.set_facecolor('white')
    # ax.set_facecolor('white')
    series = _stats.compsum(returns) if compounded else returns.cumsum()
    # print(series)
    df = pd.DataFrame()
    df['date'] = series.index
    df['value'] = series.tolist()
    fig.add_trace(go.Scatter(x=df['date'], y=df['value']))
    # ax.plot(series, lw=lw, label="Backtest", color=colors[0])

    highlight = 'black' if grayscale else 'red'
    maxy = max(df['value'])
    miny = min(df['value'])
    for _, row in longest_dd.iterrows():
        # ax.axvspan(*_mdates.datestr2num([str(row['start']), str(row['end'])]),
        #            color=highlight, alpha=.1)
        fig.add_shape(type="rect",
                      xref="x", yref="y",
                      x0=row['start'], x1=row['end'], y0=miny, y1=maxy, fillcolor=highlight, opacity=0.1
                      )

    # rotate and align the tick labels so they look better
    # fig.autofmt_xdate()

    # use a more precise date string for the x axis locations in the toolbar
    # ax.fmt_xdata = _mdates.DateFormatter('%Y-%m-%d')

    fig.add_hline(y=0, line_color="#000000")
    # ax.axhline(0, ls="--", lw=1, color="#000000", zorder=2)
    # _plt.yscale("symlog" if log_scale else "linear")
    if ylabel:
        fig.update_layout(yaxis_title="Cumulative Returns")
        # ax.set_ylabel("Cumulative Returns", fontname=fontname,
        #               fontweight='bold', fontsize=12, color="black")
        # ax.yaxis.set_label_coords(-.1, .5)

    # ax.yaxis.set_major_formatter(_FuncFormatter(format_pct_axis))
    # ax.yaxis.set_major_formatter(_plt.FuncFormatter(
    #     lambda x, loc: "{:,}%".format(int(x*100))))

    # fig.autofmt_xdate()
    #
    # try:
    #     _plt.subplots_adjust(hspace=0, bottom=0, top=1)
    # except Exception:
    #     pass
    #
    # try:
    #     fig.tight_layout()
    # except Exception:
    #     pass
    #
    # if savefig:
    #     if isinstance(savefig, dict):
    #         _plt.savefig(**savefig)
    #     else:
    #         _plt.savefig(savefig)
    #
    # if show:
    #     _plt.show(block=False)
    #
    # _plt.close()

    if not show:
        return fig

    return fig


def plot_distribution(returns, figsize=(10, 6),
                      fontname='Arial', grayscale=False, ylabel=True,
                      subtitle=True, compounded=True,
                      savefig=None, show=True):
    colors = _FLATUI_COLORS
    if grayscale:
        colors = ['#f9f9f9', '#dddddd', '#bbbbbb', '#999999', '#808080']
    # colors, ls, alpha = _get_colors(grayscale)

    port = _pd.DataFrame(returns.fillna(0))
    port.columns = ['Daily']

    apply_fnc = _stats.comp if compounded else _np.sum

    port['Weekly'] = port['Daily'].resample(
        'W-MON').apply(apply_fnc).resample('W-MON').last()
    port['Weekly'].ffill(inplace=True)

    port['Monthly'] = port['Daily'].resample(
        'M').apply(apply_fnc).resample('M').last()
    port['Monthly'].ffill(inplace=True)

    port['Quarterly'] = port['Daily'].resample(
        'Q').apply(apply_fnc).resample('Q').last()
    port['Quarterly'].ffill(inplace=True)

    port['Yearly'] = port['Daily'].resample(
        'A').apply(apply_fnc).resample('A').last()
    port['Yearly'].ffill(inplace=True)

    fig = go.Figure()
    # fig, ax = _plt.subplots(figsize=figsize)
    # ax.spines['top'].set_visible(False)
    # ax.spines['right'].set_visible(False)
    # ax.spines['bottom'].set_visible(False)
    # ax.spines['left'].set_visible(False)

    fig.update_layout(title="Return Quantiles\n")
    fig.update_xaxes(tickformat="%")
    # fig.suptitle("Return Quantiles\n", y=.99,
    #              fontweight="bold", fontname=fontname,
    #              fontsize=14, color="black")

    if subtitle:
        fig.update_layout(title="Return Quantiles\n" + "\n%s - %s                   " % (
            returns.index.date[:1][0].strftime('%e %b \'%y'),
            returns.index.date[-1:][0].strftime('%e %b \'%y')
        ))
        # ax.set_title("\n%s - %s                   " % (
        #     returns.index.date[:1][0].strftime('%e %b \'%y'),
        #     returns.index.date[-1:][0].strftime('%e %b \'%y')
        # ), fontsize=12, color='gray')

    # fig.set_facecolor('white')
    # ax.set_facecolor('white')
    # print(port)
    fig.add_trace(go.Box(y=port['Daily'], name="Daily"))
    fig.add_trace(go.Box(y=port['Weekly'], name="Weekly"))
    fig.add_trace(go.Box(y=port['Monthly'], name="Monthly"))
    fig.add_trace(go.Box(y=port['Quarterly'], name="Quarterly"))
    fig.add_trace(go.Box(y=port['Yearly'], name="Yearly"))
    fig.update_yaxes(tickformat="%")
    # _sns.boxplot(data=port, ax=ax, palette=tuple(colors[:5]))

    # ax.yaxis.set_major_formatter(_plt.FuncFormatter(
    #     lambda x, loc: "{:,}%".format(int(x * 100))))

    if ylabel:
        fig.update_layout(yaxis_title="Reruns")
        # ax.set_ylabel('Rerurns', fontname=fontname,
        #               fontweight='bold', fontsize=12, color="black")
        # ax.yaxis.set_label_coords(-.1, .5)

    # fig.autofmt_xdate()
    #
    # try:
    #     _plt.subplots_adjust(hspace=0)
    # except Exception:
    #     pass
    # try:
    #     fig.tight_layout(w_pad=0, h_pad=0)
    # except Exception:
    #     pass
    #
    # if savefig:
    #     if isinstance(savefig, dict):
    #         _plt.savefig(**savefig)
    #     else:
    #         _plt.savefig(savefig)
    #
    # if show:
    #     _plt.show(block=False)
    #
    # _plt.close()

    if not show:
        return fig

    return fig


def plot_table(tbl, columns=None, title="", title_loc="left",
               header=True,
               colWidths=None,
               rowLoc='right',
               colLoc='right',
               colLabels=None,
               edges='horizontal',
               orient='horizontal',
               figsize=(5.5, 6),
               savefig=None,
               show=False):
    if columns is not None:
        try:
            tbl.columns = columns
        except Exception:
            pass

    fig = _plt.figure(figsize=figsize)
    ax = _plt.subplot(111, frame_on=False)

    if title != "":
        ax.set_title(title, fontweight="bold",
                     fontsize=14, color="black", loc=title_loc)

    the_table = ax.table(cellText=tbl.values,
                         colWidths=colWidths,
                         rowLoc=rowLoc,
                         colLoc=colLoc,
                         edges=edges,
                         colLabels=(tbl.columns if header else colLabels),
                         loc='center',
                         zorder=2
                         )

    the_table.auto_set_font_size(False)
    the_table.set_fontsize(12)
    the_table.scale(1, 1)

    for (row, col), cell in the_table.get_celld().items():
        cell.set_height(0.08)
        cell.set_text_props(color='black')
        cell.set_edgecolor('#dddddd')
        if row == 0 and header:
            cell.set_edgecolor('black')
            cell.set_facecolor('black')
            cell.set_linewidth(2)
            cell.set_text_props(weight='bold', color='black')
        elif col == 0 and "vertical" in orient:
            cell.set_edgecolor('#dddddd')
            cell.set_linewidth(1)
            cell.set_text_props(weight='bold', color='black')
        elif row > 1:
            cell.set_linewidth(1)

    ax.grid(False)
    ax.set_xticks([])
    ax.set_yticks([])

    try:
        _plt.subplots_adjust(hspace=0)
    except Exception:
        pass
    try:
        fig.tight_layout(w_pad=0, h_pad=0)
    except Exception:
        pass

    if savefig:
        if isinstance(savefig, dict):
            _plt.savefig(**savefig)
        else:
            _plt.savefig(savefig)

    if show:
        _plt.show(block=False)

    _plt.close()

    if not show:
        return fig

    return None


def format_cur_axis(x, _):
    if x >= 1e12:
        res = '$%1.1fT' % (x * 1e-12)
        return res.replace('.0T', 'T')
    if x >= 1e9:
        res = '$%1.1fB' % (x * 1e-9)
        return res.replace('.0B', 'B')
    if x >= 1e6:
        res = '$%1.1fM' % (x * 1e-6)
        return res.replace('.0M', 'M')
    if x >= 1e3:
        res = '$%1.0fK' % (x * 1e-3)
        return res.replace('.0K', 'K')
    res = '$%1.0f' % x
    return res.replace('.0', '')


def format_pct_axis(x, _):
    x *= 100  # lambda x, loc: "{:,}%".format(int(x * 100))
    if x >= 1e12:
        res = '%1.1fT%%' % (x * 1e-12)
        return res.replace('.0T%', 'T%')
    if x >= 1e9:
        res = '%1.1fB%%' % (x * 1e-9)
        return res.replace('.0B%', 'B%')
    if x >= 1e6:
        res = '%1.1fM%%' % (x * 1e-6)
        return res.replace('.0M%', 'M%')
    if x >= 1e3:
        res = '%1.1fK%%' % (x * 1e-3)
        return res.replace('.0K%', 'K%')
    res = '%1.0f%%' % x
    return res.replace('.0%', '%')
