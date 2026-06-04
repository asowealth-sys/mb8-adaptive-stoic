from __future__ import annotations

from pathlib import Path
from typing import BinaryIO

import pandas as pd


def read_dataset(path_or_buffer: str | Path | BinaryIO, filename: str | None = None) -> pd.DataFrame:
    suffix = Path(filename or str(path_or_buffer)).suffix.lower()
    if suffix == ".csv":
        return pd.read_csv(path_or_buffer)
    if suffix in {".xls", ".xlsx"}:
        return pd.read_excel(path_or_buffer)
    raise ValueError("Unsupported dataset format. Upload CSV, XLS, or XLSX.")

