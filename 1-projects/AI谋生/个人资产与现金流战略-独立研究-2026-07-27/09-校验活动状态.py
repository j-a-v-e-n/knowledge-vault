#!/usr/bin/env python3
"""Fail-closed validation for the durable personal-asset/cash-flow state.

The validator proves only that the current state has the expected closed
schema, fresh local snapshot, exact local byte bindings, and authorization
boundaries. It does not prove market demand, payment, delivery, profit,
investment performance, review quality, or runtime correctness.
"""

from __future__ import annotations

import csv
import hashlib
import html
import json
import os
import re
import stat
import subprocess
import sys
import tempfile
from datetime import datetime, timedelta, timezone
from functools import lru_cache
from pathlib import Path


RESEARCH_ROOT = Path(__file__).resolve().parent
STATE_PATH = RESEARCH_ROOT / "08-活动状态.json"
LEGACY_OPPORTUNITY_ROOT = (RESEARCH_ROOT.parent / "机会到交易系统").resolve()
INVESTMENT_ROOT = (
    RESEARCH_ROOT / "../../../MyBrain/projects/investment-discipline-system"
).resolve()

SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+$")
EXPECTED_SCHEMA_VERSION = "1.1"
EXPECTED_MAX_AGE_HOURS = 72
PRE_SEND_REFRESH_MAX_AGE_HOURS = 24

ALLOWED_STATUSES = {
    "active_internal",
    "blocked_internal",
    "blocked_external",
    "stopped",
    "observation_only",
}
ALLOWED_CLAIM_CLASSES = {"observed", "inferred", "unknown", "externally_validated"}
AUTONOMOUS_SCOPES = {
    "public_read_only_research",
    "workspace_read",
    "local_reversible_edit",
    "local_test",
    "paper_simulation",
    "unpublished_draft",
    "independent_review",
}
REQUIRED_APPROVAL_ACTIONS = {
    "external_contact",
    "public_publish_or_deploy",
    "spend_or_purchase",
    "receive_or_refund_payment",
    "contract_or_legal_commitment",
    "private_account_or_credential_use",
    "nonpublic_third_party_data_use",
    "new_external_integration",
    "live_or_shadow_investment_execution",
    "investment_risk_rule_change",
}
REQUIRED_FALSE_EXPERIMENT_AUTHORITY = {
    "external_contact_authorized",
    "quote_authorized",
    "account_access_authorized",
    "submission_authorized",
    "payment_action_authorized",
    "delivery_harness_authorized",
}
REQUIRED_FALSE_EXPERIMENT_RESULTS = {
    "externally_validated_demand",
    "willingness_to_pay",
    "delivery_feasible",
    "profitable",
    "repeatable",
    "asset_candidate",
}
REQUIRED_CA_MISSING_BINDINGS = {
    "sender_account",
    "observation_cutoff_at",
    "pre_send_source_refresh",
    "exact_user_authorization",
}
EXPECTED_INVESTMENT_IDENTITY = {
    "commit": "fed7d6694dc1b47490848b83e3ff0b56e04a3f39",
    "tree": "2da5f0af186345da05738f971cb8afbdb6dac8db",
    "parent": "d8c108f81f84f4c5be99fe09902ace161bda5745",
}
EXPECTED_INVESTMENT_PROJECT_SUBTREE = "77edce348cb622fe40d598902ac898c981514808"
EXPECTED_INVESTMENT_ARCHIVE_COMMIT = "2f4fd7fe85858db302dc1ba1cd61415aa1adf0de"
EXPECTED_INVESTMENT_RECORD = {
    "path": "investment-discipline-fed7-durable-candidate.json",
    "sha256": "9800b6aead4a4ce5b5235bc804202b65c22d81d6626d756ac766b59d0965f3f9",
}
EXPECTED_INVESTMENT_BUNDLE = {
    "path": "investment-discipline-fed7-subtree.bundle",
    "sha256": "aa36d78d87f3f76ebf73e543c77b7a7711695ccdd6c1d9a126570f47d5e87877",
    "bytes": 62374247,
}
EXPECTED_INVESTMENT_FULL_RUN = {
    "record_path": "investment-fed7-full-suite-run-2026-07-27.json",
    "record_sha256": "58652cd15aa7698a57e3cf5c0148d310f3ca55c0cc9cda2936dd9512a8340bd7",
    "log_path": "investment-fed7-full-governance-suite-2026-07-27.log",
    "log_sha256": "02332c7c1cae91ead41df9d00976048c7e697b5bc9ddabe92413a143046a8c16",
    "log_bytes": 530124,
    "log_lines": 1308,
    "exit_code": 1,
    "summary": [
        "Ran 532 tests in 862.542s",
        "FAILED (failures=40, errors=2)",
    ],
}
EXPECTED_INVESTMENT_ROOT_CAUSE_REVIEW = {
    "path": "review-investment-fed7-root-causes-2026-07-27.json",
    "sha256": "c5ccf9a10b4c993f052a984a6f1c03e2c18a742e178b8e8d174ac8cd55c65d1f",
}

EXPECTED_WORKSTREAM_PATHS = {
    "long_term_capability_strategy": ".",
    "opportunity_to_transaction": ".",
    "investment_discipline": "../../../MyBrain/projects/investment-discipline-system",
}
EXPECTED_WORKSTREAM_ROOTS = {
    "long_term_capability_strategy": RESEARCH_ROOT,
    "opportunity_to_transaction": RESEARCH_ROOT,
    "investment_discipline": INVESTMENT_ROOT,
}
EXPECTED_WORKSTREAM_CLASSIFICATIONS = {
    "long_term_capability_strategy": "strategic_capability_portfolio",
    "opportunity_to_transaction": (
        "problem_discovery_experiment_with_unproven_cash_and_asset_hypotheses"
    ),
    "investment_discipline": "paper_only_research_and_discipline_system",
}
EXPECTED_STRATEGY_ARTIFACT_PATHS = {
    "00-项目北极星与三层结构.md",
    "13-长期能力投资地图与训练路线.md",
    "14-Agent-Harness与垂直适配独立复核.md",
    "evidence/jensen-open-agent-interview-caption-identity-2026-07-27.json",
}
EXPECTED_CA_TARGET = {
    "public_building_id": "Building #CA012650",
    "public_record_location": "Best Western Plus Marina Gateway Hotel",
    "routing_contact_only": True,
}
EXPECTED_CA_CHANNEL = "guestservices@bwmarinagateway.com"
EXPECTED_CA_CHANNEL_SOURCE = "https://www.bwmarinagateway.com/contact.htm"
EXPECTED_CA_EXPERIMENT_ID = "experiment-ca012650-public-record-verification"
EXPECTED_CA_APPROVAL_ID = "approval-ca012650-one-message-verification"
EXPECTED_REVIEW_STATE_PATHS = {
    "legacy_runtime_tombstone": "evidence/review-legacy-opportunity-tombstone-2026-07-27.json",
    "ca012650_internal_candidate": (
        "evidence/review-ca012650-durable-candidate-2026-07-27-r2.json"
    ),
}
EXPECTED_CA_R2_SCHEMA_VERSION = "ca012650-durable-candidate-independent-review/2"
EXPECTED_CA_R2_REVIEW_ID = "review-ca012650-durable-candidate-2026-07-27-r2"
EXPECTED_CA_R2_REVIEWER_IDENTITY = "/root/ca_gate_fix_map"
EXPECTED_CA_R2_SEVERITY_COUNTS = {"critical": 0, "major": 0}
EXPECTED_CA_R2_MISSING_EXTERNAL_BINDINGS = {
    "sender_account",
    "observation_cutoff_at",
    "pre_send_source_refresh",
    "exact_user_authorization",
}
EXPECTED_CA_R2_REVIEWED_PROPERTIES = {
    (
        "The exact candidate binding set is unique and closed, includes the "
        "validator, adversarial tests, and all three superseded historical FAIL "
        "receipts, and every bound digest matches."
    ),
    (
        "The detached receipt gate enforces this exact schema, review ID, reviewer "
        "agent identity, zero Critical and Major findings, and a review time later "
        "than all three historical FAIL receipts."
    ),
    (
        "Execution-time freshness is checked independently against completion, "
        "CEC capture, and organization/channel capture; a newer source cannot "
        "mask a stale source."
    ),
    (
        "All authority- and result-critical active-state prose and refresh claim "
        "boundaries are exact, stage-dependent closed values; opposite-semantics "
        "mutations fail validation."
    ),
    (
        "Every controlled JSON byte boundary recursively rejects duplicate keys, "
        "including state authority fields and receipt verdict, identity, and "
        "external-action fields."
    ),
    "Both durable-evidence r1 major findings remain remediated in the candidate bytes.",
    (
        "All demand, payment, delivery, profit, repeatability, and asset claims "
        "remain false; no external action is authorized, and sender account, "
        "observation cutoff, fresh source records, and exact user authorization "
        "remain missing."
    ),
}
EXPECTED_CA_R2_CLAIM_BOUNDARY = (
    "This detached receipt records a read-only review of the exact internal "
    "candidate bytes. It does not authorize contact, follow-up, quoting, account "
    "access, submission, payment, delivery, publication, investment execution, "
    "or any claim of demand, willingness to pay, delivery feasibility, profit, "
    "repeatability, or asset value."
)
CA_R2_RECEIPT_KEYS = {
    "schema_version",
    "review_id",
    "recorded_at",
    "reviewer_agent_identity",
    "reviewer_role",
    "reviewer_modified_candidate",
    "verdict",
    "severity_counts",
    "candidate_bindings",
    "reviewed_properties",
    "external_action_status",
    "missing_external_bindings",
    "claim_boundary",
}
EXPECTED_CA_R2_CANDIDATE_PATHS = {
    "03-否决门与反方审查.md",
    "07-自主运行协议.md",
    "09-校验活动状态.py",
    "10-现实候选预筛与首个反证实验.md",
    "11-内部诊断页-CA012650.md",
    "12-首个反证实验与对外动作候选.md",
    "README.md",
    "tests/test_active_state_validator.py",
    "evidence/cec-building-benchmarking-prescreen-2026-07-27.json",
    "evidence/experiment-ca012650-internal-2026-07-27.json",
    "evidence/reproduce_cec_prescreen.py",
    "evidence/cec-building-benchmarking-reproduction-2026-07-27.json",
    "evidence/raw/CoveredBuildingsExport-2026-07-27.csv",
    "evidence/raw/2024_Download_ADA-2026-07-27.xlsx",
    "evidence/review-ca012650-durable-evidence-2026-07-27-r1.json",
    "evidence/review-ca012650-detached-gate-2026-07-27-attempt-1.json",
    "evidence/review-ca012650-detached-gate-2026-07-27-attempt-2.json",
}
EXPECTED_CA_R2_HISTORICAL_REJECTIONS = {
    "evidence/review-ca012650-durable-evidence-2026-07-27-r1.json": {
        "sha256": "6b122f068b46b5a3ba93aab03d17f0772be75913251ea8b69989cd4275c5fcaf",
        "review_id": "reviewer-ca012650-durable-evidence-2026-07-27-r1",
    },
    "evidence/review-ca012650-detached-gate-2026-07-27-attempt-1.json": {
        "sha256": "b1c723efb84d469e5a010a1b2b9087648502e85fc95294cf41a35348eb2704f0",
        "review_id": "review-ca012650-detached-gate-2026-07-27-attempt-1",
    },
    "evidence/review-ca012650-detached-gate-2026-07-27-attempt-2.json": {
        "sha256": "e2a2eedc3f84f6390f32983913c887500d842959324ce0e76e6ac50bd1ec7d69",
        "review_id": "review-ca012650-detached-gate-2026-07-27-attempt-2",
    },
}
EXPECTED_CA_INTERNAL_REVIEW_SCOPES = {
    "pending_fresh_review": (
        "The prior review was invalidated by durable raw-source and reproduction "
        "bindings; the exact current package awaits fresh independent review and "
        "authorizes no external action."
    ),
    "passed_current_candidate": (
        "The exact detached receipt passed only the current internal candidate "
        "closure; it does not validate demand, payment, delivery, profit, "
        "repeatability, asset value, current source freshness, or any external "
        "authorization."
    ),
}
EXPECTED_CA_REFRESH_CLAIM_BOUNDARIES = {
    "CEC status/address": (
        "This refresh establishes only the exact public record row, address, "
        "reporting year, and compliance status at capture time. It does not "
        "establish demand, payment, legal duty, ownership, delivery feasibility, "
        "or authority to contact."
    ),
    "organization/channel": (
        "This refresh establishes only current page liveness, organization "
        "identity, and a public routing channel at capture time. It does not "
        "establish recipient authority, consent, demand, payment, or authority "
        "to contact."
    ),
}
EXPECTED_CA_APPROVAL_CLAIM_BOUNDARIES = {
    "blocked_missing_bindings": (
        "Any future detached internal review PASS would not authorize sending and "
        "would not establish demand, payment, delivery, profit, repeatability, or "
        "an asset."
    ),
    "request_ready": (
        "Readiness proves only exact current source, sender, cutoff, target, channel, "
        "and message bindings. Sending remains unauthorized until an exact "
        "one-message user authorization receipt is bound."
    ),
    "authorized_once": (
        "Authorization covers exactly one bound message to the exact routing channel. "
        "It authorizes no follow-up, quote, payment, delivery, account access, or "
        "result claim, and it is consumed by one execution attempt."
    ),
    "executed_once": (
        "The exact one-message authorization has been consumed. Transport status "
        "does not prove demand, payment, delivery feasibility, profit, repeatability, "
        "or asset value, and no follow-up is authorized."
    ),
    "observing": (
        "Observation is passive until the bound cutoff. No follow-up, quote, payment, "
        "delivery, account access, or expansion of the result boundary is authorized."
    ),
    "closed": (
        "Closure records only the allowed outcome class and a no-follow-up chain. It "
        "does not by itself establish demand, payment, delivery feasibility, profit, "
        "repeatability, or asset value, and it authorizes no further action."
    ),
}
EXPECTED_STATIC_WORKSTREAM_SEMANTICS = {
    "long_term_capability_strategy": {
        "observed_facts": [
            {
                "claim_class": "observed",
                "claim": (
                    "本项目原始问题是数周到数年应长期学习与积累什么；Agent、Harness、"
                    "投研系统和单个市场 Probe 都是载体，不是北极星。"
                ),
                "evidence_locator": "00-项目北极星与三层结构.md",
            },
            {
                "claim_class": "inferred",
                "claim": (
                    "当前一手来源支持把可靠自主系统作为技术主轴，把需求、交易和"
                    "结果验证作为商业主轴；通用 Agent/Harness 机制值得深学，但通用"
                    "框架本身正在被平台化。"
                ),
                "evidence_locator": (
                    "13-长期能力投资地图与训练路线.md; "
                    "14-Agent-Harness与垂直适配独立复核.md"
                ),
            },
            {
                "claim_class": "observed",
                "claim": (
                    "本轮已独立获取并绑定黄仁勋与 LangChain 公开访谈的英文字幕身份；"
                    "访谈同时强调足够强的模型、Harness、领域信息、工具与后续 post-training，"
                    "而不是模型任意互换。"
                ),
                "evidence_locator": (
                    "evidence/jensen-open-agent-interview-caption-identity-2026-07-27.json"
                ),
            },
        ],
        "unknowns": [
            "哪个具体领域能让 Javen 合法取得真实工作流、设备、数据和责任人反馈",
            "跨模型与跨 Harness 的改进能否在未见案例和环境变化下稳定成立",
            "可靠自主系统与 EE/ML/Controls 的组合能否形成现实结果、交易或长期接入",
        ],
        "next_action": {
            "description": (
                "设计一个有外部验收的跨模型、跨 Harness 失败归因实验，并寻找一个经授权"
                "的 EE/ML/Controls 现实接口；不把完成课程或背框架 API 当作验收。"
            ),
            "scope": "unpublished_draft",
            "external_effect": False,
            "destructive": False,
        },
        "stop_conditions": [
            "学习产物只在看过的内部样本或公开 benchmark 上有效",
            "托管平台以更低全成本提供同等通用能力而项目仍重复造轮子",
            "长期无法取得真实领域接口、授权数据或责任人反馈",
            "所谓资产仍完全依赖 Javen 逐项判断与交付",
        ],
    },
    "investment_discipline": {
        "observed_facts": [
            {
                "claim_class": "observed",
                "claim": (
                    "精确干净候选绑定为 commit fed7d6694dc1b47490848b83e3ff0b56e04a3f39、"
                    "tree 2da5f0af186345da05738f971cb8afbdb6dac8db、parent "
                    "d8c108f81f84f4c5be99fe09902ace161bda5745。"
                ),
                "evidence_locator": "evidence/investment-candidate-audit-2026-07-27.json",
            },
            {
                "claim_class": "observed",
                "claim": (
                    "最新持久完整治理测试输出 Ran 532 tests in 862.542s 与 "
                    "FAILED (failures=40, errors=2)，因此候选未通过整体接纳。"
                ),
                "evidence_locator": "evidence/investment-candidate-audit-2026-07-27.json",
            },
            {
                "claim_class": "observed",
                "claim": (
                    "目标 no-live 测试输出 Ran 18 tests in 7.518s 与 OK，点时 no-live "
                    "verifier 也 pass；这只支持狭窄的 no-live 检查，不证明系统恢复、"
                    "运行、完整、安全或收益。"
                ),
                "evidence_locator": "evidence/investment-candidate-audit-2026-07-27.json",
            },
            {
                "claim_class": "observed",
                "claim": (
                    "独立根因审查已把完整治理测试的 failures/errors 分类为 metadata、"
                    "contract migration、stale receipt、stale freeze、shared-baseline "
                    "cascade 与 fixture gaps；独立持久 suite 转录复核确认 failure "
                    "headings 40、error headings 2，裁决仍为 NO_GO_BLOCKED_INTERNAL。"
                ),
                "evidence_locator": (
                    "evidence/review-investment-fed7-root-causes-2026-07-27.json; "
                    "evidence/review-investment-fed7-persisted-suite-2026-07-27.json"
                ),
            },
        ],
        "unknowns": [
            "可组合 successor recovery proof 的精确协议能否同时保留历史过渡证明并安全允许后续合法后代",
            "独立 successor candidate 按已分类根因顺序修复后能否通过 targeted suites 与完整 suite",
            "修复后的 exact successor 能否通过两份 candidate-bound 独立审查并形成真实 review envelope 和 full-history/tag bundle",
        ],
        "next_action": {
            "description": (
                "保持 fed7 及其持久 bundle 不变；只在新的隔离 successor candidate 中先设计"
                "可组合 recovery proof 与正反测试，再按已确认根因顺序修复；不创建"
                "追溯性 review tag，不运行恢复、启动、live 或 shadow 脚本。"
            ),
            "scope": "local_test",
            "external_effect": False,
            "destructive": False,
        },
        "stop_conditions": [
            "候选 commit、tree 或 parent 身份变化",
            "工作树不再干净或验证结果无法绑定到精确候选",
            "任何整体接纳检查仍失败或关键覆盖不可用",
            "任何动作会越过 paper-only 或 human-final",
        ],
    },
}
EXPECTED_OPPORTUNITY_FIRST_FACT = {
    "claim_class": "observed",
    "claim": (
        "旧 schema/workspace 0.1 已全局 tombstone；保留 API 与 CLI 均 fail closed，"
        "根测试输出 Ran 6 tests 与 OK，独立复审结论为 PASS。这个 PASS 只证明"
        "旧运行时被隔离，不证明存在新的可运行系统。"
    ),
    "evidence_locator": "evidence/review-legacy-opportunity-tombstone-2026-07-27.json",
}
EXPECTED_OPPORTUNITY_REVIEW_FACTS = {
    "pending_fresh_review": {
        "claim_class": "observed",
        "claim": (
            "CA012650 内部实验包新增了持久公开源字节、确定性转换脚本与复现记录；"
            "这使旧独立复审失效，当前精确候选正在等待新的独立复审，任何发送仍未获授权。"
        ),
        "evidence_locator": (
            "evidence/experiment-ca012650-internal-2026-07-27.json; "
            "evidence/cec-building-benchmarking-reproduction-2026-07-27.json"
        ),
    },
    "passed_current_candidate": {
        "claim_class": "observed",
        "claim": (
            "CA012650 内部实验包的持久公开源字节、确定性转换脚本、复现"
            "记录、校验器与对抗测试已由当前精确 detached receipt 独立复核为 PASS；"
            "该 PASS 只支持内部候选闭包，不证明需求、付款、交付、利润、复购或资产价值，"
            "也不授权任何发送。"
        ),
        "evidence_locator": (
            "evidence/review-ca012650-durable-candidate-2026-07-27-r2.json"
        ),
    },
}
EXPECTED_OPPORTUNITY_STAGE_FACT_CLAIMS = {
    "blocked_missing_bindings": (
        "发送账户、观察截止时间、发送前公开源刷新和精确用户授权均未绑定，"
        "external_contact_authorized 为 false。"
    ),
    "request_ready": (
        "发送账户、观察截止和临发送公开源刷新已由 readiness receipt 精确绑定；"
        "精确用户授权仍未绑定，external_contact_authorized 为 false，尚不得发送。"
    ),
    "authorized_once": (
        "精确一次性用户授权已绑定但尚未执行；授权仅覆盖已绑定的一条消息，"
        "不含跟进、报价、付款、交付、账户访问或任何结果声明。"
    ),
    "executed_once": (
        "精确一次性授权已被一条消息执行消费；transport status 只记录传输，"
        "不证明需求、付款、交付、利润、复购或资产价值，且不得跟进。"
    ),
    "observing": (
        "单条消息执行完毕并处于被动观察；不得跟进，且截止前任何沉默、退信、"
        "自动回复或 transport acceptance 都不得解释为需求或付款意愿。"
    ),
    "closed": (
        "观察已由 closure receipt 关闭；未发送跟进，结果只能按允许的 outcome "
        "class 解释，本 schema 中所有需求、付款、交付、利润、复购和资产声明仍为 false。"
    ),
}
EXPECTED_OPPORTUNITY_STAGE_RECEIPT_FIELDS = {
    "request_ready": "readiness_receipt",
    "authorized_once": "authorization_receipt",
    "executed_once": "execution_receipt",
    "observing": "observation_receipt",
    "closed": "closure_receipt",
}
EXPECTED_OPPORTUNITY_UNKNOWNS = [
    "当前公开状态是否对应目标组织尚未解决的问题",
    "公开组织邮箱能否把问题路由给拥有授权的人",
    "是否存在真实需求或付款意愿",
    "是否能够准确交付并形成正向利润",
    "是否会复购以及能否沉淀为可重复资产",
]
EXPECTED_OPPORTUNITY_STOP_CONDITIONS = [
    "发送前公开源显示记录已经解决、豁免或目标错误",
    "目标组织要求停止联系或路由身份被反证",
    "任何必需绑定仍为空或用户未精确授权",
    "动作扩大为报价、交付、付款、账户访问或自动跟进",
]
EXPECTED_OPPORTUNITY_ACTIONS = {
    "blocked_missing_bindings": {
        "description": (
            "保持不发送；只有在精确发送账户、精确观察截止、临发送公开源刷新"
            "和用户对精确消息的授权全部绑定后，才可重新进入发送前校验。"
        ),
        "scope": "unpublished_draft",
        "external_effect": False,
        "destructive": False,
    },
    "request_ready": {
        "description": (
            "保持不发送；只可在本地核对 readiness receipt 和精确消息，并等待用户"
            "对这一条消息的精确一次性授权。"
        ),
        "scope": "unpublished_draft",
        "external_effect": False,
        "destructive": False,
    },
    "authorized_once": {
        "description": (
            "保持不自动发送；只可在本地核对 authorization receipt 与一次性执行前条件，"
            "任何外部执行都必须由另一个精确、单次、可审计的执行门消费授权。"
        ),
        "scope": "local_test",
        "external_effect": False,
        "destructive": False,
    },
    "executed_once": {
        "description": "不发送任何后续消息；只在本地核对 execution receipt，并等待进入被动观察。",
        "scope": "local_test",
        "external_effect": False,
        "destructive": False,
    },
    "observing": {
        "description": "不跟进；只在本地等待观察截止并记录允许的被动结果分类。",
        "scope": "local_test",
        "external_effect": False,
        "destructive": False,
    },
    "closed": {
        "description": "保持关闭且不跟进；只在本地保留收据链和结果边界。",
        "scope": "local_test",
        "external_effect": False,
        "destructive": False,
    },
}
EXPECTED_DURABLE_REPRODUCTION = {
    "raw/CoveredBuildingsExport-2026-07-27.csv": {
        "bytes": 3919934,
        "sha256": "8a996c43d04a8a690d60087c361e6f9580e1492868ee367f9958ff0b1a23bb75",
    },
    "raw/2024_Download_ADA-2026-07-27.xlsx": {
        "bytes": 5668934,
        "sha256": "dab1834454bd5ff6c17d9240e978084dd2a4f59c5ee02e7ee2ad70d266b65b00",
    },
}
EXPECTED_REPRODUCTION_SCRIPT = {
    "path": "reproduce_cec_prescreen.py",
    "sha256": "814ad0dd926404370a14f1ef557eca881c9717dfadbf0b78826adb621410e9db",
}
EXPECTED_REPRODUCTION_RECORD = {
    "path": "cec-building-benchmarking-reproduction-2026-07-27.json",
    "sha256": "d711cd145207961d85e57e6be8f97972283678820de32323a47f596ef8ef4dc2",
}

APPROVAL_STAGES = (
    "blocked_missing_bindings",
    "request_ready",
    "authorized_once",
    "executed_once",
    "observing",
    "closed",
)
PREVIOUS_APPROVAL_STAGE = {
    "blocked_missing_bindings": None,
    "request_ready": "blocked_missing_bindings",
    "authorized_once": "request_ready",
    "executed_once": "authorized_once",
    "observing": "executed_once",
    "closed": "observing",
}
STAGE_RECEIPTS = (
    "readiness_receipt",
    "authorization_receipt",
    "execution_receipt",
    "observation_receipt",
    "closure_receipt",
)
RECEIPT_STAGE_PAIRS = {
    "readiness_receipt": ("blocked_missing_bindings", "request_ready"),
    "authorization_receipt": ("request_ready", "authorized_once"),
    "execution_receipt": ("authorized_once", "executed_once"),
    "observation_receipt": ("executed_once", "observing"),
    "closure_receipt": ("observing", "closed"),
}
EXPERIMENT_ACTION_STATUS_BY_STAGE = {
    "blocked_missing_bindings": "blocked",
    "request_ready": "pending_authorization",
    "authorized_once": "authorized_once",
    "executed_once": "executed_once",
    "observing": "observing",
    "closed": "closed",
}
OPPORTUNITY_STATUS_BY_STAGE = {
    "blocked_missing_bindings": "blocked_external",
    "request_ready": "blocked_external",
    "authorized_once": "blocked_external",
    "executed_once": "observation_only",
    "observing": "observation_only",
    "closed": "stopped",
}

TOP_LEVEL_KEYS = {
    "schema_version",
    "as_of",
    "freshness_policy",
    "state_scope",
    "truth_policy",
    "authority_envelope",
    "workstreams",
    "approval_queue",
}
TRUTH_POLICY_KEYS = {
    "old_documents_are_authority",
    "ai_summary_is_evidence",
    "required_claim_classes",
}
AUTHORITY_ENVELOPE_KEYS = {
    "default",
    "autonomous_scopes",
    "explicit_approval_required",
    "hard_boundaries",
}
HARD_BOUNDARY_KEYS = {
    "investment_paper_only",
    "investment_human_final",
    "broker_connection_allowed",
    "live_order_allowed",
}
FRESHNESS_POLICY_KEYS = {
    "max_age_hours",
    "pre_send_refresh_max_age_hours",
    "refresh_due_at",
    "on_stale",
}
FACT_KEYS = {"claim_class", "claim", "evidence_locator"}
NEXT_ACTION_KEYS = {"description", "scope", "external_effect", "destructive"}
BINDING_KEYS = {"path", "sha256"}
COMMON_WORKSTREAM_KEYS = {
    "id",
    "path",
    "classification",
    "status",
    "observed_facts",
    "unknowns",
    "next_action",
    "stop_conditions",
}
WORKSTREAM_KEYS = {
    "long_term_capability_strategy": COMMON_WORKSTREAM_KEYS | {"strategy_artifacts"},
    "opportunity_to_transaction": COMMON_WORKSTREAM_KEYS
    | {"independent_reviews", "current_experiment"},
    "investment_discipline": COMMON_WORKSTREAM_KEYS
    | {"candidate_audit", "safety_boundary"},
}
REVIEW_STATE_KEYS = {"path", "sha256", "verdict"}
CURRENT_EXPERIMENT_KEYS = {
    "experiment_id",
    "spec_path",
    "spec_sha256",
    "internal_review_result",
    "internal_review_scope",
    "external_action_status",
    "external_contact_authorized",
    "result_claims",
}
CANDIDATE_AUDIT_KEYS = {"path", "sha256", "overall_acceptance"}
SAFETY_BOUNDARY_KEYS = {
    "paper_only",
    "human_final",
    "live_trading",
    "broker_integration",
}
APPROVAL_KEYS = {
    "id",
    "action",
    "experiment_id",
    "status",
    "external_effect",
    "authorized",
    "ready",
    "executable",
    "authorization_consumed",
    "exact_target",
    "exact_channel",
    "channel_source",
    "message_binding",
    "sender_account",
    "observation_cutoff_at",
    "pre_send_source_refresh",
    "exact_user_authorization",
    "missing_bindings",
    "lifecycle",
    "claim_boundary",
}
APPROVAL_TARGET_KEYS = {
    "public_building_id",
    "public_record_location",
    "routing_contact_only",
}
SOURCE_REFRESH_KEYS = {
    "status",
    "completed_at",
    "cec_status_record",
    "organization_channel_record",
}
LIFECYCLE_KEYS = {"stage", "previous_stage", *STAGE_RECEIPTS}
RECEIPT_ROOT_KEYS = {
    "schema_version",
    "receipt_type",
    "approval_id",
    "experiment_id",
    "from_stage",
    "to_stage",
    "recorded_at",
    "exact_target",
    "exact_channel",
    "channel_source",
    "message_binding",
    "stage_payload",
}


def exact_object(
    value: object, expected_keys: set[str], *, errors: list[str], label: str
) -> bool:
    if not isinstance(value, dict):
        errors.append(f"{label}: must be an object")
        return False
    actual = set(value)
    missing = sorted(expected_keys - actual)
    unknown = sorted(actual - expected_keys)
    if missing:
        errors.append(f"{label}: missing fields {missing}")
    if unknown:
        errors.append(f"{label}: unknown fields {unknown}")
    return not missing and not unknown


def exact_string_set(
    value: object, expected: set[str], *, errors: list[str], label: str
) -> bool:
    if not isinstance(value, list) or any(
        not isinstance(item, str) or not item for item in value
    ):
        errors.append(f"{label}: must be a list of non-empty strings")
        return False
    if len(value) != len(set(value)):
        errors.append(f"{label}: duplicates are forbidden")
    if set(value) != expected:
        errors.append(f"{label}: exact required set changed")
    return len(value) == len(expected) and set(value) == expected


def nonempty_list(value: object) -> bool:
    return isinstance(value, list) and bool(value) and all(
        isinstance(item, str) and item.strip() for item in value
    )


def parse_timestamp(value: object, *, errors: list[str], label: str) -> datetime | None:
    if not isinstance(value, str) or not value.strip():
        errors.append(f"{label}: missing timestamp")
        return None
    try:
        parsed = datetime.fromisoformat(value)
    except ValueError:
        errors.append(f"{label}: invalid RFC 3339 timestamp")
        return None
    if parsed.tzinfo is None:
        errors.append(f"{label}: timestamp must include an offset")
        return None
    return parsed


def validate_not_future(
    value: object, *, now: datetime, errors: list[str], label: str
) -> datetime | None:
    parsed = parse_timestamp(value, errors=errors, label=label)
    if parsed is not None and parsed.astimezone(timezone.utc) > now:
        errors.append(f"{label}: timestamp is in the future")
    return parsed


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _has_symlink_component(path: Path) -> bool:
    if not path.is_absolute():
        raise ValueError("symlink inspection requires an absolute path")
    current = Path(path.anchor)
    for part in path.parts[1:]:
        if part in ("", "."):
            continue
        if part == "..":
            current = current.parent
            continue
        current = current / part
        if current.is_symlink():
            return True
    return False


def _inside(path: Path, root: Path) -> bool:
    return path == root or root in path.parents


def _secure_regular_file(
    raw_path: str, *, base: Path, allowed_root: Path
) -> tuple[Path | None, str | None]:
    candidate = Path(raw_path)
    if candidate.is_absolute():
        return None, "absolute paths are forbidden"
    lexical = base / candidate
    if _has_symlink_component(lexical):
        return None, "symlink components are forbidden"
    try:
        resolved = lexical.resolve(strict=True)
    except (OSError, RuntimeError):
        return None, "path does not resolve"
    allowed = allowed_root.resolve()
    if not _inside(resolved, allowed):
        return None, "path escapes its allowed evidence root"
    try:
        mode = os.lstat(resolved).st_mode
    except OSError:
        return None, "path cannot be inspected"
    if not stat.S_ISREG(mode):
        return None, "path is not a regular file"
    return resolved, None


def confined_file(
    raw_path: object,
    *,
    base: Path,
    errors: list[str],
    label: str,
    allowed_root: Path = RESEARCH_ROOT,
) -> Path | None:
    if not isinstance(raw_path, str) or not raw_path.strip():
        errors.append(f"{label}: missing path")
        return None
    resolved, reason = _secure_regular_file(
        raw_path, base=base, allowed_root=allowed_root
    )
    if resolved is None:
        errors.append(f"{label}: {reason}")
    return resolved


def verify_bound_file(
    binding: object,
    *,
    base: Path,
    errors: list[str],
    label: str,
    allowed_root: Path = RESEARCH_ROOT,
    closed: bool = False,
) -> Path | None:
    if not isinstance(binding, dict):
        errors.append(f"{label}: binding must be an object")
        return None
    if closed:
        exact_object(binding, BINDING_KEYS, errors=errors, label=f"{label} binding")
    path = confined_file(
        binding.get("path"),
        base=base,
        errors=errors,
        label=label,
        allowed_root=allowed_root,
    )
    expected = binding.get("sha256")
    if not isinstance(expected, str) or not SHA256_RE.fullmatch(expected):
        errors.append(f"{label}: sha256 must be an exact lowercase digest")
        return path
    if path is not None and sha256_file(path) != expected:
        errors.append(f"{label}: sha256 mismatch")
    return path


class DuplicateJSONKeyError(ValueError):
    def __init__(self, key: str) -> None:
        self.key = key
        super().__init__(f"duplicate JSON key {key!r}")


def _strict_json_object(pairs: list[tuple[str, object]]) -> dict:
    value: dict[str, object] = {}
    for key, item in pairs:
        if key in value:
            raise DuplicateJSONKeyError(key)
        value[key] = item
    return value


def loads_json_strict(raw: str) -> object:
    """Parse JSON bytes with recursive duplicate-object-key rejection."""

    return json.loads(raw, object_pairs_hook=_strict_json_object)


def load_json(path: Path, *, errors: list[str], label: str) -> dict | None:
    try:
        value = loads_json_strict(path.read_text(encoding="utf-8"))
    except DuplicateJSONKeyError as exc:
        errors.append(f"{label}: duplicate JSON key rejected: {exc.key!r}")
        return None
    except (OSError, UnicodeError, json.JSONDecodeError):
        errors.append(f"{label}: unreadable or invalid JSON")
        return None
    if not isinstance(value, dict):
        errors.append(f"{label}: JSON root must be an object")
        return None
    return value


def validate_freshness(
    state: dict, *, now: datetime, errors: list[str]
) -> datetime | None:
    as_of = validate_not_future(
        state.get("as_of"), now=now, errors=errors, label="active state as_of"
    )
    policy = state.get("freshness_policy")
    if not exact_object(
        policy, FRESHNESS_POLICY_KEYS, errors=errors, label="freshness_policy"
    ):
        return as_of
    assert isinstance(policy, dict)
    if policy.get("max_age_hours") != EXPECTED_MAX_AGE_HOURS:
        errors.append("freshness_policy: max_age_hours changed")
    if policy.get("pre_send_refresh_max_age_hours") != (
        PRE_SEND_REFRESH_MAX_AGE_HOURS
    ):
        errors.append("freshness_policy: pre_send_refresh_max_age_hours changed")
    if policy.get("on_stale") != "fail_closed":
        errors.append("freshness_policy: on_stale must be fail_closed")
    due = parse_timestamp(
        policy.get("refresh_due_at"), errors=errors, label="freshness_policy refresh_due_at"
    )
    if as_of is not None and due is not None:
        expected_due = as_of + timedelta(hours=EXPECTED_MAX_AGE_HOURS)
        if due != expected_due:
            errors.append("freshness_policy: refresh_due_at does not equal as_of plus max age")
        if due <= as_of:
            errors.append("freshness_policy: refresh_due_at must be after as_of")
        if now > due.astimezone(timezone.utc):
            errors.append("active state is stale and must fail closed until refreshed")
    return as_of


def validate_declared_workstream_root(
    stream: dict, *, errors: list[str], label: str
) -> Path | None:
    stream_id = stream.get("id")
    expected_raw = EXPECTED_WORKSTREAM_PATHS.get(stream_id)
    if stream.get("path") != expected_raw:
        errors.append(f"{label}: declared project path changed")
        return None
    root = EXPECTED_WORKSTREAM_ROOTS.get(stream_id)
    if root is None:
        return None
    lexical = RESEARCH_ROOT / expected_raw
    if _has_symlink_component(lexical):
        errors.append(f"{label}: declared project root contains a symlink")
        return None
    try:
        resolved = lexical.resolve(strict=True)
    except (OSError, RuntimeError):
        errors.append(f"{label}: declared project root does not resolve")
        return None
    if resolved != root or not resolved.is_dir():
        errors.append(f"{label}: declared project root is not the exact allowed directory")
        return None
    return resolved


def validate_evidence_locator(
    locator: object,
    *,
    stream_root: Path | None,
    errors: list[str],
    label: str,
) -> None:
    if not isinstance(locator, str) or not locator.strip():
        errors.append(f"{label}: missing evidence_locator")
        return
    parts = [part.strip() for part in locator.split(";")]
    if not parts or any(not part for part in parts):
        errors.append(f"{label}: evidence_locator contains an empty item")
        return
    if len(parts) != len(set(parts)):
        errors.append(f"{label}: duplicate evidence locator")
    roots = [RESEARCH_ROOT]
    if stream_root is not None and stream_root != RESEARCH_ROOT:
        roots.append(stream_root)
    for index, raw in enumerate(parts):
        candidate = Path(raw)
        if candidate.is_absolute() or ".." in candidate.parts:
            errors.append(
                f"{label}[{index}]: evidence locator must be a confined relative path"
            )
            continue
        matches: set[Path] = set()
        security_errors: list[str] = []
        for root in roots:
            lexical = root / candidate
            if not lexical.exists() and not lexical.is_symlink():
                continue
            resolved, reason = _secure_regular_file(raw, base=root, allowed_root=root)
            if resolved is not None:
                matches.add(resolved)
            elif reason is not None:
                security_errors.append(reason)
        if security_errors:
            errors.append(f"{label}[{index}]: {security_errors[0]}")
        elif not matches:
            errors.append(f"{label}[{index}]: locator does not resolve to a real file")
        elif len(matches) != 1:
            errors.append(f"{label}[{index}]: locator is ambiguous across allowed roots")


def validate_common_workstream(
    stream: dict, *, now: datetime, errors: list[str]
) -> Path | None:
    stream_id = stream.get("id")
    prefix = f"workstream {stream_id or '<missing>'}:"
    expected_keys = WORKSTREAM_KEYS.get(stream_id)
    if expected_keys is None:
        errors.append(f"{prefix} unknown workstream id")
        return None
    exact_object(stream, expected_keys, errors=errors, label=prefix)
    if stream.get("classification") != EXPECTED_WORKSTREAM_CLASSIFICATIONS[stream_id]:
        errors.append(f"{prefix} classification changed")
    if stream.get("status") not in ALLOWED_STATUSES:
        errors.append(f"{prefix} invalid status")
    stream_root = validate_declared_workstream_root(stream, errors=errors, label=prefix)

    if not nonempty_list(stream.get("unknowns")):
        errors.append(f"{prefix} unknowns must be explicit and non-empty")
    if not nonempty_list(stream.get("stop_conditions")):
        errors.append(f"{prefix} stop_conditions must be explicit and non-empty")

    facts = stream.get("observed_facts")
    if not isinstance(facts, list) or not facts:
        errors.append(f"{prefix} observed_facts must be non-empty")
    else:
        for index, fact in enumerate(facts):
            fact_prefix = f"{prefix} fact {index}"
            if not exact_object(fact, FACT_KEYS, errors=errors, label=fact_prefix):
                continue
            assert isinstance(fact, dict)
            if fact.get("claim_class") not in ALLOWED_CLAIM_CLASSES:
                errors.append(f"{fact_prefix}: invalid claim_class")
            if not isinstance(fact.get("claim"), str) or not fact["claim"].strip():
                errors.append(f"{fact_prefix}: missing claim")
            validate_evidence_locator(
                fact.get("evidence_locator"),
                stream_root=stream_root,
                errors=errors,
                label=f"{fact_prefix} evidence_locator",
            )

    action = stream.get("next_action")
    if exact_object(action, NEXT_ACTION_KEYS, errors=errors, label=f"{prefix} next_action"):
        assert isinstance(action, dict)
        if not isinstance(action.get("description"), str) or not action[
            "description"
        ].strip():
            errors.append(f"{prefix} next action description is empty")
        if action.get("scope") not in AUTONOMOUS_SCOPES:
            errors.append(f"{prefix} next action is outside autonomous scopes")
        if action.get("external_effect") is not False:
            errors.append(f"{prefix} next action must have external_effect=false")
        if action.get("destructive") is not False:
            errors.append(f"{prefix} next action must have destructive=false")
    return stream_root


def validate_static_workstream_semantics(stream: dict, errors: list[str]) -> None:
    """Close human-readable authority/result semantics for fixed snapshots."""

    stream_id = stream.get("id")
    expected = EXPECTED_STATIC_WORKSTREAM_SEMANTICS.get(stream_id)
    if expected is None:
        return
    prefix = f"workstream {stream_id} semantic closure:"
    for field in ("observed_facts", "unknowns", "next_action", "stop_conditions"):
        if stream.get(field) != expected[field]:
            errors.append(f"{prefix} {field} differs from the exact closed value")


def validate_opportunity_semantics(
    stream: dict,
    *,
    ca_review_status: str,
    stage: str,
    approval_item: object,
    errors: list[str],
) -> None:
    """Deterministically render every authority/result-critical opportunity prose field."""

    prefix = "opportunity semantic closure:"
    review_fact = EXPECTED_OPPORTUNITY_REVIEW_FACTS.get(ca_review_status)
    stage_claim = EXPECTED_OPPORTUNITY_STAGE_FACT_CLAIMS.get(stage)
    action = EXPECTED_OPPORTUNITY_ACTIONS.get(stage)
    if review_fact is None or stage_claim is None or action is None:
        errors.append(f"{prefix} review status or lifecycle stage has no closed rendering")
        return

    if stage == "blocked_missing_bindings":
        stage_locator: object = "evidence/experiment-ca012650-internal-2026-07-27.json"
    else:
        receipt_field = EXPECTED_OPPORTUNITY_STAGE_RECEIPT_FIELDS.get(stage)
        lifecycle = (
            approval_item.get("lifecycle") if isinstance(approval_item, dict) else None
        )
        binding = (
            lifecycle.get(receipt_field)
            if isinstance(lifecycle, dict) and isinstance(receipt_field, str)
            else None
        )
        stage_locator = binding.get("path") if isinstance(binding, dict) else None
    expected_facts = [
        EXPECTED_OPPORTUNITY_FIRST_FACT,
        review_fact,
        {
            "claim_class": "observed",
            "claim": stage_claim,
            "evidence_locator": stage_locator,
        },
    ]
    if stream.get("observed_facts") != expected_facts:
        errors.append(f"{prefix} observed_facts differ from exact stage rendering")
    if stream.get("unknowns") != EXPECTED_OPPORTUNITY_UNKNOWNS:
        errors.append(f"{prefix} unknowns differ from the exact closed value")
    if stream.get("stop_conditions") != EXPECTED_OPPORTUNITY_STOP_CONDITIONS:
        errors.append(f"{prefix} stop_conditions differ from the exact closed value")
    if stream.get("next_action") != action:
        errors.append(f"{prefix} next_action differs from exact stage rendering")


def validate_strategy(stream: dict, errors: list[str]) -> None:
    if stream.get("status") != "active_internal":
        errors.append("long-term capability strategy must remain active_internal")
    artifacts = stream.get("strategy_artifacts")
    if not isinstance(artifacts, list):
        errors.append("long-term capability strategy artifacts must be a list")
        return
    observed_paths: list[str] = []
    resolved_paths: set[Path] = set()
    for index, binding in enumerate(artifacts):
        label = f"long-term strategy artifact[{index}]"
        if isinstance(binding, dict):
            exact_object(binding, BINDING_KEYS, errors=errors, label=f"{label} binding")
            raw = binding.get("path")
            if isinstance(raw, str):
                observed_paths.append(raw)
        path = verify_bound_file(
            binding,
            base=RESEARCH_ROOT,
            errors=errors,
            label=label,
            closed=False,
        )
        if path is not None:
            if path in resolved_paths:
                errors.append("long-term strategy artifacts contain a duplicate file")
            resolved_paths.add(path)
    if len(observed_paths) != len(set(observed_paths)):
        errors.append("long-term strategy artifact paths must be unique")
    if set(observed_paths) != EXPECTED_STRATEGY_ARTIFACT_PATHS or len(
        artifacts
    ) != len(EXPECTED_STRATEGY_ARTIFACT_PATHS):
        errors.append("long-term strategy artifacts are not the exact expected set")


def validate_durable_reproduction(
    prescreen_path: Path, *, now: datetime, errors: list[str]
) -> None:
    """Verify that the public source bytes and deterministic reproduction are durable.

    This checks byte identity and the recorded transformation chain only. It does
    not re-download sources or promote the reproduced observations into demand.
    """

    prefix = "CEC durable reproduction:"
    prescreen = load_json(prescreen_path, errors=errors, label=f"{prefix} prescreen")
    if prescreen is None:
        return
    durable = prescreen.get("durable_reproduction")
    durable_keys = {
        "redownload_and_reproduction_verified_at",
        "raw_files",
        "transformation_script",
        "reproduction_record",
    }
    if not exact_object(durable, durable_keys, errors=errors, label=f"{prefix} binding"):
        return
    assert isinstance(durable, dict)
    verified_at = validate_not_future(
        durable.get("redownload_and_reproduction_verified_at"),
        now=now,
        errors=errors,
        label=f"{prefix} verified_at",
    )

    raw_files = durable.get("raw_files")
    observed_raw: dict[str, dict] = {}
    if not isinstance(raw_files, list):
        errors.append(f"{prefix} raw_files must be a list")
    else:
        for index, binding in enumerate(raw_files):
            label = f"{prefix} raw_files[{index}]"
            if not exact_object(
                binding, {"path", "bytes", "sha256"}, errors=errors, label=label
            ):
                continue
            assert isinstance(binding, dict)
            raw_path = binding.get("path")
            if not isinstance(raw_path, str):
                errors.append(f"{label}: path must be a string")
                continue
            if raw_path in observed_raw:
                errors.append(f"{prefix} duplicate raw file path")
            observed_raw[raw_path] = binding
            file_path = verify_bound_file(
                binding,
                base=prescreen_path.parent,
                errors=errors,
                label=label,
            )
            if file_path is not None and file_path.stat().st_size != binding.get("bytes"):
                errors.append(f"{label}: byte length mismatch")
    if set(observed_raw) != set(EXPECTED_DURABLE_REPRODUCTION):
        errors.append(f"{prefix} raw file set changed")
    for raw_path, expected in EXPECTED_DURABLE_REPRODUCTION.items():
        if observed_raw.get(raw_path) != {"path": raw_path, **expected}:
            errors.append(f"{prefix} {raw_path} bytes or digest changed")

    script_binding = durable.get("transformation_script")
    if not exact_object(
        script_binding, BINDING_KEYS, errors=errors, label=f"{prefix} script binding"
    ) or script_binding != EXPECTED_REPRODUCTION_SCRIPT:
        errors.append(f"{prefix} transformation script binding changed")
    verify_bound_file(
        script_binding,
        base=prescreen_path.parent,
        errors=errors,
        label=f"{prefix} transformation script",
    )

    record_binding = durable.get("reproduction_record")
    if not exact_object(
        record_binding, BINDING_KEYS, errors=errors, label=f"{prefix} record binding"
    ) or record_binding != EXPECTED_REPRODUCTION_RECORD:
        errors.append(f"{prefix} reproduction record binding changed")
    record_path = verify_bound_file(
        record_binding,
        base=prescreen_path.parent,
        errors=errors,
        label=f"{prefix} reproduction record",
    )
    if record_path is None:
        return
    record = load_json(record_path, errors=errors, label=f"{prefix} reproduction record")
    if record is None:
        return
    reproduced_at = validate_not_future(
        record.get("reproduced_at"),
        now=now,
        errors=errors,
        label=f"{prefix} reproduced_at",
    )
    if verified_at is not None and reproduced_at != verified_at:
        errors.append(f"{prefix} prescreen and record timestamps differ")
    if record.get("schema_version") != "cec-prescreen-reproduction-record/1":
        errors.append(f"{prefix} reproduction record schema changed")

    execution = record.get("execution")
    if not isinstance(execution, dict):
        errors.append(f"{prefix} execution record is missing")
    else:
        if execution.get("exit_code") != 0:
            errors.append(f"{prefix} reproduction execution did not exit zero")
        if execution.get("script_path") != EXPECTED_REPRODUCTION_SCRIPT["path"]:
            errors.append(f"{prefix} executed script path changed")
        if execution.get("script_sha256") != EXPECTED_REPRODUCTION_SCRIPT["sha256"]:
            errors.append(f"{prefix} executed script digest changed")

    record_sources = record.get("sources")
    if not isinstance(record_sources, dict) or set(record_sources) != {
        "covered",
        "submitted",
    }:
        errors.append(f"{prefix} reproduction source set changed")
    else:
        record_by_path = {
            source.get("path"): source
            for source in record_sources.values()
            if isinstance(source, dict)
        }
        for raw_path, expected in EXPECTED_DURABLE_REPRODUCTION.items():
            source = record_by_path.get(raw_path)
            if not isinstance(source, dict):
                errors.append(f"{prefix} record omits {raw_path}")
            elif source.get("bytes") != expected["bytes"] or source.get(
                "sha256"
            ) != expected["sha256"]:
                errors.append(f"{prefix} record source identity changed for {raw_path}")

    selected = record.get("selected_target_observations")
    covered = selected.get("covered_2026_row") if isinstance(selected, dict) else None
    submitted = (
        selected.get("submitted_2024_exact_address_city_row")
        if isinstance(selected, dict)
        else None
    )
    if not isinstance(covered, dict) or (
        covered.get("Building ID") != "Building #CA012650"
        or covered.get("Street") != "800 bay marina drive"
        or covered.get("City") != "national city"
        or covered.get("Compliance Status") != "not submitted"
    ):
        errors.append(f"{prefix} selected current target observation changed")
    if not isinstance(submitted, dict) or (
        submitted.get("Standard ID") != "CA012650"
        or submitted.get("Address 1") != "800 bay marina drive"
        or submitted.get("City") != "national city"
    ):
        errors.append(f"{prefix} selected prior target observation changed")


def validate_experiment(
    stream: dict,
    *,
    ca_review_status: str,
    now: datetime,
    errors: list[str],
) -> tuple[dict | None, Path | None]:
    prefix = "opportunity experiment:"
    current = stream.get("current_experiment")
    if not exact_object(
        current, CURRENT_EXPERIMENT_KEYS, errors=errors, label=f"{prefix} current_experiment"
    ):
        return None, None
    assert isinstance(current, dict)
    if current.get("experiment_id") != EXPECTED_CA_EXPERIMENT_ID:
        errors.append(f"{prefix} unexpected experiment_id")
    if current.get("spec_path") != (
        "evidence/experiment-ca012650-internal-2026-07-27.json"
    ):
        errors.append(f"{prefix} spec path changed")
    expected_review_result = (
        "PASS" if ca_review_status == "passed_current_candidate" else "PENDING_FRESH_REVIEW"
    )
    if current.get("internal_review_result") != expected_review_result:
        errors.append(f"{prefix} state review result does not match current receipt status")
    expected_review_scope = EXPECTED_CA_INTERNAL_REVIEW_SCOPES.get(ca_review_status)
    if current.get("internal_review_scope") != expected_review_scope:
        errors.append(f"{prefix} internal review scope differs from exact review status")
    results = current.get("result_claims")
    if not exact_object(
        results,
        REQUIRED_FALSE_EXPERIMENT_RESULTS,
        errors=errors,
        label=f"{prefix} state result_claims",
    ):
        results = None
    if isinstance(results, dict) and any(value is not False for value in results.values()):
        errors.append(f"{prefix} current unvalidated result claims must remain false")

    spec_binding = {
        "path": current.get("spec_path"),
        "sha256": current.get("spec_sha256"),
    }
    spec_path = verify_bound_file(
        spec_binding, base=RESEARCH_ROOT, errors=errors, label=f"{prefix} spec"
    )
    if spec_path is None:
        return None, None
    experiment = load_json(spec_path, errors=errors, label=f"{prefix} spec")
    if experiment is None:
        return None, spec_path

    if experiment.get("experiment_id") != current.get("experiment_id"):
        errors.append(f"{prefix} experiment_id mismatch")
    captured_at = validate_not_future(
        experiment.get("captured_at"), now=now, errors=errors, label=f"{prefix} captured_at"
    )
    if experiment.get("internal_review_recorded_at") is not None:
        errors.append(
            f"{prefix} candidate must not self-record detached review time or verdict"
        )
    if experiment.get("status") != "blocked_before_external_action":
        errors.append(f"{prefix} historical internal candidate status changed")

    authority = experiment.get("authority")
    expected_authority_keys = {"internal_research_authorized"} | REQUIRED_FALSE_EXPERIMENT_AUTHORITY
    if exact_object(
        authority, expected_authority_keys, errors=errors, label=f"{prefix} authority"
    ):
        assert isinstance(authority, dict)
        if authority.get("internal_research_authorized") is not True:
            errors.append(f"{prefix} internal research authority is not explicit")
        for key in sorted(REQUIRED_FALSE_EXPERIMENT_AUTHORITY):
            if authority.get(key) is not False:
                errors.append(f"{prefix} historical authority {key} must be false")

    sender = experiment.get("sender_binding")
    if not isinstance(sender, dict):
        errors.append(f"{prefix} sender_binding must be an object")
    elif sender.get("sending_account") is not None or sender.get(
        "sending_account_status"
    ) != "unbound":
        errors.append(f"{prefix} historical sending account binding changed")
    if experiment.get("observation_cutoff_at") is not None:
        errors.append(f"{prefix} historical observation cutoff binding changed")

    bound_inputs = experiment.get("bound_inputs")
    seen_paths: set[Path] = set()
    role_counts: dict[str, int] = {}
    prescreen_path: Path | None = None
    if not isinstance(bound_inputs, list) or not bound_inputs:
        errors.append(f"{prefix} bound_inputs must be a non-empty list")
    else:
        for index, binding in enumerate(bound_inputs):
            if not isinstance(binding, dict):
                errors.append(f"{prefix} bound_inputs[{index}] must be an object")
                continue
            if set(binding) != {"path", "sha256", "role"}:
                errors.append(f"{prefix} bound_inputs[{index}] schema changed")
            role = binding.get("role")
            if not isinstance(role, str) or not role:
                errors.append(f"{prefix} bound_inputs[{index}] role is missing")
            else:
                role_counts[role] = role_counts.get(role, 0) + 1
            bound_path = verify_bound_file(
                binding,
                base=spec_path.parent,
                errors=errors,
                label=f"{prefix} bound_inputs[{index}]",
            )
            if bound_path is not None:
                if bound_path in seen_paths:
                    errors.append(f"{prefix} duplicate bound input path")
                seen_paths.add(bound_path)
                if role == "source_identity_and_target_observations":
                    prescreen_path = bound_path
    expected_role_counts = {
        "source_identity_and_target_observations": 1,
        "deterministic_transformation_code": 1,
        "fresh_reproduction_record": 1,
        "durable_public_source_bytes": 2,
        "internal_diagnostic": 1,
        "unexecuted_experiment_and_message_draft": 1,
        "human_readable_current_status_boundary": 1,
    }
    if role_counts != expected_role_counts:
        errors.append(f"{prefix} exact bound input role counts changed")
    if prescreen_path is not None:
        validate_durable_reproduction(prescreen_path, now=now, errors=errors)

    experiment_results = experiment.get("result_claims")
    if not exact_object(
        experiment_results,
        REQUIRED_FALSE_EXPERIMENT_RESULTS,
        errors=errors,
        label=f"{prefix} bound result_claims",
    ):
        experiment_results = None
    if isinstance(experiment_results, dict) and any(
        value is not False for value in experiment_results.values()
    ):
        errors.append(f"{prefix} bound result claims must remain false")
    if isinstance(results, dict) and results != experiment_results:
        errors.append(f"{prefix} state result_claims do not match bound experiment")

    external_gate = [
        gate
        for gate in experiment.get("gate_results", [])
        if isinstance(gate, dict) and gate.get("gate") == "external_action"
    ]
    if len(external_gate) != 1 or external_gate[0].get("result") != "blocked":
        errors.append(f"{prefix} historical external_action gate must be uniquely blocked")
    review_gates = [
        gate
        for gate in experiment.get("gate_results", [])
        if isinstance(gate, dict) and gate.get("gate") == "one_message_verification_probe"
    ]
    if len(review_gates) != 1 or review_gates[0].get("result") != (
        "detached_receipt_required"
    ):
        errors.append(f"{prefix} candidate must defer review status to detached receipt")
    return experiment, spec_path


def ca_r2_candidate_paths() -> set[Path]:
    return {
        (RESEARCH_ROOT / relative_path).resolve()
        for relative_path in EXPECTED_CA_R2_CANDIDATE_PATHS
    }


def validate_ca_r2_candidate_bindings(
    bindings: object, *, receipt_parent: Path, errors: list[str]
) -> dict[Path, dict]:
    """Require a unique, canonical, closed candidate binding set."""

    prefix = "opportunity independent reviews: CA r2 candidate"
    expected_paths = ca_r2_candidate_paths()
    expected_raw_paths = {
        os.path.relpath(path, start=receipt_parent) for path in expected_paths
    }
    if not isinstance(bindings, list):
        errors.append(f"{prefix}: candidate_bindings must be a list")
        return {}

    observed_paths: list[Path] = []
    observed_raw_paths: list[str] = []
    binding_by_path: dict[Path, dict] = {}
    for index, binding in enumerate(bindings):
        label = f"{prefix}[{index}]"
        if not exact_object(binding, BINDING_KEYS, errors=errors, label=label):
            continue
        assert isinstance(binding, dict)
        raw_path = binding.get("path")
        if isinstance(raw_path, str):
            observed_raw_paths.append(raw_path)
        bound_path = verify_bound_file(
            binding,
            base=receipt_parent,
            allowed_root=RESEARCH_ROOT,
            errors=errors,
            label=label,
            closed=True,
        )
        if bound_path is not None:
            observed_paths.append(bound_path)
            binding_by_path[bound_path] = binding

    if len(observed_raw_paths) != len(set(observed_raw_paths)):
        errors.append(f"{prefix}: duplicate literal binding path")
    if len(observed_paths) != len(set(observed_paths)):
        errors.append(f"{prefix}: duplicate resolved binding path")
    if (
        len(bindings) != len(expected_paths)
        or set(observed_paths) != expected_paths
        or set(observed_raw_paths) != expected_raw_paths
    ):
        errors.append(f"{prefix}: does not bind the exact unique closed review candidate")
    return binding_by_path


def validate_ca_r2_receipt_contract(
    receipt: dict, *, receipt_path: Path, now: datetime, errors: list[str]
) -> datetime | None:
    prefix = "opportunity independent reviews: CA r2 receipt"
    exact_object(receipt, CA_R2_RECEIPT_KEYS, errors=errors, label=prefix)
    if receipt.get("schema_version") != EXPECTED_CA_R2_SCHEMA_VERSION:
        errors.append(f"{prefix}: schema_version changed")
    if receipt.get("review_id") != EXPECTED_CA_R2_REVIEW_ID:
        errors.append(f"{prefix}: review_id changed")
    if receipt.get("reviewer_agent_identity") != EXPECTED_CA_R2_REVIEWER_IDENTITY:
        errors.append(f"{prefix}: reviewer_agent_identity changed")
    if receipt.get("reviewer_role") != "independent_read_only_subagent":
        errors.append(f"{prefix}: reviewer_role changed")
    if receipt.get("reviewer_modified_candidate") is not False:
        errors.append(f"{prefix}: reviewer must not modify candidate")
    if receipt.get("verdict") != "PASS":
        errors.append(f"{prefix}: verdict must be PASS")

    severity_counts = receipt.get("severity_counts")
    if exact_object(
        severity_counts,
        {"critical", "major"},
        errors=errors,
        label=f"{prefix} severity_counts",
    ):
        assert isinstance(severity_counts, dict)
        if any(type(value) is not int for value in severity_counts.values()):
            errors.append(f"{prefix}: severity counts must be exact integers")
        if severity_counts != EXPECTED_CA_R2_SEVERITY_COUNTS:
            errors.append(f"{prefix}: Critical and Major counts must both be zero")

    exact_string_set(
        receipt.get("reviewed_properties"),
        EXPECTED_CA_R2_REVIEWED_PROPERTIES,
        errors=errors,
        label=f"{prefix} reviewed_properties",
    )
    if receipt.get("external_action_status") != "BLOCKED_NOT_AUTHORIZED":
        errors.append(f"{prefix}: external action must remain BLOCKED_NOT_AUTHORIZED")
    exact_string_set(
        receipt.get("missing_external_bindings"),
        EXPECTED_CA_R2_MISSING_EXTERNAL_BINDINGS,
        errors=errors,
        label=f"{prefix} missing_external_bindings",
    )
    if receipt.get("claim_boundary") != EXPECTED_CA_R2_CLAIM_BOUNDARY:
        errors.append(f"{prefix}: claim_boundary changed")

    recorded_at = validate_not_future(
        receipt.get("recorded_at"),
        now=now,
        errors=errors,
        label=f"{prefix} recorded_at",
    )
    binding_by_path = validate_ca_r2_candidate_bindings(
        receipt.get("candidate_bindings"),
        receipt_parent=receipt_path.parent,
        errors=errors,
    )

    for relative_path, expected in EXPECTED_CA_R2_HISTORICAL_REJECTIONS.items():
        historical_path = (RESEARCH_ROOT / relative_path).resolve()
        historical_binding = binding_by_path.get(historical_path)
        if not isinstance(historical_binding, dict) or historical_binding.get(
            "sha256"
        ) != expected["sha256"]:
            errors.append(f"{prefix}: historical FAIL binding changed for {relative_path}")
        historical_receipt = load_json(
            historical_path,
            errors=errors,
            label=f"{prefix} historical FAIL {relative_path}",
        )
        if historical_receipt is None:
            continue
        if historical_receipt.get("review_id") != expected["review_id"]:
            errors.append(f"{prefix}: historical FAIL review_id changed")
        if historical_receipt.get("verdict") != "FAIL":
            errors.append(f"{prefix}: historical predecessor must remain FAIL")
        predecessor_at = parse_timestamp(
            historical_receipt.get("recorded_at"),
            errors=errors,
            label=f"{prefix} historical FAIL recorded_at",
        )
        if (
            recorded_at is not None
            and predecessor_at is not None
            and recorded_at.astimezone(timezone.utc)
            <= predecessor_at.astimezone(timezone.utc)
        ):
            errors.append(f"{prefix}: recorded_at must be later than every historical FAIL")
    return recorded_at


def validate_review_receipts(
    stream: dict, *, now: datetime, errors: list[str]
) -> tuple[str, datetime | None]:
    prefix = "opportunity independent reviews:"
    reviews = stream.get("independent_reviews")
    required_keys = {"legacy_runtime_tombstone", "ca012650_internal_candidate"}
    if not exact_object(reviews, required_keys, errors=errors, label=prefix):
        return "pending_fresh_review", None
    assert isinstance(reviews, dict)

    loaded: dict[str, tuple[Path, dict]] = {}
    receipt_times: dict[str, datetime | None] = {}
    for key in sorted(required_keys):
        state_binding = reviews.get(key)
        if key == "ca012650_internal_candidate" and isinstance(
            state_binding, dict
        ) and set(state_binding) == {"status", "receipt"}:
            if state_binding != {"status": "pending_fresh_review", "receipt": None}:
                errors.append(f"{prefix} CA pending review object changed")
            continue
        exact_object(
            state_binding,
            REVIEW_STATE_KEYS,
            errors=errors,
            label=f"{prefix} {key} state binding",
        )
        if isinstance(state_binding, dict) and state_binding.get("path") != (
            EXPECTED_REVIEW_STATE_PATHS[key]
        ):
            errors.append(f"{prefix} {key} receipt path changed")
        receipt_path = verify_bound_file(
            state_binding,
            base=RESEARCH_ROOT,
            errors=errors,
            label=f"{prefix} {key}",
        )
        if not isinstance(state_binding, dict) or state_binding.get("verdict") != "PASS":
            errors.append(f"{prefix} {key} state verdict must be PASS")
        if receipt_path is None:
            continue
        receipt = load_json(receipt_path, errors=errors, label=f"{prefix} {key} receipt")
        if receipt is None:
            continue
        loaded[key] = (receipt_path, receipt)
        if receipt.get("verdict") != "PASS":
            errors.append(f"{prefix} {key} receipt verdict must be PASS")
        if receipt.get("reviewer_role") != "independent_read_only_subagent":
            errors.append(f"{prefix} {key} reviewer role changed")
        if receipt.get("reviewer_modified_candidate") is not False:
            errors.append(f"{prefix} {key} reviewer must not modify candidate")
        receipt_times[key] = validate_not_future(
            receipt.get("recorded_at"),
            now=now,
            errors=errors,
            label=f"{prefix} {key} recorded_at",
        )

    ca_pair = loaded.get("ca012650_internal_candidate")
    if ca_pair is not None:
        ca_path, ca_receipt = ca_pair
        receipt_times["ca012650_internal_candidate"] = (
            validate_ca_r2_receipt_contract(
                ca_receipt,
                receipt_path=ca_path,
                now=now,
                errors=errors,
            )
        )

    legacy_pair = loaded.get("legacy_runtime_tombstone")
    if legacy_pair is not None:
        legacy_path, legacy_receipt = legacy_pair
        raw_root = legacy_receipt.get("candidate_root")
        if not isinstance(raw_root, str):
            resolved_root = None
            errors.append(f"{prefix} legacy candidate root does not resolve")
        else:
            lexical_root = legacy_path.parent / raw_root
            if _has_symlink_component(lexical_root):
                resolved_root = None
                errors.append(f"{prefix} legacy candidate root contains a symlink")
            else:
                try:
                    resolved_root = lexical_root.resolve(strict=True)
                except (OSError, RuntimeError):
                    resolved_root = None
                    errors.append(f"{prefix} legacy candidate root does not resolve")
        if resolved_root != LEGACY_OPPORTUNITY_ROOT:
            errors.append(f"{prefix} legacy candidate root changed")
        legacy_bindings = legacy_receipt.get("candidate_bindings")
        expected_legacy_paths = {
            (LEGACY_OPPORTUNITY_ROOT / "src/opportunity_os.py").resolve(),
            (LEGACY_OPPORTUNITY_ROOT / "tests/test_opportunity_os.py").resolve(),
            (
                LEGACY_OPPORTUNITY_ROOT
                / "pilot/restaurant-web-repair/quarantine/REVOCATION_MANIFEST.json"
            ).resolve(),
            (LEGACY_OPPORTUNITY_ROOT / "README.md").resolve(),
            (LEGACY_OPPORTUNITY_ROOT / "LEGACY_STATUS.md").resolve(),
            (LEGACY_OPPORTUNITY_ROOT / "LEGACY_CODE_GAP_AUDIT.md").resolve(),
        }
        observed_legacy_paths: set[Path] = set()
        if not isinstance(legacy_bindings, list):
            errors.append(f"{prefix} legacy receipt candidate_bindings must be a list")
        else:
            for index, binding in enumerate(legacy_bindings):
                bound_path = verify_bound_file(
                    binding,
                    base=LEGACY_OPPORTUNITY_ROOT,
                    errors=errors,
                    label=f"{prefix} legacy candidate[{index}]",
                    allowed_root=LEGACY_OPPORTUNITY_ROOT,
                )
                if bound_path is not None:
                    observed_legacy_paths.add(bound_path)
        if observed_legacy_paths != expected_legacy_paths:
            errors.append(f"{prefix} legacy receipt does not bind exact tombstone candidate")
    ca_state = reviews.get("ca012650_internal_candidate")
    if isinstance(ca_state, dict) and set(ca_state) == {"status", "receipt"}:
        return "pending_fresh_review", None
    return "passed_current_candidate", receipt_times.get(
        "ca012650_internal_candidate"
    )


def validate_ca_review_prose(ca_review_status: str, errors: list[str]) -> None:
    """Candidate documents must never self-certify a detached review verdict."""

    documents = {
        "11": RESEARCH_ROOT / "11-内部诊断页-CA012650.md",
        "12": RESEARCH_ROOT / "12-首个反证实验与对外动作候选.md",
        "README": RESEARCH_ROOT / "README.md",
    }
    text_by_name: dict[str, str] = {}
    for name, path in documents.items():
        resolved = confined_file(
            path.name,
            base=RESEARCH_ROOT,
            allowed_root=RESEARCH_ROOT,
            errors=errors,
            label=f"CA review prose {name}",
        )
        if resolved is None:
            continue
        try:
            text_by_name[name] = resolved.read_text(encoding="utf-8")
        except (OSError, UnicodeError):
            errors.append(f"CA review prose {name}: unreadable UTF-8")

    del ca_review_status  # verdict is intentionally absent from candidate prose
    neutral_markers = {
        "11": "REVIEW-STATUS-DETERMINED-BY-EXACT-DETACHED-RECEIPT",
        "12": "REVIEW-STATUS-DETERMINED-BY-EXACT-DETACHED-RECEIPT",
        "README": "当前复核状态只由活动状态绑定的精确字节 detached receipt 派生",
    }
    forbidden = {
        "11": ("INDEPENDENT-INTERNAL-REVIEW-PASS", "已取得独立 PASS"),
        "12": (
            "INDEPENDENT-INTERNAL-REVIEW-PASS",
            "内部候选已取得独立 PASS",
            "内部 PASS 只说明",
        ),
        "README": ("经内部独立复核", "内部研究包已经过独立复核"),
    }
    for name, markers in forbidden.items():
        text = text_by_name.get(name, "")
        if neutral_markers[name] not in text:
            errors.append(
                f"CA review prose {name}: detached-review neutral marker is missing"
            )
        for marker in markers:
            if marker in text:
                errors.append(
                    f"CA review prose {name}: candidate prose must not self-certify PASS"
                )


@lru_cache(maxsize=4)
def _inspect_investment_bundle(
    path_text: str, size: int, mtime_ns: int, expected_sha256: str
) -> tuple[str, ...]:
    """Derive the archive commit/tree from the bound bundle in a fresh temp repo."""

    del size, mtime_ns, expected_sha256  # cache identity; byte hash is checked separately
    bundle_path = Path(path_text)
    findings: list[str] = []
    with tempfile.TemporaryDirectory(prefix="active-state-bundle-") as temp_dir:
        repo = Path(temp_dir) / "repo.git"
        commands = [
            ["git", "init", "--bare", str(repo)],
            [
                "git",
                "-C",
                str(repo),
                "fetch",
                str(bundle_path),
                "refs/heads/durable-investment-fed7",
            ],
            ["git", "-C", str(repo), "fsck", "--full"],
        ]
        for command in commands:
            completed = subprocess.run(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=False,
            )
            if completed.returncode != 0:
                findings.append(
                    f"command failed ({' '.join(command[:3])}): exit {completed.returncode}"
                )
                return tuple(findings)
        for expression, expected, label in (
            ("FETCH_HEAD", EXPECTED_INVESTMENT_ARCHIVE_COMMIT, "archive commit"),
            ("FETCH_HEAD^{tree}", EXPECTED_INVESTMENT_PROJECT_SUBTREE, "archive tree"),
        ):
            completed = subprocess.run(
                ["git", "-C", str(repo), "rev-parse", expression],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=False,
            )
            observed = completed.stdout.strip()
            if completed.returncode != 0 or observed != expected:
                findings.append(f"{label} mismatch")
    return tuple(findings)


def validate_investment_durable_candidate(
    audit_path: Path, audit: dict, *, now: datetime, errors: list[str]
) -> None:
    prefix = "investment durable candidate:"
    durable = audit.get("durable_candidate")
    durable_keys = {
        "record_path",
        "record_sha256",
        "bundle_path",
        "bundle_sha256",
        "bundle_bytes",
        "reconstructed_project_tree",
        "fresh_reconstruction_check",
    }
    if not exact_object(durable, durable_keys, errors=errors, label=prefix):
        return
    assert isinstance(durable, dict)
    expected_durable = {
        "record_path": EXPECTED_INVESTMENT_RECORD["path"],
        "record_sha256": EXPECTED_INVESTMENT_RECORD["sha256"],
        "bundle_path": EXPECTED_INVESTMENT_BUNDLE["path"],
        "bundle_sha256": EXPECTED_INVESTMENT_BUNDLE["sha256"],
        "bundle_bytes": EXPECTED_INVESTMENT_BUNDLE["bytes"],
        "reconstructed_project_tree": EXPECTED_INVESTMENT_PROJECT_SUBTREE,
        "fresh_reconstruction_check": "pass",
    }
    if durable != expected_durable:
        errors.append(f"{prefix} audit binding changed")

    record_binding = {
        "path": durable.get("record_path"),
        "sha256": durable.get("record_sha256"),
    }
    record_path = verify_bound_file(
        record_binding,
        base=audit_path.parent,
        errors=errors,
        label=f"{prefix} record",
    )
    bundle_binding = {
        "path": durable.get("bundle_path"),
        "sha256": durable.get("bundle_sha256"),
    }
    bundle_path = verify_bound_file(
        bundle_binding,
        base=audit_path.parent,
        errors=errors,
        label=f"{prefix} bundle",
    )
    if bundle_path is not None:
        bundle_stat = bundle_path.stat()
        if bundle_stat.st_size != EXPECTED_INVESTMENT_BUNDLE["bytes"]:
            errors.append(f"{prefix} bundle byte length mismatch")
        for finding in _inspect_investment_bundle(
            str(bundle_path),
            bundle_stat.st_size,
            bundle_stat.st_mtime_ns,
            EXPECTED_INVESTMENT_BUNDLE["sha256"],
        ):
            errors.append(f"{prefix} {finding}")
    if record_path is None:
        return
    record = load_json(record_path, errors=errors, label=f"{prefix} record")
    if record is None:
        return
    if record.get("schema_version") != "investment-discipline-durable-candidate/1":
        errors.append(f"{prefix} record schema changed")
    validate_not_future(
        record.get("recorded_at"), now=now, errors=errors, label=f"{prefix} recorded_at"
    )
    source = record.get("source_candidate")
    if not isinstance(source, dict):
        errors.append(f"{prefix} source candidate identity missing")
    else:
        expected_source = {
            "repository_commit": EXPECTED_INVESTMENT_IDENTITY["commit"],
            "repository_tree": EXPECTED_INVESTMENT_IDENTITY["tree"],
            "repository_parent": EXPECTED_INVESTMENT_IDENTITY["parent"],
            "project_path": "MyBrain/projects/investment-discipline-system",
            "project_subtree": EXPECTED_INVESTMENT_PROJECT_SUBTREE,
            "source_clone_was_clean": True,
        }
        if source != expected_source:
            errors.append(f"{prefix} source candidate identity changed")
    bundle_record = record.get("durable_bundle")
    if not isinstance(bundle_record, dict):
        errors.append(f"{prefix} bundle record missing")
    else:
        expected_fields = {
            "path": EXPECTED_INVESTMENT_BUNDLE["path"],
            "bytes": EXPECTED_INVESTMENT_BUNDLE["bytes"],
            "sha256": EXPECTED_INVESTMENT_BUNDLE["sha256"],
            "ref": "refs/heads/durable-investment-fed7",
            "archive_commit": EXPECTED_INVESTMENT_ARCHIVE_COMMIT,
            "archive_tree": EXPECTED_INVESTMENT_PROJECT_SUBTREE,
        }
        for key, expected in expected_fields.items():
            if bundle_record.get(key) != expected:
                errors.append(f"{prefix} record {key} changed")
    reconstruction = record.get("fresh_reconstruction_check")
    if not isinstance(reconstruction, dict):
        errors.append(f"{prefix} fresh reconstruction check missing")
    else:
        expected_checks = {
            "git_bundle_verify_exit": 0,
            "git_clone_exit": 0,
            "git_fsck_full_exit": 0,
            "git_status_porcelain": "",
            "reconstructed_commit": EXPECTED_INVESTMENT_ARCHIVE_COMMIT,
            "reconstructed_tree": EXPECTED_INVESTMENT_PROJECT_SUBTREE,
        }
        for key, expected in expected_checks.items():
            if reconstruction.get(key) != expected:
                errors.append(f"{prefix} reconstruction {key} changed")


def validate_investment_current_run(
    audit_path: Path,
    audit: dict,
    full_suite: dict,
    *,
    now: datetime,
    errors: list[str],
) -> None:
    prefix = "investment current full-suite run:"
    validate_not_future(
        audit.get("fresh_full_suite_persisted_at"),
        now=now,
        errors=errors,
        label=f"{prefix} audit persisted_at",
    )
    expected_audit_fields = {
        "run_record_path": EXPECTED_INVESTMENT_FULL_RUN["record_path"],
        "run_record_sha256": EXPECTED_INVESTMENT_FULL_RUN["record_sha256"],
        "complete_output_path": EXPECTED_INVESTMENT_FULL_RUN["log_path"],
        "complete_output_sha256": EXPECTED_INVESTMENT_FULL_RUN["log_sha256"],
        "complete_output_bytes": EXPECTED_INVESTMENT_FULL_RUN["log_bytes"],
        "complete_output_lines": EXPECTED_INVESTMENT_FULL_RUN["log_lines"],
        "process_exit_code": EXPECTED_INVESTMENT_FULL_RUN["exit_code"],
    }
    for key, expected in expected_audit_fields.items():
        if full_suite.get(key) != expected:
            errors.append(f"{prefix} audit {key} changed")

    record_binding = {
        "path": full_suite.get("run_record_path"),
        "sha256": full_suite.get("run_record_sha256"),
    }
    record_path = verify_bound_file(
        record_binding,
        base=audit_path.parent,
        errors=errors,
        label=f"{prefix} record",
    )
    log_binding = {
        "path": full_suite.get("complete_output_path"),
        "sha256": full_suite.get("complete_output_sha256"),
    }
    log_path = verify_bound_file(
        log_binding,
        base=audit_path.parent,
        errors=errors,
        label=f"{prefix} complete output",
    )
    if log_path is not None:
        if log_path.stat().st_size != EXPECTED_INVESTMENT_FULL_RUN["log_bytes"]:
            errors.append(f"{prefix} complete output byte length changed")
        try:
            raw_log = log_path.read_text(encoding="utf-8")
        except (OSError, UnicodeError):
            raw_log = ""
            errors.append(f"{prefix} complete output is not readable UTF-8")
        if len(raw_log.splitlines()) != EXPECTED_INVESTMENT_FULL_RUN["log_lines"]:
            errors.append(f"{prefix} complete output line count changed")
        for summary_line in EXPECTED_INVESTMENT_FULL_RUN["summary"]:
            if summary_line not in raw_log:
                errors.append(f"{prefix} complete output omits verbatim summary")

    if record_path is None:
        return
    record = load_json(record_path, errors=errors, label=f"{prefix} record")
    if record is None:
        return
    if record.get("schema_version") != "investment-fed7-full-suite-run/1":
        errors.append(f"{prefix} record schema changed")
    validate_not_future(
        record.get("recorded_at"), now=now, errors=errors, label=f"{prefix} recorded_at"
    )
    identity = record.get("candidate_identity")
    if not isinstance(identity, dict) or any(
        identity.get(key) != value
        for key, value in EXPECTED_INVESTMENT_IDENTITY.items()
    ):
        errors.append(f"{prefix} record candidate identity changed")
    elif identity.get("project_subtree") != EXPECTED_INVESTMENT_PROJECT_SUBTREE:
        errors.append(f"{prefix} record project subtree changed")
    if record.get("command") != (
        "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s governance_tests -v"
    ):
        errors.append(f"{prefix} command changed")
    if record.get("process_exit_code") != EXPECTED_INVESTMENT_FULL_RUN["exit_code"]:
        errors.append(f"{prefix} exit code changed")
    if record.get("verbatim_summary") != EXPECTED_INVESTMENT_FULL_RUN["summary"]:
        errors.append(f"{prefix} verbatim summary changed")
    if record.get("parsed_headings") != {"fail": 40, "error": 2}:
        errors.append(f"{prefix} parsed failure headings changed")
    if record.get("complete_output") != {
        "path": EXPECTED_INVESTMENT_FULL_RUN["log_path"],
        "sha256": EXPECTED_INVESTMENT_FULL_RUN["log_sha256"],
        "bytes": EXPECTED_INVESTMENT_FULL_RUN["log_bytes"],
        "lines": EXPECTED_INVESTMENT_FULL_RUN["log_lines"],
    }:
        errors.append(f"{prefix} complete output binding changed")
    if record.get("acceptance") != "FAIL_BLOCKED_INTERNAL":
        errors.append(f"{prefix} acceptance must remain FAIL_BLOCKED_INTERNAL")


def validate_investment_root_cause_review(
    audit_path: Path, audit: dict, *, now: datetime, errors: list[str]
) -> None:
    prefix = "investment root-cause review:"
    binding = audit.get("independent_root_cause_review")
    expected_keys = {
        "path",
        "sha256",
        "reviewer_id",
        "verdict",
        "reviewer_modified_candidate",
    }
    if not exact_object(binding, expected_keys, errors=errors, label=prefix):
        return
    assert isinstance(binding, dict)
    expected_binding = {
        **EXPECTED_INVESTMENT_ROOT_CAUSE_REVIEW,
        "reviewer_id": "/root/investment_blocker_analysis",
        "verdict": "NO_GO_BLOCKED_INTERNAL",
        "reviewer_modified_candidate": False,
    }
    if binding != expected_binding:
        errors.append(f"{prefix} audit binding changed")
    review_path = verify_bound_file(
        binding,
        base=audit_path.parent,
        errors=errors,
        label=f"{prefix} evidence",
    )
    if review_path is None:
        return
    review = load_json(review_path, errors=errors, label=f"{prefix} evidence")
    if review is None:
        return
    if review.get("schema_version") != "investment-fed7-independent-root-cause-review/1":
        errors.append(f"{prefix} schema changed")
    validate_not_future(
        review.get("recorded_at"), now=now, errors=errors, label=f"{prefix} recorded_at"
    )
    if review.get("reviewer_role") != "independent_read_only_subagent":
        errors.append(f"{prefix} reviewer role changed")
    if review.get("reviewer_modified_candidate") is not False:
        errors.append(f"{prefix} reviewer must remain read-only")
    if review.get("verdict") != "NO_GO_BLOCKED_INTERNAL":
        errors.append(f"{prefix} verdict changed")
    identity = review.get("candidate_identity")
    if not isinstance(identity, dict) or any(
        identity.get(key) != value for key, value in EXPECTED_INVESTMENT_IDENTITY.items()
    ):
        errors.append(f"{prefix} candidate identity changed")
    elif identity.get("project_subtree") != EXPECTED_INVESTMENT_PROJECT_SUBTREE:
        errors.append(f"{prefix} project subtree changed")
    if review.get("live_or_shadow_investment_authority") is not False:
        errors.append(f"{prefix} live/shadow authority must remain false")


def validate_investment_audit(
    stream: dict, *, now: datetime, errors: list[str]
) -> None:
    prefix = "investment audit:"
    binding = stream.get("candidate_audit")
    exact_object(
        binding,
        CANDIDATE_AUDIT_KEYS,
        errors=errors,
        label=f"{prefix} state binding",
    )
    if isinstance(binding, dict) and binding.get("path") != (
        "evidence/investment-candidate-audit-2026-07-27.json"
    ):
        errors.append(f"{prefix} audit evidence path changed")
    audit_path = verify_bound_file(
        binding, base=RESEARCH_ROOT, errors=errors, label=f"{prefix} evidence"
    )
    if audit_path is None:
        return
    audit = load_json(audit_path, errors=errors, label=f"{prefix} evidence")
    if audit is None:
        return
    validate_investment_durable_candidate(audit_path, audit, now=now, errors=errors)
    validate_investment_root_cause_review(audit_path, audit, now=now, errors=errors)
    if not isinstance(binding, dict) or binding.get("overall_acceptance") != "blocked_internal":
        errors.append(f"{prefix} state acceptance must remain blocked_internal")
    identity = audit.get("candidate_identity")
    if not isinstance(identity, dict) or any(
        identity.get(key) != value for key, value in EXPECTED_INVESTMENT_IDENTITY.items()
    ):
        errors.append(f"{prefix} exact commit/tree/parent identity mismatch")
    if audit.get("overall_acceptance") != "blocked_internal":
        errors.append(f"{prefix} overall acceptance must remain blocked_internal")
    claims = audit.get("result_claims")
    if not isinstance(claims, dict) or not claims or any(
        value is not False for value in claims.values()
    ):
        errors.append(f"{prefix} all result claims must be explicit false")

    checks = {
        item.get("check"): item
        for item in audit.get("observed_checks", [])
        if isinstance(item, dict) and isinstance(item.get("check"), str)
    }
    full_suite = checks.get("full_governance_suite", {})
    if full_suite.get("verbatim_summary") != EXPECTED_INVESTMENT_FULL_RUN[
        "summary"
    ] or full_suite.get("acceptance") != "fail":
        errors.append(f"{prefix} full governance failure evidence changed")
    if isinstance(full_suite, dict):
        validate_investment_current_run(
            audit_path, audit, full_suite, now=now, errors=errors
        )
    no_live = checks.get("targeted_no_live_suite", {})
    if no_live.get("verbatim_summary") != [
        "Ran 18 tests in 7.518s",
        "OK",
    ] or no_live.get("acceptance") != "pass_with_narrow_claim_boundary":
        errors.append(f"{prefix} targeted no-live evidence changed")


def _experiment_message_binding(
    experiment: dict, spec_path: Path, *, errors: list[str]
) -> tuple[Path | None, str | None]:
    matches = [
        binding
        for binding in experiment.get("bound_inputs", [])
        if isinstance(binding, dict)
        and binding.get("role") == "unexecuted_experiment_and_message_draft"
    ]
    if len(matches) != 1:
        errors.append("CA012650 approval: experiment message binding is not unique")
        return None, None
    binding = matches[0]
    path = verify_bound_file(
        binding,
        base=spec_path.parent,
        errors=errors,
        label="CA012650 approval: experiment message binding",
    )
    digest = binding.get("sha256") if isinstance(binding.get("sha256"), str) else None
    return path, digest


def validate_refresh_record(
    binding: object,
    *,
    record_type: str,
    completed_at: datetime | None,
    stage: str,
    validation_now: datetime,
    snapshot_at: datetime,
    errors: list[str],
    base: Path = RESEARCH_ROOT,
    allowed_root: Path = RESEARCH_ROOT,
) -> datetime | None:
    prefix = f"CA012650 approval {record_type} refresh record:"
    record_path = verify_bound_file(
        binding,
        base=base,
        errors=errors,
        label=prefix,
        closed=True,
        allowed_root=allowed_root,
    )
    if record_path is None:
        return None
    record = load_json(record_path, errors=errors, label=prefix)
    if record is None:
        return None
    if record_type == "CEC status/address":
        keys = {
            "schema_version",
            "captured_at",
            "source_url",
            "source_content_binding",
            "exact_target",
            "observed_reporting_year",
            "observed_compliance_status",
            "claim_boundary",
        }
        expected_schema = "ca012650-cec-status-refresh/1"
    else:
        keys = {
            "schema_version",
            "captured_at",
            "source_url",
            "source_content_binding",
            "organization_name",
            "organization_liveness",
            "http_status",
            "final_url",
            "exact_channel",
            "routing_contact_only",
            "claim_boundary",
        }
        expected_schema = "ca012650-organization-channel-refresh/1"
    if not exact_object(record, keys, errors=errors, label=prefix):
        return None
    if record.get("schema_version") != expected_schema:
        errors.append(f"{prefix} schema changed")
    captured_at = validate_not_future(
        record.get("captured_at"),
        now=snapshot_at,
        errors=errors,
        label=f"{prefix} captured_at",
    )
    if completed_at is not None and captured_at is not None and captured_at > completed_at:
        errors.append(f"{prefix} capture is later than refresh completion")
    if stage in {"request_ready", "authorized_once"} and captured_at is not None:
        if validation_now - captured_at.astimezone(timezone.utc) > timedelta(
            hours=PRE_SEND_REFRESH_MAX_AGE_HOURS
        ):
            errors.append(f"{prefix} is older than the pre-send freshness window")
    source_content_path = verify_bound_file(
        record.get("source_content_binding"),
        base=record_path.parent,
        errors=errors,
        label=f"{prefix} source content",
        closed=True,
        allowed_root=allowed_root,
    )
    if record.get("claim_boundary") != EXPECTED_CA_REFRESH_CLAIM_BOUNDARIES.get(
        record_type
    ):
        errors.append(f"{prefix} claim boundary differs from the exact closed value")

    if record_type == "CEC status/address":
        if record.get("source_url") != (
            "https://touchstone-content.s3.us-east-1.amazonaws.com/governments/"
            "CoveredBuildingsExport.csv"
        ):
            errors.append(f"{prefix} source URL changed")
        expected_target = {
            "public_building_id": "Building #CA012650",
            "public_record_location": "Best Western Plus Marina Gateway Hotel",
            "public_address": "800 Bay Marina Drive, National City",
        }
        target = record.get("exact_target")
        if not exact_object(
            target, set(expected_target), errors=errors, label=f"{prefix} exact_target"
        ) or target != expected_target:
            errors.append(f"{prefix} target/status binding changed")
        if record.get("observed_reporting_year") != "2026":
            errors.append(f"{prefix} reporting year changed")
        if record.get("observed_compliance_status") != "not submitted":
            errors.append(f"{prefix} current status no longer permits request_ready")
        if source_content_path is not None:
            raw_root = (allowed_root / "evidence/raw").resolve()
            if not _inside(source_content_path, raw_root) or source_content_path.suffix != (
                ".csv"
            ):
                errors.append(f"{prefix} source content must be a bound raw CSV snapshot")
            else:
                try:
                    with source_content_path.open(
                        "r", encoding="utf-8-sig", newline=""
                    ) as handle:
                        reader = csv.DictReader(handle)
                        expected_fields = {
                            "Building ID",
                            "Street",
                            "City",
                            "Gross Floor Area",
                            "Reporting Year",
                            "Compliance Status",
                        }
                        if set(reader.fieldnames or []) != expected_fields:
                            errors.append(f"{prefix} raw CSV columns changed")
                            rows: list[dict[str, str]] = []
                        else:
                            rows = [
                                row
                                for row in reader
                                if row.get("Building ID") == "Building #CA012650"
                            ]
                except (OSError, UnicodeError, csv.Error):
                    rows = []
                    errors.append(f"{prefix} raw CSV cannot be parsed")
                if len(rows) != 1:
                    errors.append(f"{prefix} raw CSV must contain exactly one target row")
                else:
                    expected_row = {
                        "Building ID": "Building #CA012650",
                        "Street": "800 bay marina drive",
                        "City": "national city",
                        "Reporting Year": "2026",
                        "Compliance Status": "not submitted",
                    }
                    if any(rows[0].get(key) != value for key, value in expected_row.items()):
                        errors.append(
                            f"{prefix} self-reported status/address differs from bound raw CSV"
                        )
    else:
        if record.get("source_url") != EXPECTED_CA_CHANNEL_SOURCE:
            errors.append(f"{prefix} source URL changed")
        if record.get("organization_name") != EXPECTED_CA_TARGET[
            "public_record_location"
        ]:
            errors.append(f"{prefix} organization identity changed")
        if record.get("organization_liveness") != "public_contact_page_accessible":
            errors.append(f"{prefix} organization liveness is not freshly established")
        if record.get("http_status") != 200:
            errors.append(f"{prefix} HTTP status does not establish page liveness")
        if record.get("final_url") != EXPECTED_CA_CHANNEL_SOURCE:
            errors.append(f"{prefix} final URL changed")
        if record.get("exact_channel") != EXPECTED_CA_CHANNEL:
            errors.append(f"{prefix} exact channel changed")
        if record.get("routing_contact_only") is not True:
            errors.append(f"{prefix} routing-only boundary changed")
        if source_content_path is not None:
            raw_root = (allowed_root / "evidence/raw").resolve()
            if not _inside(source_content_path, raw_root) or source_content_path.suffix.lower() not in {
                ".html",
                ".htm",
            }:
                errors.append(f"{prefix} source content must be a bound raw HTML snapshot")
            else:
                try:
                    raw_text = source_content_path.read_text(encoding="utf-8")
                except (OSError, UnicodeError):
                    raw_text = ""
                    errors.append(f"{prefix} raw HTML cannot be decoded as UTF-8")
                normalized = re.sub(
                    r"\s+",
                    " ",
                    re.sub(r"<[^>]+>", " ", html.unescape(raw_text)).lower(),
                )
                if EXPECTED_CA_CHANNEL.lower() not in raw_text.lower():
                    errors.append(f"{prefix} bound HTML does not contain exact channel")
                if "best western plus marina gateway" not in normalized:
                    errors.append(f"{prefix} bound HTML does not contain organization identity")
    return captured_at


def validate_source_refresh(
    refresh: object,
    *,
    stage: str,
    validation_now: datetime,
    snapshot_at: datetime,
    errors: list[str],
) -> list[datetime]:
    prefix = "CA012650 approval source refresh:"
    if not exact_object(refresh, SOURCE_REFRESH_KEYS, errors=errors, label=prefix):
        return []
    assert isinstance(refresh, dict)
    is_ready = APPROVAL_STAGES.index(stage) >= APPROVAL_STAGES.index("request_ready")
    if not is_ready:
        expected = {
            "status": "not_completed",
            "completed_at": None,
            "cec_status_record": None,
            "organization_channel_record": None,
        }
        if refresh != expected:
            errors.append(f"{prefix} blocked stage must keep refresh wholly incomplete")
        return []
    if refresh.get("status") != "completed":
        errors.append(f"{prefix} request-ready or later stage requires completed refresh")
    completed_at = validate_not_future(
        refresh.get("completed_at"),
        now=snapshot_at,
        errors=errors,
        label=f"{prefix} completed_at",
    )
    if stage in {"request_ready", "authorized_once"} and completed_at is not None:
        if validation_now - completed_at.astimezone(timezone.utc) > timedelta(
            hours=PRE_SEND_REFRESH_MAX_AGE_HOURS
        ):
            errors.append(f"{prefix} completion is older than the pre-send freshness window")
    cec_captured_at = validate_refresh_record(
        refresh.get("cec_status_record"),
        record_type="CEC status/address",
        completed_at=completed_at,
        stage=stage,
        validation_now=validation_now,
        snapshot_at=snapshot_at,
        errors=errors,
    )
    organization_captured_at = validate_refresh_record(
        refresh.get("organization_channel_record"),
        record_type="organization/channel",
        completed_at=completed_at,
        stage=stage,
        validation_now=validation_now,
        snapshot_at=snapshot_at,
        errors=errors,
    )
    observed_times = [
        timestamp
        for timestamp in (completed_at, cec_captured_at, organization_captured_at)
        if timestamp is not None
    ]
    return observed_times


def validate_execution_refresh_window(
    *,
    executed_at: datetime | None,
    refresh_timestamps: list[datetime],
    errors: list[str],
) -> None:
    prefix = "CA012650 approval execution freshness:"
    if executed_at is None:
        errors.append(f"{prefix} executed stage lacks an exact executed_at")
        return
    if not refresh_timestamps:
        errors.append(f"{prefix} executed stage lacks complete refresh timestamps")
        return
    executed_utc = executed_at.astimezone(timezone.utc)
    for refresh_at in refresh_timestamps:
        refresh_utc = refresh_at.astimezone(timezone.utc)
        if executed_utc < refresh_utc:
            errors.append(f"{prefix} execution predates completed source refresh")
        if executed_utc - refresh_utc > timedelta(
            hours=PRE_SEND_REFRESH_MAX_AGE_HOURS
        ):
            errors.append(
                f"{prefix} execution occurred after at least one source freshness window"
            )


def validate_stage_receipt(
    binding: object,
    *,
    receipt_field: str,
    item: dict,
    now: datetime,
    errors: list[str],
) -> dict | None:
    prefix = f"CA012650 approval {receipt_field}:"
    receipt_path = verify_bound_file(
        binding,
        base=RESEARCH_ROOT,
        errors=errors,
        label=prefix,
        closed=True,
    )
    if receipt_path is None:
        return None
    receipt = load_json(receipt_path, errors=errors, label=prefix)
    if receipt is None:
        return None
    if not exact_object(receipt, RECEIPT_ROOT_KEYS, errors=errors, label=prefix):
        return None
    expected_from, expected_to = RECEIPT_STAGE_PAIRS[receipt_field]
    expected_type = receipt_field.removesuffix("_receipt")
    expected_values = {
        "schema_version": "1.0",
        "receipt_type": expected_type,
        "approval_id": EXPECTED_CA_APPROVAL_ID,
        "experiment_id": EXPECTED_CA_EXPERIMENT_ID,
        "from_stage": expected_from,
        "to_stage": expected_to,
        "exact_target": EXPECTED_CA_TARGET,
        "exact_channel": EXPECTED_CA_CHANNEL,
        "channel_source": EXPECTED_CA_CHANNEL_SOURCE,
    }
    for key, expected in expected_values.items():
        if receipt.get(key) != expected:
            errors.append(f"{prefix} {key} does not bind the exact action")
    validate_not_future(
        receipt.get("recorded_at"), now=now, errors=errors, label=f"{prefix} recorded_at"
    )
    receipt_message = receipt.get("message_binding")
    if not exact_object(
        receipt_message, BINDING_KEYS, errors=errors, label=f"{prefix} message_binding"
    ):
        receipt_message = None
    if isinstance(receipt_message, dict) and receipt_message != item.get("message_binding"):
        errors.append(f"{prefix} message binding differs from approval")

    payload = receipt.get("stage_payload")
    if receipt_field == "readiness_receipt":
        keys = {
            "sender_account",
            "observation_cutoff_at",
            "cec_status_record",
            "organization_channel_record",
        }
        if exact_object(payload, keys, errors=errors, label=f"{prefix} stage_payload"):
            assert isinstance(payload, dict)
            if payload.get("sender_account") != item.get("sender_account"):
                errors.append(f"{prefix} sender account differs from approval")
            if payload.get("observation_cutoff_at") != item.get("observation_cutoff_at"):
                errors.append(f"{prefix} observation cutoff differs from approval")
            refresh = item.get("pre_send_source_refresh", {})
            for key in ("cec_status_record", "organization_channel_record"):
                if payload.get(key) != refresh.get(key):
                    errors.append(f"{prefix} {key} differs from approval")
    elif receipt_field == "authorization_receipt":
        keys = {
            "user_authorized",
            "one_message_only",
            "authorized_at",
            "sender_account",
            "authorization_scope",
        }
        if exact_object(payload, keys, errors=errors, label=f"{prefix} stage_payload"):
            assert isinstance(payload, dict)
            if payload.get("user_authorized") is not True or payload.get(
                "one_message_only"
            ) is not True:
                errors.append(f"{prefix} exact one-message authorization is missing")
            if payload.get("authorization_scope") != "exact_one_message_only_no_follow_up":
                errors.append(f"{prefix} authorization scope changed")
            if payload.get("sender_account") != item.get("sender_account"):
                errors.append(f"{prefix} sender account differs from approval")
            validate_not_future(
                payload.get("authorized_at"),
                now=now,
                errors=errors,
                label=f"{prefix} authorized_at",
            )
    elif receipt_field == "execution_receipt":
        keys = {
            "executed_at",
            "message_count",
            "transport_status",
            "authorization_receipt_sha256",
        }
        if exact_object(payload, keys, errors=errors, label=f"{prefix} stage_payload"):
            assert isinstance(payload, dict)
            if payload.get("message_count") != 1:
                errors.append(f"{prefix} exactly one message must be recorded")
            if payload.get("transport_status") not in {
                "transport_accepted",
                "transport_rejected",
                "unknown_after_submission",
            }:
                errors.append(f"{prefix} invalid transport status")
            auth_binding = item.get("lifecycle", {}).get("authorization_receipt")
            expected_auth_hash = (
                auth_binding.get("sha256") if isinstance(auth_binding, dict) else None
            )
            if payload.get("authorization_receipt_sha256") != expected_auth_hash:
                errors.append(f"{prefix} authorization receipt hash is not chained")
            validate_not_future(
                payload.get("executed_at"),
                now=now,
                errors=errors,
                label=f"{prefix} executed_at",
            )
    elif receipt_field == "observation_receipt":
        keys = {"started_at", "observation_cutoff_at", "follow_up_allowed"}
        if exact_object(payload, keys, errors=errors, label=f"{prefix} stage_payload"):
            assert isinstance(payload, dict)
            if payload.get("observation_cutoff_at") != item.get("observation_cutoff_at"):
                errors.append(f"{prefix} observation cutoff differs from approval")
            if payload.get("follow_up_allowed") is not False:
                errors.append(f"{prefix} follow-up must remain forbidden")
            validate_not_future(
                payload.get("started_at"),
                now=now,
                errors=errors,
                label=f"{prefix} started_at",
            )
    elif receipt_field == "closure_receipt":
        keys = {"closed_at", "outcome_class", "follow_up_sent"}
        if exact_object(payload, keys, errors=errors, label=f"{prefix} stage_payload"):
            assert isinstance(payload, dict)
            if payload.get("outcome_class") not in {
                "problem_signal_only",
                "inbound_interest_only",
                "counterevidence_stop",
                "target_routing_disconfirmed",
                "invalid_no_target_evidence",
                "inconclusive_no_follow_up",
            }:
                errors.append(f"{prefix} invalid closure outcome class")
            if payload.get("follow_up_sent") is not False:
                errors.append(f"{prefix} follow-up must remain unsent")
            validate_not_future(
                payload.get("closed_at"),
                now=now,
                errors=errors,
                label=f"{prefix} closed_at",
            )
    return receipt


def _receipt_time(receipt: dict, key: str) -> datetime | None:
    value = receipt.get("stage_payload", {}).get(key)
    if not isinstance(value, str):
        return None
    try:
        parsed = datetime.fromisoformat(value)
    except ValueError:
        return None
    return parsed if parsed.tzinfo is not None else None


def validate_lifecycle(
    item: dict,
    *,
    now: datetime,
    current_review_recorded_at: datetime | None,
    errors: list[str],
) -> tuple[str | None, dict[str, datetime | None]]:
    lifecycle = item.get("lifecycle")
    prefix = "CA012650 approval lifecycle:"
    if not exact_object(lifecycle, LIFECYCLE_KEYS, errors=errors, label=prefix):
        return None, {}
    assert isinstance(lifecycle, dict)
    stage = lifecycle.get("stage")
    if stage not in APPROVAL_STAGES:
        errors.append(f"{prefix} invalid stage")
        return None, {}
    if item.get("status") != stage:
        errors.append(f"{prefix} approval status and lifecycle stage differ")
    expected_previous = PREVIOUS_APPROVAL_STAGE[stage]
    if lifecycle.get("previous_stage") != expected_previous:
        errors.append(f"{prefix} illegal or skipped transition")

    stage_index = APPROVAL_STAGES.index(stage)
    loaded_receipts: dict[str, dict] = {}
    for receipt_index, receipt_field in enumerate(STAGE_RECEIPTS, start=1):
        binding = lifecycle.get(receipt_field)
        if receipt_index <= stage_index:
            if not isinstance(binding, dict):
                errors.append(f"{prefix} {stage} requires {receipt_field}")
            else:
                receipt = validate_stage_receipt(
                    binding,
                    receipt_field=receipt_field,
                    item=item,
                    now=now,
                    errors=errors,
                )
                if receipt is not None:
                    loaded_receipts[receipt_field] = receipt
        elif binding is not None:
            errors.append(f"{prefix} future receipt {receipt_field} must be null")

    prior_recorded: datetime | None = None
    for receipt_field in STAGE_RECEIPTS[:stage_index]:
        receipt = loaded_receipts.get(receipt_field)
        if receipt is None:
            continue
        try:
            recorded = datetime.fromisoformat(receipt["recorded_at"])
        except (KeyError, TypeError, ValueError):
            continue
        if prior_recorded is not None and recorded < prior_recorded:
            errors.append(f"{prefix} receipt chronology is not monotonic")
        prior_recorded = recorded

    readiness = loaded_receipts.get("readiness_receipt")
    authorization = loaded_receipts.get("authorization_receipt")
    execution = loaded_receipts.get("execution_receipt")
    observation = loaded_receipts.get("observation_receipt")
    closure = loaded_receipts.get("closure_receipt")
    authorized_at = (
        _receipt_time(authorization, "authorized_at") if authorization else None
    )
    executed_at = _receipt_time(execution, "executed_at") if execution else None
    observed_at = _receipt_time(observation, "started_at") if observation else None
    closed_at = _receipt_time(closure, "closed_at") if closure else None
    if authorization is not None and readiness is not None:
        ready_recorded = parse_timestamp(
            readiness.get("recorded_at"), errors=errors, label=f"{prefix} readiness time"
        )
        if authorized_at is not None and ready_recorded is not None and authorized_at < ready_recorded:
            errors.append(f"{prefix} authorization predates readiness")
    if readiness is not None and current_review_recorded_at is not None:
        ready_recorded = parse_timestamp(
            readiness.get("recorded_at"),
            errors=errors,
            label=f"{prefix} readiness review ordering",
        )
        if ready_recorded is not None and ready_recorded < current_review_recorded_at:
            errors.append(f"{prefix} readiness predates current detached review")
    if executed_at is not None and authorized_at is not None and executed_at < authorized_at:
        errors.append(f"{prefix} execution predates authorization")
    if observed_at is not None and executed_at is not None and observed_at < executed_at:
        errors.append(f"{prefix} observation predates execution")
    if closed_at is not None and observed_at is not None and closed_at < observed_at:
        errors.append(f"{prefix} closure predates observation")
    cutoff = item.get("observation_cutoff_at")
    if executed_at is not None and isinstance(cutoff, str):
        try:
            cutoff_at = datetime.fromisoformat(cutoff)
        except ValueError:
            cutoff_at = None
        if cutoff_at is not None and cutoff_at <= executed_at:
            errors.append(f"{prefix} observation cutoff must follow execution")
    readiness_recorded_at = None
    if readiness is not None:
        readiness_recorded_at = parse_timestamp(
            readiness.get("recorded_at"),
            errors=errors,
            label=f"{prefix} readiness recorded_at",
        )
    return stage, {
        "readiness_recorded_at": readiness_recorded_at,
        "authorized_at": authorized_at,
        "executed_at": executed_at,
        "observed_at": observed_at,
        "closed_at": closed_at,
    }


def validate_approval_queue(
    approval_queue: object,
    *,
    approval_actions: set[str],
    ca_review_status: str,
    ca_reviewed_at: datetime | None,
    experiment: dict | None,
    spec_path: Path | None,
    now: datetime,
    snapshot_at: datetime,
    errors: list[str],
) -> str | None:
    if not isinstance(approval_queue, list):
        errors.append("approval_queue must be a list")
        return None
    if len(approval_queue) != 1:
        errors.append("approval_queue must contain only the exact CA012650 entry")
    if not approval_queue:
        return None
    item = approval_queue[0]
    if not exact_object(item, APPROVAL_KEYS, errors=errors, label="approval_queue[0]"):
        if not isinstance(item, dict):
            return None
    assert isinstance(item, dict)
    prefix = "CA012650 approval:"
    if item.get("id") != EXPECTED_CA_APPROVAL_ID:
        errors.append(f"{prefix} approval id changed")
    if item.get("action") != "external_contact" or item.get("action") not in approval_actions:
        errors.append(f"{prefix} action is outside the exact approval envelope")
    if item.get("external_effect") is not True:
        errors.append(f"{prefix} external_effect must be true")
    if item.get("experiment_id") != EXPECTED_CA_EXPERIMENT_ID:
        errors.append(f"{prefix} experiment id changed")
    target = item.get("exact_target")
    if exact_object(target, APPROVAL_TARGET_KEYS, errors=errors, label=f"{prefix} target"):
        if target != EXPECTED_CA_TARGET:
            errors.append(f"{prefix} exact target changed")
    if item.get("exact_channel") != EXPECTED_CA_CHANNEL:
        errors.append(f"{prefix} exact channel changed")
    if item.get("channel_source") != EXPECTED_CA_CHANNEL_SOURCE:
        errors.append(f"{prefix} channel source changed")

    message_path = verify_bound_file(
        item.get("message_binding"),
        base=RESEARCH_ROOT,
        errors=errors,
        label=f"{prefix} message",
        closed=True,
    )
    if experiment is not None and spec_path is not None:
        if item.get("experiment_id") != experiment.get("experiment_id"):
            errors.append(f"{prefix} experiment_id differs from bound experiment")
        experiment_target = experiment.get("exact_target")
        if not isinstance(experiment_target, dict):
            errors.append(f"{prefix} bound experiment exact_target is missing")
        else:
            experiment_subset = {
                "public_building_id": experiment_target.get("public_building_id"),
                "public_record_location": experiment_target.get("public_record_location"),
                "routing_contact_only": experiment_target.get("routing_contact_only"),
            }
            if target != experiment_subset or experiment_subset != EXPECTED_CA_TARGET:
                errors.append(f"{prefix} target differs from bound experiment")
            if item.get("exact_channel") != experiment_target.get(
                "allowed_future_channel"
            ):
                errors.append(f"{prefix} channel differs from bound experiment")
            if item.get("channel_source") != experiment_target.get("channel_source"):
                errors.append(f"{prefix} channel source differs from bound experiment")
        experiment_message_path, experiment_message_hash = _experiment_message_binding(
            experiment, spec_path, errors=errors
        )
        message_binding = item.get("message_binding")
        state_hash = (
            message_binding.get("sha256") if isinstance(message_binding, dict) else None
        )
        if message_path != experiment_message_path or state_hash != experiment_message_hash:
            errors.append(f"{prefix} message differs from bound experiment")

    stage, lifecycle_times = validate_lifecycle(
        item,
        now=snapshot_at,
        current_review_recorded_at=ca_reviewed_at,
        errors=errors,
    )
    if stage is None:
        return None
    if item.get("claim_boundary") != EXPECTED_CA_APPROVAL_CLAIM_BOUNDARIES.get(stage):
        errors.append(f"{prefix} claim boundary differs from exact lifecycle stage")
    if APPROVAL_STAGES.index(stage) >= APPROVAL_STAGES.index("request_ready"):
        if ca_review_status != "passed_current_candidate" or ca_reviewed_at is None:
            errors.append(
                f"{prefix} request_ready requires the current exact detached PASS receipt"
            )
    refresh_timestamps = validate_source_refresh(
        item.get("pre_send_source_refresh"),
        stage=stage,
        validation_now=now,
        snapshot_at=snapshot_at,
        errors=errors,
    )
    latest_refresh_at = max(refresh_timestamps) if refresh_timestamps else None
    for event_name in ("readiness_recorded_at", "authorized_at", "executed_at"):
        event_time = lifecycle_times.get(event_name)
        if (
            latest_refresh_at is not None
            and event_time is not None
            and event_time < latest_refresh_at
        ):
            errors.append(
                f"{prefix} {event_name} predates the completed source refresh"
            )
    if APPROVAL_STAGES.index(stage) >= APPROVAL_STAGES.index("executed_once"):
        validate_execution_refresh_window(
            executed_at=lifecycle_times.get("executed_at"),
            refresh_timestamps=refresh_timestamps,
            errors=errors,
        )

    missing = item.get("missing_bindings")
    if not isinstance(missing, list) or any(
        not isinstance(value, str) or not value for value in missing
    ):
        errors.append(f"{prefix} missing_bindings must be a string list")
        missing_set: set[str] = set()
    else:
        if len(missing) != len(set(missing)):
            errors.append(f"{prefix} missing_bindings contains duplicates")
        missing_set = set(missing)

    if stage == "blocked_missing_bindings":
        if missing_set != REQUIRED_CA_MISSING_BINDINGS:
            errors.append(f"{prefix} exact missing bindings changed")
        if item.get("sender_account") is not None:
            errors.append(f"{prefix} blocked sender account must be null")
        if item.get("observation_cutoff_at") is not None:
            errors.append(f"{prefix} blocked observation cutoff must be null")
        if item.get("exact_user_authorization") is not False:
            errors.append(f"{prefix} blocked exact user authorization must be false")
        expected_flags = (False, False, False, False)
    else:
        if missing_set:
            errors.append(f"{prefix} request-ready or later stage cannot retain missing bindings")
        sender = item.get("sender_account")
        if not isinstance(sender, str) or not EMAIL_RE.fullmatch(sender):
            errors.append(f"{prefix} request-ready or later stage needs an exact sender account")
        cutoff = parse_timestamp(
            item.get("observation_cutoff_at"),
            errors=errors,
            label=f"{prefix} observation_cutoff_at",
        )
        if stage in {"request_ready", "authorized_once"} and cutoff is not None:
            if cutoff.astimezone(timezone.utc) <= now:
                errors.append(f"{prefix} pre-execution observation cutoff has expired")
        if stage == "request_ready":
            if item.get("exact_user_authorization") is not False:
                errors.append(f"{prefix} request_ready cannot self-authorize")
            expected_flags = (False, True, False, False)
        elif stage == "authorized_once":
            if item.get("exact_user_authorization") is not True:
                errors.append(f"{prefix} authorized_once requires exact user authorization")
            expected_flags = (True, True, True, False)
        else:
            if item.get("exact_user_authorization") is not True:
                errors.append(f"{prefix} post-execution state must retain authorization fact")
            expected_flags = (False, False, False, True)

    actual_flags = (
        item.get("authorized"),
        item.get("ready"),
        item.get("executable"),
        item.get("authorization_consumed"),
    )
    if actual_flags != expected_flags:
        errors.append(
            f"{prefix} flags do not match lifecycle stage; external stages default unreachable"
        )
    return stage


def validate(state: dict, *, now: datetime | None = None) -> list[str]:
    errors: list[str] = []
    validation_now = now or datetime.now(timezone.utc)
    if validation_now.tzinfo is None:
        raise ValueError("injected now must include a timezone")
    validation_now = validation_now.astimezone(timezone.utc)

    if not exact_object(state, TOP_LEVEL_KEYS, errors=errors, label="active state"):
        # Continue where possible so one run exposes all independent schema faults.
        pass
    if state.get("schema_version") != EXPECTED_SCHEMA_VERSION:
        errors.append("active state schema_version changed")
    if state.get("state_scope") != (
        "Current durable state for the independent personal-asset and cash-flow "
        "research root; legacy documents are locators or evidence subjects, never authority."
    ):
        errors.append("active state scope changed")
    snapshot = validate_freshness(state, now=validation_now, errors=errors)
    snapshot_at = (
        snapshot.astimezone(timezone.utc) if snapshot is not None else validation_now
    )

    truth = state.get("truth_policy")
    if exact_object(truth, TRUTH_POLICY_KEYS, errors=errors, label="truth_policy"):
        assert isinstance(truth, dict)
        if truth.get("old_documents_are_authority") is not False:
            errors.append("truth_policy: old_documents_are_authority must be false")
        if truth.get("ai_summary_is_evidence") is not False:
            errors.append("truth_policy: ai_summary_is_evidence must be false")
        exact_string_set(
            truth.get("required_claim_classes"),
            ALLOWED_CLAIM_CLASSES,
            errors=errors,
            label="truth_policy required_claim_classes",
        )

    envelope = state.get("authority_envelope")
    approval_actions: set[str] = set()
    if exact_object(
        envelope, AUTHORITY_ENVELOPE_KEYS, errors=errors, label="authority_envelope"
    ):
        assert isinstance(envelope, dict)
        if envelope.get("default") != "deny_high_impact_or_external_actions":
            errors.append("authority_envelope: default must deny high-impact/external actions")
        exact_string_set(
            envelope.get("autonomous_scopes"),
            AUTONOMOUS_SCOPES,
            errors=errors,
            label="authority_envelope autonomous_scopes",
        )
        if exact_string_set(
            envelope.get("explicit_approval_required"),
            REQUIRED_APPROVAL_ACTIONS,
            errors=errors,
            label="authority_envelope explicit_approval_required",
        ):
            approval_actions = set(envelope["explicit_approval_required"])
        hard = envelope.get("hard_boundaries")
        expected_hard = {
            "investment_paper_only": True,
            "investment_human_final": True,
            "broker_connection_allowed": False,
            "live_order_allowed": False,
        }
        if exact_object(
            hard, HARD_BOUNDARY_KEYS, errors=errors, label="authority_envelope hard_boundaries"
        ) and hard != expected_hard:
            errors.append("investment hard boundaries changed")

    workstreams = state.get("workstreams")
    stream_by_id: dict[str, dict] = {}
    if not isinstance(workstreams, list):
        errors.append("workstreams must be a list")
    else:
        for index, stream in enumerate(workstreams):
            if not isinstance(stream, dict):
                errors.append(f"workstreams[{index}]: must be an object")
                continue
            stream_id = stream.get("id")
            if not isinstance(stream_id, str) or not stream_id:
                errors.append(f"workstreams[{index}]: missing id")
                continue
            if stream_id in stream_by_id:
                errors.append(f"workstream {stream_id}: duplicate id")
                continue
            stream_by_id[stream_id] = stream
        if set(stream_by_id) != set(WORKSTREAM_KEYS) or len(workstreams) != len(
            WORKSTREAM_KEYS
        ):
            errors.append("workstreams must be the exact declared three-workstream set")

    for stream in stream_by_id.values():
        validate_common_workstream(stream, now=snapshot_at, errors=errors)

    strategy = stream_by_id.get("long_term_capability_strategy")
    if strategy is not None:
        validate_strategy(strategy, errors)
        validate_static_workstream_semantics(strategy, errors)

    opportunity = stream_by_id.get("opportunity_to_transaction")
    experiment: dict | None = None
    spec_path: Path | None = None
    ca_review_status = "pending_fresh_review"
    ca_reviewed_at: datetime | None = None
    if opportunity is not None:
        ca_review_status, ca_reviewed_at = validate_review_receipts(
            opportunity, now=snapshot_at, errors=errors
        )
        validate_ca_review_prose(ca_review_status, errors)
        experiment, spec_path = validate_experiment(
            opportunity,
            ca_review_status=ca_review_status,
            now=snapshot_at,
            errors=errors,
        )

    investment = stream_by_id.get("investment_discipline")
    if investment is not None:
        if investment.get("status") != "blocked_internal":
            errors.append("investment workstream must remain blocked_internal")
        expected_safety = {
            "paper_only": True,
            "human_final": True,
            "live_trading": False,
            "broker_integration": False,
        }
        safety = investment.get("safety_boundary")
        if exact_object(
            safety,
            SAFETY_BOUNDARY_KEYS,
            errors=errors,
            label="investment safety_boundary",
        ) and safety != expected_safety:
            errors.append("investment safety boundary changed")
        validate_investment_audit(investment, now=snapshot_at, errors=errors)
        validate_static_workstream_semantics(investment, errors)

    stage = validate_approval_queue(
        state.get("approval_queue"),
        approval_actions=approval_actions,
        ca_review_status=ca_review_status,
        ca_reviewed_at=ca_reviewed_at,
        experiment=experiment,
        spec_path=spec_path,
        now=validation_now,
        snapshot_at=snapshot_at,
        errors=errors,
    )
    if opportunity is not None and stage is not None:
        expected_opportunity_status = OPPORTUNITY_STATUS_BY_STAGE[stage]
        if opportunity.get("status") != expected_opportunity_status:
            errors.append(
                "opportunity workstream status does not match approval lifecycle stage"
            )
        current = opportunity.get("current_experiment")
        if isinstance(current, dict):
            if current.get("external_action_status") != EXPERIMENT_ACTION_STATUS_BY_STAGE[
                stage
            ]:
                errors.append(
                    "opportunity current_experiment external action status does not match lifecycle"
                )
            expected_authorized = stage == "authorized_once"
            if current.get("external_contact_authorized") is not expected_authorized:
                errors.append(
                    "opportunity current_experiment authorization flag does not match lifecycle"
                )
        queue = state.get("approval_queue")
        approval_item = queue[0] if isinstance(queue, list) and queue else None
        validate_opportunity_semantics(
            opportunity,
            ca_review_status=ca_review_status,
            stage=stage,
            approval_item=approval_item,
            errors=errors,
        )
    return errors


def main() -> int:
    load_errors: list[str] = []
    state = load_json(STATE_PATH, errors=load_errors, label="active state")
    if state is None:
        for error in load_errors:
            print(f"ERROR: {error}")
        return 1
    errors = validate(state)
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print("PASS: active state closed schema, freshness, evidence, lifecycle, and authority validate")
    print(
        "NOTE: this does not validate demand, payment, delivery, profit, investment "
        "performance, review quality, or runtime acceptance"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
