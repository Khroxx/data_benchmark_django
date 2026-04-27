from __future__ import annotations

from datetime import datetime, timezone
from statistics import median
from time import perf_counter

from django.http import HttpRequest, HttpResponseNotAllowed, JsonResponse


DEFAULT_RUNS = 1


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

    if payload_type == "flat-json":
        return pad_content(
            '{"id":1,"name":"benchmark-entry","status":"ok","category":"flat","active":true,"score":12345}',
            target_bytes,
        )
    if payload_type == "nested-json":
        return pad_content(
            '{"meta":{"name":"benchmark","version":1},"items":[{"id":1,"tags":["alpha","beta"],"payload":{"kind":"nested","enabled":true,"metrics":{"count":3,"value":42}}}]}',
            target_bytes,
        )
    if payload_type == "csv":
        return pad_content(
            "id,name,status,value\n1,benchmark,ok,42\n2,runner,ok,84\n",
            target_bytes,
        )
    if payload_type == "blob":
        return pad_content("benchmark-payload-blob-", target_bytes)

    raise ValueError("invalid type query parameter")


def pad_content(base: str, target_bytes: int) -> bytes:
    if target_bytes <= 0:
        return b""

    if len(base) >= target_bytes:
        return base[:target_bytes].encode("utf-8")

    parts: list[str] = []
    current_length = 0
    while current_length < target_bytes:
        remaining = target_bytes - current_length
        if remaining >= len(base):
            parts.append(base)
            current_length += len(base)
            continue

        parts.append(base[:remaining])
        current_length += remaining

    return "".join(parts).encode("utf-8")


def average(values: list[int]) -> float:
    if not values:
        return 0.0
    return sum(values) / len(values)


def first_non_empty(*values: str | None) -> str:
    for value in values:
        if value and value.strip():
            return value.strip()
    return ""
