# gopass_utils

A set of utilities to manage secrets with [Gopass](https://www.gopass.pw/) and extract them as needed.

This module is designed for use in Python projects that require secure, runtime access to
secrets such as database passwords, API tokens, or configuration blobs.

## Features

-  Securely fetch secrets from Gopass CLI
-  Supports environment-scoped secrets (e.g. `dev/`, `prod/`)
-  In-memory caching (optional)
-  Easy integration with existing Python logging
-  Supports JSON-formatted secrets

## Installation

```bash
wget https://github.com/gopasspw/gopass/releases/download/v1.15.15/gopass_1.15.15_linux_amd64.deb
sudo dpkg -i gopass_1.15.15_linux_amd64.deb
```

## New in this Release - v0.4.0
* Use new packaging build env.

## History

## New in this Previos Release - v0.3.0
* Update to use v1.15.15 of gopass.
* Change back to using -o option of gopass.

### New in Previous Release - v0.2.0
* Remove `-o` option in call to gopass.

### New in Previous Release - v0.1.0
* Initial release.
