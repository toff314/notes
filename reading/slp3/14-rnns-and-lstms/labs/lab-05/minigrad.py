"""极简自动微分（numpy 实现），供 lab-05 使用。

只实现实验需要的算子：matmul / add / mul / div / exp / tanh / sigmoid / softmax 交叉熵。
"""
import numpy as np


class T:
    __slots__ = ("data", "grad", "_p", "_b")

    def __init__(self, data, _p=(), _b=None):
        self.data = np.asarray(data, dtype=np.float64)
        self.grad = np.zeros_like(self.data)
        self._p = _p
        self._b = _b if _b is not None else (lambda: None)


def _unbroadcast(g, shape):
    while g.ndim > len(shape):
        g = g.sum(axis=0)
    for i, s in enumerate(shape):
        if s == 1 and g.shape[i] != 1:
            g = g.sum(axis=i, keepdims=True)
    return g


def matmul(a, b):
    a = a if isinstance(a, T) else T(a)
    b = b if isinstance(b, T) else T(b)
    A, B = a.data, b.data
    out = T(A @ B, (a, b))

    def bwd():
        g = out.grad
        if A.ndim == 2 and B.ndim == 1:
            a.grad += np.outer(g, B)
            b.grad += A.T @ g
        elif A.ndim == 1 and B.ndim == 2:
            a.grad += B @ g
            b.grad += np.outer(A, g)
        else:
            a.grad += g @ B.T
            b.grad += A.T @ g
    out._b = bwd
    return out


def add(a, b):
    a = a if isinstance(a, T) else T(a)
    b = b if isinstance(b, T) else T(b)
    out = T(a.data + b.data, (a, b))

    def bwd():
        a.grad += _unbroadcast(out.grad, a.data.shape)
        b.grad += _unbroadcast(out.grad, b.data.shape)
    out._b = bwd
    return out


def mul(a, b):
    a = a if isinstance(a, T) else T(a)
    b = b if isinstance(b, T) else T(b)
    out = T(a.data * b.data, (a, b))

    def bwd():
        a.grad += _unbroadcast(out.grad * b.data, a.data.shape)
        b.grad += _unbroadcast(out.grad * a.data, b.data.shape)
    out._b = bwd
    return out


def div(a, b):
    a = a if isinstance(a, T) else T(a)
    b = b if isinstance(b, T) else T(b)
    out = T(a.data / b.data, (a, b))

    def bwd():
        a.grad += _unbroadcast(out.grad / b.data, a.data.shape)
        b.grad += _unbroadcast(-out.grad * a.data / (b.data ** 2), b.data.shape)
    out._b = bwd
    return out


def exp(a):
    out = T(np.exp(a.data), (a,))

    def bwd():
        a.grad += out.grad * out.data
    out._b = bwd
    return out


def tanh(a):
    out = T(np.tanh(a.data), (a,))

    def bwd():
        a.grad += out.grad * (1.0 - out.data ** 2)
    out._b = bwd
    return out


def sigmoid(a):
    out = T(1.0 / (1.0 + np.exp(-a.data)), (a,))

    def bwd():
        a.grad += out.grad * out.data * (1.0 - out.data)
    out._b = bwd
    return out


def softmax_ce(logits, y):
    z = logits.data - logits.data.max()
    p = np.exp(z) / np.exp(z).sum()
    out = T(-np.log(max(p[y], 1e-12)), (logits,))

    def bwd():
        d = p.copy()
        d[y] -= 1.0
        logits.grad += d
    out._b = bwd
    return out


def backward(out):
    topo, seen = [], set()

    def visit(n):
        if id(n) in seen:
            return
        seen.add(id(n))
        for p in n._p:
            visit(p)
        topo.append(n)

    visit(out)
    out.grad = np.ones_like(out.data)
    for n in reversed(topo):
        n._b()


class Adam:
    def __init__(self, params, lr=0.01):
        self.p, self.lr, self.t = params, lr, 0
        self.m = {k: np.zeros_like(v.data) for k, v in params.items()}
        self.v = {k: np.zeros_like(v.data) for k, v in params.items()}

    def step(self, clip=5.0):
        self.t += 1
        for k, p in self.p.items():
            g = np.clip(p.grad, -clip, clip)
            self.m[k] = 0.9 * self.m[k] + 0.1 * g
            self.v[k] = 0.999 * self.v[k] + 0.001 * g * g
            mh = self.m[k] / (1 - 0.9 ** self.t)
            vh = self.v[k] / (1 - 0.999 ** self.t)
            p.data -= self.lr * mh / (np.sqrt(vh) + 1e-8)
            p.grad = np.zeros_like(p.data)
