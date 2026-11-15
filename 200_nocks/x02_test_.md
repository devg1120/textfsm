
##### ======================================== CISCO show ip interface brief
```
# input #
Interface              IP-Address      OK? Method Status                Protocol
GigabitEthernet0/0     192.168.1.1     YES NVRAM  up                    up
GigabitEthernet0/1     unassigned      YES unset  administratively down down
----------------------------------------
# template #
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

----------------------------------------
# result #
['INTERFACE', 'IP_ADDRESS', 'OK', 'METHOD', 'STATUS', 'PROTOCOL']
['GigabitEthernet0/0', '192.168.1.1', 'YES', 'NVRAM', 'up', 'up']
['GigabitEthernet0/1', 'unassigned', 'YES', 'unset', 'administratively down', 'down']
```

##### ======================================== CISCO show vlan brief
```
# input #
VLAN Name                             Status    Ports
---- -------------------------------- --------- -------------------------------
1    default                          active    Gi0/1, Gi0/2
10   Sales_Dept                       active    Gi0/3, Gi0/4, Gi0/5, Gi0/6
                                                Gi0/7, Gi0/8
1002 fddi-default                     act/unsup
----------------------------------------
# template #
Value Required VLAN_ID (\d+)
Value NAME (\S+)
Value STATUS (\S+)
Value List PORTS ([^,\s]+)

Start
  ^VLAN\s+Name -> ParseVlan

ParseVlan
  ^\d+ -> Continue.Record
  ^${VLAN_ID}\s+${NAME}\s+${STATUS}(?:\s+${PORTS})? -> Continue
  ^${VLAN_ID}\s+${NAME}\s+${STATUS}(?:\s+[^,\s]+,)+\s*${PORTS} -> Continue
  ^\s+${PORTS} -> Continue
  ^\s+(?:[^,\s]+,)+\s*${PORTS} -> Continue
  ^VLAN\s+Type -> Record End

----------------------------------------
# result #
['VLAN_ID', 'NAME', 'STATUS', 'PORTS']
['1', 'default', 'active', ['Gi0/1', 'Gi0/2']]
['10', 'Sales_Dept', 'active', ['Gi0/3', 'Gi0/6', 'Gi0/7', 'Gi0/8']]
['1002', 'fddi-default', 'act/unsup', [None]]
```

##### ======================================== CISCO cdp neighbors detail -----
```
# input #
-------------------------
Device ID: Core-SW01.example.local
Entry address(es):
  IP address: 10.0.0.1
Platform: cisco WS-C3850-24T,  Capabilities: Switch IGMP
Interface: GigabitEthernet0/1,  Port ID (outgoing port): GigabitEthernet1/0/24
----------------------------------------
# template #
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

----------------------------------------
# result #
['NEIGHBOR', 'MGMT_IP', 'PLATFORM', 'LOCAL_INTF', 'REMOTE_INTF']
['Core-SW01.example.local', '10.0.0.1', 'cisco WS-C3850-24T', 'GigabitEthernet0/1', 'GigabitEthernet1/0/24']
```

##### ======================================== CISCO show ip route
```
# input #
O    10.1.0.0/16 [110/20] via 192.168.1.2, 01:23:45, GigabitEthernet0/1
                 [110/20] via 192.168.2.2, 01:23:45, GigabitEthernet0/2
C    192.168.1.0/24 is directly connected, GigabitEthernet0/1
S*   0.0.0.0/0 [1/0] via 192.168.1.254
----------------------------------------
# template #
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

----------------------------------------
# result #
['PROTOCOL', 'NETWORK', 'DISTANCE', 'METRIC', 'NEXT_HOP', 'INTERFACE']
['O', '10.1.0.0/16', '110', '20', '192.168.1.2', 'GigabitEthernet0/1']
['O', '10.1.0.0/16', '110', '20', '192.168.2.2', 'GigabitEthernet0/2']
['C', '192.168.1.0/24', '', '', '', 'GigabitEthernet0/1']
['S*', '0.0.0.0/0', '1', '0', '192.168.1.254', '']
['S*', '0.0.0.0/0', '', '', '', '']
```
