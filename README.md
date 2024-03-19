# poetry-patches

A patches plugin for Poetry.

## Installation

To install this plugin, run:

```sh
pipx inject poetry poetry-patches
```

Check the [docs](https://python-poetry.org/docs/plugins/#using-plugins) for more info.

## Usage

Add `[tool.poetry-patches]` to `pyproject.toml`.

```toml
[tool.poetry-patches]
django = ["patches/django/mypatch.diff"]
```

## Commands

- `poetry patches apply`
- `poetry patches revert`
