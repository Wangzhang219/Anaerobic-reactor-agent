"""Rich-formatted terminal output for diagnosis results and rules."""

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich import box

from ..engine.rule_loader import RuleLoader
from ..models.diagnosis import DiagnosisResult, ParameterStatus, FaultSeverity, GradedRecommendation
from ..utils.exceptions import ConfigurationError

console = Console()

STATUS_COLORS = {
    ParameterStatus.NORMAL: "green",
    ParameterStatus.WARNING: "yellow",
    ParameterStatus.ALARM: "red",
}

SEVERITY_COLORS = {
    FaultSeverity.WARNING: "yellow",
    FaultSeverity.ALARM: "red",
    FaultSeverity.CRITICAL: "bright_red",
}

LEVEL_LABELS = {"immediate": "[!] 紧急", "long_term": "[~] 长期", "preventive": "[*] 预防"}


def format_result(result: DiagnosisResult):
    """Pretty-print a diagnosis result using Rich."""

    status_color = STATUS_COLORS.get(result.overall_status, "white")
    status_text = Text(f"  {result.overall_status.value.upper()}  ", style=f"bold white on {status_color}")
    console.print()
    console.print(Panel(status_text, title="Overall Reactor Status", border_style=status_color))

    if result.faults:
        console.print()
        console.print(f"[bold]Detected Faults ({len(result.faults)}):[/bold]")
        for fault in result.faults:
            sev_color = SEVERITY_COLORS.get(fault.severity, "white")
            body = f"[bold]{fault.fault_type}[/bold] (confidence: {fault.confidence:.0%})\n"
            body += f"{fault.description}\n"
            if fault.causal_chain:
                body += f"\n[dim]Causal Chain: {fault.causal_chain}[/dim]\n"
            if fault.evidence:
                body += f"\nEvidence:\n  " + "\n  ".join(f"- {e}" for e in fault.evidence)
            console.print(
                Panel(
                    body,
                    title=f"[{sev_color}]{fault.severity.value.upper()}[/{sev_color}]",
                    border_style=sev_color,
                )
            )
    else:
        console.print("\n[green]No faults detected. Reactor is operating normally.[/green]")

    console.print()
    table = Table(title="Parameter Assessment", box=box.SIMPLE)
    table.add_column("Parameter", style="cyan")
    table.add_column("Value", justify="right")
    table.add_column("Status")
    table.add_column("Health", justify="right")
    table.add_column("Normal Range")
    table.add_column("Message")

    for a in result.parameter_assessments:
        status_style = STATUS_COLORS.get(a.status, "white")
        table.add_row(
            a.parameter_name,
            str(a.current_value),
            f"[{status_style}]{a.status.value}[/{status_style}]",
            f"{a.health_score:.0%}",
            a.normal_range,
            a.message,
        )

    console.print(table)

    if result.recommendations:
        console.print()
        console.print("[bold]Recommendations:[/bold]")
        for i, rec in enumerate(result.recommendations, 1):
            label = LEVEL_LABELS.get(rec.level, f"[{rec.level}]")
            console.print(f"  {i}. {label} {rec.text}")

    if result.llm_analysis:
        console.print()
        console.print(Panel(
            result.llm_analysis,
            title=f"LLM Analysis ({result.llm_model or 'unknown model'})",
            border_style="blue",
        ))


def format_rules(loader: RuleLoader):
    """Display all fault rules in a Rich table."""
    table = Table(title="Fault Diagnosis Rules", box=box.SIMPLE)
    table.add_column("Priority", justify="right")
    table.add_column("Name", style="cyan")
    table.add_column("Type")
    table.add_column("Severity")
    table.add_column("Conditions")
    table.add_column("Min Confidence", justify="right")

    for rule in loader.rules:
        sev_color = SEVERITY_COLORS.get(FaultSeverity(rule.severity), "white")
        conditions_str = ", ".join(
            f"{c.parameter} {c.operator} {c.value}" for c in rule.conditions
        )
        table.add_row(
            str(rule.priority),
            rule.name,
            rule.fault_type,
            f"[{sev_color}]{rule.severity}[/{sev_color}]",
            conditions_str,
            f"{rule.min_confidence:.0%}",
        )

    console.print(table)
    console.print(f"\nTotal: {len(loader.rules)} rules loaded")


def validate_rules_output():
    """Load rules and report validity."""
    try:
        loader = RuleLoader()
        console.print(f"[green]All rule files loaded successfully.[/green]")
        console.print(f"  Rules: {len(loader.rules)}")
        console.print(f"  Threshold parameters: {len(loader.thresholds.get('parameters', {}))}")
    except ConfigurationError as e:
        console.print(f"[red]Configuration error:[/red] {e}")
        raise SystemExit(1)
