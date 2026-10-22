"""In-memory storage for uploaded datasets."""

import logging

import pandas as pd

logger = logging.getLogger(__name__)


class DatasetStorage:
    def __init__(self):
        self._store: dict[int, tuple[str, pd.DataFrame]] = {}
        self._counter = 0

    def save(self, df: pd.DataFrame, filename: str) -> int:
        """Store a copy of the data and return a new integer ID."""
        self._counter += 1
        dataset_id = self._counter
        self._store[dataset_id] = (filename, df.copy(deep=True))
        logger.debug("Stored dataset: id=%s, rows=%s", dataset_id, len(df))
        return dataset_id

    def get(self, dataset_id: int) -> pd.DataFrame | None:
        """Return a copy of the stored DataFrame, or None."""
        entry = self._store.get(dataset_id)
        if entry is None:
            logger.debug("Dataset not found in storage: id=%s", dataset_id)
            return None
        df = entry[1].copy(deep=True)
        logger.debug("Retrieved dataset copy: id=%s, rows=%s", dataset_id, len(df))
        return df

    def get_metadata(self, dataset_id: int) -> dict | None:
        """Return metadata calculated from the current dataset, or None."""
        entry = self._store.get(dataset_id)
        if entry is None:
            logger.debug("Dataset metadata not found: id=%s", dataset_id)
            return None
        filename, df = entry
        metadata = {
            "id": dataset_id,
            "filename": filename,
            "rows": len(df),
            "columns": len(df.columns),
            "column_names": list(df.columns),
        }
        logger.debug("Retrieved dataset metadata: id=%s", dataset_id)
        return metadata

    def update(self, dataset_id: int, df: pd.DataFrame) -> bool:
        """Replace an existing dataset; return True, or False if missing."""
        entry = self._store.get(dataset_id)
        if entry is None:
            logger.debug("Dataset update failed: id=%s", dataset_id)
            return False
        self._store[dataset_id] = (entry[0], df.copy(deep=True))
        logger.debug("Updated dataset: id=%s, rows=%s", dataset_id, len(df))
        return True

    def clear(self) -> None:
        """Clear all data and reset the ID counter."""
        self._store.clear()
        self._counter = 0
        logger.debug("Cleared dataset storage")
