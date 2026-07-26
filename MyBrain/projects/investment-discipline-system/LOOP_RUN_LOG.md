# 循环运行记录｜投研纪律系统

此入口由 `scripts/derive_project_state.py refresh` 整文件生成；任何额外内容都会使 freshness 检查失败。

<!-- PROJECT_STATE_VIEW:START -->
```json
{
  "basis": {
    "facts": [
      {
        "canonical_sha256": "dbe4bef02c64159c36ebe68dbf2ba5a1aa63c7dc6e51aa3e4fd401d9c28318a8",
        "json_pointers": [
          "/depends_on",
          "/packet_id",
          "/routing/action_id",
          "/routing/addresses_finding_ids",
          "/routing/phase_id",
          "/routing/route_order",
          "/routing/summary",
          "/schema_version",
          "/state"
        ],
        "path": ".work_packets/packets/WP-CI-ASSURANCE-RUNTIME.packet.json"
      },
      {
        "canonical_sha256": "907614f4dde773b57790c9008189f528f745e2b1592469a3e6676c5badab28cb",
        "json_pointers": [
          "/depends_on",
          "/packet_id",
          "/routing/action_id",
          "/routing/addresses_finding_ids",
          "/routing/phase_id",
          "/routing/route_order",
          "/routing/summary",
          "/schema_version",
          "/state"
        ],
        "path": ".work_packets/packets/WP-CI-LINT-BASELINE.packet.json"
      },
      {
        "canonical_sha256": "7cada68c1ebea5a813e86448336d2e22a4d7233a54054c3505268d012e3e5c81",
        "json_pointers": [
          "/depends_on",
          "/packet_id",
          "/routing/action_id",
          "/routing/addresses_finding_ids",
          "/routing/phase_id",
          "/routing/route_order",
          "/routing/summary",
          "/schema_version",
          "/state"
        ],
        "path": ".work_packets/packets/WP-CONTRACT-SUPERSESSION-CLOSURE-POLICY.packet.json"
      },
      {
        "canonical_sha256": "0eecc5b44bcb466c23fea247852b80e670e7911d2086e089b4d3f89e80138331",
        "json_pointers": [
          "/packet_id",
          "/schema_version",
          "/state",
          "/superseded_by"
        ],
        "path": ".work_packets/packets/WP-CONTRACT-SUPERSESSION.packet.json"
      },
      {
        "canonical_sha256": "782170a462ca5ac1d1d871cea62494cf15af16bd06a455c60523e5373cd8462b",
        "json_pointers": [
          "/depends_on",
          "/packet_id",
          "/routing/action_id",
          "/routing/addresses_finding_ids",
          "/routing/phase_id",
          "/routing/route_order",
          "/routing/summary",
          "/schema_version",
          "/state"
        ],
        "path": ".work_packets/packets/WP-DEPENDENCY-BOUNDARY.packet.json"
      },
      {
        "canonical_sha256": "4579d139bb5e81d1ec27ad26834105916ba8569ef3a509817c90a70e5e5986ab",
        "json_pointers": [
          "/depends_on",
          "/packet_id",
          "/routing/action_id",
          "/routing/addresses_finding_ids",
          "/routing/phase_id",
          "/routing/route_order",
          "/routing/summary",
          "/schema_version",
          "/state"
        ],
        "path": ".work_packets/packets/WP-FREEZE-CLOSURE-PROTOCOL.packet.json"
      },
      {
        "canonical_sha256": "12d384cd32a0a8cfb1f9881c8375592718ddcc298a18784e18ee94753fddb2e9",
        "json_pointers": [
          "/depends_on",
          "/packet_id",
          "/routing/action_id",
          "/routing/addresses_finding_ids",
          "/routing/phase_id",
          "/routing/route_order",
          "/routing/summary",
          "/schema_version",
          "/state"
        ],
        "path": ".work_packets/packets/WP-METHOD-INTEGRATION.packet.json"
      },
      {
        "canonical_sha256": "3adab1957d0af2cfe60575d60d09a83d8a98a99ede31402aafc7f4d75d9bb10b",
        "json_pointers": [
          "/depends_on",
          "/packet_id",
          "/routing/action_id",
          "/routing/addresses_finding_ids",
          "/routing/phase_id",
          "/routing/route_order",
          "/routing/summary",
          "/schema_version",
          "/state"
        ],
        "path": ".work_packets/packets/WP-METHOD-RUNTIME-FOUNDATION.packet.json"
      },
      {
        "canonical_sha256": "f7dd5724b98a0fd64c17965e541ad6f86c519cda43e0ba8d6d51303fe5e15fb2",
        "json_pointers": [],
        "path": "@runtime/execution-freshness"
      },
      {
        "canonical_sha256": "a7d62337b74701019eb2cf3db68b3150b5bb44bcbecbc94d7ea5e9be822daf53",
        "json_pointers": [],
        "path": "@runtime/work-packets"
      },
      {
        "canonical_sha256": "08e5c5bddf249a162017bd599fa19a0cc5f47a80600a53d3414b67b74fd60ae4",
        "json_pointers": [
          "/change_control/closure_mutation_policy/freeze_state_authority",
          "/contract_id",
          "/schema_version",
          "/status"
        ],
        "path": "governance/ACCEPTANCE_CONTRACT_V1.json"
      },
      {
        "canonical_sha256": "30718ac826eb2b79ae608259ac8be286e50e4eb6073ff36d6bb6cae89f15c1cb",
        "json_pointers": [
          "/challenge/rounds/9/candidate_commit",
          "/challenge/rounds/9/candidate_tree",
          "/challenge/rounds/9/evidence_path",
          "/challenge/rounds/9/evidence_sha256",
          "/challenge/rounds/9/findings",
          "/challenge/rounds/9/id",
          "/challenge/rounds/9/result",
          "/challenge/rounds/9/review_sequence"
        ],
        "path": "governance/AI_PROJECT_RESEARCH_REGISTER_V1.json"
      },
      {
        "canonical_sha256": "e39f603a5ebcff23859d200f9c9dc20f6c19d48aa185d09445bd42e31abcc3ff",
        "json_pointers": [],
        "path": "governance/FROZEN_BUNDLE_V1.json"
      },
      {
        "canonical_sha256": "6220e2a16402cc9821d53e1bbb37195c21d4e6769a02213f311f38732c2e674e",
        "json_pointers": [
          "/packet_routing",
          "/phase_model",
          "/projection_schema_version",
          "/review_source",
          "/schema_version",
          "/sources/acceptance_contract",
          "/sources/review_register",
          "/sources/runtime_authorities",
          "/sources/work_packets"
        ],
        "path": "governance/PROJECT_STATE_VIEW_POLICY_V1.json"
      }
    ],
    "state_basis_sha256": "d2ca110c60c1ea555c2e847a0e227645004798e4d3606af2faedd50928e9f682"
  },
  "latest_blocking_review": {
    "evidence_path": "audits/PROJECT_GOVERNANCE_ADVERSARIAL_REVIEW_R10_2026-07-25.md",
    "open_finding_ids": [
      "R10-CRIT-CIRCULAR-COVERAGE",
      "R10-CRIT-REGRESSION-BUDGET",
      "R10-CRIT-STATE-FRESHNESS",
      "R10-MAJOR-LIVING-REVIEW",
      "R10-MAJOR-LOOP-FRESHNESS",
      "R10-MAJOR-RESEARCH-STATUS",
      "R10-MAJOR-WORK-GRAPH"
    ],
    "review_id": "CHALLENGE-10",
    "review_sequence": 10,
    "subject_candidate_commit": "aa0a5966e114d6d7c87aa14fe2c27253f9f89f26"
  },
  "next_action": {
    "action_id": "ACT-METHOD-RUNTIME-FOUNDATION",
    "packet_id": "WP-METHOD-RUNTIME-FOUNDATION",
    "summary": "Bind generated project-state views and current execution-attempt freshness before method-governance integration."
  },
  "phase": {
    "blocking_gate_ids": [
      "GATE-DESIGN-FREEZE-OPEN-FINDINGS",
      "GATE-DESIGN-FREEZE-AUTHORITY-MISSING"
    ],
    "id": "design_freeze",
    "state": "blocked"
  },
  "schema_version": "project-state-view/v1"
}
```
<!-- PROJECT_STATE_VIEW:END -->
