# TextFSM 実践チートシート（ユースケース別）

## 1. 基本ルールと頻出エラー対策

### テンプレートの基本構造
```text
# 1. Value定義（変数名と正規表現）
Value 変数名 (正規表現)

# 空行（必須）

# 2. State定義（Startは必須）
Start
  ^ルール行 -> アクション
```

### よくあるエラーと注意点
* **`Value` の括弧**: `Value NAME (\S+)` のように、正規表現全体を必ず `()` で囲む。外側に `\(` を書くと `Unknown option` エラーになる。
* **変数参照**: ルール行で変数を使うときは `${NAME}` のように必ず `$` を付ける。
* **行末の表現**: `$` は変数展開に使われるため、正規表現の「行末」や「空行」は **`$$`** と2つ重ねる（例: 空行は `^$$`）。
* **インデント**: ステート名（`Start` など）の下のルール行は、必ず**半角スペース2つ**でインデントする。
* **文字コード**: Windows環境ではテンプレートファイルを必ず **UTF-8（BOMなし）** で保存する。

---

## 2. Value オプション一覧

複数のオプションを指定する場合は `Value Filldown, Required DEVICE (\S+)` のようにカンマで区切る。

| オプション | 役割 | 主なユースケース |
| :--- | :--- | :--- |
| **`List`** | 値をリスト `[]` に追加していく | 1つのVLANに複数ポートがぶら下がる場合など |
| **`Filldown`** | `Record` 後も値を保持し、次の行へ引き継ぐ | 親要素（機器名など）を子要素の各行にコピーする |
| **`Fillup`** | 後から出現した値で、過去の空欄をさかのぼって埋める | 先に明細が並び、最後にグループ名や小計が出るログ |
| **`Required`** | この値が空のままならレコード出力をスキップする | ヘッダ行や子要素のない親行などのゴミデータを除外 |
| **`Key`** | レコードの一意性（主キー）を定義する | 複合キーの重複検知（重複時に `TextFSMError` を発生） |

---

## 3. アクション（`->` の後ろ）一覧

| アクション | 動作 |
| :--- | :--- |
| `-> Record` | 現在の変数を1レコードとして保存し、変数をリセットする（`Filldown` 除く） |
| `-> Continue` | 行を消費せず、次のルールも**同じ行に対して**続けて評価する |
| `-> Continue.Record` | 現在の変数を保存・リセットした上で、**同じ行を次のルールでも再評価**する |
| `-> StateName` | 指定した別のステート（状態）へ移動する |
| `-> Record StateName` | 現在の変数を保存・リセットしてから、別のステートへ移動する |
| `-> Error` | 異常な行にマッチした際にパースを強制終了し `TextFSMError` を出す |

---

## 4. ユースケース別テンプレート集

### パターンA：シンプルな1行1レコードの表形式
```text
Value INTERFACE (\S+)
Value IP_ADDRESS (\d+\.\d+\.\d+\.\d+)
Value STATUS (\w+)

Start
  ^${INTERFACE}\s+${IP_ADDRESS}\s+${STATUS} -> Record
```

### パターンB：複数行にまたがるリスト（`Value List` + `Continue.Record`）
`VLAN 20` のように次の行にポートが続くケース。
```text
Value Key VLAN_ID (\d+)
Value NAME (\w+)
Value List PORTS (\S+)

Start
  # 新しいVLAN番号が来たら、前のVLANを保存してから同じ行を再評価
  ^\d+ -> Continue.Record
  ^${VLAN_ID}\s+${NAME}\s+${PORTS}
  ^\s+${PORTS}
```

### パターンC：1つの対象につき複数行続くブロック形式（ステート遷移）
`show interfaces` のように縦に項目が並ぶケース。
```text
Value INTERFACE (\S+)
Value STATUS (up|down|administratively down)
Value DESCRIPTION (.+)
Value MTU (\d+)

Start
  ^${INTERFACE}\s+is\s+${STATUS} -> InterfaceBlock

InterfaceBlock
  ^\s+Description:\s+${DESCRIPTION}
  ^\s+MTU\s+${MTU}\s+bytes
  # 空行が来たら1ブロック終了とみなして保存し、Startへ戻る
  ^$$ -> Record Start
  # 空行なしで次のブロックが始まった場合の保険
  ^\S+\s+is\s+ -> Continue.Record
  ^${INTERFACE}\s+is\s+${STATUS}
```

### パターンD：親の値を子に引き継ぐ階層構造（`Filldown` + `Required`）
```text
Value Filldown DEVICE (\S+)
Value Required INTERFACE (\S+)
Value IP_ADDRESS (\d+\.\d+\.\d+\.\d+)

Start
  ^Device:\s+${DEVICE}
  ^\s+${INTERFACE}\s+${IP_ADDRESS} -> Record
```

### パターンE：後から出るグループ名をさかのぼって埋める（`Fillup`）
```text
Value INTERFACE (\S+)
Value IP_ADDRESS (\d+\.\d+\.\d+\.\d+)
Value Fillup GROUP_NAME (\S+)

Start
  ^\s+${INTERFACE}\s+${IP_ADDRESS} -> Record
  ^Group:\s+${GROUP_NAME}
```

---

## 5. Python 実行ボイラープレート（辞書リスト出力）

```python
from pathlib import Path
import textfsm

raw_text = """
# ここにパースしたいCLI出力を入れる
"""

# スクリプトと同じフォルダにある同名 .template ファイルをUTF-8で読み込む
template_path = Path(__file__).resolve().with_suffix(".template")

with open(template_path, encoding="utf-8") as f:
    fsm = textfsm.TextFSM(f)
    # 辞書のリスト [{'INTERFACE': 'Gi0/1', ...}, ...] で取得
    records = fsm.ParseTextToDicts(raw_text)

for record in records:
    print(record)
```
