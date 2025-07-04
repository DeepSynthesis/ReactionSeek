import pubchempy as pcp

import pandas as pd

def pubchem_standardize(input_filename, output_filename):
    column = ['volume', 'article', 'raw_name', 'CAS', 'CIRsmiles', 'PubChemsmiles']
    input_df = pd.read_csv(input_filename + '.csv')
    result_df = pd.DataFrame(columns=column)
    data = []
    for i in range(len(input_df)):
        print(i)
        if input_df['CIRsmiles'][i] != 'Not Found':
            data.append([input_df['volume'][i], input_df['article'][i], input_df['raw_name'][i], input_df['CAS'][i], input_df['CIRsmiles'][i], input_df['CIRsmiles'][i]])
        else:
            if input_df['CAS'][i] == 'Not Found':
                data.append([input_df['volume'][i], input_df['article'][i], input_df['raw_name'][i], input_df['CAS'][i], input_df['CIRsmiles'][i], 'Not Found'])
            else:
                try:
                    smi = pcp.get_compounds(input_df['CAS'][i], 'name')[0].isomeric_smiles                
                except:
                    data.append([input_df['volume'][i], input_df['article'][i], input_df['raw_name'][i], input_df['CAS'][i], input_df['CIRsmiles'][i], 'Not Found'])
                    continue
                if smi is not None:
                    data.append([input_df['volume'][i], input_df['article'][i], input_df['raw_name'][i], input_df['CAS'][i], input_df['CIRsmiles'][i], smi])
                else:
                    data.append([input_df['volume'][i], input_df['article'][i], input_df['raw_name'][i], input_df['CAS'][i], input_df['CIRsmiles'][i], 'Not Found'])

    result_df = pd.concat([result_df, pd.DataFrame(data, columns=column)], ignore_index=True)
    result_df.to_csv(output_filename + '.csv', index=None)

if __name__ == '__main__':
    input_filename = 'names_cir'
    output_filename = 'names_cir_pub'
    pubchem_standardize(input_filename, output_filename)



