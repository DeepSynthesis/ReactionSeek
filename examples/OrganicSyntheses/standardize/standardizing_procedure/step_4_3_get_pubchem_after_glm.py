import pandas as pd

def get_pubchem_after_glm(input_filename, input_pubchemdata, output_filename):
    column = ['volume', 'article', 'raw_name', 'CAS', 'CIRsmiles', 'PubChemsmiles', 'PubChem_after_cas_check_smiles', 'PubChem_name_smiles', 'OPSIN_name_smiles', 'Processed_name', 'Processed_PubChemsmiles']
    pubchem_column = ['raw_name', 'processed_name', 'pubchem_name']
    input_df = pd.read_csv(input_filename + '.csv')
    pubchem_input_df = pd.read_csv(input_pubchemdata +'.csv')
    print(len(pubchem_input_df))
    pubchem_result_df = pd.DataFrame(columns=pubchem_column)
    result_df = pd.DataFrame(columns=column)
    data = []
    pubchem_data = []

    for i in range(len(input_df)):
        print(i)
        if input_df['OPSIN_name_smiles'][i] != 'Not Found':
            data.append([input_df['volume'][i], input_df['article'][i], input_df['raw_name'][i], input_df['CAS'][i], input_df['CIRsmiles'][i], input_df['PubChemsmiles'][i], input_df['PubChem_after_cas_check_smiles'][i], input_df['PubChem_name_smiles'][i], input_df['OPSIN_name_smiles'][i], 'None', input_df['OPSIN_name_smiles'][i]])
        else:
            try:
                raw_name = input_df['raw_name'][i]
                index = pubchem_input_df[pubchem_input_df.raw_name == input_df['raw_name'][i]].index.tolist()[0]
                data.append([input_df['volume'][i], input_df['article'][i], input_df['raw_name'][i], input_df['CAS'][i], input_df['CIRsmiles'][i], input_df['PubChemsmiles'][i], input_df['PubChem_after_cas_check_smiles'][i], input_df['PubChem_name_smiles'][i], input_df['OPSIN_name_smiles'][i], pubchem_input_df['processed_name'][index], pubchem_input_df['pubchem_name'][index]])
            except Exception as e:
                data.append([input_df['volume'][i], input_df['article'][i], input_df['raw_name'][i], input_df['CAS'][i], input_df['CIRsmiles'][i], input_df['PubChemsmiles'][i], input_df['PubChem_after_cas_check_smiles'][i], input_df['PubChem_name_smiles'][i], input_df['OPSIN_name_smiles'][i], 'Not Found', 'Not Found'])
    result_df = pd.concat([result_df, pd.DataFrame(data, columns=column)], ignore_index=True)
    result_df.to_csv(output_filename + '.csv', index=None)

if __name__ == '__main__':
    input_filename = 'names_cir_pub_cas_ckecked_pub_name_pub_opsin'
    input_pubchemdata = 'names_cir_pub_cas_ckecked_pub_name_pub_opsin_prename_pubchemdata'
    output_filename = 'names_cir_pub_cas_ckecked_pub_name_pub_opsin_glm_pubchem'
    get_pubchem_after_glm(input_filename, input_pubchemdata, output_filename)