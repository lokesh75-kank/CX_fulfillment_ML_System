/**
 * Recommendations Page
 * 
 * Shows recommendations and allows exporting experiment plans
 */

import { useState, useEffect } from 'react';
import { useRouter } from 'next/router';
import axios from 'axios';
import Link from 'next/link';

interface Recommendation {
  action_id: string;
  name: string;
  description: string;
  target_cause: string;
  implementation: string;
  complexity: string;
  rollout_time: string;
  expected_cx_impact: number;
  expected_efficiency_impact: number;
  confidence: number;
  net_benefit: number | null;
  recommendation: string | null;
}

export default function Recommendations() {
  const router = useRouter();
  const { id } = router.query;
  const [recommendations, setRecommendations] = useState<Recommendation[]>([]);
  const [loading, setLoading] = useState(true);
  const [exporting, setExporting] = useState<string | null>(null);

  useEffect(() => {
    if (id) {
      fetchRecommendations(id as string);
    }
  }, [id]);

  const fetchRecommendations = async (incidentId: string) => {
    try {
      const response = await axios.get(`http://localhost:8000/api/recommendations/${incidentId}`);
      setRecommendations(response.data);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching recommendations:', error);
      setLoading(false);
    }
  };

  const exportExperimentPlan = async (actionId: string) => {
    setExporting(actionId);
    try {
      // In production, this would call an export endpoint
      // For now, just simulate
      await new Promise(resolve => setTimeout(resolve, 1000));
      alert('Experiment plan exported! (In production, this would download a markdown file)');
      setExporting(null);
    } catch (error) {
      console.error('Error exporting:', error);
      setExporting(null);
    }
  };

  const getComplexityColor = (complexity: string) => {
    switch (complexity) {
      case 'low': return 'bg-green-100 text-green-800';
      case 'medium': return 'bg-yellow-100 text-yellow-800';
      case 'high': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getRecommendationColor = (rec: string | null) => {
    if (!rec) return 'bg-gray-100 text-gray-800';
    switch (rec) {
      case 'strong_recommend': return 'bg-green-100 text-green-800';
      case 'recommend': return 'bg-blue-100 text-blue-800';
      case 'consider': return 'bg-yellow-100 text-yellow-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  if (loading) {
    return <div className="p-8">Loading...</div>;
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <Link href={`/incidents/${id}`} className="text-blue-600 hover:text-blue-800 mb-4 inline-block">
          ← Back to Incident
        </Link>

        <div className="bg-white rounded-lg shadow mb-6">
          <div className="px-6 py-4 border-b border-gray-200">
            <h1 className="text-2xl font-bold text-gray-900">
              Recommendations
            </h1>
            <p className="text-sm text-gray-500 mt-1">
              {recommendations.length} recommendations generated
            </p>
          </div>
        </div>

        {/* Recommendations List */}
        <div className="space-y-6">
          {recommendations.length === 0 ? (
            <div className="bg-white rounded-lg shadow p-8 text-center text-gray-500">
              No recommendations available
            </div>
          ) : (
            recommendations.map((rec) => (
              <div key={rec.action_id} className="bg-white rounded-lg shadow">
                <div className="px-6 py-4 border-b border-gray-200">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <h2 className="text-xl font-semibold text-gray-900">
                        {rec.name}
                      </h2>
                      {rec.recommendation && (
                        <span className={`px-2 py-1 rounded text-xs font-medium ${getRecommendationColor(rec.recommendation)}`}>
                          {rec.recommendation.replace('_', ' ')}
                        </span>
                      )}
                    </div>
                    <span className={`px-2 py-1 rounded text-xs font-medium ${getComplexityColor(rec.complexity)}`}>
                      {rec.complexity} complexity
                    </span>
                  </div>
                </div>

                <div className="px-6 py-4">
                  <p className="text-gray-700 mb-4">{rec.description}</p>

                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
                    <div>
                      <p className="text-sm text-gray-500">CX Impact</p>
                      <p className="text-lg font-semibold text-green-600">
                        +{rec.expected_cx_impact.toFixed(1)} points
                      </p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-500">Efficiency Impact</p>
                      <p className={`text-lg font-semibold ${rec.expected_efficiency_impact < 0 ? 'text-red-600' : 'text-green-600'}`}>
                        {rec.expected_efficiency_impact > 0 ? '+' : ''}{rec.expected_efficiency_impact.toFixed(1)}%
                      </p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-500">Confidence</p>
                      <p className="text-lg font-semibold text-gray-900">
                        {(rec.confidence * 100).toFixed(0)}%
                      </p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-500">Rollout Time</p>
                      <p className="text-lg font-semibold text-gray-900">
                        {rec.rollout_time}
                      </p>
                    </div>
                  </div>

                  {rec.net_benefit !== null && (
                    <div className="mb-4">
                      <p className="text-sm text-gray-500">Net Benefit Score</p>
                      <p className="text-lg font-semibold text-gray-900">
                        {rec.net_benefit.toFixed(3)}
                      </p>
                    </div>
                  )}

                  <div className="border-t border-gray-200 pt-4">
                    <h3 className="text-sm font-medium text-gray-500 mb-2">Implementation</h3>
                    <p className="text-sm text-gray-700">{rec.implementation}</p>
                  </div>

                  <div className="mt-4 flex gap-3">
                    <button
                      onClick={() => exportExperimentPlan(rec.action_id)}
                      disabled={exporting === rec.action_id}
                      className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50"
                    >
                      {exporting === rec.action_id ? 'Exporting...' : 'Export Experiment Plan'}
                    </button>
                  </div>
                </div>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
}

