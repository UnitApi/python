"""
UnitAPI Utilities Module

This module provides utility functions for the UnitAPI system.
"""

import os
import sys
import platform
import subprocess
import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger("unitapi.utils")


def check_dependencies() -> Dict[str, Dict[str, Any]]:
    """
    Check if required dependencies are installed.

    Returns:
        A dictionary with dependency information
    """
    dependencies = {
        "ffmpeg": {"installed": False, "version": None, "path": None},
        "python": {
            "installed": True,
            "version": platform.python_version(),
            "path": sys.executable,
        },
    }

    # Check for FFmpeg
    try:
        result = subprocess.run(
            ["ffmpeg", "-version"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

        if result.returncode == 0:
            dependencies["ffmpeg"]["installed"] = True

            # Extract version
            version_line = result.stdout.split("\n")[0]
            if "ffmpeg version" in version_line:
                dependencies["ffmpeg"]["version"] = (
                    version_line.split("ffmpeg version")[1].strip().split(" ")[0]
                )

            # Find path
            try:
                path_result = subprocess.run(
                    (
                        ["which", "ffmpeg"]
                        if platform.system() != "Windows"
                        else ["where", "ffmpeg"]
                    ),
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                )

                if path_result.returncode == 0:
                    dependencies["ffmpeg"]["path"] = path_result.stdout.strip()
            except Exception as e:
                logger.debug(f"Error finding FFmpeg path: {e}")

    except Exception as e:
        logger.debug(f"Error checking FFmpeg: {e}")

    return dependencies


def get_system_info() -> Dict[str, Any]:
    """
    Get system information.

    Returns:
        A dictionary with system information
    """
    info = {
        "platform": platform.system(),
        "platform_release": platform.release(),
        "platform_version": platform.version(),
        "architecture": platform.machine(),
        "processor": platform.processor(),
        "python_version": platform.python_version(),
        "python_implementation": platform.python_implementation(),
        "python_path": sys.executable,
    }

    return info


def ensure_dir(path: str) -> bool:
    """
    Ensure a directory exists, creating it if necessary.

    Args:
        path: Path to the directory

    Returns:
        True if the directory exists or was created, False otherwise
    """
    if not path:
        return False

    try:
        if not os.path.exists(path):
            os.makedirs(path)
            logger.debug(f"Created directory: {path}")
        return True
    except Exception as e:
        logger.error(f"Error creating directory {path}: {e}")
        return False


def find_executable(name: str) -> Optional[str]:
    """
    Find the path to an executable.

    Args:
        name: Name of the executable

    Returns:
        Path to the executable, or None if not found
    """
    try:
        if platform.system() == "Windows":
            cmd = ["where", name]
        else:
            cmd = ["which", name]

        result = subprocess.run(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )

        if result.returncode == 0:
            return result.stdout.strip().split("\n")[0]
    except Exception as e:
        logger.debug(f"Error finding executable {name}: {e}")

    return None


def run_command(cmd: List[str], cwd: Optional[str] = None) -> Dict[str, Any]:
    """
    Run a command and return the result.

    Args:
        cmd: Command to run
        cwd: Working directory

    Returns:
        A dictionary with the command result
    """
    result = {
        "success": False,
        "returncode": None,
        "stdout": "",
        "stderr": "",
        "error": None,
    }

    try:
        process = subprocess.run(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, cwd=cwd
        )

        result["returncode"] = process.returncode
        result["stdout"] = process.stdout
        result["stderr"] = process.stderr
        result["success"] = process.returncode == 0
    except Exception as e:
        result["error"] = str(e)

    return result
