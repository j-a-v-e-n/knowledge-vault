# C6 macOS Sandbox Probe：证据与边界

- 当前证据状态：`HISTORICAL-PROBE-PRESERVED / ITERATION-B-HOST-INTEGRATION-PASS / EXACT-CODE-INTERFACE-REVIEW-PASS / NOT-A-FINAL-CANDIDATE-REVIEW`
- 证据用途：C6 declarative shadow runner 的 host-specific defense-in-depth 设计输入
- 裁决：作为唯一 defense boundary 为 `NO-GO`；与 closed declarative IR、exact snapshot、干净启动器、FD 清理和资源限制组合时为 `CONDITIONALLY USEFUL`
- 项目写入：probe 本身未修改项目文件；全部临时 profile/script/fixture 位于 `/private/tmp/otts-sandbox-probe-019fa520/`
- 外部动作：未访问凭据或用户数据，未联系外部网络；网络测试只使用 loopback、无数据 UDP connect 与本地 `socketpair()`

## Declarative Gate iteration B：当前 exact evidence

本节记录 iteration A 被拒绝后的新代码与接口证据；后面的 Python 3.14 probe 原样保留为历史设计输入。iteration B exact files：

```text
8ca4d90c958ea04adf14d003226a620a4000ad805e439823b5c5cc34a7e7ebb9  SHADOW_CAPABILITY_POLICY.json
ba5bb3aeb55b14eaa8135c8367ed16295d0782a4f7813b337397998117edbc97  run_shadow_acceptance.py
a870a2262633b19d40bd892a00c72240d8e8f4c65be436f32573cc8378176eec  test_shadow_acceptance.py
823acd5aba8ac2949312c663acd25bd4c3de203a7c18604d9da066df2f2d45b3  verify_post_closure_manifest.py
d6ea9916c9bff14e9111d5b881dce518a35df9d9c23a9841b1e3f84d91f9bcad  test_phase_manifests.py
```

受管 suite 明确返回 `OK (skipped=1)`：唯一 skip 是 host-required positive path，不能被解释为主机隔离已实测。随后在允许 nested `sandbox-exec` 的真实 host context 执行：

```text
OTTS_REQUIRE_HOST_SANDBOX=1 python3 -B test_shadow_acceptance.py -v
OK
```

该强制路径实际完成 opened-and-unlinked input/output FD、inline exact profile、全部 required denial probes 与 worker positive result；没有 unsandboxed fallback。独立只读 reviewer `/root/declarative_gate_code_review` 又对上列 exact bytes 给出代码/接口 `PASS`，无 Critical、无 Major；phase-boundary suite 同时为 `OK`。

Iteration B 的 final runtime 是：

```text
/Applications/Xcode.app/Contents/Developer/Library/Frameworks/Python3.framework/Versions/3.9/Resources/Python.app/Contents/MacOS/Python
```

`/Applications/Xcode.app` 到 runtime/Python home 的 anchor chain 必须为 root-owned 且 group/other non-writable；`/Applications` 父目录的 admin-group writable 状态进入显式 residual，hostile same-UID/admin race-and-restore 排除在本地接受 threat model 外。每个实际 worker result 都把当次加载的 Python module file rows 与 closure digest 加入 runtime TCB；它不声称闭合 dynamic libraries 或完整 host runtime。

执行数据只从 runner 预先打开、核验并 unlink 的 descriptor 读取；profile 以 exact bytes 使用 `-p`，target-controlled pathname reopen count 必须是 non-boolean integer zero。回执必须逐字保存：same-UID concurrent mutation resistance 未证明、host universal noninterference 未证明、Darwin 没有 host RSS hard limit、只执行 fixed structural IR bounds、aggregate deadline 已执行，以及所有 capability/runtime/deployment/freeze/external-action authority 均为 false。

剩余 Minor：stdout/stderr 的命名上限与结构值累计上限包含事后检测层；parent 配置了精确 `close_fds/pass_fds`，但 worker 没有在 sandbox-exec 后枚举实际 FD set，所以报告只能说 `PARENT_CONFIGURED_ONLY`。这些限制未被重命名成更强证明。

本节 PASS 只关闭 Gate 代码/接口拒绝项；它不等于完整 C6 manifest-bound review，不授权创建 governance/shadow root，也不证明任何商机、客户、交易、盈利或现实动作。

## 主机与工具身份

```text
ProductName:    macOS
ProductVersion: 26.2
BuildVersion:   25C56
architecture:   arm64
sandbox-exec:   /usr/bin/sandbox-exec
```

本机 `man sandbox-exec` 逐字标记 `sandbox-exec – execute within a sandbox (DEPRECATED)`。在 Codex 已有 sandbox 内直接嵌套调用会得到：

```text
sandbox-exec: sandbox_apply: Operation not permitted
exit=71
```

因此 integration 必须把 unavailable、profile compile failure 或 `sandbox_apply` failure 解释为 `BLOCKED`，不得回退到 unsandboxed execution。

## Tight profile

临时原件：`/private/tmp/otts-sandbox-probe-019fa520/profile-python314-tight.sb`

SHA-256：

```text
bda3f89201b9ff9e1d4fa8aad58449860d1fe525d13fca9e913bdef99c6757d6
```

Exact profile：

```scheme
(version 1)
(deny default)
(deny network*)
(deny process-fork)

(allow process-exec (literal (param "PYTHON_EXEC")))

(allow file-read* file-test-existence file-map-executable
  (subpath (param "PYTHON_HOME"))
  (subpath (param "STAGING_DIR"))
  (subpath (param "OUTPUT_DIR"))
  (subpath "/System")
  (subpath "/Library/Apple")
  (subpath "/usr/lib")
  (subpath "/usr/share")
  (literal "/")
  (literal "/Library")
  (literal "/Library/Frameworks")
  (literal "/Library/Frameworks/Python.framework")
  (literal "/Library/Frameworks/Python.framework/Versions")
  (literal "/Library/Frameworks/Python.framework/Versions/3.14")
  (literal "/private")
  (literal "/private/tmp")
  (literal (param "PROBE_ROOT"))
  (literal "/dev/null")
  (literal "/dev/random")
  (literal "/dev/urandom")
  (literal "/private/etc/localtime"))

(allow file-write* (subpath (param "OUTPUT_DIR")))
(allow sysctl-read)
```

不使用 `system.sb`：该文件自称 Apple private interface；它允许更多 system paths、Mach services 与 syslog outbound，且 imported bytes 不进入调用方 profile hash，不能形成可复算的 effective policy identity。对照 profile SHA-256 为 `966b0378fa89b3a4cdddf6ef5ba77a83925004b1224187cda57527d8ebed4f3b`，只作为比较，不进入推荐合同。

## Python 启动兼容性

`/Library/Frameworks/Python.framework/Versions/3.14/bin/python3` 是 launcher；在 `deny process-fork` 下它试图 `posix_spawn`：

```text
/Library/Frameworks/Python.framework/Versions/3.14/Resources/Python.app/Contents/MacOS/Python
```

并得到：

```text
Undefined error: 0
exit=1
```

实测可运行的 final runtime 是：

```text
/Library/Frameworks/Python.framework/Versions/3.14/Resources/Python.app/Contents/MacOS/Python
```

Runner 不能只做 `realpath bin/python3`；它必须识别、验证并 hash-bind 实际 final runtime 与 Python home。该结论是当前 distribution/host 事实，不是跨 Python distribution 规则。

## 主探针观察

在空环境、tight profile、final runtime、精确 staging/output 参数下，主探针 `exit=0`：

```json
{
  "fixture_read": "ALLOWED",
  "allowed_write": "ALLOWED",
  "forbidden_read": "EPERM",
  "forbidden_write": "EPERM",
  "network_socket_create": "ALLOWED",
  "network_bind_loopback": "EPERM",
  "network_udp_connect_loopback": "EPERM",
  "child_same_runtime": "EPERM"
}
```

这只支持以下精确表述：exact staging read 与 output-subtree write 可用；self-generated sibling read、staging write、loopback bind/connect 和 `os.posix_spawn` 被当前 effective profile 拒绝。`socket()` 对象本身仍能创建，所以不能写成“socket capability 不存在”。

使用 `(deny default)` 且不允许 initial interpreter exec 时，Python workload 没有启动，marker 不存在：profile 在 workload 前生效。但 initial exec 的 allow rule 会保留到 workload 内。

## 必须保留的反例

### Same-process re-exec

因为 initial launch 需要允许 exact final runtime 的 `process-exec`，sandboxed Python 内对同一 executable 的 `os.execve` 实测成功：

```text
exit=0
reexec-marker-python314-tight.txt contains: reexec-ran
```

OS sandbox 仍继承，但 Python audit hook 可被清空或 workload 可被替换。因此 artifact 不能包含 target-controlled code；process absence 的承重证据必须来自 closed IR 没有 import/os/exec/opcode，而不是 sandbox profile 自证。

### Inherited file/socket descriptors

Sandbox 不撤销启动前已取得的能力：

```text
FD 3 os.read -> b'synthetic-forbidden\n' ; exit=0
FD 4 os.write -> 12 ; file content: OVERWRITTEN ; exit=0
socketpair child_returncode=0 ; received=inherited-socket-write
```

因此 launcher contract 必须固定：

```python
close_fds=True
pass_fds=()
stdin=subprocess.DEVNULL
```

stdout/stderr 只能绑定 runner-created bounded files；环境从无秘密 allowlist 构造。Parent 必须使用 fixed `close_fds/pass_fds`，配置中出现任何额外 handle 都使本地 acceptance 失败；iteration B 尚未在 sandbox-exec 后枚举实际 FD set，因此不能把 parent configuration 说成完整 runtime-FD absence proof。

### Parameter substitution

- 缺少必需 `-D` 参数：profile compile `exit=65`。
- 重复 key 不拒绝；最后一个值生效。把 `OUTPUT_DIR` 第二次指向 staging 后，原 output write 得 `EPERM`，staging write 反而 `ALLOWED`，且 `exit=0`。

所以 argv 必须由 runner 固定构造，不使用 shell，不接受 target-controlled profile/path 参数，主动拒绝重复 key，并在 launch 前验证绝对路径、parent、owner、mode、node type 与 link count。

### Links 与 provenance

- staging symlink 指向 forbidden target：read `EPERM`。
- staging hardlink 指向 forbidden inode：通过 staging path 读取成功。

这说明 path sandbox 不证明数据来源。源 inventory 必须拒绝 symlink、hardlink、special node；同一个 `O_NOFOLLOW` opened regular single-link object 完成 bounded hash+copy。后续 Gate 不能把 owner-read-only pathname 称为 immutable：同 UID 进程仍可 `chmod` 后覆写。修订方向必须让 worker 只从 runner 预先打开、复核并 unlink 的 descriptor 读取 exact snapshot，并把同 UID/管理员并发篡改抵抗保留为未证明项。

## C6 可承重合同

- shadow artifact 只含 canonical data/text 与 exact closed declarative IR；不执行 artifact-provided Python/native/script/plugin/template。
- Tight profile bytes、final runtime、Python home、`sandbox-exec` binary、OS build 与 architecture 进入 platform-bound runtime TCB identity。
- Runner 创建私有临时状态，固定 argv 与环境，以 `close_fds/pass_fds` 配置关闭一切未明确传递的继承 FD，不使用 shell；source 使用 read-once opened-object snapshot，worker 输入与有界 stdout/stderr/output 只通过 runner 预先打开、复核并 unlink 的 descriptor 传递，profile 以 exact bytes 直接传入而不重开 profile pathname；未做 post-sandbox FD enumeration 的事实必须留在回执中。
- Sandbox canary、profile compile/apply、read/write/network/process probes 任一异常即 `BLOCKED`；绝不 fallback。
- CPU、wall time、aggregate deadline、file size、FD/process、stdout/stderr、output count/bytes 与 IR entries/cases/nodes/depth/fan-out/total-input/CAS 配额由固定 resource policy 控制；CAS 与显式 output 配额在 create/write 前检查，stdout/stderr 命名 ceiling 与结构值累计 ceiling 保留事后检测层，并由更宽的 fixed hard/structural caps 约束。Darwin 首版没有已证明的进程级 memory/RSS 硬限制，只能报告结构性分配上限；`sandbox-exec` 不提供这些保证。
- Receipt 只能声明 exact local deterministic declarative evaluation、当前 effective host probes、snapshot/output identities 与全部 authority false。

## 明确不证明

本 probe 不证明未来 macOS/SBPL 兼容、跨平台隔离、`system.sb` 稳定、全部 native/Mach/IOKit/shared-memory/signal/FD 路径穷尽、sandbox 能阻止 inherited capability、fixture provenance、同 UID/管理员并发篡改抵抗、完整 Python/dynamic-library/host TCB 闭包、进程级 memory/RSS 硬限制、runner 无 bug、host-level universal noninterference、保密性、production safety 或任何外部行动权限。

因此 `sandbox-exec` 只能是当前主机的 deprecated/unsupported defense-in-depth canary；根因级边界是 target-controlled IR 对外部能力不可表达、exact snapshot 与独立审查。
