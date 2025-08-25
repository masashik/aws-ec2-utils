import http from 'k6/http';
import { check, sleep } from 'k6';

export let options = {
  vus: 20,
  duration: '10m',
  thresholds: {
    http_req_failed: ['rate<0.01'],
    http_req_duration: ['p(95)<800'],
  },
};

export default function () {
  const res = http.get(`${__ENV.BASE_URL}/healthz`);
  check(res, { 'status 200': (r) => r.status === 200 });
  sleep(0.1);
}
