import { useState, useEffect } from 'react';
import { interventionsApi, evidenceApi } from '@/services/api';
import type { Intervention, Evidence } from '@/types';

export function InterventionDetail({ interventionId }: { interventionId: number }) {
  const [intervention, setIntervention] = useState<Intervention | null>(null);
  const [evidence, setEvidence] = useState<Evidence[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadData();
  }, [interventionId]);

  const loadData = async () => {
    setLoading(true);
    try {
      const [interventionRes, evidenceRes] = await Promise.all([
        interventionsApi.get(interventionId),
        evidenceApi.list(interventionId),
      ]);
      setIntervention(interventionRes.data);
      setEvidence(evidenceRes.data);
    } catch (error) {
      console.error('Failed to load intervention:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="p-6">加载中...</div>;
  }

  if (!intervention) {
    return <div className="p-6">未找到干预措施</div>;
  }

  return (
    <div className="p-6 max-w-4xl mx-auto">
      <button
        onClick={() => window.history.back()}
        className="mb-4 text-blue-600 hover:underline"
      >
        ← 返回列表
      </button>

      <div className="bg-white rounded-lg shadow-lg p-6 mb-6">
        <h1 className="text-3xl font-bold mb-4">{intervention.name}</h1>

        <div className="grid md:grid-cols-2 gap-4 mb-6">
          <div>
            <p className="text-sm text-gray-500">分类</p>
            <p className="font-medium">{intervention.category}</p>
          </div>
          <div>
            <p className="text-sm text-gray-500">证据等级</p>
            <p className="font-medium">Level {intervention.evidence_level}</p>
          </div>
        </div>

        {intervention.description && (
          <div className="mb-4">
            <h3 className="font-semibold mb-2">描述</h3>
            <p className="text-gray-700">{intervention.description}</p>
          </div>
        )}

        {intervention.mechanism && (
          <div className="mb-4">
            <h3 className="font-semibold mb-2">作用机制</h3>
            <p className="text-gray-700">{intervention.mechanism}</p>
          </div>
        )}
      </div>

      <div className="bg-white rounded-lg shadow-lg p-6">
        <h2 className="text-2xl font-bold mb-4">相关证据</h2>

        {evidence.length === 0 ? (
          <p className="text-gray-500">暂无证据数据</p>
        ) : (
          <div className="space-y-4">
            {evidence.map((e) => (
              <div key={e.id} className="border-l-4 border-blue-500 pl-4">
                {e.source_type && (
                  <p className="text-sm font-medium text-blue-600">
                    {e.source_type}
                  </p>
                )}

                {e.citation && (
                  <p className="text-gray-700">{e.citation}</p>
                )}

                <div className="flex gap-4 text-sm text-gray-500 mt-2">
                  {e.sample_size && (
                    <span>样本: {e.sample_size}</span>
                  )}
                  {e.duration_days && (
                    <span>时长: {e.duration_days}天</span>
                  )}
                  {e.quality_score && (
                    <span>质量分数: {e.quality_score}</span>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
