import pandas as pd

def get_opsin_names(input_filename, output_filename):
    column = ['raw_name', 'search_name']
    input_df = pd.read_csv(input_filename + '.csv')
    result_df = pd.DataFrame(columns=column)
    data = []
    search_names = []
    for i in range(len(input_df)):
        print(i)
        if input_df['PubChem_name_smiles'][i] == 'Not Found':
            if ':' in input_df['raw_name'][i]:
                name = input_df['raw_name'][i].split(':')[1].split(';')[0].strip()
                name = name.replace('\n', '').replace('\r', '')              
            else:
                if ',\n' in input_df['raw_name'][i]:
                    name = input_df['raw_name'][i].split(',\n')[1].split(' (')[0].strip()
                    name = name.replace('\n', '').replace('\r', '')    
                else:
                    name = input_df['raw_name'][i].split(' (')[0].strip()
                    name = name.replace('\n', '').replace('\r', '')      
            data.append([input_df['raw_name'][i], name])
            search_names.append(name+'\n')

    result_df = pd.concat([result_df, pd.DataFrame(data, columns=column)], ignore_index=True)
    result_df.to_csv(output_filename + '.csv', index=None)
    print(len(result_df))
    with open('input.txt', 'w') as f:
        f.writelines(search_names)
        f.close()

if __name__ == '__main__':
    input_filename = 'names_cir_pub_cas_ckecked_pub_name_pub'
    output_filename = 'names_cir_pub_cas_ckecked_pub_name_pub_preopsin'
    get_opsin_names(input_filename, output_filename)