#!/usr/bin/env python3

import asyncio
import numpy as np
import pgen


def gen_sin(t):
    return np.sin(t * np.pi / 8) / 2 + 0.5


def gen_noise(t):
    return np.random.normal(0, 0.1, t.shape)


def gen_point(x):
    y_sin = gen_sin(x)
    y_noise = gen_noise(x)
    return y_sin + y_noise


def main():
    # import matplotlib.pyplot as plt
    # xs = np.arange(64)
    # ys = gen_point(xs)
    # plt.figure(figsize=(8, 4))
    # plt.plot(xs, ys, '.-')
    # plt.savefig('pattern.pdf')
    # plt.clf()

    print(pgen.ASCII_ART)
    gen = pgen.PGen(gen_point,
                    seconds_per_point=5,
                    max_requests_per_second=100,
                    url='https://abcdabcd987.com/',
                    timeout_seconds=30)
    asyncio.run(gen.run())


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('exit')
