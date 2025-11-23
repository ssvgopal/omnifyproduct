'use client';

import { useState, useEffect } from 'react';
import { Activity, AlertCircle, CheckCircle, TrendingUp, TrendingDown, Database, Server, Zap } from 'lucide-react';

export default function VendorMonitoringPage() {
  const [metrics, setMetrics] = useState({
    apiResponseTime: 145,
    errorRate: 0.03,
    activeUsers: 234,
    syncJobsRunning: 12,
    databaseSize: '2.4 GB',
    uptime: 99.98,
  });

  return (
    <div>
      <div className="mb-8">
        <h1 className="text-3xl font-bold mb-2">System Monitoring</h1>
        <p className="text-slate-400">Real-time system health and performance metrics</p>
      </div>

      {/* System Health Status */}
      <div className="bg-slate-800 p-6 rounded-lg border border-slate-700 mb-8">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <div className="w-4 h-4 bg-green-500 rounded-full animate-pulse"></div>
            <div>
              <p className="text-xl font-bold">All Systems Operational</p>
              <p className="text-sm text-slate-400">Last checked: 30 seconds ago</p>
            </div>
          </div>
          <div className="flex items-center gap-2 px-4 py-2 bg-green-500/20 text-green-300 rounded-lg">
            <CheckCircle className="h-5 w-5" />
            <span className="font-medium">{metrics.uptime}% Uptime</span>
          </div>
        </div>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-4 gap-6 mb-8">
        <div className="bg-slate-800 p-6 rounded-lg border border-slate-700">
          <div className="flex items-center justify-between mb-4">
            <div className="p-2 bg-blue-500/20 rounded-lg">
              <Zap className="h-6 w-6 text-blue-400" />
            </div>
            <TrendingDown className="h-5 w-5 text-green-400" />
          </div>
          <p className="text-sm text-slate-400 mb-1">API Response Time</p>
          <p className="text-3xl font-bold">{metrics.apiResponseTime}ms</p>
          <p className="text-xs text-green-400 mt-2">-15ms from last hour</p>
        </div>

        <div className="bg-slate-800 p-6 rounded-lg border border-slate-700">
          <div className="flex items-center justify-between mb-4">
            <div className="p-2 bg-red-500/20 rounded-lg">
              <AlertCircle className="h-6 w-6 text-red-400" />
            </div>
            <TrendingUp className="h-5 w-5 text-red-400" />
          </div>
          <p className="text-sm text-slate-400 mb-1">Error Rate</p>
          <p className="text-3xl font-bold">{metrics.errorRate}%</p>
          <p className="text-xs text-red-400 mt-2">+0.01% from last hour</p>
        </div>

        <div className="bg-slate-800 p-6 rounded-lg border border-slate-700">
          <div className="flex items-center justify-between mb-4">
            <div className="p-2 bg-green-500/20 rounded-lg">
              <Activity className="h-6 w-6 text-green-400" />
            </div>
            <TrendingUp className="h-5 w-5 text-green-400" />
          </div>
          <p className="text-sm text-slate-400 mb-1">Active Users</p>
          <p className="text-3xl font-bold">{metrics.activeUsers}</p>
          <p className="text-xs text-green-400 mt-2">+23 from last hour</p>
        </div>

        <div className="bg-slate-800 p-6 rounded-lg border border-slate-700">
          <div className="flex items-center justify-between mb-4">
            <div className="p-2 bg-purple-500/20 rounded-lg">
              <Server className="h-6 w-6 text-purple-400" />
            </div>
            <Activity className="h-5 w-5 text-purple-400" />
          </div>
          <p className="text-sm text-slate-400 mb-1">Sync Jobs Running</p>
          <p className="text-3xl font-bold">{metrics.syncJobsRunning}</p>
          <p className="text-xs text-slate-400 mt-2">3 queued</p>
        </div>
      </div>

      {/* Service Status */}
      <div className="grid grid-cols-2 gap-6 mb-8">
        <div className="bg-slate-800 p-6 rounded-lg border border-slate-700">
          <h2 className="text-lg font-bold mb-4">Service Status</h2>
          <div className="space-y-3">
            {[
              { name: 'API Gateway', status: 'operational', latency: '45ms' },
              { name: 'Brain Compute Service', status: 'operational', latency: '234ms' },
              { name: 'Database (Primary)', status: 'operational', latency: '12ms' },
              { name: 'Database (Replica)', status: 'operational', latency: '15ms' },
              { name: 'Queue Service', status: 'operational', latency: '8ms' },
              { name: 'Auth Service', status: 'degraded', latency: '156ms' },
            ].map((service) => (
              <div key={service.name} className="flex items-center justify-between p-3 bg-slate-900 rounded-lg">
                <div className="flex items-center gap-3">
                  <div
                    className={`w-2 h-2 rounded-full ${
                      service.status === 'operational' ? 'bg-green-500' : 'bg-yellow-500'
                    }`}
                  />
                  <p className="font-medium">{service.name}</p>
                </div>
                <div className="flex items-center gap-4">
                  <p className="text-sm text-slate-400">{service.latency}</p>
                  <span
                    className={`px-2 py-1 rounded text-xs font-medium ${
                      service.status === 'operational'
                        ? 'bg-green-500/20 text-green-300'
                        : 'bg-yellow-500/20 text-yellow-300'
                    }`}
                  >
                    {service.status}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="bg-slate-800 p-6 rounded-lg border border-slate-700">
          <h2 className="text-lg font-bold mb-4">Recent Events</h2>
          <div className="space-y-3">
            {[
              { type: 'info', message: 'Scheduled maintenance completed', time: '10 minutes ago' },
              { type: 'warning', message: 'High API usage detected for client "Acme"', time: '1 hour ago' },
              { type: 'success', message: 'Database backup completed', time: '2 hours ago' },
              { type: 'error', message: 'Failed sync job for "Demo Beauty Co"', time: '3 hours ago' },
              { type: 'info', message: 'New client onboarded: "TechStart Inc"', time: '5 hours ago' },
            ].map((event, idx) => (
              <div key={idx} className="flex items-start gap-3 p-3 bg-slate-900 rounded-lg">
                <div
                  className={`p-1 rounded ${
                    event.type === 'success'
                      ? 'bg-green-500/20 text-green-400'
                      : event.type === 'error'
                      ? 'bg-red-500/20 text-red-400'
                      : event.type === 'warning'
                      ? 'bg-yellow-500/20 text-yellow-400'
                      : 'bg-blue-500/20 text-blue-400'
                  }`}
                >
                  <Activity className="h-4 w-4" />
                </div>
                <div className="flex-1">
                  <p className="text-sm">{event.message}</p>
                  <p className="text-xs text-slate-400 mt-1">{event.time}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Infrastructure */}
      <div className="bg-slate-800 p-6 rounded-lg border border-slate-700">
        <h2 className="text-lg font-bold mb-4">Infrastructure</h2>
        <div className="grid grid-cols-3 gap-6">
          <div className="flex items-center gap-4 p-4 bg-slate-900 rounded-lg">
            <Database className="h-8 w-8 text-blue-400" />
            <div>
              <p className="text-sm text-slate-400">Database Size</p>
              <p className="text-xl font-bold">{metrics.databaseSize}</p>
            </div>
          </div>
          <div className="flex items-center gap-4 p-4 bg-slate-900 rounded-lg">
            <Server className="h-8 w-8 text-purple-400" />
            <div>
              <p className="text-sm text-slate-400">API Servers</p>
              <p className="text-xl font-bold">3 active</p>
            </div>
          </div>
          <div className="flex items-center gap-4 p-4 bg-slate-900 rounded-lg">
            <Zap className="h-8 w-8 text-amber-400" />
            <div>
              <p className="text-sm text-slate-400">Compute Units</p>
              <p className="text-xl font-bold">245 / 1000</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
