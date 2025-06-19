import pubchempy as pcp

import pandas as pd

def pubchem_after_glm(input_filename, output_filename):
    column = ['raw_name', 'processed_name', 'pubchem_name']
    input_df = pd.read_csv(input_filename + '.csv')
    result_df = pd.DataFrame(columns=column)
    data = []
    for i in range(len(input_df)):
        print(i)
        if input_df['processed_name'][i] == 'none':
            data.append([input_df['raw_name'][i], input_df['processed_name'][i], 'None'])
        else:
            try:
                name = input_df['processed_name'][i]
                smi = pcp.get_compounds(name, 'name')[0].isomeric_smiles                
            except Exception as e:
                data.append([input_df['raw_name'][i], input_df['processed_name'][i], 'Not Found'])
                continue
            if smi is not None:
                data.append([input_df['raw_name'][i], input_df['processed_name'][i], smi])
            else:
                data.append([input_df['raw_name'][i], input_df['processed_name'][i], 'Not Found'])

    result_df = pd.concat([result_df, pd.DataFrame(data, columns=column)], ignore_index=True)
    result_df.to_csv(output_filename + '.csv', index=None)

if __name__ == '__main__':
    input_filename = 'names_cir_pub_cas_ckecked_pub_name_pub_opsin_prename'
    output_filename = 'names_cir_pub_cas_ckecked_pub_name_pub_opsin_prename_pubchemdata'
    pubchem_after_glm(input_filename, output_filename)



