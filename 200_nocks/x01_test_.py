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
    print("## ", end="")
    print("="*(tl+3), Title)
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
print("[LINK] (ttps://yoloz.hatenablog.com/entry/2022/02/06/034008)")
##########################################

InputData = '''
2022_01_01 banana 100
           orange 200
           carrot 300
2022_12_31 banana 200
'''

Title = "BASIC"
Template = r'''
Value Date (\d+_\d+_\d+)
Value Item (\D+)
Value Qty (\d+)

Start
  ^${Date}\s*${Item}\s*${Qty} -> Record
  ^\s*${Item}\s*${Qty} -> Record
'''

parseTemplate(Title,InputData,Template)
#-----------------------------------------
Title = "Filldown"
Template = r'''
Value Filldown Date (\d+_\d+_\d+)
Value Item (\D+)
Value Qty (\d+)

Start
  ^${Date}\s*${Item}\s*${Qty} -> Record
  ^\s*${Item}\s*${Qty} -> Record
'''

parseTemplate(Title,InputData,Template)
#-----------------------------------------
Title = "EOF State"
Template = r'''
Value Filldown Date (\d+_\d+_\d+)
Value Item (\D+)
Value Qty (\d+)

Start
  ^${Date}\s*${Item}\s*${Qty} -> Record
  ^\s*${Item}\s*${Qty} -> Record

EOF
'''

parseTemplate(Title,InputData,Template)
#-----------------------------------------
Title = "Fillup"
Template = r'''
Value Fillup Date (\d+_\d+_\d+)
Value Item (\D+)
Value Qty (\d+)

Start
  ^${Date}\s*${Item}\s*${Qty} -> Record
  ^\s*${Item}\s*${Qty} -> Record
'''

parseTemplate(Title,InputData,Template)
#-----------------------------------------
Title = "Required"
Template = r'''
Value Required Date (\d+_\d+_\d+)
Value Item (\D+)
Value Qty (\d+)

Start
  ^${Date}\s*${Item}\s*${Qty} -> Record
  ^\s*${Item}\s*${Qty} -> Record
'''

parseTemplate(Title,InputData,Template)
#-----------------------------------------
Title = "List"
Template = r'''
Value Date (\d+_\d+_\d+)
Value List Item (\D+)
Value List Qty (\d+)

Start
  ^\d -> Continue.Record
  ^${Date}\s*${Item}\s*${Qty}
  ^\s*${Item}\s*${Qty}
'''

parseTemplate(Title,InputData,Template)

