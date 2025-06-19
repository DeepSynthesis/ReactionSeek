import json
import re
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from collections import Counter

# --- Keyword Definitions for Classification ---

# 1. Catalyst System Type
CATALYST_KEYWORDS = {
    "Enzyme/Biocatalyst": [
        "yeast", "baker's yeast", "lipase", "enzyme", "esterase", "dehydrogenase",
        "oxidase", "reductase", "whole cell", "microorganism", "fermentation", "biocatalytic", "biotransformation"
    ],
    "Organocatalyst - Proline/Amino Acid": ["proline", "diphenylprolinol", "amino acid based"],
    "Organocatalyst - Chiral Amine/Imidazolidinone": [
        "cinchona alkaloid", "quinine", "quinidine", "cinchonidine", "cinchonine",
        "macmillan catalyst", "imidazolidinone", "jørgensen-hayashi",
        "primary amine catalyst", "secondary amine catalyst", "((S)-(-)-alpha,alpha-Diphenyl-2-pyrrolidinemethanol trimethylsilyl ether)" # Example of specific organocatalyst
    ],
    "Organocatalyst - Chiral Phosphoric Acid (CPA)/Brønsted Acid": [
        "phosphoric acid catalyst", "brønsted acid catalyst", "binol phosphoric acid", "trip", "strip",
        "chiral phosphoric acid", "chiral brønsted acid"
    ],
    "Organocatalyst - NHC (N-Heterocyclic Carbene)": ["nhc", "n-heterocyclic carbene", "imidazolylidene", "triazolylidene"],
    "Organocatalyst - Thiourea/Urea": ["thiourea catalyst", "urea catalyst", "schreiner's thiourea"],
    "Organocatalyst - Phase Transfer (Chiral PTC)": ["phase transfer catalyst", "chiral quaternary ammonium", "chiral onium salt", "chiral crown ether"],
    "Organocatalyst - General/Other": ["organocatalyst", "organocatalytic", "metal-free catalyst"], # More general, lower priority

    "Metal Catalyst - Ruthenium (Ru)": ["ruthenium", " ru[(]", "rucl2", "ru-binap", "grubbs catalyst" ], # Added Grubbs as it's often Ru
    "Metal Catalyst - Rhodium (Rh)": ["rhodium", "rh[(]", "rhcl", "wilkinson's catalyst"],
    "Metal Catalyst - Palladium (Pd)": ["palladium", "pd[(]", "pdcl2", "pd(OAc)2", "pd(PPh3)4", "buchwald", "hartwig"],
    "Metal Catalyst - Iridium (Ir)": ["iridium", "ir[(]"],
    "Metal Catalyst - Copper (Cu)": ["copper", "cu[(]", "cucl", "cui", "cu(otc)2", "cuotc"],
    "Metal Catalyst - Nickel (Ni)": ["nickel", "ni[(]", "nicl2"],
    "Metal Catalyst - Titanium (Ti)": ["titanium", "ti[(]", "ti(OiPr)4", "sharpless catalyst", "katsuki-sharpless"], # Sharpless often Ti
    "Metal Catalyst - Zinc (Zn)": ["zinc", "zn[(]", "zn(otf)2", "diethylzinc"],
    "Metal Catalyst - Iron (Fe)": ["iron", "fe[(]", "fecl3"],
    "Metal Catalyst - Gold (Au)": ["gold", "au[(]", "aucl", "aucl3"],
    "Metal Catalyst - Silver (Ag)": ["silver", "ag[(]", "agotf"],
    "Metal Catalyst - Aluminum (Al)": ["aluminum", "al[(]", "alcl3", "(salen)al"],
    "Metal Catalyst - Magnesium (Mg)": ["magnesium", "mg[(]", "grignard reagent"], # Grignard can be catalytic in some contexts
    "Metal Catalyst - Boron (B)": ["boron", "borane", " BH3", " Corey-Bakshi-Shibata", "CBS catalyst", "oxazaborolidine"], # CBS is catalytic
    "Metal Catalyst - Zirconium (Zr)": ["zirconium", "zr[(]"],
    "Metal Catalyst - Scandium/Lanthanide": ["scandium", "lanthanide", "ytterbium", "sc(otf)3", "yb(otf)3"],
    "Metal Catalyst - General Ligands": [ # These suggest a metal complex if a specific metal isn't caught
        "binap", "salen", "box ", "pybox", "phosphine", "diamine", "bis(oxazoline)", "duphos", "josiphos",
        "ferrocene ligand", "phos ", "chiral ligand"
    ],
    "Metal Catalyst - General": ["metal catalyst", "transition metal", "lewis acid catalyst"], # Lowest priority for metals

    "Stoichiometric Chiral Auxiliary/Reagent": [
        "chiral auxiliary", "stoichiometric chiral", "chiral pool", "(-)-menthyl", "(+)-menthyl", "ephedrine", "pseudoephedrine",
        "oppolzer's sultam", "evans auxiliary", "myers auxiliary", "dimenthyl succinate", "chiral starting material"
    ],
    "Resolution Agent/Process": [
        "resolution with", "resolved by", "resolving agent", "brucine", "strychnine", "(r,r)-tartaric acid", "(s,s)-tartaric acid",
        "dibenzoyltartaric acid", "camphorsulfonic acid", "chiral hplc separation", "preparative chiral hplc"
    ]
}

# 2. Reaction Type
REACTION_TYPE_KEYWORDS = {
    "Reduction (C=O, C=N)": ["reduction of ketone", "reduction of aldehyde", "reduction of imine", "hydrosilylation", "borane reduction", "noyori hydrogenation", "transfer hydrogenation of ketone", "cbs reduction"],
    "Hydrogenation (C=C, C#C)": ["hydrogenation of alkene", "hydrogenation of olefin", "hydrogenation of alkyne", "asymmetric hydrogenation"],
    "Oxidation": ["oxidation", "epoxidation", "sharpless epoxidation", "jacobsen epoxidation", "dihydroxylation", "sharpless dihydroxylation", "sulfoxidation", "baeyer-villiger", "oxidative kinetic resolution"],
    "Aldol/Mannich/Related C-C": ["aldol reaction", "mannich reaction", "nitroaldol", "henry reaction", "mukaiyama aldol", "direct aldol"],
    "Michael Addition/Conjugate Addition": ["michael addition", "conjugate addition", "1,4-addition"],
    "Cycloaddition": ["diels-alder", "cycloaddition", "[3+2]", "[4+2]", "[2+2]", "hetero-diels-alder"],
    "Allylic Substitution/Alkylation": ["allylic substitution", "allylic alkylation", "tsuji-trost reaction", "asymmetric allylic"],
    "C-H Activation/Functionalization": ["c-h activation", "c-h functionalization", "c-h borylation", "c-h arylation"],
    "Cross-Coupling (C-C, C-N, C-O)": ["suzuki coupling", "heck reaction", "neghishi coupling", "sonogashira coupling", "buchwald-hartwig amination", "ullmann coupling", "kumada coupling"],
    "Isomerization": ["isomerization", "racemization control"],
    "Alkylation/Addition (non-carbonyl, non-allylic)": ["alkylation", "cyanation", "grignard addition to", "organolithium addition to"],
    "Ring Opening/Closing (non-cycloaddition)": ["ring opening", "ring closing metathesis", "rcm", "cyclization", "lactonization", "lactamization"],
    "Hydrofunctionalization (of C=C, C#C)": ["hydroboration", "hydroamination", "hydrocyanation", "hydrosilylation of alkene", "hydroformylation"],
    "Synthesis of Chiral Catalyst/Ligand/Auxiliary": [
        "synthesis of chiral ligand", "preparation of chiral catalyst", "synthesis of chiral auxiliary",
        "synthesis of binap", "preparation of salen", "synthesis of box", "synthesis of proline derivative",
        "resolution of .* ligand", "resolution of .* catalyst", "1,1'-binaphthyl-2,2'-diyl hydrogen phosphate" # Specific example
    ],
    "Resolution (Kinetic/Dynamic/Classical)": ["resolution", "kinetic resolution", "dynamic kinetic resolution", "classical resolution", "resolved by", "separation of enantiomers"],
    "Other/General Asymmetric Transformation": ["asymmetric synthesis", "enantioselective synthesis", "stereoselective synthesis"] # Generic fallback
}

# 3. Substrate Type (Simplified)
SUBSTRATE_TYPE_KEYWORDS = {
    "Ketone/Aldehyde/α,β-Unsaturated Carbonyl": ["ketone", "aldehyde", "enone", "enal", "oxo", "α,β-unsaturated carbonyl", "cyclohexanone", "acetophenone", "benzaldehyde", "acetoacetate", "3-oxo carboxylate"],
    "Imine/Hydrazone/Nitrone": ["imine", "ketimine", "aldimine", "hydrazone", "nitrone", "schiff base"],
    "Alkene/Olefin/Allene/Diene": ["alkene", "olefin", "styrene", "allene", "diene", "enyne", "vinyl"],
    "Alkyne": ["alkyne", "propargylic"],
    "Ester/Lactone/Acid/Amide/Anhydride (as main reactant)": ["ester", "lactone", "carboxylic acid", "amide", "lactam", "anhydride", "succinate"], # e.g., for alpha-functionalization or if it IS the prochiral center
    "Alcohol/Phenol (for KR or derivatization)": ["alcohol", "phenol", "diol", "hydroxybutanoate"],
    "Sulfide/Thioether": ["sulfide", "thioether", "thioester"],
    "Halide/Pseudohalide (for coupling/substitution)": ["aryl halide", "vinyl halide", "alkyl halide", "bromide", "chloride", "iodide", "triflate"],
    "Nitro Compound": ["nitroalkane", "nitroolefin", "nitroaldol"],
    "Organoboron/Organosilicon/Organometallic Reagent": ["boronic acid", "boronate ester", "organosilane", "grignard reagent", "organolithium"],
    "Phosphorus Compound (e.g. for making chiral P-ligands)": ["phosphine oxide", "phosphinate", "phosphonate", "hydrogen phosphate"],
    "Heterocycle (as core structure being modified)": ["furan", "pyran", "pyrrolidine", "piperidine", "indole"],
    "Racemic Mixture (for resolution)": ["racemic", "(±)-", "dl-", "racemate"]
}

# --- Classification Functions ---

def classify_catalyst_system(title, snippet):
    text_to_search = (title + " " + snippet).lower()
    # Priority: Enzyme > Organo > Metal > Stoich/Resolution
    # Within Organo/Metal, more specific first.

    for category, keywords in CATALYST_KEYWORDS.items():
        for keyword in keywords:
            if re.search(r'\b' + re.escape(keyword.lower()) + r'\b', text_to_search):
                # Special handling for CBS (boron-based organometallic catalyst, but often grouped with organocatalysis conceptually)
                if "Organocatalyst" in category and "boron" in category.lower(): # e.g. "CBS"
                    return "Organocatalyst - Boron Based (e.g. CBS)"
                if "Metal Catalyst - Boron (B)" == category and ("cbs catalyst" in keyword or "oxazaborolidine" in keyword):
                     return "Organocatalyst - Boron Based (e.g. CBS)" # Reclassify CBS as organo
                if category.startswith("Metal Catalyst - General Ligands"):
                    # If a specific metal was already found, append ligand info, else classify as "Metal Catalyst (Ligand indicated)"
                    # This part is complex and might be better handled by first finding metal, then ligand.
                    # For now, if this matches, and no specific metal before, it's a general metal.
                    # This rule is tricky; a more robust system would identify metal and ligands separately.
                    # For simplicity, if a known ligand family is named, assume metal involvement if not enzyme/organo.
                    return "Metal Catalyst (Ligand Family Mentioned)"
                return category
    return "Catalyst System Unknown"

def classify_reaction_type(title, snippet):
    text_to_search = (title + " " + snippet).lower()
    # Priority for specific reaction types
    for category, keywords in REACTION_TYPE_KEYWORDS.items():
        for keyword in keywords:
            if re.search(r'\b' + re.escape(keyword.lower()) + r'\b', text_to_search):
                return category
            # Handle cases like "resolution of 1,1'-bi-2-naphthol" for "Synthesis of Chiral..."
            if "resolution of .* ligand" in keyword or "resolution of .* catalyst" in keyword:
                if re.search(keyword.replace(".*", ".+").lower(), text_to_search):
                     return "Synthesis of Chiral Catalyst/Ligand/Auxiliary"

    return "Reaction Type Unknown"


def classify_substrate_type(title, snippet):
    text_to_search = (title + " " + snippet).lower()
    for category, keywords in SUBSTRATE_TYPE_KEYWORDS.items():
        for keyword in keywords:
            if re.search(r'\b' + re.escape(keyword.lower()) + r'\b', text_to_search):
                return category
    return "Substrate Type Unknown"

# --- Main Analysis Script ---
def main():
    try:
        df = pd.read_json("extracted_asymmetric_reactions.json")
    except FileNotFoundError:
        print("Error: 'extracted_asymmetric_reactions.json' not found. Please ensure the file is in the correct directory.")
        return
    except ValueError as e:
        print(f"Error reading JSON file: {e}. Please check the file format.")
        return

    print(f"Loaded {len(df)} reactions for classification.")

    # Apply classifications
    df['catalyst_system_type'] = df.apply(lambda row: classify_catalyst_system(row['title'], row['procedure_snippet']), axis=1)
    df['reaction_type'] = df.apply(lambda row: classify_reaction_type(row['title'], row['procedure_snippet']), axis=1)
    df['substrate_type'] = df.apply(lambda row: classify_substrate_type(row['title'], row['procedure_snippet']), axis=1)

    # --- Temporal Analysis ---
    plt.style.use('seaborn-v0_8-whitegrid')

    # 1. Number of asymmetric reactions per year
    yearly_counts = df['year'].value_counts().sort_index()
    plt.figure(figsize=(12, 6))
    yearly_counts.plot(kind='bar', colormap='viridis')
    plt.title('Number of Reported Asymmetric Reactions per Year in Organic Syntheses (Filtered)')
    plt.xlabel('Year')
    plt.ylabel('Number of Reactions')
    plt.tight_layout()
    plt.savefig("asymmetric_reactions_per_year.png")
    plt.close()
    print("Generated plot: asymmetric_reactions_per_year.png")

    # Create decade column for coarser trend analysis
    df['decade'] = (df['year'] // 10) * 10

    # 2. Distribution of Catalyst System Types over Decades
    catalyst_trends = df.groupby('decade')['catalyst_system_type'].value_counts(normalize=True).mul(100).unstack(fill_value=0)
    # Filter out very minor categories for cleaner plot or combine them
    major_catalyst_categories = df['catalyst_system_type'].value_counts()
    catalyst_threshold = 5 # Count threshold to be considered "major"
    other_catalysts_label = f'Other (<{catalyst_threshold} total entries)'

    def aggregate_minor_catalysts(row):
        major_cols = major_catalyst_categories[major_catalyst_categories >= catalyst_threshold].index
        new_row = row[major_cols.intersection(row.index)].copy()
        new_row[other_catalysts_label] = row[major_cols.difference(row.index).union(row.index.difference(major_cols))].sum()
        return new_row

    if not catalyst_trends.empty:
        # Apply aggregation if many categories
        if len(catalyst_trends.columns) > 10: # Heuristic for "too many categories"
            catalyst_trends_agg = pd.DataFrame({idx: aggregate_minor_catalysts(row) for idx, row in catalyst_trends.iterrows()}).T
        else:
            catalyst_trends_agg = catalyst_trends

        catalyst_trends_agg.plot(kind='bar', stacked=True, figsize=(15, 8), colormap='tab20')
        plt.title('Distribution of Catalyst System Types per Decade (%)')
        plt.xlabel('Decade')
        plt.ylabel('Percentage of Reactions')
        plt.legend(title='Catalyst System Type', bbox_to_anchor=(1.05, 1), loc='upper left')
        plt.tight_layout()
        plt.savefig("catalyst_types_per_decade.png")
        plt.close()
        print("Generated plot: catalyst_types_per_decade.png")
    else:
        print("No data for catalyst trends plot after grouping.")


    # 3. Distribution of Reaction Types over Decades
    reaction_trends = df.groupby('decade')['reaction_type'].value_counts(normalize=True).mul(100).unstack(fill_value=0)
    major_reaction_categories = df['reaction_type'].value_counts()
    reaction_threshold = 5 # Count threshold
    other_reactions_label = f'Other (<{reaction_threshold} total entries)'
    
    def aggregate_minor_reactions(row):
        major_cols = major_reaction_categories[major_reaction_categories >= reaction_threshold].index
        new_row = row[major_cols.intersection(row.index)].copy()
        new_row[other_reactions_label] = row[major_cols.difference(row.index).union(row.index.difference(major_cols))].sum()
        return new_row

    if not reaction_trends.empty:
        if len(reaction_trends.columns) > 10:
             reaction_trends_agg = pd.DataFrame({idx: aggregate_minor_reactions(row) for idx, row in reaction_trends.iterrows()}).T
        else:
            reaction_trends_agg = reaction_trends
            
        reaction_trends_agg.plot(kind='bar', stacked=True, figsize=(15, 8), colormap='tab20b')
        plt.title('Distribution of Reaction Types per Decade (%)')
        plt.xlabel('Decade')
        plt.ylabel('Percentage of Reactions')
        plt.legend(title='Reaction Type', bbox_to_anchor=(1.05, 1), loc='upper left')
        plt.tight_layout()
        plt.savefig("reaction_types_per_decade.png")
        plt.close()
        print("Generated plot: reaction_types_per_decade.png")
    else:
        print("No data for reaction trends plot after grouping.")

    # Display some classification results
    print("\n--- Sample of Classified Reactions (first 10) ---")
    print(df[['year', 'title', 'catalyst_system_type', 'reaction_type', 'substrate_type']].head(10).to_string())

    print("\n---Counts for Catalyst System Types---")
    print(df['catalyst_system_type'].value_counts().to_string())
    print("\n---Counts for Reaction Types---")
    print(df['reaction_type'].value_counts().to_string())
    print("\n---Counts for Substrate Types---")
    print(df['substrate_type'].value_counts().to_string())

    # Save the enriched dataframe
    output_filename_classified = "classified_asymmetric_reactions.json"
    df.to_json(output_filename_classified, orient='records', indent=2)
    print(f"\nEnriched data saved to {output_filename_classified}")
    
    csv_output_filename = "classified_asymmetric_reactions.csv"
    df.to_csv(csv_output_filename, index=False)
    print(f"Enriched data also saved to {csv_output_filename}")

if __name__ == "__main__":
    main()