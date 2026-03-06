from prometheus_client import start_http_server, Gauge
import time

# Metrics
risk_score = Gauge("service_risk_score", "Risk score per service", ["service"])
drift_count = Gauge("policy_drift_count", "Number of drift violations")

def run_metrics():
    # Example values (from your risk engine)
    risk_score.labels("frontend").set(30)
    risk_score.labels("backend").set(30)
    risk_score.labels("database").set(90)

    drift_count.set(1)

    # Start metrics server
    start_http_server(8000)
    print("📊 Metrics exposed on :8000/metrics")

    while True:
        time.sleep(10)

if __name__ == "__main__":
    run_metrics()
