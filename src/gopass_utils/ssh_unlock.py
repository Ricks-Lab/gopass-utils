#!/usr/bin/env python3
import argparse
import subprocess
from pathlib import Path
import sys
import pexpect
import socket

def get_hostname() -> str:
    return socket.gethostname().lower()

SSH_DIR = Path.home() / ".ssh"

# Key name → Gopass path → Expected comment (e.g., hostname or system)
SSH_KEYS = {
    "rick_askone":     ("ssh/rick_askone", "askone"),
    "rick_eos":        ("ssh/rick_eos", "eos"),
    "rick_git_askone": ("ssh/rick_git_askone", "askone"),
    "rick_git_eos":    ("ssh/rick_git_eos", "eos"),
    "rick_git_nexon":  ("ssh/rick_git_nexon", "nexon"),
    "rick_nexon":      ("ssh/rick_nexon", "nexon"),
}

def is_key_loaded(key_path: Path) -> bool:
    try:
        # Get fingerprint of this key
        result = subprocess.run(
            ["ssh-keygen", "-lf", str(key_path)],
            capture_output=True,
            check=True,
            text=True
        )
        fingerprint = result.stdout.strip().split()[1]  # SHA256:...
    except Exception:
        return False

    # Compare with loaded keys
    try:
        result = subprocess.run(["ssh-add", "-l"], capture_output=True, text=True)
        return fingerprint in result.stdout
    except Exception:
        return False

def get_key_comment(key_path: Path) -> str:
    try:
        result = subprocess.run(
            ["ssh-keygen", "-lf", str(key_path)],
            capture_output=True,
            check=True,
            text=True
        )
        # Output example: 2048 SHA256:... rick@askone (RSA)
        return result.stdout.strip().split()[-2]
    except Exception:
        return "unknown"

def unlock_key(key_name: str, gopass_path: str, expected_host: str):
    key_path = SSH_DIR / key_name
    if not key_path.exists():
        print(f"❌ Key not found: {key_path}")
        return

    if is_key_loaded(key_path):
        print(f"✅ Already unlocked: {key_name}")
        return

    # Validate host match from comment
    comment = get_key_comment(key_path)
    if expected_host and expected_host.lower() not in comment.lower():
        print(f"⚠️  Key {key_name} comment ({comment}) does not match expected host '{expected_host}'")
        return

    try:
        # Get passphrase from gopass
        result = subprocess.run(
            ["gopass", "show", gopass_path],
            capture_output=True,
            check=True,
            text=True
        )
        passphrase = result.stdout.strip()

        # Use pexpect to simulate interactive passphrase entry
        child = pexpect.spawn(f"ssh-add {key_path}")
        child.expect("Enter passphrase for.*:")
        child.sendline(passphrase)
        child.expect(pexpect.EOF)

        if child.exitstatus == 0:
            print(f"✅ Unlocked {key_name}")
        else:
            print(f"❌ Failed to unlock {key_name}: exit {child.exitstatus}")

    except subprocess.CalledProcessError as e:
        print(f"❌ Gopass error for {gopass_path}: {e.stderr.strip()}")
    except pexpect.ExceptionPexpect as e:
        print(f"❌ pexpect error for {key_name}: {e}")

def main():
    parser = argparse.ArgumentParser(description="Unlock SSH keys using gopass")
    parser.add_argument(
        "--keys", nargs="+",
        help="One or more SSH key base names to unlock (default: all for this host)",
        choices=list(SSH_KEYS.keys())
    )
    args = parser.parse_args()

    current_host = get_hostname()

    if args.keys:
        selected_keys = args.keys
    else:
        # Only keys matching current host
        selected_keys = [
            key for key, (_, expected_host) in SSH_KEYS.items()
            if expected_host in current_host
        ]

    if not selected_keys:
        print(f"ℹ️  No keys configured for host '{current_host}'")
        return

    for key_name in selected_keys:
        gopass_path, expected_host = SSH_KEYS[key_name]
        unlock_key(key_name, gopass_path, expected_host)

if __name__ == "__main__":
    main()
