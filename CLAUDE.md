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
- Agent起動時、Task tool の prompt に以下を必ず含める：
  - `作業ディレクトリ: [絶対パス]`（例：`~/projects/foo`）
  - `期待する成果: [具体的内容]`（例：`src/auth.ts に変更が加わること`）
  - `失敗時の報告: "ERROR: [理由]" で始めること`
- Agent完了時の確認：
  - Agent出力に `ERROR:` が含まれる → 即座に作業停止、ユーザーに状況報告、次アクション再検討
  - 重要操作（ファイル削除、DB変更等）の場合のみ → 報告されたファイル/ディレクトリの実在を確認
  - 確認例: `ls -la [報告されたパス] 2>/dev/null || echo "VERIFICATION_FAILED"`

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

## トラブル対応 {#troubleshooting}

### エラー・バグ発生時
1. エラー発生 → 再現手順確認
2. 現象確認 → ログ分析
3. 原因特定 → デバッグ実施
4. 修正実装 → 最小限の修正
5. 検証 → 回帰テスト

### 認識齟齬発生時
1. 齟齬発生 → 議論停止・情報収集
2. 事実確認 → WebFetch仕様確認
3. 選択肢提示 → 複数案提示
4. 合意形成 → 技術的妥協点
5. 実装継続 → 学習記録作成

### 対応指針
- **曖昧指示**: AskUserQuestionで選択肢提示
- **技術疑問**: WebFetch仕様確認 + 複数案提示
- **緊急時**: セキュリティ必須、他簡略化可

---

## コード品質基準（必須チェック項目） {#code-quality}

### 言語別品質基準
#### 型安全言語（TypeScript, Rust, Go等）
- [ ] **型安全性**: `any`等の回避・型推論活用
- [ ] **コンパイルエラー**: 0件必須
- [ ] **型チェック**: strictモード有効化
- [ ] **リンター警告**: 0件必須（cargo clippy, eslint等）
- [ ] **コードフォーマット**: 言語標準ツールで統一（cargo fmt, prettier等）
- [ ] **エラーハンドリング**: 型システム活用（Result<T>, Option<T>等、unwrap禁止）

**コード編集後の推奨フロー**:
1. フォーマッター実行 → 2. リンター確認 → 3. 関連テスト実行

#### 動的言語（JavaScript, Python, Ruby等）
- [ ] **リンター**: 言語別リンター 0件必須
- [ ] **フォーマッター**: 統一されたコード整形
- [ ] **テストカバレッジ**: 新機能の適切なカバレッジ

### 共通品質基準
- [ ] **命名規則**: プロジェクト内での一貫した命名規則遵守
- [ ] **コメント**: 複雑なロジックには適切な説明コメント
- [ ] **依存関係**: 不要な依存の排除、セキュリティ脆弱性の回避

## セキュリティ基準（必須チェック項目） {#security-standards}

### OWASP対応（技術問わず）
- [ ] **入力検証**: 全ユーザー入力の適切なバリデーション実装（例: zod, yup, joi等のライブラリ使用）
- [ ] **出力エスケープ**: インジェクション攻撃対策の適切な処理（例: DOMPurify, テンプレートエンジンの自動エスケープ）
- [ ] **認証・認可**: 適切な権限チェックとセッション管理（例: JWT, OAuth2/OIDC, セッション管理ライブラリ）
- [ ] **暗号化通信**: 機密データ送信時の暗号化確保（例: HTTPS/TLS, 暗号化ライブラリ）

### 実装での注意点
- [ ] **機密情報**: ハードコードされた秘密情報（API Key等）の排除
- [ ] **依存関係**: 既知の脆弱性を持つライブラリの使用回避
- [ ] **エラーハンドリング**: 機密情報を漏洩しないエラーメッセージ
- [ ] **データ保護**: 個人情報・機密データの適切な取り扱い

### Git ワークフロー
- [ ] **ブランチ戦略**: feature/fix/refactor の適切な命名
- [ ] **コミットメッセージ**: 変更内容の明確な説明
- [ ] **プルリクエスト**: 変更の目的と影響範囲の説明
- [ ] **マージ前確認**: CI/CD パイプラインの成功確認

### テスト要件
- [ ] **単体テスト**: 新機能・修正箇所の適切なテストカバレッジ
- [ ] **統合テスト**: 重要な機能フローの end-to-end テスト
- [ ] **手動テスト**: UI/UX の視覚的・操作的な動作確認
- [ ] **リグレッション**: 既存機能への影響がないことを確認

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

- [ ] ユーザー向け情報を含んでいないか？
- [ ] 具体的な動作指示・判断基準になっているか？
- [ ] トークン効率を考慮した簡潔な記述か？
- [ ] 外部ファイルへの参照で代替できないか？

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

## 関連ドキュメント {#related-docs}

- **ユーザーガイド**: `~/.claude/USER_GUIDE.md` (コマンド一覧・使い方)
- **スラッシュコマンド**: `~/.claude/commands/` (効率化ワークフロー)
- **技術スタック設定**: `~/.claude/stacks/` (技術別専門設定)
- **プロジェクト設定**: `~/.claude/project-configs/`
- **学習記録**: `~/.claude/learning-sessions/`
- **詳細ケーススタディ**: `~/.claude/docs/case-studies.md`
- **実装予定機能**: `~/.claude/docs/roadmap.md`
- **コマンド実装状況**: `~/.claude/docs/command-dashboard.md`

---

## 学習記録活用（cldev統合）

### 学習記録の場所
`~/.claude/learning-sessions/*.md`

### 自動参照推奨タイミング
- `/urgent`, `/fix`, `/debug` 実行時
- エラー調査時（過去の類似問題確認）
- 技術的決定の背景確認

### 記録フォーマット
各学習記録は以下を含む：
- 問題の説明
- 根本原因
- 解決策
- 重要な学び
- 関連ファイル

---
