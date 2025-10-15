# -*- coding: UTF-8 -*-
# the first step for the data collection
from zhipuai import ZhipuAI
import os
import time
import json
import pandas as pd
import glob

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

def get_names(text, api_key):
    '''
    get information from reaction procedures.
    Input: title and procedure string.
    Output: a string containing a table of information.
    '''
    
    
    # Original prompt (commented out for reference)
    # prompt = f"""
    # You will be given a reaction title and a synthesis procedure. Please summarize the following details in a table: Reaction product, Starting material, Reagent catalyst, Solvent, Other compound, Example label, Temperature, Time, Yield percent and Yield other. If any information is not provided or you are unsure, use "N/A" in the cell.   

    # If multiple reactions are provided, use multiple rows to represent them. If multiple units or components are provided for the same factor, include them in the same cell and separate by comma.
    # If multiple Reactants, Reactant amounts, Products, Product amounts, reaction temperature, reaction time are present, separate them using a comma in the same cell.
    # Output table should have 10 columns: | REACTION_PRODUCT | STARTING_MATERIAL | REAGENT_CATALYST | SOLVENT | OTHER_COMPOUND | EXAMPLE_LABEL | TEMPERATURE | TIME | YIELD_PERCENT | YIELD_OTHER |

    # Yield percents are final product yield provided in %.
    # Yield others are Yields provided in g, mg, mol, mmol.
    # There may be post-processing steps for the reactions mentioned in the text. The relevant reagents used should also be categorized under OTHER_COMPOUND.
    # Starting material is a substance that providing carbon atoms to products (N-hydroxy succinimide etc.). In organic reactions compounds providing non carbon atoms to a product(acetic acid etc.) are considered REAGENT_CATALYST.
    # EXAMPLE_LABEL only retains the corresponding numerical part. For example, the extracted result for "Step 2" should be "2".
    # In case a reaction was carried out at more than one temperature, the given lowest and the given highest temperature must be annotated.
    # Solvent should only include the solvents of the reaction process, and should not include the solvents added in the washing, recrystallization and other processes.
    # OTHER_COMPOUND refers to substances other than REACTION_PRODUCT, STARTING_MATERIAL, REAGENT_CATALYST and SOLVENT. In addition to the reaction stage, the substances in other stages should also be included here.
    # The temperature range can be given with (1) numerical values or (2) by a specific keyword. "on ice".
    # If different procedures with different reaction times were carried out consecutively (e.g. 30 min stirring at 20 °C, then 2 h reflux) the individual times must be annotated.

    # Optimized prompt with clearer classification rules
    prompt = f"""
    You will be given a reaction title and a synthesis procedure. Please extract and categorize chemical compounds into a structured table.

    **CRITICAL CLASSIFICATION RULES:**

    0. **REACTION_PRODUCT**: The actual compound synthesized and obtained at the END of the reaction procedure. Look for phrases like "to obtain", "to give", "was obtained", "afforded", or "yield" followed by the product name. When the final product is described as "title compound", "the compound of Example X", or similar references, then use the title compound from the beginning. Do NOT use title compounds that appear at the beginning unless they are explicitly referenced as the final product obtained.

    1. **STARTING_MATERIAL**: Compounds whose atoms/groups are incorporated into the final product structure. This includes:
       - Main reactants providing the primary molecular framework  
       - Protecting reagents whose groups become part of the product (e.g., silyl chlorides → silyl ethers, acyl chlorides → esters)
       - Coupling partners providing structural fragments (e.g., Grignard reagents, boronic acids, organometallic reagents)
       - Sulfonyl chlorides, acid chlorides, and similar reagents that contribute their functional groups to the product
       - Any reagent that contributes atoms/groups that remain in the final product structure
       - Key question: "Do atoms from this compound appear in the final product structure?"
       - Examples: piperidine-1-sulfonyl chloride → piperidine-1-sulfonyl group in product
    
    2. **REAGENT_CATALYST**: Compounds that facilitate the reaction but do NOT contribute atoms/groups to the final product structure. This includes:
       - Catalysts (e.g., palladium complexes, acids, bases)
       - Activating agents (e.g., imidazole, triethylamine, LDA, NaH - these activate but don't incorporate)
       - Coupling reagents that facilitate bond formation (e.g., CDI, TBAF, DCC, EDCI)
       - Oxidizing/reducing agents (e.g., NaBH4, LiAlH4)
       - Compounds that enable reactions but are not incorporated into products
       - Key distinction: If the reagent's atoms appear in the final product → STARTING_MATERIAL, if not → REAGENT_CATALYST

    3. **SOLVENT**: Substances used as reaction medium during the main reaction (not workup solvents). Include water when used as co-solvent in reactions (e.g., "dioxane and water", "THF/water mixture")
    
    4. **OTHER_COMPOUND**: ALL specific chemical compounds used in post-processing/workup steps including:
       - Extraction solvents (EtOAc, dichloromethane, chloroform, etc.)
       - Washing agents (water, aqueous solutions, brine, sodium chloride solution, etc.)
       - Water in all forms: "water", "aqueous", "H2O", "saturated aqueous solution", "aqueous layer"
       - Chromatography materials AND eluents (silica gel, heptane, hexane, ethyl acetate, methanol, etc.)
       - Crystallization solvents (when specifically named)
       - Drying agents (Na2SO4, MgSO4, anhydrous sodium sulfate, etc.)
       - Quenching agents (water, ammonium chloride, etc.)
       - Look for key phrases: "extracted with", "washed with", "dried over", "purified by", "chromatography", "eluted with", "crystallized from"
       - CRITICAL EXCLUSIONS: Method descriptions ("flash column chromatography", "preparative HPLC", "rotary evaporator", "vacuum"), general terms ("eluents", "mobile phases"), equipment names, procedural descriptions
       - Only include explicitly named chemical compounds - NOT methods or procedures

    5. **EXAMPLE_LABEL**: Extract ONLY numbers from procedural identifiers. CRITICAL RULES:
       - ✓ Extract from: "Example X", "Step X", "Intermediate X", "Procedure X", "Part X" → extract "X"
       - ✗ DO NOT extract: Compound numbers ("Compound 123" → ignore "123"), chemical codes ("76e", "I-307", "243A"), measurements ("200 mg"), percentages ("53%"), molecular references
       - ✓ Multiple procedural labels: "Step 2" + "Example 56" → "2, 56"
       - ✗ Chemical identifiers: "obtained compound 76f" → ignore "76f", "from Example 243A" → ignore "243A" (this is a compound reference, not current procedure)
       - Only extract numbers that directly follow procedural words like Step/Example/Procedure in the CURRENT procedure description

    **Output Requirements:**
    - 10 columns: | REACTION_PRODUCT | STARTING_MATERIAL | REAGENT_CATALYST | SOLVENT | OTHER_COMPOUND | EXAMPLE_LABEL | TEMPERATURE | TIME | YIELD_PERCENT | YIELD_OTHER |
    - Use "N/A" if information is not provided
    - Separate multiple items in same cell with commas
    - REACTION_PRODUCT: Extract the final product actually obtained/synthesized at the end. Use title compound only when explicitly referenced as final product (e.g., "to give the title compound")
    - STARTING_MATERIAL: Compounds whose atoms/groups are incorporated into final product - includes protecting reagents (silyl chlorides), coupling partners (boronic acids), sulfonyl chlorides, acid chlorides - any reagent contributing structural components to the product
    - REAGENT_CATALYST: Only compounds that facilitate reactions but are NOT incorporated - catalysts, bases, activating agents that don't contribute to product structure
    - OTHER_COMPOUND: Include ONLY specific chemical compounds in workup/post-processing steps. NEVER include method descriptions ("flash column chromatography", "HPLC", "vacuum") or procedures. Only actual chemicals: solvents, washing agents, drying agents, etc.
    - EXAMPLE_LABEL: ONLY numbers following "Step", "Example", "Intermediate", "Procedure" etc. in CURRENT text. IGNORE all compound codes (76e, I-307), reference numbers (Example 243A), measurements, percentages
    - YIELD_PERCENT: final product yield in %
    - YIELD_OTHER: yields in g, mg, mol, mmol
    - TEMPERATURE: include highest and lowest temperatures used
    - TIME: include all times (separate consecutive steps with commas)

    Example 1:
    Procedure:<'''(Example 8) Synthesis of 1-(4-(dimethylamino)piperidin-1-yl)-3-(1-ethyl-1H-imidazol-2-yl)-3-hydroxypropan-1-one:
A solution of lithium diisopropylamide in tetrahydrofuran (2.0 M, 0.969 mL, 1.94 mmol) was added dropwise to a solution of 1-(4-(dimethylamino)piperidin-1-yl)ethanone (0.300 g, 1.76 mmol) in tetrahydrofuran (6.0 mL) at -78°C and the reaction liquid was stirred at the same temperature for 1 hour. A solution of 1-ethyl-1H-imidazole-2-carbaldehyde (0.262 g, 2.12 mmol) in tetrahydrofuran (2.8 mL) was added to the reaction liquid. The reaction liquid was stirred for 1 hour and then stirred at 0°C for further 1 hour. A saturated aqueous solution of ammonium chloride and an aqueous solution of potassium carbonate were sequentially added to the reaction liquid and then the reaction liquid was extracted with chloroform. The organic layer was washed with a 10% aqueous solution of sodium chloride and then dried over anhydrous sodium sulfate and filtered. The filtrate was concentrated under reduced pressure. The residue was purified by flash column chromatography (NH silica gel, chloroform/methanol) to obtain 1-(4-(dimethylamino)piperidin-1-yl)-3-(1-ethyl-1H-imidazol-2-yl)-3-hydroxypropan-1-one (0.221 g, 0.751 mmol, 43%) (hereinafter referred to as the compound of Example 8) as a colorless oil.'''>
    Answer:
    | REACTION_PRODUCT | STARTING_MATERIAL | REAGENT_CATALYST | SOLVENT | OTHER_COMPOUND | EXAMPLE_LABEL | TEMPERATURE | TIME | YIELD_PERCENT | YIELD_OTHER |
    |---|---|---|---|---|---|---|---|---|---|
    | 1-(4-(dimethylamino)piperidin-1-yl)-3-(1-ethyl-1H-imidazol-2-yl)-3-hydroxypropan-1-one | 1-(4-(dimethylamino)piperidin-1-yl)ethanone, 1-ethyl-1H-imidazole-2-carbaldehyde | lithium diisopropylamide | tetrahydrofuran | ammonium chloride, potassium carbonate, sodium chloride, anhydrous sodium sulfate, aqueous, methanol, silica gel, chloroform | 8 | -78°C, 0°C | 1 h, 1 h | 43% | 0.221 g, 0.751 mmol |
    
    Example 2:
    Procedure:<'''Example 194
3-Isobutyl-5-methyl-1-(oxetan-2-ylmethyl)-6-[(2-oxoimidazolidin-1-yl)methyl]thieno[2,3-d]pyrimidine-2,4(1H,3H)-dione (racemate)
813 mg (1.84 mmol) of the compound from Example 243A were dissolved in 40 ml of dioxane, and 461 mg (2.76 mmol) of CDI were added. The mixture was stirred at RT for 16 h. The reaction solution was then concentrated on a rotary evaporator. The residue was dissolved in 15 ml of DMSO and this solution was purified by means of preparative HPLC (Method 14). Combination of the product fractions and freeze-drying gave 383 mg (42% of theory) of the title compound'''>
    Answer:
    | REACTION_PRODUCT | STARTING_MATERIAL | REAGENT_CATALYST | SOLVENT | OTHER_COMPOUND | EXAMPLE_LABEL | TEMPERATURE | TIME | YIELD_PERCENT | YIELD_OTHER |
    |---|---|---|---|---|---|---|---|---|---|
    | 3-Isobutyl-5-methyl-1-(oxetan-2-ylmethyl)-6-[(2-oxoimidazolidin-1-yl)methyl]thieno[2,3-d]pyrimidine-2,4(1H,3H)-dione (racemate) | compound from Example 243A | CDI | dioxane | DMSO | 194 | RT | 16 h | 42% | 383 mg |

    Example 3:
    Procedure:<'''(Example 56)
Step 1
In the same manner as steps 4 and 5 of Example 53, Compound I-307 (56 mg, 0.105 mmol, 56% yield) was obtained as a yellow solid from Compound 202 (100 mg, 0.189 mmol) and Compound 208 (0.128 mL, 1.892 mmol).'''>
    Answer:
    | REACTION_PRODUCT | STARTING_MATERIAL | REAGENT_CATALYST | SOLVENT | OTHER_COMPOUND | EXAMPLE_LABEL | TEMPERATURE | TIME | YIELD_PERCENT | YIELD_OTHER |
    |---|---|---|---|---|---|---|---|---|---|
    | Compound I-307 | Compound 202, Compound 208 | N/A | N/A | N/A | 1, 56 | N/A | N/A | 56% | 0.105 mmol, 56 mg |
    
    Example 4:
    Procedure:<'''Step 5
(E)-methyl3-(4-((1R,3R/1S,3S)-6-(1-ethyl-1H-pyrazol-4-yl)-2-(2-fluoro-2-methylpropyl)-3-methyl-1,2,3,4-tetrahydrobenzofuro[2,3-c]pyridin-1-yl)-3,5-difluoroph enyl)acrylate
(E)-methyl 3-(4-((1R,3R/1S,3S)-6-bromo-2-(2-fluoro-2-methylpropyl)-3-methyl-1,2,3,4-tetrahydrobenzofuro[2,3-c]pyridin-1-yl)-3,5-difluorophenyl)acrylate 76e (200 mg, 0.373 mmol), 1-ethyl-4-(4,4,5,5-tetramethyl-1,3,2-dioxaborolan-2-yl)-1H-pyrazole 17a (166 mg, 0.746 mmol) and potassium carbonate (154 mg, 1.119 mmol) were dissolved in 6 mL of a mixture of 1,4-dioxane and water (V/V=5:1), then [1,1'-bis(diphenylphosphino)ferrocene]dichloropalladium (II) (27mg, 0.037mmol) was added. The mixture was warmed up to 85°C and was stirred for 12 hours, then the reaction was stopped. The reaction solution was cooled to room temperature and filtered. The filtrate was concentrated under reduced pressure. The residue was purified by silica gel column chromatography with elution system B to obtain the title compound (E)-methyl 3-(4-((1R,3R/1S,3S)-6-(1-ethyl-1H-pyrazol-4-yl)-2-(2-fluoro-2-methylpropyl)-3-methyl-1,2,3,4-tetrahydrobenzofuro[2,3-c]pyridin-1-yl)-3,5-difluoroph enyl)acrylate 76f (110 mg, yield 53%) as a yellow oil.'''>
    Answer:
    | REACTION_PRODUCT | STARTING_MATERIAL | REAGENT_CATALYST | SOLVENT | OTHER_COMPOUND | EXAMPLE_LABEL | TEMPERATURE | TIME | YIELD_PERCENT | YIELD_OTHER |
    |---|---|---|---|---|---|---|---|---|---|
    | (E)-methyl 3-(4-((1R,3R/1S,3S)-6-(1-ethyl-1H-pyrazol-4-yl)-2-(2-fluoro-2-methylpropyl)-3-methyl-1,2,3,4-tetrahydrobenzofuro[2,3-c]pyridin-1-yl)-3,5-difluorophenyl)acrylate | (E)-methyl 3-(4-((1R,3R/1S,3S)-6-bromo-2-(2-fluoro-2-methylpropyl)-3-methyl-1,2,3,4-tetrahydrobenzofuro[2,3-c]pyridin-1-yl)-3,5-difluorophenyl)acrylate, 1-ethyl-4-(4,4,5,5-tetramethyl-1,3,2-dioxaborolan-2-yl)-1H-pyrazole | [1,1'-bis(diphenylphosphino)ferrocene]dichloropalladium (II), potassium carbonate, silica gel | 1,4-dioxane, water | N/A | 5 | 85°C, room temperature | 12 h | 53% | 110 mg |

    Example 5:
    Procedure:<'''Step 2: 8-Chloro-1-(2,6-dichlorophenyl)-5-((2,2-dimethyl-1,3-dioxolan-4-yl)methoxy)-2-(hydroxymethyl)-1,6-naphthyridin-4(1H)-one
To a solution of 2-(((tert-butyldimethylsilyl)oxy)methyl)-8-chloro-1-(2,6-dichlorophenyl)-5-((2,2-dimethyl-1,3-dioxolan-4-yl)methoxy)-1,6-naphthyridin-4(1H)-one (2.9 g, 4.83 mmol) in THF (20 ml) was added a 1 M solution of TBAF in THF (7.25 ml, 7.25 mmol) at 0° C. The reaction was stirred at 0° C. for 1 hour. It was quenched with water and diluted in EtOAc. The aqueous layer was extracted with EtOAc. The combined organic layer was washed with brine, dried over Na2SO4, filtered, and concentrated under reduced pressure. The residue was purified by silica gel chromatography (10-100% EtOAc in heptane) to give the title compound (1.74 g, 74% yield).'''>
    Answer:
    | REACTION_PRODUCT | STARTING_MATERIAL | REAGENT_CATALYST | SOLVENT | OTHER_COMPOUND | EXAMPLE_LABEL | TEMPERATURE | TIME | YIELD_PERCENT | YIELD_OTHER |
    |---|---|---|---|---|---|---|---|---|---|
    | 8-Chloro-1-(2,6-dichlorophenyl)-5-((2,2-dimethyl-1,3-dioxolan-4-yl)methoxy)-2-(hydroxymethyl)-1,6-naphthyridin-4(1H)-one | 2-(((tert-butyldimethylsilyl)oxy)methyl)-8-chloro-1-(2,6-dichlorophenyl)-5-((2,2-dimethyl-1,3-dioxolan-4-yl)methoxy)-1,6-naphthyridin-4(1H)-one | TBAF | THF | water, EtOAc, brine, Na2SO4, silica gel, heptane | 2 | 0° C | 1 h | 74% | 1.74 g |

    Example 6:
    Procedure:<'''Intermediate 6B
5-bromo-3-(((tert-butyldimethylsilyl)oxy)methyl)-2-methoxypyridine
(5-Bromo-2-methoxypyridin-3-yl)methanol (1.876 g, 8.60 mmol), tert-butyldimethylsilyl chloride (1.556 g, 10.32 mmol), and imidazole (0.879 g, 12.91 mmol) were stirred in CH2Cl2 (35 mL) overnight at room temperature. After this time, 5 mL of CH3OH was added to quench the reaction, and the reaction mixture was stirred at room temperature for 10 minutes. The mixture was diluted with CH2Cl2 and washed twice with saturated aqueous NaHCO3 solution and once with brine. The organic solution was dried over Na2SO4, filtered, and concentrated to afford the title compound 5-bromo-3-(((tert-butyldimethylsilyl)oxy)methyl)-2-methoxypyridine (2.71 g, 95% yield).'''>
    Answer:
    | REACTION_PRODUCT | STARTING_MATERIAL | REAGENT_CATALYST | SOLVENT | OTHER_COMPOUND | EXAMPLE_LABEL | TEMPERATURE | TIME | YIELD_PERCENT | YIELD_OTHER |
    |---|---|---|---|---|---|---|---|---|---|
    | 5-bromo-3-(((tert-butyldimethylsilyl)oxy)methyl)-2-methoxypyridine | (5-Bromo-2-methoxypyridin-3-yl)methanol, tert-butyldimethylsilyl chloride | imidazole | CH2Cl2 | CH3OH, NaHCO3, brine, Na2SO4 | 6B | room temperature | overnight, 10 min | 95% | 2.71 g |

    Example 7:
    Procedure:<'''Example 29. (R)-N-methyl-N-(1-(piperidine-1-ylsulfonyl)pyrrolidine-3-yl)-7H-pyrrolo[2,3-d]pyrimidine-4-amine
70.0 mg of (R)-N-methyl-N-(pyrrolidine-3-yl)-7H-pyrrolo[2,3-d]pyrimidine-4-amine was added to a 5-mL round-bottomed flask and then dissolved with 1.00 mL of dichloromethane (CH2Cl2). After 0.0450 mL of piperidine-1-sulfonyl chloride was added thereto, the reaction mixture was treated with 0.0590 mL of N,N-diisopropylethylamine and then stirred overnight at room temperature. The reaction mixture was concentrated under reduced pressure, and then the resulting residue was purified by flash column chromatography (MeOH:CH2Cl2=2:98). The resulting fraction was concentrated under reduced pressure and then further under vacuum. As a result, 91.0 mg of (R)-N-methyl-N-(1-(piperidine-1-ylsulfonyl)pyrrolidine-3-yl)-7H-pyrrolo[2,3-d]pyrimidine-4-amine was obtained with a yield of about 77.8%.'''>
    Answer:
    | REACTION_PRODUCT | STARTING_MATERIAL | REAGENT_CATALYST | SOLVENT | OTHER_COMPOUND | EXAMPLE_LABEL | TEMPERATURE | TIME | YIELD_PERCENT | YIELD_OTHER |
    |---|---|---|---|---|---|---|---|---|---|
    | (R)-N-methyl-N-(1-(piperidine-1-ylsulfonyl)pyrrolidine-3-yl)-7H-pyrrolo[2,3-d]pyrimidine-4-amine | (R)-N-methyl-N-(pyrrolidine-3-yl)-7H-pyrrolo[2,3-d]pyrimidine-4-amine, piperidine-1-sulfonyl chloride | N,N-diisopropylethylamine | dichloromethane | MeOH, CH2Cl2 | 29 | room temperature | overnight | about 77.8% | 91.0 mg |

    /////
    Procedure:<'''{text}'''>
    """
    response = get_completion(prompt, api_key)
    print(response)
    return response

def main(api_key):
    output_df = pd.DataFrame(columns=['input_file', 'output'])
    for file in glob.glob('./test_data/*.txt'):
        with open(file, 'r') as f:
            data = f.read()
            print(f'Reading {file}')
            output = get_names(data, api_key)
            output_df = pd.concat([output_df, pd.DataFrame({'input_file': [file], 'output': [output]})])
            f.close()
    output_df.to_csv('output.csv', index=False)


if __name__ == '__main__':
    api_key = 'Your api key' # Your api key
    start = time.perf_counter()
    main(api_key)
    end = time.perf_counter()
    print('runningtime:' + str(end - start))

#     test_input = '''Step 2: (R)-tert-Butyl (2-(8-(benzyloxy)-2-oxo-1,2-dihydroquinolin-5-yl)-2-((tert-butyldimethylsilyl)oxy)ethyl)((1-benzylpiperidin-4-yl)methyl)carbamate
# A stirred solution of (R)-8-(benzyloxy)-5-(2-(((1-benzylpiperidin-4-yl)methyl)amino)-1-((tert-butyldimethylsilyl)oxy)ethyl)quinolin-2(1H)-one (2.65 g, 4.33 mmol) in DCM (25 mL) was added with a solution of di-tert-butyldicarbonate (1.13 g, 5.18 mmol) in DCM (5 mL). The reaction mixture was stirred at room temperature for 16 hours. The solvent was evaporated under reduced pressure and the residue purified by flash column chromatography (eluent-100% DCM to 30:1 DCM/7M NH3/MeOH) to afford the title compound (2.83 g, 92%).
# '''
#     get_names(test_input)


