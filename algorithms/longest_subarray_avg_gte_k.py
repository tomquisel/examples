#!/usr/bin/env python
import sys
import os
import re
import random
import time, datetime
from collections import defaultdict
import pandas as pd
import numpy as np
from argparse import ArgumentParser


def main():
    args = handle_args()
    start, length = find_longest_subarray_avg_gte_k(
        args.array, args.k, args.verbose
    )
    start2, length2 = brute_force(args.array, args.k, args.verbose)
    assert start == start2 and length == length2,\
        'fast alg did not match brute force alg! {} {} != {} {}'\
            .format(start, length, start2, length2)
    print 'Start: {} Length: {}'.format(start, length)


def handle_args():
    description = 'Find longest subarray with avg >= k'
    parser = ArgumentParser(description=description)
    parser.add_argument(
        'array', type=int, nargs='+', help='array of numbers to search'
    )
    parser.add_argument(
        '-k', dest='k', type=int,
        help='the average of the subarray should be >= k'
    )
    parser.add_argument('--verbose', action='store_true')
    return parser.parse_args()


def find_longest_subarray_avg_gte_k(a, k, verbose=False):
    df = pd.DataFrame([k] + a, columns=['values'])
    # transform into sum >= 0 problem
    df['values'] -= k
    # find sum up to each index (sum of subarray is now cumsum[j] - cumsum[i])
    df['cumsum'] = df.values.cumsum()
    # record the index for each value/cumsum pair
    df['index'] = df.index
    # reverse sort by cumsum, index so that any earlier spot in the list is a
    # valid subarray ending location for a later subarray start location
    df.sort_values(['cumsum', 'index'], ascending=False, inplace=True)
    # compute the cummax() to identify the latest ending location for each
    # starting location that is valid
    df['maxend'] = df['index'].cummax()
    df['subarraylen'] = df['maxend'] - df['index']
    # find the longest subarray
    best_subarray_ind = df.subarraylen.argmax()

    if verbose:
        print 'Optimized algorithm:'
        print df

    return (df.loc[best_subarray_ind, 'index'],
            df.loc[best_subarray_ind, 'subarraylen'])


def brute_force(a, k, verbose=False):
    if verbose:
        print 'Brute force algorithm:'
    best_len, best_mean, best_i, best_j = None, None, None, None
    a = np.array(a)
    for i in range(len(a)):
        for j in range(i+1, len(a)+1):
            mean_val = a[i:j].mean()
            length = j - i
            if mean_val >= k and (best_len is None or length > best_len):
                print 'found new best {} {} {}'.format(length, i, j)
                best_len, best_i, best_j = length, i, j
    return best_i, best_len


if __name__ == '__main__':
    main()
