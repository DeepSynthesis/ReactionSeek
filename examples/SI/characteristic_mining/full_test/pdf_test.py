import pdfplumber
import re

def pdf_reader(path, output_name):
    output_list = []
    with pdfplumber.open(path) as pdf:

        with open(output_name, 'w', encoding='utf-8') as f:
            for page in pdf.pages:
                raw_text = page.extract_text()
                mid_text = raw_text.replace('Me ', '')
                mid_text = mid_text.replace('Me', '')
                mid_text = mid_text.replace('–', '-')
                mid_text = mid_text.replace('δ', 'δ ')
                mid_text = mid_text.replace('\nN ', '\n')
                mid_text_no_number = re.sub(r'\n(?:\d+\s)*\d+\n', '', mid_text)#删除一行数字（化学式的脚标）
                mid_text_no_number_letter = re.sub(r'\n(?:[A-Z]+\s)*[A-Z]+\n', '', mid_text_no_number)#删除一行字母（绝大多数的旋光脚标）
                mid_text_no_number_letter = re.sub(r'\n(?:[A-Z0-9]+\s)*[A-Z0-9]+\n', '', mid_text_no_number_letter)
                mid_text_no_number_letter = re.sub(r'\n\d+$', '', mid_text_no_number_letter)#删除页码
                mid_text_no_number_letter = re.sub(r'\nS\d+$', '', mid_text_no_number_letter)#删除页码
                f.write(mid_text_no_number_letter)
                f.write('\nEND\n\n')
            f.write('FILE_END\n')
        for page in pdf.pages:
            raw_text = page.extract_text()
            mid_text = raw_text.replace('Me ', '')
            mid_text = mid_text.replace('Me', '')
            mid_text = mid_text.replace('–', '-')
            mid_text = mid_text.replace('δ', 'δ ')
            mid_text = mid_text.replace('\nN ', '\n')
            mid_text_no_number = re.sub(r'\n(?:\d+\s)*\d+\n', '', mid_text)#删除一行数字（化学式的脚标）
            mid_text_no_number_letter = re.sub(r'\n(?:[A-Z]+\s)*[A-Z]+\n', '', mid_text_no_number)#删除一行字母（绝大多数的旋光脚标）
            mid_text_no_number_letter = re.sub(r'\n(?:[A-Z0-9]+\s)*[A-Z0-9]+\n', '', mid_text_no_number_letter)
            mid_text_no_number_letter = re.sub(r'\n\d+$', '', mid_text_no_number_letter)#删除页码
            mid_text_no_number_letter = re.sub(r'\nS\d+$', '', mid_text_no_number_letter)#删除页码
            output_list.append(mid_text_no_number_letter)
    return output_list

