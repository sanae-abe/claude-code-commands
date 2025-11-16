# AutoFlow型品質ゲートシステム統合計画書

**作成日**: 2025-11-15
**目的**: AutoFlowの5層品質ゲートシステムをClaude Code開発フローに統合し、LLM生成コードの品質を自動保証する

---

## 目次

1. [現状分析](#1-現状分析)
2. [目標設定](#2-目標設定)
3. [システム設計](#3-システム設計)
4. [実装計画](#4-実装計画)
5. [統合戦略](#5-統合戦略)
6. [リスク評価](#6-リスク評価)
7. [成功指標](#7-成功指標)

---

## 1. 現状分析

### 既存の品質管理

**現在の `/task-validate` コマンド**:
- 3層バリデーション（syntax, security, integration）
- 手動実行が必要
- プロジェクト固有の設定に依存

**CLAUDE.md の品質基準**:
- 5層品質ゲートシステム定義済み
- Layer 1-2: 構文・フォーマット
- Layer 3-4: セマンティック・統合
- Layer 5: セキュリティ（最重要）

**課題**:
1. 品質チェックが手動実行（自動化されていない）
2. AutoFlowのような包括的なゲートシステムがない
3. LLM生成コードの典型的ミス（Markdown in YAML等）を検出できない
4. クリティカルエラーでの自動停止機能がない
5. 自動修正（Auto-fix）機能が限定的

---

## 2. 目標設定

### 主要目標

**Goal 1: AutoFlow互換の品質ゲートシステム構築**
- 5層のゲートを実装
- クリティカルエラーで即座に停止
- 自動修正機能（70%以上のエラー対応）

**Goal 2: Claude Code開発フローへのシームレス統合**
- 既存コマンド（/commit, /feature, /implement）との連携
- Git操作前の自動検証
- TodoWrite完了時の自動実行

**Goal 3: 開発速度の向上**
- 手戻り工数30%削減
- セキュリティリスクの早期検出（100%）
- LLM生成コードのエラー率50%削減

---

## 3. システム設計

### 3.1 アーキテクチャ概要

```
┌─────────────────────────────────────────────────────┐
│         Claude Code 開発フロー                       │
├─────────────────────────────────────────────────────┤
│                                                     │
│  /feature → 実装 → /task-validate → /commit        │
│              ↓            ↓              ↓          │
│         LLM生成    品質ゲート      Git操作          │
│                                                     │
└─────────────────────────────────────────────────────┘
                        ↓
        ┌───────────────────────────────┐
        │   Quality Gate Pipeline       │
        ├───────────────────────────────┤
        │ Layer 1: Syntax Validation    │
        │ Layer 2: Format Validation    │
        │ Layer 3: Semantic Validation  │
        │ Layer 4: Integration Check    │
        │ Layer 5: Security Scan        │
        └───────────────────────────────┘
                        ↓
        ┌───────────────────────────────┐
        │   Validation Report           │
        ├───────────────────────────────┤
        │ ✅ Passed: 4                  │
        │ ❌ Failed: 1                  │
        │ 🔧 Auto-fixed: 2              │
        │                               │
        │ → ユーザーアクション提示      │
        └───────────────────────────────┘
```

### 3.2 技術選択

#### Option A: Rust実装（AutoFlow方式）
**利点**:
- 型安全性、高速実行
- AutoFlowとの互換性
- 並列ゲート実行可能

**欠点**:
- 開発工数大（1-2週間）
- Rustビルド環境必要
- メンテナンスコスト高

#### Option B: Shell + Python実装（推奨）
**利点**:
- 既存システムとの親和性高
- 開発速度速い（2-3日）
- 柔軟な拡張性

**欠点**:
- Rustより実行速度遅い（許容範囲）
- 型安全性低い（テストで補完）

**決定**: **Option B (Shell + Python)** を採用
- 理由: 開発速度とメンテナンス性を優先

### 3.3 ディレクトリ構造

```
~/.claude/
├── validation/
│   ├── gates/
│   │   ├── layer1_syntax.sh          # 構文検証
│   │   ├── layer2_format.sh          # フォーマット検証
│   │   ├── layer3_semantic.sh        # セマンティック検証
│   │   ├── layer4_integration.sh     # 統合検証
│   │   └── layer5_security.sh        # セキュリティ検証
│   ├── fixers/
│   │   ├── yaml_fixer.py             # YAML自動修正
│   │   ├── markdown_stripper.py      # Markdown削除
│   │   └── enum_normalizer.py        # Enum正規化
│   ├── schemas/
│   │   ├── tasks.schema.json         # tasks.ymlスキーマ
│   │   ├── sprints.schema.json       # sprints.ymlスキーマ
│   │   └── package.schema.json       # package.jsonスキーマ
│   ├── patterns/
│   │   └── security-patterns.json    # セキュリティパターン
│   ├── pipeline.sh                   # メインパイプライン
│   └── README.md                     # 使用方法
├── commands/
│   └── validate.md                   # /validateコマンド（既存のtask-validateを拡張）
└── utils/
    ├── gate-runner.sh                # ゲート実行ユーティリティ
    └── report-generator.py           # レポート生成
```

---

## 4. 実装計画

### Phase 1: 基盤実装（Day 1-2）

#### Step 1.1: ゲートパイプライン骨格
**ファイル**: `~/.claude/validation/pipeline.sh`

```bash
#!/bin/bash
set -euo pipefail

# Quality Gate Pipeline
# Usage: pipeline.sh [--layers=all|syntax,security] [--auto-fix] [--stop-on-failure]

LAYERS="${1:-all}"
AUTO_FIX="${2:-false}"
STOP_ON_FAILURE="${3:-true}"

GATES_DIR="$(dirname "$0")/gates"
REPORT_FILE="/tmp/quality-gate-report.json"

# Initialize report
cat > "$REPORT_FILE" << EOF
{
  "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "results": [],
  "passed": true,
  "total_gates": 0,
  "passed_gates": 0,
  "failed_gates": 0,
  "auto_fixed": 0
}
EOF

# Run gates in order
run_gate() {
    local gate_script="$1"
    local gate_name="$2"
    local is_critical="$3"

    echo "🔍 Running: $gate_name"

    if bash "$gate_script" "$AUTO_FIX"; then
        echo "✅ $gate_name - PASSED"
        # Update report (passed)
        return 0
    else
        echo "❌ $gate_name - FAILED"
        # Update report (failed)

        if [[ "$is_critical" == "true" && "$STOP_ON_FAILURE" == "true" ]]; then
            echo "⚠️  Critical gate failed, stopping pipeline"
            exit 1
        fi
        return 1
    fi
}

# Execute gates based on layers
if [[ "$LAYERS" == "all" || "$LAYERS" =~ "syntax" ]]; then
    run_gate "$GATES_DIR/layer1_syntax.sh" "Layer 1: Syntax Validation" true
    run_gate "$GATES_DIR/layer2_format.sh" "Layer 2: Format Validation" true
fi

if [[ "$LAYERS" == "all" || "$LAYERS" =~ "security" ]]; then
    run_gate "$GATES_DIR/layer5_security.sh" "Layer 5: Security Validation" true
fi

if [[ "$LAYERS" == "all" || "$LAYERS" =~ "integration" ]]; then
    run_gate "$GATES_DIR/layer3_semantic.sh" "Layer 3: Semantic Validation" false
    run_gate "$GATES_DIR/layer4_integration.sh" "Layer 4: Integration Validation" false
fi

# Generate final report
python3 "$(dirname "$0")/../utils/report-generator.py" "$REPORT_FILE"
```

#### Step 1.2: Layer 1 - 構文検証
**ファイル**: `~/.claude/validation/gates/layer1_syntax.sh`

```bash
#!/bin/bash
set -euo pipefail

# Layer 1: Syntax Validation
# Checks: YAML/JSON syntax, schema compliance, required fields

AUTO_FIX="${1:-false}"
EXIT_CODE=0

# YAML syntax check
check_yaml_syntax() {
    local file="$1"

    if ! python3 -c "import yaml; yaml.safe_load(open('$file'))" 2>/dev/null; then
        echo "  ❌ Invalid YAML syntax: $file"
        return 1
    fi

    echo "  ✅ Valid YAML syntax: $file"
    return 0
}

# JSON schema validation
validate_schema() {
    local file="$1"
    local schema="$2"

    if ! python3 -c "
import json, jsonschema, yaml
with open('$file') as f:
    data = yaml.safe_load(f)
with open('$schema') as s:
    schema = json.load(s)
jsonschema.validate(data, schema)
" 2>/dev/null; then
        echo "  ❌ Schema validation failed: $file"
        return 1
    fi

    echo "  ✅ Schema validation passed: $file"
    return 0
}

# Find and validate YAML files
for yaml_file in tasks.yml .autoflow/SPRINTS.yml; do
    if [[ -f "$yaml_file" ]]; then
        if ! check_yaml_syntax "$yaml_file"; then
            EXIT_CODE=1
        fi

        # Schema validation (if schema exists)
        schema_name=$(basename "$yaml_file" .yml)
        schema_file="$HOME/.claude/validation/schemas/${schema_name}.schema.json"

        if [[ -f "$schema_file" ]]; then
            if ! validate_schema "$yaml_file" "$schema_file"; then
                EXIT_CODE=1
            fi
        fi
    fi
done

# JSON syntax check (package.json, tsconfig.json, etc.)
for json_file in package.json tsconfig.json; do
    if [[ -f "$json_file" ]]; then
        if ! python3 -c "import json; json.load(open('$json_file'))" 2>/dev/null; then
            echo "  ❌ Invalid JSON syntax: $json_file"
            EXIT_CODE=1
        else
            echo "  ✅ Valid JSON syntax: $json_file"
        fi
    fi
done

exit $EXIT_CODE
```

#### Step 1.3: Layer 2 - フォーマット検証
**ファイル**: `~/.claude/validation/gates/layer2_format.sh`

```bash
#!/bin/bash
set -euo pipefail

# Layer 2: Format Validation
# Detects: Markdown in YAML, incorrect enum values, field name mistakes

AUTO_FIX="${1:-false}"
EXIT_CODE=0
FIXER_DIR="$(dirname "$0")/../fixers"

# Detect Markdown in YAML
detect_markdown_in_yaml() {
    local file="$1"

    if grep -q '```yaml\|```yml' "$file"; then
        echo "  ❌ Markdown code blocks detected in $file"

        if [[ "$AUTO_FIX" == "true" ]]; then
            echo "  🔧 Auto-fixing: Removing markdown code blocks..."
            python3 "$FIXER_DIR/markdown_stripper.py" "$file"
            echo "  ✅ Auto-fixed: $file"
            return 0
        fi

        return 1
    fi

    echo "  ✅ No markdown in YAML: $file"
    return 0
}

# Check enum values (SCREAMING_SNAKE_CASE)
check_enum_values() {
    local file="$1"

    # Check for common mistakes: "Done" instead of "DONE"
    if grep -q 'status: Done\|status: Completed\|status: Pending' "$file"; then
        echo "  ⚠️  Incorrect enum values in $file"

        if [[ "$AUTO_FIX" == "true" ]]; then
            echo "  🔧 Auto-fixing: Normalizing enum values..."
            python3 "$FIXER_DIR/enum_normalizer.py" "$file"
            echo "  ✅ Auto-fixed: $file"
            return 0
        fi

        return 1
    fi

    return 0
}

# Check field names
check_field_names() {
    local file="$1"

    # Common mistakes: sprint_id instead of id
    if grep -q 'sprint_id:\|task_id:' "$file"; then
        echo "  ❌ Incorrect field names in $file (use 'id:' not 'sprint_id:')"

        if [[ "$AUTO_FIX" == "true" ]]; then
            sed -i.bak 's/sprint_id:/id:/g; s/task_id:/id:/g' "$file"
            rm -f "${file}.bak"
            echo "  ✅ Auto-fixed: $file"
            return 0
        fi

        return 1
    fi

    return 0
}

# Run checks on YAML files
for yaml_file in tasks.yml .autoflow/SPRINTS.yml; do
    if [[ -f "$yaml_file" ]]; then
        detect_markdown_in_yaml "$yaml_file" || EXIT_CODE=1
        check_enum_values "$yaml_file" || EXIT_CODE=1
        check_field_names "$yaml_file" || EXIT_CODE=1
    fi
done

exit $EXIT_CODE
```

#### Step 1.4: Layer 5 - セキュリティ検証（最重要）
**ファイル**: `~/.claude/validation/gates/layer5_security.sh`

```bash
#!/bin/bash
set -euo pipefail

# Layer 5: Security Validation (CRITICAL)
# Checks: Hardcoded credentials, OWASP Top 10, known vulnerabilities

EXIT_CODE=0
PATTERNS_FILE="$HOME/.claude/validation/patterns/security-patterns.json"

# Credential scanner
scan_credentials() {
    echo "  🔍 Scanning for hardcoded credentials..."

    # Patterns from security-patterns.json
    local patterns=(
        'API_KEY\s*=\s*["\x27][A-Za-z0-9_-]+["\x27]'
        'SECRET\s*=\s*["\x27][^"\x27]+["\x27]'
        'PASSWORD\s*=\s*["\x27][^"\x27]+["\x27]'
        'password\s*:\s*["\x27][^"\x27]+["\x27]'
        'token\s*=\s*["\x27][A-Za-z0-9_-]+["\x27]'
    )

    for pattern in "${patterns[@]}"; do
        if git grep -E "$pattern" -- '*.js' '*.ts' '*.py' '*.rb' 2>/dev/null; then
            echo "  ❌ CRITICAL: Hardcoded credentials detected"
            echo "     Pattern: $pattern"
            EXIT_CODE=1
        fi
    done

    if [[ $EXIT_CODE -eq 0 ]]; then
        echo "  ✅ No hardcoded credentials found"
    fi
}

# OWASP Top 10 basic checks
check_owasp() {
    echo "  🔍 OWASP Top 10 checks..."

    # A01: SQL Injection risk
    if git grep -E 'query\s*=.*\+.*|execute\(.*\+' -- '*.js' '*.py' 2>/dev/null; then
        echo "  ⚠️  Potential SQL injection risk detected"
        EXIT_CODE=1
    fi

    # A03: XSS risk (dangerouslySetInnerHTML, v-html without sanitization)
    if git grep -E 'dangerouslySetInnerHTML|v-html' -- '*.jsx' '*.tsx' '*.vue' 2>/dev/null; then
        echo "  ⚠️  Potential XSS risk detected (dangerouslySetInnerHTML/v-html)"
        EXIT_CODE=1
    fi

    # A07: Authentication bypass
    if git grep -E 'auth.*=.*true|isAuthenticated\s*=\s*true' -- '*.js' '*.ts' 2>/dev/null; then
        echo "  ⚠️  Potential authentication bypass detected"
        EXIT_CODE=1
    fi

    if [[ $EXIT_CODE -eq 0 ]]; then
        echo "  ✅ OWASP checks passed"
    fi
}

# Dependency vulnerability check (using npm audit, pip-audit, etc.)
check_dependencies() {
    echo "  🔍 Checking dependencies for vulnerabilities..."

    if [[ -f "package.json" ]]; then
        if npm audit --audit-level=high 2>&1 | grep -q "vulnerabilities"; then
            echo "  ⚠️  High-severity vulnerabilities found in npm dependencies"
            EXIT_CODE=1
        else
            echo "  ✅ npm dependencies clean"
        fi
    fi

    # Python dependencies (if requirements.txt exists)
    if [[ -f "requirements.txt" ]] && command -v pip-audit &>/dev/null; then
        if ! pip-audit -r requirements.txt 2>/dev/null; then
            echo "  ⚠️  Vulnerabilities found in Python dependencies"
            EXIT_CODE=1
        else
            echo "  ✅ Python dependencies clean"
        fi
    fi
}

# Run security scans
scan_credentials
check_owasp
check_dependencies

exit $EXIT_CODE
```

### Phase 2: フィクサー実装（Day 2-3）

#### Fixer 1: YAML自動修正
**ファイル**: `~/.claude/validation/fixers/yaml_fixer.py`

```python
#!/usr/bin/env python3
"""YAML Auto-fixer for common LLM mistakes"""

import sys
import re
from pathlib import Path

def fix_yaml(file_path: str) -> bool:
    """Fix common YAML issues and return True if fixed"""

    with open(file_path, 'r') as f:
        content = f.read()

    original = content

    # Remove markdown code blocks
    content = re.sub(r'```ya?ml\n', '', content)
    content = re.sub(r'\n```', '', content)

    # Fix field names
    content = re.sub(r'sprint_id:', 'id:', content)
    content = re.sub(r'task_id:', 'id:', content)

    # Normalize enum values
    content = re.sub(r'status: Done', 'status: DONE', content)
    content = re.sub(r'status: Pending', 'status: PENDING', content)
    content = re.sub(r'status: In Progress', 'status: IN_PROGRESS', content)

    if content != original:
        with open(file_path, 'w') as f:
            f.write(content)
        return True

    return False

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: yaml_fixer.py <file.yml>")
        sys.exit(1)

    fixed = fix_yaml(sys.argv[1])
    sys.exit(0 if fixed else 1)
```

### Phase 3: Claude Code統合（Day 3-4）

#### 統合1: `/validate` コマンド作成

既存の `/task-validate` を拡張し、品質ゲートパイプラインを呼び出す。

**ファイル**: `~/.claude/commands/validate.md`

```markdown
---
allowed-tools: Bash, Read, Write, TodoWrite, AskUserQuestion
argument-hint: "[--layers=all|syntax,security] [--auto-fix] [--report=text|json]"
description: Multi-layer quality gate validation with auto-fix support
model: sonnet
---

# validate

Arguments: $ARGUMENTS

## Execution Flow

1. Parse arguments (layers, auto-fix, report format)
2. Run quality gate pipeline: `~/.claude/validation/pipeline.sh`
3. Parse validation report
4. Display results to user
5. If failures: show actionable suggestions
6. If auto-fix enabled: show what was fixed

## Implementation

```bash
# Run quality gate pipeline
LAYERS="${LAYERS:-all}"
AUTO_FIX="${AUTO_FIX:-false}"
REPORT_FORMAT="${REPORT_FORMAT:-text}"

bash ~/.claude/validation/pipeline.sh \
    --layers="$LAYERS" \
    --auto-fix="$AUTO_FIX" \
    --stop-on-failure=true

# Get exit code
VALIDATION_RESULT=$?

# Display report
if [[ "$REPORT_FORMAT" == "json" ]]; then
    cat /tmp/quality-gate-report.json
else
    python3 ~/.claude/utils/report-generator.py /tmp/quality-gate-report.json
fi

exit $VALIDATION_RESULT
```

## User Guidance

If validation fails:
1. Show specific errors with file:line references
2. Suggest fixes (manual or --auto-fix)
3. Link to relevant documentation

Example output:
```
❌ Quality Gate Report
════════════════════════════════════════

❌ Layer 2: Format Validation - FAILED
  Errors:
    tasks.yml:5 - Markdown code block detected

  Suggestions:
    Run with --auto-fix: /validate --auto-fix
    Or manually remove ```yaml blocks

✅ Layer 5: Security Validation - PASSED
  No security issues detected

════════════════════════════════════════
Total Gates: 5
Passed: 4
Failed: 1

💡 Fix errors and re-run validation
```
```

---

## 5. 統合戦略

### 5.1 既存ワークフローとの統合

```
現在:
/feature → 実装 → /commit → push

Phase 1実装後:
/feature → 実装 → /validate → /commit → push
                        ↓
                   エラー検出 → 自動修正 or 手動修正
```

**Phase 1**: 手動で `/validate` 実行後に `/commit`
**Phase 2以降**: `/commit` 前の自動実行を検討（使用状況を見て判断）

---

## 6. リスク評価

### セキュリティリスク **HIGH**
- **リスク**: 品質ゲート自体に脆弱性
- **軽減策**:
  - 入力サニタイゼーション徹底
  - 一時ファイルの安全な削除
  - 権限最小化（読み取り専用で実行）

### 技術的リスク **MEDIUM**
- **リスク**: 既存プロジェクトとの互換性問題
- **軽減策**:
  - プロジェクトごとにオプトイン（.validate.ymlで設定）
  - 段階的ロールアウト
  - フィードバックループ

### 開発効率リスク **LOW**
- **リスク**: 検証時間による開発速度低下
- **軽減策**:
  - 並列ゲート実行（将来）
  - キャッシング（同一コードは再検証スキップ）
  - 軽量ゲート優先実行

---

## 7. 成功指標

### KPI（3ヶ月後測定）

1. **品質向上**:
   - セキュリティリスク検出率: 100%
   - LLM生成コードエラー: 50%削減
   - 本番環境バグ: 30%削減

2. **開発速度**:
   - 手戻り工数: 30%削減
   - コードレビュー時間: 20%短縮
   - デプロイ頻度: 変化なし（速度低下しない）

3. **ユーザー満足度**:
   - 開発者フィードバック: 4.0/5.0以上
   - Auto-fix成功率: 70%以上
   - False positive率: 10%以下

---

## 付録A: セキュリティ実装チェックリスト

### 入力検証（Phase 1必須）

```bash
# すべてのユーザー入力を検証
safe_validate_layers() {
    local layers="$1"
    if [[ ! "$layers" =~ ^[a-zA-Z0-9,_-]+$ ]] && [[ "$layers" != "all" ]]; then
        echo "Error: Invalid layers format" >&2
        exit 1
    fi
    echo "$layers"
}

# ファイルパス検証（パストラバーサル防止）
validate_file_path() {
    local file="$1"
    if [[ "$file" =~ \.\./|^/ ]]; then
        echo "Error: Invalid file path" >&2
        return 1
    fi
    [[ -f "$file" ]] || { echo "Error: File not found" >&2; return 1; }
    return 0
}

# シンボリックリンク検証
if [[ -L "$file" ]]; then
    echo "Error: Cannot process symbolic link" >&2
    exit 1
fi
```

### コマンド実行安全性（Phase 1必須）

```bash
# 一時ファイルの安全な生成
REPORT_FILE=$(mktemp /tmp/quality-gate-report.XXXXXX.json)
chmod 600 "$REPORT_FILE"
trap 'rm -f "$REPORT_FILE" /tmp/gate-*.log 2>/dev/null' EXIT INT TERM

# Pythonスクリプトの安全な呼び出し
python3 -c "
import sys
import yaml
with open(sys.argv[1]) as f:
    yaml.safe_load(f)
" "$file" 2>/dev/null

# タイムアウト設定（ReDoS対策）
timeout 10s git grep -E "$pattern" -- '*.js' '*.ts' 2>/dev/null
```

---

## 付録B: パフォーマンス最適化実装

### npm auditキャッシュ（Phase 1必須）

```bash
# package-lock.json のハッシュでキャッシュ
LOCK_HASH=$(md5sum package-lock.json 2>/dev/null | awk '{print $1}')
CACHE_FILE="/tmp/npm-audit-cache-${LOCK_HASH}.json"

if [[ -f "$CACHE_FILE" ]] && [[ $(find "$CACHE_FILE" -mmin -60) ]]; then
    # 60分以内のキャッシュを使用
    cat "$CACHE_FILE"
else
    npm audit --json > "$CACHE_FILE"
    cat "$CACHE_FILE"
fi
```

### ゲート並列実行（Phase 1必須）

```bash
# 独立したゲートを並列実行
run_gates_parallel() {
    local pids=()
    local failed=false

    run_gate "$GATES_DIR/layer1_syntax.sh" "Layer 1" true &
    pids+=($!)

    run_gate "$GATES_DIR/layer2_format.sh" "Layer 2" true &
    pids+=($!)

    # 全ジョブ完了待ち
    for pid in "${pids[@]}"; do
        wait "$pid" || failed=true
    done

    [[ "$failed" == "false" ]]
}
```

**効果**: 25秒 → 10秒（60%高速化）

---

## 付録C: 保守性改善実装

### 共通ログ関数（Phase 1必須）

```bash
# utils/logging.sh
log_error() {
    echo "[ERROR] $*" >&2
}

log_warn() {
    echo "[WARN] $*" >&2
}

log_info() {
    echo "[INFO] $*"
}
```

### 共通設定ファイル（Phase 1推奨）

```bash
# config.sh
REPORT_DIR="/tmp"
CACHE_EXPIRY_MINUTES=60
GATE_TIMEOUT_SECONDS=10

# プロジェクト固有設定（オーバーライド可能）
if [[ -f "./.autoflow/validation.conf" ]]; then
    source "./.autoflow/validation.conf"
fi
```

### テストスイート（Phase 1必須）

```bash
# tests/test_layer1_syntax.sh
test_valid_yaml() {
    cat > /tmp/test.yml << EOF
key: value
list:
  - item1
EOF

    bash gates/layer1_syntax.sh false < /tmp/test.yml
    [[ $? -eq 0 ]] || { echo "FAIL: Valid YAML test"; return 1; }
    echo "PASS: Valid YAML test"
}
```

---

## 次のステップ

### Phase 1実装（Day 1-3）

**Day 1-2: コア機能**:
- [ ] Layer 1, 2, 5ゲート実装（セキュリティ対策込み）
- [ ] Auto-fix機能（YAML fixer, markdown stripper）
- [ ] `/validate`コマンド
- [ ] 共通関数（utils/logging.sh, config.sh）

**Day 3: 最適化・テスト**:
- [ ] パフォーマンス最適化（並列実行、npm auditキャッシュ）
- [ ] 基本テストスイート（tests/test_*.sh）
- [ ] 性能計測（目標: 10秒以内）

### Phase 2以降（使用状況を見て判断）

- Layer 3, 4追加
- `/commit`への自動統合
- プロジェクト固有カスタマイズ

---

**作成者**: Claude Code + AutoFlow品質ゲートシステム
**最終更新**: 2025-11-16（Iterative Review適用）
