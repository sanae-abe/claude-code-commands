# Frontend Web Development

## 📋 クイックスタート

```bash
# 開発開始（99%使用）
npm run dev              # Vite/Webpack開発サーバー起動
npm run type-check       # TypeScript型チェック
npm run lint:fix         # ESLint自動修正

# コード品質確認（90%使用）
npm run test             # テスト実行（Vitest/Jest）
npm run format           # Prettier自動整形
npm run build            # プロダクションビルド

# パフォーマンス分析（80%使用）
npm run build -- --analyze  # バンドルサイズ分析
npm run lighthouse          # Core Web Vitals測定
npm run test:coverage       # テストカバレッジ
```

## 🎯 品質基準

### TypeScript
- **strict mode必須**: tsconfig.jsonで`"strict": true`
- **型エラー0件**: `npm run type-check`で検証
- **型推論活用**: `any`の使用を最小限に

### ESLint
- **0エラー必須**: フレームワーク別ルール適用
  - React: `eslint-plugin-react`, `eslint-plugin-react-hooks`
  - Vue: `eslint-plugin-vue`
  - Angular: `@angular-eslint`
- **自動修正活用**: `npm run lint:fix`で修正可能なものは自動修正

### Prettier
- **統一フォーマット**: プロジェクト全体で一貫したコードスタイル
- **自動整形**: 保存時またはコミット前に実行

### Bundler最適化
- **Vite**: 最速の開発体験、HMR（Hot Module Replacement）
- **Webpack**: 高度なカスタマイズ、Code Splitting
- **Parcel**: ゼロコンフィグ、シンプルなプロジェクト向け

## 🔒 セキュリティ

### XSS対策
- **Reactのエスケープ機能**: デフォルトで自動エスケープ（`{変数}`）
- **DOMPurify使用**: raw HTMLを扱う場合は必須
  ```tsx
  import DOMPurify from 'dompurify';
  const clean = DOMPurify.sanitize(dirtyHTML);
  ```
- **dangerouslySetInnerHTML禁止**: やむを得ない場合のみ、DOMPurify併用

### CSP（Content Security Policy）
- **設定必須**: HTTPヘッダーまたはmetaタグで設定
  ```html
  <meta http-equiv="Content-Security-Policy"
        content="default-src 'self'; script-src 'self' 'unsafe-inline'">
  ```
- **インラインスクリプト制限**: nonceまたはhashの使用推奨

### HTTPS
- **全通信暗号化**: 開発環境でもHTTPS使用を推奨
- **Mixed Content回避**: HTTP/HTTPS混在を避ける

### Dependencies
- **脆弱性チェック**: `npm audit`で0エラー
- **定期更新**: Dependabot、Renovateの活用
- **Snyk統合**: CI/CDでのセキュリティスキャン

## 📊 パフォーマンス

### Core Web Vitals（目標値）
- **LCP (Largest Contentful Paint)**: < 2.5秒（良好）
- **FID (First Input Delay)**: < 100ms（良好）
- **CLS (Cumulative Layout Shift)**: < 0.1（良好）

### バンドルサイズ
- **ベースライン±10%**: 大幅な増加を避ける
- **Code Splitting**: ルートベース、コンポーネントベースで分割
- **Tree Shaking**: 未使用コードの削除

### メモリ管理
- **リーク防止**: useEffect cleanupの徹底
  ```tsx
  useEffect(() => {
    const subscription = subscribe();
    return () => subscription.unsubscribe(); // cleanup
  }, []);
  ```
- **適切なメモ化**: useMemo、useCallback、React.memoの活用

## 💡 実践例

### ケース1: バンドルサイズ最適化
```bash
# 状況: main.js 800KB、初期ロード5秒
npm run build -- --analyze

# 分析結果: lodash全体がバンドルされている（500KB）

# 対策1: Tree Shaking対応のインポート
# Before:
import _ from 'lodash';
_.debounce(fn, 100);

# After:
import debounce from 'lodash-es/debounce';
debounce(fn, 100);

# 対策2: Code Splitting（React.lazy）
# Before:
import HeavyComponent from './HeavyComponent';

# After:
const HeavyComponent = React.lazy(() => import('./HeavyComponent'));
<Suspense fallback={<Loading />}>
  <HeavyComponent />
</Suspense>

# 結果: 800KB → 200KB（75%削減）、ロード5秒 → 1.2秒
```

### ケース2: Core Web Vitals改善
```bash
# 状況: LCP 4.5秒（悪い）、FID 150ms（悪い）

# 対策1: 画像最適化
# - WebP形式への変換
# - Lazy Loading導入
<img src="image.webp" loading="lazy" alt="説明" />

# 対策2: Critical CSS
# - Above the Fold CSSをインライン化
# - 非クリティカルCSSを遅延ロード

# 対策3: JavaScript最適化
# - React.lazyで初期バンドル削減
# - useTransition、useDeferredValueで非緊急処理遅延

# 結果:
# LCP: 4.5秒 → 1.1秒（良好）
# FID: 150ms → 45ms（良好）
# Lighthouse Score: 65点 → 95点
```

### ケース3: XSS脆弱性対策
```tsx
// 状況: ユーザー入力をそのまま表示する実装

// ❌ 危険な実装
function UserComment({ comment }) {
  return <div dangerouslySetInnerHTML={{ __html: comment }} />;
}
// 攻撃: comment = "<script>alert('XSS')</script>"

// ✅ 安全な実装1: Reactのデフォルトエスケープ
function UserComment({ comment }) {
  return <div>{comment}</div>;  // 自動エスケープ
}

// ✅ 安全な実装2: Markdownの場合はDOMPurify
import DOMPurify from 'dompurify';
import marked from 'marked';

function UserComment({ markdown }) {
  const html = marked(markdown);
  const clean = DOMPurify.sanitize(html);
  return <div dangerouslySetInnerHTML={{ __html: clean }} />;
}

// 結果: XSS攻撃を完全防御、セキュリティ監査合格
```

### よくあるパターン

#### パフォーマンス最適化
- **初期表示**: Vite + React.lazy + Suspense + 画像最適化
- **バンドルサイズ**: Tree Shaking + Code Splitting + 依存関係見直し
- **ランタイム**: メモ化（useMemo、React.memo）+ Virtualization

#### 品質保証
- **型安全**: TypeScript strict + ESLint + 型推論活用
- **テスト**: Vitest/Jest + Testing Library + カバレッジ80%+
- **整形**: Prettier + Git Hooks（pre-commit）

#### セキュリティ
- **XSS防御**: Reactエスケープ + DOMPurify（raw HTML時）
- **CSP**: HTTPヘッダー設定 + nonce/hash
- **依存関係**: npm audit + Snyk + 定期更新

## 🔧 技術スタック選択ガイド

### React
- **適用**: 大規模SPA、豊富なエコシステム、柔軟性重視
- **特徴**: 仮想DOM、Hooks、豊富なライブラリ
- **学習コスト**: 中（基本は容易、高度な最適化は複雑）

### Vue
- **適用**: 中小規模、段階的導入、学習コスト重視
- **特徴**: テンプレート構文、リアクティブシステム、公式ルーター/状態管理
- **学習コスト**: 低（公式ドキュメント充実）

### Angular
- **適用**: エンタープライズ、大規模チーム、型安全重視
- **特徴**: フルフレームワーク、TypeScript標準、依存性注入
- **学習コスト**: 高（学習曲線急、習得後は生産性高）

## 📚 参考リソース

- **React公式**: https://react.dev/
- **Vue公式**: https://vuejs.org/
- **Angular公式**: https://angular.io/
- **Core Web Vitals**: https://web.dev/vitals/
- **OWASP XSS**: https://owasp.org/www-community/attacks/xss/
