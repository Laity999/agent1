# IRISFLOW 光鉴：鉴微逐新

## 架构

### 前端

#### IRIS OBSERVATORY 观象台

### 后端

#### IRIS PIPELINE 引流渠

##### IRIS SCOUT 窥远仪

##### IRIS PRISM 析光仪

##### IRIS OPTIMIZER 显影仪

```mermaid
---
title: IRISFLOW 光鉴 — 系统架构图
---

flowchart TB
    %% 样式定义
    classDef frontend fill:#4A90D9,color:#fff,stroke:#2C5F8A,stroke-width:2px
    classDef pipeline fill:#2C3E50,color:#fff,stroke:#1A252F,stroke-width:2px
    classDef scout fill:#27AE60,color:#fff,stroke:#1E8449,stroke-width:2px
    classDef prism fill:#F39C12,color:#fff,stroke:#D68910,stroke-width:2px
    classDef optimizer fill:#8E44AD,color:#fff,stroke:#6C3483,stroke-width:2px
    classDef external fill:#95A5A6,color:#fff,stroke:#7F8C8D,stroke-width:2px,stroke-dasharray:5 5
    classDef legend fill:#ECF0F1,color:#2C3E50,stroke:#BDC3C7,stroke-width:1px

    %% ===== 前端层 =====
    subgraph Frontend["🖥️ 前端层"]
        Observatory["IRIS OBSERVATORY<br>观象台"]:::frontend
    end

    %% ===== 后端层 =====
    subgraph Backend["⚙️ 后端层 — IRIS PIPELINE 引流渠"]
        direction LR
        Scout["IRIS SCOUT<br>窥远仪<br><small>数据采集与探测</small>"]:::scout
        Prism["IRIS PRISM<br>析光仪<br><small>数据分析与处理</small>"]:::prism
        Optimizer["IRIS OPTIMIZER<br>显影仪<br><small>策略优化与行动</small>"]:::optimizer
    end

    %% ===== 外部数据源 =====
    External[(🗄️ 外部数据源<br><small>数据库 / 日志 / API</small>)]:::external

    %% ===== 核心数据流（实线） =====
    Scout -->|① 原始数据| Prism
    Prism -->|② 分析洞察| Optimizer
    Optimizer -->|③ 优化指令| Scout

    %% ===== 前后端交互 =====
    Observatory -->|④ 下发任务 / 配置| Backend
    Backend -->|⑤ 推送实时结果| Observatory

    %% ===== 外部交互（虚线） =====
    Scout -.->|采集数据| External
    Optimizer -.->|执行动作| External

    %% ===== 数据闭环标注 =====
    Note1[/"🔄 数据闭环：洞察 → 优化 → 再采集"/]
    Note1 -.-> Backend

    %% ===== 图例 =====
    subgraph Legend["📋 图例"]
        direction LR
        L1[实线：核心数据流]:::legend
        L2[虚线：外部交互]:::legend
        L3[彩色区块：独立组件]:::legend
    end
