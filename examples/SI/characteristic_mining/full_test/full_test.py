import pandas as pd
import openai
from pdf_test import pdf_reader
from HNMRtest import extract_1HNMR
from HPLCtest import extract_HPLC
from MStest import extract_MS
from utils import split_on_found

def main(tasks, api_key, model, base_url):
    si_pdf = [
            'angew_2020_luosz_Catalytic Asymmetric Electrochemical α‐Arylation of Cyclic β‐Ketocarbonyls with Anodic Benzyne Intermediates',
            'ccsc_2021_luosz-Catalytic Asymmetric Addition and Telomerization of Butadiene with Enamine Intermediates',
            'jacs_2016_luosz_Asymmetric Retro-Claisen Reaction by Chiral Primary Amine Catalysis',
            'nat-com_2023_luosz_Asymmetric α-allylic allenylation of β-ketocarbonyls and aldehydes by synergistic Pd chiral primary amine catalysis',
            'chem-com_2020_luosz_Collective enantioselective total synthesis of (+)-sinensilactam A, (+)-lingzhilactone B and (−)-lingzhiol divergent reactivity of styrene',
            'science_2022_luosz_Deracemization through photochemical EZ isomerization of enamines'
    ]
    pdf_path = 'si_pdf/'
    csv_path = 'csv_output/'
    text_path = 'text_output/'
    len_limit = len('''4aa, Colorless oil (5 h, 16.5 mg, 67% yield 94% ee). [] 20 = 46.7 (c = 0.96, CHCl ) 1H NMR (400 MHz, CDCl ) δ 7.40–7.33 (m, 2H), 7.33–7.27 (m, 1H), 7.25–7.20 (m, 2H), 4.22 (qq, J = 7.0, 3.7 Hz, 2H), 2.85–2.72 (m, 1H), 2.66–2.51 (m, 2H), 2.43–2.32
    (m, 1H), 2.09–1.92 (m, 1H), 1.91–1.68 (m, 3H), 1.24 (t, J = 7.2 Hz, 3H) ppm;13C NMR (101 MHz, CDCl ) δ 206.8, 171.4, 136.9, 128.5,127.9, 127.7, 77.5, 66.6, 61.8, 40.9, 35.5, 27.8, 22.3, 14.1 ppm; IR (KBr, cm-1): 2938, 2359, 1714, 1499, 1216, 906, 729; HRMS (ESI)
    calcd for C H O +: 247.1329, found 247.1325 HPLC analysis: Daicel Chiralpak OD-H, hexane/iso-propanol = 49:1, flow rate = 0.5mL/min,  = 204 nm, retention time: 19.916 min (minor) and 21.275 min (major).
    4ab, Colorless oil (5 h, 16.1 mg, 69% yield, 96% ee). [] 20 = -38.5 (c = 0.78, CHCl ) 1H NMR (400 MHz, CDCl ) δ 7.37(dd, J = 8.2, 6.5 Hz, 2H), 7.34–7.27 (m, 1H), 7.25–7.19 (m, 2H), 3.73 (s, 3H), 2.80–2.70 (m, 1H), 2.55 (t, J = 6.7 Hz, 2H), 2.42 (dddd,
    J = 13.8, 8.2, 3.8, 1.3 Hz, 1H), 2.04–1.91 (m, 1H), 1.81 (dddd, J = 22.0, 13.8, 5.7, 4.0 Hz, 3H) ppm;13C NMR (101 MHz, CDCl ) δ206.7, 171.9, 136.7, 128.6, 127.9, 127.8, 66.7, 52.8, 40.8, 35.3, 27.8, 22.2 ppm; IR (KBr, cm-1): 2939, 2360, 1714, 1215, 905, 728;
    HRMS (ESI) calcd for C H O+: 233.1172, found 233.1168 HPLC analysis: Daicel Chiralpak IC-H, hexane/iso-propanol = 19:1, flowrate = 1.0 mL/min,  = 205 nm, retention time: 21.770 min (minor) and 23.135 min (major).
    4ac, Colorless oil (5 h, 17.6 mg, 65% yield, 94% ee). [] 20 = 63.2 (c = 0.83, CHCl ) 1H NMR (400 MHz, CDCl ) δ7.36 (dd, J = 8.2, 6.6 Hz, 2H), 7.33–7.28 (m, 1H), 7.25–7.20 (m, 2H), 4.22–4.03 (m, 2H), 2.76 (dtd, J = 14.0, 3.9, 2.0 Hz, 1H), 2.57
    (dd, J = 7.7, 5.1 Hz, 2H), 2.45–2.32 (m, 1H), 1.98 (ddt, J = 8.2, 5.9, 3.0 Hz, 1H), 1.82 (dtt, J = 12.4, 9.8, 4.6 Hz, 3H), 1.68–1.51 (m,''')
    if 'H_NMR' in tasks:
        for path in si_pdf:
            text_list = pdf_reader(pdf_path+path+'.pdf', text_path+path+'.txt')
            columns = ['path', 'item_num', 'summary'] # Initialize an empty dataframe with the desired columns
            result_df = pd.DataFrame(columns=columns)
            output_list = []
            for i in range(len(text_list)):
                if i < len(text_list) - 1:
                    before_input, after = split_on_found(text_list[i])#用于解决串号
                    if len(text_list[i+1]) > len_limit:
                        after_input = after + '\n' + text_list[i+1][:len_limit]
                    else:
                        after_input = after + '\n' +text_list[i+1]
                    print(path+': '+str(i))
                    if before_input != '':
                        before_output = extract_1HNMR(before_input, api_key, model, base_url)
                        after_output = extract_1HNMR(after_input, api_key, model, base_url)
                        output_list.append([path, i, before_output])
                        output_list.append([path, i, after_output])
                    else:
                        after_output = extract_1HNMR(after_input, api_key, model, base_url)
                        output_list.append([path, i, after_output])
            result_df = pd.concat([result_df, pd.DataFrame(output_list, columns=columns)], ignore_index=True)
            result_df.to_csv(csv_path+path+'_HNMR.csv', index=None)
    if 'HPLC' in tasks:
        for path in si_pdf:
            text_list = pdf_reader(pdf_path+path+'.pdf', text_path+path+'.txt')
            columns = ['path', 'item_num', 'summary'] # Initialize an empty dataframe with the desired columns
            result_df = pd.DataFrame(columns=columns)
            output_list = []
            for i in range(len(text_list)):
                if i < len(text_list) - 1:
                    before_input, after = split_on_found(text_list[i])#用于解决串号
                    if len(text_list[i+1]) > len_limit:
                        after_input = after + '\n' + text_list[i+1][:len_limit]
                    else:
                        after_input = after + '\n' +text_list[i+1]
                    print(path+': '+str(i))
                    if before_input != '':
                        before_output = extract_HPLC(before_input, api_key, model, base_url)
                        after_output = extract_HPLC(after_input, api_key, model, base_url)
                        output_list.append([path, i, before_output])
                        output_list.append([path, i, after_output])
                    else:
                        after_output = extract_HPLC(after_input, api_key, model, base_url)
                        output_list.append([path, i, after_output])
            result_df = pd.concat([result_df, pd.DataFrame(output_list, columns=columns)], ignore_index=True)
            result_df.to_csv(csv_path+path+'_HPLC.csv', index=None)
    if 'MS' in tasks:
        for path in si_pdf:
            text_list = pdf_reader(pdf_path+path+'.pdf', text_path+path+'.txt')
            columns = ['path', 'item_num', 'summary'] # Initialize an empty dataframe with the desired columns
            result_df = pd.DataFrame(columns=columns)
            output_list = []
            for i in range(len(text_list)):
                if i < len(text_list) - 1:
                    before_input, after = split_on_found(text_list[i])#用于解决串号
                    if len(text_list[i+1]) > len_limit:
                        after_input = after + '\n' + text_list[i+1][:len_limit]
                    else:
                        after_input = after + '\n' +text_list[i+1]
                    print(path+': '+str(i))
                    if before_input != '':
                        before_output = extract_MS(before_input, api_key, model, base_url)
                        after_output = extract_MS(after_input, api_key, model, base_url)
                        output_list.append([path, i, before_output])
                        output_list.append([path, i, after_output])
                    else:
                        after_output = extract_MS(after_input, api_key, model, base_url)
                        output_list.append([path, i, after_output])
            result_df = pd.concat([result_df, pd.DataFrame(output_list, columns=columns)], ignore_index=True)
            result_df.to_csv(csv_path+path+'_MS.csv', index=None)

if __name__ == '__main__':
    tasks = ['1HNMR', 'HPLC', 'MS']
    api_key = 'your api key'# Your API key.
    model = 'gpt-4'# Data mining model.
    base_url = 'https://api.openai.com/v1/chat/completions'# The API endpoint.
    main(tasks, api_key, model, base_url)