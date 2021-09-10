python3 -m mypy -p Nodes --disallow-untyped-calls --ignore-missing-imports
python3 -m mypy -p Server --disallow-untyped-calls --ignore-missing-imports
python3 -m pytest
