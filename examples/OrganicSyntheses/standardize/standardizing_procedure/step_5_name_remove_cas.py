import re
import pandas as pd

def name_remove_cas(input_filename, output_filename):
    smiles_df = pd.read_csv(input_filename + '.csv')
    column = ['volume', 'article', 'raw_name', 'CAS', 'CIRsmiles', 'PubChemsmiles', 'PubChem_after_cas_check_smiles', 'PubChem_name_smiles', 'OPSIN_name_smiles', 'Processed_name', 'Processed_PubChemsmiles']
    result_df = pd.DataFrame(columns=column)
    data = []
    pattern = re.compile(r"\(+[\d\s]+-[\d\s]+-[\d\s]+\)+")


    for i in range(len(smiles_df)):
        print(i)
        processed_raw_name = re.sub(pattern, '', smiles_df['raw_name'][i])
        data.append([smiles_df['volume'][i], smiles_df['article'][i], processed_raw_name, smiles_df['CAS'][i], smiles_df['CIRsmiles'][i], smiles_df['PubChemsmiles'][i], smiles_df['PubChem_after_cas_check_smiles'][i], smiles_df['PubChem_name_smiles'][i], smiles_df['OPSIN_name_smiles'][i], smiles_df['Processed_name'][i], smiles_df['Processed_PubChemsmiles'][i]])
    result_df = pd.concat([result_df, pd.DataFrame(data, columns=column)], ignore_index=True)
    result_df.to_csv(output_filename + '.csv', index=None)

if __name__ == '__main__':
    input_filename = 'names_cir_pub_cas_ckecked_pub_name_pub_opsin_glm_pubchem'
    output_filename = 'names_cir_pub_cas_ckecked_pub_name_pub_opsin_glm_pubchem_final'
    name_remove_cas(input_filename, output_filename)