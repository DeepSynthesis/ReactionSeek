import json
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np # For handling potential NaN in plotting if categories are missing in some decades

def plot_analysis_results(json_file_path="final_classified_asymmetric_reactions.json"):
    """
    Loads the analyzed data and generates plots for temporal trends.
    Assumes the JSON file contains columns like 'year', 'decade',
    'major_catalyst_class', 'metal_center', 'ligand_or_core_type',
    'reaction_type', 'substrate_type'.
    """
    try:
        df = pd.read_json(json_file_path)
    except FileNotFoundError:
        print(f"Error: File '{json_file_path}' not found.")
        return [] # Return empty list if file not found
    except ValueError as e:
        print(f"Error reading JSON file: {e}")
        return []

    print(f"Generating plots from '{json_file_path}'...")
    plt.style.use('seaborn-v0_8-whitegrid')
    output_plot_list = []
    
    # Ensure 'decade' column exists from 'year'
    if 'decade' not in df.columns and 'year' in df.columns:
        df['decade'] = (df['year'] // 10) * 10

    # --- Plot 2: Major Catalyst Class Distribution per Decade ---
    if 'decade' in df.columns and 'major_catalyst_class' in df.columns:
        catalyst_class_per_decade = df.groupby('decade')['major_catalyst_class'].value_counts(normalize=False).unstack(fill_value=0)
        print(catalyst_class_per_decade)
        if not catalyst_class_per_decade.empty:
            catalyst_class_per_decade.plot(kind='bar', stacked=True, figsize=(10, 7), color=['#FFFFBB', '#BCD2F8', '#FFB8B8'])
            plt.xlabel('Decade', fontsize=16)
            plt.ylabel('Number of Reactions', fontsize=16)
            plt.legend(bbox_to_anchor=(0.03, 1), loc='upper left', frameon=True)
            plt.tight_layout()
            plot_filename = "2_major_catalyst_class_per_decade_new.png"
            plt.savefig(plot_filename)
            plt.close()
            output_plot_list.append(plot_filename)
            print(f"Saved: {plot_filename}")
    else:
        print("Skipping Plot 2: 'decade' or 'major_catalyst_class' column not found.")

if __name__ == "__main__":
    # This script assumes 'final_classified_asymmetric_reactions.json'
    # was created by the previous script which included the detailed catalyst parsing.
    json_file_for_plotting = "final_classified_asymmetric_reactions.json"
    
    try:
        # Check if the expected input file exists
        with open(json_file_for_plotting, 'r') as f:
            # File exists, proceed to plotting
            pass
        print(f"Attempting to generate plots from: {json_file_for_plotting}")
        generated_plots = plot_analysis_results(json_file_for_plotting)
        if generated_plots:
            print("\nPlotting complete. Please find the PNG files in your working directory.")
        else:
            print("\nPlotting script ran, but no plots were generated. Check for earlier error messages or data issues.")
            
    except FileNotFoundError:
        print(f"\nPlotting script error: The input file '{json_file_for_plotting}' was not found.")
        print("This file should have been generated by the previous data analysis script that processes the manually corrected data")
        print("and adds 'major_catalyst_class', 'metal_center', 'ligand_or_core_type' columns.")
        print("Please ensure that script ran successfully and created this specific JSON file.")