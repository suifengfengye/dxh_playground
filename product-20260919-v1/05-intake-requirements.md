# 工作 3 补充：录入链路需求与旅程（改版标尺）

版本：v1 / 2026-09-19。性质：基于用户评审反馈的改版需求，不是用户研究结果。
适用对象：P01、P02（取代原 W02A/B/C）、P08。**不改动** P03–P07、P09。
使用技能：`job-stories`（需求与验收）、`customer-journey-map`（旅程与流失点）、`ui-ux-pro-max`（交互规则）。

## 1. 为什么要改

用户对 v1 草图的三条评审意见：

1. 登录后的录入路径太长，全部做成了表单。
2. AI 能力体现很弱。
3. 需要用户填写的信息过多。

诊断（本轮的设计依据，不是已验证结论）：v1 把 AI 放在流程末端——用户先完成三步表单，AI 才出来生成文档。等于让用户先做苦力。正确顺序应是 **AI 先起草，用户只做校对**。因此在 P02/P08 引入「对话 + 事实清单」双视图。

## 2. 人物设定（假设，非研究数据）

Carla，34 岁，Austin TX，市场/运营背景，非技术。公司裁员后重新找工作，手边是一份两年前的简历。会用 LinkedIn 和 Indeed，也用过通用聊天模型改过简历；**不愿再学一个新工具**，对"又要填一堆表"极度敏感。

待验证：以上人物基于定位推断，未经过真实访谈。招募首批 10–15 位测试者时应先校验，而不是当作已知事实。

## 3. 旅程图

阶段沿用 `customer-journey-map` 框架，只保留与本产品相关的部分。Emoji 表示情绪倾向。

| 阶段 | 触点 | 用户动作 | 心里在想 | 情绪 | 痛点 | 机会 |
|---|---|---|---|---|---|---|
| 认知 Awareness | 朋友推荐、社媒、搜索 | 扫到"AI 帮你定制简历" | "又是 AI 简历工具？" | 😐 钝感 | 看不出与自己用通用模型有何差别 | 首屏直接写「AI 做什么 / 绝不做什么」，而不是功能列表 |
| 考虑 Consideration | 落地页 | 找安装要求、价格、隐私 | "要不要装东西？要填多久？" | 😟 警惕 | 不知道要投入多少时间 | 明确 "No installation" 与「只有 姓名+一段经历 是必需的」 |
| 注册 Acquisition | 邮箱登录 | 输入邮箱收链接 | "别让我设密码" | 😐 略不耐 | 邮件延迟、链接过期 | 同页重发；不建注册/登录/忘记密码三套流程 |
| **录入 Onboarding**（问题区） | 引导页 | 上传简历、回答问题 | "还要填多少？填完能干嘛？" | 😩 由期待转疲惫 | **三步表单、字段多、看不到尽头、AI 全程不显形** | 合成单页：对话 + 事实清单侧栏；一键确认；AI 主动先给结论 |
| 首次产出 Time to value | 职位详情、导出页 | 看适配依据与草稿 | "这些是我说的，还是它编的？" | 🤔 半信 | 无法判断 AI 有没有编造 | 每条改动给出处与改动日志（沿用 P06 证据区） |
| 复用 Engagement | 工作台 | 处理第二个职位 | "这次能更快吗？" | 🙂 期待 | 需要重新解释背景 | 复用同一份已确认资料，不重复采集 |
| 留存 Retention（本轮不解决） | — | — | "我投完了，还需要它吗？" | — | 求职结束即流失 | 结果跟踪、面试准备等，属后续范围 |

### 关键时刻

- **Aha moment**：不是"生成了一份简历"，而是**看到职位要求逐条对上自己的真实经历**。这决定了入职页不该停在"下载 PDF"。
- **Moments of truth**：① 上传简历后第一屏的 AI 提取结果是否可信；② 第一次点"Looks right"；③ 第一次离开录入页之后是否回来。
- **流失触发点**：引导超过一屏；出现事先未说明的必填字段；被问工作授权/薪资；AI 提取错误需要逐条手改；长任务无阶段反馈。

### 优先改进

| 优先级 | 改进 | 对应 |
|---|---|---|
| P0 | 三步表单合成单页「对话 + 清单」 | W02 |
| P0 | 首屏 AI 先给结论（导入职位后立刻说匹配到几条） | W04、W05 |
| P1 | 每条 AI 改动给出处与改动日志 | W06 |
| P1 | 清单组件在 P02 与 P08 复用，用户不必学两套界面 | W02、W08 |
| 后置 | 结果跟踪、面试准备 | 不在本轮 |

## 4. Job stories 与验收标准

格式：`When 情境 / I want 动机 / So I can 结果`。验收标准用于判定草图是否合格。

### JS-01 用现成简历快速建立资料

When I already have a resume file and this is my first time here,
I want to hand it over and only check what the assistant extracted,
so I can reach my workspace without filling in a form.

1. 首屏同时可见上传 / 粘贴 / 直接输入三个入口，不需要先选模式再进入下一步。
2. 上传后立刻出现读取状态，不出现空白表单。
3. 提取结果以**事实卡片**逐条给出，默认状态为「待确认」。
4. 确认一条事实不超过一次点击。
5. 除姓名与邮箱外，没有任何字段被标为必填。
6. 未确认的事实不得用于生成任何材料。

### JS-02 没有文件也能开始

When I don't have a resume file handy, or mine is outdated,
I want to describe my recent work in my own words,
so I can start without hunting for a file.

1. 提供 "Just type it" 入口，不要求先选模板或格式。
2. 允许一次投入整段自由文本。
3. AI 必须把自由文本转成结构化事实卡（职位、公司、时间、职责），不能只把原文存下来。
4. 缺公司/时间等字段时，卡片显示「待补充」，不得编造。
5. 一次只追问一个信息，不弹出多字段表单。
6. 任何时候可以用一个真实角色进入工作区。

### JS-03 随时知道「还缺什么」

When I'm partway through giving my background and I don't know what else is needed,
I want a plain list of what's confirmed, waiting, optional, and asked later,
so I can decide whether to continue or start working.

1. 侧栏分四组：Required to start / Waiting on you / Optional / Asked later。
2. 用具体 section 名称表达，**不使用百分比进度**。
3. 满足最小要求后主 CTA 可用（Start with what I have）。
4. 点击任一条目可定位并编辑对应事实。
5. 窄屏折叠为可展开清单，并显示待处理数量。
6. 空态不显示虚构示例数据。

### JS-04 精确保住一条事实

When the assistant extracted something inaccurate,
I want to fix just that one item without reopening a long form,
so I can trust the profile as a source of truth.

1. 每张卡提供 Edit，就地展开为**带可见标签**的字段。
2. 编辑不跳页，不影响其他已确认内容。
3. 可以整体 Remove 一条事实。
4. 用户手写内容与 AI 生成内容分开存储，后续 AI 重写不得覆盖用户文本。
5. 修改后更新该条的确认状态与时间。
6. 已提交的历史材料不受影响。

### JS-05 中途离开不丢东西

When I get interrupted during setup,
I want to close the tab and return exactly where I stopped,
so I don't redo work.

1. 顶栏常驻保存状态与 Finish later。
2. 已确认事实与草稿保存在服务端。
3. 重新登录后回到同一位置，未确认卡片仍在。
4. 保存失败明确显示 Retry，不得显示 Saved。
5. 不要求完成引导才能进入工作区。

### JS-06 不被强制提供敏感或未知信息

When the product asks something I don't want to answer yet,
I want to skip it without being blocked or judged,
so I can proceed on my own terms.

1. 引导流程内**不出现**工作授权、薪资、地点、语言的问题。
2. 这类问题只在具体职位命中时才就地提问。
3. 所有非必需项标记 optional 并提供 Skip。
4. 不收集年龄、照片、证件、SSN。
5. 选择「暂不提供」后不重复追问。

### JS-07 更新资料而不污染历史

When my experience changes after I already applied with older materials,
I want to update the profile and see what existing work is affected,
so I don't silently overwrite what an employer received.

1. P08 与 P02 使用同一套「对话 + 清单」结构。
2. 上传新版简历时先给「拟变更」卡片逐条确认。
3. 已提交版本与草稿不被覆盖，只标记为「基于旧资料」。
4. 重新分析/重新生成由用户主动触发。

## 5. 采用的 UX 规则（来自 `ui-ux-pro-max`）

| 规则条目 | 内容 | 落在哪里 |
|---|---|---|
| Onboarding · User Freedom | 提供 Skip / Back，不强制线性引导 | JS-03、JS-06 |
| Feedback · Progress Indicators | 用清单表达进度，不伪造百分比 | JS-03 验收 2 |
| Forms · Required Indicators | 明确标记必填 | JS-01 验收 5 |
| Forms · Input Labels | 每个输入都要有可见标签 | JS-04 验收 1 |
| Forms · Submit Feedback | 提交后给出 loading → 成功/失败 | JS-05 验收 4 |
| Content · Truncation | 长内容折叠并给出展开入口 | P05 Job posting 长文 |

## 6. 对草图的影响

| 页面 | 改动 | 状态 |
|---|---|---|
| P01 | 去掉「1-2-3 步骤条」式文案，改为「AI 会做什么 / 绝不做什么」对比 | 本轮 |
| P02 | W02A + W02A-2 + W02B + W02C **合并为一页**：对话流 + 事实卡片 + 清单侧栏 | 本轮 |
| P08 | 与 P02 同构，语气从「引导」改为「更新」 | 本轮 |
| 手机草图 | 新增 P02：侧栏折叠为清单抽屉 | 本轮 |
| P03–P07、P09 | 本轮不动，仍为 v1 形态；确认录入模型后再按同一思路重做 | 待办 |

## 7. 本轮不做

- 聊天式首页（P03 仍是列表工作台，对话只出现在录入与 P06 的就地建议里）。
- 引导内的偏好问卷、人格测评、薪资采集。
- 职位搜索、自动投递、Gmail/Notion 同步（沿用 MVP 范围的延后项）。
