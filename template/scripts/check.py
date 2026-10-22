"""Check Rust formatting/lints and Godot import. Requires Python 3.11+."""

import argparse
import os
from pathlib import Path
import re
import socket
import subprocess
import sys

import native_build


ROOT = Path(__file__).resolve().parent.parent
ENGINE_DIAGNOSTIC = re.compile(r"\b(?:SCRIPT ERROR|ERROR|Error):|panicked at")


def editor_server_arguments():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as listener:
        listener.bind(("127.0.0.1", 0))
        port = listener.getsockname()[1]

    return (
        "--debug-server",
        f"tcp://127.0.0.1:{port}",
        "--dap-port",
        "0",
        "--lsp-port",
        "0",
    )


def run(command, *, timeout=300):
    try:
        result = subprocess.run(
            command,
            cwd=ROOT,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout,
        )
    except subprocess.TimeoutExpired as error:
        output = error.stdout or ""

        if isinstance(output, bytes):
            output = output.decode("utf-8", errors="replace")

        raise RuntimeError(
            f"Command timed out after {timeout}s: {command}\n{output}"
        ) from error

    print(
        result.stdout,
        end="",
        flush=True,
    )

    if result.returncode != 0 or ENGINE_DIAGNOSTIC.search(result.stdout):
        raise RuntimeError(
            f"Command failed (exit {result.returncode}): {command}"
        )

    return result.stdout


def check_rust():
    manifest = str(ROOT / "rust/Cargo.toml")
    subprocess.run(
        ["cargo", "fmt", "--manifest-path", manifest, "--check"],
        cwd=ROOT,
        check=True,
    )

    for kind in ("runtime", "editor"):
        arguments = [
            "--locked",
            "--manifest-path",
            manifest,
            "--no-default-features",
            "--target-dir",
            str(ROOT / "rust/target" / kind),
        ]

        if kind == "editor":
            arguments.extend(["--features", "editor"])

        subprocess.run(
            [
                "cargo",
                "clippy",
                *arguments,
                "--all-targets",
                "--",
                "-D",
                "warnings",
            ],
            cwd=ROOT,
            check=True,
        )


def check_godot(godot=None):
    executable = godot or os.environ.get("GODOT", "godot")
    output = run([executable, "--version"], timeout=15)
    version = re.search(r"^([0-9]+)\.([0-9]+)(?:\.|$)", output.strip())

    if version is None or int(version[1]) != 4 or int(version[2]) < 7:
        raise ValueError(
            f"Expected Godot 4.7+ within major version 4, got {output.strip()!r}"
        )

    native_build.build("runtime")
    native_build.build("editor")
    project = str(ROOT / "godot")
    run(
        [
            executable,
            "--headless",
            "--editor",
            "--path",
            project,
            "--import",
            *editor_server_arguments(),
        ],
        timeout=120,
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "suite",
        choices=("rust", "godot", "all"),
        nargs="?",
        default="all",
    )
    parser.add_argument(
        "--godot",
        help="Godot executable path; defaults to GODOT or godot on PATH",
    )
    args = parser.parse_args()

    try:
        if args.suite in ("rust", "all"):
            check_rust()

        if args.suite in ("godot", "all"):
            check_godot(args.godot)
    except (
        OSError,
        ValueError,
        RuntimeError,
        subprocess.CalledProcessError,
    ) as error:
        print(f"error: {error}", file=sys.stderr)

        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
