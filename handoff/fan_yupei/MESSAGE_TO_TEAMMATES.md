# Ready-to-Send Handoff Message

大家好，我已经完成并整理好我负责的 Fan Yupei D4/D5 部分，代码和结果都在：

- Repo: https://github.com/FAN0020/pe6201-a2-team-a6
- Branch: `feature/evaluation`
- Freeze SHA: `e36bb1b2fcad625ed944e7df863165d95c0ef53f`
- Handoff folder: `handoff/fan_yupei/`

已完成内容包括：我的 8 个 evaluation cases（`REF-6401`–`REF-6408`）、全组
30-case/58-trial evaluation set、expected outcomes 和 scripted moves、完整 harness
与 exact grader、gated booking trace 检查、judgement、freeze manifest、scripted
evaluation、GPT-5.4 descriptor-v1 正式结果、同一 freeze 的 v2 对照、结果汇总、
defect analysis、cost handoff、报告文字和 demo runbook。

关键结果：scripted 为 58/58；GPT-5.4 v1 为 20/58（negative 20/42）；GPT-5.4
v2 为 25/58（negative 21/42）。v2 比 v1 高 8.6 percentage points，但多用了
53,834 tokens，成本高 US$0.150148。Independent judgement：scripted 3/3，两个
live arm 都是 0/3；失败记录和 raw responses 全部保留，没有 selective retry。

为了避免文件名混淆，`handoff/fan_yupei/results.json` 是最终 live GPT-5.4
prompt-v2/descriptor-v2 结果；`results_descriptor_v1.json` 是我按时间表负责的
descriptor-v1 结果。`SHA256SUMS` 可验证所有 handoff 文件没有被改动。

请大家接下来：

1. Review 并通过正常 PR 流程合并 `feature/evaluation`，不要直接改 main。
2. 其余四位把相同 freeze、相同 cases、相同 v2 prompt 的 live result JSON 放进
   `artifacts/live_results/`。
3. 收齐后运行 `python3 analysis/aggregate_live_results.py`；只使用
   `compatible: true` 的结果。
4. 把 `handoff/fan_yupei/live_cost_handoff.csv` 和其余模型的真实结果交给 D6
   owner 完成最终成本表。

复现命令和完整注意事项都写在 `handoff/fan_yupei/HANDOFF.md`。仓库内没有 API
key。谢谢！
