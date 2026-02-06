export interface Intervention {
  id: number;
  name: string;
  name_en?: string;
  description?: string;
  category: 'nutrition' | 'exercise' | 'sleep' | 'supplement' | 'medical';
  mechanism?: string;
  evidence_level: number;
  created_at: string;
  updated_at: string;
}

export interface Evidence {
  id: number;
  intervention_id: number;
  source_type?: string;
  pubmed_id?: string;
  citation?: string;
  sample_size?: number;
  duration_days?: number;
  effect_size?: {
    metric: string;
    value: number;
    ci_95: [number, number];
  };
  outcomes?: string[];
  quality_score?: number;
  created_at: string;
}

export interface Recommendation {
  id: number;
  user_id: string;
  intervention_id: number;
  priority: number;
  reasoning?: string;
  risk_score?: number;
  benefit_score?: number;
  net_benefit?: number;
  created_at: string;
}

export interface InterventionWithScores {
  id: number;
  name: string;
  category: string;
  evidence_level: number;
  risk_score: number;
  benefit_score: number;
  net_benefit: number;
}

export const categoryLabels = {
  nutrition: '营养',
  exercise: '运动',
  sleep: '睡眠',
  supplement: '补充剂',
  medical: '医疗'
};

export const evidenceLevelLabels = {
  1: '一级 (高质量RCT/Meta分析)',
  2: '二级 (质量较好的RCT/观察性研究)',
  3: '三级 (病例对照/队列研究)',
  4: '四级 (专家意见/机制研究)'
};
