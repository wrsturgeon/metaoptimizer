from beartype import beartype
from beartype.typing import Callable, Tuple
from check_and_compile import check_and_compile
from jax import numpy as jnp
from jax.experimental.checkify import check
from jaxtyping import jaxtyped, Array, Float, PyTree


# TODO: Why don't named annotations like "P" & "S" work here?
Optimizer = Callable[
    [
        PyTree[Float[Array, ""]],
        PyTree[Float[Array, "..."]],
        PyTree[Float[Array, "..."]],
        PyTree[Float[Array, "..."]],
    ],
    Tuple[PyTree[Float[Array, "..."]], PyTree[Float[Array, "..."]]],
]


# @check_and_compile()
@jaxtyped(typechecker=beartype)
def inverse_sigmoid(x: Float[Array, "*n"]) -> Float[Array, "*n"]:
    # https://stackoverflow.com/questions/10097891/inverse-logistic-sigmoid-function
    check(
        jnp.logical_and(jnp.all(0 < x), jnp.all(x < 1)),
        "{x} must be between 0 and 1",
        x=x,
    )
    return jnp.log(x) - jnp.log(1 - x)
