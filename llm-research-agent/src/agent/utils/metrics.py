from prometheus_client import Counter, Histogram

TOOL_CALL_COUNT = Counter("tool_call_count", "Tool call count", ["tool"])
TOOL_LATENCY = Histogram("tool_latency_seconds", "Tool latency in seconds", ["tool"])
