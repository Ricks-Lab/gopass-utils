# gopass_utils

A set of utilities to manage secrets with [Gopass](https://www.gopass.pw/) and extract them as needed.

This module is designed for use in Python projects that require secure, runtime access to secrets such as database passwords, API tokens, or configuration blobs.

## Features

-  Securely fetch secrets from Gopass CLI
-  Supports environment-scoped secrets (e.g. `dev/`, `prod/`)
-  In-memory caching (optional)
-  Easy integration with existing Python logging
-  Supports JSON-formatted secrets

## Installation

In editable mode during development:

```bash
pip install -e .

