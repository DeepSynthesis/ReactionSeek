# -*- coding: UTF-8 -*-
# the second step for the data collection
import pandas as pd
import time

def string_to_dataframe(input_string, index_prefix="entry"):
    '''
    Convert input string containing reaction table data to dataframe.
    
    Args:
        input_string (str): String containing table data with | separators
        index_prefix (str): Prefix for index column (default: "entry")
    
    Returns:
        pandas.DataFrame: Structured dataframe with reaction data
    '''
    # Define the standard columns based on the output.csv format
    columns = ['Index', 'REACTION_PRODUCT', 'STARTING_MATERIAL', 'REAGENT_CATALYST', 
               'SOLVENT', 'OTHER_COMPOUND', 'EXAMPLE_LABEL', 'TEMPERATURE', 
               'TIME', 'YIELD_PERCENT', 'YIELD_OTHER']
    
    result_df = pd.DataFrame(columns=columns)
    
    if not input_string or "|" not in input_string:
        return result_df
    
    # Split the input string into lines
    lines = input_string.strip().split("\n")
    
    # Find the header line and data lines
    header_line_idx = -1
    for i, line in enumerate(lines):
        if line.strip().startswith("|") and ("REACTION_PRODUCT" in line or "STARTING_MATERIAL" in line):
            header_line_idx = i
            break
    
    if header_line_idx == -1:
        # No proper header found, assume the format from tabulate_condition function
        # Skip first 2 lines (header and separator)
        data_lines = [line for line in lines[2:] if line.strip() and "|" in line]
    else:
        # Skip header and separator line (if exists)
        data_lines = []
        for line in lines[header_line_idx + 1:]:
            if line.strip() and "|" in line and not line.strip().startswith("|---"):
                data_lines.append(line)
    
    # Process each data line
    entry_counter = 1
    for line in data_lines:
        if not line.strip() or line.strip().startswith("|---"):
            continue
            
        # Extract data from pipe-separated line
        data = [x.strip() for x in line.split("|")[1:-1]]
        
        # Create indexed entry
        indexed_data = [f"{index_prefix}"] + data
        
        # Ensure we have the right number of columns
        while len(indexed_data) < len(columns):
            indexed_data.append("")
        
        # Truncate if too many columns
        indexed_data = indexed_data[:len(columns)]
        
        if len(indexed_data) == len(columns):
            result_df = pd.concat([result_df, pd.DataFrame([indexed_data], columns=columns)], ignore_index=True)
            entry_counter += 1
    
    return result_df
def main():
    # Read the original CSV file
    df = pd.read_csv('output.csv')
    
    # Initialize empty list to store all processed dataframes
    all_dataframes = []
    
    # Process each row using the new string_to_dataframe function
    for i, row in df.iterrows():
        output_string = str(row['output'])
        input_file = str(row['input_file'])
        
        # Extract index from input filename (remove .txt extension)
        index_prefix = input_file.replace('.txt', '') if '.txt' in input_file else input_file
        
        # Convert string to dataframe
        parsed_df = string_to_dataframe(output_string, index_prefix=index_prefix)
        
        if not parsed_df.empty:
            all_dataframes.append(parsed_df)
    
    # Combine all dataframes
    if all_dataframes:
        final_df = pd.concat(all_dataframes, ignore_index=True)
    else:
        # Create empty dataframe with standard columns if no data found
        columns = ['Index', 'REACTION_PRODUCT', 'STARTING_MATERIAL', 'REAGENT_CATALYST', 
                   'SOLVENT', 'OTHER_COMPOUND', 'EXAMPLE_LABEL', 'TEMPERATURE', 
                   'TIME', 'YIELD_PERCENT', 'YIELD_OTHER']
        final_df = pd.DataFrame(columns=columns)
    
    # Merge rows with the same Index
    if not final_df.empty:
        # Group by Index and merge content in each column with ", " separator
        merged_df = final_df.groupby('Index').agg({
            col: lambda x: ', '.join(x.dropna().astype(str)) if col != 'Index' else x.iloc[0]
            for col in final_df.columns if col != 'Index'
        }).reset_index()
        final_df = merged_df
    
    # Save the processed data
    final_df.to_csv('output_table.csv', index=None)

if __name__ == '__main__':
    start = time.perf_counter()
    main()
    end = time.perf_counter()
    print('runningtime:' + str(end - start))