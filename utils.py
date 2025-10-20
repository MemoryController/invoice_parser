import os
import pdfplumber

ITEM_TITLE = ['name','class','unit','count','single_price','total_price','tax_rate','total_tax']
def get_items_from_invoice(path:str)->dict|None: # 如果返回None则代表fail了
    with pdfplumber.open(path) as pdf:
        full_text = ""
        for page in pdf.pages:
            full_text += page.extract_text() + "\n"
        collect_flag = False
        invoice = {}
        invoice_id = ''
        invoice_date = ''
        invoice_company = ''
        items = []
        # 有些项目名称分了多行，需要存储上一个的名称
        last_line_name = ''

        for line in full_text.split('\n'):
            if '项目名称' in line:
                collect_flag = True
                continue
            if '合 计' in line:
                break
            if '发票号码' in line:
                invoice_id = line.split('：')[-1]
                continue
            if '开票日期' in line:
                invoice_date = line.split('：')[-1][0:4]+line.split('：')[-1][5:7]+line.split('：')[-1][8:10]
                continue
            if '销 名称：' in line:
                invoice_company = line.split('：')[-1]
                continue
            if collect_flag:
                cells = line.split()
                if len(cells) == 1:
                    # 上一行剩余的名称没写完
                    for item in items:
                        if item['name'] == last_line_name:
                            # 追加名称
                            last_line_name += cells[0]
                            item['name'] = last_line_name
                            break
                else:
                    # 新的一个项目名称
                    last_line_name = cells[0]
                    item = {
                        'name': cells[0],
                    }
                    for i in range(-1,-len(cells),-1):
                        # 倒序遍历这行的元素
                        item[ITEM_TITLE[i]] = cells[i]
                    for i in range(-len(cells),-len(ITEM_TITLE),-1):
                        # 填充没有的
                        item[ITEM_TITLE[i]] = '-'
                    items.append(item)

        invoice['id'] = invoice_id
        invoice['date'] = invoice_date
        invoice['company'] = invoice_company
        invoice['items'] = items
        if len(items) != 0:
            return invoice
        else:
            return None

def extract_items_to_csv(invoices:list[dict],remove_prefix=True)->str:
    """
    将发票内容转换成csv的文字
    :return: csv文件内容
    """
    content = '发票号码,项目名称,规格型号,单位,数量,单价,金额,税率,税额,日期,供应商\n'
    for invoice in invoices:
        id_num = invoice['id']
        date = invoice['date']
        company = invoice['company']
        for item in invoice['items']:
            # 遍历每个项目，添加内容
            if remove_prefix:
                item["name"] = item["name"].split('*')[-1]
            content += f'{id_num},{item["name"]},{item["class"]},{item["unit"]},{item["count"]},{item["single_price"]},{item["total_price"]},{item["tax_rate"]},{item["total_tax"]},{date},{company}\n'

    return content

def get_pdf_files_abs_path(dir_path)->list[str]:
    """
    获得所有pdf文件的绝对路径
    :param dir_path: 操作路径
    :return: pdf文件的路径列表
    """
    pdf_files = [
        os.path.abspath(os.path.join(dir_path, f))
        for f in os.listdir(dir_path)
        if f.lower().endswith(".pdf")
    ]
    return pdf_files




