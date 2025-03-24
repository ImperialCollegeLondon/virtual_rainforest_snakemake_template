#!/usr/bin/env python3
"""A wrapper script for invoking qsub with the correct arguments."""

import math
import sys
from os import execvp


def get_runtime_str(runtime_min: int) -> str:
    """Convert the runtime in whole minutes to HH:MM:SS."""
    hours, mins = divmod(runtime_min, 60)
    return f"{hours:02}:{mins:02}:00"


def main(threads: int, mem_mb: int, runtime_min: int, job_script: str) -> None:
    """Launch qsub with the specified arguments."""
    # qsub wants memory requirement in whole gigabytes
    mem_gb = max(1, math.ceil(mem_mb / 1000))

    execvp(
        "qsub",
        (
            "qsub",
            f"-lselect=1:ncpus={threads}:mem={mem_gb}gb",
            f"-lwalltime={get_runtime_str(runtime_min)}",
            job_script,
        ),
    )


def usage() -> None:
    """Display help and exit."""
    print("Usage: pbs-submit.py [num threads] [memory in mb] [runtime in minutes]")
    sys.exit(1)


if __name__ == "__main__":
    if len(sys.argv) != 5:
        usage()

    try:
        threads = int(sys.argv[1])
        mem_mb = int(sys.argv[2])
        runtime_min = int(sys.argv[3])
    except ValueError:
        usage()

    main(threads, mem_mb, runtime_min, sys.argv[-1])
