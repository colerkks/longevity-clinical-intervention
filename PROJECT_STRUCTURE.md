# 项目结构设计

## 目录规划

```
longevity-clinical-intervention/
├── README.md                    # 项目说明
├── CONTRIBUTING.md              # 贡献指南
├── LICENSE                     # MIT License
│
├── backend/                    # 后端服务
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py            # FastAPI 应用入口
│   │   ├── models/            # 数据模型
│   │   │   ├── intervention.py
│   │   │   ├── evidence.py
│   │   │   └── user.py
│   │   ├── schemas/           # Pydantic schemas
│   │   ├── api/               # API 路由
│   │   │   ├── interventions.py
│   │   │   ├── evidence.py
│   │   │   └── recommendations.py
│   │   ├── services/          # 业务逻辑
│   │   │   ├── evidence_grading.py
│   │   │   ├── risk_benefit.py
│   │   │   └── recommendation_engine.py
│   │   ├── database.py         # 数据库配置
│   │   └── utils/             # 工具函数
│   ├── tests/                  # 测试
│   ├── requirements.txt         # Python 依赖
│   └── Dockerfile
│
├── frontend/                   # 前端应用
│   ├── src/
│   │   ├── components/         # React 组件
│   │   ├── pages/            # 页面
│   │   ├── services/          # API 调用
│   │   └── utils/            # 工具函数
│   ├── package.json
│   └── tsconfig.json
│
├── data/                      # 数据文件
│   ├── interventions.csv       # 干预措施数据
│   ├── evidence_db.json        # 证据数据库
│   └── references/            # 文献引用
│
└── docs/                      # 文档
    ├── api.md                 # API 文档
    ├── evidence_levels.md      # 证据分级说明
    └── clinical_guidelines.md # 临床指南
```

## 数据模型核心概念

### 1. Intervention（干预措施）
```json
{
  "id": "unique_id",
  "name": "补充剂名称/干预类型",
  "category": "nutrition|exercise|sleep|supplement|medical",
  "mechanism": "作用机制描述",
  "evidence_level": 1-4,
  "clinical_trials": [],
  "risks": [],
  "benefits": []
}
```

### 2. Evidence（证据）
```json
{
  "id": "evidence_id",
  "intervention_id": "关联干预措施",
  "source": {
    "type": "randomized_trial|cohort_study|case_control|meta_analysis",
    "pubmed_id": "PMID",
    "sample_size": 1000,
    "duration_days": 365
  },
  "outcomes": [],
  "effect_size": {
    "metric": "hazard_ratio|mean_difference",
    "value": 0.85,
    "ci_95": [0.78, 0.92]
  }
}
```

### 3. Evidence Levels（证据分级）

- **Level 1**: 高质量随机对照试验或Meta分析
- **Level 2**: 质量较好的RCT或观察性研究
- **Level 3**: 病例对照研究或队列研究
- **Level 4**: 专家意见、病例报告、机制研究

## 开发优先级

### Phase 1: 数据基础设施
1. 设计数据库schema
2. 创建干预措施CRUD API
3. 构建证据录入系统
4. 实现证据分级算法

### Phase 2: 核心分析引擎
1. 风险-收益量化分析
2. 干预措施效果评估
3. 药物/补充剂相互作用检测
4. 个性化推荐算法

### Phase 3: 用户界面
1. 干预措施查询和筛选
2. 证据可视化
3. 个性化建议生成器
4. 效果追踪dashboard
