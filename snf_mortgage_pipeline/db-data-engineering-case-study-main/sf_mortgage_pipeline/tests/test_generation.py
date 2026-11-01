import csv
import json
import runpy

def test_generator_outputs_synthetic_files(tmp_path, monkeypatch):
    # Generator is script-style; test in isolated copied package directory.
    from pathlib import Path
    source = Path(__file__).resolve().parents[1] / "ingestion/generate_data.py"
    package = tmp_path / "ingestion"
    package.mkdir()
    target = package / "generate_data.py"
    target.write_text(source.read_text())
    runpy.run_path(str(target), run_name="__main__")
    assert json.loads((tmp_path / "data/mortgage_applications.json").read_text())
    with (tmp_path / "data/credit_bureau.csv").open() as f:
        assert list(csv.DictReader(f))
