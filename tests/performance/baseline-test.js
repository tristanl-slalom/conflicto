// k6 Performance Baseline Test for Conflicto
// Tests basic performance characteristics of the deployed application

import http from 'k6/http';
import { check, sleep } from 'k6';
import { Rate } from 'k6/metrics';

// Custom metrics
let errorRate = new Rate('errors');

export let options = {
  stages: [
    { duration: '2m', target: 10 },   // Ramp up to 10 users over 2 minutes
    { duration: '5m', target: 10 },   // Stay at 10 users for 5 minutes
    { duration: '2m', target: 20 },   // Ramp up to 20 users over 2 minutes
    { duration: '3m', target: 20 },   // Stay at 20 users for 3 minutes
    { duration: '2m', target: 0 },    // Ramp down over 2 minutes
  ],

  thresholds: {
    http_req_duration: ['p(95)<500'],  // 95% of requests under 500ms
    http_req_failed: ['rate<0.1'],     // Error rate under 10%
    errors: ['rate<0.1'],              // Custom error rate under 10%
  },
};

const BASE_URL = __ENV.TEST_BASE_URL || 'http://localhost:8000';

export function setup() {
  console.log(`Starting performance test against: ${BASE_URL}`);

  // Verify the service is responding before starting the test
  let response = http.get(`${BASE_URL}/api/v1/health/`);
  if (response.status !== 200) {
    throw new Error(`Service not ready. Health check returned: ${response.status}`);
  }

  console.log('Service health verified, starting performance test...');
}

export default function () {
  let responses = {};

  // Test 1: Health Check (lightweight endpoint)
  responses.health = http.get(`${BASE_URL}/api/v1/health/`);

  let healthCheckOk = check(responses.health, {
    'health check status is 200': (r) => r.status === 200,
    'health check response time < 200ms': (r) => r.timings.duration < 200,
    'health check returns healthy status': (r) => {
      try {
        let body = JSON.parse(r.body);
        return body.status === 'healthy';
      } catch (e) {
        return false;
      }
    },
  });

  errorRate.add(!healthCheckOk);

  // Test 2: Session List (database query)
  responses.sessionList = http.get(`${BASE_URL}/api/v1/sessions/`);

  let sessionListOk = check(responses.sessionList, {
    'session list status is 200': (r) => r.status === 200,
    'session list response time < 1000ms': (r) => r.timings.duration < 1000,
    'session list returns array': (r) => {
      try {
        let body = JSON.parse(r.body);
        return Array.isArray(body);
      } catch (e) {
        return false;
      }
    },
  });

  errorRate.add(!sessionListOk);

  // Test 3: Session Creation (write operation) - only for some users
  if (Math.random() < 0.3) {  // 30% of users create sessions
    let sessionData = {
      name: `Load Test Session ${__VU}-${__ITER}`,
      description: `Performance test session created by VU ${__VU} at iteration ${__ITER}`
    };

    responses.sessionCreate = http.post(
      `${BASE_URL}/api/v1/sessions/`,
      JSON.stringify(sessionData),
      {
        headers: {
          'Content-Type': 'application/json',
        },
      }
    );

    let sessionCreateOk = check(responses.sessionCreate, {
      'session creation status is 201': (r) => r.status === 201,
      'session creation response time < 2000ms': (r) => r.timings.duration < 2000,
      'session creation returns session object': (r) => {
        try {
          let body = JSON.parse(r.body);
          return body.id && body.name === sessionData.name;
        } catch (e) {
          return false;
        }
      },
    });

    errorRate.add(!sessionCreateOk);

    // If session was created successfully, clean it up
    if (responses.sessionCreate.status === 201) {
      try {
        let createdSession = JSON.parse(responses.sessionCreate.body);
        let deleteResponse = http.del(`${BASE_URL}/api/v1/sessions/${createdSession.id}`);

        check(deleteResponse, {
          'session deletion status is 204': (r) => r.status === 204,
        });
      } catch (e) {
        console.error(`Failed to cleanup session: ${e}`);
      }
    }
  }

  // Realistic pause between requests (1-3 seconds)
  sleep(Math.random() * 2 + 1);
}

export function teardown(data) {
  console.log('Performance test completed');

  // Final health check to ensure service is still responsive
  let response = http.get(`${BASE_URL}/api/v1/health/`);

  if (response.status === 200) {
    console.log('Service still healthy after performance test');
  } else {
    console.error(`Service health check failed after test: ${response.status}`);
  }
}
