from pathlib import Path
import sys

parent_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(parent_dir))

##########################################
import textfsm

InputData = '''
  Gi0/1   192.168.1.1
  Gi0/2   192.168.1.2
Group: LAN-Segment
  Gi0/3   10.0.0.1
Group: WAN-Segment
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
