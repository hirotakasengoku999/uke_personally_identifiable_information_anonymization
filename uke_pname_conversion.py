import PySimpleGUI as sg
import uke_pname_conversion
from pathlib import Path
import shutil, time, mojimoji, yaml

with open('./setting.yaml', 'r', encoding='utf8') as f:
    master_dict = yaml.safe_load(f)

def make_newtext(target_file):
    # ファイルを１行ずつ読み込み、リストにする
    with open(target_file, encoding='cp932') as f:
        rows = f.readlines()

    # 一番最初に出てくるREレコードの列数が38なら出来高、30ならDPC
    m_dict = ""
    for row in rows:
        row_list =  row.split(',')
        if row_list[0] == 'RE':
            if len(row_list) == 38:
                m_dict = master_dict['RECEIPTC']
            elif len(row_list) == 30:
                m_dict = master_dict['RECEIPTD']
            else:
                m_dict = master_dict['RECEIPTC']
            break

    # 変換する場所
    hospital_row = m_dict['hospital_name']['row']
    patient_row = m_dict['patient_name']['row']
    patient_cols = m_dict['patient_name']['col']
    patientid_col = m_dict['patient_id']['col']
    new_text = ""
    for row in rows:

        # 病院名
        if row_list[0] == hospital_row:
            row_list[m_dict['hospital_name']['col'] - 1] = "テスト病院"
            new_text += ','.join(row_list)

        # 患者名
        elif patient_row in row_list:
            if row_list[0] == patient_row:
                pid = row_list[patientid_col - 1]
                for col_num in patient_cols:
                    row_list[col_num - 1] = mojimoji.han_to_zen(pid) 
            elif row_list.index(patient_row) > 0:
                interrupt_num = row_list.index(patient_row)
                pid = row_list[patientid_col + interrupt_num - 1]
                for col_num in patient_cols:
                    cn = col_num - 1 + interrupt_num
                    row_list[cn] = mojimoji.han_to_zen(pid)
            new_text += ','.join(row_list)

        else:
            new_text += i
    return(new_text)


def conv(input_path, output_path):
    # アウトプットフォルダを空にする
    if output_path.exists():
        shutil.rmtree(output_path)
    output_path.mkdir()

    # インプットパスのフォルダーリストをfoldersに格納する
    current = Path.cwd()
    files = input_path.glob('**/*.UKE')

    for file in files:
        sg.Print(f'「{file.name}」を変換します...')
        out_file = output_path.joinpath(str(file).replace(str(input_path), "")[1:])
        if not out_file.parent.exists():
            out_file.parent.mkdir(parents=True)
        new_text = make_newtext(file)
        with open(out_file, mode='x') as f:
            f.write(new_text)
        sg.Print(f'「{file.name}」を変換しました')
    sg.Print("全てのファイルを変換しました。")
    time.sleep(1)


layout = [
    [sg.Text('入力フォルダを選択してください')],
    [sg.InputText(), sg.FolderBrowse(key="-INPUTDIR-")],
    [sg.Text('出力フォルダを選択してください')],
    [sg.InputText(), sg.FolderBrowse(key="-OUTPUTDIR-")],
    [sg.Button('実行', key='-SUBMIT-')]
]

window = sg.Window('レセプトの患者氏名を匿名化するアプリ',
    layout)

while True:
    event, values = window.read()
    if event == '-SUBMIT-':
        if values['-INPUTDIR-'] and values['-OUTPUTDIR-']:
            conv(Path(values['-INPUTDIR-']), Path(values['-OUTPUTDIR-']))
    if event == sg.WIN_CLOSED:
        break