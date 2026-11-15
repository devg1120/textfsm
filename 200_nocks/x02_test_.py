from pathlib import Path
import sys
parent_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(parent_dir))

##########################################
import io
import textfsm

def parseTemplate(Title, InputData,Template):
    Template_io = io.StringIO(Template.strip())
    fsm = textfsm.TextFSM(Template_io)
    result = fsm.ParseText(InputData)
    tl = 40
    print("")
    print("##### ", end="")
    print("="*(tl), Title)
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

Title = "CISCO show ip interface brief"
InputData = '''
Interface              IP-Address      OK? Method Status                Protocol
GigabitEthernet0/0     192.168.1.1     YES NVRAM  up                    up
GigabitEthernet0/1     unassigned      YES unset  administratively down down
'''

Template = r'''
Value INTERFACE (\S+)
Value IP_ADDRESS (\S+)
Value OK (YES|NO)
Value METHOD (\S+)
Value STATUS (up|down|administratively down)
Value PROTOCOL (up|down)

Start
  ^Interface\s+IP-Address -> ParseInterfaces

ParseInterfaces
  ^${INTERFACE}\s+${IP_ADDRESS}\s+${OK}\s+${METHOD}\s+${STATUS}\s+${PROTOCOL} -> Record

'''

parseTemplate(Title,InputData,Template)
#-----------------------------------------

Title = "CISCO show vlan brief"
InputData = '''
VLAN Name                             Status    Ports
---- -------------------------------- --------- -------------------------------
1    default                          active    Gi0/1, Gi0/2
10   Sales_Dept                       active    Gi0/3, Gi0/4, Gi0/5, Gi0/6
                                                Gi0/7, Gi0/8
1002 fddi-default                     act/unsup
'''

Template = r'''
Value Required VLAN_ID (\d+)
Value NAME (\S+)
Value STATUS (\S+)
Value List PORTS ([^,\s]+)

Start
  ^VLAN\s+Name -> ParseVlan

ParseVlan
  # 次のVLAN行が来たら、前のVLANの蓄積データをRecordして、新しい行を処理(Continue)
  ^\d+ -> Continue.Record
  # VLAN ID, Name, Status と、最初の1つ目のポートを取得（ポートが無いVLANにも対応）
  ^${VLAN_ID}\s+${NAME}\s+${STATUS}(?:\s+${PORTS})? -> Continue
  # 同じ行に2つ目以降のポートがあれば、1つずつListに追加しながら繰り返す
  ^${VLAN_ID}\s+${NAME}\s+${STATUS}(?:\s+[^,\s]+,)+\s*${PORTS} -> Continue
  # 2行目以降に折り返されたポート行の1つ目を取得
  ^\s+${PORTS} -> Continue
  # 折り返された行の2つ目以降のポートを1つずつListに追加
  ^\s+(?:[^,\s]+,)+\s*${PORTS} -> Continue
  # "VLAN Type SAID..." などの別テーブルが始まったら終了（余計な行を拾わないため）
  ^VLAN\s+Type -> Record End


'''

parseTemplate(Title,InputData,Template)
#-----------------------------------------

Title = "CISCO cdp neighbors detail -----" 
InputData = '''
-------------------------
Device ID: Core-SW01.example.local
Entry address(es):
  IP address: 10.0.0.1
Platform: cisco WS-C3850-24T,  Capabilities: Switch IGMP
Interface: GigabitEthernet0/1,  Port ID (outgoing port): GigabitEthernet1/0/24
'''

Template = r'''
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
  ^-{5,} -> Record Start
'''

parseTemplate(Title,InputData,Template)
#-----------------------------------------
Title = "CISCO show ip route" 
InputData = '''
O    10.1.0.0/16 [110/20] via 192.168.1.2, 01:23:45, GigabitEthernet0/1
                 [110/20] via 192.168.2.2, 01:23:45, GigabitEthernet0/2
C    192.168.1.0/24 is directly connected, GigabitEthernet0/1
S*   0.0.0.0/0 [1/0] via 192.168.1.254
'''

Template = r'''
Value Filldown PROTOCOL ([A-Z\*]+)
Value Filldown NETWORK (\d+\.\d+\.\d+\.\d+/\d+)
Value DISTANCE (\d+)
Value METRIC (\d+)
Value NEXT_HOP (\d+\.\d+\.\d+\.\d+)
Value INTERFACE (\S+)

Start
  ^${PROTOCOL}\s+${NETWORK}\s+\[${DISTANCE}/${METRIC}\]\s+via\s+${NEXT_HOP}(?:,\s+\S+,\s+${INTERFACE})? -> Record
  ^\s+\[${DISTANCE}/${METRIC}\]\s+via\s+${NEXT_HOP}(?:,\s+\S+,\s+${INTERFACE})? -> Record
  ^${PROTOCOL}\s+${NETWORK}\s+is\s+directly\s+connected,\s+${INTERFACE} -> Record
'''

parseTemplate(Title,InputData,Template)
