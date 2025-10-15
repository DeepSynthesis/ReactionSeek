import pandas as pd
import csv
import os
import json
from collections import defaultdict

def read_output_table(file_path):
    """
    Step 1: Read output_table.csv where multiple entries within a single cell are separated by ", "
    
    Returns:
        pd.DataFrame: The loaded CSV data
    """
    try:
        # Read the CSV file with proper handling
        df = pd.read_csv(file_path)
        
        print(f"Successfully loaded CSV with {len(df)} rows and {len(df.columns)} columns")
        print(f"Columns: {list(df.columns)}")
        
        # Display basic info about the data
        print(f"\nFirst few rows:")
        print(df.head())
        
        return df
        
    except Exception as e:
        print(f"Error reading CSV file: {e}")
        return None

def read_ann_file(ann_file_path):
    """
    Read and parse .ann file to extract entities by type
    
    Returns:
        dict: Dictionary with entity types as keys and sets of entity texts as values
    """
    entities = defaultdict(set)
    
    try:
        with open(ann_file_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and line.startswith('T'):
                    parts = line.split('\t')
                    if len(parts) >= 3:
                        entity_info = parts[1].split(' ', 1)[0]  # Get entity type
                        entity_text = parts[2].strip()  # Get entity text
                        entities[entity_info].add(entity_text)
    except Exception as e:
        print(f"Error reading ann file {ann_file_path}: {e}")
    
    return entities

def split_csv_entries(entry):
    """
    Split CSV entries that are separated by ", " and clean them
    Exclude "N/A" entries from evaluation
    
    Returns:
        set: Set of cleaned entries (excluding N/A)
    """
    if pd.isna(entry) or entry == "N/A" or entry.strip() == "":
        return set()
    
    # Split by ", " and clean each entry
    entries = [e.strip() for e in str(entry).split(', ') if e.strip()]
    
    # Filter out "N/A" entries (case insensitive)
    filtered_entries = [e for e in entries if e.lower() != "n/a"]
    
    return set(filtered_entries)

def normalize_for_comparison(text):
    """
    Normalize text for special case comparisons
    Add manual adjustments for special cases here
    
    Returns:
        str: normalized text
    """
    # Convert to lowercase for case-insensitive matching
    normalized = text.strip().lower()
    
    # Normalize whitespace: replace multiple spaces with single space
    import re
    normalized = re.sub(r'\s+', ' ', normalized)
    
    # Special case normalization for TIME field: h, H, hour, Hour, Hours, hours equivalence
    # Replace all variations with "h" for standardization
    
    # Match patterns like "2 hours", "1 hour", "16 Hours", "3 Hour" and convert to "2 h", "1 h", "16 h", "3 h"
    normalized = re.sub(r'\b(\d+(?:\.\d+)?)\s*hours?\b', r'\1 h', normalized, flags=re.IGNORECASE)
    
    # Handle capital H variations: "2 H" -> "2 h"
    normalized = re.sub(r'\b(\d+(?:\.\d+)?)\s*h\b', r'\1 h', normalized, flags=re.IGNORECASE)
    
    # Also handle cases like "2hrs", "2Hrs" -> "2 h"
    normalized = re.sub(r'\b(\d+(?:\.\d+)?)\s*hrs?\b', r'\1 h', normalized, flags=re.IGNORECASE)
    
    # Handle "minutes" -> "min" standardization as well
    normalized = re.sub(r'\b(\d+(?:\.\d+)?)\s*minutes?\b', r'\1 min', normalized)
    
    # Special case normalization for TEMPERATURE field: RT, r.t., room temperature equivalence
    # Standardize all variations to "rt"
    if normalized in ['room temperature', 'room temp', 'ambient temperature', 'ambient temp']:
        normalized = 'rt'
    elif normalized in ['r.t.', 'r.t', 'r t', 'rt.']:
        normalized = 'rt'
    
    # Special case normalization for YIELD fields: normalize spaces around % symbol
    # "62 %" -> "62%", "62  %" -> "62%", etc.
    normalized = re.sub(r'\b(\d+(?:\.\d+)?)\s*%', r'\1%', normalized)
    
    # TODO: Add additional special case normalizations here
    # Example special cases to handle:
    # - Temperature format variations
    # - Chemical name variations
    
    return normalized

def create_normalized_sets(original_set):
    """
    Create both original and normalized versions of the set for comparison
    
    Returns:
        tuple: (original_set, normalized_set, text_to_original_mapping)
    """
    normalized_set = set()
    text_to_original = {}
    
    for text in original_set:
        normalized_text = normalize_for_comparison(text)
        normalized_set.add(normalized_text)
        # Handle multiple original texts mapping to same normalized text
        if normalized_text not in text_to_original:
            text_to_original[normalized_text] = []
        text_to_original[normalized_text].append(text)
    
    return original_set, normalized_set, text_to_original

def compare_sets_with_special_cases(csv_set, ann_set):
    """
    Compare two sets with special case handling for manual TP adjustments
    
    This function is designed to handle cases like:
    - "RT" vs "room temperature" should be considered the same (TP)
    - "title compound" in ANN-only should be treated as TP not FN
    - Other domain-specific equivalences
    
    Returns:
        tuple: (TP, FP, FN, detailed_matches) where detailed_matches contains
               information about what was matched including special cases
    """
    
    # === SPECIAL CASE HANDLING SECTION ===
    # Add specific special case rules here
    # This section is reserved for manual adjustments to TP recognition
    
    # Special equivalences for exact matching (all lowercase)
    special_equivalences = {
        "aqueous": "water",  # aqueous and water should be treated as equivalent
        "water": "aqueous",  # bidirectional mapping
        "ch2cl2": "dichloromethane",  # CH2Cl2 and dichloromethane should be treated as equivalent
        "dichloromethane": "ch2cl2",  # bidirectional mapping
        "dcm": "dichloromethane",  # DCM is also dichloromethane
        "dcm": "ch2cl2",  # DCM is also CH2Cl2
        # "rt": "room temperature",  # Example - add when needed
        # "r.t.": "room temperature", 
        # Add more equivalences as needed
    }
    
    # Special cases for ANN-only items that should be treated as TP (all lowercase)
    ann_only_as_tp = {
        "title compound",  # title compound in ANN-only should be TP
        # Add more cases as needed
    }
    
    # === END SPECIAL CASE HANDLING SECTION ===
    
    # Create normalized versions for comparison
    csv_orig, csv_norm, csv_to_orig = create_normalized_sets(csv_set)
    ann_orig, ann_norm, ann_to_orig = create_normalized_sets(ann_set)
    
    # Track what gets matched
    matched_csv = set()
    matched_ann = set()
    detailed_matches = {
        'exact_matches': set(),
        'special_case_matches': [],
        'containment_matches': [],
        'ann_only_as_tp': set(),
        'csv_only': set(),
        'ann_only': set()
    }
    
    # First pass: exact matches (normalized)
    exact_matches = csv_norm.intersection(ann_norm)
    for norm_text in exact_matches:
        # Handle multiple original texts mapping to same normalized text
        csv_orig_texts = csv_to_orig.get(norm_text, [norm_text])
        ann_orig_texts = ann_to_orig.get(norm_text, [norm_text])
        
        # If we got single values instead of lists (backward compatibility)
        if not isinstance(csv_orig_texts, list):
            csv_orig_texts = [csv_orig_texts]
        if not isinstance(ann_orig_texts, list):
            ann_orig_texts = [ann_orig_texts]
        
        # Match all combinations
        for csv_orig_text in csv_orig_texts:
            for ann_orig_text in ann_orig_texts:
                matched_csv.add(csv_orig_text)
                matched_ann.add(ann_orig_text)
                detailed_matches['exact_matches'].add((csv_orig_text, ann_orig_text))
    
    # Second pass: special case equivalence matches
    remaining_csv = csv_orig - matched_csv
    remaining_ann = ann_orig - matched_ann
    
    # Apply special equivalence rules
    for csv_text in remaining_csv.copy():
        for ann_text in remaining_ann.copy():
            csv_norm = normalize_for_comparison(csv_text)
            ann_norm = normalize_for_comparison(ann_text)
            # Check if they are equivalent through special rules
            if (csv_norm in special_equivalences and 
                special_equivalences[csv_norm] == ann_norm) or \
               (ann_norm in special_equivalences and 
                special_equivalences[ann_norm] == csv_norm):
                matched_csv.add(csv_text)
                matched_ann.add(ann_text)
                remaining_csv.remove(csv_text)
                remaining_ann.remove(ann_text)
                detailed_matches['special_case_matches'].append((csv_text, ann_text))
                break
    
    # Third pass: Check for containment relationships
    # When ANN entry is fully contained within CSV entry, treat as TP
    remaining_csv_after_equivalence = csv_orig - matched_csv
    remaining_ann_after_equivalence = ann_orig - matched_ann
    
    for csv_text in remaining_csv_after_equivalence.copy():
        matched_ann_texts = []
        for ann_text in remaining_ann_after_equivalence.copy():
            csv_norm = normalize_for_comparison(csv_text)
            ann_norm = normalize_for_comparison(ann_text)
            
            # Check if ANN entry is contained within CSV entry
            if ann_norm and csv_norm and ann_norm in csv_norm and ann_norm != csv_norm:
                matched_ann_texts.append(ann_text)
                detailed_matches['containment_matches'].append((csv_text, ann_text))
        
        # If we found matches, mark the CSV item and all matched ANN items
        if matched_ann_texts:
            matched_csv.add(csv_text)
            for ann_text in matched_ann_texts:
                matched_ann.add(ann_text)
                remaining_ann_after_equivalence.discard(ann_text)  # Use discard to avoid KeyError
    
    # Fourth pass: Handle ANN-only items that should be treated as TP
    remaining_ann_after_equivalence = ann_orig - matched_ann
    for ann_text in remaining_ann_after_equivalence.copy():
        if ann_text in ann_only_as_tp:
            matched_ann.add(ann_text)
            detailed_matches['ann_only_as_tp'].add(ann_text)
    
    # Calculate final counts
    base_tp = len(matched_csv)  # Regular TP from CSV-ANN matches
    special_tp = len(detailed_matches['ann_only_as_tp'])  # Special TP from ANN-only
    total_tp = base_tp + special_tp
    
    fp = len(csv_orig - matched_csv)  # Only in CSV
    fn = len(ann_orig - matched_ann)  # Only in ANN (after special case handling)
    
    # Store remaining unmatched items
    detailed_matches['csv_only'] = csv_orig - matched_csv
    detailed_matches['ann_only'] = ann_orig - matched_ann
    
    return total_tp, fp, fn, detailed_matches

def compare_sets(csv_set, ann_set):
    """
    Legacy compare_sets function - now calls the enhanced version
    
    Returns:
        tuple: (TP, FP, FN) counts
    """
    tp, fp, fn, _ = compare_sets_with_special_cases(csv_set, ann_set)
    return tp, fp, fn

def evaluate_row(row, ann_entities):
    """
    Step 2: Evaluate a single row against corresponding .ann file
    
    Returns:
        dict: Results for each field with TP/FP/FN counts
    """
    # Mapping from CSV columns to ANN entity types
    column_mapping = {
        'REACTION_PRODUCT': 'REACTION_PRODUCT',
        'STARTING_MATERIAL': 'STARTING_MATERIAL', 
        'REAGENT_CATALYST': 'REAGENT_CATALYST',
        'SOLVENT': 'SOLVENT',
        'OTHER_COMPOUND': 'OTHER_COMPOUND',
        'EXAMPLE_LABEL': 'EXAMPLE_LABEL',
        'TEMPERATURE': 'TEMPERATURE',
        'TIME': 'TIME',
        'YIELD_PERCENT': 'YIELD_PERCENT',
        'YIELD_OTHER': 'YIELD_OTHER'
    }
    
    results = {}
    
    # Special handling for water/aqueous cross-field matching
    # Only check in chemical-relevant fields: STARTING_MATERIAL, REAGENT_CATALYST, SOLVENT, OTHER_COMPOUND
    csv_water_terms = set()
    csv_starting_material_set = split_csv_entries(row.get('STARTING_MATERIAL', ''))
    csv_solvent_set = split_csv_entries(row.get('SOLVENT', ''))
    csv_other_compound_set = split_csv_entries(row.get('OTHER_COMPOUND', ''))
    csv_reagent_catalyst_set = split_csv_entries(row.get('REAGENT_CATALYST', ''))
    
    # Define comprehensive list of water-related terms
    water_equivalents = ['water', 'aqueous', 'h2o', 'h₂o', 'dihydrogen monoxide']
    
    # Find water terms in CSV (only in relevant chemical fields)
    for term in csv_starting_material_set | csv_solvent_set | csv_other_compound_set | csv_reagent_catalyst_set:
        normalized_term = normalize_for_comparison(term)
        if normalized_term in water_equivalents:
            csv_water_terms.add(term)
    
    # Collect all water-related terms from ANN by field
    ann_water_by_field = {}
    ann_starting_material_set = ann_entities.get('STARTING_MATERIAL', set())
    ann_solvent_set = ann_entities.get('SOLVENT', set())
    ann_other_compound_set = ann_entities.get('OTHER_COMPOUND', set())
    ann_reagent_catalyst_set = ann_entities.get('REAGENT_CATALYST', set())
    
    # Find water terms in each ANN field separately
    for field_name, ann_set in [('STARTING_MATERIAL', ann_starting_material_set), ('SOLVENT', ann_solvent_set), 
                                ('OTHER_COMPOUND', ann_other_compound_set), ('REAGENT_CATALYST', ann_reagent_catalyst_set)]:
        ann_water_by_field[field_name] = set()
        for term in ann_set:
            normalized_term = normalize_for_comparison(term)
            if normalized_term in water_equivalents:
                ann_water_by_field[field_name].add(term)
    
    # Count total ANN water terms across all fields
    total_ann_water = sum(len(waters) for waters in ann_water_by_field.values())
    
    # Check if cross-field water matching should be applied
    has_cross_field_water_match = csv_water_terms and total_ann_water > 0
    
    # Debug for row_index 1
    if row.get('Index', 0) == 1:
        print(f"Debug row_index 1:")
        print(f"  csv_water_terms: {csv_water_terms}")
        print(f"  ann_water_by_field: {ann_water_by_field}")
        print(f"  total_ann_water: {total_ann_water}")
        print(f"  has_cross_field_water_match: {has_cross_field_water_match}")
    
    # Count water terms in each relevant field for proper handling
    water_field_info = {}
    for csv_col, ann_type in [('STARTING_MATERIAL', 'STARTING_MATERIAL'), ('SOLVENT', 'SOLVENT'), ('OTHER_COMPOUND', 'OTHER_COMPOUND'), ('REAGENT_CATALYST', 'REAGENT_CATALYST')]:
        if csv_col in row:
            csv_set = split_csv_entries(row[csv_col])
            ann_set = ann_entities.get(ann_type, set())
            
            csv_water_count = len([term for term in csv_set if normalize_for_comparison(term) in water_equivalents])
            ann_water_count = len(ann_water_by_field.get(ann_type, set()))
            
            water_field_info[csv_col] = {
                'csv_water': csv_water_count,
                'ann_water': ann_water_count,
                'csv_set': csv_set,
                'ann_set': ann_set
            }
    
    
    
    for csv_col, ann_type in column_mapping.items():
        if csv_col in row:
            # Get sets from both sources
            csv_set = split_csv_entries(row[csv_col])
            ann_set = ann_entities.get(ann_type, set())
            
            # Apply special water cross-field matching
            if csv_col in ['STARTING_MATERIAL', 'SOLVENT', 'OTHER_COMPOUND', 'REAGENT_CATALYST'] and has_cross_field_water_match:
                # Remove water terms from both sets for normal matching
                csv_set_no_water = {term for term in csv_set 
                                   if normalize_for_comparison(term) not in water_equivalents}
                ann_set_no_water = {term for term in ann_set 
                                   if normalize_for_comparison(term) not in water_equivalents}
                
                # Count water terms in current field
                csv_water_in_field = len([term for term in csv_set 
                                        if normalize_for_comparison(term) in water_equivalents])
                ann_water_in_field = len(ann_water_by_field.get(ann_type, set()))
                
                # Calculate TP, FP, FN for non-water terms
                tp_no_water, fp_no_water, fn_no_water = compare_sets(csv_set_no_water, ann_set_no_water)
                
                # For cross-field water matching:
                # - CSV water terms are ignored (not counted as FP)
                # - ANN water terms in ANY field are counted as TP
                # - Only count each ANN water term once across all fields
                
                # Calculate total available cross-field matches
                total_csv_water = len(csv_water_terms)
                max_cross_field_matches = min(total_csv_water, total_ann_water)
                
                # Debug for row 1
                if row.get('Index', 0) == 1:
                    print(f"  Processing {csv_col}:")
                    print(f"    csv_water_in_field: {csv_water_in_field}")
                    print(f"    ann_water_in_field: {ann_water_in_field}")
                    print(f"    total_csv_water: {total_csv_water}")
                    print(f"    total_ann_water: {total_ann_water}")
                    print(f"    max_cross_field_matches: {max_cross_field_matches}")
                
                # Each field with ANN water terms gets TP for those terms
                # CSV water is always ignored (no FP)
                if ann_water_in_field > 0:
                    # Add TP for each ANN water term in this field
                    water_tp = ann_water_in_field
                    tp = tp_no_water + water_tp
                    fp = fp_no_water  # CSV water ignored, no FP
                    fn = fn_no_water  # ANN water matched cross-field, no FN
                    
                    if row.get('Index', 0) == 1:
                        print(f"    {csv_col} gets water_tp: {water_tp} for ann_water_in_field")
                        
                else:
                    # Fields without ANN water proceed normally
                    tp = tp_no_water
                    fp = fp_no_water  # CSV water still ignored if cross-field matching active
                    fn = fn_no_water
                    
                    if row.get('Index', 0) == 1:
                        print(f"    {csv_col} has no ANN water, csv water ignored")
                        
                # For detailed tracking, we need to handle water cross-field matching specially
                if ann_water_in_field > 0:
                    # For fields with ANN water: CSV water ignored, ANN water counted as matched (TP)
                    effective_csv_set = csv_set_no_water | ann_water_by_field.get(ann_type, set())  # Add ANN water to CSV for matching
                    effective_ann_set = ann_set  # Keep original ANN set
                else:
                    # For fields without ANN water: CSV water ignored
                    effective_csv_set = csv_set_no_water  # CSV water ignored
                    effective_ann_set = ann_set  # Keep original ANN set
                
            else:
                # Normal matching for other fields or when no cross-field water matching
                tp, fp, fn = compare_sets(csv_set, ann_set)
                effective_csv_set = csv_set
                effective_ann_set = ann_set
            
            results[csv_col] = {
                'csv_set': effective_csv_set,  # Use effective set for detailed tracking
                'ann_set': effective_ann_set,  # Use effective set for detailed tracking
                'original_csv_set': csv_set,   # Keep original for reference
                'original_ann_set': ann_set,   # Keep original for reference
                'tp': tp,
                'fp': fp,
                'fn': fn
            }
    
    return results

def save_results_to_csv(total_results, output_file="evaluation_results_summary.csv"):
    """
    Save evaluation results to CSV file for easy analysis
    
    Args:
        total_results: Dictionary with total counts per field
        output_file: Output CSV file path
    """
    
    # Prepare data for CSV
    csv_data = []
    
    # Calculate overall totals
    total_tp = sum(counts['tp'] for counts in total_results.values())
    total_fp = sum(counts['fp'] for counts in total_results.values())
    total_fn = sum(counts['fn'] for counts in total_results.values())
    
    overall_precision = total_tp / (total_tp + total_fp) if (total_tp + total_fp) > 0 else 0
    overall_recall = total_tp / (total_tp + total_fn) if (total_tp + total_fn) > 0 else 0
    overall_f1 = 2 * overall_precision * overall_recall / (overall_precision + overall_recall) if (overall_precision + overall_recall) > 0 else 0
    
    # Add individual field results
    for field, counts in sorted(total_results.items()):
        tp, fp, fn = counts['tp'], counts['fp'], counts['fn']
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0
        f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0
        
        csv_data.append({
            'Field': field,
            'TP': tp,
            'FP': fp,
            'FN': fn,
            'Precision': round(precision, 4),
            'Recall': round(recall, 4),
            'F1_Score': round(f1, 4),
            'Support': tp + fn,  # Total ground truth items
            'Predicted': tp + fp   # Total predicted items
        })
    
    # Add overall summary row
    csv_data.append({
        'Field': 'OVERALL',
        'TP': total_tp,
        'FP': total_fp,
        'FN': total_fn,
        'Precision': round(overall_precision, 4),
        'Recall': round(overall_recall, 4),
        'F1_Score': round(overall_f1, 4),
        'Support': total_tp + total_fn,
        'Predicted': total_tp + total_fp
    })
    
    # Write to CSV
    import pandas as pd
    df_results = pd.DataFrame(csv_data)
    df_results.to_csv(output_file, index=False)
    
    print(f"Results saved to CSV: {output_file}")
    return output_file

def save_comparison_csv(output_file="evaluation_comparison.csv"):
    """
    Save comparison of all evaluation versions to CSV
    """
    
    comparison_data = []
    
    # Load all result files
    result_files = {
        'Basic': 'evaluation_results.json',
        'Case_Insensitive': 'evaluation_results_case_insensitive.json', 
        'Time_Normalized': 'evaluation_results_time_normalized.json',
        'Containment': 'evaluation_results_containment.json'
    }
    
    all_results = {}
    for version, filename in result_files.items():
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                all_results[version] = json.load(f)
        except FileNotFoundError:
            print(f"Warning: {filename} not found, skipping {version}")
    
    if not all_results:
        print("No result files found for comparison")
        return
    
    # Get all fields from the latest results
    latest_results = list(all_results.values())[-1]
    fields = list(latest_results['summary'].keys()) + ['OVERALL']
    
    # Create comparison data
    for field in fields:
        row_data = {'Field': field}
        
        for version, results in all_results.items():
            if field == 'OVERALL':
                f1_score = results['overall']['overall_f1']
                precision = results['overall']['overall_precision']
                recall = results['overall']['overall_recall']
            else:
                if field in results['summary']:
                    f1_score = results['summary'][field]['f1']
                    precision = results['summary'][field]['precision']
                    recall = results['summary'][field]['recall']
                else:
                    f1_score = precision = recall = 0
            
            row_data[f'{version}_F1'] = round(f1_score, 4)
            row_data[f'{version}_Precision'] = round(precision, 4)
            row_data[f'{version}_Recall'] = round(recall, 4)
        
        # Calculate improvements
        if len(all_results) >= 2:
            versions = list(all_results.keys())
            first_f1 = row_data[f'{versions[0]}_F1'] if f'{versions[0]}_F1' in row_data else 0
            last_f1 = row_data[f'{versions[-1]}_F1'] if f'{versions[-1]}_F1' in row_data else 0
            row_data['Total_Improvement'] = round(last_f1 - first_f1, 4)
        
        comparison_data.append(row_data)
    
    # Save comparison CSV
    df_comparison = pd.DataFrame(comparison_data)
    df_comparison.to_csv(output_file, index=False)
    
    print(f"Comparison results saved to CSV: {output_file}")
    return output_file

def save_detailed_results(total_results, detailed_mismatches, all_entries, output_file="evaluation_results.json"):
    """
    Step 3: Save final TP/FP/FN totals and detailed mismatch information
    Also generate two CSV files: all entries classification and error details
    
    Args:
        total_results: Dictionary with total counts per field
        detailed_mismatches: List of all FP/FN entries with locations
        all_entries: List of all entries with their classifications
        output_file: Output file path
    """
    
    results_summary = {
        "summary": {},
        "detailed_mismatches": detailed_mismatches,
        "timestamp": pd.Timestamp.now().isoformat()
    }
    
    # Calculate summary statistics
    total_tp = total_fp = total_fn = 0
    
    for field, counts in total_results.items():
        tp, fp, fn = counts['tp'], counts['fp'], counts['fn']
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0
        f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0
        
        results_summary["summary"][field] = {
            "tp": tp,
            "fp": fp, 
            "fn": fn,
            "precision": round(precision, 3),
            "recall": round(recall, 3),
            "f1": round(f1, 3)
        }
        
        total_tp += tp
        total_fp += fp
        total_fn += fn
    
    # Add overall totals
    overall_precision = total_tp / (total_tp + total_fp) if (total_tp + total_fp) > 0 else 0
    overall_recall = total_tp / (total_tp + total_fn) if (total_tp + total_fn) > 0 else 0
    overall_f1 = 2 * overall_precision * overall_recall / (overall_precision + overall_recall) if (overall_precision + overall_recall) > 0 else 0
    
    results_summary["overall"] = {
        "total_tp": total_tp,
        "total_fp": total_fp,
        "total_fn": total_fn,
        "overall_precision": round(overall_precision, 3),
        "overall_recall": round(overall_recall, 3),
        "overall_f1": round(overall_f1, 3)
    }
    
    # Save to JSON file
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results_summary, f, indent=2, ensure_ascii=False)
    
    print(f"\nResults saved to {output_file}")
    
    # Generate additional CSV files
    base_name = output_file.rsplit('.', 1)[0]  # Remove .json extension
    
    # 1. Save all entries classification CSV
    all_entries_csv_file = f"{base_name}_all_entries.csv"
    save_all_entries_csv(all_entries, all_entries_csv_file)
    
    # 2. Save error details CSV
    error_csv_file = f"{base_name}_errors.csv"
    save_error_details_csv(detailed_mismatches, error_csv_file)
    
    print(f"All entries classification saved to {all_entries_csv_file}")
    print(f"Error details saved to {error_csv_file}")
    
    return results_summary

def save_all_entries_csv(all_entries, output_file="evaluation_all_entries.csv"):
    """
    Save all entries with their classifications to CSV file
    
    Args:
        all_entries: List of all entries with classification information
        output_file: Output CSV file path
    """
    
    if all_entries:
        df_all = pd.DataFrame(all_entries)
        # Sort by row_index and field for better readability
        df_all = df_all.sort_values(['row_index', 'field', 'entry'])
        df_all.to_csv(output_file, index=False)
        print(f"All entries saved to CSV: {output_file} ({len(all_entries)} entries)")
    else:
        print("No entries found - all entries CSV not generated")
    
    return output_file

def save_error_details_csv(detailed_mismatches, output_file="evaluation_errors.csv"):
    """
    Save detailed mismatch information to CSV file
    
    Args:
        detailed_mismatches: List of all FP/FN entries with locations
        output_file: Output CSV file path
    """
    
    # Convert detailed mismatches to CSV format
    csv_data = []
    
    for mismatch in detailed_mismatches:
        # Convert sets to comma-separated strings for CSV
        csv_set_str = ', '.join(sorted(mismatch.get('csv_set', [])))
        ann_set_str = ', '.join(sorted(mismatch.get('ann_set', [])))
        
        csv_data.append({
            'type': mismatch['type'],
            'field': mismatch['field'],
            'entry': mismatch['entry'],
            'row_index': mismatch['row_index'],
            'csv_set': csv_set_str,
            'ann_set': ann_set_str,
            'corrected_label': ''  # Empty column for manual correction
        })
    
    # Save to CSV
    if csv_data:
        df_errors = pd.DataFrame(csv_data)
        df_errors.to_csv(output_file, index=False)
        print(f"Error details saved to CSV: {output_file}")
    else:
        print("No errors found - error CSV not generated")
    
    return output_file

def display_mismatch_analysis(detailed_mismatches):
    """
    Display detailed analysis of FP and FN entries with their locations
    """
    print("\n" + "="*80)
    print("DETAILED MISMATCH ANALYSIS")
    print("="*80)
    
    # Group mismatches by type
    fp_entries = defaultdict(list)
    fn_entries = defaultdict(list)
    
    for mismatch in detailed_mismatches:
        field = mismatch['field']
        if mismatch['type'] == 'FP':
            fp_entries[field].append(mismatch)
        elif mismatch['type'] == 'FN':
            fn_entries[field].append(mismatch)
    
    # Display FP entries
    if any(fp_entries.values()):
        print("\n🔴 FALSE POSITIVES (FP) - Items only in CSV output:")
        print("-" * 60)
        
        for field, entries in fp_entries.items():
            if entries:
                print(f"\n📋 {field} ({len(entries)} FP entries):")
                for entry in entries:
                    print(f"  • Row {entry['row_index']:04d}: '{entry['entry']}'")
                    print(f"    CSV: {entry['csv_set']}")
                    print(f"    ANN: {entry['ann_set']}")
                    print()
    
    # Display FN entries  
    if any(fn_entries.values()):
        print("\n🔵 FALSE NEGATIVES (FN) - Items only in ANN ground truth:")
        print("-" * 60)
        
        for field, entries in fn_entries.items():
            if entries:
                print(f"\n📋 {field} ({len(entries)} FN entries):")
                for entry in entries:
                    print(f"  • Row {entry['row_index']:04d}: '{entry['entry']}'")
                    print(f"    CSV: {entry['csv_set']}")
                    print(f"    ANN: {entry['ann_set']}")
                    print()
    
    # Summary statistics
    total_fp = sum(len(entries) for entries in fp_entries.values())
    total_fn = sum(len(entries) for entries in fn_entries.values())
    
    print(f"\n📊 MISMATCH SUMMARY:")
    print(f"  Total False Positives: {total_fp}")
    print(f"  Total False Negatives: {total_fn}")
    print(f"  Total Mismatches: {total_fp + total_fn}")

def main():
    """Main function to run the evaluation"""
    file_path = "output_table.csv"
    
    # Step 1: Read the CSV file
    df = read_output_table(file_path)
    
    if df is None:
        print("Step 1 failed!")
        return
    
    print("\nStep 1 completed successfully!")
    
    # Step 2: Compare each row with corresponding .ann file
    print("\nStarting Step 2: Comparing with .ann files...")
    
    # Full dataset processing with containment matching (ANN ⊆ CSV → TP)
    total_results = defaultdict(lambda: {'tp': 0, 'fp': 0, 'fn': 0})
    detailed_mismatches = []
    all_entries = []  # Track all entries for comprehensive CSV
    processed_rows = 0
    
    for idx, row in df.iterrows():
        # Format index with leading zeros (e.g., "0000", "0001", etc.)
        ann_file = f"./train/{row['Index']:04d}.ann"
        
        if os.path.exists(ann_file):
            # Read the corresponding .ann file
            ann_entities = read_ann_file(ann_file)
            
            # Evaluate this row
            row_results = evaluate_row(row, ann_entities)
            
            # Accumulate results
            for field, field_results in row_results.items():
                total_results[field]['tp'] += field_results['tp']
                total_results[field]['fp'] += field_results['fp'] 
                total_results[field]['fn'] += field_results['fn']
                
                # Collect detailed mismatch information
                _, _, _, detailed_matches = compare_sets_with_special_cases(
                    field_results['csv_set'], 
                    field_results['ann_set']
                )
                
                # Track all entries with their classifications
                # TP entries from exact matches
                for csv_entry, ann_entry in detailed_matches.get('exact_matches', []):
                    all_entries.append({
                        'row_index': row['Index'],
                        'field': field,
                        'entry': csv_entry,
                        'classification': 'TP',
                        'match_type': 'exact',
                        'matched_with': ann_entry,
                        'csv_set_size': len(field_results['csv_set']),
                        'ann_set_size': len(field_results['ann_set'])
                    })
                
                # TP entries from containment matches
                for csv_entry, ann_entry in detailed_matches.get('containment_matches', []):
                    all_entries.append({
                        'row_index': row['Index'],
                        'field': field,
                        'entry': csv_entry,
                        'classification': 'TP',
                        'match_type': 'containment',
                        'matched_with': ann_entry,
                        'csv_set_size': len(field_results['csv_set']),
                        'ann_set_size': len(field_results['ann_set'])
                    })
                
                # TP entries from special case matches
                for csv_entry, ann_entry in detailed_matches.get('special_case_matches', []):
                    all_entries.append({
                        'row_index': row['Index'],
                        'field': field,
                        'entry': csv_entry,
                        'classification': 'TP',
                        'match_type': 'special_case',
                        'matched_with': ann_entry,
                        'csv_set_size': len(field_results['csv_set']),
                        'ann_set_size': len(field_results['ann_set'])
                    })
                
                # TP entries from ann-only special cases
                for ann_entry in detailed_matches.get('ann_only_as_tp', set()):
                    all_entries.append({
                        'row_index': row['Index'],
                        'field': field,
                        'entry': ann_entry,
                        'classification': 'TP',
                        'match_type': 'ann_only_special',
                        'matched_with': '',
                        'csv_set_size': len(field_results['csv_set']),
                        'ann_set_size': len(field_results['ann_set'])
                    })
                
                # FP entries (CSV only)
                for fp_entry in detailed_matches.get('csv_only', set()):
                    all_entries.append({
                        'row_index': row['Index'],
                        'field': field,
                        'entry': fp_entry,
                        'classification': 'FP',
                        'match_type': 'no_match',
                        'matched_with': '',
                        'csv_set_size': len(field_results['csv_set']),
                        'ann_set_size': len(field_results['ann_set'])
                    })
                    # Also add to detailed mismatches
                    detailed_mismatches.append({
                        'type': 'FP',
                        'field': field,
                        'entry': fp_entry,
                        'row_index': row['Index'],
                        'csv_set': list(field_results['csv_set']),  # Convert set to list for JSON
                        'ann_set': list(field_results['ann_set'])   # Convert set to list for JSON
                    })
                
                # FN entries (ANN only)
                for fn_entry in detailed_matches.get('ann_only', set()):
                    all_entries.append({
                        'row_index': row['Index'],
                        'field': field,
                        'entry': fn_entry,
                        'classification': 'FN',
                        'match_type': 'no_match',
                        'matched_with': '',
                        'csv_set_size': len(field_results['csv_set']),
                        'ann_set_size': len(field_results['ann_set'])
                    })
                    # Also add to detailed mismatches
                    detailed_mismatches.append({
                        'type': 'FN',
                        'field': field,
                        'entry': fn_entry,
                        'row_index': row['Index'],
                        'csv_set': list(field_results['csv_set']),  # Convert set to list for JSON
                        'ann_set': list(field_results['ann_set'])   # Convert set to list for JSON
                    })
            
            processed_rows += 1
            
            # Print progress every 10 rows
            if processed_rows % 10 == 0:
                print(f"  Processed {processed_rows}/{len(df)} rows...")
        else:
            print(f"Warning: Ann file {ann_file} not found for row {idx}")
    
    print(f"\nStep 2 completed! Processed {processed_rows} rows.")
    
    # Step 3: Save results and display detailed analysis
    print("\nStarting Step 3: Saving results and analyzing mismatches...")
    
    # Save detailed results
    results_summary = save_detailed_results(total_results, detailed_mismatches, all_entries, "evaluation_results_containment.json")
    
    # Save results to CSV files
    print("\n📄 Saving results to CSV files...")
    save_results_to_csv(total_results, "evaluation_results_final.csv")
    save_comparison_csv("evaluation_comparison_all_versions.csv")
    
    # Display summary results
    print("\n" + "="*60)
    print("CONTAINMENT MATCHING EVALUATION RESULTS")
    print("="*60)
    
    for field, counts in total_results.items():
        tp, fp, fn = counts['tp'], counts['fp'], counts['fn']
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0
        f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0
        
        print(f"\n📊 {field}:")
        print(f"  TP={tp}, FP={fp}, FN={fn}")
        print(f"  Precision={precision:.3f}, Recall={recall:.3f}, F1={f1:.3f}")
    
    # Display overall statistics
    overall = results_summary["overall"]
    print(f"\n🎯 OVERALL RESULTS (WITH CONTAINMENT MATCHING):")
    print(f"  Total TP={overall['total_tp']}, FP={overall['total_fp']}, FN={overall['total_fn']}")
    print(f"  Overall Precision={overall['overall_precision']:.3f}")
    print(f"  Overall Recall={overall['overall_recall']:.3f}")
    print(f"  Overall F1={overall['overall_f1']:.3f}")
    
    # Compare with previous TIME-normalized results
    try:
        with open('evaluation_results_time_normalized.json', 'r', encoding='utf-8') as f:
            time_normalized_results = json.load(f)
            
        print(f"\n📊 IMPROVEMENT OVER TIME-NORMALIZED RESULTS:")
        print(f"{'Field':<20} {'Time-Normalized F1':<20} {'Containment F1':<20} {'Improvement':<12}")
        print("-" * 75)
        
        time_normalized_f1 = time_normalized_results["overall"]["overall_f1"]
        containment_f1 = overall["overall_f1"]
        
        for field in results_summary["summary"]:
            time_f1 = time_normalized_results["summary"][field]["f1"]
            cont_f1 = results_summary["summary"][field]["f1"]
            improvement = cont_f1 - time_f1
            
            print(f"{field:<20} {time_f1:<20.3f} {cont_f1:<20.3f} {improvement:+.3f}")
        
        print("-" * 75)
        overall_improvement = containment_f1 - time_normalized_f1
        print(f"{'OVERALL':<20} {time_normalized_f1:<20.3f} {containment_f1:<20.3f} {overall_improvement:+.3f}")
        
        # Show statistics about containment matches
        containment_count = 0
        for mismatch in detailed_mismatches:
            if 'containment' in str(mismatch):  # This is a rough estimate
                containment_count += 1
                
        print(f"\n📦 CONTAINMENT MATCHING STATISTICS:")
        print(f"  Containment matches found and applied")
        print(f"  Examples: 'Step 3' ⊃ '3', compound names ⊃ abbreviations")
        
    except FileNotFoundError:
        print("Time-normalized results not found for comparison.")
    
    print(f"\n✅ Containment matching evaluation completed!")
    print(f"Full results saved to evaluation_results_containment.json")

if __name__ == "__main__":
    main()
