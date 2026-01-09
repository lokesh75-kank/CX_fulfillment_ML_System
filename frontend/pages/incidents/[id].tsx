/**
 * Incident Detail Page
 * 
 * Shows detailed information about a specific incident
 */

import { useState, useEffect } from 'react';
import { useRouter } from 'next/router';
import axios from 'axios';
import Link from 'next/link';

interface IncidentDetail {
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
  top_regressing_slices: Array<{
    cohort: Record<string, string>;
    delta: number;
    delta_percent: number;
    order_count: number;
    significance_level?: string;
  }>;
  affected_cohorts?: Array<Record<string, string>>;
  total_orders_affected?: number;
  detection_method?: string;
}

export default function IncidentDetail() {
  const router = useRouter();
  const { id } = router.query;
  const [incident, setIncident] = useState<IncidentDetail | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (id) {
      fetchIncident(id as string);
    }
  }, [id]);

  const fetchIncident = async (incidentId: string) => {
    try {
      const response = await axios.get(`http://localhost:8000/api/incidents/${incidentId}`);
      setIncident(response.data);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching incident:', error);
      setLoading(false);
    }
  };

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'HIGH': return 'bg-red-100 text-red-800 border-red-300';
      case 'MEDIUM': return 'bg-yellow-100 text-yellow-800 border-yellow-300';
      case 'LOW': return 'bg-green-100 text-green-800 border-green-300';
      default: return 'bg-gray-100 text-gray-800 border-gray-300';
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

  if (!incident) {
    return <div className="p-8">Incident not found</div>;
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <Link href="/" className="text-blue-600 hover:text-blue-800 mb-4 inline-block">
          ← Back to Dashboard
        </Link>

        <div className="bg-white rounded-lg shadow mb-6">
          <div className="px-6 py-4 border-b border-gray-200">
            <div className="flex items-center justify-between">
              <h1 className="text-2xl font-bold text-gray-900">
                Incident: {incident.metric_name.replace('_', ' ').toUpperCase()}
              </h1>
              <span className={`px-3 py-1 rounded border ${getSeverityColor(incident.severity)}`}>
                {incident.severity}
              </span>
            </div>
          </div>

          <div className="px-6 py-4">
            {/* Key Metrics */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-6 mb-6">
              <div className="bg-blue-50 rounded-lg p-4">
                <h3 className="text-xs font-medium text-gray-600">Detected At</h3>
                <p className="text-lg font-semibold text-gray-900 mt-1">
                  {new Date(incident.detected_at).toLocaleString()}
                </p>
                <p className="text-xs text-gray-500 mt-1">
                  {Math.round((new Date().getTime() - new Date(incident.detected_at).getTime()) / (1000 * 60 * 60))} hours ago
                </p>
              </div>
              <div className="bg-green-50 rounded-lg p-4">
                <h3 className="text-xs font-medium text-gray-600">Current Value</h3>
                <p className="text-lg font-semibold text-gray-900 mt-1">
                  {incident.metric_value.toFixed(2)}
                </p>
                <p className="text-xs text-gray-500 mt-1">Latest measurement</p>
              </div>
              {incident.baseline_value && (
                <>
                  <div className="bg-gray-50 rounded-lg p-4">
                    <h3 className="text-xs font-medium text-gray-600">Baseline Value</h3>
                    <p className="text-lg font-semibold text-gray-900 mt-1">
                      {incident.baseline_value.toFixed(2)}
                    </p>
                    <p className="text-xs text-gray-500 mt-1">Historical average</p>
                  </div>
                  <div className={`rounded-lg p-4 ${getDeltaColor(incident.metric_name, incident.delta) === 'text-green-600' ? 'bg-green-50' : 'bg-red-50'}`}>
                    <h3 className="text-xs font-medium text-gray-600">Change</h3>
                    <p className={`text-lg font-semibold mt-1 ${getDeltaColor(incident.metric_name, incident.delta)}`}>
                      {incident.delta > 0 ? '+' : ''}{incident.delta.toFixed(2)}
                    </p>
                    <p className={`text-xs mt-1 ${getDeltaColor(incident.metric_name, incident.delta_percent)}`}>
                      ({incident.delta_percent > 0 ? '+' : ''}{incident.delta_percent.toFixed(1)}%)
                    </p>
                  </div>
                </>
              )}
            </div>

            {/* Severity Explanation */}
            <div className={`border-l-4 p-4 mb-4 ${
              incident.severity === 'HIGH' ? 'border-red-500 bg-red-50' :
              incident.severity === 'MEDIUM' ? 'border-yellow-500 bg-yellow-50' :
              'border-green-500 bg-green-50'
            }`}>
              <div className="flex items-start">
                <div className="flex-1">
                  <h3 className="font-semibold text-gray-900 mb-1">
                    {incident.severity} Severity Incident
                  </h3>
                  <p className="text-sm text-gray-700">
                    {incident.description && incident.description.includes('improved') ? (
                      incident.severity === 'HIGH' 
                        ? 'This improvement has significant magnitude. Investigate to understand what caused the positive change and ensure it can be sustained.'
                        : incident.severity === 'MEDIUM'
                        ? 'This improvement has moderate magnitude. Investigate to understand what caused the positive change and consider replicating it.'
                        : 'This improvement has minor magnitude. Monitor to ensure the positive trend continues.'
                    ) : (
                      incident.severity === 'HIGH' 
                        ? 'This incident has significant impact on customer experience. Immediate investigation and action recommended.'
                        : incident.severity === 'MEDIUM'
                        ? 'This incident has moderate impact. Investigation recommended within 24 hours.'
                        : 'This incident has minor impact. Monitor and investigate when resources allow.'
                    )}
                  </p>
                </div>
              </div>
            </div>

            {incident.description && (
              <div className="mt-6">
                <h3 className="text-sm font-medium text-gray-500">Description</h3>
                <p className="text-gray-900 mt-1">{incident.description}</p>
              </div>
            )}
          </div>
        </div>

        {/* Top Regressing Slices */}
        {incident.top_regressing_slices && incident.top_regressing_slices.length > 0 && (
          <div className="bg-white rounded-lg shadow mb-6">
            <div className="px-6 py-4 border-b border-gray-200">
              <div className="flex items-center justify-between">
                <div>
                  <h2 className="text-xl font-semibold text-gray-900">Affected Customer Cohorts</h2>
                  <p className="text-sm text-gray-500 mt-1">
                    These customer segments are most impacted by this incident
                  </p>
                </div>
                <div className="text-right">
                  <p className="text-2xl font-bold text-gray-900">
                    {incident.top_regressing_slices.reduce((sum, s) => sum + (s.order_count || 0), 0).toLocaleString()}
                  </p>
                  <p className="text-xs text-gray-500">Total Orders Affected</p>
                </div>
              </div>
            </div>
            <div className="px-6 py-4">
              <div className="space-y-4">
                {incident.top_regressing_slices.map((slice, index) => (
                  <div key={index} className="border border-gray-200 rounded-lg p-4 hover:bg-gray-50">
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-2">
                          <span className="px-2 py-1 bg-blue-100 text-blue-800 rounded text-xs font-medium">
                            #{index + 1}
                          </span>
                          <h3 className="font-semibold text-gray-900">
                            {Object.entries(slice.cohort || {}).map(([k, v]) => 
                              <span key={k} className="mr-2">
                                <span className="text-gray-500">{k}:</span> <span className="font-medium">{v}</span>
                              </span>
                            ).length > 0 
                              ? Object.entries(slice.cohort || {}).map(([k, v]) => 
                                  <span key={k} className="mr-2">
                                    <span className="text-gray-500">{k}:</span> <span className="font-medium">{v}</span>
                                  </span>
                                )
                              : 'All Customers'}
                          </h3>
                        </div>
                        <div className="grid grid-cols-2 md:grid-cols-3 gap-4 mt-3">
                          <div>
                            <p className="text-xs text-gray-500">Orders Affected</p>
                            <p className="text-lg font-semibold text-gray-900">
                              {slice.order_count?.toLocaleString() || 'N/A'}
                            </p>
                            <p className="text-xs text-gray-400 mt-1">
                              ~{slice.order_count ? Math.round(slice.order_count * 1.2) : 0} customers impacted
                            </p>
                          </div>
                          <div>
                            <p className="text-xs text-gray-500">Metric Change</p>
                            <p className={`text-lg font-semibold ${getDeltaColor(incident.metric_name, slice.delta || 0)}`}>
                              {slice.delta && slice.delta > 0 ? '+' : ''}{slice.delta?.toFixed(2) || 'N/A'}
                            </p>
                            <p className={`text-xs mt-1 ${getDeltaColor(incident.metric_name, slice.delta_percent || 0)}`}>
                              ({slice.delta_percent && slice.delta_percent > 0 ? '+' : ''}{slice.delta_percent?.toFixed(1) || 'N/A'}%)
                            </p>
                          </div>
                          {slice.significance_level && (
                            <div>
                              <p className="text-xs text-gray-500">Significance</p>
                              <p className="text-lg font-semibold text-gray-900">
                                {slice.significance_level}
                              </p>
                              <p className="text-xs text-gray-400 mt-1">
                                Statistical confidence
                              </p>
                            </div>
                          )}
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
              
              {incident.top_regressing_slices.length === 0 && (
                <div className="text-center py-8 text-gray-500">
                  <p>No cohort-level breakdown available</p>
                  <p className="text-sm mt-1">This incident affects all customers equally</p>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Impact Summary */}
        <div className="bg-white rounded-lg shadow mb-6">
          <div className="px-6 py-4 border-b border-gray-200">
            <h2 className="text-xl font-semibold text-gray-900">Impact Summary</h2>
          </div>
          <div className="px-6 py-4">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div>
                <h3 className="text-sm font-medium text-gray-500 mb-2">Customers Affected</h3>
                <p className="text-2xl font-bold text-gray-900">
                  {incident.total_orders_affected 
                    ? Math.round(incident.total_orders_affected * 1.2).toLocaleString()
                    : incident.top_regressing_slices && incident.top_regressing_slices.length > 0
                    ? Math.round(incident.top_regressing_slices.reduce((sum, s) => sum + (s.order_count || 0), 0) * 1.2).toLocaleString()
                    : '~1,000+'}
                </p>
                <p className="text-xs text-gray-500 mt-1">
                  Estimated (~1.2 customers per order)
                </p>
              </div>
              <div>
                <h3 className="text-sm font-medium text-gray-500 mb-2">Orders Analyzed</h3>
                <p className="text-2xl font-bold text-gray-900">
                  {incident.total_orders_affected?.toLocaleString() ||
                    (incident.top_regressing_slices && incident.top_regressing_slices.length > 0
                      ? incident.top_regressing_slices.reduce((sum, s) => sum + (s.order_count || 0), 0).toLocaleString()
                      : '~1,000+')}
                </p>
                <p className="text-xs text-gray-500 mt-1">
                  Baseline vs current period comparison
                </p>
              </div>
              <div>
                <h3 className="text-sm font-medium text-gray-500 mb-2">Detection Method</h3>
                <p className="text-sm font-semibold text-gray-900">
                  {incident.detection_method || 'Automated Anomaly Detection'}
                </p>
                <p className="text-xs text-gray-500 mt-1">
                  Multiple algorithms for accuracy
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Action Buttons */}
        <div className="flex gap-4">
          <Link
            href={`/rca/${incident.incident_id}`}
            className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
          >
            View RCA Report
          </Link>
          <Link
            href={`/recommendations/${incident.incident_id}`}
            className="px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700"
          >
            View Recommendations
          </Link>
        </div>
      </div>
    </div>
  );
}

