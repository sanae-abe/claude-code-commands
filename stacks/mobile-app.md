# Mobile App Development

## 📋 クイックスタート

```bash
# React Native開発（99%使用）
npm start                # Metro Bundler起動
npm run ios              # iOSシミュレーター起動
npm run android          # Androidエミュレーター起動

# Flutter開発（99%使用）
flutter run              # デバイス/エミュレーターで起動
flutter run -d ios       # iOS指定
flutter run -d android   # Android指定

# ビルド・デプロイ（90%使用）
npm run build:ios        # iOSリリースビルド
npm run build:android    # Androidリリースビルド
fastlane ios beta        # TestFlight配信
fastlane android beta    # Play Console内部テスト配信
```

## 🎯 品質基準

### クロスプラットフォーム
- **React Native**: JavaScriptベース、豊富なエコシステム
- **Flutter**: Dartベース、高性能、ネイティブ感
- **Native（Swift/Kotlin）**: 最高性能、プラットフォーム特化

### パフォーマンス
- **アプリサイズ**: < 50MB（ダウンロードサイズ）
- **起動時間**: < 2秒（コールドスタート）
- **FPS**: 60fps維持（スクロール、アニメーション）
- **メモリ使用量**: 適切な範囲、リーク防止

### デバイス対応
- **iOS**: 最新2バージョン + 1つ前のメジャーバージョン
- **Android**: API 21+（Android 5.0以降）
- **画面サイズ**: 全デバイス対応（iPhone SE〜iPad Pro、各種Android）

## 🔒 セキュリティ

### データ保護
- **ローカルストレージ暗号化**: AsyncStorage + 暗号化ライブラリ
- **Keychain/KeyStore使用**: 機密情報（トークン等）
- **証明書ピンニング**: HTTPS通信の中間者攻撃防御

### 権限管理
```javascript
// React Native権限リクエスト例
import { PermissionsAndroid, Platform } from 'react-native';

async function requestCameraPermission() {
  if (Platform.OS === 'android') {
    const granted = await PermissionsAndroid.request(
      PermissionsAndroid.PERMISSIONS.CAMERA,
      {
        title: 'カメラ権限',
        message: 'QRコードスキャンにカメラが必要です',
        buttonPositive: '許可'
      }
    );
    return granted === PermissionsAndroid.RESULTS.GRANTED;
  }
  // iOS: Info.plistで説明文設定済み
  return true;
}
```

### コード難読化
- **ProGuard（Android）**: リリースビルドで必須
- **Bitcode（iOS）**: App Store最適化
- **JavaScriptバンドル難読化**: React Nativeの場合

## 📊 パフォーマンス

### 最適化ポイント
- **画像**: WebP形式、適切なサイズ、Lazy Loading
- **リスト**: FlatList（React Native）、ListView（Flutter）の仮想化
- **メモリ**: useEffectクリーンアップ、不要なリスナー削除
- **ネットワーク**: キャッシュ、オフライン対応、最適化されたAPI呼び出し

### バンドルサイズ削減
```bash
# React Native
npx react-native-bundle-visualizer

# Flutter
flutter build apk --analyze-size
flutter build ios --analyze-size
```

## 💡 実践例

### ケース1: アプリサイズ最適化
```bash
# 状況: アプリサイズ 120MB（ユーザー離脱）

# 対策1: 画像最適化
# - PNG → WebP変換
# - 不要な高解像度画像削除
# 削減: 60MB

# 対策2: 未使用ライブラリ削除
npm uninstall moment  # 66KB
npm install dayjs     # 2KB（代替）
# 削減: 10MB

# 対策3: ProGuard最適化
# android/app/proguard-rules.pro 設定
# 削減: 20MB

# 結果: 120MB → 30MB（75%削減）
# ダウンロード率: 40% → 85%向上
```

### ケース2: 起動速度改善
```javascript
// 状況: コールドスタート5秒（遅い）

// ❌ 起動時に全データロード
function App() {
  const [data, setData] = useState(null);

  useEffect(() => {
    // 大量のデータ取得（5秒）
    fetchAllData().then(setData);
  }, []);

  return data ? <MainApp data={data} /> : <Loading />;
}

// ✅ 遅延ロード + スプラッシュスクリーン活用
function App() {
  const [essentialData, setEssentialData] = useState(null);

  useEffect(() => {
    // 必須データのみ（0.5秒）
    fetchEssentialData().then(setEssentialData);
  }, []);

  useEffect(() => {
    // その他のデータはバックグラウンドで
    if (essentialData) {
      fetchAdditionalData();
    }
  }, [essentialData]);

  return <MainApp data={essentialData} />;
}

// 結果: 5秒 → 1.2秒（75%改善）
```

### ケース3: TestFlight/Play Console自動化
```bash
# Fastlane設定（fastlane/Fastfile）
lane :ios_beta do
  # 1. ビルド番号自動インクリメント
  increment_build_number

  # 2. ビルド
  build_app(scheme: "MyApp")

  # 3. TestFlight配信
  upload_to_testflight(
    skip_waiting_for_build_processing: true
  )

  # 4. Slack通知
  slack(message: "TestFlightにビルド配信完了")
end

# 実行
fastlane ios_beta

# 結果: 手動2時間 → 自動15分
# 週次リリースが容易に
```

### よくあるパターン

#### パフォーマンス
- **画像**: WebP、適切サイズ、CDN配信
- **リスト**: 仮想化、Pagination
- **ネットワーク**: キャッシュ、オフライン対応

#### ストア対応
- **iOS**: App Store Connect、TestFlight、レビューガイドライン遵守
- **Android**: Play Console、内部テスト/クローズドテスト、段階的ロールアウト

#### デバイステスト
- **iOS**: 実機テスト（最新iPhone、iPad）、シミュレーター
- **Android**: Firebase Test Lab、各メーカー端末

## 🔧 技術スタック選択ガイド

### React Native
- **適用**: Web技術活用、既存Reactコード流用、豊富なライブラリ
- **特徴**: JavaScriptベース、Hot Reload、Expo活用可
- **注意点**: ネイティブモジュール連携、パフォーマンス調整

### Flutter
- **適用**: 高性能UI、ネイティブ感重視、Google ecosystem
- **特徴**: Dartベース、Hot Reload、Material/Cupertino Design
- **注意点**: Dart学習、ライブラリエコシステム成熟度

### Native（Swift/Kotlin）
- **適用**: 最高性能、プラットフォーム特化機能、長期保守
- **特徴**: 最新API即座利用、最高パフォーマンス
- **注意点**: 2倍の開発コスト、コード重複

## 📱 App Store最適化

### App Store Connect
- **スクリーンショット**: 各デバイスサイズ対応、魅力的なデザイン
- **App Preview**: 動画プレビュー（15-30秒）
- **説明文**: キーワード最適化、明確な価値提案

### Play Console
- **ストアリスティング**: タイトル最適化、説明文キーワード
- **段階的ロールアウト**: 5% → 20% → 50% → 100%
- **クラッシュレポート**: Firebase Crashlytics統合

## 📚 参考リソース

- **React Native公式**: https://reactnative.dev/
- **Flutter公式**: https://flutter.dev/
- **iOS Human Interface Guidelines**: https://developer.apple.com/design/human-interface-guidelines/
- **Android Material Design**: https://material.io/design
- **Fastlane**: https://fastlane.tools/
