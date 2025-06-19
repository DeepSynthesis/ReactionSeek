from g4f.client import Client

from g4f.cookies import set_cookies
import time
import random

def request_with_backoff(max_tries, func, *args, **kwargs):
    base_delay = random.uniform(5, 10)
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
    

system_prompt = f"""
    You're an expert in chemistry. You will be provided with a text containing IR data, extract the data completely and output it in tabular form.
    You need to find the code name of the molecule, test method and find all the IR wave number that correspond to that code, and organize them in a single row.
    You should only extract the complete IR data and should not output the line when the data is incomplete. If you find a compound code that cannot find complete IR data because of text truncation, do not output it.

    If multiple molecules are provided, use multiple rows to represent them.
    Output table should have 3 columns: | code name | test method | wave numbers |

    Example 1:
    Text:<'''Figure S2. The reaction set-up of the scale-up reaction.
3aa: Prepared according to the general procedure outlined above and
obtained as white solid (85% yield, 9:1 d.r., 99% ee). [α]D28 = -27.4 (c =
0.76, CHCl ). HPLC analysis: Daicel Chiralpak AS-H,hexane/iso-propanol = 95:5, flow rate = 0.7 mL/min, λ = 251 nm,
retention time: 9.60 min (minor) and 11.11 min (major). 1H NMR (500
MHz, CDCl ) δ 7.33 (d, J = 6.5 Hz, 1H), 7.21 (dd, J = 15.4, 7.9 Hz, 3H), 7.14-7.11 (m, 3H), 6.81(d, J = 8.5 Hz, 2H), 6.67 (t, J = 7.2 Hz, 1H), 5.65 (d, J = 8.5 Hz, 1H), 3.53 (t, J = 6.3 Hz, 2H),
3.03 (dt, J = 15.5, 5.6 Hz, 1H), 2.93-2.84 (m, 1H), 2.76-2.68 (m, 1H), 2.47 (d, J = 12.8 Hz, 1H),
2.30-2.20 (m, 2H), 2.10-2.03 (m, 1H), 1.85 (d, J = 3.2 Hz, 1H), 1.70-1.57 (m, 3H). 13C NMR (126
MHz, CDCl ) δ 212.06, 149.47, 140.46, 134.68, 129.35, 127.94, 127.33, 126.79, 126.43, 116.48,112.41, 59.43, 54.14, 43.65, 43.31, 32.91, 28.79, 27.83, 25.80. IR (KBr, cm-1): 3059, 2934, 2858,
1705, 1596, 1504, 1269, 746, 692; HRMS (ESI) calcd for C H ON+: 306.1852, found 306.1848.3ab: Prepared according to the general procedure outlined above and
obtained as white solid (87% yield, 6:1 d.r., 98% ee). [α] 28 = -27.7 (c= 0.43, CHCl ). HPLC analysis: Daicel Chiralpak AS-H,hexane/iso-propanol = 95:5, flow rate = 0.7 mL/min, λ = 251 nm,
retention time: 10.76 min (minor) and 12.75 min (major). 1H NMR
(300 MHz, CDCl ) δ 7.37-7.30 (m, 1H), 7.19-7.08 (m, 5H), 6.72 (d, J = 9.1 Hz, 2H), 5.60 (d, J =S8
8.5 Hz, 1H), 3.57-3.42 (m, 2H), 3.09-2.79 (m, 2H), 2.77-2.62 (m, 1H), 2.54-2.40 (m, 1H),
2.38-2.15 (m, 3H), 2.14-2.00 (m, 1H), 1.88-1.82 (m, 2H), 1.77-1.67 (m, 1H). 13C NMR (75 MHz,
CDCl ) δ 211.87, 148.05, 140.18, 134.45, 129.08, 127.96, 127.30, 126.98, 126.59, 116.21, 113.48,59.43, 54.25, 43.96, 43.28, 32.97, 28.76, 27.80, 25.83. IR (KBr, cm-1): 2921, 2851, 1706, 1595,
1495, 1392, 1124, 807, 749; HRMS (ESI) calcd for C H ONCl+: 340.1458, found 340.1460.3ac: Prepared according to the general procedure outlined above and
obtained as white solid (92% yield, 10:1 d.r., 96% ee). [α]D28 = -34.6
(c = 0.71, CHCl ). HPLC analysis: Daicel Chiralpak AS-H,hexane/iso-propanol = 95:5, flow rate = 0.7 mL/min, λ = 251 nm,
retention time: 11.01 min (minor) and 13.09 min (major). 1H NMR (300 MHz, CDCl ) δ 7.32 (d, J= 7.5 Hz, 1H), 7.26 (d, J = 8.1 Hz, 2H), 7.14 (s, 3H), 6.67 (d, J = 9.0 Hz, 2H), 5.60 (d, J = 8.5 Hz,
1H), 3.56-3.41 (m, 2H), 3.04-2.85 (m, 2H), 2.77-2.62 (m, 1H), 2.46 (d, J = 12.7 Hz, 1H),
2.37-2.15 (m, 2H), 2.12-2.03 (m, 1H), 1.85 (d, J = 5.5 Hz, 1H), 1.75-1.48 (m, 3H). 13C NMR (75
MHz, CDCl ) δ 211.83, 148.44, 140.15, 134.43, 131.96, 127.94, 127.29, 127.00, 126.60, 116.55,113.94, 59.40, 54.17, 43.92, 43.27, 32.97, 28.75, 27.83, 25.83. IR (KBr, cm-1): 2936, 2854, 1705,
1588, 1494, 1392, 1124, 805, 750; HRMS (ESI) calcd for C H ONBr+: 384.0958, found384.0954.
3ad: Prepared according to the general procedure outlined above and
obtained as white solid (72% yield, 12:1 d.r., 97% ee). [α] 28 = -22.4(c = 1.13, CHCl ). HPLC analysis: Daicel Chiralpak AS-H,hexane/iso-propanol = 95:5, flow rate = 0.7 mL/min, λ = 251 nm,
retention time: 10.29 min (minor) and 12.19 min (major). 1H NMR (500 MHz, CDCl ) δ 7.36-7.30(m, 1H), 7.18-7.09 (m, 3H), 6.90 (dd, J = 12.8, 4.7 Hz, 2H), 6.76-6.71 (m, 2H), 5.52 (d, J = 8.4 Hz,
1H), 3.50 (dd, J = 10.2, 6.0 Hz, 2H), 3.00 (dt, J = 15.2, 5.8 Hz, 1H), 2.89-2.79 (m, 1H), 2.76-2.72
(m, 1H), 2.52-2.42 (m, 1H), 2.33-2.19 (m, 2H), 2.11-2.03 (m, 1H), 1.87 (d, J = 9.3 Hz, 1H),
1.76-1.51 (m, 3H). 13C NMR (126 MHz, CDCl ) δ 212.15, 156.32, 154.45, 146.25, 140.18, 134.55,128.12, 127.36, 126.84, 126.47, 115.72, 115.55, 113.85, 113.79, 59.46, 54.72, 44.16, 43.28, 32.86,
28.84, 27.44, 25.76. IR (KBr, cm-1): 2938, 2861, 1707, 1509, 1231, 812, 752; HRMS (ESI) calcd
for C H ONF+: 324.1758, found 324.1754.S9'''>
    Answer:
    | code name | test method | wave numbers |
    |-----------|-------------|--------------|
    | 3aa | KBr | 3059, 2934, 2858, 1705, 1596, 1504, 1269, 746, 692 |
    | 3ab | KBr | 2921, 2851, 1706, 1595, 1495, 1392, 1124, 807, 749 |
    | 3aa | KBr | 2936, 2854, 1705, 1588, 1494, 1392, 1124, 805, 750 |
    | 3aa | KBr | 2938, 2861, 1707, 1509, 1231, 812, 752 |

    """

test_text = '''
3ae: Prepared according to the general procedure outlined above and
obtained as white solid (51% yield, 3:1 d.r., 96% ee). [α] 28 = -40.0(c = 0.51, CHCl ). HPLC analysis: Daicel Chiralpak AS-H,hexane/iso-propanol = 98:2, flow rate = 0.7 mL/min, λ = 251 nm,
retention time: 11.52 min (minor) and 12.83 min (major). 1H NMR (500 MHz, CDCl ) δ 7.43 (d, J= 8.9 Hz, 2H), 7.34 (d, J = 6.9 Hz, 1H), 7.19-7.12 (m, 3H), 6.81 (d, J = 8.7 Hz, 2H), 5.76 (d, J =
8.6 Hz, 1H), 3.62-3.48 (m, 2zH), 2.75 – 2.67 (m, 1H), 2.48 (d, J = 13.2 Hz, 1H), 2.26 (td, J = 12.8,
6.1 Hz, 1H), 2.20-2.06 (m, 2zH), 1.91-1.83 (m, 1H), 1.72-1.49 (m,3H). 13C NMR (125 MHz,
CDCl ) δ 211.55, 151.51, 140.05, 134.32, 127.86, 127.27, 127.18, 126.77, 126.67, 126.64, 113.03,111.25, 59.31, 54.04, 44.09, 43.25, 33.05, 28.69, 28.07, 25.87. IR (KBr, cm-1): 2922, 2853, 1708,
1616, 1526, 1492, 1107, 816, 751; HRMS (ESI) calcd for C H ONF +: 374.1726, found374.1722.
3af: Prepared according to the general procedure outlined above and
obtained as white solid (73% yield, 5:1 d.r., 96% ee). [α] 28 = -23.2(c = 0.38, CHCl ). HPLC analysis: Daicel Chiralpak OD-H,hexane/iso-propanol = 99:1, flow rate = 1.0 mL/min, λ = 251 nm,
retention time: 7.60 min (minor) and 12.40 min (major). 1H NMR (500 MHz, CDCl ) δ 7.36-7.30(m, 1H), 7.16-7.07 (m, 3H), 7.01 (d, J = 8.4 Hz, 2H), 6.73 (d, J = 8.6 Hz, 2H), 5.57 (d, J = 8.6 Hz,
1H), 3.52 (t, J = 6.3 Hz, 2H), 3.01 (dt, J = 15.6, 5.9 Hz, 1H), 2.85 (dt, J = 20.9, 6.1 Hz, 1H),
2.77-2.68 (m, 1H), 2.50-2.44 (m, 1H), 2.25-2.29 (m, 2H), 2.22 (s, 3H), 2.09-2.02 (m, 1H),
1.87-1.81 (m, 1H), 1.74-1.57 (m, 3H). 13C NMR (126 MHz, CDCl ) δ 212.25, 147.45, 140.43,134.75, 129.87, 128.03, 127.40, 126.72, 126.35, 125.73, 112.76, 59.48, 54.35, 43.70, 43.32, 32.88,
28.85, 27.64, 25.75, 20.29. IR (KBr, cm-1): 3009, 2923, 2857, 1705, 1616, 1518, 1447, 1123, 796,
752; HRMS (ESI) calcd for C H ON+: 320.2009, found 320.2006.3ag: Prepared according to the general procedure outlined above
and obtained as white solid (70% yield, 10:1 d.r., 97% ee). [α] 28 =-19.5 (c = 1.31, CHCl ). HPLC analysis: Daicel Chiralpak AS-H,hexane/iso-propanol = 95:5, flow rate = 0.7 mL/min, λ = 251 nm,
retention time: 13.06 min (minor) and 16.60 min (major). 1H NMR (500 MHz, CDCl ) δ 7.36-7.29(m, 1H), 7.17-7.06 (m, 3H), 6.83-6.74 (m, 4H), 5.45 (d, J = 8.5 Hz, 1H), 3.73 (s, 3H), 3.52-3.48
S10
(m, 2H), 2.98 (dt, J = 15.8, 6.4 Hz, 1H), 2.84-2.71 (m, 2H), 2.49-2.45 (m, 1H), 2.31-2.23 (m, 2H),
2.09-2.02 (m, 1H), 1.88-1.84 (m, 1H), 1.74-1.58 (m, 3H). 13C NMR (125 MHz, CDCl ) δ 212.42,151.68, 144.36, 140.23, 134.73, 128.23, 127.44, 126.67, 126.31, 114.88, 114.76, 59.45, 55.90,
54.91, 44.11, 43.27, 32.74, 28.89, 27.18, 25.64. IR (KBr, cm-1): 2919, 2849, 1705, 1503, 1463,
1243, 1038, 812, 752; HRMS (ESI) calcd for C H O N+: 336.1958, found 336.1952.3ah: Prepared according to the general procedure outlined above and
obtained as colorless oil (72% yield, 8:1 d.r., 95% ee). [α] 28 = -23.7 (c= 0.38, CHCl ). HPLC analysis: Daicel Chiralpak OD-H,hexane/iso-propanol = 95:5, flow rate = 0.7 mL/min, λ = 251 nm,
retention time: 12.46 min (minor) and 15.22 min (major). 1H NMR (400 MHz, CDCl ) δ 7.32 (d, J= 7.5 Hz, 1H), 7.12 (dd, J = 9.9, 6.7 Hz, 4H), 6.46-6.42 (m, 1H), 6.36 (s, 1H), 6.26 (d, J = 8.1 Hz,
1H), 5.64 (d, J = 8.5 Hz, 1H), 3.78 (s, 3H), 3.52 (t, J = 6.1 Hz, 2H), 3.03 (dt, J = 15.5, 5.5 Hz, 1H),
2.95-2.85 (m, 1H), 2.71 (t, J = 12.7 Hz, 1H), 2.47 (d, J = 12.9 Hz, 1H), 2.31-2.19 (m, 2H), 2.07 (d,
J = 10.2 Hz, 1H), 1.86 (d, J = 4.9 Hz, 1H), 1.67-1.62 (m, 3H). 13C NMR (100 MHz, CDCl ) δ211.89, 160.96, 150.94, 140.45, 134.68, 130.00, 127.94, 127.36, 126.84, 126.48, 105.68, 101.34,
99.00, 59.43, 55.27, 54.33, 43.82, 43.30, 32.90, 28.78, 27.94, 25.82. IR (KBr, cm-1): 2921, 2851,
1705, 1608, 1574, 1497, 1216, 812, 750; HRMS (ESI) calcd for C H O N+: 336.1958, found336.1955.
3ai: Prepared according to the general procedure outlined above and
obtained as white solid (73% yield, 6:1 d.r., 97% ee). [α] 28 = -28.5(c = 0.38, CHCl ). HPLC analysis: Daicel Chiralpak AS-H,hexane/iso-propanol = 98:2, flow rate = 0.7 mL/min, λ = 251 nm,
retention time: 8.84 min (minor) and 10.34 min (major). 1H NMR (500 MHz, CDCl ) δ 7.32 (d, J= 7.1 Hz, 1H), 7.12 (dd, J = 13.3, 5.1 Hz, 3H), 6.96 (d, J = 8.3 Hz, 1H), 6.63 (s, 1H), 6.58 (dd, J =
8.3, 2.4 Hz, 1H), 5.56 (d, J = 8.6 Hz, 1H), 3.60-3.45 (m, 2H), 3.01 (dt, J = 15.6, 6.0 Hz, 1H), 2.83
(dt, J = 20.5, 5.9 Hz, 1H), 2.73 (dt, J = 12.4, 7.1 Hz, 1H), 2.47 (d, J = 12.8 Hz, 1H), 2.26 (td, J =
12.6, 6.0 Hz, 2H), 2.21 (s, 3H), 2.14 (s, 3H), 2.08-1.99 (m, 1H), 1.85 (d, J = 9.8 Hz, 1H),
1.75-1.57 (m, 3H). 13C NMR (125 MHz, CDCl ) δ 212.32, 147.89, 140.44, 137.31, 134.77, 130.42,128.05, 127.45, 126.67, 126.30, 124.63, 114.29, 110.36, 77.41, 77.16, 76.91, 59.43, 54.35, 43.59,
43.35, 32.90, 28.89, 27.59, 25.75, 20.59, 18.65. IR (KBr, cm-1): 3020, 2922, 2857, 1708, 1614,
S11

'''

extract_prompt = f"""
    Text:<'''{test_text}'''>
    """

client = Client()
print(extract_prompt)
response = request_with_backoff(5, client.chat.completions.create, model="gpt-3.5-turbo", 
                                messages=[{"role": "system", "content": system_prompt},
                                            {"role": "user", "content": extract_prompt}])
try:
    print(response.choices[0].message.content)
except:
    print('error!')
    print(response)
print('\n')

'''
gpt-3.5-turbo能用
gpt-4能用
4-turbo g4f.errors.ResponseStatusError: Response 403: Failed to create conversation

'''