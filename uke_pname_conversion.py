'''
UKEファイルの個人情報を以下のようにマスキングします。
■病院名：「テスト病院」に変更
    IRレコード、7列目
■患者氏名：全角患者IDに変更
    医科:RE 5、37列目
    DPC:RE 5、29列目
    ※レコード識別情報が4列目にある場合は上記列番号＋3
'''
import os, shutil, time, mojimoji, yaml


with open('./setting.yaml', 'r', encoding='utf8') as f:
    master_dict = yaml.safe_load(f)


def make_newtext(target_file, file):
    # ファイルを１行ずつ読み込み、リストにする
    with open(target_file, encoding='cp932') as f:
        l = f.readlines()

    new_text = ""
    for i in l:
        list_i = i.split(',')
        work_str = ""

        # 変換する場所
        m_dict = master_dict[file[:8]]
        hospital_row = m_dict['hospital_name']['row']
        patient_row = m_dict['patient_name']['row']
        patient_cols = m_dict['patient_name']['col']
        patientid_col = m_dict['patient_id']['col']
        # 病院名
        if list_i[0] == hospital_row:
            list_i[m_dict['hospital_name']['col'] - 1] = "テスト病院"
            new_text += ','.join(list_i)

        # 患者名
        elif patient_row in list_i:
            if list_i[0] == patient_row:
                pid = list_i[patientid_col - 1]
                for col_num in patient_cols:
                    list_i[col_num - 1] = mojimoji.han_to_zen(pid) 
            elif list_i.index(patient_row) > 0:
                interrupt_num = list_i.index(patient_row)
                pid = list_i[patientid_col + interrupt_num - 1]
                for col_num in patient_cols:
                    cn = col_num - 1 + interrupt_num
                    list_i[cn] = mojimoji.han_to_zen(pid)
            new_text += ','.join(list_i)

        else:
            new_text += i
    return(new_text)


def conv(input_path, output_path):
    # アウトプットフォルダを空にする
    shutil.rmtree(output_path)
    os.makedirs(output_path)

    # インプットパスのフォルダーリストをfoldersに格納する
    base_dir = os.getcwd()
    dirs = os.listdir(input_path)
    folders = [f for f in dirs if os.path.isdir(os.path.join(input_path, f))]

    for folder in folders:
        target_folder = os.path.join(input_path, folder)

        # UKEファイルリスを作成
        files = os.listdir(target_folder)
        uke_files = [f for f in files if '.UKE' in f]

        # 年月フォルダ直下にUKEファイルが４つ格納されていた場合
        if uke_files:
            # アウトプットフォルダーを生成
            out_path = os.path.join(output_path, folder)
            os.makedirs(out_path)
            for file in uke_files:
                target_file = os.path.join(target_folder, file)
                new_text = make_newtext(target_file, file)

                out_file = os.path.join(out_path, file)
                with open(out_file, mode='x') as f:
                    f.write(new_text) 
                print("「" + file + "」を変換しました")
        # 年月フォルダ直下にUKEファイルが格納されていなかった場合
        else:
            # 中間フォルダリスト
            middle_folders = [f for f in files if os.path.isdir(os.path.join(target_folder, f))]
            for middle_folder in middle_folders:
                # アウトプットフォルダーを生成
                out_path = os.path.join(output_path, folder, middle_folder)
                os.makedirs(out_path)

                leaf_folder = os.path.join(target_folder, middle_folder)
                files = os.listdir(leaf_folder)
                uke_files = [f for f in files if '.UKE' in f]

                for file in uke_files:
                    target_file = os.path.join(leaf_folder, file)
                    new_text = make_newtext(target_file, file)
                    out_file = os.path.join(out_path, file)
                    with open(out_file, mode='x') as f:
                        f.write(new_text)
                    print("「" + file + "」を変換しました")
        print(f'{folder}を変換しました')

    print("全てのファイルを変換しました。")
    time.sleep(3)

if __name__ == '__main__':
    current = os.getcwd()
    input_path = os.path.join(current, 'in')
    output_path = os.path.join(current, 'out')
    conv(input_path, output_path)