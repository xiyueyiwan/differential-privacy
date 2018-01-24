#!/usr/bin/env python3

import matplotlib.pyplot as plt
import numpy as np
from accuracy import total_optimal
from collections import defaultdict


def threshold(c, queries):
    return (queries[c-1] + queries[c])/2


def epsilon(e, c, monotonic=True):
    f = factor(monotonic)
    e1 = e/(1+(f*c)**(2/3))
    e2 = e - e1
    return e1, e2


def error_rate_cdf(k, e1, e2, queries, T, c, step=1):
    return zip(*uniq_xs(error_rate(a, k, e1, e2, queries, T, c)
                        for a in np.arange(T+1)[::step]))


def error_rate(a, k, e1, e2, queries, T, c):
    beta = total_optimal(a, k, e1, e2)
    worst_scores = np.sum(queries[queries >= (T - a)][-c:])
    top_scores = np.sum(queries[:c])
    return 1 - worst_scores/top_scores, 1 - beta


def discrete_pdf(ys):
    return [ys[0]] + [ys[i] - ys[i-1] for i in range(1, len(ys))]


def uniq_xs(pairs_gen):
    pairs_list = []
    dups = defaultdict(list)
    for i, (x, y) in enumerate(pairs_gen):
        dups[x].append(i)
        pairs_list.append((x, y))
    indices = [x for v in dups.values() for x in v[:-1] if len(v) > 1]
    return ((x, y) for i, (x, y) in enumerate(pairs_list) if i not in indices)


def factor(monotonic):
    return 1 if monotonic else 2


if __name__ == '__main__':
    queries = np.loadtxt('data/kosarak_clean.json', dtype=int)
    step = 1
    sensitivity = 1
    monotonic = True
    f = factor(monotonic)
    c = 50
    T = threshold(c, queries)
    k = len(queries)

    e = 0.1
    e1, e2 = epsilon(e, c, monotonic)
    e1 = e1 / sensitivity
    e2 = e2 / (sensitivity * f * c)

    fig, ax = plt.subplots()
    xs, ys = error_rate_cdf(k, e1, e2, queries, T, c, step=step)
    ax.bar(xs, ys, color="red", align='edge',
           label=r"$\mathrm{Pr}(\mathrm{SER} \leq x) \geq 1 - \beta$")

    ax.bar(xs, discrete_pdf(ys), width=1/100, color="blue", align='edge',
           label=r"$\mathrm{Pr}(\mathrm{SER} = x) \approx 1 - \beta$")

    plt.xlim(0,1)
    plt.ylim(0,1)
    plt.xlabel(r"$x$")
    plt.ylabel(r"$1 - \beta$")
    ax.legend(loc='upper left')
    plt.title(r"SER distribution on Kosarak, $k = {}, c = {}, \epsilon = {}$".format(k, c, e))
    plt.show()
