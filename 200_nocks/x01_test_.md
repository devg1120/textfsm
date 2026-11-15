[LINK] (ttps://yoloz.hatenablog.com/entry/2022/02/06/034008)

## =========================================== BASIC
"""
# input #
2022_01_01 banana 100
           orange 200
           carrot 300
2022_12_31 banana 200
----------------------------------------
# template #
Value Date (\d+_\d+_\d+)
Value Item (\D+)
Value Qty (\d+)

Start
  ^${Date}\s*${Item}\s*${Qty} -> Record
  ^\s*${Item}\s*${Qty} -> Record

----------------------------------------
# result #
['Date', 'Item', 'Qty']
['2022_01_01', 'banana ', '100']
['', 'orange ', '200']
['', 'carrot ', '300']
['2022_12_31', 'banana ', '200']
"""

## =========================================== Filldown
"""
# input #
2022_01_01 banana 100
           orange 200
           carrot 300
2022_12_31 banana 200
----------------------------------------
# template #
Value Filldown Date (\d+_\d+_\d+)
Value Item (\D+)
Value Qty (\d+)

Start
  ^${Date}\s*${Item}\s*${Qty} -> Record
  ^\s*${Item}\s*${Qty} -> Record

----------------------------------------
# result #
['Date', 'Item', 'Qty']
['2022_01_01', 'banana ', '100']
['2022_01_01', 'orange ', '200']
['2022_01_01', 'carrot ', '300']
['2022_12_31', 'banana ', '200']
['2022_12_31', '', '']
"""

## =========================================== EOF State
"""
# input #
2022_01_01 banana 100
           orange 200
           carrot 300
2022_12_31 banana 200
----------------------------------------
# template #
Value Filldown Date (\d+_\d+_\d+)
Value Item (\D+)
Value Qty (\d+)

Start
  ^${Date}\s*${Item}\s*${Qty} -> Record
  ^\s*${Item}\s*${Qty} -> Record

EOF

----------------------------------------
# result #
['Date', 'Item', 'Qty']
['2022_01_01', 'banana ', '100']
['2022_01_01', 'orange ', '200']
['2022_01_01', 'carrot ', '300']
['2022_12_31', 'banana ', '200']
"""

## =========================================== Fillup
"""
# input #
2022_01_01 banana 100
           orange 200
           carrot 300
2022_12_31 banana 200
----------------------------------------
# template #
Value Fillup Date (\d+_\d+_\d+)
Value Item (\D+)
Value Qty (\d+)

Start
  ^${Date}\s*${Item}\s*${Qty} -> Record
  ^\s*${Item}\s*${Qty} -> Record

----------------------------------------
# result #
['Date', 'Item', 'Qty']
['2022_01_01', 'banana ', '100']
['2022_12_31', 'orange ', '200']
['2022_12_31', 'carrot ', '300']
['2022_12_31', 'banana ', '200']
"""

## =========================================== Required
"""
# input #
2022_01_01 banana 100
           orange 200
           carrot 300
2022_12_31 banana 200
----------------------------------------
# template #
Value Required Date (\d+_\d+_\d+)
Value Item (\D+)
Value Qty (\d+)

Start
  ^${Date}\s*${Item}\s*${Qty} -> Record
  ^\s*${Item}\s*${Qty} -> Record

----------------------------------------
# result #
['Date', 'Item', 'Qty']
['2022_01_01', 'banana ', '100']
['2022_12_31', 'banana ', '200']
"""

## =========================================== List
"""
# input #
2022_01_01 banana 100
           orange 200
           carrot 300
2022_12_31 banana 200
----------------------------------------
# template #
Value Date (\d+_\d+_\d+)
Value List Item (\D+)
Value List Qty (\d+)

Start
  ^\d -> Continue.Record
  ^${Date}\s*${Item}\s*${Qty}
  ^\s*${Item}\s*${Qty}

----------------------------------------
# result #
['Date', 'Item', 'Qty']
['2022_01_01', ['banana ', 'orange ', 'carrot '], ['100', '200', '300']]
['2022_12_31', ['banana '], ['200']]
"""
