"""Project report archive generation.

Bundles a project's exported report files into a single downloadable archive.
The archive format and output name are chosen by the requesting client so the
download can be labelled to match their internal naming conventions.
"""

import os
import subprocess

_EXPORT_ROOT = "/tmp/nexus-exports"
_SUPPORTED_FORMATS = ("zip", "tar", "tgz")


def _write_report_files(project_id: str, workdir: str) -> list[str]:
    """Write the project's report sections into workdir, returning their names."""
    os.makedirs(workdir, exist_ok=True)
    names: list[str] = []
    for section in ("summary", "timeline", "deliverables"):
        name = f"{section}.txt"
        with open(os.path.join(workdir, name), "w", encoding="utf-8") as handle:
            handle.write(f"{section} report for project {project_id}\n")
        names.append(name)
    return names


def _compress(workdir: str, filename: str, fmt: str) -> str:
    """Compress the prepared workdir into an archive named *filename*."""
    output_path = os.path.join(_EXPORT_ROOT, filename)
    if fmt == "zip":
        command = f"cd {workdir} && zip -r {output_path} ."
    else:
        command = f"tar czf {output_path} -C {workdir} ."
    subprocess.run(command, shell=True, check=False)
    return output_path


def build_project_archive(project_id: str, filename: str, fmt: str = "zip") -> dict:
    """Build a downloadable report archive for a project.

    Prepares the report files in a temp workspace and compresses them into the
    requested output filename and format.
    """
    fmt = fmt if fmt in _SUPPORTED_FORMATS else "zip"
    os.makedirs(_EXPORT_ROOT, exist_ok=True)
    workdir = os.path.join(_EXPORT_ROOT, f"work-{project_id}")
    files = _write_report_files(project_id, workdir)
    archive_path = _compress(workdir, filename, fmt)
    return {
        "project_id": project_id,
        "archive": archive_path,
        "format": fmt,
        "files": files,
    }
