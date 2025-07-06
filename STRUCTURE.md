# 协商共和国：项目文件结构

本文档说明项目的文件组织结构和各目录的用途。

---

## 📁 根目录文件

### 核心文档
```
├── README.md                    # 项目介绍
├── INSTURCT.md                    # 创作宪法 (是什么/为什么)
├── WORKFLOW.md                  # 创作手册 (如何做)
├── OUTLINE.md                   # 故事大纲和情节框架
├── ROADMAP.md                   # 创作进度和计划安排
├── STRUCTURE.md                 # 项目文件结构说明（本文档）
└── LICENSE                      # 项目许可证
```

### 配置文件
```
├── book.json                    # 电子书配置
└── .cursor/                     # AI协作配置目录
```

---

## 📚 主要目录结构

### manuscript/ - 小说手稿
```
manuscript/
├── 第一部分_协商共和国编年史/
│   ├── README.md               # 第一部分规划文档
│   ├── 第一章_*.md             # 各章节文件
│   └── 第二章_*.md
├── 第二部分_唯一候选人/
│   ├── README.md               # 第二部分规划文档
│   └── [章节文件]
└── 第三部分_系统的胜利/
    ├── README.md               # 第三部分规划文档
    └── [章节文件]
```

### worldbuilding/ - 世界构建
```
worldbuilding/
├── core.md                     # 核心世界观设定
├── life.md                     # 2038年生活图景
├── timeline.md                 # 历史与角色时间线
├── politics.md                 # 宏观政治
├── charactor.md                # 角色设定和传记
├── glosory.md                  # 术语词汇表
├── organization_acr.md         # 组织机构：ACR阵营
└── organization_cafs.md        # 组织机构：CAFS阵营
```

### prompts/ - AI创作提示
```
prompts/
├── 提示模板/                   # 标准化创作模板
│   ├── 场景生成.md
│   └── 角色对话.md
├── 当前章节提示/               # 进行中的创作提示
└── 已完成提示/                 # 历史创作记录
```

### resources/ - 创作资源
```
resources/
├── style.md                    # 写作风格指南
├── quality_control.md          # 质量控制手册
├── memory.md                  # 项目记忆存档
└── [其他参考资料]
```

### repomix/ - 项目版本
```
repomix/
├── 版本1.md                   # 项目早期版本
└── 版本2.md                   # 项目更新版本
```

---

## 🔗 文档关系图

```
INSTURCT.md (宪法) ───┐
                    ├─→ WORKFLOW.md (手册) ───┐
                    │                         ├─→ worldbuilding/
                    │                         ├─→ prompts/
                    │                         └─→ manuscript/
                    └─→ OUTLINE.md

README.md ──┐
            ├─→ INSTURCT.md
            ├─→ WORKFLOW.md
            ├─→ STRUCTURE.md
            └─→ ROADMAP.md
```

---

## 📝 文件命名规范

### 章节文件
```
第X章_章节标题.md
例：第一章_我不是被选出来的而是被评分出来的.md
```

### 提示文件
```
当前章节提示/章节名_创作提示.md
已完成提示/章节名_创作提示.md
```

### 世界构建文件
```
功能描述.md
例：charactor.md, glosory.md
```

---

## 🛠️ 使用指南

### 查找文件
1. **了解项目** → `README.md`
2. **理解创作理念 (为什么)** → `INSTURCT.md`
3. **学习创作方法 (如何做)** → `WORKFLOW.md`
4. **查看故事大纲** → `OUTLINE.md`
5. **查找本文档** → `STRUCTURE.md`

### 创作流程
我们的创作流程、版本控制和质量保证等所有操作规范，均已详细定义在 **`WORKFLOW.md`** 文件中。请将该文件作为所有创作活动的行动指南。

### AI协作
AI协作的具体模式和指令规范，请参考 **`WORKFLOW.md`** 中的相关章节。

---

## 📊 目录状态

- ✅ **已建立**: manuscript/, worldbuilding/, prompts/, resources/
- 🔄 **使用中**: 所有核心文档和目录
- ⏳ **待完善**: 部分章节内容

---

**最后更新**: 2025年7月4日
**维护者**: 项目团队

