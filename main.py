import os.path
import shutil

import utils

if __name__ == '__main__':
    # 获得输入输出相关的路径
    input_path = input('批量发票所在路径:(默认为当前路径)')
    if input_path == '':
        input_path = './'
    output_path = input('数据输出路径:(默认为当前路径下的data.csv)')
    if output_path == '':
        output_path = './data.csv'

    pdfs = utils.get_pdf_files_abs_path(input_path)
    results = [] # 保存发票字典的列表
    for p in pdfs:
        # 遍历每个pdf
        result = utils.get_items_from_invoice(p)
        if result is None:
            # 提取失败了 扔进failed文件夹
            failed_dir = os.path.join(input_path,'failed')
            if not os.path.exists(failed_dir):
                os.mkdir(failed_dir)
            shutil.copy(p,failed_dir)
        else:
            results.append(result)
    with open(output_path,'w',encoding='utf-8') as fp:
        # 输出到文件
        content = utils.extract_items_to_csv(results)
        fp.write(content)

