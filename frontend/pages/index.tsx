/**
 * Dashboard Page
 * 
 * Main dashboard showing CX Score trends and active incidents
 */

import { useState, useEffect } from 'react';
import axios from 'axios';

interface Incident {
  incident_id: string;
  detected_at: string;
  metric_name: string;
  metric_value: number;
  baseline_value: number | null;
  delta: number;
  delta_percent: number;
  severity: string;
  status: string;
  description: string | null;
}

interface MetricsSummary {
  current_cx_score: number;
  baseline_cx_score: number | null;
  delta: number | null;
  trend: string;
}

export default function Dashboard() {
  const [incidents, setIncidents] = useState<Incident[]>([]);
  const [metrics, setMetrics] = useState<MetricsSummary | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const [incidentsRes, metricsRes] = await Promise.all([
        axios.get('http://localhost:8000/api/incidents/'),
        axios.get('http://localhost:8000/api/metrics/summary')
      ]);
      
      setIncidents(incidentsRes.data);
      setMetrics(metricsRes.data);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching data:', error);
      setLoading(false);
    }
  };

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'HIGH': return 'bg-red-100 text-red-800';
      case 'MEDIUM': return 'bg-yellow-100 text-yellow-800';
      case 'LOW': return 'bg-green-100 text-green-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getDeltaColor = (metricName: string, delta: number) => {
    // Metrics where higher is better
    const higherIsBetter = ['cx_score', 'on_time_rate', 'item_accuracy', 
                           'on_time_score', 'item_accuracy_score', 
                           'cancellation_score', 'refund_score', 
                           'support_score', 'rating_score', 'rating_proxy'];
    
    // Metrics where lower is better
    const lowerIsBetter = ['cancellation_rate', 'refund_rate', 'support_rate',
                          'eta_mean_absolute_error', 'eta_mean_error', 'eta_std_error'];
    
    if (higherIsBetter.includes(metricName)) {
      // For higher-is-better metrics: positive delta = good (green), negative = bad (red)
      return delta >= 0 ? 'text-green-600' : 'text-red-600';
    } else if (lowerIsBetter.includes(metricName)) {
      // For lower-is-better metrics: negative delta = good (green), positive = bad (red)
      return delta <= 0 ? 'text-green-600' : 'text-red-600';
    } else {
      // Unknown metric: use absolute value
      return delta >= 0 ? 'text-green-600' : 'text-red-600';
    }
  };

  if (loading) {
    return <div className="p-8">Loading...</div>;
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-8">
          CX-Fulfillment Agent Dashboard
        </h1>

        {/* Metrics Summary */}
        {metrics && (
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="text-sm font-medium text-gray-500">Current CX Score</h3>
              <p className="text-3xl font-bold text-gray-900 mt-2">
                {metrics.current_cx_score.toFixed(1)}
              </p>
              {metrics.baseline_cx_score && (
                <div className="mt-2">
                  <p className="text-xs text-gray-500">Baseline: {metrics.baseline_cx_score.toFixed(1)}</p>
                  <p className={`text-sm mt-1 font-medium ${metrics.delta && metrics.delta < 0 ? 'text-red-600' : 'text-green-600'}`}>
                    {metrics.delta && metrics.delta > 0 ? '+' : ''}{metrics.delta?.toFixed(1)} points
                  </p>
                </div>
              )}
            </div>

            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="text-sm font-medium text-gray-500">Active Incidents</h3>
              <p className="text-3xl font-bold text-gray-900 mt-2">
                {incidents.filter(i => i.status !== 'resolved').length}
              </p>
              <p className="text-xs text-gray-500 mt-1">
                {incidents.filter(i => i.severity === 'HIGH').length} HIGH, {incidents.filter(i => i.severity === 'MEDIUM').length} MEDIUM
              </p>
            </div>

            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="text-sm font-medium text-gray-500">Trend</h3>
              <p className={`text-3xl font-bold mt-2 capitalize ${
                metrics.trend === 'down' ? 'text-red-600' : 
                metrics.trend === 'up' ? 'text-green-600' : 
                'text-gray-600'
              }`}>
                {metrics.trend === 'down' ? '↓' : metrics.trend === 'up' ? '↑' : '→'} {metrics.trend}
              </p>
            </div>

            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="text-sm font-medium text-gray-500">Time Window</h3>
              <p className="text-sm font-semibold text-gray-900 mt-2">
                Last 24 hours
              </p>
              <p className="text-xs text-gray-500 mt-1">
                Auto-refreshes hourly
              </p>
            </div>
          </div>
        )}

        {/* Incidents List */}
        <div className="bg-white rounded-lg shadow">
          <div className="px-6 py-4 border-b border-gray-200">
            <h2 className="text-xl font-semibold text-gray-900">Active Incidents</h2>
          </div>
          <div className="divide-y divide-gray-200">
            {incidents.length === 0 ? (
              <div className="px-6 py-8 text-center text-gray-500">
                No active incidents
              </div>
            ) : (
              incidents.map((incident) => (
                <div key={incident.incident_id} className="px-6 py-4 hover:bg-gray-50 border-b border-gray-100 last:border-0">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-3 mb-2">
                        <span className={`px-2 py-1 rounded text-xs font-medium ${getSeverityColor(incident.severity)}`}>
                          {incident.severity}
                        </span>
                        <h3 className="text-lg font-medium text-gray-900">
                          {incident.metric_name.replace('_', ' ').toUpperCase()}
                        </h3>
                        <span className="text-xs text-gray-400">
                          Detected: {new Date(incident.detected_at).toLocaleString()}
                        </span>
                      </div>
                      
                      {incident.description && (
                        <p className="text-sm text-gray-600 mb-3">
                          {incident.description}
                        </p>
                      )}

                      {/* Metric Breakdown */}
                      <div className="bg-gray-50 rounded p-3 mb-3">
                        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                          {incident.baseline_value !== null && (
                            <>
                              <div>
                                <p className="text-xs text-gray-500">Baseline</p>
                                <p className="font-semibold text-gray-900">{incident.baseline_value.toFixed(2)}</p>
                              </div>
                              <div>
                                <p className="text-xs text-gray-500">Current</p>
                                <p className="font-semibold text-gray-900">{incident.metric_value.toFixed(2)}</p>
                              </div>
                              <div>
                                <p className="text-xs text-gray-500">Change</p>
                                <p className={`font-semibold ${getDeltaColor(incident.metric_name, incident.delta)}`}>
                                  {incident.delta > 0 ? '+' : ''}{incident.delta.toFixed(2)}
                                </p>
                              </div>
                              <div>
                                <p className="text-xs text-gray-500">% Change</p>
                                <p className={`font-semibold ${getDeltaColor(incident.metric_name, incident.delta_percent)}`}>
                                  {incident.delta_percent > 0 ? '+' : ''}{incident.delta_percent.toFixed(1)}%
                                </p>
                              </div>
                            </>
                          )}
                        </div>
                      </div>

                      {/* Severity Explanation */}
                      <div className="text-xs text-gray-500">
                        <span className="font-medium">Severity:</span> {
                          incident.description && incident.description.includes('improved') ? (
                            incident.severity === 'HIGH' ? 'Large improvement detected, investigate to understand and sustain' :
                            incident.severity === 'MEDIUM' ? 'Moderate improvement detected, investigate to understand and replicate' :
                            'Small improvement detected, monitor to ensure trend continues'
                          ) : (
                            incident.severity === 'HIGH' ? 'Large impact, urgent action needed' :
                            incident.severity === 'MEDIUM' ? 'Moderate impact, investigate soon' :
                            'Small impact, monitor'
                          )
                        }
                      </div>
                    </div>
                    <div className="ml-4">
                      <a
                        href={`/incidents/${incident.incident_id}`}
                        className="text-blue-600 hover:text-blue-800 font-medium text-sm"
                      >
                        Investigate →
                      </a>
                    </div>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

