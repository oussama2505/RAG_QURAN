import sys
import time
from typing import Optional, Callable
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

console = Console()

def print_colored(text: str, color: str = "white", style: str = "") -> None:
    """Print colored text to the console."""
    console.print(text, style=f"{color} {style}")

def print_success(text: str) -> None:
    """Print success message in green."""
    print_colored(text, "green", "bold")

def print_error(text: str) -> None:
    """Print error message in red."""
    print_colored(text, "red", "bold")

def print_warning(text: str) -> None:
    """Print warning message in yellow."""
    print_colored(text, "yellow", "bold")

def print_info(text: str) -> None:
    """Print info message in blue."""
    print_colored(text, "blue", "bold")

def with_progress(description: str) -> Callable:
    """Decorator to show progress for long-running operations."""
    def decorator(func: Callable) -> Callable:
        async def wrapper(*args, **kwargs):
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console
            ) as progress:
                task = progress.add_task(description, total=None)
                result = await func(*args, **kwargs)
                progress.update(task, completed=True)
                return result
        return wrapper
    return decorator

def format_json(data: dict) -> str:
    """Format data as pretty-printed JSON."""
    import json
    return json.dumps(data, indent=2)

def format_markdown(data: dict) -> str:
    """Format data as markdown."""
    output = []
    if 'answer' in data:
        output.append(f"# Answer\n\n{data['answer']}\n")
    if 'sources' in data:
        output.append("## Sources\n")
        for source in data['sources']:
            output.append(f"- {source}\n")
    if 'filters_applied' in data:
        output.append("## Filters Applied\n")
        for filter_name, value in data['filters_applied'].items():
            if value is not None:
                output.append(f"- {filter_name}: {value}\n")
    return "\n".join(output) 