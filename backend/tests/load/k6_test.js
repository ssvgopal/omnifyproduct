/**
 * Load Testing with k6
 * Run with: k6 run backend/tests/load/k6_test.js
 */

import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
    stages: [
        { duration: '30s', target: 20 },  // Ramp up to 20 users
        { duration: '1m', target: 20 },    // Stay at 20 users
        { duration: '30s', target: 50 },  // Ramp up to 50 users
        { duration: '1m', target: 50 },   // Stay at 50 users
        { duration: '30s', target: 0 },    // Ramp down
    ],
    thresholds: {
        http_req_duration: ['p(95)<500'],  // 95% of requests should be below 500ms
        http_req_failed: ['rate<0.01'],     // Error rate should be less than 1%
    },
};

const BASE_URL = __ENV.BASE_URL || 'http://localhost:8000';

export default function () {
    // Login
    const loginRes = http.post(`${BASE_URL}/api/auth/login`, JSON.stringify({
        email: `loadtest${Math.floor(Math.random() * 1000)}@example.com`,
        password: 'LoadTest123!'
    }), {
        headers: { 'Content-Type': 'application/json' },
    });
    
    check(loginRes, {
        'login successful': (r) => r.status === 200,
    });
    
    const token = loginRes.json('access_token');
    
    if (!token) {
        return;
    }
    
    const headers = {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
    };
    
    // View dashboard
    const dashboardRes = http.get(`${BASE_URL}/api/dashboard`, { headers });
    check(dashboardRes, {
        'dashboard loaded': (r) => r.status === 200,
    });
    
    // List campaigns
    const campaignsRes = http.get(`${BASE_URL}/api/campaigns`, { headers });
    check(campaignsRes, {
        'campaigns listed': (r) => r.status === 200,
    });
    
    sleep(1);
}

