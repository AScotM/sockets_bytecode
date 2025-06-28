#!/usr/bin/env python3
"""Robust Socket Monitoring Tool - Conflict-Free Version"""

import json
import logging
import shutil
import subprocess
import time
from io import StringIO

# Configuration using simple class instead of dataclass
class Config:
    def __init__(self):
        self.LOG_LEVEL = "INFO"
        self.COMMAND_TIMEOUT = 10  # seconds
        self.SS_PATH = shutil.which("ss") or "/usr/bin/ss"

config = Config()

# Logging setup
logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("socket_monitor.log")
    ]
)
logger = logging.getLogger(__name__)

class SocketMonitor:
    @staticmethod
    def get_summary(json_output: bool = False):
        """
        Get socket summary statistics.
        
        Args:
            json_output: Return parsed JSON if True, raw text otherwise
            
        Returns:
            str: Raw command output when json_output=False
            dict: Parsed data when json_output=True
        """
        try:
            if not shutil.which(config.SS_PATH):
                raise FileNotFoundError(f"Command not found: {config.SS_PATH}")

            start_time = time.time()
            
            result = subprocess.run(
                [config.SS_PATH, "-s"],
                capture_output=True,
                text=True,
                timeout=config.COMMAND_TIMEOUT,
                check=True
            )
            
            logger.info(f"Command completed in {time.time() - start_time:.2f}s")
            
            if json_output:
                return SocketMonitor._parse_summary(result.stdout)
            return result.stdout.strip()
            
        except subprocess.TimeoutExpired:
            logger.error("Command timed out")
            raise
        except subprocess.CalledProcessError as e:
            logger.error(f"Command failed with code {e.returncode}: {e.stderr}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            raise

    @staticmethod
    def _parse_summary(output: str) -> dict:
        """Parse ss command output into structured data."""
        parsed = {}
        current_section = None
        
        for line in output.splitlines():
            line = line.strip()
            
            if line.endswith(':'):
                current_section = line[:-1]
                parsed[current_section] = {}
                continue
                
            if ':' in line:
                key, val = [part.strip() for part in line.split(':', 1)]
                
                try:
                    val = int(val) if val.isdigit() else val
                except (ValueError, AttributeError):
                    pass
                    
                if current_section:
                    parsed[current_section][key] = val
                else:
                    parsed[key] = val
                    
        return parsed

def main():
    """Command line interface"""
    monitor = SocketMonitor()
    
    try:
        # Get and display summary
        summary = monitor.get_summary(json_output=True)
        print(json.dumps(summary, indent=2))
            
    except Exception as e:
        logger.critical(f"Application failed: {str(e)}")
        return 1
        
    return 0

if __name__ == "__main__":
    exit(main())
