"""Media transcoding helpers that delegate to the system ffmpeg tool."""

import subprocess

_OUTPUT_DIR = "/tmp/nexus-renditions"


def prepare_pipeline(filename: str, profile: str) -> str:
    """Prepare and execute the transcode pipeline for a stored file."""
    return _assemble_command(filename, profile)


def _assemble_command(filename: str, profile: str) -> str:
    """Build the transcode command line, then run it."""
    scale = "640:-1" if profile == "thumb" else "1280:-1"
    output = f"{_OUTPUT_DIR}/{profile}.mp4"
    command = f"ffmpeg -i {_OUTPUT_DIR}/{filename} -vf scale={scale} {output}"
    return _run_shell(command)


def _run_shell(command: str) -> str:
    """Run a prepared shell command and return the output path."""
    subprocess.run(command, shell=True, check=False)
    return command.split()[-1]
