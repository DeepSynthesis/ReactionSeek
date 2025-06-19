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


    # --- Plot 1: Total Asymmetric Reactions per Decade ---
    if 'decade' in df.columns:
        plt.figure(figsize=(10, 6))
        reactions_per_decade = df['decade'].value_counts().sort_index()
        reactions_per_decade.plot(kind='bar', colormap='viridis')
        plt.title('Total Asymmetric Reactions Reported per Decade\n(Org. Synth., Filtered & Manually Corrected Data)')
        plt.xlabel('Decade')
        plt.ylabel('Number of Reactions')
        plt.xticks(rotation=45)
        plt.tight_layout()
        plot_filename = "1_total_reactions_per_decade.png"
        plt.savefig(plot_filename)
        plt.close()
        output_plot_list.append(plot_filename)
        print(f"Saved: {plot_filename}")
    else:
        print("Skipping Plot 1: 'decade' column not found.")

    # --- Plot 2: Major Catalyst Class Distribution per Decade ---
    if 'decade' in df.columns and 'major_catalyst_class' in df.columns:
        catalyst_class_per_decade = df.groupby('decade')['major_catalyst_class'].value_counts(normalize=False).unstack(fill_value=0)
        if not catalyst_class_per_decade.empty:
            catalyst_class_per_decade.plot(kind='bar', stacked=True, figsize=(12, 7), colormap='Spectral')
            plt.title('Distribution of Major Catalyst Classes per Decade')
            plt.xlabel('Decade')
            plt.ylabel('Number of Reactions')
            plt.xticks(rotation=45)
            plt.legend(title='Catalyst Class', bbox_to_anchor=(1.05, 1), loc='upper left')
            plt.tight_layout()
            plot_filename = "2_major_catalyst_class_per_decade.png"
            plt.savefig(plot_filename)
            plt.close()
            output_plot_list.append(plot_filename)
            print(f"Saved: {plot_filename}")
    else:
        print("Skipping Plot 2: 'decade' or 'major_catalyst_class' column not found.")


    # --- Plot 3: Metal Center Distribution per Decade (for Metal Catalysts) ---
    if 'decade' in df.columns and 'major_catalyst_class' in df.columns and 'metal_center' in df.columns:
        df_metal = df[df['major_catalyst_class'] == 'Metal Catalyst'].copy()
        if not df_metal.empty:
            metal_counts = df_metal['metal_center'].value_counts()
            # Consolidate rare metals, ensure 'Unknown Metal' is not part of 'Other Known Metal'
            rare_metals = metal_counts[(metal_counts < 2) & (metal_counts.index != 'Unknown Metal')].index
            
            df_metal['metal_center_plot'] = df_metal['metal_center'].astype(str)
            df_metal.loc[df_metal['metal_center_plot'].isin(rare_metals), 'metal_center_plot'] = 'Other Known Metal'
            
            metal_center_per_decade = df_metal.groupby('decade')['metal_center_plot'].value_counts(normalize=False).unstack(fill_value=0)
            if not metal_center_per_decade.empty:
                # Ensure all expected columns are present for plotting, adding missing ones with 0
                expected_metals_for_plot = list(df_metal['metal_center_plot'].unique())
                for metal in expected_metals_for_plot:
                    if metal not in metal_center_per_decade.columns:
                         metal_center_per_decade[metal] = 0
                metal_center_per_decade = metal_center_per_decade[expected_metals_for_plot] # Order columns

                metal_center_per_decade.plot(kind='bar', stacked=True, figsize=(14, 8), colormap='tab20')
                plt.title('Distribution of Metal Centers per Decade (Metal Catalysts)')
                plt.xlabel('Decade')
                plt.ylabel('Number of Reactions')
                plt.xticks(rotation=45)
                plt.legend(title='Metal Center', bbox_to_anchor=(1.05, 1), loc='upper left')
                plt.tight_layout()
                plot_filename = "3_metal_center_per_decade.png"
                plt.savefig(plot_filename)
                plt.close()
                output_plot_list.append(plot_filename)
                print(f"Saved: {plot_filename}")
    else:
        print("Skipping Plot 3: Necessary columns for metal center analysis not found.")

    # --- Plot 4: Ligand/Core Type Distribution per Decade (Organocatalysts) ---
    if 'decade' in df.columns and 'major_catalyst_class' in df.columns and 'ligand_or_core_type' in df.columns:
        df_organo = df[df['major_catalyst_class'] == 'Organocatalyst'].copy()
        if not df_organo.empty:
            organo_core_counts = df_organo['ligand_or_core_type'].value_counts()
            rare_organo_cores = organo_core_counts[(organo_core_counts < 2) & (organo_core_counts.index != 'Other Organocatalyst')].index
            
            df_organo['ligand_or_core_type_plot'] = df_organo['ligand_or_core_type'].astype(str)
            df_organo.loc[df_organo['ligand_or_core_type_plot'].isin(rare_organo_cores), 'ligand_or_core_type_plot'] = 'Other Specific Organocatalyst'
            
            organo_core_per_decade = df_organo.groupby('decade')['ligand_or_core_type_plot'].value_counts(normalize=False).unstack(fill_value=0)
            if not organo_core_per_decade.empty:
                expected_organo_cores_for_plot = list(df_organo['ligand_or_core_type_plot'].unique())
                for core in expected_organo_cores_for_plot:
                    if core not in organo_core_per_decade.columns:
                        organo_core_per_decade[core] = 0
                organo_core_per_decade = organo_core_per_decade[expected_organo_cores_for_plot]

                organo_core_per_decade.plot(kind='bar', stacked=True, figsize=(14, 8), colormap='Set3')
                plt.title('Distribution of Organocatalyst Core Types per Decade')
                plt.xlabel('Decade')
                plt.ylabel('Number of Reactions')
                plt.xticks(rotation=45)
                plt.legend(title='Organocatalyst Core', bbox_to_anchor=(1.05, 1), loc='upper left')
                plt.tight_layout()
                plot_filename = "4_organocatalyst_core_per_decade.png"
                plt.savefig(plot_filename)
                plt.close()
                output_plot_list.append(plot_filename)
                print(f"Saved: {plot_filename}")
    else:
        print("Skipping Plot 4: Necessary columns for organocatalyst core analysis not found.")

    # --- Plot 5: Reaction Type Distribution per Decade ---
    if 'decade' in df.columns and 'reaction_type' in df.columns:
        df_reaction = df.copy()
        reaction_type_counts = df_reaction['reaction_type'].value_counts()
        rare_reaction_types = reaction_type_counts[(reaction_type_counts < 3) & (reaction_type_counts.index != 'Reaction Type Unknown')].index
        df_reaction['reaction_type_plot'] = df_reaction['reaction_type'].astype(str)
        df_reaction.loc[df_reaction['reaction_type_plot'].isin(rare_reaction_types), 'reaction_type_plot'] = 'Other Reaction Type'

        reaction_type_per_decade = df_reaction.groupby('decade')['reaction_type_plot'].value_counts(normalize=False).unstack(fill_value=0)
        if not reaction_type_per_decade.empty:
            expected_reactions_for_plot = list(df_reaction['reaction_type_plot'].unique())
            for rtype in expected_reactions_for_plot:
                if rtype not in reaction_type_per_decade.columns:
                    reaction_type_per_decade[rtype] = 0
            reaction_type_per_decade = reaction_type_per_decade[expected_reactions_for_plot]

            reaction_type_per_decade.plot(kind='bar', stacked=True, figsize=(14, 8), colormap='tab20b')
            plt.title('Distribution of Reaction Types per Decade')
            plt.xlabel('Decade')
            plt.ylabel('Number of Reactions')
            plt.xticks(rotation=45)
            plt.legend(title='Reaction Type', bbox_to_anchor=(1.05, 1), loc='upper left')
            plt.tight_layout()
            plot_filename = "5_reaction_type_per_decade.png"
            plt.savefig(plot_filename)
            plt.close()
            output_plot_list.append(plot_filename)
            print(f"Saved: {plot_filename}")
    else:
        print("Skipping Plot 5: 'decade' or 'reaction_type' column not found.")

    # --- Plot 6: Substrate Type Distribution per Decade ---
    if 'decade' in df.columns and 'substrate_type' in df.columns:
        df_substrate = df.copy()
        substrate_type_counts = df_substrate['substrate_type'].value_counts()
        rare_substrate_types = substrate_type_counts[(substrate_type_counts < 4) & (substrate_type_counts.index != 'Substrate Type Unknown')].index
        df_substrate['substrate_type_plot'] = df_substrate['substrate_type'].astype(str)
        df_substrate.loc[df_substrate['substrate_type_plot'].isin(rare_substrate_types), 'substrate_type_plot'] = 'Other Substrate Type'

        substrate_type_per_decade = df_substrate.groupby('decade')['substrate_type_plot'].value_counts(normalize=False).unstack(fill_value=0)
        if not substrate_type_per_decade.empty:
            expected_substrates_for_plot = list(df_substrate['substrate_type_plot'].unique())
            for stype in expected_substrates_for_plot:
                if stype not in substrate_type_per_decade.columns:
                    substrate_type_per_decade[stype] = 0
            substrate_type_per_decade = substrate_type_per_decade[expected_substrates_for_plot]
            
            substrate_type_per_decade.plot(kind='bar', stacked=True, figsize=(14, 8), colormap='Paired')
            plt.title('Distribution of Substrate Types per Decade')
            plt.xlabel('Decade')
            plt.ylabel('Number of Reactions')
            plt.xticks(rotation=45)
            plt.legend(title='Substrate Type', bbox_to_anchor=(1.05, 1), loc='upper left')
            plt.tight_layout()
            plot_filename = "6_substrate_type_per_decade.png"
            plt.savefig(plot_filename)
            plt.close()
            output_plot_list.append(plot_filename)
            print(f"Saved: {plot_filename}")
    else:
        print("Skipping Plot 6: 'decade' or 'substrate_type' column not found.")
        
    print(f"\nGenerated {len(output_plot_list)} plots: {', '.join(output_plot_list)}")
    return output_plot_list

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