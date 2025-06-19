import json
import re
import os

# --- Configuration ---
MODERN_REACTION_START_YEAR = 1980 # Adjustable threshold for "modern" reactions

# Regex patterns to find ee, er, dr values.
# These patterns aim to capture phrases like "95% ee", "ee of 95%", "90:10 er", "er of 90:10"
# Allowing for variations in spacing and abbreviations.
EE_PATTERNS = [
    re.compile(r'\b(\d{1,3}(?:\.\d+)?\s*%(?:\s*(?:e\.e\.|ee|enantiomeric\s+excess))\b)', re.IGNORECASE),
    re.compile(r'\b(?:e\.e\.|ee|enantiomeric\s+excess)\s*(?:of|is|was|:|value)?\s*>?=?\s*(\d{1,3}(?:\.\d+)?\s*%)', re.IGNORECASE),
    re.compile(r'\b(ee\s*=\s*\d{1,3}(?:\.\d+)?\s*%)',re.IGNORECASE), # ee = X%
    re.compile(r'\b(\d{1,3}(?:\.\d+)?)\s*%(?:\s*ee)', re.IGNORECASE), # e.g. ">99 % ee" - captures the number part
]
ER_PATTERNS = [
    re.compile(r'\b(\d{1,3}(?:\.\d+)?\s*:\s*\d{1,3}(?:\.\d+)?(?:\s*(?:e\.r\.|er|enantiomeric\s+ratio))\b)', re.IGNORECASE),
    re.compile(r'\b(?:e\.r\.|er|enantiomeric\s+ratio)\s*(?:of|is|was|:|value)?\s*>?=?\s*(\d{1,3}(?:\.\d+)?\s*:\s*\d{1,3}(?:\.\d+)?\b)', re.IGNORECASE),
    re.compile(r'\b(er\s*=\s*\d{1,3}(?:\.\d+)?\s*:\s*\d{1,3}(?:\.\d+)?\b)',re.IGNORECASE), # er = X:Y
]
DR_PATTERNS = [
    re.compile(r'\b(\d{1,3}(?:\.\d+)?\s*:\s*\d{1,3}(?:\.\d+)?(?:\s*(?:d\.r\.|dr|diastereomeric\s+ratio|diastereoselectivity))\b)', re.IGNORECASE),
    re.compile(r'\b(?:d\.r\.|dr|diastereomeric\s+ratio|diastereoselectivity)\s*(?:of|is|was|:|value)?\s*>?=?\s*(\d{1,3}(?:\.\d+)?\s*:\s*\d{1,3}(?:\.\d+)?\b)', re.IGNORECASE),
    re.compile(r'\b(dr\s*=\s*\d{1,3}(?:\.\d+)?\s*:\s*\d{1,3}(?:\.\d+)?\b)',re.IGNORECASE), # dr = X:Y
]

# Keywords for titles that might suggest asymmetric synthesis, as a secondary check or for broader searches later
# For now, primary focus is on reported ee/dr in procedure.
TITLE_KEYWORDS = [
    "asymmetric", "enantioselective", "chiral catalyst", "organocatalytic",
    "sharpless", "noyori", "knowles", "jacobsen", "macmillan", "list", "jørgensen", "fu",
    "binap", "box", "pybox", "salen", "cinchona", "proline", "phosphoric acid" # examples of catalyst/ligand families
]
TITLE_KEYWORD_PATTERN = re.compile(r'\b(?:' + '|'.join(TITLE_KEYWORDS) + r')\b', re.IGNORECASE)

# --- Helper Functions ---

def extract_year_from_cite(cite_string):
    """
    Extracts the year from the 'Cite' string (e.g., "Org. Synth. 1921, 1, 3").
    """
    if not cite_string:
        return None
    match = re.search(r'\b(\d{4})\b', cite_string)
    return int(match.group(1)) if match else None

def find_stereochem_mentions(text):
    """
    Searches text for mentions of ee, er, or dr values.
    Returns a list of found mentions (actual matched strings).
    """
    mentions = []
    all_patterns = EE_PATTERNS + ER_PATTERNS + DR_PATTERNS
    for pattern in all_patterns:
        # Using finditer to get match objects, which give access to the full matched string via group(0)
        for match in pattern.finditer(text):
            # Extract the full match, or the first non-empty capturing group if a more specific part is needed
            # For this purpose, the whole phrase (group(0)) is usually best.
            mention_text = match.group(0) # The entire substring matched by the RE
            if mention_text and mention_text not in mentions: # Add if not None and unique
                mentions.append(str(mention_text).strip())
    return mentions

# --- Main Processing Logic ---

def process_org_synth_files(file_info_list):
    """
    Processes a list of Organic Syntheses JSON file information.
    Filters for modern asymmetric catalytic reactions based on reported ee/dr values.
    """
    all_extracted_reactions = []
    total_articles_scanned = 0
    relevant_reactions_count = 0

    # Sort file_info_list by filename to process in rough chronological order of volumes
    def get_volume_start(filename):
        match = re.search(r'Volume(\d+)', filename) # Simpler regex for volume number
        return int(match.group(1)) if match else 999 # Put unmatched last
    
    sorted_file_info_list = sorted(file_info_list, key=lambda x: get_volume_start(x['fileName']))

    for file_info in sorted_file_info_list:
        filename = file_info['fileName']
        print(f"Processing file: {filename}...")
        try:
            # Assuming files are accessible in the environment where this code is run
            with open(filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except FileNotFoundError:
            print(f"Error: File not found: {filename}")
            continue
        except json.JSONDecodeError:
            print(f"Error: Could not decode JSON from file: {filename}")
            continue
        
        volume_source_name = filename.replace('_deleted.json', '').replace('.json', '')


        for article_id, article_data in data.items():
            total_articles_scanned += 1

            title = article_data.get("Title", "")
            procedure_list = article_data.get("Procedure", [])
            cite_string = article_data.get("Cite", "")
            doi = article_data.get("DOI", "")

            year = extract_year_from_cite(cite_string)

            if year is None or year < MODERN_REACTION_START_YEAR:
                continue 

            procedure_text = "\n".join(procedure_list) if isinstance(procedure_list, list) else str(procedure_list)
            stereochem_mentions = find_stereochem_mentions(procedure_text)
            title_has_keywords = bool(TITLE_KEYWORD_PATTERN.search(title))


            if stereochem_mentions: 
                reaction_data = {
                    'volume_source': volume_source_name,
                    'article_id': article_id,
                    'year': year,
                    'title': title,
                    'doi': doi,
                    'procedure_snippet': procedure_text[:1000] + "..." if len(procedure_text) > 1000 else procedure_text,
                    'quantitative_stereochem_mentions': stereochem_mentions,
                    'title_has_asym_keywords': title_has_keywords
                }
                all_extracted_reactions.append(reaction_data)
                relevant_reactions_count += 1
            elif title_has_keywords and year >= 1990: # Broader search for newer articles with title keywords if no explicit ee/dr
                # This part can be adjusted or removed if strict ee/dr reporting is the ONLY criterion
                # For now, let's include them but perhaps flag them differently or analyze separately.
                # For this initial run, we stick to the primary criteria of reported ee/dr.
                pass


    print(f"\n--- Processing Summary ---")
    print(f"Total files processed: {len(sorted_file_info_list)}")
    print(f"Total articles scanned (since {MODERN_REACTION_START_YEAR}): Approximately articles in processed files from this year onwards.") # Actual count of scanned modern articles is implicit.
    print(f"Total articles fully parsed: {total_articles_scanned}") # This is total articles in all files, not just modern
    print(f"Identified relevant asymmetric reactions (with ee/er/dr mentions since {MODERN_REACTION_START_YEAR}): {relevant_reactions_count}")

    return all_extracted_reactions

# --- Example Usage ---
if __name__ == "__main__":
    # This list will be populated by the user's file upload mechanism
    # These are the file names mentioned in the prompt
    file_infos = [
        {"fileName": "Volume1-10_deleted.json"},
        {"fileName": "Volume11-20_deleted.json"},
        {"fileName": "Volume21-30_deleted.json"},
        {"fileName": "Volume31-40_deleted.json"},
        {"fileName": "Volume41-50_deleted.json"},
        {"fileName": "Volume51-60_deleted.json"},
        {"fileName": "Volume61-70_deleted.json"},
        {"fileName": "Volume71-80_deleted.json"},
        {"fileName": "Volume81-90_deleted.json"},
        {"fileName": "Volume91-100_deleted.json"},
    ]
    
    # This check is for local testing; in the execution environment, files are assumed accessible.
    # print("Checking for local file existence (for testing purposes):")
    # files_present_locally = True
    # for fi_idx, fi_val in enumerate(file_infos):
    #     if not os.path.exists(fi_val['fileName']):
    #         print(f"Warning: File {fi_val['fileName']} not found in current directory.")
    #         # To prevent crash if a file is missing, it's better to handle it in process_org_synth_files
    # files_present_locally = False 
    # if files_present_locally:
    # print("All specified files seem to be present locally for testing.")
    # print("-" * 20)

    extracted_reactions = process_org_synth_files(file_infos)

    if extracted_reactions:
        print(f"\n--- Sample of Extracted Asymmetric Reactions (first 5) ---")
        for i, reaction in enumerate(extracted_reactions[:5]):
            print(f"\nReaction {i+1}:")
            print(f"  Source: {reaction['volume_source']}")
            print(f"  Article ID: {reaction['article_id']}")
            print(f"  Year: {reaction['year']}")
            print(f"  Title: {reaction['title']}")
            print(f"  DOI: {reaction['doi']}")
            print(f"  Mentions: {reaction['quantitative_stereochem_mentions']}")
            print(f"  Title indicates asymmetric: {reaction['title_has_asym_keywords']}")
            # print(f"  Procedure Snippet: {reaction['procedure_snippet']}") # Can be very long, enable if needed

        # To save all results to a JSON file (useful for next steps):
        output_filename = "extracted_asymmetric_reactions.json"
        with open(output_filename, 'w', encoding='utf-8') as outfile:
            json.dump(extracted_reactions, outfile, indent=2)
        print(f"\nAll {len(extracted_reactions)} extracted reactions saved to {output_filename}")

        # Example of loading into pandas for further analysis (optional, for user):
        # import pandas as pd
        # df = pd.DataFrame(extracted_reactions)
        # print("\nDataFrame head:")
        # print(df.head())
        # print(f"\nDataFrame shape: {df.shape}")

    else:
        print(f"\nNo relevant asymmetric reactions with ee/er/dr mentions found (since {MODERN_REACTION_START_YEAR}) based on the criteria.")