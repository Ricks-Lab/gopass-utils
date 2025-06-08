#!/usr/bin/env python3

import argparse
import pprint
import subprocess
from pathlib import Path
import pexpect
import socket
import tomllib

from gopass_utils import gu_logger

SSH_DIR = Path.home() / ".ssh"
CONFIG_FILE = SSH_DIR / "ssh_unlock_config.toml"
LOGGER = gu_logger.configure_logger(__name__, stream=True)

def get_hostname() -> str:
    """ Get the hostname for system.

    :return: Hostname as a string
    """
    return socket.gethostname().lower()


def load_config_toml(config_path: str = CONFIG_FILE) -> dict:
    """ Read the database configuration file and return it as a dictionary.

    :param config_path: Full path to the configuration file as string.
    :return: Configuration dictionary.
    """
    hostname = get_hostname()
    try_config_paths = (config_path, ) if config_path else (CONFIG_FILE, )
    for try_config_path in try_config_paths:
        try:
            with open(try_config_path, mode="rb") as f:
                config = tomllib.load(f)
            LOGGER.debug("Loaded %s: %s", try_config_path, config)
            return config["ssh_keys"]
        except FileNotFoundError:
            LOGGER.info("FileNotFoundError: %s", try_config_path)
            continue
        except KeyError:
            LOGGER.info("KeyError: %s missing [%s] entry", try_config_path, "ssh_keys")
            continue
        except Exception as e:
            raise RuntimeError("Unexpected Error loading SSH config") from e
    raise RuntimeError("Failed to load SSH config")


# Key name → Gopass path → Expected comment (e.g., hostname or system)
SSH_KEYS: dict = load_config_toml()
LOGGER.debug("Loaded: %s", pprint.pprint(SSH_KEYS))

def is_key_loaded(key_path: Path) -> bool:
    """ Check if a key is loaded.

    :param key_path: path to the key file.
    :return: True if the key is loaded, False otherwise.
    """
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
    """ Get the comment for a key.

    :param key_path: path to the key file.
    :return: comment as a string
    """
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

def unlock_key(key_name: str, gopass_path: str, expected_host: str) -> None:
    """ Unlock the key defined by `key_name` and gopass path.

    :param key_name: Name of the key file to unlock.
    :param gopass_path: The gopass path of the key file to unlock.
    :param expected_host:  The host name of the key file to unlock.
    """
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
    LOGGER.info("Current host: %s", current_host)

    if args.keys:
        selected_keys = args.keys
    else:
        # Only keys matching current host
        selected_keys = [
            key for key, meta in SSH_KEYS.items()
            if meta["host"] in current_host
        ]

    if not selected_keys:
        print(f"ℹ️  No keys configured for host '{current_host}'")
        return

    for key_name in selected_keys:
        key_data = SSH_KEYS[key_name]
        gopass_path = key_data["path"]
        expected_host = key_data["host"]
        unlock_key(key_name, gopass_path, expected_host)


if __name__ == "__main__":
    main()
