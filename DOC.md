サンプル：解析したいテキスト
たとえば、以下のようなルーターの出力から「インターフェース名」「IPアドレス」「状態」を表にしたいとします。
text
Interface              IP-Address      Status
GigabitEthernet0/1     192.168.1.1     up
GigabitEthernet0/2     10.0.0.1        down
コードは注意してご使用ください。

1. Valueパート（項目の定義）
テンプレートの冒頭で、「どんな名前の箱に、どんな文字を入れるか」を正規表現で定義します。
textfsm
Value INTERFACE \((\S+)\)
Value IP_ADDRESS (\d+\.\d+\.\d+\.\d+)
Value STATUS (\w+)
コードは注意してご使用ください。

Value: 定義を始めるときの決まり文句です。
INTERFACE など: 項目名（変数名）です。大文字で書くのが一般的です。
(\S+) など: 抜き出す文字のルール（正規表現）を必ず丸括弧 () で囲みます。
\S+ ＝ 空白以外の文字の連続
\d+\.\d+\.\d+\.\d+ ＝ IPアドレスの形式
\w+ ＝ 英数字の連続
2. Stateパート（読み進め方のルール）
Valueの定義が終わったら、空行を1行挟んで、テキストを1行ずつどう処理するかを書きます。
textfsm
Start
  ^\${INTERFACE}\s+\({IP_ADDRESS}\s+\){STATUS} -> Record
コードは注意してご使用ください。

Start: 処理の開始地点を表す名前です（必ず Start から始まります）。
先頭の半角スペース2つ: Start の中身であることを示すため、インデント（字下げ）をします。
^: 行の先頭を表します。
${INTERFACE}: 上で定義した Value を当てはめる場所です。
\s+: スペースの連続を表します。
-> Record: 「この行で当てはめたデータを1行分の結果として保存して、次の行へ進む」という命令です。
完成したテンプレートと出力結果
上記を合体させたものが完成形です（空行が区切りになります）。
textfsm
Value INTERFACE \((\S+)\)
Value IP_ADDRESS (\d+\.\d+\.\d+\.\d+)
Value STATUS (\w+)

Start
  ^\${INTERFACE}\s+\({IP_ADDRESS}\s+\){STATUS} -> Record
コードは注意してご使用ください。

仕組みの動き：
1行目の Interface IP-Address Status は、IPアドレスの形式に一致しないため自動で無視されます。
2行目と3行目はルールに一致するため、データが抜き出され、最終的に以下のような表形式（リスト）になります。
python
[
  ['GigabitEthernet0/1', '192.168.1.1', 'up'],
  ['GigabitEthernet0/2', '10.0.0.1', 'down']
]
コードは注意してご使用ください。

よく使うアクション（-> の後ろに書く命令）
命令	意味	使う場面
Record	今のデータを保存して、値をリセットする	表の1行分のデータが完成したとき
Next	何も保存せず、次の行のチェックへ進む	不要な行を読み飛ばしたいとき（省略可）
Continue	今の行を保存せず、同じ行に対して下のルールも続けてチェックする	1つの行に複数のルールを適用したいとき
-> 別のState名	別のルール群（State）へ移動する	特定の見出しが出てきたら読み方を変えたいとき
この基本を押さえたうえで、次に知りたいステップがあれば教えてください：
複数行にまたがるデータ（1つの機器情報が3〜4行に分かれている場合など）の抜き出し方
Pythonから実際にテンプレートを動かすサンプルコード
手元にある具体的なテキスト用のテンプレート作成
ご希望に合わせて解説や作成を行います。

Value の定義時にオプションフラグである Key と List を組み合わせることで、「1つの機器やインターフェースに対して、複数の値が紐づくデータ」をきれいに整理できます。
具体的なサンプルを使って仕組みを解説します。
サンプル：解析したいテキスト
たとえば、1つのVLANに「複数のポート」が所属しているテキストを解析したいとします。
text
VLAN   Name       Ports
10     Sales      Gi0/1, Gi0/2
20     Dev        Gi0/3
                  Gi0/4
コードは注意してご使用ください。

※VLAN 20のように、ポートが改行されて複数行にまたがっているケースを想定します。
Key と List の役割
Value と項目名の間にオプションを挟みます（複数ある場合はカンマ区切り）。
textfsm
Value Key VLAN_ID (\d+)
Value NAME (\w+)
Value List PORTS \((\S+)\)
コードは注意してご使用ください。

Key（主キーの指定）:
「この項目がデータの見出し（一意の識別子）である」と指定します。データベースの主キーと同じ役割で、行を識別する基準になります。
List（リスト化の指定）:
通常、同じ項目に新しい値が入ると上書きされますが、List をつけると上書きせず配列（リスト）にどんどん追加していきます。
テンプレートの書き方（複数行対応）
List を使う場合、1行ずつデータを溜め込み、次のデータに切り替わるタイミングで Record（保存）するのが基本パターンです。
textfsm
Value Key VLAN_ID (\d+)
Value NAME (\w+)
Value List PORTS \((\S+)\)

Start
  # 1. 新しいVLANの行が来たら、前のデータを保存（Record）してから新しい行を読み込む
  ^\d+ -> Continue.Record
  ^\${VLAN_ID}\s+\({NAME}\s+\){PORTS}
  # 2. 行頭に数字がなく、スペースから始まる行（続きのポート）をListに追加する
  ^\s+\${PORTS}
コードは注意してご使用ください。

ここでのポイント（2つの重要なテクニック）
Continue.Record の動き:
^\d+ -> Continue.Record は、「行頭が数字（新しいVLANの開始）だったら、今まで溜めていた前のVLANのデータを保存し（Record）、そのまま同じ行に対して下のルールも実行する（Continue）」という便利な決まり文句です。
最初の行（VLAN 10）のときはまだ何も溜まっていないため、空データは無視されて下の行に進みます。
最後の EOF（自動保存）:
TextFSMはテキストの最後（End Of File）に到達すると、溜まっていた最後のデータ（VLAN 20）を自動で Record してくれます。
出力結果
上記のテンプレートを実行すると、以下のように PORTS がリスト形式でまとまった結果が得られます。
python
[
  ['10', 'Sales', ['Gi0/1,', 'Gi0/2']],
  ['20', 'Dev', ['Gi0/3', 'Gi0/4']]
]
コードは注意してご使用ください。

（※Gi0/1, のカンマを消したい場合は、PORTS の正規表現を ([^,\s]+) のように調整します）
まとめ：オプションの使い分け
オプション	役割	こんなときに使う
Key	データの基準（見出し）にする	どの項目が「1レコードの主役」かを明確にしたいとき
List	値を上書きせず配列に溜める	1つの見出しに、複数のIP・ポート・ルートなどが紐づくとき
Filldown	前の行の値をコピーして引き継ぐ	上の行にしか書かれていない見出しを、下の行にも埋めたいとき
Filldown と List は似ていますが、「行を分けたいときは Filldown」「1つの行の中に配列としてまとめたいときは List」と使い分けるのがコツです。
次はどのステップに進みましょうか？
Filldown を使った場合との違い（同じテキストを Filldown で処理したときの出力比較）
カンマ区切りの文字列（Gi0/1, Gi0/2）を1行から綺麗にリスト化する正規表現のコツ
Pythonコードでの実行方法（結果のリストを辞書型に変換して扱う方法など）
ご希望のものがあればお知らせください。

clitable（Command Line Interface Table）は、TextFSMに標準で同梱されているモジュールです。
通常のTextFSMでは「このテキストにはこのテンプレートを使う」と人間が毎回指定する必要がありますが、clitable を使うと「OSの種類（CiscoやLinuxなど）」や「実行したコマンド名」を渡すだけで、適切なテンプレートを自動検索して解析してくれます。
ネットワーク自動化で有名な Netmiko や ntc-templates も、内部でこの仕組みを利用しています。
1. フォルダ構成
clitable を使うには、テンプレートをまとめたフォルダの中に index という名前の管理ファイルを1つ用意します。
text
templates/
 ├── index                         # どのテンプレートを使うかの対応表
 ├── cisco_ios_show_ip_int.textfsm # Cisco用のテンプレート
 └── linux_df_h.textfsm            # Linux用のテンプレート
コードは注意してご使用ください。

2. index ファイルの書き方
index ファイルは、CSV形式で「テンプレートファイル名」と「条件（OSやコマンド名）」を紐づけます。
csv
Template, Hostname, Platform, Command
cisco_ios_show_ip_int.textfsm, .*, cisco_ios, sh[[ow]] ip int[[erface]] br[[ief]]
linux_df_h.textfsm, .*, linux, df -h
コードは注意してご使用ください。

ここが便利！
[[ ]] による省略表記への対応:
sh[[ow]] のように二重括弧で囲むと、sh でも show でも一致するようになります（CLIの省略コマンドに自動対応できます）。
上から順に評価:
条件に一致するものを上から探し、最初に見つかったテンプレートを自動適用します。
3. Pythonでの実行サンプルコード
textfsm ライブラリから clitable をインポートして使います。
python
from textfsm import clitable

# 1. indexファイルがあるディレクトリを指定して初期化
cli_table = clitable.CliTable('index', 'templates')

# 2. 検索条件（PlatformやCommand）を辞書で定義
attributes = {
    'Command': 'sh ip int br',  # 省略形でもindexのルールで一致する
    'Platform': 'cisco_ios'
}

# 3. 解析したい生テキスト（実際はSSHなどで機器から取得した文字列）
raw_output = """
Interface              IP-Address      OK? Method Status                Protocol
GigabitEthernet0/1     192.168.1.1     YES manual up                    up
GigabitEthernet0/2     10.0.0.1        YES manual down                  down
"""

# 4. 自動でテンプレートを選んで解析を実行
cli_table.ParseCmd(raw_output, attributes)

# 5. 結果の表示
print("見出し:", cli_table.header)
for row in cli_table:
    print("データ:", list(row))
コードは注意してご使用ください。

実行結果
text
見出し: ['INTERFACE', 'IP_ADDRESS', 'STATUS']
データ: ['GigabitEthernet0/1', '192.168.1.1', 'up']
データ: ['GigabitEthernet0/2', '10.0.0.1', 'down']
コードは注意してご使用ください。

clitable を使うメリットまとめ
プログラム側の分岐（if文）が不要になる: 「もしCiscoならテンプレートA、LinuxならテンプレートB…」といった条件分岐をPythonコードに書く必要がなくなります。
テンプレートの追加が簡単: 新しいコマンドに対応したいときは、テンプレートファイルを追加して index に1行書き足すだけで済みます。
clitable の仕組みについて、さらに知りたいことはありますか？
すでに数百種類のテンプレートと index が揃っている ntc-templates の導入・活用方法
抽出した cli_table の結果を Pythonの辞書（dict）やJSON形式に変換する コード例
Hostname を使った機器ごとのテンプレート切り替え（特定のホスト名だけ別ルールにする方法）
興味のあるものがあればお知らせください。
