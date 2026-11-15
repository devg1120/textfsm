from pathlib import Path
import sys

parent_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(parent_dir))

##########################################
import textfsm

InputData = '''
GigabitEthernet0/1 is up, line protocol is up
  Description: Uplink to Core Switch
  Internet address is 192.168.1.1/24
  MTU 1500 bytes, BW 1000000 Kbit/sec

GigabitEthernet0/2 is administratively down, line protocol is down
  MTU 1500 bytes, BW 1000000 Kbit/sec
'''

filename = Path(__file__).resolve()
test_name = filename.stem
template_filename = f'{test_name}.template'

with open(template_filename,  encoding='utf-8') as template:
    fsm = textfsm.TextFSM(template)
    result = fsm.ParseText(InputData)

print(InputData)
print("---------------------")
print(fsm)
print("---------------------")
print(fsm.header)
print(*result, sep='\n')
