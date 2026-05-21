"""Click CLI application for the anaerobic reactor agent."""

import sys
from typing import Optional

import click

from ..engine.rule_engine import RuleEngine
from ..engine.rule_loader import RuleLoader
from ..models.reactor_state import ReactorParameters
from ..models.diagnosis import DiagnosisResult
from ..utils.validators import validate_reactor_params
from ..config.settings import SUPPORTED_REACTOR_TYPES
from ..config.logging_config import setup_logging

logger = setup_logging()


@click.group()
@click.version_option(version="0.1.0", prog_name="anaerobic-agent")
def cli():
    """Anaerobic Reactor Intelligent Agent — monitor, diagnose, and get recommendations."""


@cli.command()
@click.option("--ph", type=float, required=True, help="pH value (0-14)")
@click.option("--temperature", type=float, required=True, help="Temperature in Celsius")
@click.option("--cod-inlet", type=float, required=True, help="COD at inlet (mg/L)")
@click.option("--cod-outlet", type=float, required=True, help="COD at outlet (mg/L)")
@click.option("--vfa", type=float, required=True, help="Volatile Fatty Acids (mg/L)")
@click.option("--alkalinity", type=float, required=True, help="Alkalinity (mg CaCO3/L)")
@click.option("--orp", type=float, required=True, help="ORP (mV)")
@click.option("--biogas", type=float, required=True, help="Biogas production rate (m3/d)")
@click.option("--methane", type=float, required=True, help="Methane content (%)")
@click.option("--olr", type=float, required=True, help="Organic Loading Rate (kg COD/m3.d)")
@click.option("--hrt", type=float, required=True, help="Hydraulic Retention Time (hours)")
@click.option("--nh3-n", type=float, default=None, help="Ammonia nitrogen (mg/L)")
@click.option("--reactor-type", type=str, default="UASB", help="Reactor type")
@click.option("--llm/--no-llm", default=False, help="Enable LLM analysis")
@click.option("--output", "output_format", type=click.Choice(["text", "json"]), default="text")
@click.option("--output-file", type=click.Path(), default=None, help="Save JSON output to file")
@click.option("--reactor-id", type=str, default=None, help="Reactor identifier")
def check(
    ph, temperature, cod_inlet, cod_outlet, vfa, alkalinity, orp,
    biogas, methane, olr, hrt, nh3_n, reactor_type, llm, output_format,
    output_file, reactor_id,
):
    """Run a single-shot diagnosis from command-line parameters."""
    from .output import format_result

    params = ReactorParameters(
        ph=ph, temperature=temperature, cod_inlet=cod_inlet, cod_outlet=cod_outlet,
        vfa=vfa, alkalinity=alkalinity, orp=orp, biogas_production=biogas,
        methane_content=methane, olr=olr, hrt=hrt,
        nh3_n=nh3_n, reactor_type=reactor_type,
    )

    warnings = validate_reactor_params(params)
    if warnings:
        for w in warnings:
            click.echo(click.style(f"Warning: {w}", fg="yellow"), err=True)

    engine = RuleEngine()
    result = engine.diagnose(params)
    result.reactor_id = reactor_id

    if llm:
        _enrich_with_llm(result)

    if output_format == "json":
        click.echo(result.model_dump_json(indent=2))
    else:
        format_result(result)

    if output_file:
        import json
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(result.model_dump_json(indent=2))
        click.echo(f"\nResults saved to: {output_file}")


@cli.command()
def interactive():
    """Start interactive guided diagnosis mode."""
    from .interactive import run_interactive
    run_interactive()


@cli.group()
def rules():
    """Rule management commands."""


@rules.command("list")
def rules_list():
    """Display all loaded fault diagnosis rules."""
    from .output import format_rules
    loader = RuleLoader()
    format_rules(loader)


@rules.command("validate")
def rules_validate():
    """Validate YAML rule files."""
    from .output import validate_rules_output
    validate_rules_output()


@cli.command()
@click.option("--port", type=int, default=8501, help="Streamlit server port")
@click.option("--host", type=str, default="localhost", help="Streamlit server host")
def web(port, host):
    """Launch the Streamlit web dashboard."""
    import subprocess
    from ..config.settings import PROJECT_ROOT

    web_app = PROJECT_ROOT / "anaerobic_reactor_agent" / "web" / "app.py"
    subprocess.run(
        [sys.executable, "-m", "streamlit", "run", str(web_app),
         "--server.port", str(port), "--server.address", host]
    )


def _enrich_with_llm(result: DiagnosisResult):
    """Try to enrich diagnosis with LLM analysis."""
    from ..llm.factory import create_provider
    try:
        provider = create_provider()
        if provider:
            click.echo("Running LLM analysis...")
            result.llm_analysis = provider.analyze(result)
            result.llm_model = provider.model_name
        else:
            click.echo("No LLM provider configured. Set ANTHROPIC_API_KEY or OPENAI_API_KEY.", err=True)
    except Exception as e:
        click.echo(f"LLM enrichment failed: {e}", err=True)
