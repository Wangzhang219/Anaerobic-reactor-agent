"""Input validation utilities."""

from typing import List
from ..models.reactor_state import ReactorParameters


def validate_reactor_params(params: ReactorParameters) -> List[str]:
    """Validate reactor parameters and return list of warnings.

    These are soft warnings — the diagnosis will still run.
    """
    warnings = []

    if params.ph < 5.0 or params.ph > 9.0:
        warnings.append(f"pH is {params.ph}, extremely outside biological range (5.0-9.0)")

    if params.temperature < 10 or params.temperature > 65:
        warnings.append(
            f"Temperature {params.temperature}°C is outside methanogenic range (10-65°C)"
        )

    if params.cod_outlet > params.cod_inlet:
        warnings.append(
            f"COD outlet ({params.cod_outlet}) > COD inlet ({params.cod_inlet}), "
            "removal rate is negative — check measurements"
        )

    if params.methane_content > 80:
        warnings.append(f"Methane content {params.methane_content}% unusually high, verify measurement")

    if params.olr > 50:
        warnings.append(f"OLR {params.olr} kg COD/m3.d is extremely high for most reactor types")

    if params.hrt < 2:
        warnings.append(f"HRT {params.hrt}h is very short, risk of biomass washout")

    return warnings
