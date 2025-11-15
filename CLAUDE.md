# Claude Code 設定

> **このファイルについて**: LLM向けに最適化された設定ファイル。編集時もLLM最適化を維持すること。ユーザー向け情報は `~/.claude/USER_GUIDE.md` に記載。

## 基本開発フロー {#basic-dev-flow}

### 1. 要件分析・計画
1. タスク受領 → 要件明確化質問
2. 要件確認 → AskUserQuestionで選択肢提示
3. 影響範囲分析 → 依存関係ファイル確認
4. 実装計画立案 → TodoWrite活用

### 2. 段階的実装
1. 小タスク分割 → 優先順位付け
2. 順次実装 → 逐次テスト・エラー修正
3. 都度確認 → ユーザーフィードバック
4. 最終統合 → 全体テスト・品質確認

**ドキュメント駆動実装（tasks.yml使用時）**:
- 実装前に参照ドキュメントを必ずRead（設計書、API仕様等）
- ドキュメントの要件・制約に厳密に従う
- acceptance_criteriaを実装完了の判断基準とする

**TDD原則（テストが必要な場合）**:
- Red: テストを先に書く（失敗を確認）
- Green: 最小限の実装でテストを通す
- Refactor: 重複排除、設計改善

#### 実装フェーズのデフォルト動作原則
以下の原則を実装フェーズでは常に適用：

**並列実行の最大化**:
- 独立タスク = ファイル依存関係なし、実行順序関係なし
- 例外: Edit後のRead、Write後のBash実行は順次実行
- 判定迷い時 = 安全側で順次実行
- 複数ファイル読み取り、独立した検索・分析は同時処理

**Subagent活用の効率化**:
- 複雑な探索・検索はTask tool（subagent_type=Explore）に委譲
- Agent完了時は結果を1-2文で要約し、次アクション明示
- 例: "3ファイルでエラー検出。修正が必要なのは auth.ts のみ"
- 報告が長文の場合は要点3つ以内に絞る
- 並列実行可能なagentは同時起動

**Subagent起動の品質確保**:

**起動時prompt必須要素**:
- 作業ディレクトリ: `[絶対パス]`
- 期待する成果:
  - `subagent_type=Explore`: ファイルパス・行番号を含む検索結果
  - その他: 変更対象ファイルの明示
- 失敗報告: `ERROR: [理由]` で開始

**完了時検証フロー**:
```
IF agent出力に "ERROR:" 含む:
    作業停止 → ユーザー報告 → 再実行判断

ELIF subagent_type == "Explore":
    IF 出力に正規表現 `[^:]+:\d+` マッチあり:
        成功 → 次タスク続行
    ELSE:
        Grep/Glob直接実行に切替

ELSE:
    IF 期待ファイルが実在:
        成功 → 次タスク続行
    ELSE:
        検証失敗 → ユーザー報告
```

**検証コマンド**: `ls -la [パス] 2>/dev/null || echo "FAIL"`

**実装進捗の可視化**:
- 3ステップ以上のタスクは必ずTodoWrite使用
- 各ステップ完了時に即座に status 更新
- コードコメントやBash echoでの説明禁止、直接出力のみ

**ルール適用の一貫性**:
- 他者に指摘したルール・ガイドラインを自分の出力にも適用
- ダブルスタンダード禁止

### 3. 品質確認（技術スタック別）
- **型安全言語**: 型エラー0件・型推論活用・strictモード
- **動的言語**: リンター・フォーマッター・テストカバレッジ
- **セキュリティ**: OWASP対応・入力検証・出力エスケープ
- **テスト**: 新機能カバレッジ・既存機能影響確認

#### 5層品質ゲートシステム {#quality-gates}

**多層検証による段階的品質保証**:

**Layer 1-2: 構文・フォーマット (syntax)**
- TypeScript型チェック (`npx tsc --noEmit`)
- ESLint (`npx eslint . --ext .ts,.tsx`)
- Prettier (`npx prettier --check`)
- 自動修正: `--auto-fix` フラグで対応

**Layer 5: セキュリティ (security)** - **最重要**
- .env変更検出 (`~/.claude/validation/check-env-changes.sh`)
- 認証情報パターンスキャン (API_KEY, SECRET, TOKEN等)
- OWASP Top 10チェックリスト
- パターン辞書: `~/.claude/validation/security-patterns.json`

**Layer 3-4: セマンティック・統合 (integration)**
- テストカバレッジ (`npm test -- --coverage`)
- API型整合性チェック（フロント/バックエンド）

**実行コマンド**:
- `/task-validate --layers=security` - セキュリティ検証のみ
- `/task-validate --layers=syntax --auto-fix` - 構文チェック+自動修正
- `/task-validate --layers=all --report=json` - 全層検証+JSON出力
- `/task-validate --layers=security,syntax` - 複数層指定

### 4. タスク完了・クリーンアップ

#### プロセス起動時の自動分類（Bash run_in_background=true 実行直後）

**判定ロジック（command文字列に対する正規表現マッチング）**:

```python
# 1. クリーンアップ対象パターン（cleanup_required）
CLEANUP_PATTERNS = [
    r'^(npm|yarn|pnpm|bun)\s+run\s+(dev|start|watch|serve)',
    r'^(vite|next|webpack-dev-server|nodemon|cargo\s+watch)',
    r'^(jest|vitest|cargo\s+test).*--watch',
    r'^(live-server|http-server|python\s+-m\s+http\.server)',
]

# 2. 継続実行パターン（keep_running）
KEEP_RUNNING_PATTERNS = [
    r'^(docker|kubectl|minikube)',
    r'^(postgres|mysql|redis-server|mongod)',
    r'(build|compile).*--release',
    r'^(npm|yarn|pnpm|bun)\s+run\s+build',
]

# 3. 判定不能（ask_user）
# 上記いずれにもマッチしない場合
```

**実行フロー**:
```
IF command matches CLEANUP_PATTERNS:
    shell_id にラベル付与: cleanup_required
    IF TodoWrite使用中:
        最終todoに追加: {content: "バックグラウンドプロセスをクリーンアップ", activeForm: "バックグラウンドプロセスをクリーンアップ中", status: "pending"}
    ELSE:
        内部記録: cleanup_targets.append(shell_id)

ELIF command matches KEEP_RUNNING_PATTERNS:
    shell_id にラベル付与: keep_running
    何もしない（継続実行）

ELSE:
    AskUserQuestion即座に実行:
        question: "バックグラウンドプロセス `{command}` をタスク完了時に自動停止しますか？"
        options: ["はい（自動停止）", "いいえ（継続実行）"]
    IF ユーザー選択 == "はい":
        cleanup_required として処理
    ELSE:
        keep_running として処理
```

#### タスク完了時の実行トリガー

**トリガー検出条件（いずれか）**:
1. TodoWrite最終todo（最後の要素）が completed に変更された直後
2. ユーザーメッセージに「完了」「終わり」「done」「finish」が含まれる
3. 全todoが completed かつ 新規ユーザーメッセージ受信時

**クリーンアップ実行**:
```
cleanup_targets = [cleanup_required ラベルの全shell_id]

IF cleanup_targets が空:
    何もしない

ELIF len(cleanup_targets) == 1:
    KillShell(cleanup_targets[0])
    エラー無視（既に終了済みの場合）

ELSE:
    FOR EACH shell_id IN cleanup_targets:
        KillShell(shell_id)
        エラー無視
```

**エラーハンドリング**: 全てのKillShellエラーを無視（既に終了済み・存在しない場合は正常）

## タスク管理戦略 {#task-management}

### TodoWrite使用基準

**必須（3つ以上のステップ）**:
- 機能実装（設計→実装→テスト）
- バグ修正（調査→修正→検証）
- リファクタリング（分析→変更→確認）

**不要（単一・簡単なタスク）**:
- ファイル1つの修正
- 情報検索・質問への回答
- 単純なコマンド実行

### ドキュメント駆動タスク管理 {#doc-driven-tasks}

**tasks.yml による構造化タスク管理**:
- プロジェクトルートに `tasks.yml` を配置
- 各タスクに `docs` 配列でドキュメント参照を記載
- `/implement` コマンドが自動的にドキュメントコンテキストを注入

**tasks.yml 構造**:
```yaml
- id: task-1
  goal: "実装目標"
  status: pending
  docs:
    - "docs/design.md#SectionName"
    - "docs/api-spec.md#Endpoint"
  acceptance_criteria:
    - "受入基準1"
    - "受入基準2"
```

**実装ワークフロー**:
1. `/implement task-1` 実行
2. `docs` 配列の全ドキュメントセクションを自動Read
3. コンテキスト注入して実装開始
4. 完了時に `status: completed` に自動更新

## トラブル対応 {#troubleshooting}

**判断基準**:
- **曖昧指示**: AskUserQuestionで選択肢提示
- **技術不明**: WebFetch仕様確認 + 複数案提示
- **認識齟齬**: 停止 → 事実確認 → 学習記録作成
- **緊急時**: セキュリティ優先、他簡略化可

---

## コード品質基準 {#code-quality}

### 型安全言語（TypeScript, Rust, Go等）
- 型安全性: any回避・strictモード有効化・型推論活用
- コンパイルエラー・リンター警告: 0件必須
- フォーマッター: 言語標準ツールで統一
- エラーハンドリング: 型システム活用（Result<T>, Option<T>等、unwrap禁止）

### 動的言語（JavaScript, Python, Ruby等）
- リンター・フォーマッター: 0件必須・統一整形
- テストカバレッジ: 新機能の適切なカバレッジ

### 全言語共通
- 命名規則・コメント: プロジェクト内で一貫性確保
- 依存関係: 不要な依存排除・脆弱性回避
- 編集後フロー: フォーマッター → リンター → テスト
- 詳細: `~/.claude/stacks/{tech}.md`

## セキュリティ基準 {#security-standards}

- OWASP Top 10対応必須
- 機密情報管理: ハードコード禁止・環境変数使用
- 依存関係: 定期的な脆弱性スキャン
- セキュリティテスト: 認証・認可・入力検証の検証必須
- 詳細: `~/.claude/stacks/{tech}.md`

## リスク評価の必須記載

### 全技術提案での必須フォーマット
すべての技術提案・実装案には以下フォーマットでリスク評価を**必ず含める**。リスク評価なしの提案は不完全とみなす：

```markdown
## 🛡️ リスク評価

### セキュリティリスク **（最重要）**
- **[HIGH/MEDIUM/LOW]**: [認証、機密情報、入力検証等の具体的リスク]
- **軽減策**: [暗号化、サニタイズ、権限制御等の対策]

### 技術的リスク
- **[HIGH/MEDIUM/LOW]**: [破綻的変更、パフォーマンス、保守性への影響]
- **軽減策**: [段階的移行、テスト、rollback戦略]

### 開発効率リスク
- **[HIGH/MEDIUM/LOW]**: [工数増加、学習コスト、複雑性増大]
- **軽減策**: [段階実装、ドキュメント整備、チーム共有]
```

### リスクレベル判定基準
- **HIGH**: 本番環境・セキュリティ・データに重大な影響
- **MEDIUM**: 開発効率・保守性に一定の影響
- **LOW**: 軽微な影響、既知の対策で解決可能

### セキュリティリスク重視方針
- **OWASP Top 10** 基本対策を技術スタック問わず考慮
- **入力検証・出力エスケープ** の実装状況を明記
- **認証・認可・機密情報** への影響を詳細評価
- **外部通信・依存関係** のセキュリティリスクを確認

---

## ファイル操作権限 {#file-permissions}

### 絶対禁止操作

- `.env`, `.envrc`, `.env.*`, `credentials.*`, `secrets.*` の読み書き
- `.git/` ディレクトリ内の直接操作（git コマンド経由のみ可）
- `.DS_Store`, `Thumbs.db` 等のOS固有ファイル作成
- ホームディレクトリ外（`~/`以外）への書き込み

---

## AI協働ツール最適化 {#ai-collaboration}

### ツール選択の優先順位

**1. 探索・検索はTask tool（Explore agent）**
- 複数ファイル横断検索
- アーキテクチャ理解
- 「どこで実装されているか」系の質問

**2. 並列実行を最大化**
- 独立タスク = 単一メッセージで複数ツール
- 例: 複数Read、独立した検索、agent同時起動
- 依存あり = 順次実行（Edit後Read、Write後Bash等）

**3. 専用ツール優先**
- ファイル操作: Read/Edit/Write（Bash cat/sed/echo禁止）
- 検索: Grep/Glob（Bash find/grep禁止）
- コード編集: Serena MCP（大規模変更時、トークン効率向上）

**4. MCP活用**
- IDE MCP: 診断情報（ESLint、TypeScript等）、コード実行
- Serena MCP: シンボリック編集でファイル全体読み込み回避

### エージェントメタデータ制約 {#agent-metadata}

**フロントマターによる安全性制御**:

**.agent.md ファイル構造**:
```yaml
---
model: claude-sonnet-4-5-20250929
tools: [Read, Grep, Glob]
security_level: high
readonly: true
forbidden_paths: [~/.ssh/*, ~/.aws/*, .env*]
max_turns: 20
---
```

**セキュリティレベル別制約**:
- `high`: Read/Grep/Globのみ許可（読み取り専用）
- `medium`: Write/Edit許可、Bash/WebFetch禁止
- `low`: 全ツール許可、forbidden_pathsのみ制限

**パス制限パターン**:
- `~/.ssh/*`, `~/.aws/*` - 認証情報ディレクトリ
- `.env*`, `credentials.*`, `secrets.*` - 環境変数・機密ファイル
- `/etc/*`, `/usr/*` - システムディレクトリ

**実行フロー**:
1. `.agent.md` のフロントマターをパース
2. `tools` リストから許可ツールを抽出
3. `forbidden_paths` でパスアクセスを制限
4. ツール実行時に制約を検証

---

## CLI実装言語の自動選択 {#cli-language-selection}

### 言語選択の優先順位

CLI実装時、以下の順で判断：

**1. セキュリティリスクあり → Rust**
- ユーザー入力処理（CLI引数、stdin等）
- 外部データソース（API、ネットワーク通信）
- 認証・暗号化・機密情報処理

**2. データ処理・API連携 → Python**
- CSV/JSON/YAML処理、データ集計
- REST API クライアント
- 統計計算、ログ解析、レポート生成

**3. 高パフォーマンス必須 → Rust**
- 大量データ（GB単位、数万件以上）
- 並行処理、CPU集約的処理
- バイナリ配布が必要

**4. 軽量自動化 → Shell**
- < 50行かつ外部入力なし
- Git hooks、CI/CD、ビルドスクリプト

**5. デフォルト → Python**
- 上記に該当しない中規模スクリプト

### 言語別実装ルール

#### Shell
- `set -euo pipefail` 必須
- 変数は `"$var"` で引用
- `eval` 禁止、外部入力を直接コマンドに渡さない
- 詳細: `~/.claude/stacks/shell-cli.md`

#### Python
- 型ヒント使用（mypy推奨）
- CLI: Click/Typer/argparse
- エラーハンドリング徹底

#### Rust
- CLI: clap
- Result型でエラーハンドリング
- 詳細: `~/.claude/stacks/rust-cli.md`

---

## WebFetch使用時の重要原則
- [禁止] HTTP成功を「エラー」と報告しない
- [必須] 大容量処理は「処理中」として正確に報告
- [必須] 具体的なエラー内容を明示

---

## このファイルの編集ルール {#editing-rules}

### LLM最適化の原則

CLAUDE.mdを編集する際は以下の原則を厳守：

1. **ユーザー向け情報の除外**
   - コマンド使用例（`cldev lr find "認証"` 等）は削除
   - 「/helpで確認」等のユーザー案内は削除
   - 使い方・トラブルシューティングは `USER_GUIDE.md` へ

2. **LLM動作指示に特化**
   - 具体的な動作指示・判断基準のみ記載
   - 技術的な条件分岐・アルゴリズムを明示
   - チェックリスト・フォーマット定義を優先

3. **構造化と簡潔性**
   - 装飾的な文章を避け、箇条書き・表・コードブロックを活用
   - セクションIDを付与（`{#section-id}`）
   - 冗長な説明を削除し、必要最小限の情報のみ

4. **トークン効率**
   - 全会話で読み込まれるため、不要な情報は徹底削除
   - 重複する内容は統合
   - 外部ファイル参照を活用（技術スタック別設定等）

### 編集時のチェックリスト

- ユーザー向け情報を含んでいないか？
- 具体的な動作指示・判断基準になっているか？
- トークン効率を考慮した簡潔な記述か？
- 外部ファイルへの参照で代替できないか？

---

## 設定ファイル管理 {#config-files}

### 設定ファイル構造

- `~/.claude/settings.json` - Claude Code システム設定
- `~/.claude/CLAUDE.md` - LLM向け動作設定（このファイル）
- `~/.claude/USER_GUIDE.md` - ユーザー向けガイド
- `~/.claude/stacks/*.md` - 技術スタック別設定
- `project/.claude/CLAUDE.md` - プロジェクト固有設定

---

## 技術スタック設定システム {#tech-stack-system}

### 設定継承メカニズム

**3層構造**:
1. **基盤層**: `~/.claude/CLAUDE.md` (技術中立的な開発フロー・セキュリティ基準)
2. **技術層**: `~/.claude/stacks/{tech-stack}.md` (技術スタック別設定)
3. **プロジェクト層**: `project/.claude/CLAUDE.md` (プロジェクト固有設定)

**継承例**:
- `/feature` → 基盤層の段階的実装フロー
- `/web:lighthouse` → 技術層のWeb特化機能
- プロジェクト固有コマンド → プロジェクト層の専用機能

#### プロジェクト設定での技術指定
```yaml
# project/.claude/CLAUDE.md 冒頭
tech_stack: frontend-web  # 継承する技術スタック指定
project_type: spa        # プロジェクト種別
team_size: 3-5           # チーム規模
```

### 技術スタック別設定ファイル

技術スタック別の詳細設定は以下のファイルを参照：
- `~/.claude/stacks/frontend-web.md` - Web Frontend開発
- `~/.claude/stacks/backend-api.md` - API Backend開発
- `~/.claude/stacks/mobile-app.md` - Mobile App開発
- `~/.claude/stacks/data-science.md` - Data Science開発
- `~/.claude/stacks/rust-cli.md` - Rust CLI開発
- `~/.claude/stacks/shell-cli.md` - Shell CLI開発（POSIX準拠の完全基準）

### 設計・開発ガイドライン

スラッシュコマンド開発時の基準：
- `~/.claude/stacks/slash-command-design.md` - LLM最適化されたコマンド設計指針


---

## MCP統合 {#mcp-servers}

### 利用可能なMCP関数

#### IDE MCP Server
- `mcp__ide__executeCode` - コード実行（Jupyter等）
- `mcp__ide__getDiagnostics` - 診断情報取得（ESLint、TypeScript等）

#### Figma Dev Mode MCP
- 詳細ルール: `~/.claude/docs/mcp-figma-rules.md`（Figmaプロジェクトのみ）

---

## 外部設定参照 {#external-refs}

**開発時参照**:
- 技術判断: `~/.claude/stacks/{tech}.md`
- 品質検証: `~/.claude/validation/layers/*.md`
- セキュリティパターン: `~/.claude/validation/security-patterns.json`
- OWASPチェックリスト: `~/.claude/validation/owasp-top10-checklist.md`
- スキーマ定義: `~/.claude/schemas/*.json`
- テンプレート: `~/.claude/templates/*.yml`
- ユーティリティ: `~/.claude/utils/*.py`
- エージェント: `~/.claude/agents/*.agent.md`
- エラー調査: `~/.claude/learnings/*.md`

**意思決定・アイデア創出**:
- 意思決定フレームワーク: `~/.claude/docs/decision-frameworks.md`
- ICE/RICE スコアリング基準、First Principles等の実践的手法

**機能別参照**:
- AutoFlow統合: `~/.claude/docs/autoflow-integration-guide.md`
- Figma連携: `~/.claude/docs/mcp-figma-rules.md`

**コマンド実装**:
- /implement: `commands/implement.md`
- /task-validate: `commands/task-validate.md`

---

## 学習記録参照 {#learning-records}

- 参照タイミング: エラー調査・技術決定時
- 検索コマンド: `cldev lr suggest "[エラーメッセージ]"` または `cldev lr find "[キーワード]"`
- 記録場所: `~/.claude/learnings/*.md`

---
