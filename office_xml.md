https://learn.microsoft.com/en-us/openspecs/main/ms-openspeclp/3589baea-5b22-48f2-9d43-f5bea4960ddb


https://learn.microsoft.com/en-us/openspecs/standards_support/ms-stdsuplp/17a32be7-10b3-4025-bea4-133a66b4c689



word の 説明

# Microsoft Word Open XML仕様の概要

このドキュメントは、Microsoft Word の Open XML（`.docx`）ファイル形式に関する技術仕様とライセンス情報について説明しています。

---

# Word Open XML拡張仕様の概要

このドキュメントは、ISO/IEC 29500 規格に基づくワード処理文書の XML 拡張要素と属性について詳細に説明しています。

---

# 知的財産権とライセンスに関する注意事項

Microsoft のオープン仕様に関する著作権・特許・商標・ライセンスの規定を明示し、以下について記述しています。

- コピーや配布の権利
- 特許の範囲
- 商標の使用制限

---

# 仕様の構造と適用範囲

拡張された XML 語彙は、文書の内容や書式情報を追加・拡張するためのものです。

ISO/IEC 29500 の互換性を維持しつつ、以下の主要な拡張グループに分かれています。

- 書式設定の拡張
- 文書設定の拡張
- 構造化ドキュメントタグの拡張
- 段落・表行の属性拡張
- 編集競合解決用要素
- 画像・埋め込みオブジェクト識別

---

# 拡張要素と属性の詳細

## 書式設定の拡張

例：

- `shadow`
- `glow`
- `ligatures`

---

## 文書設定の拡張

例：

- 画像保存設定
- 多著者対応設定

---

## 構造化ドキュメントタグの拡張

例：

- `entityPicker`
- `appearance`

---

## 段落・表行の属性拡張

例：

- `paraId`
- `noSpellErr`

---

## 編集競合解決用要素

例：

- `conflictIns`
- `conflictDel`

---

## オブジェクト識別用属性

例：

- `anchorId`

---

## その他の拡張

- `footnoteColumns`
- `restartNumberingAfterBreak`
- `symEx`
- `reactions`

---

# 互換性設定の詳細

`compatSetting` 要素により、Word の互換性動作を制御します。

## 主な設定例

- テーブルスタイルのフォントサイズ上書き
- ミラーインデント反転
- OpenType機能有効化
- 多行ヘッダー区別

各設定は `true / false` などの値で制御されます。

---

# 重要ポイント

- `Ignorable` 属性や `AlternateContent` 要素で互換性維持
- 標準仕様との併用が可能
- バージョン管理により互換性を保証

---

# 互換性モード設定

## compatSetting 要素

| 属性 | 内容 |
|---|---|
| `name` | `compatibilityMode` |
| `uri` | `http://schemas.microsoft.com/office/word` |
| `val` | 機能セットのバージョン |

## バージョン値

| 値 | 内容 |
|---|---|
| 11 | MS-DOC |
| 12 | ECMA-376 |
| 14 | ISO/IEC 29500 |
| 15 | 拡張機能セット |

---

# Floating Table後のテキスト配置

## allowTextAfterFloatingTableBreak

- `false`：テーブル後に配置
- `true`：テキスト回り込み

---

# ハイフネーション制御

## allowHyphenationAtTrackBottom

- `false`：禁止
- `true`：許可

## useWord2013TrackBottomHyphenation

- `false`：次ページ
- `true`：同ページ

---

# 旧MacOSレイアウト設定

- `false`：Windowsフォントメトリクス
- `true`：旧Macフォントメトリクス

---

# 数値書式設定

## 例

- 漢数字
- 囲み数字
- 全角数字
- カーディナルテキスト

例：

- `"One, Two, Three"`
- `U+FF11`

---

# WordML の要素と属性

## 主な要素

- `appearance`
- `collapsed`
- `commentsEx`
- `dataBinding`
- `docId`
- `footnoteColumns`
- `people`
- `repeatingSection`

## 主な属性

- `restartNumberingAfterBreak`
- `anchorId`
- `noSpellErr`
- `paraId`
- `textId`

---

# WordML の複合型

- `CT_CommentEx`
- `CT_CommentsEx`
- `CT_Guid`
- `CT_People`
- `CT_Person`
- `CT_PresenceInfo`
- `CT_SdtAppearance`
- `CT_SdtRepeatedSection`

---

# GUID形式

```txt
{8-4-4-4-12}
```

16進数パターンで構成されます。

---

# 3Dおよび色彩関連

## 主な複合型

- `CT_Bevel`
- `CT_Camera`
- `CT_Color`
- `CT_DefaultImageDpi`
- `CT_FillTextEffect`
- `CT_Glow`
- `CT_Shadow`

---

# 3Dと光源設定

## 主な型

- `CT_Scene3D`
- `CT_LightRig`
- `CT_SphereCoords`

## 主な属性

- `lat`
- `lon`
- `rev`

---

# 色彩とグラデーション

## 主な型

- `CT_SchemeColor`
- `CT_SRgbColor`

テーマ色・透明度・グラデーション形状を設定可能。

---

# ライン・フォント設定

## 主な列挙型

- `ST_LineCap`
- `ST_NumForm`
- `ST_NumSpacing`
- `ST_Ligatures`

---

# 影・反射などの視覚効果

## 主な型

- `CT_Reflection`
- `CT_Shadow`

影の距離・角度・ぼかしを詳細設定可能。

---

# カメラ視点の種類

## 代表例

- `Perspective Front`
- `Perspective Left`
- `Perspective Right`
- `Oblique Bottom Right`

## XMLスキーマ

`ST_PresetCameraType` により定義。

---

# XMLスキーマの役割

データ構造や値を制限し、一貫性を保証。

## 主な列挙型

- `ST_PresetCameraType`
- `ST_PresetLineDashVal`
- `ST_PresetMaterialType`

---

# 対応バージョン

- Word 2007
- Word 2010
- Word 2013
- Word 2016
- Word 2019
- Word 2021
- Word 2024 LTSC
- Office 365

---

# 変更追跡と改訂履歴

| 種類 | 内容 |
|---|---|
| メジャー | 実装影響あり |
| マイナー | 説明修正 |
| なし | 軽微変更 |

---

# セキュリティと考慮事項

- 安全設計ガイド提供
- XMLスキーマベースのセキュリティ管理
- データ整合性・拡張性を規定

---

# リリース情報

- 最終リリース予定：2025年11月13日
- 将来の拡張方針も記載

---

# まとめ

この資料は、Microsoft Word Open XML に関する以下を包括的に解説しています。

- XMLスキーマ構造
- 互換性設定
- WordML要素・属性
- 3D・視覚効果
- コメント管理
- バージョン管理
- セキュリティ
- 拡張ポイント
- Officeバージョン対応

Word の内部構造や `.docx` 実装理解のための詳細仕様書です。