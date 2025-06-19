import json
import re
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from collections import Counter

# --- Keyword Definitions for Detailed Catalyst Classification ---

# Metals (lowercase for matching)
METALS = ['ru', 'rh', 'pd', 'ir', 'cu', 'ni', 'fe', 'ti', 'zn', 'mn', 'co', 'mo', 'v', 'au', 'ag', 'al', 'mg', 'b', 'zr', 'sc', 'yb', 'lanthanide']

# Ligand Skeletons / Organocatalyst Cores (lowercase for matching, representative examples)
# Order can matter if some are subsets of others; more specific first.
LIGAND_ORGANOCATALYST_CORES = {
    # Phosphine Ligands (often bidentate)
    "BINAP": [r"binap"], # Covers BINAP, Tol-BINAP, Xyl-BINAP if 'binap' is present
    "SEGPHOS": [r"segphos"],
    "DIFLUORPHOS": [r"difluorphos"],
    "DuPhOS": [r"duphos"],
    "JOSIPHOS": [r"josiphos"],
    "PhanePhos": [r"phanephos"],
    "WALPHOS": [r"walphos"],
    "CHIRAPHOS": [r"chiraphos"],
    "DIPAMP": [r"dipamp"],
    "Phosphoramidite": [r"phosphoramidite"],
    "Monodentate P-Ligand": [r"monophos", r"buchwald ligand", r"cataCXium"], # Generic for monodentate if not more specific
    "Other Bidentate P-Ligand": [r"dppe", r"dppp", r"dppb", r"bisphosphine", r"diphosphine"], # Generic for other bidentate

    # N-Ligands & Mixed N,O / N,P
    "Salen/Salan": [r"salen", r"salan"],
    "BOX/PyBOX": [r"box", r"bis\(oxazoline\)", r"pybox"],
    "DPEN/DACH/Chiral Diamine": [r"dpen", r"diphenylethylenediamine", r"dach", r"diaminocyclohexane", r"chiral diamine"],
    "Trost Ligand": [r"trost ligand"],
    "NHC Ligand (for metal)": [r"nhc ligand", r"n-heterocyclic carbene ligand"], # For NHCs bound to metals

    # O-Ligands (for metals)
    "BINOL-derived Ligand (for metal)": [r"binol-metal", r"ti-binol"], # Distinguish from CPA BINOL
    "TADDOL": [r"taddol"],
    "Tartrate (as ligand)": [r"tartrate ligand", r"diethyl tartrate"], # e.g., Sharpless epoxidation

    # Organocatalyst Cores
    "Proline/Proline Derivative": [r"proline", r"diphenylprolinol", r"prolinol"],
    "MacMillan Imidazolidinone": [r"macmillan catalyst", r"imidazolidinone organocatalyst"],
    "Jørgensen-Hayashi Catalyst": [r"jørgensen-hayashi", r"diarylprolinol silyl ether"],
    "Cinchona Alkaloid Organocatalyst": [r"cinchona alkaloid", r"quinine", r"quinidine", r"cinchonidine", r"cinchonine"], # As organocatalyst, not ligand for metal
    "Chiral Phosphoric Acid (CPA)": [r"phosphoric acid organocatalyst", r"cpa", r"binol phosphoric acid", r"trip", r"strip"],
    "Thiourea/Urea Organocatalyst": [r"thiourea organocatalyst", r"urea organocatalyst", r"schreiner's thiourea"],
    "NHC Organocatalyst": [r"nhc organocatalyst", r"n-heterocyclic carbene organocatalyst"], # Purely organocatalytic NHC
    "Chiral Amine (Primary/Secondary, other)": [r"chiral amine organocatalyst", r"primary amine organocatalyst", r"secondary amine organocatalyst"],
    "CBS Catalyst/Oxazaborolidine": [r"cbs catalyst", r"corey-bakshi-shibata", r"oxazaborolidine"], # Boron-based, often considered organometallic or special organocat.

    # Enzyme types
    "Yeast": [r"yeast", r"baker's yeast"],
    "Lipase": [r"lipase"],
    "Esterase": [r"esterase"],
    "Dehydrogenase/Reductase": [r"dehydrogenase", r"reductase", r"kred"],
    "Oxidase": [r"oxidase"],

    # Stoichiometric / Resolution
    "Chiral Auxiliary (Evans, Oppolzer, etc.)": [r"chiral auxiliary", r"evans auxiliary", r"oppolzer's sultam", r"myers auxiliary", r"(-)-menthyl"],
    "Resolving Agent (Tartaric Acid, Brucine etc.)": [r"resolving agent", r"tartaric acid", r"brucine", r"camphorsulfonic acid", r"dbta"]
}

def parse_catalyst_details(catalyst_system_type_str):
    """
    Parses the manually corrected catalyst_system_type string to extract
    major class, metal center, and ligand/core type.
    """
    if pd.isna(catalyst_system_type_str):
        return "Unknown", "N/A", "N/A"

    text_lower = str(catalyst_system_type_str).lower()
    major_class = "Unknown"
    metal_center = "N/A"
    ligand_core = "N/A"

    # Determine Major Class first
    if "enzyme" in text_lower or "biocatalyst" in text_lower or "yeast" in text_lower or "lipase" in text_lower:
        major_class = "Enzyme/Biocatalyst"
    elif "organocatalyst" in text_lower or \
         any(k in text_lower for k in ["proline", "cinchona", "macmillan", "phosphoric acid", "thiourea", "nhc organo", "cbs catalyst", "oxazaborolidine"]):
        major_class = "Organocatalyst"
    elif "metal catalyst" in text_lower or \
         any(metal in text_lower for metal in METALS) or \
         any(k in text_lower for k in ["binap", "salen", "box", "phosphine ligand", "diamine ligand"]): # Ligand names often imply metal
        major_class = "Metal Catalyst"
    elif "stoichiometric chiral auxiliary" in text_lower or "auxiliary" in text_lower:
        major_class = "Stoichiometric Chiral Auxiliary"
    elif "resolution" in text_lower or "resolving agent" in text_lower:
        major_class = "Resolution Process"
    elif catalyst_system_type_str != "Catalyst System Unknown": # If manually corrected but doesn't fit above
        major_class = "Other Defined Catalyst" # Could be a specific named reaction not easily parsed

    # Extract Metal Center (if Metal Catalyst)
    if major_class == "Metal Catalyst":
        found_metals = []
        for metal_name in METALS:
            if re.search(r'\b' + metal_name + r'\b', text_lower):
                found_metals.append(metal_name.upper())
        if found_metals:
            metal_center = ", ".join(sorted(list(set(found_metals)))) # Handle multiple metals if mentioned (e.g. bimetallic)
        else:
            metal_center = "Unknown Metal"

    # Extract Ligand/Core Type
    # This part is crucial and relies on good keywords and potentially the major_class identified
    found_ligand_core = False
    for core_name, patterns in LIGAND_ORGANOCATALYST_CORES.items():
        for pattern in patterns:
            if re.search(pattern, text_lower):
                # Check context for organocatalyst vs ligand for metal
                if major_class == "Organocatalyst" and "Organocatalyst" not in core_name and "Enzyme" not in core_name and "Auxiliary" not in core_name and "Resolving Agent" not in core_name:
                    if any(oc_indicator in core_name.lower() for oc_indicator in ["proline", "macmillan", "jørgensen", "cinchona", "phosphoric", "thiourea", "nhc organo", "cbs", "amine"]):
                        ligand_core = core_name
                        found_ligand_core = True
                        break
                elif major_class == "Metal Catalyst" and "Ligand" in core_name:
                    ligand_core = core_name
                    found_ligand_core = True
                    break
                elif major_class == "Enzyme/Biocatalyst" and ("Yeast" in core_name or "Lipase" in core_name or "Esterase" in core_name or "Dehydrogenase" in core_name or "Oxidase" in core_name):
                    ligand_core = core_name
                    found_ligand_core = True
                    break
                elif major_class == "Stoichiometric Chiral Auxiliary" and "Auxiliary" in core_name:
                    ligand_core = core_name
                    found_ligand_core = True
                    break
                elif major_class == "Resolution Process" and "Resolving Agent" in core_name:
                    ligand_core = core_name
                    found_ligand_core = True
                    break
                elif major_class != "Unknown" and not found_ligand_core : # If major class is known, try to assign a general core
                     ligand_core = core_name
                     found_ligand_core = True # Set it, but it might be overridden by a more specific match later in the loop
                     break
        if found_ligand_core and (ligand_core == core_name): # Ensure the break is from an actual match for *this* core_name
            break
            
    if not found_ligand_core or ligand_core == "N/A":
        if major_class == "Organocatalyst":
            ligand_core = "Other Organocatalyst"
        elif major_class == "Metal Catalyst" and metal_center != "N/A" and metal_center != "Unknown Metal":
            ligand_core = f"Unspecified Ligand for {metal_center}"
        elif major_class == "Metal Catalyst":
            ligand_core = "Unspecified Ligand for Unknown Metal"
        elif major_class == "Enzyme/Biocatalyst":
            ligand_core = "Other Enzyme"
        elif major_class == "Stoichiometric Chiral Auxiliary":
            ligand_core = "Other Chiral Auxiliary"
        elif major_class == "Resolution Process":
            ligand_core = "Other Resolution Method"
        elif major_class == "Other Defined Catalyst":
             ligand_core = catalyst_system_type_str # Use the full string if it's a specific defined type
        else:
            ligand_core = "N/A"


    # Final check for CBS catalyst due to its unique nature (boron based, often organo-like)
    if "cbs catalyst" in text_lower or "oxazaborolidine" in text_lower:
        major_class = "Organocatalyst" # Or "Organometallic Catalyst"
        metal_center = "B"
        ligand_core = "CBS Catalyst/Oxazaborolidine"

    return major_class, metal_center, ligand_core

def analyze_data(df):
    """Performs analysis and prints results."""

    print(f"Loaded {len(df)} manually corrected reactions for detailed analysis.")

    # Apply detailed catalyst parsing
    parsed_catalyst_info = df['catalyst_system_type'].apply(parse_catalyst_details)
    df['major_catalyst_class'] = parsed_catalyst_info.apply(lambda x: x[0])
    df['metal_center'] = parsed_catalyst_info.apply(lambda x: x[1])
    df['ligand_or_core_type'] = parsed_catalyst_info.apply(lambda x: x[2])

    # --- Overall Proportions ---
    print("\n--- Overall Proportions ---")

    def print_proportions(column_name):
        counts = df[column_name].value_counts()
        percentages = df[column_name].value_counts(normalize=True).mul(100).round(1)
        print(f"\nDistribution of '{column_name}':")
        for item, count in counts.items():
            print(f"  {item}: {count} ({percentages[item]}%)")

    print_proportions('major_catalyst_class')
    # Filter for metal catalysts before printing metal_center and ligand_type for metals
    df_metal_catalysts = df[df['major_catalyst_class'] == 'Metal Catalyst']
    if not df_metal_catalysts.empty:
        print_proportions_metal_center = df_metal_catalysts['metal_center'].value_counts()
        print_proportions_metal_center_perc = df_metal_catalysts['metal_center'].value_counts(normalize=True).mul(100).round(1)
        print(f"\nDistribution of 'metal_center' (within Metal Catalysts - Total {len(df_metal_catalysts)}):")
        for item, count in print_proportions_metal_center.items():
            print(f"  {item}: {count} ({print_proportions_metal_center_perc[item]}%)")

        print_proportions_ligand_metal = df_metal_catalysts['ligand_or_core_type'].value_counts()
        print_proportions_ligand_metal_perc = df_metal_catalysts['ligand_or_core_type'].value_counts(normalize=True).mul(100).round(1)
        print(f"\nDistribution of 'ligand_or_core_type' (within Metal Catalysts - Total {len(df_metal_catalysts)}):")
        for item, count in print_proportions_ligand_metal.items():
            print(f"  {item}: {count} ({print_proportions_ligand_metal_perc[item]}%)")
    else:
        print("\nNo reactions classified as 'Metal Catalyst' found for metal_center/ligand_or_core_type breakdown.")

    df_organocatalysts = df[df['major_catalyst_class'] == 'Organocatalyst']
    if not df_organocatalysts.empty:
        print_proportions_organo_core = df_organocatalysts['ligand_or_core_type'].value_counts()
        print_proportions_organo_core_perc = df_organocatalysts['ligand_or_core_type'].value_counts(normalize=True).mul(100).round(1)
        print(f"\nDistribution of 'ligand_or_core_type' (within Organocatalysts - Total {len(df_organocatalysts)}):")
        for item, count in print_proportions_organo_core.items():
            print(f"  {item}: {count} ({print_proportions_organo_core_perc[item]}%)")

    else:
        print("\nNo reactions classified as 'Organocatalyst' found for ligand_or_core_type breakdown.")


    print_proportions('substrate_type') # Assuming this was well-corrected manually

    # --- Temporal Analysis ---
    # (Plot generation would happen here. Since I can't show plots,
    # I will prepare data suitable for plotting and discuss based on that.)

    print("\n--- Temporal Trends Data (Counts per Decade) ---")
    # Number of reactions per decade
    reactions_per_decade = df['decade'].value_counts().sort_index()
    print("\nTotal Asymmetric Reactions per Decade:")
    print(reactions_per_decade)

    # Major Catalyst Class per Decade
    catalyst_class_per_decade = df.groupby('decade')['major_catalyst_class'].value_counts().unstack(fill_value=0)
    print("\nMajor Catalyst Class Distribution per Decade:")
    print(catalyst_class_per_decade.to_string())

    # Metal Center per Decade (for Metal Catalysts)
    if not df_metal_catalysts.empty:
        metal_center_per_decade = df_metal_catalysts.groupby('decade')['metal_center'].value_counts().unstack(fill_value=0)
        print("\nMetal Center Distribution per Decade (for Metal Catalysts):")
        print(metal_center_per_decade.to_string())

        # Ligand/Core Type per Decade (for Metal Catalysts)
        ligand_metal_per_decade = df_metal_catalysts.groupby('decade')['ligand_or_core_type'].value_counts().unstack(fill_value=0)
        print("\nLigand/Core Type Distribution per Decade (for Metal Catalysts):")
        print(ligand_metal_per_decade.to_string())
    else:
        print("\nSkipping Metal Center/Ligand per Decade analysis as no Metal Catalysts were identified.")


    # Ligand/Core Type per Decade (for Organocatalysts)
    if not df_organocatalysts.empty:
        organo_core_per_decade = df_organocatalysts.groupby('decade')['ligand_or_core_type'].value_counts().unstack(fill_value=0)
        print("\nLigand/Core Type Distribution per Decade (for Organocatalysts):")
        print(organo_core_per_decade.to_string())
    else:
        print("\nSkipping Organocatalyst Core per Decade analysis as no Organocatalysts were identified.")


    # Substrate Type per Decade
    substrate_type_per_decade = df.groupby('decade')['substrate_type'].value_counts().unstack(fill_value=0)
    print("\nSubstrate Type Distribution per Decade:")
    print(substrate_type_per_decade.to_string())
    
    # Save the further classified dataframe
    output_filename_final = "final_classified_asymmetric_reactions.json"
    df.to_json(output_filename_final, orient='records', indent=2)
    print(f"\nDataframe with detailed catalyst parsing saved to {output_filename_final}")
    
    csv_output_filename_final = "final_classified_asymmetric_reactions.csv"
    df.to_csv(csv_output_filename_final, index=False)
    print(f"Dataframe also saved to {csv_output_filename_final}")

    return df


# --- Main Execution ---
if __name__ == "__main__":
    corrected_file_path = "classified_asymmetric_reactions_deleted_manural_deleted.json" # Make sure this file is in the same directory
    try:
        df_corrected = pd.read_json(corrected_file_path)
        df_analyzed = analyze_data(df_corrected.copy()) # Analyze a copy

        # At this point, df_analyzed contains the data used for the printed statistics.
        # The textual interpretation of trends would follow, based on the printed tables.
        # For example, one would look at how the counts in "Major Catalyst Class Distribution per Decade" change.
        print("\n\n--- INTERPRETATION OF TRENDS (Based on printed tables above) ---")
        print("The textual analysis of trends, proportions, and their interpretations would be manually constructed now,")
        print("drawing insights from the quantitative data printed above. This involves looking at how different categories")
        print("(e.g., 'Metal Catalyst', specific metals like 'Ru', specific ligands like 'BINAP') change in frequency")
        print("across the decades (1980s, 1990s, 2000s, 2010s, 2020s) and their overall share.")
        print("Key aspects to discuss would include:")
        print("1. Overall publication trend of asymmetric reactions in Org. Synth. (from 'Total Asymmetric Reactions per Decade').")
        print("2. Dominance and evolution of major catalyst classes (Metal vs. Organo vs. Enzyme).")
        print("3. For metal catalysts: which metals are prominent overall and in which decades? (e.g., Ti early on, Ru/Rh for hydrogenations, Pd/Cu for C-C couplings/conjugate additions).")
        print("4. For metal catalysts: which ligand types gain prominence? (e.g., emergence of BINAP, Salen, BOX).")
        print("5. For organocatalysts: rise of specific cores (Proline, MacMillan, CPA) especially post-2000.")
        print("6. Evolution of reaction types: are certain reactions more common in earlier vs. later decades?")
        print("7. Common substrate classes and any shifts over time.")
        print("8. Relating these trends to major breakthroughs (e.g., Nobel Prizes) and the specific focus of Org. Synth. (practicality, scalability).")
        print("9. Explaining *why* certain catalysts/reactions/substrates are prevalent (utility, availability, robustness).")


    except FileNotFoundError:
        print(f"Error: The manually corrected file '{corrected_file_path}' was not found.")
    except Exception as e:
        print(f"An error occurred: {e}")