from nontest import jit

from functools import partial
from jax import Array, nn as jnn, numpy as jnp, random as jrnd
from jax.numpy import linalg as jla
from typing import Callable


@partial(jit, static_argnames=["nl"])
def feedforward(
    W: list[Array],
    B: list[Array],
    x: Array,
    nl: Callable[Array, Array] = jnn.gelu,
) -> Array:
    n = len(W)
    assert n == len(B)
    for i in range(n):
        x = nl((W[i] @ x) + B[i])
    return x


# shouldn't be JITted b/c only run once
def feedforward_init(
    sizes: list[int],
    key: jrnd.PRNGKey,
) -> tuple[list[Array], list[Array]]:
    n = len(sizes)
    W = []
    B = []
    init = jnn.initializers.he_normal()
    for i in range(1, n):
        key, k = jrnd.split(key)
        W.append(init(k, (sizes[i], sizes[i - 1]), jnp.float32))
        B.append(jnp.zeros(sizes[i]))
    return W, B


@jit
def rotate_weights(
    W: list[Array],
    B: list[Array],
    R: list[Array],
) -> tuple[list[Array], list[Array]]:
    assert isinstance(W, list)
    assert isinstance(B, list)
    assert isinstance(R, list)
    n = len(R)
    assert n + 1 == len(W) == len(B)
    # Note that "permutations" should occur only vertically,
    # since, in `Wx + B`, horizontal indices of `W`
    # track indices of the column-vector `x`.
    # So we're looking for `RW` instead of `WR`.
    for i in range(n):
        W[i] = R[i] @ W[i]
        B[i] = R[i] @ B[i]
        RT = R[i].T
        Rinv = jla.inv(R[i])
        inv_diff = jnp.abs(RT - Rinv)
        assert jnp.all(inv_diff < 0.01)
        W[-1] = R[i].T @ W[-1]
        # B[-1] = R[i].T @ B[-1]
    return W, B


# TODO: Try using ML to find rotation matrices s.t.
# each rotation matrix minimizes distance to the true weights
# but all matrices, taken together, produce an identity matrix
# (so the output indices really mean what they should,
# instead of a permutation thereof).
# Right now, we're just unilaterally reverse-rotating the last `W`,
# which is probably far from ideal but much faster.
