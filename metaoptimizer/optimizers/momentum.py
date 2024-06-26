from metaoptimizer.optimizers import inverse_sigmoid

from beartype import beartype
from beartype.typing import NamedTuple, Tuple
from check_and_compile import check_and_compile
from jax import nn as jnn, numpy as jnp
from jax.tree_util import tree_map
from jaxtyping import jaxtyped, Array, Float, PyTree
import operator


@jaxtyped(typechecker=beartype)
class Params(NamedTuple):
    log_lr: Float[Array, ""]
    inv_sig_momentum: Float[Array, ""]


@jaxtyped(typechecker=beartype)
class State(NamedTuple):
    last_update: PyTree[Float[Array, "..."]]


@jaxtyped(typechecker=beartype)
def defaults(
    lr: Float[Array, ""] = jnp.array(0.01),
    momentum: Float[Array, ""] = jnp.array(0.9),
) -> Params:
    return Params(log_lr=jnp.log(lr), inv_sig_momentum=inverse_sigmoid(momentum))


@jaxtyped(typechecker=beartype)
def init(initial_weights: PyTree[Float[Array, "..."]], p: Params) -> State:
    return State(last_update=tree_map(jnp.zeros_like, initial_weights))


# @check_and_compile()
@jaxtyped(typechecker=beartype)
def update(
    p: Params,
    s: State,
    w: PyTree[Float[Array, "..."]],
    dLdw: PyTree[Float[Array, "..."]],
) -> Tuple[State, PyTree[Float[Array, "..."]]]:
    lr = jnp.exp(p.log_lr)
    momentum = jnn.sigmoid(p.inv_sig_momentum)
    update = tree_map(lambda di, lu: lr * di + momentum * lu, dLdw, s.last_update)
    updated = tree_map(operator.sub, w, update)
    return State(last_update=update), updated
