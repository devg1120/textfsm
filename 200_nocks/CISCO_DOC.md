# TextFSM 実践サンプル集（Cisco IOS 編）

Cisco IOS の運用で頻出する4つのコマンド（表形式・複数行リスト・ブロック形式・ECMPルート）をパースするための実践テンプレート集です。

---

## 1. `show ip interface brief`（シンプルな表形式）

`administratively down` のようにステータスに半角スペースが含まれる場合や、`unassigned` がIP欄に入るケースに対応したパターンです。

### CLI出力サンプル
```text
Interface              IP-Address      OK? Method Status                Protocol
GigabitEthernet0/0     192.168.1.1     YES NVRAM  up                    up
GigabitEthernet0/1     unassigned      YES unset  administratively down down
Vlan10                 10.10.10.254    YES manual up                    up
```

### テンプレート（`cisco_ios_show_ip_interface_brief.template`）
```text
Value INTERFACE (\S+)
Value IP_ADDRESS (\S+)
Value OK (YES|NO)
Value METHOD (\S+)
Value STATUS (up|down|administratively down)
Value PROTOCOL (up|down)

Start
  ^Interface\s+IP-Address -> Next

Next
  ^${INTERFACE}\s+${IP_ADDRESS}\s+${OK}\s+${METHOD}\s+${STATUS}\s+${PROTOCOL} -> Record
```

* **ポイント**: 1行目のヘッダ行を `Start` でスキップして `Next` ステートへ移すことで、ヘッダ文字列の誤マッチを防いでいます。

---

## 2. `show vlan brief`（複数行にまたがるポートリスト）

Cisco IOSのVLAN表示で、ポート数が多い場合に次の行へインデントされて折り返される出力や、ポートが1つもないVLANに対応するパターンです。

### CLI出力サンプル
```text
VLAN Name                             Status    Ports
---- -------------------------------- --------- -------------------------------
1    default                          active    Gi0/1, Gi0/2
10   Sales_Dept                       active    Gi0/3, Gi0/4, Gi0/5, Gi0/6
                                                Gi0/7, Gi0/8
1002 fddi-default                     act/unsup
```

### テンプレート（`cisco_ios_show_vlan_brief.template`）
```text
Value Key VLAN_ID (\d+)
Value NAME (\S+)
Value STATUS (\S+)
Value List PORTS ([^,\s]+)

Start
  ^VLAN\s+Name -> Next

Next
  # 新しいVLAN行が始まったら、前のレコードを保存して同じ行を再評価
  ^\d+ -> Continue.Record
  ^${VLAN_ID}\s+${NAME}\s+${STATUS}(?:\s+${PORTS})? -> Continue
  # 1行目の2番目以降のポートをカンマ区切りで取得（最大4つまでの例）
  ^\d+\s+\S+\s+\S+\s+[^,\s]+,\s*${PORTS} -> Continue
  ^\d+\s+\S+\s+\S+\s+(?:[^,\s]+,\s*){2}${PORTS} -> Continue
  ^\d+\s+\S+\s+\S+\s+(?:[^,\s]+,\s*){3}${PORTS}
  # 折り返し行（先頭が空白）のポートを取得
  ^\s+${PORTS} -> Continue
  ^\s+[^,\s]+,\s*${PORTS}
```

* **ポイント**: ポートが1つも割り当てられていない行（`VLAN 1002`）にも対応するため、`(?:\s+${PORTS})?` と非キャプチャグループを使ってポート部分を任意（0回または1回）にしています。

---

## 3. `show cdp neighbors detail`（`-----` 区切りのブロック形式）

ハイフンの区切り線で各隣接機器の情報が分かれている、縦長ブロック形式をパースするパターンです。

### CLI出力サンプル
```text
-------------------------
Device ID: Core-SW01.example.local
Entry address(es):
  IP address: 10.0.0.1
Platform: cisco WS-C3850-24T,  Capabilities: Switch IGMP
Interface: GigabitEthernet0/1,  Port ID (outgoing port): GigabitEthernet1/0/24
Holdtime : 154 sec

-------------------------
Device ID: Access-SW02.example.local
Entry address(es):
  IP address: 10.0.0.2
Platform: cisco C9200L-24P-4G,  Capabilities: Switch IGMP
Interface: GigabitEthernet0/2,  Port ID (outgoing port): GigabitEthernet1/0/1
Holdtime : 162 sec
```

### テンプレート（`cisco_ios_show_cdp_neighbors_detail.template`）
```text
Value Required NEIGHBOR (\S+)
Value MGMT_IP (\d+\.\d+\.\d+\.\d+)
Value PLATFORM (.+?)
Value LOCAL_INTF (\S+)
Value REMOTE_INTF (\S+)

Start
  ^Device ID:\s+${NEIGHBOR} -> NeighborBlock

NeighborBlock
  ^\s+IP address:\s+${MGMT_IP}
  ^Platform:\s+${PLATFORM},
  ^Interface:\s+${LOCAL_INTF},\s+Port ID \(outgoing port\):\s+${REMOTE_INTF}
  # 区切り線が来たら1台分のデータを保存してStartに戻る
  ^-{5,} -> Record Start
```

* **ポイント**: `Value Required NEIGHBOR` を指定しているため、最後の区切り線以降にデータがない場合でも空レコードは生成されません。また、`Platform` の後ろのカンマまでを最短一致 `(.+?)` で取得しています。

---

## 4. `show ip route`（ECMP / 複数ネクストホップの `Filldown`）

等コストマルチパス（ECMP）で、1つの宛先ネットワークに対して2行目以降に `[110/20] via ...` だけが続くケースです。親のネットワーク情報を下の行へ引き継ぐ `Filldown` の典型例です。

### CLI出力サンプル
```text
O    10.1.0.0/16 [110/20] via 192.168.1.2, 01:23:45, GigabitEthernet0/1
                 [110/20] via 192.168.2.2, 01:23:45, GigabitEthernet0/2
C    192.168.1.0/24 is directly connected, GigabitEthernet0/1
S*   0.0.0.0/0 [1/0] via 192.168.1.254
```

### テンプレート（`cisco_ios_show_ip_route.template`）
```text
Value Filldown PROTOCOL ([A-Z\*]+)
Value Filldown NETWORK (\d+\.\d+\.\d+\.\d+/\d+)
Value DISTANCE (\d+)
Value METRIC (\d+)
Value NEXT_HOP (\d+\.\d+\.\d+\.\d+)
Value INTERFACE (\S+)

Start
  # 通常の経路行（via あり）
  ^${PROTOCOL}\s+${NETWORK}\s+\[${DISTANCE}/${METRIC}\]\s+via\s+${NEXT_HOP}(?:,\s+\S+,\s+${INTERFACE})? -> Record
  # ECMPの2行目以降（プロトコルとネットワークが省略されている行）
  ^\s+\[${DISTANCE}/${METRIC}\]\s+via\s+${NEXT_HOP}(?:,\s+\S+,\s+${INTERFACE})? -> Record
  # 直接接続（directly connected）
  ^${PROTOCOL}\s+${NETWORK}\s+is\s+directly\s+connected,\s+${INTERFACE} -> Record
```

* **ポイント**: `PROTOCOL` と `NETWORK` に `Filldown` を付けることで、2行目の `[110/20] via 192.168.2.2...` にも直前の `O` と `10.1.0.0/16` が自動的に補完され、2つの独立したルートレコードとして抽出できます。

---

## 実務向けの補足：`ntc-templates` の活用

Cisco IOS の主要コマンドを実務でパースする場合は、オープンソースのテンプレート集 **`ntc-templates`** をインストールすると、数百種類の完成済みテンプレートをすぐに利用できます。

```bash
pip install ntc-templates
```

```python
from ntc_templates.parse import parse_output

raw_output = """
Interface              IP-Address      OK? Method Status                Protocol
GigabitEthernet0/0     192.168.1.1     YES NVRAM  up                    up
"""

parsed = parse_output(platform="cisco_ios", command="show ip interface brief", data=raw_output)
print(parsed)
```
