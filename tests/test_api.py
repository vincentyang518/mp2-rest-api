def test_upload_csv(client, sample_csv_bytes):
    response = client.post(
        "/upload",
        files={"file": ("sample_data.csv", sample_csv_bytes, "text/csv")},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["rows"] == 6
    assert data["columns"] == 2
    assert isinstance(data["id"], int) and data["id"] > 0


def test_process_and_retrieve(client, uploaded_dataset_id, processing_body):
    response = client.post(
        f"/datasets/{uploaded_dataset_id}/process",
        json=processing_body,
    )
    assert response.status_code == 200
    report = response.json()
    assert report["validation_rows_removed"] == 1
    assert report["cleaning_report"] == {
        "rows_before": 5,
        "rows_after": 3,
        "rows_removed": 2,
        "columns_before": 2,
        "columns_after": 2,
        "columns_removed": 0,
    }

    retrieved = client.get(f"/datasets/{uploaded_dataset_id}")
    assert retrieved.status_code == 200
    data = retrieved.json()
    assert data["total_rows"] == 3
    assert data["data"] == [
        {"student_id": 1, "score": 80},
        {"student_id": 2, "score": 90},
        {"student_id": 5, "score": 85},
    ]


def test_retrieve_missing_dataset(client):
    response = client.get("/datasets/999")
    assert response.status_code == 404


def test_processing_error_preserves_dataset(
    client, uploaded_dataset_id, processing_body
):
    processing_body["processing"]["outliers"].update(
        enabled=True, columns=["score"], method="unsupported"
    )
    response = client.post(
        f"/datasets/{uploaded_dataset_id}/process", json=processing_body
    )
    assert response.status_code == 400
    assert "Unsupported outlier method" in response.json()["detail"]
    retrieved = client.get(f"/datasets/{uploaded_dataset_id}")
    assert retrieved.json()["total_rows"] == 6


def test_request_ids_on_success_and_error(client):
    success = client.get("/health")
    error = client.get("/datasets/999")
    ids = [response.headers.get("X-Request-ID") for response in (success, error)]
    assert all(request_id and len(request_id) == 8 for request_id in ids)
    assert ids[0] != ids[1]
