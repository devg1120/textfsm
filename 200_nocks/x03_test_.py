from pathlib import Path
import sys
parent_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(parent_dir))

##########################################
import io
import textfsm

def parseTemplate(Title, Desc, InputData,Template):
    Template_io = io.StringIO(Template.strip())
    fsm = textfsm.TextFSM(Template_io)
    result = fsm.ParseText(InputData)
    tl = 10
    print("")
    print("##### ", end="")
    print("="*(tl), Title)
    print(Desc)
    print("")
    print("```")
    print("# input #")
    print(InputData.strip())
    print("-"*tl)
    print("# template #")
    print(fsm)
    print("-"*tl)
    print("# result #")
    print(fsm.header)
    print(*result, sep='\n')
    print("```")


##########################################
print("[LINK](https://yoloz.hatenablog.com/entry/2022/02/06/034008)")
##########################################

#--------------------------------------------------------#
Title = "パターンA：シンプルな1行1レコードの表形式"
Desc = "1行1レコードの表形式"

InputData = '''
Interface        IP-Address      Status
GigabitEthernet1 192.168.1.1     up
GigabitEthernet2 192.168.2.1     down
Loopback0        10.0.0.1        up

'''

Template = r'''
Value INTERFACE (\S+)
Value IP_ADDRESS (\d+\.\d+\.\d+\.\d+)
Value STATUS (\w+)

Start
  ^${INTERFACE}\s+${IP_ADDRESS}\s+${STATUS} -> Record

'''

parseTemplate(Title,Desc,InputData,Template)

#--------------------------------------------------------#
Title = "パターンB：複数行にまたがるリスト（Value List + Continue.Record）"
Desc = "VLAN 20 のように次の行にポートが続くケース。"

InputData = '''
VLAN Name                             Ports
---- -------------------------------- -------------------------------
10   default                          Gi1/0/1
20   Sales                            Gi1/0/2
                                      Gi1/0/3
                                      Gi1/0/4
30   Engineering                      Gi1/0/5

'''

Template = r'''
Value Key VLAN_ID (\d+)
Value NAME (\w+)
Value List PORTS (\S+)

Start
  # 新しいVLAN番号が来たら、前のVLANを保存してから同じ行を再評価
  ^\d+ -> Continue.Record
  ^${VLAN_ID}\s+${NAME}\s+${PORTS}
  ^\s+${PORTS}

'''

parseTemplate(Title,Desc,InputData,Template)

#--------------------------------------------------------#
Title = "パターンC：1つの対象につき複数行続くブロック形式（ステート遷移）"
Desc = "show interfaces のように縦に項目が並ぶケース。"

InputData = '''
GigabitEthernet0/1 is up
  Description: Uplink to Core Switch
  MTU 1500 bytes

GigabitEthernet0/2 is administratively down
  Description: Unused Port
  MTU 1500 bytes


'''

Template = r'''
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

'''

parseTemplate(Title,Desc,InputData,Template)

#--------------------------------------------------------#
Title = "パターンD：親の値を子に引き継ぐ階層構造（Filldown + Required）"
Desc = ""

InputData = '''
Device: Router-Tokyo
  Gi0/0 10.1.1.1
  Gi0/1 10.1.2.1
Device: Router-Osaka
  Gi0/0 10.2.1.1

'''

Template = r'''
Value Filldown DEVICE (\S+)
Value Required INTERFACE (\S+)
Value IP_ADDRESS (\d+\.\d+\.\d+\.\d+)

Start
  ^Device:\s+${DEVICE}
  ^\s+${INTERFACE}\s+${IP_ADDRESS} -> Record

'''

parseTemplate(Title,Desc,InputData,Template)

#--------------------------------------------------------#
Title = "パターンE：後から出るグループ名をさかのぼって埋める（Fillup）"
Desc = ""

InputData = '''
  Gi0/0 192.168.10.1
  Gi0/1 192.168.10.2
Group: LAN_Segment
  Gi0/2 172.16.1.1
Group: WAN_Segment

'''

Template = r'''
Value INTERFACE (\S+)
Value IP_ADDRESS (\d+\.\d+\.\d+\.\d+)
Value Fillup GROUP_NAME (\S+)

Start
  ^\s+${INTERFACE}\s+${IP_ADDRESS} -> Record
  ^Group:\s+${GROUP_NAME}

'''

parseTemplate(Title,Desc,InputData,Template)

#--------------------------------------------------------#
Title = "パターンF：ヘッダーや不要なセクションのスキップ（ステート隔離）"

Desc ="コマンドの先頭にあるバナー情報や、途中のサマリー行・不要なブロックを無視して、特定のセクションだけを抽出するパターンです。"

InputData = '''
System Banner: Welcome to Switch-01
Uptime: 120 days

Interface Table
Gi0/1   0011.2233.4455
Gi0/2   aabb.ccdd.eeff
---
Footer: End of output
Gi0/3   9999.8888.7777

'''

Template = r'''
Value INTERFACE (\S+)
Value MAC_ADDR ([0-9a-fA-F\.]+)

Start
  # "Interface Table" という見出しが来るまで他の行はすべて無視する
  ^Interface Table -> ParseTable

ParseTable
  # 終了の合図（空行や区切り線など）が来たら Start に戻って以降の行を無視
  ^--- -> Start
  ^${INTERFACE}\s+${MAC_ADDR} -> Record

'''

parseTemplate(Title,Desc,InputData,Template)


#--------------------------------------------------------#
Title = "パターンG：1行に複数の要素がカンマ区切りなどで並ぶケース（Continue の活用）"

Desc = "1つの行に複数のポートやVLAN IDが横並びで記載されている場合に、行を消費せずに1つずつ切り出してレコード化するパターンです。"

InputData = '''
VLAN 10: Gi0/1, Gi0/2, Gi0/3
VLAN 20: Gi0/4, Gi0/5
'''

Template = r'''
Value VLAN_ID (\d+)
Value PORTS (.+)

Start
  ^VLAN\s+${VLAN_ID}:\s+${PORTS} -> Record

'''

parseTemplate(Title,Desc,InputData,Template)


#--------------------------------------------------------#
Title = "パターンH：一部だけのレコードをクリアして保持値を維持する（Clear と Clearall）"

Desc = "階層構造（Filldown）を使いつつ、親が変わったタイミングや特定の条件で変数をリセットしたい場合に使用します。通常の Record は Filldown 以外の変数をクリアしますが、Clearall を使うと Filldown の値もすべてリセットできます。"

InputData = '''
VRF: Customer_A
  10.0.1.0/24 via 192.168.1.1
  10.0.2.0/24 via 192.168.1.1
VRF: Customer_B
  172.16.0.0/16 via 192.168.2.1


'''

Template = r'''
Value Filldown VRF (\S+)
Value NETWORK (\d+\.\d+\.\d+\.\d+/\d+)
Value NEXT_HOP (\d+\.\d+\.\d+\.\d+)

Start
  # VRFが変わったら、前のVRFの情報を完全にリセット
  ^VRF: -> Continue.Clearall
  # Clearallだと今読んだVRFも消えるため、Continueで再評価させるのがテクニック
  ^VRF:\s+${VRF}
  ^\s+${NETWORK}\s+via\s+${NEXT_HOP} -> Record

EOF
'''

parseTemplate(Title,Desc,InputData,Template)


#--------------------------------------------------------#
Title = "パターンI：複数条件・表記揺れ（Optional項目）の吸収"

Desc = "「ある行には存在するが、別の行には存在しない項目」を含む出力（例：ルーティングテーブルの直接接続とスタティックルートの混在など）を1つのテンプレートで扱うパターンです。"

InputData = '''
C    192.168.1.0/24 is directly connected, GigabitEthernet0/0
S    10.0.0.0/8 via 192.168.1.254, GigabitEthernet0/0
O    172.16.10.0/24 via 192.168.1.253, GigabitEthernet0/1


'''

Template = r'''
Value PROTOCOL ([A-Z])
Value PREFIX (\d+\.\d+\.\d+\.\d+/\d+)
Value NEXT_HOP (\d+\.\d+\.\d+\.\d+)
Value INTERFACE (\S+)

Start
  # via がある場合と、directly connected の場合を正規表現のグループ化(?: ... )? で吸収
  ^${PROTOCOL}\s+${PREFIX}(?:\s+via\s+${NEXT_HOP},)?\s+(?:is directly connected,\s+)?${INTERFACE} -> Record


'''

parseTemplate(Title,Desc,InputData,Template)

#--------------------------------------------------------#
Title = "パターンJ：インデントの深さで親子関係を判別する（BGPや設定ファイル系）"

Desc = "show running-config や show ip bgp summary のように、スペースの数（インデント）によって階層が表現されるテキストのパースです。"

InputData = '''
neighbor 10.1.1.1
  remote-as 65001
  state Established
neighbor 10.1.1.2
  remote-as 65002
  state Active

'''

Template = r'''
Value Filldown NEIGHBOR (\d+\.\d+\.\d+\.\d+)
Value Required REMOTE_AS (\d+)
Value STATE (\S+)

Start
  # インデントなし（行頭）は親要素
  ^neighbor\s+${NEIGHBOR}
  # スペース2つ以上のインデントは子要素
  ^\s{2,}remote-as\s+${REMOTE_AS}
  ^\s{2,}state\s+${STATE} -> Record

'''

parseTemplate(Title,Desc,InputData,Template)
"""
#--------------------------------------------------------#
Title = ""

Desc = ""

InputData = '''

'''

Template = r'''

'''

parseTemplate(Title,InputData,Template)
"""

