# Shell CLI実装ガイドライン

## 📋 目次

- [概要](#概要)
- [セキュリティ基準（18項目）](#セキュリティ基準18項目)
  - [基本セキュリティ（8項目）](#基本セキュリティ8項目)
  - [高度なセキュリティ（10項目）](#高度なセキュリティ10項目)
- [ユーザビリティ基準（10項目）](#ユーザビリティ基準10項目)
- [パフォーマンス基準（12項目）](#パフォーマンス基準12項目)
- [保守性基準（12項目）](#保守性基準12項目)
- [実装チェックリスト](#実装チェックリスト)
- [参考資料](#参考資料)

---

## 🎯 概要

### 目的
このガイドラインはClaude CodeがShell CLIツールを実装する際の完全な品質基準を提供します。セキュリティ、ユーザビリティ、パフォーマンス、保守性の4観点から52項目の実装ルールを定義しています。

### 対象読者
- **主要**: Claude Code（AI開発エージェント）
- **補助**: Shell CLI実装を行う開発者

### 適用タイミング
以下のケースでShell CLI実装が選択された場合に適用：
- Git hooks、pre-commit等の自動化スクリプト
- ビルドスクリプト、CI/CD自動化
- 簡易的な開発ツール（< 200行）
- 依存関係を最小化したい場合

### 重要原則
1. **セキュリティ最優先**: ユーザー入力を扱う場合は常に検証・サニタイズ
2. **明示的なエラーハンドリング**: `set -euo pipefail`を常に使用
3. **POSIX互換性**: 移植性が重要な場合はPOSIX準拠
4. **パフォーマンス意識**: 起動時間とループ内処理を最適化

---

## 🔒 セキュリティ基準（18項目）

### 基本セキュリティ（8項目）

#### 3. 適切なエラーメッセージ

**目的**: 機密情報漏洩防止、デバッグ支援

❌ **悪い例**（機密情報露出）:
```bash
# パスワードがエラーメッセージに含まれる
echo "Failed to connect: mysql -u root -p$PASSWORD" >&2
```

✅ **良い例**（安全なエラーメッセージ）:
```bash
# 機密情報を含まない、有用なエラーメッセージ
error() {
    echo "Error: $*" >&2
    return 1
}

# 使用例
if ! mysql -u root -p"$PASSWORD" < schema.sql; then
    error "Database initialization failed. Check credentials and permissions."
fi
```

📝 **なぜ重要か**:
- エラーログは多くの場所に記録される（ログファイル、監視システム等）
- パスワード、APIキー等の機密情報漏洩リスクを回避
- ユーザーに必要な情報のみ提供

---

#### 4. 破壊的変更の確認

**目的**: データ損失防止、誤操作防止

❌ **悪い例**（確認なし削除）:
```bash
# 警告なしでファイルを削除
rm -rf "$directory"
```

✅ **良い例**（確認プロンプト）:
```bash
# 破壊的操作前に確認
confirm() {
    local prompt="${1:-Are you sure?}"
    local response

    read -p "$prompt [y/N] " response
    case "$response" in
        [yY][eE][sS]|[yY]) return 0 ;;
        *) return 1 ;;
    esac
}

# 使用例
if confirm "Delete directory '$directory' and all contents?"; then
    rm -rf "$directory"
    echo "Deleted: $directory"
else
    echo "Operation cancelled."
fi
```

📝 **なぜ重要か**:
- 誤操作による重要データの損失を防止
- ユーザーに操作内容を明示的に確認させる
- `-f`（force）オプションを使う前に必ず確認

---

#### 5. 数値オプション制限

**目的**: インジェクション攻撃防止、入力検証

❌ **悪い例**（入力検証なし）:
```bash
# ユーザー入力を検証せずに使用
count="$1"
for i in $(seq 1 "$count"); do
    process_item "$i"
done
```

✅ **良い例**（厳密な数値検証）:
```bash
# 数値であることを検証し、範囲を制限
validate_number() {
    local input="$1"
    local min="${2:-1}"
    local max="${3:-1000}"

    # 数値のみ許可
    if ! [[ "$input" =~ ^[0-9]+$ ]]; then
        error "Invalid input: must be a positive integer"
        return 1
    fi

    # 範囲チェック
    if (( input < min || input > max )); then
        error "Value out of range: must be between $min and $max"
        return 1
    fi

    return 0
}

# 使用例
count="$1"
if validate_number "$count" 1 100; then
    for i in $(seq 1 "$count"); do
        process_item "$i"
    done
fi
```

📝 **なぜ重要か**:
- コマンドインジェクション攻撃を防止
- 異常な値によるリソース枯渇（DoS）を防止
- ユーザーに明確なエラーフィードバック

---

#### 6. 選択肢の検証

**目的**: インジェクション防止、入力サニタイズ

❌ **悪い例**（ホワイトリストなし）:
```bash
# ユーザー入力を直接コマンドに使用
action="$1"
$action  # 危険: 任意のコマンド実行可能
```

✅ **良い例**（ホワイトリスト検証）:
```bash
# 許可された選択肢のみ受け付ける
validate_choice() {
    local input="$1"
    shift
    local valid_choices=("$@")

    for choice in "${valid_choices[@]}"; do
        if [[ "$input" == "$choice" ]]; then
            return 0
        fi
    done

    error "Invalid choice: '$input'. Valid options: ${valid_choices[*]}"
    return 1
}

# 使用例
action="$1"
if validate_choice "$action" "start" "stop" "restart"; then
    case "$action" in
        start) start_service ;;
        stop) stop_service ;;
        restart) restart_service ;;
    esac
fi
```

📝 **なぜ重要か**:
- ホワイトリスト方式で安全性を確保
- 予期しないコマンド実行を完全に防止
- 明確なエラーメッセージでユーザーを誘導

---

#### 9. 終了コード一貫性

**目的**: エラーハンドリング統一、スクリプト連携

❌ **悪い例**（不統一な終了コード）:
```bash
# 異なるエラーで同じコード
if [[ ! -f "$file" ]]; then
    exit 1
fi

if [[ ! -r "$file" ]]; then
    exit 1
fi
```

✅ **良い例**（体系的な終了コード）:
```bash
#!/bin/bash
set -euo pipefail

# 終了コードの定数定義
readonly EXIT_SUCCESS=0
readonly EXIT_USAGE_ERROR=1
readonly EXIT_FILE_NOT_FOUND=2
readonly EXIT_PERMISSION_DENIED=3
readonly EXIT_NETWORK_ERROR=4

# エラーハンドリング関数
die() {
    local code="$1"
    shift
    echo "Error: $*" >&2
    exit "$code"
}

# 使用例
if [[ ! -f "$file" ]]; then
    die "$EXIT_FILE_NOT_FOUND" "File not found: $file"
fi

if [[ ! -r "$file" ]]; then
    die "$EXIT_PERMISSION_DENIED" "Permission denied: $file"
fi
```

📝 **なぜ重要か**:
- CI/CDパイプラインでのエラー判定が容易
- 呼び出し元スクリプトでエラー種別を識別可能
- デバッグ・トラブルシューティングが効率化

---

#### 11. 標準入出力の適切な使用

**目的**: ログ分離、パイプライン連携

❌ **悪い例**（出力が混在）:
```bash
# エラーとデータが同じストリーム
echo "Processing file: $file"
echo "Error: invalid format"
cat "$file"
```

✅ **良い例**（適切なストリーム分離）:
```bash
# 標準出力: データのみ
# 標準エラー出力: ログ・エラー

log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $*" >&2
}

error() {
    echo "Error: $*" >&2
}

# 使用例
log "Processing file: $file"
if ! data=$(process_file "$file"); then
    error "Invalid format in file: $file"
    exit 1
fi

# データのみを標準出力（パイプライン連携可能）
echo "$data"
```

📝 **なぜ重要か**:
- パイプライン連携時にログがデータに混入しない
- リダイレクト時の動作が予測可能
- UNIXフィロソフィーに準拠

---

#### 16. クリーンアップ処理

**目的**: 機密情報残存防止、リソース解放

❌ **悪い例**（クリーンアップなし）:
```bash
# 一時ファイルが残る
tmpfile="/tmp/secret_data.$$"
echo "$password" > "$tmpfile"
process_data "$tmpfile"
# スクリプト終了時にファイルが残る
```

✅ **良い例**（trap による確実なクリーンアップ）:
```bash
#!/bin/bash
set -euo pipefail

# クリーンアップ関数
cleanup() {
    local exit_code=$?

    # 一時ファイルの削除
    if [[ -n "${tmpfile:-}" ]] && [[ -f "$tmpfile" ]]; then
        rm -f "$tmpfile"
    fi

    # 機密変数のクリア
    unset password api_key

    exit "$exit_code"
}

# trapで確実にクリーンアップ
trap cleanup EXIT INT TERM

# 一時ファイル作成
tmpfile=$(mktemp)
chmod 600 "$tmpfile"

# 処理
echo "$password" > "$tmpfile"
process_data "$tmpfile"

# 正常終了時もcleanupが実行される
```

📝 **なぜ重要か**:
- Ctrl+C等での中断時も確実にクリーンアップ
- 機密情報の漏洩リスクを最小化
- ディスク容量の無駄遣いを防止

---

#### 17. 依存関係チェック

**目的**: サプライチェーン攻撃防止、明確なエラー

❌ **悪い例**（依存確認なし）:
```bash
# コマンドが存在しない場合に不明瞭なエラー
jq '.data' < response.json
```

✅ **良い例**（事前依存確認）:
```bash
# 依存コマンドのチェック
require_command() {
    local cmd="$1"
    local package="${2:-$cmd}"

    if ! command -v "$cmd" &>/dev/null; then
        error "Required command not found: $cmd"
        error "Install it with: apt install $package  # or brew install $package"
        exit 127
    fi
}

# スクリプト開始時に全依存を確認
require_command jq
require_command curl
require_command git

# 以降は安全にコマンド使用可能
jq '.data' < response.json
```

📝 **なぜ重要か**:
- 明確なエラーメッセージでユーザーを誘導
- スクリプト実行前に問題を検出
- 不正なコマンド実行（PATH汚染等）を防止

---

### 高度なセキュリティ（10項目）

#### 19. パストラバーサル対策

**目的**: ディレクトリトラバーサル攻撃防止

❌ **悪い例**（パストラバーサル可能）:
```bash
# 危険: ../../../../etc/passwd が可能
file="$1"
cat "$file"
```

✅ **良い例**（パス検証とサニタイズ）:
```bash
# ベースネーム抽出とホワイトリスト検証
safe_read_file() {
    local input="$1"
    local safe_dir="/var/app/data"

    # ディレクトリ部分を削除（ベースネームのみ）
    local filename
    filename=$(basename "$input")

    # ファイル名の検証（英数字、ドット、ハイフン、アンダースコアのみ）
    if ! [[ "$filename" =~ ^[a-zA-Z0-9._-]+$ ]]; then
        error "Invalid filename: $filename"
        return 1
    fi

    # 安全なディレクトリ内のファイルのみ読み取り
    local safe_path="$safe_dir/$filename"

    if [[ ! -f "$safe_path" ]]; then
        error "File not found: $filename"
        return 1
    fi

    cat "$safe_path"
}

# 使用例
safe_read_file "$user_input"
```

📝 **なぜ重要か**:
- 任意のファイル読み取りを防止
- `/etc/passwd`等の機密ファイルアクセスを防止
- ベースネームのみ使用する設計を推奨

---

#### 20. 一時ファイルの安全な作成

**目的**: 競合状態防止、予測不可能なファイル名

❌ **悪い例**（予測可能、競合状態）:
```bash
# 危険: プロセスIDは予測可能
tmpfile="/tmp/myapp.$$"
echo "$sensitive_data" > "$tmpfile"
```

✅ **良い例**（mktemp使用）:
```bash
# mktemp でランダムな一時ファイル作成
create_secure_temp() {
    local tmpfile
    tmpfile=$(mktemp) || {
        error "Failed to create temporary file"
        return 1
    }

    # 所有者のみ読み書き可能
    chmod 600 "$tmpfile"

    echo "$tmpfile"
}

# 使用例
tmpfile=$(create_secure_temp)
trap 'rm -f "$tmpfile"' EXIT

echo "$sensitive_data" > "$tmpfile"
process_data "$tmpfile"
```

📝 **なぜ重要か**:
- TOCTOU（Time-of-check to time-of-use）攻撃防止
- シンボリックリンク攻撃防止
- 他ユーザーによる読み取りを防止

---

#### 21. シェルインジェクション対策

**目的**: コマンドインジェクション防止

❌ **悪い例**（eval使用）:
```bash
# 危険: 任意のコマンド実行が可能
file="$1"
eval "cat $file"  # 入力: "; rm -rf /"
```

✅ **良い例**（直接実行、引用符必須）:
```bash
# 直接実行、変数を適切に引用
file="$1"
cat "$file"

# 複雑な場合は配列を使用
files=("$@")
for file in "${files[@]}"; do
    cat "$file"
done

# コマンド構築が必要な場合は printf を使用
printf '%s\n' "$file" | xargs cat
```

📝 **なぜ重要か**:
- `eval`は常に危険、使用禁止
- 引用符なし変数展開も危険
- 配列を使えば複雑な処理も安全

---

#### 22. 環境変数の安全な使用

**目的**: PATH汚染防止、環境変数インジェクション防止

❌ **悪い例**（PATH汚染）:
```bash
# 危険: ユーザー入力でPATHを汚染
user_path="$1"
PATH="$user_path:$PATH"
```

✅ **良い例**（検証とホワイトリスト）:
```bash
# 安全なPATH設定
safe_add_to_path() {
    local new_path="$1"

    # 存在確認
    if [[ ! -d "$new_path" ]]; then
        error "Directory does not exist: $new_path"
        return 1
    fi

    # ホワイトリスト検証（許可されたパスのみ）
    local allowed_paths=(
        "/usr/local/bin"
        "/opt/myapp/bin"
        "$HOME/.local/bin"
    )

    local allowed=false
    for allowed_path in "${allowed_paths[@]}"; do
        if [[ "$new_path" == "$allowed_path" ]]; then
            allowed=true
            break
        fi
    done

    if [[ "$allowed" == "false" ]]; then
        error "Path not in whitelist: $new_path"
        return 1
    fi

    PATH="$new_path:$PATH"
}

# 使用例
safe_add_to_path "/usr/local/bin"
```

📝 **なぜ重要か**:
- 悪意あるコマンドの実行を防止
- システムコマンドの上書きを防止
- 明示的なホワイトリスト方式を推奨

---

#### 23. sudoの安全な使用

**目的**: 権限昇格の最小化、監査

❌ **悪い例**（sudo + eval）:
```bash
# 危険: root権限で任意コマンド実行
user_command="$1"
sudo eval "$user_command"
```

✅ **良い例**（sudo回避、必要最小限）:
```bash
# 原則: sudo使用を避ける設計

# やむを得ず必要な場合
# 1. sudoers で特定コマンドのみ許可
#    user ALL=(ALL) NOPASSWD: /usr/local/bin/specific-command

# 2. スクリプト内では直接実行
if ! sudo /usr/local/bin/specific-command --option value; then
    error "Failed to execute privileged command"
    exit 1
fi

# 3. ユーザー入力は絶対に渡さない
# 悪い例: sudo some-command "$user_input"
# 良い例: 固定パラメータのみ
```

📝 **なぜ重要か**:
- root権限での任意コマンド実行を防止
- sudoersファイルでの明示的な許可を推奨
- 最小権限の原則に従う

---

#### 24. パスワード・機密情報の扱い

**目的**: 機密情報漏洩防止

❌ **悪い例**（コマンドライン引数）:
```bash
# 危険: psコマンドで見える
password="$1"
mysql -u root -p"$password" < schema.sql

# ログに残る
echo "Connecting with password: $password"
```

✅ **良い例**（非表示入力、環境変数）:
```bash
# 非表示入力
read_password() {
    local password
    read -s -p "Password: " password
    echo >&2  # 改行
    echo "$password"
}

# 使用例
password=$(read_password)

# 環境変数として渡す（プロセス環境のみ）
MYSQL_PWD="$password" mysql -u root < schema.sql

# 使用後即座に削除
unset password MYSQL_PWD

# より安全: ファイルから読み取り（パーミッション 600）
if [[ -f ~/.myapp/credentials ]]; then
    chmod 600 ~/.myapp/credentials
    source ~/.myapp/credentials  # PASSWORD変数を設定
    # 使用後削除
    unset PASSWORD
fi
```

📝 **なぜ重要か**:
- コマンドライン引数は`ps`で誰でも見える
- ログファイルに機密情報を残さない
- 環境変数も使用後即座にクリア

---

#### 25. 安全なファイルパーミッション

**目的**: 不正アクセス防止、機密性保持

❌ **悪い例**（緩いパーミッション）:
```bash
# 誰でも読める
echo "$api_key" > config.txt
```

✅ **良い例**（厳格なパーミッション）:
```bash
# umask で新規ファイルのデフォルトパーミッション設定
# 077 = 所有者のみ読み書き可能
umask 077

# 機密ファイル作成
config_file="$HOME/.myapp/config"
mkdir -p "$(dirname "$config_file")"
touch "$config_file"
chmod 600 "$config_file"  # 明示的に設定

# 内容を書き込み
cat > "$config_file" <<EOF
API_KEY=$api_key
SECRET=$secret
EOF

# ディレクトリも保護
chmod 700 "$HOME/.myapp"
```

📝 **なぜ重要か**:
- 他ユーザーによる機密情報読み取りを防止
- umaskでデフォルトを安全に設定
- ディレクトリとファイル両方を保護

---

#### 26. コマンド置換の安全性

**目的**: コマンドインジェクション防止

❌ **悪い例**（ユーザー入力をコマンド置換）:
```bash
# 危険: 任意のコマンド実行
user_input="$1"
result=$(eval "$user_input")
```

✅ **良い例**（信頼できるコマンドのみ）:
```bash
# 信頼できるコマンドのみコマンド置換
result=$(date +%Y-%m-%d)
hostname=$(hostname)

# ユーザー入力を含む場合は引数として渡す
# 悪い例:
# result=$(grep "$user_pattern" file.txt)  # パターンインジェクション可能

# 良い例: 固定コマンド、変数は引数
result=$(grep -F "$user_pattern" file.txt)  # -F で固定文字列検索

# より安全: 直接実行
grep -F "$user_pattern" file.txt > result.txt
```

📝 **なぜ重要か**:
- コマンド置換内でのインジェクション防止
- `eval`の使用は絶対に避ける
- `-F`（固定文字列）オプションを活用

---

#### 27. シグナルハンドリング

**目的**: 安全な中断処理、リソース解放

❌ **悪い例**（シグナルハンドリングなし）:
```bash
# Ctrl+C で中断時、一時ファイルが残る
tmpfile=$(mktemp)
long_running_process > "$tmpfile"
cat "$tmpfile"
rm "$tmpfile"
```

✅ **良い例**（trap によるシグナル処理）:
```bash
#!/bin/bash
set -euo pipefail

# クリーンアップ関数
cleanup() {
    local exit_code=$?

    echo "Cleaning up..." >&2

    # プロセス終了
    if [[ -n "${bg_pid:-}" ]]; then
        kill "$bg_pid" 2>/dev/null || true
    fi

    # 一時ファイル削除
    if [[ -n "${tmpfile:-}" ]]; then
        rm -f "$tmpfile"
    fi

    # 機密情報クリア
    unset password

    exit "$exit_code"
}

# 複数シグナルをハンドリング
trap cleanup EXIT      # 正常終了時
trap cleanup INT       # Ctrl+C (SIGINT)
trap cleanup TERM      # kill (SIGTERM)
trap cleanup HUP       # ターミナル切断 (SIGHUP)

# メイン処理
tmpfile=$(mktemp)
long_running_process > "$tmpfile" &
bg_pid=$!

wait "$bg_pid"
cat "$tmpfile"

# 正常終了時もcleanupが実行される
```

📝 **なぜ重要か**:
- Ctrl+C等での中断時も確実にクリーンアップ
- バックグラウンドプロセスを確実に終了
- 複数シグナルを統一的に処理

---

#### 28. セキュアなネットワーク通信

**目的**: 中間者攻撃防止、スクリプト検証

❌ **悪い例**（HTTPで直接実行）:
```bash
# 危険: HTTPは盗聴・改ざん可能、検証なし実行
curl http://example.com/install.sh | bash
```

✅ **良い例**（HTTPS、検証、確認）:
```bash
# 安全なスクリプトダウンロードと実行

# 1. HTTPSで取得
script_url="https://example.com/install.sh"
script_file="install.sh"
checksum_url="https://example.com/install.sh.sha256"

# 2. ダウンロード（エラーで中断）
if ! curl -fsSL "$script_url" -o "$script_file"; then
    error "Failed to download script"
    exit 1
fi

# 3. チェックサム検証
if ! curl -fsSL "$checksum_url" -o "$script_file.sha256"; then
    error "Failed to download checksum"
    exit 1
fi

if ! sha256sum -c "$script_file.sha256"; then
    error "Checksum verification failed"
    exit 1
fi

# 4. 内容を確認（任意）
echo "Downloaded script:"
less "$script_file"
read -p "Execute this script? [y/N] " response
if [[ ! "$response" =~ ^[yY]$ ]]; then
    echo "Cancelled."
    exit 0
fi

# 5. 実行
bash "$script_file"

# 6. クリーンアップ
rm -f "$script_file" "$script_file.sha256"
```

📝 **なぜ重要か**:
- HTTPは中間者攻撃で改ざん可能
- チェックサム検証で改ざんを検出
- ユーザーに内容確認の機会を提供

---

## 🟢 ユーザビリティ基準（10項目）

#### 1. Tab補完（入力補完）

**目的**: 入力効率向上、ユーザー体験改善

❌ **悪い例**（補完なし）:
```bash
# 補完機能なし
case "$1" in
    start) start_service ;;
    stop) stop_service ;;
esac
```

✅ **良い例**（Bash補完スクリプト）:
```bash
# /etc/bash_completion.d/myapp または ~/.bash_completion
_myapp_completion() {
    local cur prev opts
    COMPREPLY=()
    cur="${COMP_WORDS[COMP_CWORD]}"
    prev="${COMP_WORDS[COMP_CWORD-1]}"

    # サブコマンド候補
    local commands="start stop restart status"

    # オプション候補
    local opts="--help --version --verbose"

    # サブコマンド補完
    if [[ ${COMP_CWORD} -eq 1 ]]; then
        COMPREPLY=( $(compgen -W "$commands $opts" -- "$cur") )
        return 0
    fi

    # ファイル補完
    case "$prev" in
        --config|-c)
            COMPREPLY=( $(compgen -f -- "$cur") )
            return 0
            ;;
    esac
}

# 補完関数を登録
complete -F _myapp_completion myapp
```

📝 **なぜ重要か**:
- タイプミスを削減
- 利用可能なオプションを発見しやすい
- プロフェッショナルなCLI体験

---

#### 2. サブコマンドヘルプ

**目的**: 使い方の発見可能性向上

❌ **悪い例**（ヘルプなし）:
```bash
# エラーだけで使い方が分からない
if [[ $# -lt 1 ]]; then
    echo "Error: missing arguments" >&2
    exit 1
fi
```

✅ **良い例**（詳細なヘルプ）:
```bash
show_help() {
    cat <<EOF
Usage: $(basename "$0") [OPTIONS] COMMAND [ARGS]

A tool for managing application services.

Commands:
    start       Start the service
    stop        Stop the service
    restart     Restart the service
    status      Show service status

Options:
    -h, --help      Show this help message
    -v, --verbose   Enable verbose output
    --version       Show version information
    -c, --config    Specify config file

Examples:
    $(basename "$0") start
    $(basename "$0") --config /path/to/config.yml restart
    $(basename "$0") --verbose status

For more information, see: https://docs.example.com/myapp
EOF
}

# サブコマンド別ヘルプ
show_start_help() {
    cat <<EOF
Usage: $(basename "$0") start [OPTIONS]

Start the application service.

Options:
    --port PORT     Specify port number (default: 8080)
    --daemon        Run in background

Examples:
    $(basename "$0") start
    $(basename "$0") start --port 3000 --daemon
EOF
}

# 使用例
case "${1:-}" in
    -h|--help) show_help; exit 0 ;;
    start)
        case "${2:-}" in
            -h|--help) show_start_help; exit 0 ;;
        esac
        ;;
esac
```

📝 **なぜ重要か**:
- ユーザーが自己解決できる
- ドキュメントを探す手間を削減
- 実用的な例を提供

---

#### 7. プログレスインジケーター

**目的**: ユーザーフィードバック、処理進捗の可視化

❌ **悪い例**（無反応）:
```bash
# 長時間処理でも何も表示しない
for file in *.jpg; do
    convert "$file" "thumb_$file"
done
```

✅ **良い例**（進捗表示）:
```bash
# シンプルなカウンター
process_files() {
    local files=("$@")
    local total="${#files[@]}"
    local current=0

    for file in "${files[@]}"; do
        current=$((current + 1))
        echo "Processing $current/$total: $file" >&2

        convert "$file" "thumb_$file"
    done

    echo "Completed: $total files processed" >&2
}

# プログレスバー
show_progress() {
    local current="$1"
    local total="$2"
    local width=50

    local percent=$((current * 100 / total))
    local filled=$((current * width / total))
    local empty=$((width - filled))

    printf '\r[%s%s] %d%% (%d/%d)' \
        "$(printf '%*s' "$filled" '' | tr ' ' '=')" \
        "$(printf '%*s' "$empty" '')" \
        "$percent" "$current" "$total" >&2
}

# 使用例
files=(*.jpg)
total="${#files[@]}"
for i in "${!files[@]}"; do
    show_progress "$((i + 1))" "$total"
    convert "${files[$i]}" "thumb_${files[$i]}"
done
echo >&2  # 改行
```

📝 **なぜ重要か**:
- 長時間処理でユーザーが待てる
- 処理がフリーズしていないことを確認
- 残り時間の目安を提供

---

#### 8. 装飾の抑制

**目的**: パイプライン連携、CI/CD対応

❌ **悪い例**（常に装飾）:
```bash
# パイプライン時も色付き出力
echo -e "\033[32mSuccess\033[0m"
```

✅ **良い例**（TTY検出）:
```bash
# TTY検出で装飾を制御
setup_colors() {
    if [[ -t 1 ]] && [[ "${NO_COLOR:-}" != "1" ]]; then
        # TTYかつNO_COLOR未設定
        readonly COLOR_RED='\033[0;31m'
        readonly COLOR_GREEN='\033[0;32m'
        readonly COLOR_YELLOW='\033[1;33m'
        readonly COLOR_RESET='\033[0m'
    else
        # パイプまたはNO_COLOR設定時
        readonly COLOR_RED=''
        readonly COLOR_GREEN=''
        readonly COLOR_YELLOW=''
        readonly COLOR_RESET=''
    fi
}

setup_colors

# 使用例
echo -e "${COLOR_GREEN}Success${COLOR_RESET}"
echo -e "${COLOR_RED}Error${COLOR_RESET}"

# 環境変数でも制御可能
# NO_COLOR=1 ./script.sh
```

📝 **なぜ重要か**:
- パイプライン時にANSIコードが混入しない
- CI/CDログが読みやすい
- NO_COLOR環境変数をサポート

---

#### 10. デバッグモード

**目的**: トラブルシューティング支援

❌ **悪い例**（デバッグ機能なし）:
```bash
# エラー時の状態が分からない
process_data "$input"
```

✅ **良い例**（多段階デバッグ）:
```bash
# デバッグレベル
# 0: なし（デフォルト）
# 1: 主要な処理
# 2: 詳細な変数値
# 3: bash -x 相当
DEBUG="${DEBUG:-0}"

debug() {
    local level="$1"
    shift
    if (( DEBUG >= level )); then
        echo "[DEBUG$level] $*" >&2
    fi
}

# bash -x 相当のトレース
if (( DEBUG >= 3 )); then
    set -x
fi

# 使用例
debug 1 "Starting process"
debug 2 "Input value: $input"

process_data "$input"

debug 1 "Process completed"

# 実行:
# DEBUG=1 ./script.sh  # 主要処理のみ
# DEBUG=2 ./script.sh  # 変数値も表示
# DEBUG=3 ./script.sh  # 全コマンド実行をトレース
```

📝 **なぜ重要か**:
- 本番環境でのトラブルシューティングが容易
- 環境変数で簡単に有効化
- 段階的な詳細度で過剰なログを回避

---

#### 12. 設定ファイル対応

**目的**: 再利用性向上、コマンドライン簡素化

❌ **悪い例**（設定ハードコード）:
```bash
# 設定が埋め込まれている
API_URL="https://api.example.com"
TIMEOUT=30
```

✅ **良い例**（階層的な設定読み込み）:
```bash
#!/bin/bash
set -euo pipefail

# デフォルト設定
DEFAULT_API_URL="https://api.example.com"
DEFAULT_TIMEOUT=30
DEFAULT_RETRY=3

# 設定ファイルの優先順位
# 1. コマンドライン引数（最優先）
# 2. 環境変数
# 3. ユーザー設定ファイル (~/.config/myapp/config)
# 4. システム設定ファイル (/etc/myapp/config)
# 5. デフォルト値

load_config() {
    local system_config="/etc/myapp/config"
    local user_config="${XDG_CONFIG_HOME:-$HOME/.config}/myapp/config"

    # システム設定
    if [[ -f "$system_config" ]]; then
        source "$system_config"
    fi

    # ユーザー設定（上書き）
    if [[ -f "$user_config" ]]; then
        source "$user_config"
    fi

    # 環境変数（さらに上書き）
    API_URL="${MYAPP_API_URL:-${API_URL:-$DEFAULT_API_URL}}"
    TIMEOUT="${MYAPP_TIMEOUT:-${TIMEOUT:-$DEFAULT_TIMEOUT}}"
    RETRY="${MYAPP_RETRY:-${RETRY:-$DEFAULT_RETRY}}"
}

# 使用例
load_config

# コマンドライン引数で最終上書き
while [[ $# -gt 0 ]]; do
    case "$1" in
        --api-url) API_URL="$2"; shift 2 ;;
        --timeout) TIMEOUT="$2"; shift 2 ;;
        *) shift ;;
    esac
done

echo "API URL: $API_URL"
echo "Timeout: $TIMEOUT"
```

📝 **なぜ重要か**:
- 環境ごとの設定変更が容易
- チーム内で設定を共有可能
- XDG Base Directory仕様に準拠

---

#### 13. ドライランモード

**目的**: 安全な動作確認、テスト

❌ **悪い例**（実行のみ）:
```bash
# 確認なしで実行
rm -rf "$directory"
```

✅ **良い例**（ドライランモード）:
```bash
# ドライランフラグ
DRY_RUN="${DRY_RUN:-0}"

# ドライラン対応の実行関数
run() {
    if (( DRY_RUN )); then
        echo "[DRY RUN] $*" >&2
    else
        "$@"
    fi
}

# 使用例
run rm -rf "$directory"
run cp file1.txt file2.txt
run curl -X POST "$API_URL" -d "$data"

# 実行:
# DRY_RUN=1 ./script.sh  # 実行せず表示のみ
# ./script.sh            # 実際に実行
```

📝 **なぜ重要か**:
- 破壊的操作の事前確認
- スクリプトの動作テスト
- CI/CDでの検証に利用可能

---

#### 14. バージョン情報

**目的**: トラブルシューティング、互換性確認

❌ **悪い例**（バージョン情報なし）:
```bash
# バージョンが分からない
echo "My App"
```

✅ **良い例**（詳細なバージョン情報）:
```bash
#!/bin/bash

# バージョン情報
readonly VERSION="1.2.3"
readonly BUILD_DATE="2025-01-15"
readonly GIT_COMMIT="${GIT_COMMIT:-unknown}"
readonly GIT_BRANCH="${GIT_BRANCH:-unknown}"

show_version() {
    cat <<EOF
$(basename "$0") version $VERSION

Build Information:
  Date:      $BUILD_DATE
  Commit:    $GIT_COMMIT
  Branch:    $GIT_BRANCH

System Information:
  OS:        $(uname -s)
  Arch:      $(uname -m)
  Bash:      $BASH_VERSION

Copyright (c) 2025 Example Corp.
License: MIT
EOF
}

# 使用例
case "${1:-}" in
    -v|--version|version)
        show_version
        exit 0
        ;;
esac
```

📝 **なぜ重要か**:
- バグレポート時に正確な情報を取得
- 互換性問題の診断が容易
- ビルド情報でトレーサビリティ確保

---

#### 15. ログ出力

**目的**: 監査、トラブルシューティング

❌ **悪い例**（ログなし）:
```bash
# 実行履歴が残らない
process_data "$input"
```

✅ **良い例**（構造化ログ）:
```bash
# ログ設定
LOG_LEVEL="${LOG_LEVEL:-INFO}"  # DEBUG, INFO, WARN, ERROR
LOG_FILE="${LOG_FILE:-}"

# ログレベルの数値化
level_to_num() {
    case "$1" in
        DEBUG) echo 0 ;;
        INFO)  echo 1 ;;
        WARN)  echo 2 ;;
        ERROR) echo 3 ;;
        *)     echo 1 ;;
    esac
}

# ログ関数
log() {
    local level="$1"
    shift
    local message="$*"

    local current_level_num
    local target_level_num
    current_level_num=$(level_to_num "$LOG_LEVEL")
    target_level_num=$(level_to_num "$level")

    # レベルチェック
    if (( target_level_num < current_level_num )); then
        return 0
    fi

    # タイムスタンプ
    local timestamp
    timestamp=$(date +'%Y-%m-%d %H:%M:%S')

    # ログメッセージ
    local log_message="[$timestamp] [$level] $message"

    # 標準エラー出力
    echo "$log_message" >&2

    # ファイル出力
    if [[ -n "$LOG_FILE" ]]; then
        echo "$log_message" >> "$LOG_FILE"
    fi
}

# 使用例
log DEBUG "Starting process with input: $input"
log INFO "Processing data"
log WARN "Deprecated option used"
log ERROR "Failed to connect to database"

# 実行:
# LOG_LEVEL=DEBUG ./script.sh
# LOG_FILE=/var/log/myapp.log ./script.sh
```

📝 **なぜ重要か**:
- 実行履歴の監査が可能
- 問題発生時の原因特定が容易
- 本番環境での動作追跡

---

#### 18. POSIX互換性

**目的**: 移植性向上、幅広い環境対応

❌ **悪い例**（Bash固有機能）:
```bash
#!/bin/bash
# Bash固有の機能を使用
array=(item1 item2)
[[ "$var" == "value" ]]
```

✅ **良い例**（POSIX準拠）:
```bash
#!/bin/sh
# POSIX sh で動作

# Bash配列の代替
set -- item1 item2
for item in "$@"; do
    echo "$item"
done

# [[]] の代替
if [ "$var" = "value" ]; then
    echo "match"
fi

# $()の代替（古いシステム対応）
result=`date +%Y-%m-%d`

# ローカル変数の代替（一部のshでは未サポート）
my_function() {
    # local は使わず、明示的なクリーンアップ
    _temp_var="$1"
    echo "$_temp_var"
    unset _temp_var
}
```

📝 **なぜ重要か**:
- Alpine Linux等のBashがない環境で動作
- 古いUNIXシステムでも実行可能
- CI/CDコンテナイメージのサイズ削減

---

## ⚡ パフォーマンス基準（12項目）

#### 29. 起動時間最適化

**目的**: Git hooks等で重要な起動速度向上

❌ **悪い例**（不要な初期化）:
```bash
#!/bin/bash
# 重い初期化を実行
source /etc/profile
source ~/.bashrc
source ~/.bash_profile

# 不要なコマンド実行
uname -a
hostname
date
```

✅ **良い例**（最小限の初期化）:
```bash
#!/bin/bash
# 必要最小限の設定のみ
set -euo pipefail

# 必要な環境変数のみ設定
export PATH="/usr/local/bin:/usr/bin:/bin"
export LC_ALL=C  # ロケール処理を高速化

# 以下メイン処理
# ...
```

📝 **なぜ重要か**:
- Git hooksは起動時間が重要（開発者体験に直結）
- 不要なコマンド実行は累積で遅延を引き起こす
- `LC_ALL=C`でロケール処理を高速化

---

#### 30. サブシェル回避

**目的**: プロセス生成オーバーヘッド削減

❌ **悪い例**（不要なサブシェル）:
```bash
# パイプで複数のサブシェル生成
result=$(cat file.txt | grep pattern | wc -l)

# コマンド置換で不要なサブシェル
lines=$(wc -l < file.txt)
```

✅ **良い例**（サブシェル最小化）:
```bash
# 1コマンドで処理
result=$(grep -c pattern file.txt)

# リダイレクトで直接読み込み
wc -l < file.txt

# while readループもサブシェル回避
total=0
while IFS= read -r line; do
    total=$((total + 1))
done < file.txt
echo "$total"

# パイプラインの最適化
# 悪い例: cat file | grep | sort
# 良い例: grep pattern file.txt | sort
grep pattern file.txt | sort
```

📝 **なぜ重要か**:
- サブシェル生成はfork()呼び出しで遅い
- 不要な`cat`の使用を避ける（UUOC: Useless Use of Cat）
- パイプラインを短く保つ

---

#### 31. 外部コマンド削減

**目的**: プロセス生成削減、速度向上

❌ **悪い例**（外部コマンド多用）:
```bash
# 外部コマンドを多用
basename=$(basename "$path")
dirname=$(dirname "$path")
extension=$(echo "$filename" | sed 's/.*\.//')
upper=$(echo "$text" | tr 'a-z' 'A-Z')
```

✅ **良い例**（Bash組み込み機能）:
```bash
# Bash組み込みのパラメータ展開
basename="${path##*/}"
dirname="${path%/*}"
extension="${filename##*.}"
filename_without_ext="${filename%.*}"

# 大文字小文字変換（Bash 4.0+）
upper="${text^^}"
lower="${text,,}"

# 文字列置換
result="${text//old/new}"       # すべて置換
result="${text/old/new}"        # 最初の1つのみ置換
result="${text#prefix}"         # 前方一致削除（最短）
result="${text##prefix}"        # 前方一致削除（最長）
result="${text%suffix}"         # 後方一致削除（最短）
result="${text%%suffix}"        # 後方一致削除（最長）
```

📝 **なぜ重要か**:
- 外部コマンド実行は遅い（fork + exec）
- Bash組み込み機能は高速
- ループ内で特に効果が大きい

---

#### 32. ループ内のコマンド実行最適化

**目的**: 大量データ処理の高速化

❌ **悪い例**（ループ内で外部コマンド）:
```bash
# ループごとに外部コマンド実行
for file in *.txt; do
    wc -l "$file"
done

# ループ内でサブシェル
for i in {1..1000}; do
    result=$(date +%s)
    echo "$result"
done
```

✅ **良い例**（一括処理・並列化）:
```bash
# 一括処理
wc -l *.txt

# xargs で並列処理
printf '%s\0' *.txt | xargs -0 -P 4 wc -l

# ループ外でコマンド実行
timestamp=$(date +%s)
for i in {1..1000}; do
    echo "$((timestamp + i))"
done

# GNU Parallel（インストール必要）
parallel wc -l ::: *.txt
```

📝 **なぜ重要か**:
- ループ内の外部コマンドは累積で大幅に遅い
- 並列処理でCPUコアを有効活用
- 一括処理は常に最速

---

#### 33. 文字列処理の最適化

**目的**: 外部コマンド削減、高速化

❌ **悪い例**（sed/awk多用）:
```bash
# 複数回sedを実行
result=$(echo "$input" | sed 's/foo/bar/')
result=$(echo "$result" | sed 's/baz/qux/')
result=$(echo "$result" | sed 's/old/new/')
```

✅ **良い例**（Bash組み込み）:
```bash
# Bash組み込みのパラメータ展開
result="$input"
result="${result//foo/bar}"
result="${result//baz/qux}"
result="${result//old/new}"

# 複数置換が必要な場合は1回のsed
result=$(sed 's/foo/bar/g; s/baz/qux/g; s/old/new/g' <<< "$input")

# 正規表現マッチ
if [[ "$input" =~ ^[0-9]+$ ]]; then
    echo "数値のみ"
fi

# パターン抽出
if [[ "$email" =~ ([^@]+)@([^@]+) ]]; then
    user="${BASH_REMATCH[1]}"
    domain="${BASH_REMATCH[2]}"
fi
```

📝 **なぜ重要か**:
- `echo | sed`は2プロセス生成で遅い
- Bash組み込み機能は単一プロセス
- パイプライン削減で高速化

---

#### 34. ファイル読み込みの最適化

**目的**: I/O効率化、外部コマンド削減

❌ **悪い例**（行ごとに外部コマンド）:
```bash
# 各行でgrepを実行
while IFS= read -r line; do
    echo "$line" | grep pattern
done < file.txt

# catで読み込んでからgrep
cat file.txt | grep pattern
```

✅ **良い例**（一括処理）:
```bash
# grepで直接処理
grep pattern file.txt

# 複数条件の場合
grep -E 'pattern1|pattern2' file.txt

# while readが必要な場合
while IFS= read -r line; do
    # Bash組み込み機能で処理
    if [[ "$line" =~ pattern ]]; then
        echo "$line"
    fi
done < file.txt

# mapfile/readarrayで配列に一括読み込み（Bash 4.0+）
mapfile -t lines < file.txt
for line in "${lines[@]}"; do
    process "$line"
done
```

📝 **なぜ重要か**:
- 行ごとの外部コマンド実行は非常に遅い
- grepは最適化されたC実装で高速
- UUOC（Useless Use of Cat）を避ける

---

#### 35. 条件分岐の最適化

**目的**: 重い処理の重複実行回避

❌ **悪い例**（重い処理を毎回実行）:
```bash
# 重いコマンドを条件内で実行
if [[ $(complex_command) == "value" ]]; then
    action1
fi

if [[ $(complex_command) == "value" ]]; then
    action2
fi
```

✅ **良い例**（結果をキャッシュ）:
```bash
# 1回実行して結果をキャッシュ
result=$(complex_command)

if [[ "$result" == "value" ]]; then
    action1
fi

if [[ "$result" == "value" ]]; then
    action2
fi

# 遅延評価（必要な場合のみ実行）
if [[ "$quick_check" == "pass" ]] && [[ "$(heavy_check)" == "pass" ]]; then
    # quick_checkが失敗ならheavy_checkは実行されない
    action
fi
```

📝 **なぜ重要か**:
- 重い処理の重複実行を回避
- Bash の `&&` と `||` は短絡評価
- キャッシュで大幅な高速化

---

#### 36. 配列処理の活用

**目的**: 安全性とパフォーマンス向上

❌ **悪い例**（文字列で処理）:
```bash
# 空白区切りの文字列（危険）
files="file1 file2 file3"
for file in $files; do  # 引用符なし、空白で分割
    process "$file"
done

# ファイル名に空白があると壊れる
files="file with spaces.txt other.txt"
for file in $files; do
    # file="file", "with", "spaces.txt" と分割される
    process "$file"
done
```

✅ **良い例**（配列使用）:
```bash
# 配列で安全に処理
files=(file1 file2 file3)
for file in "${files[@]}"; do
    process "$file"
done

# 空白を含むファイル名も安全
files=("file with spaces.txt" "other.txt")
for file in "${files[@]}"; do
    process "$file"  # 正しく処理される
done

# コマンド出力を配列に格納
mapfile -t files < <(find . -name "*.txt")
for file in "${files[@]}"; do
    process "$file"
done

# 配列への追加
files=()
while IFS= read -r file; do
    files+=("$file")
done < <(find . -name "*.txt")
```

📝 **なぜ重要か**:
- 空白・特殊文字を含むファイル名を安全に処理
- 文字列分割の曖昧性を排除
- コードの可読性向上

---

#### 37. プロセス置換の活用

**目的**: 一時ファイル削減、パフォーマンス向上

❌ **悪い例**（一時ファイル使用）:
```bash
# 一時ファイルを作成
grep pattern file1.txt > /tmp/result1.$$
grep pattern file2.txt > /tmp/result2.$$
diff /tmp/result1.$$ /tmp/result2.$$
rm /tmp/result1.$$ /tmp/result2.$$

# 複数ステップで一時ファイル
sort file.txt > /tmp/sorted.$$
uniq /tmp/sorted.$$ > /tmp/unique.$$
wc -l /tmp/unique.$$
rm /tmp/sorted.$$ /tmp/unique.$$
```

✅ **良い例**（プロセス置換）:
```bash
# プロセス置換で一時ファイル不要
diff <(grep pattern file1.txt) <(grep pattern file2.txt)

# パイプラインで一時ファイル不要
sort file.txt | uniq | wc -l

# 複数入力の処理
paste <(cut -f1 file1.txt) <(cut -f2 file2.txt)

# while readとプロセス置換
while IFS= read -r line; do
    process "$line"
done < <(complex_command)
```

📝 **なぜ重要か**:
- ディスクI/Oを削減
- クリーンアップ不要
- パイプのような動作でメモリ効率的

---

#### 38. 並列処理の活用

**目的**: マルチコア活用、高速化

❌ **悪い例**（逐次処理）:
```bash
# 1つずつ処理（遅い）
for url in "${urls[@]}"; do
    curl -O "$url"
done

for file in *.mp4; do
    ffmpeg -i "$file" "compressed_$file"
done
```

✅ **良い例**（並列処理）:
```bash
# xargs で並列処理（シンプル）
printf '%s\n' "${urls[@]}" | xargs -P 4 -I {} curl -O {}

# GNU Parallel（高機能）
parallel -j 4 curl -O ::: "${urls[@]}"

# バックグラウンドジョブ（制御が必要な場合）
max_jobs=4
job_count=0

for file in *.mp4; do
    # バックグラウンド実行
    ffmpeg -i "$file" "compressed_$file" &

    job_count=$((job_count + 1))

    # 最大並列数に達したら待機
    if (( job_count >= max_jobs )); then
        wait -n  # 1つのジョブが終わるまで待機
        job_count=$((job_count - 1))
    fi
done

# すべてのジョブ完了を待機
wait
```

📝 **なぜ重要か**:
- CPUコアを有効活用
- I/O待ち時間を並列化で隠蔽
- 大量データ処理で劇的な高速化

---

#### 39. コマンド実行回数の削減

**目的**: 不要なコマンド実行の排除

❌ **悪い例**（重複実行）:
```bash
# 同じコマンドを複数回実行
if command -v git &>/dev/null; then
    git_version=$(git --version)
fi

if command -v git &>/dev/null; then
    git status
fi

if command -v git &>/dev/null; then
    git diff
fi
```

✅ **良い例**（1回のみ実行）:
```bash
# 結果をキャッシュ
has_git=false
if command -v git &>/dev/null; then
    has_git=true
fi

if [[ "$has_git" == "true" ]]; then
    git_version=$(git --version)
    git status
    git diff
fi

# 関数でキャッシュ
_git_available=""
has_git() {
    if [[ -z "$_git_available" ]]; then
        if command -v git &>/dev/null; then
            _git_available="yes"
        else
            _git_available="no"
        fi
    fi
    [[ "$_git_available" == "yes" ]]
}

# 使用例
if has_git; then
    git status
fi

if has_git; then
    git diff
fi
```

📝 **なぜ重要か**:
- `command -v`の繰り返し実行は無駄
- 重い処理のキャッシュで大幅高速化
- 関数を使った遅延評価パターン

---

#### 40. メモリ効率的な処理

**目的**: メモリ枯渇防止、大容量データ処理

❌ **悪い例**（全データをメモリに読み込み）:
```bash
# 巨大ファイルを変数に読み込み（メモリ枯渇）
data=$(cat huge_file.log)
echo "$data" | grep ERROR

# 配列に全行読み込み
mapfile -t lines < huge_file.log
for line in "${lines[@]}"; do
    process "$line"
done
```

✅ **良い例**（ストリーム処理）:
```bash
# ストリーム処理（メモリ効率的）
grep ERROR huge_file.log

# パイプラインで処理
cat huge_file.log | grep ERROR | sort | uniq -c

# while readでストリーム処理
while IFS= read -r line; do
    if [[ "$line" =~ ERROR ]]; then
        process "$line"
    fi
done < huge_file.log

# head/tailで必要な部分のみ
head -n 1000 huge_file.log | process

# split で分割処理
split -l 10000 huge_file.log chunk_
for chunk in chunk_*; do
    process "$chunk" &
done
wait
```

📝 **なぜ重要か**:
- 大容量ファイルでメモリ枯渇を防止
- ストリーム処理は定数メモリ
- パイプラインは各段階が並列動作

---

## 🛠️ 保守性基準（12項目）

#### 41. コード構造化（関数分割）

**目的**: 可読性向上、再利用性、テスト容易性

❌ **悪い例**（巨大な単一スクリプト）:
```bash
#!/bin/bash
# 500行の単一スクリプト
set -euo pipefail

# 引数解析
while [[ $# -gt 0 ]]; do
    case "$1" in
        --option1) option1="$2"; shift 2 ;;
        --option2) option2="$2"; shift 2 ;;
        *) echo "Unknown option: $1" >&2; exit 1 ;;
    esac
done

# 入力検証
if [[ -z "${option1:-}" ]]; then
    echo "Error: --option1 required" >&2
    exit 1
fi

# データ処理
# ... 200行のコード ...

# 出力
# ... 100行のコード ...
```

✅ **良い例**（関数分割）:
```bash
#!/bin/bash
set -euo pipefail

# ========================================
# Configuration
# ========================================
readonly SCRIPT_NAME="$(basename "$0")"
readonly VERSION="1.0.0"

# ========================================
# Functions
# ========================================

show_usage() {
    cat <<EOF
Usage: $SCRIPT_NAME [OPTIONS] COMMAND

Options:
    -h, --help      Show this help
    -v, --verbose   Verbose output
EOF
}

parse_arguments() {
    while [[ $# -gt 0 ]]; do
        case "$1" in
            -h|--help) show_usage; exit 0 ;;
            -v|--verbose) VERBOSE=1; shift ;;
            *) error "Unknown option: $1"; exit 1 ;;
        esac
    done
}

validate_input() {
    local input="$1"

    if [[ -z "$input" ]]; then
        error "Input cannot be empty"
        return 1
    fi

    return 0
}

process_data() {
    local input="$1"
    # 処理ロジック
    echo "processed: $input"
}

cleanup() {
    # クリーンアップ処理
    rm -f "${tmpfile:-}"
}

error() {
    echo "Error: $*" >&2
}

# ========================================
# Main
# ========================================

main() {
    parse_arguments "$@"

    local input="${1:-}"
    if ! validate_input "$input"; then
        exit 1
    fi

    trap cleanup EXIT

    local result
    result=$(process_data "$input")

    echo "$result"
}

# スクリプトとして実行された場合のみmain実行
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
```

📝 **なぜ重要か**:
- 各関数が単一責任を持つ
- テストが容易（関数単位で実行可能）
- 可読性が劇的に向上

---

#### 42. 定数の明示的定義

**目的**: マジックナンバー排除、変更容易性

❌ **悪い例**（マジックナンバー）:
```bash
# 意味不明な数値
if (( count > 100 )); then
    error "Too many items"
fi

sleep 30

timeout 300 long_running_command
```

✅ **良い例**（定数定義）:
```bash
# 定数をスクリプト冒頭で定義
readonly MAX_ITEMS=100
readonly RETRY_DELAY_SECONDS=30
readonly COMMAND_TIMEOUT_SECONDS=300

readonly CONFIG_DIR="${XDG_CONFIG_HOME:-$HOME/.config}/myapp"
readonly CACHE_DIR="${XDG_CACHE_HOME:-$HOME/.cache}/myapp"
readonly LOG_FILE="$CACHE_DIR/myapp.log"

readonly API_BASE_URL="https://api.example.com"
readonly API_VERSION="v1"
readonly API_ENDPOINT="$API_BASE_URL/$API_VERSION"

# 使用例
if (( count > MAX_ITEMS )); then
    error "Too many items (max: $MAX_ITEMS)"
fi

sleep "$RETRY_DELAY_SECONDS"

timeout "$COMMAND_TIMEOUT_SECONDS" long_running_command
```

📝 **なぜ重要か**:
- 定数の意味が明確
- 変更時に1箇所のみ修正
- `readonly`で誤った上書きを防止

---

#### 43. グローバル変数の最小化

**目的**: 予期しない副作用防止、デバッグ容易性

❌ **悪い例**（グローバル変数多用）:
```bash
# グローバル変数に依存
result=""
status=0
temp_data=""

process_data() {
    result="processed"
    status=1
    temp_data="temporary"
}

# 別の関数で上書き
another_function() {
    result="overwritten"  # 意図せず上書き
}
```

✅ **良い例**（ローカル変数 + 戻り値）:
```bash
# ローカル変数を使用
process_data() {
    local input="$1"
    local result="processed: $input"

    # 標準出力で戻り値
    echo "$result"

    # 終了コードでステータス
    return 0
}

# 使用例
if result=$(process_data "$input"); then
    echo "Success: $result"
else
    echo "Failed with status: $?"
fi

# 必要なグローバル変数は明示的に定義
declare -g GLOBAL_CONFIG=""

# 関数内でグローバル変数を変更する場合は明示
update_global_config() {
    # グローバル変数への代入を明示
    GLOBAL_CONFIG="$1"
}
```

📝 **なぜ重要か**:
- 関数の独立性を確保
- デバッグが容易（スコープが明確）
- 並列実行時の競合を回避

---

#### 44. 自己文書化コード

**目的**: コメント不要なコード、可読性向上

❌ **悪い例**（曖昧な命名）:
```bash
# 変数名が意味不明
f="$1"
p="$2"
t="$3"

# 処理内容が不明
do_it() {
    local x="$1"
    local y="$2"
    echo "$((x * 2 + y))"
}
```

✅ **良い例**（自己文書化）:
```bash
# 明確な変数名
input_file="$1"
port_number="$2"
timeout_seconds="$3"

# 関数名で意図を表現
calculate_total_with_tax() {
    local subtotal="$1"
    local tax_rate="$2"
    local total=$((subtotal + subtotal * tax_rate / 100))
    echo "$total"
}

# ブール値を明示
is_file_readable() {
    local file="$1"
    [[ -r "$file" ]]
}

# 述語関数で条件を表現
has_valid_extension() {
    local filename="$1"
    [[ "$filename" =~ \.(jpg|png|gif)$ ]]
}

# 使用例（コメント不要）
if is_file_readable "$config_file"; then
    source "$config_file"
fi

if has_valid_extension "$filename"; then
    process_image "$filename"
fi
```

📝 **なぜ重要か**:
- コメントが不要になる
- コードの意図が即座に理解できる
- 関数名がドキュメント

---

#### 45. エラーハンドリングパターンの統一

**目的**: 一貫性、保守性向上

❌ **悪い例**（不統一なエラー処理）:
```bash
# バラバラなエラーハンドリング
if [[ ! -f "$file" ]]; then
    echo "Error: file not found" >&2
    exit 1
fi

[[ -r "$file" ]] || { echo "Cannot read file" >&2; return 1; }

if ! process_data "$file"; then
    printf "Failed\n" >&2
    exit 2
fi
```

✅ **良い例**（統一的なエラーハンドリング）:
```bash
#!/bin/bash
set -euo pipefail

# ========================================
# Error Handling
# ========================================

# エラー出力（継続）
error() {
    echo "Error: $*" >&2
    return 1
}

# 致命的エラー（終了）
die() {
    local exit_code="${1:-1}"
    shift
    echo "Fatal: $*" >&2
    exit "$exit_code"
}

# 警告出力
warn() {
    echo "Warning: $*" >&2
}

# デバッグ出力
debug() {
    if [[ "${DEBUG:-0}" == "1" ]]; then
        echo "[DEBUG] $*" >&2
    fi
}

# ========================================
# Usage Examples
# ========================================

validate_file() {
    local file="$1"

    [[ -f "$file" ]] || error "File not found: $file"
    [[ -r "$file" ]] || error "Permission denied: $file"
}

# 使用例
if ! validate_file "$config_file"; then
    die 1 "Configuration file validation failed"
fi

debug "Loading configuration from: $config_file"

if ! data=$(process_file "$config_file"); then
    warn "Failed to process file, using defaults"
    data="$default_data"
fi
```

📝 **なぜ重要か**:
- エラーハンドリングが一貫
- 標準エラー出力に統一
- 重要度（error/warn/debug）を明確化

---

#### 46. テスタビリティ（単体テスト対応）

**目的**: 品質保証、リグレッション防止

❌ **悪い例**（テスト不可能）:
```bash
#!/bin/bash
# メイン処理が直接実行される
set -euo pipefail

if [[ ! -f "$1" ]]; then
    echo "Error" >&2
    exit 1
fi

cat "$1" | grep pattern
```

✅ **良い例**（テスト可能な構造）:
```bash
#!/bin/bash
# main.sh

set -euo pipefail

# ========================================
# Testable Functions
# ========================================

validate_input() {
    local input="$1"

    if [[ -z "$input" ]]; then
        echo "Input cannot be empty" >&2
        return 1
    fi

    if [[ ! "$input" =~ ^[0-9]+$ ]]; then
        echo "Input must be numeric" >&2
        return 1
    fi

    return 0
}

process_data() {
    local input="$1"
    echo "Processed: $input"
}

# ========================================
# Main Application
# ========================================

run_application() {
    local input="${1:-}"

    if ! validate_input "$input"; then
        return 1
    fi

    process_data "$input"
}

# スクリプトとして実行された場合のみ
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    run_application "$@"
fi
```

```bash
#!/bin/bash
# test.sh - テストスクリプト

source "$(dirname "$0")/main.sh"

# テスト結果カウンター
tests_passed=0
tests_failed=0

# テストヘルパー
assert_success() {
    local description="$1"
    shift

    if "$@" &>/dev/null; then
        echo "✓ $description"
        tests_passed=$((tests_passed + 1))
    else
        echo "✗ $description"
        tests_failed=$((tests_failed + 1))
    fi
}

assert_failure() {
    local description="$1"
    shift

    if ! "$@" &>/dev/null; then
        echo "✓ $description"
        tests_passed=$((tests_passed + 1))
    else
        echo "✗ $description"
        tests_failed=$((tests_failed + 1))
    fi
}

# テストケース
echo "Running tests..."

assert_success "Empty input should fail" \
    test "$(validate_input '' 2>&1 || true)" != ""

assert_success "Non-numeric input should fail" \
    validate_input "abc" 2>/dev/null

assert_success "Valid numeric input should pass" \
    validate_input "123"

# 結果表示
echo ""
echo "Tests passed: $tests_passed"
echo "Tests failed: $tests_failed"

if (( tests_failed > 0 )); then
    exit 1
fi
```

📝 **なぜ重要か**:
- 関数単位でテスト可能
- リグレッションを早期発見
- リファクタリングが安全

---

#### 47. 設定と実装の分離

**目的**: 環境依存の排除、再利用性向上

❌ **悪い例**（設定が埋め込まれている）:
```bash
# ハードコードされた設定
api_url="https://api.example.com"
timeout=30
max_retries=3

curl --max-time 30 "https://api.example.com/data"
```

✅ **良い例**（設定を分離）:
```bash
#!/bin/bash
# main.sh

set -euo pipefail

# ========================================
# Default Configuration
# ========================================

# デフォルト値を定義
readonly DEFAULT_API_URL="https://api.example.com"
readonly DEFAULT_TIMEOUT=30
readonly DEFAULT_MAX_RETRIES=3
readonly DEFAULT_LOG_LEVEL="INFO"

# ========================================
# Configuration Loading
# ========================================

load_configuration() {
    # 1. デフォルト値
    API_URL="$DEFAULT_API_URL"
    TIMEOUT="$DEFAULT_TIMEOUT"
    MAX_RETRIES="$DEFAULT_MAX_RETRIES"
    LOG_LEVEL="$DEFAULT_LOG_LEVEL"

    # 2. システム設定ファイル
    local system_config="/etc/myapp/config"
    if [[ -f "$system_config" ]]; then
        source "$system_config"
    fi

    # 3. ユーザー設定ファイル
    local user_config="${XDG_CONFIG_HOME:-$HOME/.config}/myapp/config"
    if [[ -f "$user_config" ]]; then
        source "$user_config"
    fi

    # 4. 環境変数（最優先）
    API_URL="${MYAPP_API_URL:-$API_URL}"
    TIMEOUT="${MYAPP_TIMEOUT:-$TIMEOUT}"
    MAX_RETRIES="${MYAPP_MAX_RETRIES:-$MAX_RETRIES}"
    LOG_LEVEL="${MYAPP_LOG_LEVEL:-$LOG_LEVEL}"
}

# ========================================
# Main
# ========================================

main() {
    load_configuration

    # 設定を使用
    curl --max-time "$TIMEOUT" "$API_URL/data"
}

if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
```

```bash
# config - 設定ファイル例
API_URL="https://staging-api.example.com"
TIMEOUT=60
MAX_RETRIES=5
LOG_LEVEL="DEBUG"
```

📝 **なぜ重要か**:
- 環境ごとの設定変更が容易
- コードを変更せず動作を変更
- 環境変数で柔軟に上書き可能

---

#### 48. ヘッダーコメント（スクリプト情報）

**目的**: スクリプトの目的・使い方を明確化

❌ **悪い例**（情報不足）:
```bash
#!/bin/bash
set -euo pipefail

# 何をするスクリプトか不明
# 使い方も不明
```

✅ **良い例**（詳細なヘッダー）:
```bash
#!/bin/bash
#
# ========================================
# backup-tool.sh
# ========================================
#
# Description:
#   Database backup automation script with compression and AWS S3 upload.
#   Performs incremental backups and retains last 7 days of backups.
#
# Author: DevOps Team <devops@example.com>
# Created: 2025-01-01
# Version: 1.2.3
# License: MIT
#
# ========================================
# Usage
# ========================================
#
# backup-tool.sh [OPTIONS] <database-name>
#
# Options:
#   -h, --help          Show this help message
#   -v, --verbose       Enable verbose output
#   --incremental       Perform incremental backup (default)
#   --full              Perform full backup
#   --s3-bucket BUCKET  Upload to specified S3 bucket
#   --retention DAYS    Retention period (default: 7 days)
#
# Examples:
#   # Full backup with upload to S3
#   backup-tool.sh --full --s3-bucket my-backups production-db
#
#   # Incremental backup with verbose output
#   backup-tool.sh --verbose --incremental staging-db
#
# ========================================
# Dependencies
# ========================================
#
# Required:
#   - mysqldump (>= 5.7)
#   - gzip
#   - aws-cli (>= 2.0) - for S3 upload
#
# Optional:
#   - pigz - for faster compression
#
# Install on Ubuntu:
#   sudo apt install mysql-client gzip awscli
#
# ========================================
# Environment Variables
# ========================================
#
# AWS_PROFILE          AWS profile to use (default: default)
# BACKUP_DIR           Backup directory (default: /var/backups/mysql)
# MYSQL_HOST           MySQL host (default: localhost)
# MYSQL_USER           MySQL user (default: backup)
# MYSQL_PASSWORD       MySQL password (required)
#
# ========================================
# Exit Codes
# ========================================
#
# 0   Success
# 1   Usage error
# 2   Database connection failed
# 3   Backup failed
# 4   S3 upload failed
#
# ========================================

set -euo pipefail

readonly VERSION="1.2.3"
readonly BUILD_DATE="2025-01-15"

# ... スクリプト本体 ...
```

📝 **なぜ重要か**:
- 初見でスクリプトの目的を理解
- 使い方の例を提供
- 依存関係を明示

---

#### 49. コメントのベストプラクティス

**目的**: 保守性向上、意図の明確化

❌ **悪い例**（What をコメント）:
```bash
# ユーザー名を取得
username=$(whoami)

# ファイルを削除
rm "$file"

# ループを回す
for i in {1..10}; do
    echo "$i"
done
```

✅ **良い例**（Why をコメント）:
```bash
# sudo実行時でも実際のユーザー名を取得するため
# SUDO_USERが設定されていればそれを、なければwhoamiを使用
username="${SUDO_USER:-$(whoami)}"

# 一時ファイルは処理完了後に不要なため削除
# trapで確実にクリーンアップされるが、明示的に削除
rm "$tmpfile"

# 複雑なロジックには詳細な説明
# 以下のループは、最大10回までリトライを試みる
# 各リトライ間には指数バックオフ（2^n秒）の待機時間を設ける
# これにより、一時的なネットワークエラーから回復する機会を与える
for attempt in {1..10}; do
    if curl --fail "$url"; then
        break
    fi

    # 指数バックオフ: 2, 4, 8, 16, ... 秒
    local wait_time=$((2 ** attempt))
    sleep "$wait_time"
done

# TODOコメントには担当者と期限を明記
# TODO(username): 2025-02-01までにエラーハンドリングを改善
# - リトライロジックを関数化
# - タイムアウト時間を設定可能に

# HACKコメントには理由を記載
# HACK: curlのバグ回避のため一時的にこの方法を使用
# https://github.com/curl/curl/issues/12345
# curl 8.0.0 でバグ修正予定
workaround_curl_bug

# FIXMEには既知の問題を記載
# FIXME: 大容量ファイルでメモリ不足が発生する
# ストリーム処理に変更する必要あり
data=$(cat large_file.txt)
```

📝 **なぜ重要か**:
- コードの「なぜ」を説明
- 複雑なロジックの理解を助ける
- TODO/HACK/FIXMEで課題を追跡

---

#### 50. バージョン管理とリリース管理

**目的**: トレーサビリティ、デバッグ支援

❌ **悪い例**（バージョン情報なし）:
```bash
#!/bin/bash
# バージョン情報なし
echo "My Script"
```

✅ **良い例**（詳細なバージョン管理）:
```bash
#!/bin/bash
#
# Version: 1.2.3
# Build Date: 2025-01-15
#

set -euo pipefail

# ========================================
# Version Information
# ========================================

readonly VERSION="1.2.3"
readonly BUILD_DATE="2025-01-15"

# Gitビルド時に自動設定（CI/CDで注入）
readonly GIT_COMMIT="${GIT_COMMIT:-unknown}"
readonly GIT_BRANCH="${GIT_BRANCH:-unknown}"
readonly GIT_TAG="${GIT_TAG:-}"

# ========================================
# Version Display
# ========================================

show_version() {
    cat <<EOF
$(basename "$0") version $VERSION

Build Information:
  Date:      $BUILD_DATE
  Commit:    $GIT_COMMIT
  Branch:    $GIT_BRANCH
  Tag:       ${GIT_TAG:-none}

System Information:
  OS:        $(uname -s)
  Arch:      $(uname -m)
  Kernel:    $(uname -r)
  Shell:     Bash $BASH_VERSION

Runtime Information:
  User:      $(whoami)
  Hostname:  $(hostname)
  Working:   $(pwd)

Copyright (c) 2025 Example Corp.
License: MIT License
Repository: https://github.com/example/myapp
EOF
}

# バージョン互換性チェック
check_version_compatibility() {
    local min_bash_version="4.0"

    if (( BASH_VERSINFO[0] < 4 )); then
        echo "Error: Bash $min_bash_version or higher required" >&2
        echo "Current: $BASH_VERSION" >&2
        exit 1
    fi
}

# ========================================
# Main
# ========================================

case "${1:-}" in
    -v|--version|version)
        show_version
        exit 0
        ;;
esac

check_version_compatibility

# ... メイン処理 ...
```

```bash
# Makefile または build.sh でバージョン情報を埋め込み
#!/bin/bash
# build.sh

GIT_COMMIT=$(git rev-parse --short HEAD)
GIT_BRANCH=$(git rev-parse --abbrev-ref HEAD)
GIT_TAG=$(git describe --tags --exact-match 2>/dev/null || echo "")

# スクリプトにバージョン情報を埋め込み
sed -i "s/GIT_COMMIT:-unknown/GIT_COMMIT:-$GIT_COMMIT/" main.sh
sed -i "s/GIT_BRANCH:-unknown/GIT_BRANCH:-$GIT_BRANCH/" main.sh
sed -i "s/GIT_TAG:-/GIT_TAG:-$GIT_TAG/" main.sh
```

📝 **なぜ重要か**:
- バグレポート時に正確なバージョンを特定
- CI/CDでビルド情報を追跡
- 互換性チェックで問題を早期発見

---

#### 51. ShellCheck対応

**目的**: バグ防止、ベストプラクティス遵守

❌ **悪い例**（ShellCheck警告多数）:
```bash
# SC2086: 引用符なし変数展開
files=$@
for file in $files; do
    cat $file
done

# SC2034: 未使用変数
unused_var="value"

# SC2155: declare と代入を同時実行
declare result=$(command)
```

✅ **良い例**（ShellCheck対応）:
```bash
#!/bin/bash
# ShellCheckを活用

# 引用符で変数を保護
files=("$@")
for file in "${files[@]}"; do
    cat "$file"
done

# 意図的に未使用の場合は明示
# shellcheck disable=SC2034
reserved_for_future_use="value"

# declare と代入を分離
declare result
result=$(command)

# 意図的なワードスプリッティングの場合
# shellcheck disable=SC2086
intentional_word_splitting() {
    local options="-v -x -a"
    # shellcheck disable=SC2086
    command $options  # ワードスプリッティング意図的
}

# より良い方法: 配列使用
better_approach() {
    local options=(-v -x -a)
    command "${options[@]}"
}

# ShellCheckディレクティブの使用例
# shellcheck source=/path/to/library.sh
source "$(dirname "$0")/library.sh"

# 動的source（ShellCheckで検証不可）
# shellcheck disable=SC1090
source "$DYNAMIC_PATH"
```

```bash
# .shellcheckrc - プロジェクト設定
# 使用するシェルを指定
shell=bash

# 除外する警告
disable=SC2034  # 未使用変数（設定ファイルで使用される変数）

# 外部ファイルのsourceパス
source-path=SCRIPTDIR
```

📝 **なぜ重要か**:
- 一般的なバグを事前検出
- ベストプラクティスを学習
- CI/CDで自動チェック可能

---

#### 52. デバッグ支援機能

**目的**: トラブルシューティング効率化

❌ **悪い例**（デバッグ機能なし）:
```bash
# エラー発生時の状態が不明
process_data "$input"
result=$?
if (( result != 0 )); then
    echo "Failed" >&2
    exit 1
fi
```

✅ **良い例**（充実したデバッグ機能）:
```bash
#!/bin/bash
set -euo pipefail

# ========================================
# Debug Configuration
# ========================================

# デバッグレベル
# 0: なし（本番環境）
# 1: エラーのみ
# 2: 警告とエラー
# 3: 情報、警告、エラー
# 4: すべて（変数値含む）
# 5: bash -x 相当のトレース
DEBUG="${DEBUG:-0}"

# ========================================
# Debug Functions
# ========================================

# ログレベル別の出力
debug() {
    local level="$1"
    shift
    if (( DEBUG >= level )); then
        echo "[DEBUG$level] $(date +'%H:%M:%S') $*" >&2
    fi
}

# 変数の値をダンプ
dump_var() {
    local var_name="$1"
    local var_value="${!var_name:-}"
    debug 4 "$var_name = '$var_value'"
}

# 配列の値をダンプ
dump_array() {
    local array_name="$1"
    local -n array_ref="$array_name"
    debug 4 "$array_name = (${array_ref[*]})"
}

# 関数の開始・終了をトレース
trace_function() {
    if (( DEBUG >= 3 )); then
        echo "[TRACE] $(date +'%H:%M:%S') ${FUNCNAME[1]}() called" >&2
    fi
}

# エラー発生時のスタックトレース
print_stacktrace() {
    local frame=0
    echo "Stack trace:" >&2
    while caller $frame >&2; do
        frame=$((frame + 1))
    done
}

# エラートラップ
error_handler() {
    local line="$1"
    echo "Error occurred in script at line: $line" >&2
    print_stacktrace
}

# ========================================
# Debug Setup
# ========================================

# bash -x 相当のトレース（DEBUG=5）
if (( DEBUG >= 5 )); then
    set -x
    PS4='+(${BASH_SOURCE}:${LINENO}): ${FUNCNAME[0]:+${FUNCNAME[0]}(): }'
fi

# エラー時にスタックトレース（DEBUG >= 1）
if (( DEBUG >= 1 )); then
    trap 'error_handler $LINENO' ERR
fi

# ========================================
# Example Usage
# ========================================

process_data() {
    trace_function

    local input="$1"
    dump_var input

    debug 3 "Starting data processing"

    local result="processed: $input"
    dump_var result

    debug 3 "Data processing completed"

    echo "$result"
}

main() {
    trace_function

    local input="${1:-default}"

    debug 2 "Application started with input: $input"

    local result
    if ! result=$(process_data "$input"); then
        debug 1 "process_data failed"
        return 1
    fi

    debug 2 "Result: $result"

    echo "$result"
}

# 実行例:
# DEBUG=0 ./script.sh            # 通常実行
# DEBUG=1 ./script.sh            # エラーのみ
# DEBUG=3 ./script.sh            # 詳細ログ
# DEBUG=4 ./script.sh            # 変数値含む
# DEBUG=5 ./script.sh            # 完全トレース
```

📝 **なぜ重要か**:
- 段階的なデバッグレベル
- スタックトレースで問題箇所を特定
- 本番環境でも環境変数で有効化可能

---

## ✅ 実装チェックリスト

Claude CodeがShell CLI実装時に確認する項目:

### 🔴 必須（Critical）

#### セキュリティ
- [ ] 3. エラーメッセージに機密情報を含まない
- [ ] 4. 破壊的変更前に確認プロンプト
- [ ] 5. 数値オプションの範囲検証
- [ ] 6. 選択肢のホワイトリスト検証
- [ ] 19. パストラバーサル対策（basename使用）
- [ ] 20. mktemp で一時ファイル作成
- [ ] 21. eval 使用禁止、引用符必須
- [ ] 24. パスワードは read -s で非表示入力
- [ ] 25. umask 077 で機密ファイル保護

#### 基本品質
- [ ] スクリプト冒頭に `set -euo pipefail`
- [ ] すべての変数を引用符で囲む: `"$var"`
- [ ] 9. 終了コードの一貫性（定数定義）
- [ ] 16. trap でクリーンアップ処理
- [ ] 17. 依存コマンドの事前チェック

#### 保守性
- [ ] 41. 関数分割（main関数パターン）
- [ ] 42. マジックナンバーを定数化
- [ ] 45. エラーハンドリング関数の統一

### 🟡 推奨（Important）

#### セキュリティ
- [ ] 22. PATH 汚染防止
- [ ] 23. sudo 使用最小化
- [ ] 26. コマンド置換は信頼できるコマンドのみ
- [ ] 27. シグナルハンドリング（INT, TERM）

#### ユーザビリティ
- [ ] 2. サブコマンドヘルプ
- [ ] 8. TTY検出で装飾を制御
- [ ] 10. デバッグモード（DEBUG環境変数）
- [ ] 13. ドライランモード
- [ ] 14. バージョン情報表示

#### パフォーマンス
- [ ] 29. 起動時間最適化（不要な初期化削減）
- [ ] 30. サブシェル回避
- [ ] 31. 外部コマンド削減（Bash組み込み機能）
- [ ] 32. ループ内のコマンド実行最適化

#### 保守性
- [ ] 43. グローバル変数最小化
- [ ] 44. 自己文書化コード（明確な命名）
- [ ] 47. 設定と実装の分離
- [ ] 48. ヘッダーコメント（スクリプト情報）
- [ ] 51. ShellCheck 対応

### 🟢 任意（Nice to have）

#### ユーザビリティ
- [ ] 1. Tab補完スクリプト
- [ ] 7. プログレスインジケーター
- [ ] 12. 設定ファイル対応
- [ ] 15. 構造化ログ出力
- [ ] 18. POSIX互換性（移植性が重要な場合）

#### パフォーマンス
- [ ] 33. 文字列処理最適化
- [ ] 34. ファイル読み込み最適化
- [ ] 35. 条件分岐最適化（結果キャッシュ）
- [ ] 36. 配列処理の活用
- [ ] 37. プロセス置換の活用
- [ ] 38. 並列処理（xargs -P, GNU Parallel）
- [ ] 39. コマンド実行回数削減
- [ ] 40. メモリ効率的な処理

#### 保守性
- [ ] 46. テスタビリティ（source可能な構造）
- [ ] 49. Why コメント（What ではなく）
- [ ] 50. バージョン管理・ビルド情報
- [ ] 52. デバッグ支援機能

---

## 📚 参考資料

### 公式ドキュメント
- **Bash Reference Manual**: https://www.gnu.org/software/bash/manual/
- **POSIX Shell Standard**: https://pubs.opengroup.org/onlinepubs/9699919799/utilities/V3_chap02.html

### ツール
- **ShellCheck**: https://www.shellcheck.net/
  - 静的解析ツール、CI/CD統合可能
- **shfmt**: https://github.com/mvdan/sh
  - Shell スクリプトフォーマッター
- **bats**: https://github.com/bats-core/bats-core
  - Bash Automated Testing System

### ベストプラクティスガイド
- **Google Shell Style Guide**: https://google.github.io/styleguide/shellguide.html
- **Bash Pitfalls**: https://mywiki.wooledge.org/BashPitfalls
- **Bash Guide**: https://mywiki.wooledge.org/BashGuide

### セキュリティ
- **OWASP Command Injection**: https://owasp.org/www-community/attacks/Command_Injection
- **CWE-78: OS Command Injection**: https://cwe.mitre.org/data/definitions/78.html

### パフォーマンス
- **Bash Performance Tips**: https://www.shellcheck.net/wiki/SC2002
- **Useless Use of Cat Award**: http://porkmail.org/era/unix/award.html

---

## 🎯 適用例

### 最小限の実装例

```bash
#!/bin/bash
#
# minimal-tool.sh - Minimal Shell CLI implementation
# Version: 1.0.0
#

set -euo pipefail

# ========================================
# Configuration
# ========================================

readonly VERSION="1.0.0"
readonly SCRIPT_NAME="$(basename "$0")"

# ========================================
# Functions
# ========================================

show_usage() {
    cat <<EOF
Usage: $SCRIPT_NAME [OPTIONS] COMMAND

Options:
    -h, --help     Show this help
    -v, --version  Show version

Commands:
    process FILE   Process the specified file
EOF
}

show_version() {
    echo "$SCRIPT_NAME version $VERSION"
}

error() {
    echo "Error: $*" >&2
    return 1
}

cleanup() {
    # クリーンアップ処理
    :
}

process_file() {
    local file="$1"

    if [[ ! -f "$file" ]]; then
        error "File not found: $file"
        return 1
    fi

    # 処理
    echo "Processing: $file"
}

# ========================================
# Main
# ========================================

main() {
    # 引数チェック
    if [[ $# -eq 0 ]]; then
        show_usage
        exit 1
    fi

    # オプション解析
    case "${1:-}" in
        -h|--help)
            show_usage
            exit 0
            ;;
        -v|--version)
            show_version
            exit 0
            ;;
        process)
            shift
            process_file "$@"
            ;;
        *)
            error "Unknown command: $1"
            show_usage
            exit 1
            ;;
    esac
}

trap cleanup EXIT

if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
```

このガイドラインに従うことで、安全で保守性の高いShell CLIツールを実装できます。
