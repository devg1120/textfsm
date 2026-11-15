from pathlib import Path
import sys

parent_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(parent_dir))

##########################################
import textfsm

InputData = '''
VLAN   Name       Ports
10     Sales      Gi0/1, Gi0/2
20     Dev        Gi0/3
                  Gi0/4, Gi0/5
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
