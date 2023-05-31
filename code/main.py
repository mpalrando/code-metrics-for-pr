#!/usr/bin/env python3

import os


def factorial(n):
    print('factorial({})'.format(n))
    if n == 0:
        return 1
    else:
        return n * factorial(n-1)


if __name__ == '__main__':
    print('Hello World!')
    os.exit(0)
