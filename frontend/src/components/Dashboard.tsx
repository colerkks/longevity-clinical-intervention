import { useState, useEffect } from 'react';
import { recommendationsApi } from '@/services/api';
import type { InterventionWithScores } from '@/types';

export function Dashboard() {
  const [topInterventions, setTopInterventions] = useState<InterventionWithScores[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadTopInterventions();
  }, []);

  const loadTopInterventions = async () => {
    setLoading(true);
    try {
      const response = await recommendationsApi.getTopInterventions(10);
      setTopInterventions(response.data);
    } catch (error) {
      console.error('Failed to load top interventions:', error);
    } finally {
      setLoading(false);
    }
  };

  const getNetBenefitColor = (netBenefit: number) => {
    if (netBenefit > 0.5) return 'bg-green-500';
    if (netBenefit > 0) return 'bg-green-400';
    if (netBenefit > -0.3) return 'bg-yellow-400';
    return 'bg-red-400';
  };

  return (
    <div className="p-6">
      <div className="mb-8">
        <h1 className="text-3xl font-bold mb-2">长寿医学临床干预模型</h1>
        <p className="text-gray-600">基于科学证据，为长寿提供个性化干预建议</p>
      </div>

      <div className="grid md:grid-cols-3 gap-6 mb-8">
        <div className="bg-blue-50 rounded-lg p-6">
          <p className="text-sm text-blue-600 font-medium">证据分级</p>
          <p className="text-2xl font-bold text-blue-900">4级系统</p>
        </div>
        <div className="bg-green-50 rounded-lg p-6">
          <p className="text-sm text-green-600 font-medium">风险-收益分析</p>
          <p className="text-2xl font-bold text-green-900">量化评估</p>
        </div>
        <div className="bg-purple-50 rounded-lg p-6">
          <p className="text-sm text-purple-600 font-medium">个性化推荐</p>
          <p className="text-2xl font-bold text-purple-900">AI驱动</p>
        </div>
      </div>

      <div className="mb-6 flex justify-between items-center">
        <h2 className="text-2xl font-bold">顶级干预措施</h2>
        <button
          onClick={loadTopInterventions}
          disabled={loading}
          className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 disabled:opacity-50"
        >
          {loading ? '刷新中...' : '刷新'}
        </button>
      </div>

      {loading && topInterventions.length === 0 ? (
        <div className="text-center py-12 text-gray-500">
          <p>加载中...</p>
        </div>
      ) : (
        <div className="space-y-4">
          {topInterventions.map((intervention, index) => (
            <div
              key={intervention.id}
              className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow"
            >
              <div className="flex justify-between items-start mb-4">
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-2">
                    <span className="bg-gray-200 text-gray-700 px-2 py-1 rounded text-sm font-medium">
                      #{index + 1}
                    </span>
                    <span className="bg-blue-100 text-blue-800 px-2 py-1 rounded text-sm">
                      {intervention.category}
                    </span>
                    <span className="bg-purple-100 text-purple-800 px-2 py-1 rounded text-sm">
                      Level {intervention.evidence_level}
                    </span>
                  </div>
                  <h3 className="text-xl font-semibold">{intervention.name}</h3>
                </div>

                <div className="text-center ml-4">
                  <div className={`w-16 h-16 rounded-full flex items-center justify-center ${getNetBenefitColor(intervention.net_benefit)} text-white font-bold text-lg`}>
                    {intervention.net_benefit?.toFixed(2)}
                  </div>
                  <p className="text-xs text-gray-500 mt-1">净收益</p>
                </div>
              </div>

              <div className="grid grid-cols-3 gap-4">
                <div>
                  <p className="text-sm text-gray-500">风险分数</p>
                  <div className="w-full bg-gray-200 rounded-full h-2 mt-1">
                    <div
                      className="bg-red-500 h-2 rounded-full"
                      style={{ width: `${(intervention.risk_score || 0) * 100}%` }}
                    />
                  </div>
                  <p className="text-sm font-medium mt-1">
                    {(intervention.risk_score || 0).toFixed(2)}
                  </p>
                </div>

                <div>
                  <p className="text-sm text-gray-500">收益分数</p>
                  <div className="w-full bg-gray-200 rounded-full h-2 mt-1">
                    <div
                      className="bg-green-500 h-2 rounded-full"
                      style={{ width: `${(intervention.benefit_score || 0) * 100}%` }}
                    />
                  </div>
                  <p className="text-sm font-medium mt-1">
                    {(intervention.benefit_score || 0).toFixed(2)}
                  </p>
                </div>

                <div>
                  <p className="text-sm text-gray-500">证据质量</p>
                  <p className="text-sm font-medium mt-1">
                    Level {intervention.evidence_level}
                  </p>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
