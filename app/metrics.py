from prometheus_client import Counter, Histogram

REQUESTS = Counter("cost_optimizer_requests_total", "Total API requests", ["endpoint"])
ANOMALIES = Counter("cost_optimizer_anomalies_total", "Detected anomalies")
ANALYSIS_LATENCY = Histogram("cost_optimizer_analysis_seconds", "Analysis latency in seconds")
