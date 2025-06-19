import pandas as pd

def get_opsin(input_filename, opsin_input_filename, output_filename):
    column = ['volume', 'article', 'raw_name', 'CAS', 'CIRsmiles', 'PubChemsmiles', 'PubChem_after_cas_check_smiles', 'PubChem_name_smiles', 'OPSIN_name_smiles']
    opsin_column = ['raw_name', 'search_name', 'search_smiles']
    input_df = pd.read_csv(input_filename + '.csv')
    opsin_input_df = pd.read_csv(opsin_input_filename + '.csv')
    print(len(opsin_input_df))
    opsin_result_df = pd.DataFrame(columns=opsin_column)
    result_df = pd.DataFrame(columns=column)
    data = []
    opsin_data = []

    itr = 0
    with open('output.txt', 'r') as f:
        for line in f.readlines():
            if line.strip() != '':
                opsin_data.append([opsin_input_df['raw_name'][itr], opsin_input_df['search_name'][itr], line.strip()])
            else:
                opsin_data.append([opsin_input_df['raw_name'][itr], opsin_input_df['search_name'][itr], 'Not Found'])
            itr = itr + 1
        f.close()

    opsin_result_df = pd.concat([opsin_result_df, pd.DataFrame(opsin_data, columns=opsin_column)], ignore_index=True)
    opsin_result_df.to_csv(output_filename + '_opsindata.csv', index=None)

    for i in range(len(input_df)):
        print(i)
        if input_df['PubChem_name_smiles'][i] != 'Not Found':
            data.append([input_df['volume'][i], input_df['article'][i], input_df['raw_name'][i], input_df['CAS'][i], input_df['CIRsmiles'][i], input_df['PubChemsmiles'][i], input_df['PubChem_after_cas_check_smiles'][i], input_df['PubChem_name_smiles'][i], input_df['PubChem_name_smiles'][i]])
        else:
            index = opsin_input_df[opsin_input_df.raw_name == input_df['raw_name'][i]].index.tolist()[0]
            data.append([input_df['volume'][i], input_df['article'][i], input_df['raw_name'][i], input_df['CAS'][i], input_df['CIRsmiles'][i], input_df['PubChemsmiles'][i], input_df['PubChem_after_cas_check_smiles'][i], input_df['PubChem_name_smiles'][i], opsin_result_df['search_smiles'][index]])

    result_df = pd.concat([result_df, pd.DataFrame(data, columns=column)], ignore_index=True)
    result_df.to_csv(output_filename + '.csv', index=None)

if __name__ == '__main__':
    input_filename = 'names_cir_pub_cas_ckecked_pub_name_pub'
    opsin_input_filename = 'names_cir_pub_cas_ckecked_pub_name_pub_preopsin'
    output_filename = 'names_cir_pub_cas_ckecked_pub_name_pub_opsin'
    get_opsin(input_filename, opsin_input_filename, output_filename)
