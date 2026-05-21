# 厌氧反应器智能诊断系统

## 项目简介

基于混合架构（规则引擎 + 可选大模型增强）的厌氧反应器智能体，用于废水处理中厌氧反应器的状态监测、故障诊断和操作建议。

### 核心功能
- **运行参数监测**：12 项关键参数的实时评估（pH、温度、COD、VFA、碱度、ORP、产气量、甲烷含量、OLR、HRT、氨氮等）
- **故障智能诊断**：6 种常见故障的自动识别（酸化、氨抑制、温度冲击、有机负荷过高、污泥流失、毒性抑制）
- **操作建议生成**：基于故障类型的优先级排序处理方案
- **可视化 Web 界面**：Streamlit 仪表盘，支持历史趋势分析
- **可选 AI 增强**：接入 Claude 或 OpenAI 大模型，提供因果推理深度分析

## 环境要求

- Python 3.10+
- Windows / macOS / Linux

## 快速开始

### 1. 安装依赖

```bash
pip install pydantic pyyaml python-dotenv click rich streamlit plotly
```

### 2. 启动系统

**方式一：Web 可视化界面（推荐交给老师演示）**
```bash
python -m streamlit run anaerobic_reactor_agent/web/app.py
```
浏览器访问 `http://localhost:8501`

**方式二：命令行演示**
```bash
python demo.py
```

**方式三：编程调用**
```python
from anaerobic_reactor_agent.engine.rule_engine import RuleEngine
from anaerobic_reactor_agent.models.reactor_state import ReactorParameters

params = ReactorParameters(
    ph=6.2, temperature=35, cod_inlet=5000, cod_outlet=2500,
    vfa=800, alkalinity=1500, orp=-250, biogas_production=30,
    methane_content=55, olr=8, hrt=12,
)

result = RuleEngine().diagnose(params)
print(f"状态: {result.overall_status.value}, 故障数: {result.fault_count}")
for f in result.faults:
    print(f"  - {f.fault_type}: 置信度 {f.confidence:.0%}")
```

## 项目结构

```
├── anaerobic_reactor_agent/     # 核心代码包
│   ├── models/                   # 数据模型（Pydantic）
│   ├── engine/                   # 规则引擎（诊断核心）
│   ├── knowledge/                # 知识库（YAML 规则配置文件）
│   │   ├── parameter_thresholds.yaml  # 参数阈值
│   │   ├── fault_rules.yaml           # 故障诊断规则
│   │   └── recommendations.yaml       # 预定义建议模板
│   ├── llm/                      # 大模型集成（可选）
│   ├── cli/                      # 命令行界面
│   ├── web/                      # Web 可视化界面
│   │   ├── components/           # UI 组件
│   │   └── pages/                # 页面
│   └── utils/                    # 工具函数
├── tests/                        # 单元测试
├── demo.py                       # 演示脚本
├── 启动.bat                      # Windows 一键启动
├── setup.py                      # 安装配置
└── requirements.txt              # 依赖列表
```

## 诊断的故障类型

| 故障类型 | 触发条件 | 严重程度 |
|---------|---------|---------|
| 酸化 | VFA 升高 + pH 下降 + VFA/ALK > 0.5 | 报警 |
| 氨抑制 | NH3-N > 150 + 甲烷含量下降 | 报警 |
| 温度冲击 | 温度超出范围 + 产气量下降 | 报警 |
| 有机负荷过高 | OLR 超限 + COD 去除率下降 | 预警 |
| 污泥流失 | HRT 过短 + COD 去除率下降 | 预警 |
| 毒性抑制 | 产气量骤降 + 甲烷含量低 | 危急 |

## 大模型增强（可选）

在侧边栏配置 API Key 后，系统会调用大模型对诊断结果进行深度分析：
- 因果链推理（为什么会出现这个故障）
- 风险评估（不处理的后果）
- 分步行动计划
- 后续监测建议

不配置 API Key 也不影响使用，规则引擎独立提供完整诊断结果。

## 测试

```bash
pytest tests/ -v
```
