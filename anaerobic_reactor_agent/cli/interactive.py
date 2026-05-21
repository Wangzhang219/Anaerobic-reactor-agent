"""Interactive CLI mode for guided parameter input."""

import click
from rich.console import Console
from rich.panel import Panel
from rich.prompt import FloatPrompt, Confirm

from ..engine.rule_engine import RuleEngine
from ..models.reactor_state import ReactorParameters
from ..utils.validators import validate_reactor_params
from ..config.settings import SUPPORTED_REACTOR_TYPES
from .output import format_result

console = Console()

PARAMETERS = [
    ("ph", "pH", 0, 14),
    ("temperature", "Temperature (°C)", 0, 100),
    ("cod_inlet", "COD Inlet (mg/L)", 0, 200000),
    ("cod_outlet", "COD Outlet (mg/L)", 0, 200000),
    ("vfa", "VFA (mg/L as acetic acid)", 0, 10000),
    ("alkalinity", "Alkalinity (mg CaCO3/L)", 0, 10000),
    ("orp", "ORP (mV)", -1000, 1000),
    ("biogas_production", "Biogas Production (m3/d)", 0, 100000),
    ("methane_content", "Methane Content (%)", 0, 100),
    ("olr", "Organic Loading Rate (kg COD/m3·d)", 0, 100),
    ("hrt", "Hydraulic Retention Time (hours)", 0, 200),
]

OPTIONAL_PARAMETERS = [
    ("nh3_n", "Ammonia Nitrogen (mg/L) [optional, Enter to skip]", 0, 5000),
]


def run_interactive():
    """Run the interactive guided diagnosis session."""
    console.print()
    console.print(Panel.fit(
        "[bold blue]Anaerobic Reactor Intelligent Agent[/bold blue]\n"
        "Interactive Diagnosis Mode",
        border_style="blue",
    ))

    # Reactor type
    rt_options = "/".join(SUPPORTED_REACTOR_TYPES)
    reactor_type = click.prompt(
        f"Reactor type [{rt_options}]",
        type=click.Choice(SUPPORTED_REACTOR_TYPES, case_sensitive=False),
        default="UASB",
    )

    while True:
        console.print("\n[bold]Enter reactor parameters:[/bold]")

        values = {}

        for key, label, lo, hi in PARAMETERS:
            default_info = get_default_range(key)
            prompt_text = f"{label} {default_info}"
            values[key] = FloatPrompt.ask(prompt_text)

        for key, label, lo, hi in OPTIONAL_PARAMETERS:
            raw = click.prompt(f"{label}", default="", show_default=False)
            if raw.strip():
                try:
                    values[key] = float(raw)
                except ValueError:
                    console.print(f"[yellow]Invalid value, skipping {key}[/yellow]")

        params = ReactorParameters(
            ph=values["ph"],
            temperature=values["temperature"],
            cod_inlet=values["cod_inlet"],
            cod_outlet=values["cod_outlet"],
            vfa=values["vfa"],
            alkalinity=values["alkalinity"],
            orp=values["orp"],
            biogas_production=values["biogas_production"],
            methane_content=values["methane_content"],
            olr=values["olr"],
            hrt=values["hrt"],
            nh3_n=values.get("nh3_n"),
            reactor_type=reactor_type,
        )

        warnings = validate_reactor_params(params)
        if warnings:
            console.print()
            for w in warnings:
                console.print(f"[yellow]Warning:[/yellow] {w}")

        console.print()
        if not Confirm.ask("Run diagnosis?"):
            continue

        engine = RuleEngine()
        result = engine.diagnose(params)
        format_result(result)

        console.print()
        if not Confirm.ask("Run another diagnosis?"):
            break


def get_default_range(param_key: str) -> str:
    """Provide a hint about typical values."""
    hints = {
        "ph": "[dim](6.8–7.5)[/dim]",
        "temperature": "[dim](mesophilic: 35°C)[/dim]",
        "cod_inlet": "[dim](e.g. 5000)[/dim]",
        "cod_outlet": "[dim](e.g. 500)[/dim]",
        "vfa": "[dim](<300)[/dim]",
        "alkalinity": "[dim](e.g. 2000)[/dim]",
        "orp": "[dim](-300 to -500)[/dim]",
        "biogas_production": "[dim](e.g. 50)[/dim]",
        "methane_content": "[dim](55–70%)[/dim]",
        "olr": "[dim](UASB: 2–10)[/dim]",
        "hrt": "[dim](6–48h)[/dim]",
    }
    return hints.get(param_key, "")
