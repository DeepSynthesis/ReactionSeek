# -*- coding: UTF-8 -*-
import os
import sys
import time
import json
import pandas as pd

# 添加父目录到路径以支持 config 导入
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from openai import OpenAI
from config import OPENAI_API_KEY, OPENAI_BASE_URL, OPENAI_MODEL, API_DELAY


def get_completion(prompt, model=None):
    """
    get completion from OpenAI.
    """
    if model is None:
        model = OPENAI_MODEL

    client = OpenAI(
        api_key=OPENAI_API_KEY,
        base_url=OPENAI_BASE_URL,
    )
    messages = [{'role': 'user', "content": prompt}]
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=0
    )
    return response.choices[0].message.content

def get_times(text, model):
    '''
        change time into standard time and generate a table of standard time.
    '''
    
    prompt = f"""
    You will be provided with a table containing a number of different units of time or time period, please convert them into minutes of time or time period. If any information is not provided or you are unsure, use "N/A" in the cell.   

    If multiple reaction time are present, separate them using a comma in the same cell.
    Output table should have 2 columns: | Index | Reaction time |

    Example 1:
    Table:<'''
    | Index | Reaction time |
    |-------|---------------|
    | 1 | Boiled gently for 1 hour |
    | 2 | 15-45 minutes (reaction starts), 15-30 minutes (reaction complete) |
    | 3 | Overnight |
    | 4 | 1-2 days |
    | 5 | N/A |
    '''>
    Answer:
    | Index | Reaction time |
    |-------|---------------|
    | 1 | 60 minutes |
    | 2 | 15-45 minutes (reaction starts), 15-30 minutes (reaction complete) |
    | 3 | 720 minutes |
    | 4 | 1440-2880 minutes |
    | 5 | N/A |
    
    /////

    Table:<'''
    {text}
    '''>
    """
    response = get_completion(prompt, model)
    print(response)
    return response

def tabulate_condition(output_str):
    '''
    change the table string into a dataframe.
    '''
    columns = ['Index', 'Reaction time'] # Initialize an empty dataframe with the desired columns
    result_df = pd.DataFrame(columns=columns)
    if "|" in output_str: # Check if the "|" symbol is present in the text string
        # Split the text string into lines and remove the header
        lines = output_str.strip().split("\n")[2:]
        # Iterate through the lines and extract the data
        for line in lines:
            data = [x.strip() for x in line.split("|")[1:-1]]
            if len(data) == len(columns):
                result_df = pd.concat([result_df, pd.DataFrame([data], columns=columns)], ignore_index=True) 
    return result_df

def get_time_from_df(df, model=None):
    """
    get standard time
    """
    if model is None:
        model = OPENAI_MODEL
    input_str = '''
    | Index | Reaction time |
    |-------|---------------|
    '''
    columns = ['Index', 'Reaction time']
    output_df = pd.DataFrame(columns=columns)
    data = []
    for i in range(len(df)):
        index = i + 1
        reaction_time = df['Reaction time'][i]
        if pd.isna(reaction_time):
            reaction_time = 'N/A'
        input_str = input_str + '| ' + str(index) + ' | ' + str(reaction_time) +' |\n'
    
    output_str = get_times(input_str, model)
    result_df = tabulate_condition(output_str)
    for i in range(len(result_df)):
        data.append([df['Index'][i], result_df['Reaction time'][i]])
    output_df = pd.concat([output_df, pd.DataFrame(data, columns=columns)], ignore_index=True) 
    return output_df



def main(volumes, delay=None, model=None):
    if delay is None:
        delay = API_DELAY
    if model is None:
        model = OPENAI_MODEL
    for filename in volumes:
        df = pd.read_csv(filename + '.csv')
        time.sleep(delay)
        df2 = get_time_from_df(df, model)
        df2.to_csv(filename + '_timetable.csv', index=None)


if __name__ == '__main__':
    # 配置从 .env 文件中读取，通过 config 模块统一管理
    volumes = ["Volume16-20"]  # Your input file name
    delay = API_DELAY          # Your delay time
    model = OPENAI_MODEL       # Your model name
    print(f"Using API base URL: {OPENAI_BASE_URL}")
    print(f"Using model: {model}")
    start = time.perf_counter()
    main(volumes, delay, model)
    end = time.perf_counter()
    print('runningtime:' + str(end - start))