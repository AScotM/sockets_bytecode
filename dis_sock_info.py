import subprocess
import dis
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
from rich.progress import track
import time

console = Console()

def get_socket_summary():
    console.print("[bold blue]Executing 'ss' command to fetch socket summary...[/bold blue]")
    try:
        socket_summary = subprocess.check_output(['ss', '-s'], encoding='utf-8')
        console.print("[bold green]Success! Retrieved socket summary.[/bold green]")
        return socket_summary
    except subprocess.CalledProcessError as e:
        error_message = f"Command error: {e}"
        console.print(f"[bold red]{error_message}[/bold red]")
        return error_message
    except FileNotFoundError:
        error_message = "Error: 'ss' command not found. Please install iproute."
        console.print(f"[bold red]{error_message}[/bold red]")
        return error_message
    except Exception as e:
        error_message = f"An unexpected error occurred: {e}"
        console.print(f"[bold red]{error_message}[/bold red]")
        return error_message

def print_socket_summary():
    console.print(Panel("[bold yellow]Welcome to the Socket Summary Analyzer[/bold yellow]", style="bold magenta"))
    
    for step in track(range(5), description="Preparing cinematic analysis..."):
        time.sleep(0.3)  # Simulate a loading effect
    
    socket_summary = get_socket_summary()
    console.rule("[bold green]Socket Summary[/bold green]")
    console.print(Panel(socket_summary, title="Socket Details", style="cyan"), justify="center")

    console.rule("[bold magenta]Bytecode Analysis[/bold magenta]")
    bytecode = Syntax(dis.Bytecode(get_socket_summary).dis(), "python", theme="monokai", line_numbers=True)
    console.print(bytecode)

if __name__ == "__main__":
    print_socket_summary()
