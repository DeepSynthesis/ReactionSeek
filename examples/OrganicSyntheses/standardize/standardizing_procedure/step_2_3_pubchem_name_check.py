import pubchempy as pcp

import pandas as pd

def pubchem_standard_name_check(input_filename, output_filename):
    column = ['volume', 'article', 'raw_name', 'CAS', 'CIRsmiles', 'PubChemsmiles', 'PubChem_after_cas_check_smiles', 'PubChem_name_smiles']
    input_df = pd.read_csv(input_filename + '.csv')
    result_df = pd.DataFrame(columns=column)
    data = []
    for i in range(len(input_df)):
        print(i)

        if input_df['PubChem_after_cas_check_smiles'][i] != 'Not Found':
            data.append([input_df['volume'][i], input_df['article'][i], input_df['raw_name'][i], input_df['CAS'][i], input_df['CIRsmiles'][i], input_df['PubChemsmiles'][i], input_df['PubChem_after_cas_check_smiles'][i], input_df['PubChem_after_cas_check_smiles'][i]])
        else:
            if ':' in input_df['raw_name'][i]:
                try:
                    name = input_df['raw_name'][i].split(':')[1].split(';')[0].strip()
                    smi = pcp.get_compounds(name, 'name')[0].isomeric_smiles                
                except Exception as e:
                    data.append([input_df['volume'][i], input_df['article'][i], input_df['raw_name'][i], input_df['CAS'][i], input_df['CIRsmiles'][i], input_df['PubChemsmiles'][i], input_df['PubChem_after_cas_check_smiles'][i], 'Not Found'])
                    continue
            else:
                if ',\n' in input_df['raw_name'][i]:
                    try:
                        name = input_df['raw_name'][i].split(',\n')[1].split(' (')[0].strip()
                        smi = pcp.get_compounds(name, 'name')[0].isomeric_smiles                
                    except Exception as e:
                        data.append([input_df['volume'][i], input_df['article'][i], input_df['raw_name'][i], input_df['CAS'][i], input_df['CIRsmiles'][i], input_df['PubChemsmiles'][i], input_df['PubChem_after_cas_check_smiles'][i], 'Not Found'])
                        continue
                else:
                    try:
                        name = input_df['raw_name'][i].split(' (')[0].strip()
                        smi = pcp.get_compounds(name, 'name')[0].isomeric_smiles                
                    except Exception as e:
                        data.append([input_df['volume'][i], input_df['article'][i], input_df['raw_name'][i], input_df['CAS'][i], input_df['CIRsmiles'][i], input_df['PubChemsmiles'][i], input_df['PubChem_after_cas_check_smiles'][i], 'Not Found'])
                        continue
            if smi is not None:
                data.append([input_df['volume'][i], input_df['article'][i], input_df['raw_name'][i], input_df['CAS'][i], input_df['CIRsmiles'][i], input_df['PubChemsmiles'][i], input_df['PubChem_after_cas_check_smiles'][i], smi])
            else:
                data.append([input_df['volume'][i], input_df['article'][i], input_df['raw_name'][i], input_df['CAS'][i], input_df['CIRsmiles'][i], input_df['PubChemsmiles'][i], input_df['PubChem_after_cas_check_smiles'][i], 'Not Found'])

    result_df = pd.concat([result_df, pd.DataFrame(data, columns=column)], ignore_index=True)
    result_df.to_csv(output_filename + '.csv', index=None)

if __name__ == '__main__':
    input_filename = 'names_cir_pub_cas_ckecked_pub'
    output_filename = 'names_cir_pub_cas_ckecked_pub_name_pub'
    pubchem_standard_name_check(input_filename, output_filename)

