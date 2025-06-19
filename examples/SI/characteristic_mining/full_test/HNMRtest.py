import openai
import time
import random


def request_with_backoff(max_tries, func, *args, **kwargs):
    base_delay = random.uniform(15, 30)
    for n in range(max_tries):
        try:
            response = func(*args, **kwargs)
            return response
        except Exception as e:
            if n == max_tries - 1:
                return str(e)
            else:
                delay = base_delay * 2 ** n
                time.sleep(delay)
    return "error!"
    
def extract_1HNMR(input_text, api_key, model="gpt-4", base_url="https://api.openai.com/v1/chat/completions"):
    system_prompt = f"""
        You're an expert in chemistry. You will be provided with a text may containing 1H NMR data and lots of other information. I need you to find and summarize 1H NMR data in the text and output it in markdown tabular form.
        I need you to find the code name of the molecule, and summarize all the chemical shifts, splitting modes (for example, ddt), number of atom H and coupling constants J (if mentioned) that correspond to that code, and organize them in a single row.
        If the text does not contain sufficient information, do not make up information and give the answer as “N/A”.
        If a chemical shift corresponds to multiple coupling constants J, the multiple coupling constants J should output in parentheses.
        If any coupling constants J is not provided or you are unsure, use "N/A" instead. 

        If multiple molecules are provided, use multiple rows to represent them.
        If multiple chemical shifts, splitting modes, number of atom H are present, separate them using a comma in the same cell.
        You should only out put the table containing 3 columns: | code name | chemical shifts and J | splitting modes | number of atom H |

        Note that the code name always appears before its description. When working with text, ensure that the code name and corresponding description matches correctly to avoid false matches.

        """
    
    user_prompt = f"""
        You're an expert in chemistry. You will be provided with a text may containing 1H NMR data. I need you to find and summarize 1H NMR data in the text and output it in markdown tabular form.
        I need you to find the code name of the molecule, and summarize all the chemical shifts, splitting modes (for example, d), number of atom H and coupling constants J (if mentioned) that correspond to that code, and organize them in a single row.
        You should only output the table containing 3 columns: | code name | chemical shifts and J | splitting modes | number of atom H |
        Note that the code name always appears before its description. When working with text, ensure that the code name and corresponding description matches correctly to avoid false matches.


        Input_Text:<'''General information: Commercial reagents were used as received, unless otherwise indicated.
Tetrahydroisoquinolines 11 and cobalt catalysts2-5 were prepared according to literature precedent.
Nuclear magnetic resonance (NMR) spectra were recorded using Bruker AV-400 and AV-500
Tetramethylsilane (TMS) served as the internal standard for 1H NMR, and CDCl and CD CNserved as the internal standard for 13C NMR. The following abbreviations were used to express the<|endoftext|>'''>
        Answer:
        | code name | chemical shifts and J | splitting modes | number of atom H |
        |-----------|-----------------|-----------------|------------------|

------ 
        Input_Text:<'''1H NMR(300 MHz, CDCl ) δ 7.37-7.30 (m, 1H), 7.19-7.08 (m, 5H), 6.72 (d, J = 9.1 Hz, 2H), 2.54-2.40 (m, 1H),
2.38-2.15 (m, 3H), 2.14-2.00 (m, 1H), 1.88-1.82 (m, 2H), 1.77-1.67 (m, 1H). 13C NMR (75 MHz,
CDCl ) δ 211.87, 148.05, 140.18, 59.43, 54.25, 43.96, 43.28, 32.97, 28.76, 27.80, 25.83. IR (KBr, cm-1): 2921, 2851, 1706, 1595; HRMS (ESI) calcd for C H ONCl+: 340.1458, found 340.1460.3aa: Prepared according to the general procedure outlined above and
obtained as white solid (85% yield, 9:1 d.r., 99% ee). [α]D28 = -27.4 (c =
0.76, CHCl ). HPLC analysis: Daicel Chiralpak AS-H,hexane/iso-propanol = 95:5, flow rate = 0.7 mL/min, λ = 251 nm,
retention time: 9.60 min (minor) and 11.11 min (major). 1H NMR (500
MHz, CDCl ) δ 7.33 (d, J = 6.5 Hz, 1H), 7.21 (dd, J = 15.4, 7.9 Hz, 3H), 7.14-7.11 (m, 3H), 6.81(d, J = 8.5 Hz, 2H), 6.67 (t, J = 7.2 Hz, 1H), 5.65 (d, J = 8.5 Hz, 1H), 3.53 (t, J = 6.3 Hz, 2H),
3.03 (dt, J = 15.5, 5.6 Hz, 1H), 2.93-2.84 (m, 1H), 2.76-2.68 (m, 1H), 2.47 (d, J = 12.8 Hz, 1H),
2.30-2.20 (m, 2H), 2.10-2.03 (m, 1H), 1.85 (d, J = 3.2 Hz, 1H), 1.70-1.57 (m, 3H). 13C NMR (126
MHz, CDCl ) δ 212.06, 149.47, 140.46, 134.68, 129.35, 127.94, 127.33, 126.79, 126.43, 116.48,112.41, 59.43, 54.14, 43.65, 43.31, 32.91, 28.79, 27.83, 25.80. IR (KBr, cm-1): 3059, 2934, 2858,
1705, 1596, 1504, 1269, 746, 692; HRMS (ESI) calcd for C H ON+: 306.1852, found 306.1848.
3ad: Prepared according to the general procedure outlined above and
obtained as white solid (72% yield, 12:1 d.r., 97% ee). [α] 28 = -22.4(c = 1.13, CHCl ). HPLC analysis: Daicel Chiralpak AS-H,hexane/iso-propanol = 95:5, flow rate = 0.7 mL/min, λ = 251 nm,
retention time: 10.29 min (minor) and 12.19 min (major). 1H NMR (500 MHz, CDCl ) δ 7.36-7.30(m, 1H), 7.18-7.09 (m, 3H), 6.90 (dd, J = 12.8, 4.7 Hz, 2H), 6.76-6.71 (m, 2H), 5.52 (d, J = 8.4 Hz,
1H), 3.50 (dd, J = 10.2, 6.0 Hz, 2H), 3.00 (dt, J = 15.2, 5.8 Hz, 1H), 2.89-2.79 (m, 1H), 2.76-2.72
(m, 1H), 2.52-2.42 (m, 1H), 2.33-2.19 (m, 2H), 2.11-2.03 (m, 1H), 1.87 (d, J = 9.3 Hz, 1H),
1.76-1.51 (m, 3H). 13C NMR (126 MHz, CDCl ) δ 212.15, 156.32, 154.45, 146.25, 140.18, 134.55,128.12, 127.36, 126.84, 126.47, 115.72, 115.55, 113.85, 113.79, 59.46, 54.72, 44.16, 43.28, 32.86,
28.84, 27.44, 25.76. IR (KBr, cm-1): 2938, 2861, 1707, 1509, 1231, 812, 752; HRMS (ESI) calcd<|endoftext|>'''>
        Answer:
        | code name | chemical shifts and J | splitting modes | number of atom H |
        |-----------|-----------------|-----------------|------------------|----------------------|
        | 3aa | 7.33(6.5Hz), 7.21(15.4Hz, 7.9Hz), 7.14-7.11, 6.81(8.5Hz), 6.67(7.2Hz), 5.65(8.5Hz), 3.53(6.3Hz), 3.03(15.5Hz, 5.6Hz), 2.93-2.84, 2.76-2.68, 2.47(12.8Hz), 2.30-2.20, 2.10-2.03, 1.85(3.2Hz), 1.70-1.57 | d, dd, m, d, t, d, t, dt, m, m, d, m, m, d, m | 1, 3, 3, 2, 1, 1, 2, 1, 1, 1, 1, 2, 1, 1, 3 |
        | 3ad | 7.36-7.30, 7.18-7.09, 6.90(12.8Hz, 4.7Hz), 6.76-6.71, 5.52(8.4Hz), 3.50(10.2Hz, 6.0Hz), 3.00(15.2Hz, 5.8Hz), 2.89-2.79, 2.76-2.72, 2.52-2.42, 2.33-2.19, 2.11-2.03, 1.87(9.3Hz), 1.76-1.51 | m, m, dd, m, d, dd, dt, m, m, m, m, m, d, m | 1, 3, 2, 2, 1, 2, 1, 1, 1, 1, 2, 1, 1, 3 |

------
        Input_Text:<'''1H NMR (500 MHz, CDCl ) δ 7.33 (d, J = 6.5 Hz, 1H), 7.21 (dd, J = 15.4, 7.9 Hz, 3H), 7.14-7.11 (m, 3H), 6.81(d, J = 8.5 Hz, 2H), 6.67 (t, J = 7.2 Hz, 1H), 5.65 (d, J = 8.5 Hz, 1H), 3.53 (t, J = 6.3 Hz, 2H),
3.03 (dt, J = 15.5, 5.6 Hz, 1H), 2.93-2.84 (m, 1H). 13C NMR (126
MHz, CDCl ) δ 212.06, 149.47, 140.46, 134.68, 129.35, 127.94. IR (KBr, cm-1): 3059, 2934, 2858,
1705, 1596, 1504; HRMS (ESI) calcd for C H ON+: 306.1852, found 306.1848.3ab: Prepared according to the general procedure outlined above and
obtained as white solid (87% yield, 6:1 d.r., 98% ee). [α] 28 = -27.7 (c= 0.43, CHCl ). HPLC analysis: Daicel Chiralpak AS-H,hexane/iso-propanol = 95:5, flow rate = 0.7 mL/min, λ = 251 nm,
retention time: 10.76 min (minor) and 12.75 min (major). 1H NMR
(300 MHz, CDCl ) δ 7.37-7.30 (m, 1H), 7.19-7.08 (m, 5H), 6.72 (d, J = 9.1 Hz, 2H), 5.60 (d, J =S8
8.5 Hz, 1H), 3.57-3.42 (m, 2H), 3.09-2.79 (m, 2H), 2.77-2.62 (m, 1H), 2.54-2.40 (m, 1H),
2.38-2.15 (m, 3H), 2.14-2.00 (m, 1H), 1.88-1.82 (m, 2H), 1.77-1.67 (m, 1H). 13C NMR (75 MHz,
CDCl ) δ 211.87, 148.05, 140.18, 134.45, 129.08, 127.96,<|endoftext|>'''>
        Answer:
        | code name | chemical shifts and J | splitting modes | number of atom H |
        |-----------|-----------------|-----------------|------------------|----------------------|
        | 3ab | 7.37-7.30, 7.19-7.08, 6.72(9.1Hz), 5.60(8.5Hz), 3.57-3.42, 3.09-2.79, 2.77-2.62, 2.54-2.40, 2.38-2.15, 2.14-2.00, 1.88-1.82, 1.77-1.67 | m, m, d, d, m, m, m, m, m, m, m, m | 1, 5, 2, 1, 2, 2, 1, 1, 3, 1, 2, 1 |

------
    """

    test_text = input_text
    if test_text == '\n':#新加的
        print('''| code name | chemical shifts and J | splitting modes | number of atom H |
        |-----------|-----------------|-----------------|------------------|----------------------|''')
        print('\n')
        return '''| code name | chemical shifts and J | splitting modes | number of atom H |
        |-----------|-----------------|-----------------|------------------|----------------------|'''

    extract_prompt = user_prompt + f"""
        Input_Text:<'''{test_text}<|endoftext|>'''>
        Answer:
        """

    print(extract_prompt)
    client = openai.OpenAI(api_key=api_key, base_url=base_url)
    response = request_with_backoff(5, client.chat.completions.create, model=model, 
                                    messages=[{"role": "system", "content": system_prompt},
                                                {"role": "user", "content": extract_prompt}],
                                    temperature=0.1)
    try:
        print(response.choices[0].message.content)
        print('\n')
        return str(response.choices[0].message.content)
    except:
        print('error!')
        print(response)
        print('\n')
        return response
