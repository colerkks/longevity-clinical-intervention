import { useState } from 'react';
import { interventionsApi } from '@/services/api';
import type { Intervention } from '@/types';

export function InterventionList() {
  const [interventions, setInterventions] = useState<Intervention[]>([]);
  const [loading, setLoading] = useState(false);
  const [filter, setFilter] = useState<string>('all');

  const loadInterventions = async () => {
    setLoading(true);
    try {
      const params = filter !== 'all' ? { category: filter } : undefined;
      const response = await interventionsApi.list(params);
      setInterventions(response.data);
    } catch (error) {
      console.error('Failed to load interventions:', error);
    } finally {
      setLoading(false);
    }
  };

  const evidenceLevelColor = (level: number) => {
    const colors = {
      1: 'bg-green-100 text-green-800',
      2: 'bg-blue-100 text-blue-800',
      3: 'bg-yellow-100 text-yellow-800',
      4: 'bg-gray-100 text-gray-800',
    };
    return colors[level as keyof typeof colors] || colors[4];
  };

  return (
    <div className="p-6">
      <h2 className="text-2xl font-bold mb-6">干预措施列表</h2>

      <div className="mb-6 flex gap-4">
        <select
          value={filter}
          onChange={(e) => setFilter(e.target.value)}
          className="border rounded-lg px-4 py-2"
        >
          <option value="all">全部分类</option>
          <option value="nutrition">营养</option>
          <option value="exercise">运动</option>
          <option value="sleep">睡眠</option>
          <option value="supplement">补充剂</option>
          <option value="medical">医疗</option>
        </select>

        <button
          onClick={loadInterventions}
          disabled={loading}
          className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 disabled:opacity-50"
        >
          {loading ? '加载中...' : '加载'}
        </button>
      </div>

      {interventions.length === 0 && !loading && (
        <div className="text-center py-12 text-gray-500">
          <p>点击"加载"按钮查看干预措施</p>
        </div>
      )}

      <div className="grid gap-4">
        {interventions.map((intervention) => (
          <div
            key={intervention.id}
            className="border rounded-lg p-4 hover:shadow-lg transition-shadow"
          >
            <div className="flex justify-between items-start mb-2">
              <h3 className="text-lg font-semibold">{intervention.name}</h3>
              <span className={`px-3 py-1 rounded-full text-sm ${evidenceLevelColor(intervention.evidence_level)}`}>
                等级 {intervention.evidence_level}
              </span>
            </div>

            <p className="text-gray-600 mb-3">{intervention.description}</p>

            <div className="flex gap-2 text-sm text-gray-500">
              <span>分类: {intervention.category}</span>
              <span>•</span>
              <span>
                {new Date(intervention.created_at).toLocaleDateString('zh-CN')}
              </span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
