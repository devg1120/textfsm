# -*- coding: utf-8 -*-
from pathlib import Path
import sys

parent_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(parent_dir))

##########################################
import textfsm

InputData = '''
2022_01_01 banana 100
           orange 200
           carrot 300
2022_12_31 banana 200
'''

filename = Path(__file__).resolve()
test_name = filename.stem
template_filename = f'{test_name}.template'

with open(template_filename) as template:
    fsm = textfsm.TextFSM(template)
    result = fsm.ParseText(InputData)

print(InputData)
print("---------------------")
print(fsm)
print("---------------------")
print(fsm.header)
print(*result, sep='\n')
