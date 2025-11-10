---
allowed-tools: Read, Write, Edit, Bash, AskUserQuestion, TodoWrite, Grep, Glob
argument-hint: [action] [description] | add | complete | list | sync | project | interactive
description: インテリジェント開発統合todo管理システム（Git連携・対話的UI対応）
model: sonnet
---

# インテリジェント開発統合Todo Manager

Git連携・対話的UI対応の高度なタスク管理: **$ARGUMENTS**

## 🚀 クイックスタート

```bash
# 基本操作（実装済み）
/todo                           # インタラクティブモード
/todo add "Fix bug"             # タスク追加
/todo list                      # タスク一覧表示
/todo complete 1                # タスク完了（エイリアス: done）

# 優先度・コンテキスト指定
/todo add "Fix auth timeout" --priority high --context api

# 日付指定（ISO 8601形式）
/todo add "Update docs" --due 2025-01-15
/todo add "Review PR" --due tomorrow

# フィルタリング・ソート
/todo list --filter priority:high
/todo list --sort due
```

---

## 📋 実装済み機能

### 基本コマンド

#### `add "description" [options]`
タスクを新規作成します。

**オプション**:
- `--priority <level>`: 優先度（critical|high|medium|low）
- `--context <type>`: コンテキスト（ui|api|docs|test|build|security）
- `--due <date>`: 期限（YYYY-MM-DD または tomorrow, next week 等）

**例**:
```bash
/todo add "Fix authentication timeout" --priority high --context api
/todo add "Update documentation" --due 2025-01-20
/todo add "Refactor component" --priority medium --context ui --due next week
```

#### `complete N` / `done N`
タスクを完了します（エイリアス: `complete`, `done`）。

**例**:
```bash
/todo complete 1
/todo done 3
```

#### `list [options]`
タスク一覧を表示します。

**オプション**:
- `--filter <condition>`: フィルタリング（例: `priority:high`, `context:ui`）
- `--sort <field>`: ソート（`due`, `priority`）

**例**:
```bash
/todo list                      # 全タスク表示
/todo list --filter priority:high
/todo list --sort due
```

#### その他のコマンド
- `remove N` / `delete N` - タスク削除
- `undo N` - 完了タスクを未完了に戻す
- `past due` - 期限切れタスクの表示
- `next` - 次の優先タスクの表示（期限・優先度考慮）

---

## 🔮 実験的機能（Phase 2 - 未実装）

⚠️ **注意**: 以下の機能は現在開発中で、まだ利用できません。

### Git統合機能（未実装）
- `sync --git` - Git状態との双方向同期
- `branch [branch-name]` - ブランチ関連タスク管理
- `project --overview | --stats` - プロジェクト分析

### コマンド統合（未実装）
- `integrate --debug [issue]` - `/debug`コマンドとの連携
- `integrate --commit [message]` - `/commit`コマンドとの連携
- `integrate --serena [problem]` - `/serena`コマンドとの連携

### 分析機能（未実装）
- `analyze --productivity` - 完了パターン分析
- `dashboard` - リッチ表示ダッシュボード
- `suggest --next` - 次のタスク推奨

---

## 🛠️ 実装ガイド（開発者向け）

### Current Project Context (Git Integration)

**セキュリティ強化版**:
```bash
# Git操作のキャッシング（パフォーマンス最適化）
if [[ -z "$GIT_CONTEXT_CACHED" ]]; then
    export GIT_STATUS=$(git status --porcelain 2>/dev/null | head -5 || echo "No git repo")
    export GIT_BRANCH=$(git branch --show-current 2>/dev/null || echo "No git branch")
    export GIT_COMMITS=$(git log --oneline -3 2>/dev/null || echo "No commit history")
    export GIT_CONTEXT_CACHED=1
fi

# プロジェクトルート検出（最適化版・セキュリティ強化）
detect_project_root() {
    # 段階的検索（早期終了最適化）
    for depth in 1 2 3; do
        result=$(find . -P -maxdepth $depth \( -name "package.json" -o -name "Cargo.toml" -o -name "requirements.txt" \) -type f 2>/dev/null | head -1)
        if [[ -n "$result" ]]; then
            dirname "$result"
            return 0
        fi
    done
    pwd
}

PROJECT_ROOT=$(detect_project_root)

# todos.md パス検証（パストラバーサル対策）
validate_todos_path() {
    local todos_file="$1"

    # ファイル存在確認
    if [[ ! -f "$todos_file" ]]; then
        return 1
    fi

    # パストラバーサルチェック
    local real_path=$(realpath "$todos_file" 2>/dev/null)
    if [[ "$real_path" != "$PWD"* ]]; then
        echo "❌ Security Error: Path traversal detected in todos.md path" >&2
        exit $EXIT_SECURITY_ERROR
    fi

    # ファイルサイズ制限（10MB）
    local file_size
    if command -v stat >/dev/null 2>&1; then
        file_size=$(stat -f%z "$todos_file" 2>/dev/null || stat -c%s "$todos_file" 2>/dev/null)
        if [[ $file_size -gt 10485760 ]]; then
            echo "❌ Error: todos.md exceeds 10MB limit" >&2
            exit $EXIT_FILE_TOO_LARGE
        fi
    fi

    return 0
}
```

### Interactive Mode (引数なしの場合)

**AskUserQuestion統合による対話的操作**:

> **注**: 以下は Claude Code の `AskUserQuestion` ツールを使用した擬似コードです。

```typescript
// Primary Action Selection
AskUserQuestion({
  questions: [{
    question: "TODO管理で何をしますか？",
    header: "アクション選択",
    multiSelect: false,
    options: [
      { label: "add-task", description: "🎯 新しいタスクを作成（優先度・ラベル設定）" },
      { label: "review-list", description: "📋 現在のタスクリストを確認・管理" },
      { label: "quick-complete", description: "✅ タスクの高速完了処理" },
      { label: "git-sync", description: "🔄 Git状態との同期・ブランチ連携（未実装）" },
      { label: "analyze", description: "📊 生産性・進捗の分析表示（未実装）" },
      { label: "dashboard", description: "🎨 リッチ表示ダッシュボード（未実装）" }
    ]
  }]
})

// Task Creation Dialog (add-task 選択時)
AskUserQuestion({
  questions: [{
    question: "タスクの優先度を選択してください",
    header: "優先度",
    multiSelect: false,
    options: [
      { label: "critical", description: "🔴 Critical: 本番障害・緊急対応" },
      { label: "high", description: "🟡 High: 重要機能・期限あり" },
      { label: "medium", description: "🟢 Medium: 通常開発・改善" },
      { label: "low", description: "🔵 Low: 最適化・調査・将来対応" }
    ]
  }, {
    question: "タスクのコンテキスト（分野）を選択してください",
    header: "コンテキスト",
    multiSelect: false,
    options: [
      { label: "ui", description: "🎨 UI/UX: フロントエンド・デザイン" },
      { label: "api", description: "⚙️ API: バックエンド・サーバーサイド" },
      { label: "docs", description: "📝 Docs: ドキュメント・コメント" },
      { label: "test", description: "🧪 Test: テスト・品質保証" },
      { label: "build", description: "🔧 Build: ビルド・CI/CD・インフラ" },
      { label: "security", description: "🔒 Security: セキュリティ・認証" }
    ]
  }]
})
```

### TodoWrite Integration

**すべての操作でタスク管理を体系化**:
1. プロジェクト状態の確認と分析
2. ユーザー要求の解析と実行計画
3. TODO操作の実行と検証
4. 結果の確認と次のアクション提案

### Git Integration & Context Detection

**プロジェクト認識による自動コンテキスト設定**:

プロジェクトファイル（package.json, Cargo.toml, requirements.txt等）を検出し、適切なコンテキストタグとタスク提案を自動生成。ブランチパターン（feature/, fix/, refactor/等）を分析し、関連タスクを推奨。

---

## 📝 Todo Format

**todos.md フォーマット** (ISO 8601 日付形式):

```markdown
- [ ] Task description | Priority: high|medium|low | Context: ui|api|test|docs|build | Due: YYYY-MM-DD
```

**例**:
```markdown
- [ ] Fix authentication timeout | Priority: high | Context: api | Due: 2025-01-15
- [ ] Update documentation | Priority: medium | Context: docs | Due: 2025-01-20
- [x] Refactor TaskCard component | Priority: low | Context: ui | Due: 2025-01-10
```

---

## 🔒 セキュリティガイドライン

### コマンドインジェクション対策

```bash
# 引数のサニタイズ（必須）
sanitize_arguments() {
    local raw_args="$1"
    # 危険な文字を除去: ; & | ` $ ( ) < > \
    printf '%s' "$raw_args" | sed 's/[;&|`$()<>\\]//g'
}

SANITIZED_ARGS=$(sanitize_arguments "$ARGUMENTS")
```

### パストラバーサル対策

```bash
# ファイルパス検証（必須）
validate_file_path() {
    local file_path="$1"
    local real_path

    # realpath で絶対パス取得
    real_path=$(realpath "$file_path" 2>/dev/null)

    # 現在のディレクトリ配下かチェック
    if [[ "$real_path" != "$PWD"* ]]; then
        echo "❌ Security Error: Path traversal detected" >&2
        return 1
    fi

    return 0
}
```

### Git操作の安全性

- `.git` ディレクトリへの直接操作を禁止
- Git hookの実行は慎重に検証
- Git コマンドは常に `2>/dev/null` でエラーを抑制

---

## ⚠️ Error Handling

### エラーコードの標準化

```bash
# エラーコード定義
readonly EXIT_SUCCESS=0
readonly EXIT_NO_PERMISSION=1
readonly EXIT_NOT_GIT_REPO=2
readonly EXIT_INVALID_ARGS=3
readonly EXIT_FILE_NOT_FOUND=4
readonly EXIT_SECURITY_ERROR=5
readonly EXIT_FILE_TOO_LARGE=6
```

### エラーハンドリング実装例

```bash
# ファイル操作エラー
if [ ! -w . ]; then
  echo "❌ Error: No write permission in current directory" >&2
  echo "💡 Solution: Check directory permissions or switch to project root" >&2
  exit $EXIT_NO_PERMISSION
fi

# Git リポジトリ検証
if ! git rev-parse --git-dir >/dev/null 2>&1; then
  echo "⚠️ Warning: Not a git repository" >&2
  echo "📝 Note: Git integration features will be limited" >&2
  # 継続可能なので exit しない
fi

# プロジェクト認識エラー
if [ ! -f package.json ] && [ ! -f Cargo.toml ] && [ ! -f requirements.txt ]; then
  echo "🔍 Info: Unknown project type, using generic context options" >&2
fi

# 引数検証エラー
if [[ -z "$SANITIZED_ARGS" ]]; then
  echo "❌ Error: Invalid arguments provided" >&2
  echo "💡 Usage: /todo add \"description\" [--priority high] [--context api]" >&2
  exit $EXIT_INVALID_ARGS
fi
```

---

## 📅 Date/Time Processing

**日付フォーマット**（ISO 8601標準）:
- **標準フォーマット**: `YYYY-MM-DD` (例: `2025-01-15`)
- **表示フォーマット**: `MM/DD/YYYY` (ローカライズ対応時)

**自然言語対応**:
- `tomorrow` - 翌日
- `next week` - 1週間後
- `in 3 days` - 3日後

**実装例**:
```bash
parse_natural_language_date() {
    local input="$1"
    local result

    case "$input" in
        tomorrow)
            result=$(date -v+1d +%Y-%m-%d 2>/dev/null || date -d "tomorrow" +%Y-%m-%d 2>/dev/null)
            ;;
        "next week")
            result=$(date -v+7d +%Y-%m-%d 2>/dev/null || date -d "7 days" +%Y-%m-%d 2>/dev/null)
            ;;
        "in "*)
            days="${input#in }"
            days="${days% days}"
            days="${days% day}"
            result=$(date -v+${days}d +%Y-%m-%d 2>/dev/null || date -d "${days} days" +%Y-%m-%d 2>/dev/null)
            ;;
        *)
            # ISO 8601形式をそのまま使用
            result="$input"
            ;;
    esac

    echo "$result"
}
```

---

## 🎯 Core Behavior

- **優先度順・期限順での自動ソート**
- **Git連携**（ブランチ・コミット状態の自動更新）※Phase 2
- **プロジェクト認識による自動コンテキスト判定**※Phase 2

---

## 💡 Smart Suggestions（Phase 2 - 未実装）

⚠️ 以下の機能は開発中です。

- 関連コマンド提案（/commit, /debug等）
- ワークフロー統合
- 生産性改善提案

---

## 📚 コマンド仕様統一表

| コマンド | エイリアス | 引数形式 | 例 |
|---------|----------|---------|---|
| `add` | - | `"description" [options]` | `/todo add "Fix bug" --priority high` |
| `complete` | `done` | `N` | `/todo complete 1` |
| `list` | - | `[options]` | `/todo list --filter priority:high` |
| `remove` | `delete` | `N` | `/todo remove 3` |
| `undo` | - | `N` | `/todo undo 2` |

**オプション形式の統一**:
- フラグ: `--priority high`, `--context ui`, `--due 2025-01-15`
- フィルタ: `--filter priority:high`, `--filter context:api`
- ソート: `--sort due`, `--sort priority`

---

## 🔧 実装状況

### ✅ 実装済み（Phase 1）
- [x] 基本CRUD操作（add, complete, list, remove）
- [x] 優先度・コンテキスト管理
- [x] 日付処理（ISO 8601）
- [x] インタラクティブモード
- [x] エラーハンドリング
- [x] セキュリティ対策（コマンドインジェクション、パストラバーサル）

### 🚧 開発中（Phase 2）
- [ ] Git統合（sync, branch, project）
- [ ] コマンド統合（debug, commit, serena）
- [ ] 分析機能（analyze, dashboard, suggest）
- [ ] 完了パターン分析
- [ ] ボトルネック検出

---

## 📖 参考リンク

- **ISO 8601 日付形式**: https://en.wikipedia.org/wiki/ISO_8601
- **Git Best Practices**: https://git-scm.com/book/en/v2
- **Bash Security**: https://mywiki.wooledge.org/BashGuide
