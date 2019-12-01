# Source: https://blog.codinghorror.com/sorting-for-humans-natural-sort-order/

from re import split


def atoi(s):
    return int(s) if s.isdigit() else s


def alnum_key(k):
    return list(map(atoi, split('([0-9]+)', k)))


def natural_sort(l):
    return sorted(l, key=alnum_key)


__all__ = ['alnum_key', 'natural_sort']
