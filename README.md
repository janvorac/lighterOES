# lighterOES
How hot is your plasma? Find out with molecular pyrometry.

## How to develop and contribute

Requirements:
- Python 3.11.4

install both requirements.txt + requirements_dev.txt

## How to add packages
pip-tools to have pip-compile and use

```
pip-compile requirements.in
```

to generate requiremets.txt - this is slightly better than pip freeze as you also know what came from what

## Use pre-commit

'pre-commit' is nice tool to ensure one does not commit crap

```
pre-commit install
```
