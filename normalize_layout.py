#!/bin/env python3

import sys
from dataclasses import dataclass, field
from math import gcd, lcm

def isdigit(c):
    return '0' <= c <= '9'

def ishex(c):
    return '0' <= c <= '9' or 'a' <= c <= 'f'

def ifloor(p, q):
    return p // q

def iceil(p, q):
    return (p + q - 1) // q

def fit_m(a, m):
    n = len(a)
    assert n <= m
    s0 = sum(a)
    f = [[(1e10, 0) for j in range(m + 1)] for i in range(n + 1)]
    f[0][0] = (0, 0)
    s = 0
    for i in range(1, n + 1):
        s += a[i - 1]
        for j in range(i, m + 1):
            for k in range(i - 1, j):
                f[i][j] = min(f[i][j], (f[i - 1][k][0] + (s / s0 - j / m) ** 2, k))
    cost, j = f[n][m][0], m
    b = []
    for i in range(n, 0, -1):
        b.append(j - f[i][j][1])
        j = f[i][j][1]
    b = tuple(reversed(b))
    return cost, b

# 计算最接近给定划分的较小划分
# 例：[12, 18, 30] => [1, 2, 3], [13, 17, 30] => [1, 1, 2]
def fit(splits):
    low = len(splits)
    high = max(low, min(sum(splits), 6)) + 1
    sols = ((m, fit_m(splits, m)) for m in range(low, high))
    b = min((cost + m ** 0.5 / 400, m, b) for m, (cost, b) in sols)[2]
    assert gcd(*b) == 1
    return b

# 将 vals[i] 分别增大正整数倍，使其比例符合 ratios
def scale_to_ratios(vals, ratios):
    if ratios is None: return vals
    m = lcm(*vals)
    es = [ratio * m // val for ratio, val in zip(ratios, vals)]
    d = gcd(*es)
    return [e // d * val for e, val in zip(es, vals)]

@dataclass
class Pane:
    width: int
    height: int
    id: int = -1
    horizontal: bool = True
    subs: list = field(default_factory=list)

    # 为了正确处理 lcm，在窗格的变换过程中宽高包含了周围半个分割线，等到 format 时再减去。
    def _adjust(self, f):
        if self.id != -1:
            self.width, self.height = 2, 2
            return

        splits = [sub.width if self.horizontal else sub.height for sub in self.subs]
        ratios = f(splits)
        for sub in self.subs:
            sub._adjust(f)
        widths = [sub.width for sub in self.subs]
        heights = [sub.height for sub in self.subs]
        if self.horizontal:
            widths = scale_to_ratios(widths, ratios)
            for sub, width in zip(self.subs, widths):
                sub.width = width
            self.width = sum(widths)
            self.height = lcm(*list(heights))
        else:
            heights = scale_to_ratios(heights, ratios)
            for sub, height in zip(self.subs, heights):
                sub.height = height
            self.width = lcm(*list(widths))
            self.height = sum(heights)

    ADJUST_STRATEGIES = {
        'equal': lambda a: [1] * len(a),
        'grid': lambda a: None,
        'fit': fit,
    }
    def adjust(self, strategy: str='equal'):
        self._adjust(Pane.ADJUST_STRATEGIES[strategy])

    # 缩放 pane 使其适应上一层的宽高
    def _scale(self, width, height, round_=ifloor):
        if self.horizontal:
            left, s = 0, 0
            for sub in self.subs:
                s += sub.width
                right = round_(s * width, self.width)
                sub._scale(right - left, height)
                left = right
        else:
            top, s = 0, 0
            for sub in self.subs:
                s += sub.height
                bottom = round_(s * height, self.height)
                sub._scale(width, bottom - top)
                top = bottom
        self.width, self.height = width, height

    def scale(self):
        self._scale(self.width, self.height)

    # pane-border-status 对 layout 没有任何影响。layout 只与非边界的分割线有关。
    def _format(self, left, top, border):
        width = self.width - 1
        height = self.height
        if not (border == 'top' and top == 0): height -= 1
        pre = f'{self.width - 1}x{height},{left},{top}'

        subs = []
        for sub in self.subs:
            s, w, h = sub._format(left, top, border)
            subs.append(s)
            if self.horizontal:
                left += w + 1
            else:
                top += h + 1
        s = ','.join(subs)
        suf = f',{self.id}' if self.id != -1 else f'{{{s}}}' if self.horizontal else f'[{s}]'
        return pre + suf, width, height

    def format(self, width=0, height=0, border='off'):
        self._scale(width or self.width, height or self.height)
        return self._format(0, 0, border)[0]

def parse_layout(s, border):
    def nex(c):
        nonlocal i
        if s[i] == c:
            i += 1
            return True
        else:
            return False

    def eat(c):
        assert nex(c)

    def number():
        nonlocal i
        l = i
        while i < len(s) and isdigit(s[i]): i += 1
        assert l < i, i
        return int(s[l: i])

    def parse():
        width = number()
        eat('x')
        height = number()
        eat(',')
        number() # left
        eat(',')
        top = number() # top
        width += 1
        if not (border == 'top' and top == 0): height += 1
        pane = Pane(width, height)
        if nex(','):
            pane.id = number()
        elif nex('{'):
            pane.horizontal = True
            while True:
                pane.subs.append(parse())
                if not nex(','): break
            eat('}')
        elif nex('['):
            pane.horizontal = False
            while not nex(']'):
                pane.subs.append(parse())
                if not nex(','): break
            eat(']')
        else:
            assert False, f'Unexpected character {s[i]} at {i}'
        return pane

    assert all(ishex(s[i]) for i in range(4))
    i = 4
    eat(',')
    return parse()

def calc_checksum(s):
    csum = 0
    for c in s:
        csum = (csum >> 1) + ((csum & 1) << 15) + ord(c) & 0xffff
    return csum

def main(layout, adjust, border):
    assert border in ['off', 'top'], 'Unexpected border'
    assert adjust in Pane.ADJUST_STRATEGIES, 'Unexpected strategy'

    pane = parse_layout(layout, border)
    width, height = pane.width, pane.height

    pane.adjust(adjust)
    layout = pane.format(width, height, border)
    csum = calc_checksum(layout)
    full_layout = f'{csum:04x},{layout}'
    print(full_layout)

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('layout', type=str)
    parser.add_argument('--adjust', type=str, default='equal')
    parser.add_argument('--border', type=str, default='off')

    args = parser.parse_args()
    args = vars(args)
    main(**args)
