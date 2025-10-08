import chromadb
import pandas as pd
import os
import openai
from chromadb.api.types import Documents, EmbeddingFunction, Embeddings

import chromadb.utils.embedding_functions as embedding_functions




def reaction_match(input_filename, input_name_table, output_filename):

    chroma_client = chromadb.Client()
    # client = chromadb.PersistentClient(path="/home/ljw/rxn_pred/SyntheticGPT/data/reaction")
    collection = chroma_client.create_collection(name="name_smiles")

    smiles_df = pd.read_csv(input_name_table + '.csv')
    input_df = pd.read_csv(input_name_table + '.csv')

    columns = ['Index', 'Reactants', 'ReactantSMILES', 'Reactant amounts', 'Products', 'ProductSMILES', 'Product amounts', 'Solvents', 'Reaction temperature', 'Reaction time', 'ReactionSMILES', 'Yield']
    result_df = pd.DataFrame(columns=columns)
    data = []

    #生成数据库
    mid = int(len(smiles_df)/2)

    smiles_1 = []
    names_1 = []
    ids_1 = []
    for i in range(0, mid):
        if not pd.isna(smiles_df['raw_name'][i]):
            smiles_1.append({'SMILES' : smiles_df['Processed_PubChemsmiles'][i]})
            names_1.append(smiles_df['raw_name'][i])
            ids_1.append(str(i))

    smiles_2 = []
    names_2 = []
    ids_2 = []
    for i in range(mid, len(smiles_df)):
        if not pd.isna(smiles_df['raw_name'][i]):
            smiles_2.append({'SMILES' : smiles_df['Processed_PubChemsmiles'][i]})
            names_2.append(smiles_df['raw_name'][i])
            ids_2.append(str(i))

    # for i in range(len(smiles_df)):
    #     print(smiles_df['raw_name'][i])
    #     collection.add(
    #     documents=[smiles_df['raw_name'][i]],
    #     metadatas=[{'SMILES' : smiles_df['Processed_PubChemsmiles'][i]}],
    #     ids=[str(i)]
    # )

    collection.add(
        documents=names_1,
        metadatas=smiles_1,
        ids=ids_1
    )

    collection.add(
        documents=names_2,
        metadatas=smiles_2,
        ids=ids_2
    )

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
                results = collection.query(
                    query_texts=[reactant],
                    n_results=1
                )
                reactants = reactants + results['metadatas'][0][0]['SMILES'] +', '
                reaction_smiles = reaction_smiles + results['metadatas'][0][0]['SMILES'] + '.'
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
                results = collection.query(
                    query_texts=[product],
                    n_results=1
                )
                products = products + results['metadatas'][0][0]['SMILES'] +', '
                reaction_smiles = reaction_smiles + results['metadatas'][0][0]['SMILES'] + '.'
            except:
                print('Query ERROR: '+str(product))
                continue
        products = products.strip(', ')
        reaction_smiles = reaction_smiles.strip('.')

        data.append([input_df['Index'][i], input_df['Reactants'][i], reactants, input_df['Reactant amounts'][i], input_df['Products'][i], products, input_df['Product amounts'][i], input_df['Solvents'][i], input_df['Reaction temperature'][i], input_df['Reaction time'][i], reaction_smiles, input_df['Yield'][i]])

    result_df = pd.concat([result_df, pd.DataFrame(data, columns=columns)], ignore_index=True)
    result_df.to_csv(output_filename + '.csv', index=None)

    #去掉not found
    length = len(result_df)
    for i in range(length):
        if 'Not Found' in result_df['ReactionSMILES'][i]:
            result_df = result_df.drop(index=i)
    result_df.to_csv(output_filename + '_found_smiles.csv', index=None)

if __name__ == '__main__':
    input_filename = 'raw_names'
    input_name_table = 'names_cir_pub_cas_ckecked_pub_name_pub_opsin_glm_pubchem_final'
    output_filename = 'names_cir_pub_cas_ckecked_pub_name_pub_opsin_glm_pubchem_smiles'
    reaction_match(input_filename, input_name_table, output_filename)