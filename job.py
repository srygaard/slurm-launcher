#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///

# "chmod +x job.py" to run as an executable.

import argparse
import os
import shlex
import socket
import subprocess
import sys
from collections.abc import Mapping
from enum import StrEnum
from pathlib import Path
from typing import Literal, NamedTuple, cast, get_args

type Cluster = Literal["mila", "fir", "narval", "nibi", "rorqual", "trillium", "unknown"]


def detect_cluster() -> Cluster:
    cluster: str = os.environ.get("CC_CLUSTER", "").strip().lower()
    if cluster in get_args(Cluster.__value__):
        return cast(Cluster, cluster)
    if socket.getfqdn().lower().endswith("mila.quebec"):
        return "mila"
    return "unknown"


class Ansi(StrEnum):
    PURPLE = "\033[35m"
    YELLOW = "\033[33m"
    RED = "\033[31m"
    RESET = "\033[0m"


class SbatchResult(NamedTuple):
    stdout: str
    stderr: str
    job_id: int | None
    returncode: int


def sbatch(script: str) -> SbatchResult:
    """Submit a job script to SLURM."""
    try:
        result = subprocess.run(["sbatch", "--parsable"], input=script, capture_output=True, text=True)
    except FileNotFoundError:
        return SbatchResult(stdout="",
                            stderr="Must be run on a Slurm (sbatch not found).",
                            job_id=None,
                            returncode=127)
    try:
        job_id = int(result.stdout.split(";")[0])
    except ValueError:
        job_id = None
    return SbatchResult(result.stdout, result.stderr, job_id, result.returncode)


def git_commit_hash() -> str:
    """
    >>> git_revision()  # clean checkout
    'a1b2c3d'
    >>> git_revision()  # uncommitted changes
    'a1b2c3d-dirty'
    >>> git_revision()  # no commits yet
    'unknown'
    """
    def stdout(*cmd: str) -> str:
        try:
            result = subprocess.run(cmd, capture_output=True, text=True)
        except FileNotFoundError:
            return ""
        return result.stdout.strip() if result.returncode == 0 else ""

    if not (sha_short := stdout("git", "rev-parse", "--short", "HEAD")):
        return "unknown"
    return sha_short + ("-dirty" if stdout("git", "status", "--porcelain") else "")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Submit a job to SLURM.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    slurm_dir = Path(__file__).parent / "slurm"
    parser.add_argument("-l", "--log-dir", type=Path, default=slurm_dir / "jobs",
                        help="Directory for job logs and script snapshot")
    parser.add_argument("-f", "--template", type=Path, default=None,
                        help="Path to a template file, overriding slurm/templates/<config>.<cluster>.sh")
    parser.add_argument("-C", "--cluster", default=detect_cluster(),
                        help="Override the cluster instead of using the autodetected name")
    parser.add_argument("-c", "--config", default="default",
                        help="Selects slurm/templates/<config>.<cluster>.sh")
    parser.add_argument("-T", "--time", default="3:00:00",
                        help="The sbatch wall-clock limit (HH:MM:SS)")
    parser.add_argument("-d", "--dependency", type=int, default=None,
                        help="Wait until the specified job ID finishes before starting the job")
    parser.add_argument("--dry-run", action="store_true",
                        help="Print the generated script without submitting")
    parser.add_argument("extra_args", nargs=argparse.REMAINDER,
                        help="Arguments forwarded to script, e.g. `-- --lr 3e-4 --steps 10000`")
    args = parser.parse_args()

    if args.cluster is None:
        parser.error("Unrecognized cluster. Specify using: --cluster")
    args.template = args.template or slurm_dir / "templates" / f"{args.config}.{args.cluster}.sh"

    if not args.template.is_file():
        parser.error(f"Template not found: {args.template}")
    args.extra_args = args.extra_args[1:] if args.extra_args[:1] == ["--"] else args.extra_args
    return args


def generate_header(template: Path,
                    dependency: int | None,
                    placeholders: Mapping[str, object]) -> str:
    """Fill in the template's #SBATCH directives, then append the conditional ones."""
    header = template.read_text().format_map(placeholders)
    if not header.endswith("\n"):
        header += "\n"

    if dependency is not None:
        header += f"#SBATCH --dependency=afterany:{dependency}\n"
    return header


def main(args: argparse.Namespace) -> int:
    header = generate_header(args.template, args.dependency, {
        "job_name": f"train-{args.config}",
        "time": args.time,
        "log_dir": args.log_dir,
    })
    command = shlex.join(["uv", "run", "train.py", *args.extra_args])
    script = f'{header}\n{command}'

    if args.dry_run:
        print(f"[dry-run] not submitting\n\n{Ansi.YELLOW}{script}{Ansi.RESET}\n")
        return 0

    args.log_dir.mkdir(parents=True, exist_ok=True)

    result = sbatch(script)
    if result.job_id is None:  # nothing was queued, or we can't tell which job it was
        print(f"{Ansi.RED}{result.stderr or result.stdout}{Ansi.RESET}")
        return result.returncode or 1
    if result.returncode != 0:  # queued despite the complaint -- report it, then archive
        print(f"{Ansi.RED}{result.stderr}{Ansi.RESET}")

    # Store the job script for reproducability
    meta = f"# git {git_commit_hash()}\n# argv: {shlex.join(sys.argv)}\n"
    job_script_snapshot = args.log_dir / f"{result.job_id}-job.sh"
    job_script_snapshot.write_text(f"{script}\n{meta}")

    print(f"Job {Ansi.PURPLE}{result.job_id}{Ansi.RESET} requested on {args.cluster}/{args.config}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(parse_args()))
