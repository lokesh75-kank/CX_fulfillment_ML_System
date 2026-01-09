/**
 * RCA Report Page
 * 
 * Shows root cause analysis report for an incident
 */

import { useState, useEffect } from 'react';
import { useRouter } from 'next/router';
import axios from 'axios';
import Link from 'next/link';

interface RCACause {
  rank: number;
  hypothesis: {
    name: string;
    category: string;
  };
  confidence: number;
  impact: number;
  score: number;
}

interface RCAReport {
  incident_id: string;
  incident_metric: string;
  generated_at: string;
  hypotheses_tested: number;
  ranked_causes: RCACause[];
  top_cause: RCACause | null;
  narrative: string;
  summary: string;
}

export default function RCAReport() {
  const router = useRouter();
  const { id } = router.query;
  const [report, setReport] = useState<RCAReport | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (id) {
      fetchRCA(id as string);
    }
  }, [id]);

  const fetchRCA = async (incidentId: string) => {
    try {
      const response = await axios.get(`http://localhost:8000/api/rca/${incidentId}`);
      setReport(response.data);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching RCA:', error);
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="p-8">Loading...</div>;
  }

  if (!report) {
    return <div className="p-8">RCA report not found</div>;
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
              Root Cause Analysis Report
            </h1>
            <p className="text-sm text-gray-500 mt-1">
              Generated: {new Date(report.generated_at).toLocaleString()}
            </p>
          </div>

          <div className="px-6 py-4">
            <div className="mb-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-2">Summary</h2>
              <p className="text-gray-700">{report.summary}</p>
            </div>

            <div className="mb-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-2">Narrative</h2>
              <p className="text-gray-700">{report.narrative}</p>
            </div>
          </div>
        </div>

        {/* Ranked Causes */}
        <div className="bg-white rounded-lg shadow">
          <div className="px-6 py-4 border-b border-gray-200">
            <h2 className="text-xl font-semibold text-gray-900">
              Ranked Root Causes ({report.hypotheses_tested} hypotheses tested)
            </h2>
          </div>
          <div className="px-6 py-4">
            <div className="space-y-4">
              {report.ranked_causes.map((cause) => (
                <div key={cause.rank} className="border border-gray-200 rounded-lg p-4">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-3 mb-2">
                        <span className="px-2 py-1 bg-blue-100 text-blue-800 rounded text-sm font-medium">
                          #{cause.rank}
                        </span>
                        <h3 className="text-lg font-semibold text-gray-900">
                          {cause.hypothesis.name}
                        </h3>
                        <span className="px-2 py-1 bg-gray-100 text-gray-700 rounded text-xs">
                          {cause.hypothesis.category}
                        </span>
                      </div>
                      <div className="grid grid-cols-3 gap-4 mt-4">
                        <div>
                          <p className="text-sm text-gray-500">Confidence</p>
                          <p className="text-lg font-semibold text-gray-900">
                            {(cause.confidence * 100).toFixed(0)}%
                          </p>
                        </div>
                        <div>
                          <p className="text-sm text-gray-500">Impact</p>
                          <p className="text-lg font-semibold text-gray-900">
                            {cause.impact.toFixed(2)}
                          </p>
                        </div>
                        <div>
                          <p className="text-sm text-gray-500">Score</p>
                          <p className="text-lg font-semibold text-gray-900">
                            {cause.score.toFixed(3)}
                          </p>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Action Button */}
        <div className="mt-6">
          <Link
            href={`/recommendations/${id}`}
            className="px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700 inline-block"
          >
            View Recommendations →
          </Link>
        </div>
      </div>
    </div>
  );
}

