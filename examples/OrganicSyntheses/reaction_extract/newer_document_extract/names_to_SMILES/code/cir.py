import pandas as pd
import cirpy as cir

column = ['volume', 'article', 'raw_name', 'CAS', 'CIRsmiles']
# input_df = pd.read_csv('/home/ljw/rxn_pred/SyntheticGPT/data/name_set/Volume71-80.csv')
input_df = pd.read_csv('names.csv')
result_df = pd.DataFrame(columns=column)
data = []
for i in range(len(input_df)):
    print(i)
    if input_df['CAS'][i] == 'Not Found':
        data.append([input_df['volume'][i], input_df['article'][i], input_df['raw_name'][i], input_df['CAS'][i], 'Not Found'])
    else:
        try:
            smi = cir.resolve(input_df['CAS'][i], 'smiles')
        except:
            data.append([input_df['volume'][i], input_df['article'][i], input_df['raw_name'][i], input_df['CAS'][i], 'Not Found'])
            continue
        if smi is not None:
            data.append([input_df['volume'][i], input_df['article'][i], input_df['raw_name'][i], input_df['CAS'][i], smi])
        else:
            data.append([input_df['volume'][i], input_df['article'][i], input_df['raw_name'][i], input_df['CAS'][i], 'Not Found'])

result_df = pd.concat([result_df, pd.DataFrame(data, columns=column)], ignore_index=True)
# result_df.to_csv('/home/ljw/rxn_pred/SyntheticGPT/data/name_set/Volume71-80_cir.csv', index=None)
result_df.to_csv('names_cir.csv', index=None)
