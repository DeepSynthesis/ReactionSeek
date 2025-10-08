from zhipuai import ZhipuAI
import os
import time
import json
import pandas as pd


def get_completion(prompt, api_key, model='glm-4'):
    '''
        get completion from GLM.
    '''
    messages = [{'role': 'user', "content": prompt}]
    client = ZhipuAI(api_key=api_key)
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=0
    )
    return response.choices[0].message.content



def glm_name_process(input_filename, output_filename, apikey, model='glm-4'):
    glm_column = ['raw_name', 'processed_name']
    input_df = pd.read_csv(input_filename + '.csv')
    glm_result_df = pd.DataFrame(columns=glm_column)
    glm_data = []

    prompt = """
    Please extract the compounds or elements in the following dialogues and tell me their chemical names. You should response the name in a json format like {'name' : 'chemical name'}. The key 'name' is the origin name in the input. The value 'chemical name' is the chemical name of the compound or element. You shouldn't guess the chemical name of the raw name, and you should answer according to the name entered as much as possible. If the name refers to a class of compounds, please give a compound belonging to that class in the value 'chemical name' as an alternative. For example, halogens are replaced by chlorides, and alkyl groups are replaced by ethyl groups. If it is a complex mixture such as petroleum ether or alcohol, the answer should be ' none '.If you are not sure whether your answer is correct, you should answer 'none' in 'chemical name'.

    example 1:
        input: 
            o- and, predominantly, p-tolunitrile
        answer:
            {
                "o-tolunitrile": "3-Cyanotoluene",
                "p-tolunitrile": "4-Cyanotoluene"
            }

    example 2:
        input: 
            Anhydro-o-hydroxymercuribenzoic acid
        answer:
            {
                "Anhydro-o-hydroxymercuribenzoic acid": "o-hydroxymercuribenzoic acid"
            }

    example 3:
        input: 
            dioxime of o-benzoquinone
        answer:
            {
                "dioxime of o-benzoquinone": "o-benzoquinone dioxime"
            }

    input: 

    """

    for i in range(len(input_df)):
        if input_df['OPSIN_name_smiles'][i] == 'Not Found':
            print(i)
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
            result = get_completion(prompt+name, apikey, model=model).split('}')[0] + '}'
            print(result)
            try:
                json_dic = eval(result)
                for value in json_dic.values():
                    glm_data.append([input_df['raw_name'][i], value])
            except Exception as e:
                print('index: ' + str(i) + ' Error: ' + str(e))
    glm_result_df = pd.concat([glm_result_df, pd.DataFrame(glm_data, columns=glm_column)], ignore_index=True)
    glm_result_df.to_csv(output_filename + '.csv', index=None)


if __name__ == '__main__':
    api_key = 'your api key'
    model = 'glm-4'
    input_filename = 'names_cir_pub_cas_ckecked_pub_name_pub_opsin'
    output_filename = 'names_cir_pub_cas_ckecked_pub_name_pub_opsin_prename'
    glm_name_process(input_filename, output_filename, api_key, model=model)