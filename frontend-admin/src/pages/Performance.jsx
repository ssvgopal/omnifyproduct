import React from 'react';
import { Card, CardHeader, CardTitle, CardContent, Table, TableHeader, TableBody, TableRow, TableHead, TableCell } from '@omnify/shared-ui';
import { Gauge, TrendingUp } from 'lucide-react';

const Performance = () => {
  const topEndpoints = [
    { endpoint: '/api/attribution/unified', requests: 12453, avgTime: 125, p95: 234 },
    { endpoint: '/api/oracle/alerts', requests: 8921, avgTime: 89, p95: 156 },
    { endpoint: '/api/curiosity/recommendations', requests: 6543, avgTime: 156, p95: 289 },
    { endpoint: '/api/workflows/execute', requests: 4321, avgTime: 234, p95: 456 }
  ];

  return (
    <div className="p-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Performance Monitoring</h1>
        <p className="text-gray-600">API performance metrics and bottleneck analysis</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm text-gray-600">Avg Response Time</span>
              <Gauge className="h-5 w-5 text-blue-500" />
            </div>
            <div className="text-2xl font-bold">125ms</div>
            <div className="text-sm text-green-600 mt-1">↓ 12% vs last week</div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm text-gray-600">Total Requests</span>
              <TrendingUp className="h-5 w-5 text-green-500" />
            </div>
            <div className="text-2xl font-bold">45,231</div>
            <div className="text-sm text-gray-600 mt-1">Last 24 hours</div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm text-gray-600">Slow Requests</span>
              <Gauge className="h-5 w-5 text-orange-500" />
            </div>
            <div className="text-2xl font-bold">12</div>
            <div className="text-sm text-gray-600 mt-1">&gt;1s response time</div>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Top Endpoints</CardTitle>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Endpoint</TableHead>
                <TableHead>Requests</TableHead>
                <TableHead>Avg Time</TableHead>
                <TableHead>P95 Time</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {topEndpoints.map((endpoint, index) => (
                <TableRow key={index}>
                  <TableCell className="font-mono text-sm">{endpoint.endpoint}</TableCell>
                  <TableCell>{endpoint.requests.toLocaleString()}</TableCell>
                  <TableCell>{endpoint.avgTime}ms</TableCell>
                  <TableCell>{endpoint.p95}ms</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </div>
  );
};

export default Performance;
