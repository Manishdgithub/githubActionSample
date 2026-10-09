import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
  vus: 10,
  duration: '10s',
  thresholds: {
    http_req_duration: ['p(95)<200'], // 95% of requests must complete under 200ms
    http_req_failed: ['rate<0.01'],    // Error rate must be less than 1%
  },
};

export default function () {
  const res = http.get('http://localhost:8000/healthz');
  check(res, {
    'status is 200': (r) => r.status === 200,
    'healthy body': (r) => r.json().status === 'healthy',
  });
  sleep(0.1);
}
