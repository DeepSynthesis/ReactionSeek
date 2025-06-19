
import pandas as pd
import os
from fuzzywuzzy import fuzz

def fuzzy_reaction_match(input_filename, input_name_table, output_filename):
    smiles_df = pd.read_csv(input_name_table + '.csv')
    input_df = pd.read_csv(input_name_table + '.csv')

    columns = ['Index', 'Reactants', 'ReactantSMILES', 'Reactant amounts', 'Products', 'ProductSMILES', 'Product amounts', 'Solvents', 'Reaction temperature', 'Reaction time', 'ReactionSMILES', 'Yield']
    result_df = pd.DataFrame(columns=columns)
    data = []

    #生成数据库

    database = {}
    keys = []
    for i in range(0, len(smiles_df)):
        if not pd.isna(smiles_df['raw_name'][i]):
            names = smiles_df['raw_name'][i].lower().split('\n')
            for name in names:
                database[name] = smiles_df['Processed_PubChemsmiles'][i]
                keys.append(name)

    results = [(item, fuzz.partial_ratio('3-nitrophthalic acid', item)) for item in keys]
    sorted_results = sorted(results, key=lambda x: x[1], reverse=True)
    print(sorted_results)

    #查询

    for i in range(len(input_df)):
        print(i)
        reactants = ''
        products = ''
        reaction_smiles = ''

        reactant_str = input_df['Reactants'][i]
        try:
            reactant_list = reactant_str.split(', ')
        except:
            print('String ERROR: '+str(reactant_str))
            continue
        for reactant in reactant_list:
            try:
                results = [(item, fuzz.partial_ratio(reactant.lower(), item)) for item in keys]
                sorted_results = sorted(results, key=lambda x: x[1], reverse=True)
                reactants = reactants + database[sorted_results[0][0]] +', '
                print('score: ' + str(sorted_results[0][1]))
                reaction_smiles = reaction_smiles + database[sorted_results[0][0]] + '.'
            except:
                print('Query ERROR: '+str(reactant))
                continue
        reactants = reactants.strip(', ')
        reaction_smiles = reaction_smiles.strip('.')
        
        reaction_smiles = reaction_smiles + '>>'
        
        product_str = input_df['Products'][i]
        try:
            product_list = product_str.split(', ')
        except:
            print('String ERROR: '+str(product_str))
            continue
        for product in product_list:
            try:
                results = [(item, fuzz.partial_ratio(product.lower(), item)) for item in keys]
                sorted_results = sorted(results, key=lambda x: x[1], reverse=True)
                products = products + database[sorted_results[0][0]] +', '
                print('score: ' + str(sorted_results[0][1]))
                reaction_smiles = reaction_smiles + database[sorted_results[0][0]] + '.'
            except:
                print('Query ERROR: '+str(product))
                continue
        products = products.strip(', ')
        reaction_smiles = reaction_smiles.strip('.')

        data.append([input_df['Index'][i], input_df['Reactants'][i], reactants, input_df['Reactant amounts'][i], input_df['Products'][i], products, input_df['Product amounts'][i], input_df['Solvents'][i], input_df['Reaction temperature'][i], input_df['Reaction time'][i], reaction_smiles, input_df['Yield'][i]])

    result_df = pd.concat([result_df, pd.DataFrame(data, columns=columns)], ignore_index=True)
    result_df.to_csv(output_filename + '_fuzz.csv', index=None)

    #去掉not found
    length = len(result_df)
    for i in range(length):
        if 'Not Found' in result_df['ReactionSMILES'][i]:
            result_df = result_df.drop(index=i)
    result_df.to_csv(output_filename + '_found_smiles_fuzz.csv', index=None)

if __name__ == '__main__':
    input_filename = 'raw_names'
    input_name_table = 'names_cir_pub_cas_ckecked_pub_name_pub_opsin_glm_pubchem_final'
    output_filename = 'names_cir_pub_cas_ckecked_pub_name_pub_opsin_glm_pubchem_smiles'
    fuzzy_reaction_match(input_filename, input_name_table, output_filename)