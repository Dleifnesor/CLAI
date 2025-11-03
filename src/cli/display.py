"""Display manager for Rich terminal formatting."""

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from rich.syntax import Syntax
from rich.markdown import Markdown
from rich.live import Live
from rich.layout import Layout
from typing import Dict, List, Any


class DisplayManager:
    """Manages all terminal display formatting with Rich."""
    
    def __init__(self):
        """Initialize display manager."""
        self.console = Console()
    
    def show_banner(self):
        """Display application banner."""
        banner = """
╔══════════════════════════════════════════════════════════╗
║     CLAI - Kali AI Command Chaining System              ║
║     Autonomous AI-Powered Penetration Testing           ║
╚══════════════════════════════════════════════════════════╝
"""
        self.console.print(banner, style="bold cyan")
    
    def show_objective(self, objective: str):
        """Display the security objective."""
        panel = Panel(
            objective,
            title="[bold cyan]🎯 Security Objective[/bold cyan]",
            border_style="cyan",
            padding=(1, 2),
        )
        self.console.print(panel)
    
    def show_command(
        self,
        command: str,
        tool: str,
        reasoning: str,
        risk_level: str,
    ):
        """Display command with AI reasoning."""
        # Color based on risk level
        color_map = {
            "safe": "green",
            "medium": "yellow",
            "high": "red",
            "blacklisted": "red bold",
        }
        color = color_map.get(risk_level, "white")
        
        content = f"""[bold]Command:[/bold] {command}
[bold]Tool:[/bold] {tool}
[bold]Risk Level:[/bold] [{color}]{risk_level.upper()}[/{color}]

[dim]Reasoning:[/dim]
{reasoning}
"""
        
        panel = Panel(
            content,
            title="[bold]💻 Executing Command[/bold]",
            border_style=color,
            padding=(1, 2),
        )
        self.console.print(panel)
    
    def show_output(self, output: str, tool: str, success: bool):
        """Display command output."""
        # Truncate very long output
        display_output = output[:2000] if len(output) > 2000 else output
        if len(output) > 2000:
            display_output += f"\n\n... (truncated, {len(output) - 2000} more characters)"
        
        border_color = "green" if success else "red"
        title = f"[bold]✓ Output: {tool}[/bold]" if success else f"[bold]✗ Error: {tool}[/bold]"
        
        panel = Panel(
            display_output,
            title=title,
            border_style=border_color,
            padding=(1, 2),
        )
        self.console.print(panel)
    
    def show_discoveries(self, discoveries: Dict[str, List[Any]]):
        """Display discovered assets and vulnerabilities."""
        if not any(discoveries.values()):
            return
        
        table = Table(title="📊 Discoveries", show_header=True, header_style="bold cyan")
        table.add_column("Type", style="cyan", width=15)
        table.add_column("Details", style="white", width=50)
        table.add_column("Severity", style="yellow", width=10)
        
        # Add hosts
        for host in discoveries.get('hosts', [])[:10]:  # Limit display
            table.add_row(
                "Host",
                host.get('ip', 'unknown'),
                "Info"
            )
        
        # Add services
        for service in discoveries.get('services', [])[:10]:
            details = f"{service.get('ip', 'unknown')}:{service.get('port', '?')} - {service.get('service', 'unknown')}"
            table.add_row(
                "Service",
                details,
                "Info"
            )
        
        # Add vulnerabilities
        for vuln in discoveries.get('vulnerabilities', []):
            severity = vuln.get('severity', 'medium')
            severity_color = {
                'critical': 'red bold',
                'high': 'red',
                'medium': 'yellow',
                'low': 'green',
            }.get(severity, 'white')
            
            table.add_row(
                "Vulnerability",
                vuln.get('details', vuln.get('type', 'unknown'))[:50],
                f"[{severity_color}]{severity.upper()}[/{severity_color}]"
            )
        
        # Add credentials
        for cred in discoveries.get('credentials', []):
            details = f"{cred.get('username', '?')}@{cred.get('host', '?')}"
            table.add_row(
                "Credential",
                details,
                "[red]HIGH[/red]"
            )
        
        self.console.print(table)
    
    def show_progress(self, progress: float, status: str):
        """Display progress bar."""
        self.console.print(f"\n🤖 Status: {status}")
        
        progress_bar = Progress(
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        )
        
        with progress_bar:
            task = progress_bar.add_task(
                "[cyan]Progress",
                total=100,
                completed=progress
            )
        
        self.console.print()
    
    def show_approval_request(self, command: str, info: Dict[str, Any]) -> bool:
        """
        Display approval request and get user response.
        
        Args:
            command: Command requiring approval
            info: Approval information
            
        Returns:
            True if approved
        """
        risk_level = info.get('risk_level', 'unknown')
        color = "red" if risk_level == 'high' else "yellow"
        
        content = f"""[bold {color}]⚠️  High-Risk Command Detected[/bold {color}]

[bold]Command:[/bold] {command}
[bold]Risk Level:[/bold] [{color}]{risk_level.upper()}[/{color}]

[bold]AI Reasoning:[/bold]
{info.get('ai_reasoning', 'No reasoning provided')}

[bold]Risk Assessment:[/bold]
{info.get('reason', 'Unknown risk')}
"""
        
        panel = Panel(
            content,
            title="[bold red]⚠️  Approval Required[/bold red]",
            border_style="red",
            padding=(1, 2),
        )
        
        self.console.print(panel)
        
        # Get user input
        response = self.console.input("\n[bold yellow]Execute this command? [y/N]:[/bold yellow] ")
        
        return response.lower() in ['y', 'yes']
    
    def show_error(self, error: str, error_type: str = "ERROR"):
        """Display error message."""
        self.console.print(f"\n[bold red]❌ {error_type}:[/bold red] {error}\n")
    
    def show_success(self, message: str):
        """Display success message."""
        self.console.print(f"\n[bold green]✓ {message}[/bold green]\n")
    
    def show_info(self, message: str):
        """Display info message."""
        self.console.print(f"\n[bold blue]ℹ {message}[/bold blue]\n")
    
    def show_warning(self, message: str):
        """Display warning message."""
        self.console.print(f"\n[bold yellow]⚠ {message}[/bold yellow]\n")
    
    def show_summary(self, summary: str):
        """Display summary text."""
        panel = Panel(
            summary,
            title="[bold]📋 Summary[/bold]",
            border_style="blue",
            padding=(1, 2),
        )
        self.console.print(panel)
    
    def show_report(self, report: Dict[str, Any]):
        """Display final report."""
        discoveries = report.get('discoveries', {})
        
        content = f"""[bold]Session ID:[/bold] {report.get('session_id', 'unknown')}
[bold]Objective:[/bold] {report.get('objective', 'unknown')}
[bold]Progress:[/bold] {report.get('progress', 0):.1f}%
[bold]Commands Executed:[/bold] {report.get('commands_executed', 0)}
[bold]Duration:[/bold] {report.get('duration', 0):.2f}s

[bold cyan]Discoveries:[/bold cyan]
  • Hosts: {discoveries.get('hosts', 0)}
  • Services: {discoveries.get('services', 0)}
  • Vulnerabilities: {discoveries.get('vulnerabilities', 0)}
  • Credentials: {discoveries.get('credentials', 0)}

[bold]Failed Attempts:[/bold] {report.get('failed_attempts', 0)}
[bold]Strategy Changes:[/bold] {report.get('strategy_changes', 0)}
"""
        
        panel = Panel(
            content,
            title="[bold green]✅ Assessment Complete[/bold green]",
            border_style="green",
            padding=(1, 2),
        )
        
        self.console.print(panel)
        
        # Show detailed discoveries if any
        detailed = report.get('detailed_discoveries', {})
        if any(detailed.values()):
            self.show_discoveries(detailed)
    
    def clear(self):
        """Clear the console."""
        self.console.clear()