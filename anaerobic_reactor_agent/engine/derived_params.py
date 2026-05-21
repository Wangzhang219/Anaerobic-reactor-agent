"""Computation of derived/secondary parameters from raw reactor data."""

from ..models.reactor_state import ReactorParameters
from ..utils.helpers import safe_divide


def compute_derived_params(params: ReactorParameters) -> dict:
    """Compute derived parameters from raw reactor measurements.

    Returns a flat dict that merges raw and derived values for rule evaluation.
    """
    raw = params.model_dump()
    derived = {}

    if params.cod_inlet > 0:
        derived["cod_removal_rate"] = round(
            (params.cod_inlet - params.cod_outlet) / params.cod_inlet * 100, 1
        )

    if params.alkalinity > 0:
        derived["vfa_alkalinity_ratio"] = round(params.vfa / params.alkalinity, 3)

    return {**raw, **derived}
