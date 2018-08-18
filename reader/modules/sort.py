from re import split


def atoi(s):
    try:
        return int(s)
    except:
        return s


def alnum_key(k): return [atoi(c) for c in split('([0-9]+)', k)]


def natural_sort(l): l.sort(key=alnum_key)


__all__ = ['alnum_key', 'natural_sort']

# Source: https://blog.codinghorror.com/sorting-for-humans-natural-sort-order/

