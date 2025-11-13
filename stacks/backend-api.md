# Backend API Development

## 📋 クイックスタート

```bash
# 開発開始（99%使用）
npm start                # APIサーバー起動（Node.js）
npm run dev              # 開発モード（ホットリロード）
npm run type-check       # 型チェック（TypeScript）

# データベース操作（90%使用）
npm run migrate          # マイグレーション実行
npm run seed             # テストデータ投入
npm run db:reset         # データベースリセット

# テスト・品質確認（85%使用）
npm run test             # 全テスト実行
npm run test:unit        # 単体テスト
npm run test:integration # 統合テスト
npm run lint             # Linter実行
```

## 🎯 品質基準

### API設計
- **RESTful原則遵守**: リソースベースURL、適切なHTTPメソッド
- **OpenAPI 3.0+仕様書**: 必須、swagger-uiで自動生成
- **バージョニング**: `/api/v1/`形式、破壊的変更時はバージョンアップ
- **エラーレスポンス統一**: RFC 7807 Problem Details形式推奨

### 型安全性
- **TypeScript（Node.js）**: strict mode、型エラー0件
- **Python**: Type Hints + mypy、Pydantic使用
- **Go**: 静的型付け、nil安全性確保
- **Rust**: 所有権システム、unwrap()の慎重な使用

### テスト戦略
- **単体テスト**: 関数・メソッド単位、カバレッジ80%+
- **統合テスト**: APIエンドポイント、データベース連携
- **E2Eテスト**: ユーザーシナリオベース
- **負荷テスト**: 本番想定のRPS（Requests Per Second）確認

## 🔒 セキュリティ

### OWASP API Top 10対応（必須）
1. **認証の脆弱性**: JWT + Refresh Token、OAuth 2.0
2. **認可の脆弱性**: RBAC（Role-Based Access Control）実装
3. **データ露出**: レスポンスフィルタリング、機密情報マスク
4. **Rate Limiting**: IP/ユーザーベース制限、429 Too Many Requests
5. **BOLA（Broken Object Level Authorization）**: オブジェクト所有権確認
6. **マスアサインメント**: ホワイトリスト方式の入力検証
7. **SQLインジェクション**: ORM/パラメータ化クエリ必須
8. **インジェクション**: 入力検証、出力エスケープ
9. **構成ミス**: セキュアなデフォルト設定、秘密情報の環境変数化
10. **不十分なログ記録**: 監査ログ、異常検知

### 認証・認可
```javascript
// JWT認証の実装例（Node.js + Express）
const jwt = require('jsonwebtoken');

// 認証ミドルウェア
function authenticateToken(req, res, next) {
  const token = req.headers['authorization']?.split(' ')[1];
  if (!token) return res.sendStatus(401);

  jwt.verify(token, process.env.JWT_SECRET, (err, user) => {
    if (err) return res.sendStatus(403);
    req.user = user;
    next();
  });
}

// 認可チェック
function authorizeRole(...roles) {
  return (req, res, next) => {
    if (!roles.includes(req.user.role)) {
      return res.sendStatus(403);
    }
    next();
  };
}

// 使用例
app.get('/api/admin/users',
  authenticateToken,
  authorizeRole('admin'),
  getUsers
);
```

### 入力検証
```python
# Pydanticによる入力検証（Python + FastAPI）
from pydantic import BaseModel, EmailStr, constr, validator

class UserCreate(BaseModel):
    username: constr(min_length=3, max_length=20)  # 長さ制限
    email: EmailStr  # メール形式検証
    password: constr(min_length=8)  # パスワード最小長

    @validator('password')
    def validate_password(cls, v):
        if not any(c.isupper() for c in v):
            raise ValueError('少なくとも1つの大文字が必要')
        if not any(c.isdigit() for c in v):
            raise ValueError('少なくとも1つの数字が必要')
        return v

@app.post("/users")
async def create_user(user: UserCreate):
    # 検証済みデータで安全に処理
    return {"username": user.username}
```

## 📊 パフォーマンス

### レスポンス時間目標
- **P95**: < 200ms（95%のリクエストが200ms以内）
- **P99**: < 500ms（99%のリクエストが500ms以内）
- **最大**: < 2000ms（タイムアウト設定）

### スループット
- **最小RPS**: 1000リクエスト/秒（単一インスタンス）
- **スケーリング**: 水平スケール対応、ステートレス設計

### データベース最適化
- **N+1問題解決**: JOIN、Eager Loading使用
  ```javascript
  // ❌ N+1問題
  const users = await User.findAll();
  for (const user of users) {
    user.posts = await Post.findAll({ where: { userId: user.id } });
  }

  // ✅ 解決（Eager Loading）
  const users = await User.findAll({
    include: [{ model: Post }]
  });
  ```
- **インデックス適切配置**: WHERE、JOIN条件のカラムにインデックス
- **クエリ分析**: EXPLAIN実行、スロークエリログ監視

### キャッシュ戦略
- **Redis**: セッション、頻出クエリ結果
- **CDN**: 静的アセット、API GETレスポンス（適切なCache-Controlヘッダー）
- **メモリキャッシュ**: インプロセスキャッシュ（短時間TTL）

## 💡 実践例

### ケース1: N+1問題の解決
```javascript
// 状況: ユーザー一覧取得が遅い（5秒）

// ❌ N+1問題のコード
async function getUsers() {
  const users = await User.findAll();  // 1回のクエリ

  for (const user of users) {
    // N回のクエリ（ユーザー数分）
    user.posts = await Post.findAll({ where: { userId: user.id } });
  }
  return users;
}
// クエリ数: 1 + N（100ユーザーなら101回）

// ✅ 解決（Eager Loading）
async function getUsers() {
  return await User.findAll({
    include: [{
      model: Post,
      attributes: ['id', 'title', 'createdAt']  // 必要なカラムのみ
    }]
  });
}
// クエリ数: 1回（JOIN使用）
// 結果: 5秒 → 0.2秒（25倍高速化）
```

### ケース2: Rate Limiting実装
```javascript
// 状況: API乱用による過負荷

// express-rate-limitを使用
const rateLimit = require('express-rate-limit');

// IP単位のRate Limiting
const apiLimiter = rateLimit({
  windowMs: 15 * 60 * 1000,  // 15分
  max: 100,  // 最大100リクエスト
  message: 'このIPからのリクエストが多すぎます。15分後に再試行してください。',
  standardHeaders: true,  // RateLimit-* ヘッダー
  legacyHeaders: false
});

// 認証エンドポイントの厳しい制限
const authLimiter = rateLimit({
  windowMs: 60 * 1000,  // 1分
  max: 5,  // 最大5回
  skipSuccessfulRequests: true  // 成功リクエストはカウントしない
});

app.use('/api/', apiLimiter);
app.use('/api/auth/', authLimiter);

// 結果: 乱用攻撃を防御、サーバー安定稼働
```

### ケース3: SQLインジェクション対策
```python
# 状況: ユーザー入力をそのままSQLに使用

# ❌ 危険な実装（SQLインジェクション脆弱性）
def get_user(username):
    query = f"SELECT * FROM users WHERE username = '{username}'"
    return db.execute(query)
# 攻撃: username = "admin' OR '1'='1"
# 実行SQL: SELECT * FROM users WHERE username = 'admin' OR '1'='1'
# → 全ユーザー情報が漏洩

# ✅ 安全な実装1: ORM使用
def get_user(username):
    return User.query.filter_by(username=username).first()

# ✅ 安全な実装2: パラメータ化クエリ
def get_user(username):
    query = "SELECT * FROM users WHERE username = ?"
    return db.execute(query, (username,))

# 結果: SQLインジェクション完全防御
```

### よくあるパターン

#### API設計
- **RESTful**: リソースベースURL、適切なHTTPメソッド（GET/POST/PUT/DELETE）
- **GraphQL**: 柔軟なクエリ、過剰取得/過少取得の回避
- **エラーハンドリング**: 統一形式、適切なHTTPステータスコード

#### セキュリティ
- **認証**: JWT + Refresh Token、OAuth 2.0
- **認可**: RBAC、オブジェクトレベル権限チェック
- **入力検証**: ホワイトリスト方式、型安全なスキーマ

#### パフォーマンス
- **データベース**: N+1解決、適切なインデックス、クエリ最適化
- **キャッシュ**: Redis、CDN、メモリキャッシュ
- **非同期処理**: メッセージキュー（RabbitMQ、Kafka）

## 🔧 技術スタック選択ガイド

### Node.js
- **適用**: 高並行性、リアルタイム、JavaScriptエコシステム活用
- **特徴**: イベントループ、非同期I/O、npm豊富
- **注意点**: CPU集約処理は不向き

### Python
- **適用**: データ処理、機械学習連携、開発速度重視
- **特徴**: 豊富なライブラリ、可読性高い
- **注意点**: GIL（Global Interpreter Lock）によるマルチスレッド制限

### Go
- **適用**: 高性能、並行処理、クラウドネイティブ
- **特徴**: 軽量、コンパイル高速、goroutine
- **注意点**: エラーハンドリングが冗長

### Rust
- **適用**: 最高性能、メモリ安全性、システムプログラミング
- **特徴**: 所有権システム、ゼロコスト抽象化
- **注意点**: 学習曲線急

## 📚 参考リソース

- **OWASP API Security**: https://owasp.org/www-project-api-security/
- **OpenAPI Specification**: https://swagger.io/specification/
- **JWT Best Practices**: https://tools.ietf.org/html/rfc8725
