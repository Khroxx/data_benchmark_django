from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from statistics import median
from time import perf_counter

from django.http import HttpRequest, HttpResponseNotAllowed, JsonResponse


DEFAULT_RUNS = 1
BENCHMARK_DATA_DIR = Path(__file__).resolve().parent.parent / "benchmark_data"
PAYLOAD_FILES = {
    "flat-json": "flat.json",
    "nested-json": "nested.json",
    "csv": "table.csv",
    "blob": "blob.txt",
}


def benchmark_view(request: HttpRequest) -> JsonResponse | HttpResponseNotAllowed:
    if request.method != "GET":
        return HttpResponseNotAllowed(["GET"])

    payload_type = (request.GET.get("type") or "").strip()
    if not payload_type:
        return JsonResponse({"error": "missing type query parameter"}, status=400)

    size_kb_raw = first_non_empty(request.GET.get("sizeKb"), request.GET.get("size"))
    if not size_kb_raw:
        return JsonResponse({"error": "missing sizeKb query parameter"}, status=400)

    try:
        size_kb = int(size_kb_raw)
        if size_kb < 1:
            raise ValueError
    except ValueError:
        return JsonResponse({"error": "invalid sizeKb query parameter"}, status=400)

    runs, warnings = parse_runs(request.GET.get("runs", ""))
    durations: list[int] = []
    payload = b""

    for _ in range(runs):
        start = perf_counter()
        try:
            payload = generate_payload(payload_type, size_kb)
        except ValueError as exc:
            return JsonResponse({"error": str(exc)}, status=400)
        durations.append(int((perf_counter() - start) * 1000))

    response = {
        "type": payload_type,
        "sizeKb": size_kb,
        "runs": runs,
        "durations": durations,
        "average_ms": average(durations),
        "median_ms": float(median(durations)) if durations else 0.0,
        "data_bytes": len(payload),
        "generated": True,
        "server_time": datetime.now(timezone.utc).isoformat(),
        "warnings": warnings,
    }

    if not warnings:
        response.pop("warnings")

    return JsonResponse(response)


def parse_runs(raw_runs: str) -> tuple[int, list[str]]:
    raw_runs = raw_runs.strip()
    if not raw_runs:
        return DEFAULT_RUNS, []

    try:
        runs = int(raw_runs)
        if runs < 1:
            raise ValueError
    except ValueError:
        return DEFAULT_RUNS, ["invalid runs value, defaulted to 1"]

    return runs, []


def generate_payload(payload_type: str, size_kb: int) -> bytes:
    target_bytes = size_kb * 1024
    return repeat_bytes(load_payload_fixture(payload_type), target_bytes)


def load_payload_fixture(payload_type: str) -> bytes:
    file_name = PAYLOAD_FILES.get(payload_type)
    if not file_name:
        raise ValueError("invalid type query parameter")

    path = BENCHMARK_DATA_DIR / file_name
    try:
        return path.read_bytes()
    except OSError as exc:
        raise ValueError(f"benchmark data file not found: {file_name}") from exc


def repeat_bytes(base: bytes, target_bytes: int) -> bytes:
    if target_bytes <= 0:
        return b""

    if not base:
        return b"\0" * target_bytes

    parts: list[bytes] = []
    current_length = 0
    while current_length < target_bytes:
        remaining = target_bytes - current_length
        if remaining >= len(base):
            parts.append(base)
            current_length += len(base)
            continue

        parts.append(base[:remaining])
        current_length += remaining

    return b"".join(parts)


def average(values: list[int]) -> float:
    if not values:
        return 0.0
    return sum(values) / len(values)


def first_non_empty(*values: str | None) -> str:
    for value in values:
        if value and value.strip():
            return value.strip()
    return ""
