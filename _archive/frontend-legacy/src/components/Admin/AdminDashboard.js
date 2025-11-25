/**
 * Admin Dashboard for OmnifyProduct
 * Comprehensive log analysis and client support interface
 */

import React, { useState, useEffect } from 'react';
import { logger } from '../../services/logger';
import api from '../../services/api';
import './AdminDashboard.css';

const AdminDashboard = () => {
  const [activeTab, setActiveTab] = useState('overview');
  const [logs, setLogs] = useState([]);
  const [systemHealth, setSystemHealth] = useState(null);
  const [workflowStats, setWorkflowStats] = useState(null);
  const [performanceMetrics, setPerformanceMetrics] = useState(null);
  const [loading, setLoading] = useState(true);
  const [filters, setFilters] = useState({
    level: 'ALL',
    timeRange: '1h',
    userId: '',
    workflowId: '',
    search: ''
  });

  useEffect(() => {
    logger.trackPageView('admin_dashboard');
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      setLoading(true);

      // Load all dashboard data in parallel
      const [healthData, workflowData, performanceData, logsData] = await Promise.all([
        api.getSystemHealth(),
        api.getWorkflowStats(),
        api.getPerformanceMetrics(),
        api.getLogs(filters)
      ]);

      setSystemHealth(healthData);
      setWorkflowStats(workflowData);
      setPerformanceMetrics(performanceData);
      setLogs(logsData.logs || []);

      logger.info('Admin dashboard data loaded successfully');
    } catch (error) {
      logger.error('Failed to load admin dashboard data', error);
    } finally {
      setLoading(false);
    }
  };

  const handleFilterChange = async (newFilters) => {
    const updatedFilters = { ...filters, ...newFilters };
    setFilters(updatedFilters);

    try {
      const logsData = await api.getLogs(updatedFilters);
      setLogs(logsData.logs || []);
    } catch (error) {
      logger.error('Failed to filter logs', error);
    }
  };

  const handleClientIssueAnalysis = async (clientId, issueDescription) => {
    try {
      logger.trackUserAction('analyze_client_issue', { clientId });
      const analysis = await api.analyzeClientIssue(clientId, issueDescription);

      // Show analysis results
      alert(`Analysis complete. Found ${analysis.total_logs} relevant logs. Check console for details.`);
      console.log('Client Issue Analysis:', analysis);

      return analysis;
    } catch (error) {
      logger.error('Failed to analyze client issue', error, { clientId });
      alert('Failed to analyze client issue. Check console for details.');
    }
  };

  if (loading) {
    return (
      <div className="admin-dashboard loading">
        <div className="loading-spinner">Loading dashboard...</div>
      </div>
    );
  }

  return (
    <div className="admin-dashboard">
      <header className="dashboard-header">
        <h1>🔍 OmnifyProduct Admin Dashboard</h1>
        <p>Comprehensive system monitoring and client support</p>
      </header>

      <nav className="dashboard-nav">
        <button
          className={activeTab === 'overview' ? 'active' : ''}
          onClick={() => setActiveTab('overview')}
        >
          📊 Overview
        </button>
        <button
          className={activeTab === 'logs' ? 'active' : ''}
          onClick={() => setActiveTab('logs')}
        >
          📋 Logs
        </button>
        <button
          className={activeTab === 'workflows' ? 'active' : ''}
          onClick={() => setActiveTab('workflows')}
        >
          ⚙️ Workflows
        </button>
        <button
          className={activeTab === 'performance' ? 'active' : ''}
          onClick={() => setActiveTab('performance')}
        >
          ⚡ Performance
        </button>
        <button
          className={activeTab === 'support' ? 'active' : ''}
          onClick={() => setActiveTab('support')}
        >
          🎧 Client Support
        </button>
      </nav>

      <main className="dashboard-content">
        {activeTab === 'overview' && (
          <OverviewTab
            systemHealth={systemHealth}
            workflowStats={workflowStats}
            performanceMetrics={performanceMetrics}
            logs={logs}
          />
        )}

        {activeTab === 'logs' && (
          <LogsTab
            logs={logs}
            filters={filters}
            onFilterChange={handleFilterChange}
          />
        )}

        {activeTab === 'workflows' && (
          <WorkflowsTab
            workflowStats={workflowStats}
            logs={logs}
          />
        )}

        {activeTab === 'performance' && (
          <PerformanceTab
            performanceMetrics={performanceMetrics}
            logs={logs}
          />
        )}

        {activeTab === 'support' && (
          <SupportTab
            onAnalyzeIssue={handleClientIssueAnalysis}
            logs={logs}
          />
        )}
      </main>
    </div>
  );
};

// Overview Tab Component
const OverviewTab = ({ systemHealth, workflowStats, performanceMetrics, logs }) => {
  const getHealthStatusColor = (status) => {
    switch (status) {
      case 'healthy': return '#00b894';
      case 'warning': return '#fdcb6e';
      case 'critical': return '#e17055';
      default: return '#636e72';
    }
  };

  return (
    <div className="overview-tab">
      <div className="metrics-grid">
        {/* System Health */}
        <div className="metric-card health-card">
          <h3>System Health</h3>
          <div
            className="health-status"
            style={{ color: getHealthStatusColor(systemHealth?.overall_status) }}
          >
            {systemHealth?.overall_status?.toUpperCase() || 'UNKNOWN'}
          </div>
          <div className="health-details">
            <p>Response Time: {systemHealth?.metrics?.response_time_ms || 0}ms</p>
            <p>Error Rate: {(systemHealth?.metrics?.error_rate * 100 || 0).toFixed(2)}%</p>
          </div>
        </div>

        {/* Workflow Stats */}
        <div className="metric-card workflow-card">
          <h3>Workflow Activity</h3>
          <div className="workflow-numbers">
            <p>Total: {workflowStats?.unique_workflows || 0}</p>
            <p>Completed: {workflowStats?.completed_workflows || 0}</p>
            <p>Success Rate: {workflowStats?.success_rate?.toFixed(1) || 0}%</p>
          </div>
        </div>

        {/* Performance Metrics */}
        <div className="metric-card performance-card">
          <h3>Performance</h3>
          <div className="performance-numbers">
            <p>Avg Response: {performanceMetrics?.avg_response_time || 0}ms</p>
            <p>Total Requests: {performanceMetrics?.total_requests || 0}</p>
            <p>Slow Requests: {performanceMetrics?.slow_requests || 0}</p>
          </div>
        </div>

        {/* Log Summary */}
        <div className="metric-card logs-card">
          <h3>Recent Logs</h3>
          <div className="log-numbers">
            <p>Total: {logs.length}</p>
            <p>Errors: {logs.filter(log => log.level === 'ERROR').length}</p>
            <p>Warnings: {logs.filter(log => log.level === 'WARN').length}</p>
          </div>
        </div>
      </div>

      <div className="recent-activity">
        <h3>Recent Activity</h3>
        <div className="activity-list">
          {logs.slice(0, 10).map((log, index) => (
            <div key={index} className={`activity-item ${log.level.toLowerCase()}`}>
              <span className="timestamp">
                {new Date(log.timestamp).toLocaleTimeString()}
              </span>
              <span className="level">{log.level}</span>
              <span className="message">{log.message}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

// Logs Tab Component
const LogsTab = ({ logs, filters, onFilterChange }) => {
  const [selectedLog, setSelectedLog] = useState(null);

  return (
    <div className="logs-tab">
      <div className="filters-section">
        <div className="filter-group">
          <label>Level:</label>
          <select
            value={filters.level}
            onChange={(e) => onFilterChange({ level: e.target.value })}
          >
            <option value="ALL">All Levels</option>
            <option value="ERROR">Errors</option>
            <option value="WARN">Warnings</option>
            <option value="INFO">Info</option>
            <option value="DEBUG">Debug</option>
          </select>
        </div>

        <div className="filter-group">
          <label>Time Range:</label>
          <select
            value={filters.timeRange}
            onChange={(e) => onFilterChange({ timeRange: e.target.value })}
          >
            <option value="5m">Last 5 minutes</option>
            <option value="1h">Last hour</option>
            <option value="24h">Last 24 hours</option>
            <option value="7d">Last 7 days</option>
          </select>
        </div>

        <div className="filter-group">
          <label>Search:</label>
          <input
            type="text"
            placeholder="Search logs..."
            value={filters.search}
            onChange={(e) => onFilterChange({ search: e.target.value })}
          />
        </div>
      </div>

      <div className="logs-content">
        <div className="logs-list">
          {logs.map((log, index) => (
            <div
              key={index}
              className={`log-item ${log.level.toLowerCase()}`}
              onClick={() => setSelectedLog(log)}
            >
              <div className="log-header">
                <span className="timestamp">
                  {new Date(log.timestamp).toLocaleString()}
                </span>
                <span className={`level ${log.level.toLowerCase()}`}>
                  {log.level}
                </span>
                <span className="event-type">
                  {log.event_type || 'general'}
                </span>
              </div>
              <div className="log-message">{log.message}</div>
              <div className="log-context">
                {log.context?.user_id && <span>User: {log.context.user_id}</span>}
                {log.context?.workflow_id && <span>Workflow: {log.context.workflow_id}</span>}
              </div>
            </div>
          ))}
        </div>

        {selectedLog && (
          <div className="log-details">
            <h3>Log Details</h3>
            <pre>{JSON.stringify(selectedLog, null, 2)}</pre>
            <button onClick={() => setSelectedLog(null)}>Close</button>
          </div>
        )}
      </div>
    </div>
  );
};

// Workflows Tab Component
const WorkflowsTab = ({ workflowStats, logs }) => {
  const workflowLogs = logs.filter(log =>
    log.event_type && log.event_type.includes('workflow')
  );

  return (
    <div className="workflows-tab">
      <div className="workflow-metrics">
        <div className="metric-item">
          <h4>Total Workflows</h4>
          <span className="metric-value">{workflowStats?.unique_workflows || 0}</span>
        </div>
        <div className="metric-item">
          <h4>Success Rate</h4>
          <span className="metric-value">{workflowStats?.success_rate?.toFixed(1) || 0}%</span>
        </div>
        <div className="metric-item">
          <h4>Failed Workflows</h4>
          <span className="metric-value">{workflowStats?.error_workflows || 0}</span>
        </div>
        <div className="metric-item">
          <h4>Avg Completion Time</h4>
          <span className="metric-value">
            {workflowStats?.avg_completion_time ?
              `${workflowStats.avg_completion_time.toFixed(1)}s` : 'N/A'}
          </span>
        </div>
      </div>

      <div className="workflow-activity">
        <h3>Recent Workflow Activity</h3>
        <div className="activity-timeline">
          {workflowLogs.slice(0, 20).map((log, index) => (
            <div key={index} className={`timeline-item ${log.event_type.split('_')[1]}`}>
              <div className="timeline-marker"></div>
              <div className="timeline-content">
                <div className="timeline-header">
                  <span className="event-type">{log.event_type}</span>
                  <span className="timestamp">
                    {new Date(log.timestamp).toLocaleTimeString()}
                  </span>
                </div>
                <div className="timeline-details">
                  <p>{log.message}</p>
                  {log.context?.workflow_id && (
                    <small>Workflow: {log.context.workflow_id}</small>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

// Performance Tab Component
const PerformanceTab = ({ performanceMetrics, logs }) => {
  return (
    <div className="performance-tab">
      <div className="performance-overview">
        <div className="performance-card">
          <h3>API Performance</h3>
          <div className="performance-stats">
            <div className="stat-item">
              <span className="stat-label">Total Requests:</span>
              <span className="stat-value">{performanceMetrics?.total_requests || 0}</span>
            </div>
            <div className="stat-item">
              <span className="stat-label">Avg Response Time:</span>
              <span className="stat-value">{performanceMetrics?.avg_response_time || 0}ms</span>
            </div>
            <div className="stat-item">
              <span className="stat-label">Slow Requests (&gt;1s):</span>
              <span className="stat-value">{performanceMetrics?.slow_requests || 0}</span>
            </div>
          </div>
        </div>

        <div className="performance-card">
          <h3>Top Endpoints</h3>
          <div className="endpoint-list">
            {performanceMetrics?.top_endpoints &&
              Object.entries(performanceMetrics.top_endpoints).map(([endpoint, count]) => (
                <div key={endpoint} className="endpoint-item">
                  <span className="endpoint">{endpoint}</span>
                  <span className="count">{count} requests</span>
                </div>
              ))
            }
          </div>
        </div>
      </div>

      <div className="performance-alerts">
        <h3>Performance Alerts</h3>
        <div className="alerts-list">
          {performanceMetrics?.bottlenecks?.map((bottleneck, index) => (
            <div key={index} className={`alert-item ${bottleneck.type}`}>
              <div className="alert-header">
                <span className="alert-type">{bottleneck.type.replace('_', ' ').toUpperCase()}</span>
                <span className="alert-severity">
                  {bottleneck.type.includes('high') ? 'HIGH' : 'MEDIUM'}
                </span>
              </div>
              <p className="alert-description">{bottleneck.recommendation}</p>
            </div>
          )) || <p>No performance issues detected.</p>}
        </div>
      </div>
    </div>
  );
};

// Client Support Tab Component
const SupportTab = ({ onAnalyzeIssue, logs }) => {
  const [clientId, setClientId] = useState('');
  const [issueDescription, setIssueDescription] = useState('');
  const [analyzing, setAnalyzing] = useState(false);

  const handleAnalyze = async () => {
    if (!clientId || !issueDescription) {
      alert('Please provide both Client ID and Issue Description');
      return;
    }

    setAnalyzing(true);
    try {
      await onAnalyzeIssue(clientId, issueDescription);
    } finally {
      setAnalyzing(false);
    }
  };

  // Get unique client IDs from recent logs
  const clientIds = [...new Set(
    logs
      .filter(log => log.context?.user_id)
      .map(log => log.context.user_id)
      .slice(0, 10) // Limit to recent clients
  )];

  return (
    <div className="support-tab">
      <div className="issue-analysis-section">
        <h3>🔍 Client Issue Analysis</h3>
        <p>Analyze client issues using comprehensive log data</p>

        <div className="analysis-form">
          <div className="form-group">
            <label>Client ID:</label>
            <select
              value={clientId}
              onChange={(e) => setClientId(e.target.value)}
            >
              <option value="">Select a client...</option>
              {clientIds.map(id => (
                <option key={id} value={id}>{id}</option>
              ))}
            </select>
            <input
              type="text"
              placeholder="Or enter custom client ID..."
              value={clientId}
              onChange={(e) => setClientId(e.target.value)}
            />
          </div>

          <div className="form-group">
            <label>Issue Description:</label>
            <textarea
              value={issueDescription}
              onChange={(e) => setIssueDescription(e.target.value)}
              placeholder="Describe the client's issue..."
              rows={4}
            />
          </div>

          <button
            onClick={handleAnalyze}
            disabled={analyzing}
            className="analyze-button"
          >
            {analyzing ? '🔄 Analyzing...' : '🔍 Analyze Issue'}
          </button>
        </div>
      </div>

      <div className="recent-clients">
        <h3>Recent Client Activity</h3>
        <div className="client-activity">
          {clientIds.map(clientId => {
            const clientLogs = logs.filter(log =>
              log.context?.user_id === clientId
            );
            const errorCount = clientLogs.filter(log => log.level === 'ERROR').length;

            return (
              <div key={clientId} className="client-item">
                <div className="client-header">
                  <span className="client-id">{clientId}</span>
                  <span className={`error-count ${errorCount > 0 ? 'has-errors' : ''}`}>
                    {errorCount} errors
                  </span>
                </div>
                <div className="client-stats">
                  <span>{clientLogs.length} total logs</span>
                  <span>Last activity: {
                    clientLogs.length > 0 ?
                      new Date(clientLogs[0].timestamp).toLocaleString() :
                      'N/A'
                  }</span>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
};

export default AdminDashboard;
