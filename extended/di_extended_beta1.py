#!/usr/bin/env python3
"""
Advanced Socket Summary Analyzer with Bytecode Inspection
Provides socket information and optional bytecode analysis of its own functions.
"""

import subprocess
import sys
import json
import time
import argparse
import re
import logging
import dis
import io
import contextlib
from typing import Dict, Optional, Union
from dataclasses import dataclass
from enum import Enum, auto
from pathlib import Path

# Constants
DEFAULT_SS_PATH = "/usr/sbin/ss"
SUPPORTED_PLATFORMS = ["linux"]

class SocketType(Enum):
    TCP = "t"
    UDP = "u"
    UNIX = "x"
    ALL = None

    @classmethod
    def get_types(cls):
        return [st.value for st in cls if st.value is not None]

@dataclass
class SocketStats:
    total: int
    tcp: Optional[int] = None
    udp: Optional[int] = None
    unix: Optional[int] = None
    raw_output: Optional[str] = None
    details: Optional[Dict] = None

class OutputFormat(Enum):
    TEXT = auto()
    JSON = auto()
    VERBOSE = auto()

def configure_logging(verbose: bool = False) -> None:
    """Configure logging based on verbosity level."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler(sys.stderr)]
    )

def check_platform() -> bool:
    """Verify we're running on a supported platform."""
    return sys.platform.lower() in SUPPORTED_PLATFORMS

def find_ss_binary() -> Optional[Path]:
    """Locate the ss binary with fallback paths."""
    for path in [DEFAULT_SS_PATH, "/bin/ss", "/usr/bin/ss"]:
        if Path(path).exists():
            return Path(path)
    return None

def execute_command(cmd: list[str], timeout: int = 10) -> tuple[bool, str]:
    """Execute a command with timeout and return (success, output)."""
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True,
            timeout=timeout
        )
        return True, result.stdout.strip()
    except subprocess.SubprocessError as e:
        logging.error(f"Command failed: {e}")
        return False, str(e)

def parse_socket_output(output: str) -> Dict:
    """Parse ss command output into structured data."""
    parsed = {}
    for line in output.splitlines():
        if match := re.match(r"(\w+)\s*:\s*(.+)", line):
            key, value = match.groups()
            # Handle numeric values and complex cases
            if num_match := re.match(r"^(\d+)", value.strip()):
                parsed[key] = int(num_match.group(1))
                # Extract additional stats from complex values
                if extra := re.findall(r"(\w+\s\d+)", value):
                    parsed[f"{key}_details"] = dict(
                        item.split() for item in extra
                    )
            else:
                parsed[key] = value.strip()
    return parsed

def get_socket_stats(
    socket_type: Optional[SocketType] = None,
    timeout: int = 10
) -> Union[SocketStats, str]:
    """
    Retrieve socket statistics with optional filtering.
    
    Args:
        socket_type: Type of sockets to filter (TCP, UDP, UNIX)
        timeout: Command execution timeout in seconds
    
    Returns:
        SocketStats object on success, error message on failure
    """
    if not check_platform():
        return "Error: Unsupported platform. This tool only works on Linux."

    ss_path = find_ss_binary()
    if not ss_path:
        return "Error: 'ss' command not found. Please install iproute2 package."

    cmd = [str(ss_path), "-s"]
    if socket_type and socket_type != SocketType.ALL:
        cmd.extend([f"-{socket_type.value}"])

    logging.debug(f"Executing: {' '.join(cmd)}")
    start = time.monotonic()
    
    success, output = execute_command(cmd, timeout)
    if not success:
        return output
    
    elapsed = time.monotonic() - start
    logging.info(f"Retrieved socket stats in {elapsed:.2f}s")
    
    parsed = parse_socket_output(output)
    return SocketStats(
        total=parsed.get("Total", 0),
        tcp=parsed.get("TCP"),
        udp=parsed.get("UDP"),
        unix=parsed.get("UNIX"),
        raw_output=output,
        details=parsed
    )

def get_bytecode(func) -> str:
    """
    Disassembles the given function and returns its bytecode as a string.
    
    Args:
        func: Function to disassemble
    
    Returns:
        str: Formatted bytecode
    """
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        dis.dis(func)
    return f"Bytecode for {func.__name__}:\n{buf.getvalue()}"

def format_output(
    stats: Union[SocketStats, str],
    fmt: OutputFormat = OutputFormat.TEXT,
    show_bytecode: bool = False
) -> str:
    """Format the output according to the specified format."""
    result = []
    
    # Handle error case
    if isinstance(stats, str):
        result.append(stats)
    else:
        # Main output
        if fmt == OutputFormat.TEXT:
            result.append(stats.raw_output or "No data available")
        elif fmt == OutputFormat.VERBOSE:
            verbose_out = []
            if stats.raw_output:
                verbose_out.append("=== Raw Output ===")
                verbose_out.append(stats.raw_output)
            if stats.details:
                verbose_out.append("\n=== Parsed Details ===")
                verbose_out.append(json.dumps(stats.details, indent=2))
            result.append("\n".join(verbose_out))
        else:  # JSON output
            result.append(json.dumps({
                "total": stats.total,
                "tcp": stats.tcp,
                "udp": stats.udp,
                "unix": stats.unix,
                "details": stats.details
            }, indent=2))
    
    # Add bytecode if requested
    if show_bytecode:
        result.append("\n" + get_bytecode(get_socket_stats))
    
    return "\n".join(result)

def main():
    """Main entry point for command-line execution."""
    parser = argparse.ArgumentParser(
        description="Socket Statistics Analyzer with Bytecode Inspection",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(
        "-t", "--type",
        choices=SocketType.get_types(),
        help="Filter by socket type (t: TCP, u: UDP, x: UNIX)"
    )
    parser.add_argument(
        "-f", "--format",
        choices=["text", "json", "verbose"],
        default="text",
        help="Output format"
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose logging"
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=10,
        help="Command execution timeout in seconds"
    )
    parser.add_argument(
        "--bytecode",
        action="store_true",
        help="Show bytecode disassembly of the analysis functions"
    )
    
    args = parser.parse_args()
    configure_logging(args.verbose)
    
    socket_type = SocketType(args.type) if args.type else SocketType.ALL
    output_format = OutputFormat[args.format.upper()]
    
    stats = get_socket_stats(socket_type, args.timeout)
    print(format_output(stats, output_format, args.bytecode))

if __name__ == "__main__":
    main()
