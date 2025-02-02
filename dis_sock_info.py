import subprocess
import dis
import io
import contextlib
import time
from rich.console import Console
from rich.panel import Panel
from rich.progress import track

console = Console()

def get_socket_summary():
    console.print("[bold blue]Executing 'ss' command to fetch socket summary...[/bold blue]")
    try:
        result = subprocess.run(['ss', '-s'], capture_output=True, text=True)
        console.print("[bold green]Success! Retrieved socket summary.[/bold green]")
        return result.stdout
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

def get_bytecode(func):
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        dis.dis(func)
    return buf.getvalue()

def print_socket_summary():
    console.print(Panel("[bold yellow]Welcome to the Socket Summary Analyzer[/bold yellow]", style="bold magenta"))
    
    for _ in track(range(5), description="Preparing cinematic analysis..."):
        time.sleep(0.1)
    
    socket_summary = get_socket_summary()
    console.rule("[bold green]Socket Summary[/bold green]")
    console.print(Panel(socket_summary, title="Socket Details", style="cyan"), justify="center")
    
    console.rule("[bold magenta]Bytecode Analysis[/bold magenta]")
    console.print(get_bytecode(get_socket_summary))

if __name__ == "__main__":
    print_socket_summary()
