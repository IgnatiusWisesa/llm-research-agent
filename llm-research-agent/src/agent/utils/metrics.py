from prometheus_client import Counter, Histogram

# ✅ Counts how many times each tool (e.g., generate_queries, web_search) has been called
TOOL_CALL_COUNT = Counter(
    "tool_call_count",             # Metric name shown in Prometheus
    "Tool call count",             # Description of what this metric measures
    ["tool"]                       # Labels: one for each tool name
)

# ⏱️ Measures how long each tool takes to run (in seconds), as a histogram
TOOL_LATENCY = Histogram(
    "tool_latency_seconds",        # Metric name for latency
    "Tool latency in seconds",     # Description shown in Prometheus
    ["tool"]                       # Label by tool name for granularity
)
