# MP2 Data Processing API

This FastAPI application uploads CSV datasets into in-memory storage, retrieves their rows, and validates and cleans them using the reusable MP1 data pipeline. The processing endpoint can remove invalid numeric values, duplicate rows, missing values, and outliers. Request middleware logs method, path, status, duration, and a unique request ID returned in the `X-Request-ID` header.

## Run

```bash
python -m pip install -r requirements.txt
python -m uvicorn main:app --reload
```

Open `http://127.0.0.1:8000/docs` to use the interactive API. Data is kept in memory and resets when the server restarts.

## Endpoints

| Method | Path | Purpose |
| --- | --- | --- |
| GET | `/health` | Check application status. |
| POST | `/upload` | Upload a CSV file and receive its dataset ID and metadata. |
| GET | `/datasets/{dataset_id}` | Retrieve up to `limit` rows and the stored row count. |
| POST | `/datasets/{dataset_id}/process` | Validate and process the dataset in place; return a cleaning report. |

For a fresh upload of `fixtures/sample_data.csv`, send this JSON to `/datasets/1/process` using the ID returned by `/upload`:

```json
{
  "validation": {
    "required_columns": ["student_id", "score"],
    "numeric_columns": ["score"]
  },
  "processing": {
    "remove_duplicates": true,
    "missing": {"enabled": true, "axis": "rows"},
    "outliers": {"enabled": false, "columns": [], "method": "iqr", "threshold": 1.5}
  }
}
```

The report shows one row removed during validation and two during cleaning, leaving three stored rows. Upload the sample again before repeating that workflow.

## Tests

```bash
python -m pytest tests -v
```
