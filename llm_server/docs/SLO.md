# Service Level Objectives (SLO)

- Availability (monthly): 99.5%
- Latency (p95): < 800 ms
- Error rate (5xx): < 1%

## Error Budget
- 99.5% -> Monthly allowance downtime -> 3 hours 36 minutes.

## Measurement
- Prometheus: llm_requests_total, llm_request_latency_seconds*
- k6: Benchmark (/healthz)

## Policy
- 50% error budget over then, stop releasing and focus on recovery.
