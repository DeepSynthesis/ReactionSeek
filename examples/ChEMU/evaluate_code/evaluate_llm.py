# -*- coding: utf-8 -*-
import pandas as pd
import os
from typing import List, Dict
from pathlib import Path

# 加载项目根目录的 .env 文件
_project_root = Path(__file__).resolve().parent.parent.parent.parent
_dotenv_path = _project_root / ".env"
if _dotenv_path.exists():
    from dotenv import load_dotenv
    load_dotenv(dotenv_path=_dotenv_path)

def load_fp_data():
    """
    读取evaluation_results_containment_errors.csv文件，找到type列为FP的行，
    读取对应的text文件内容，并提取class、entity、raw_text三个变量。
    
    Returns:
        list: 包含字典的列表，每个字典包含class、entity、raw_text三个键
    """
    # 读取CSV文件
    csv_path = "evaluation_results_containment_errors.csv"
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"CSV文件不存在: {csv_path}")
    
    df = pd.read_csv(csv_path)
    
    # 筛选type列为FP的行
    fp_rows = df[df['type'] == 'FP'].copy()
    
    results = []
    
    for _, row in fp_rows.iterrows():
        # 获取field、entry和row_index
        field = row['field']
        entry = row['entry'] 
        row_index = row['row_index']
        
        # 构造对应的文本文件路径 (格式: ./dev/00xx.txt)
        text_file_path = f"./train/{row_index:04d}.txt"
        
        # 读取文本文件内容
        try:
            with open(text_file_path, 'r', encoding='utf-8') as f:
                text_content = f.read()
        except FileNotFoundError:
            print(f"警告: 文本文件不存在: {text_file_path}")
            text_content = ""
        except Exception as e:
            print(f"警告: 读取文件 {text_file_path} 时出错: {e}")
            text_content = ""
        
        # 创建结果字典
        result = {
            'class': field,      # field对应class
            'entity': entry,     # entry对应entity  
            'raw_text': text_content  # 文本文件内容对应raw_text
        }
        
        results.append(result)
    
    return results

def load_fn_data():
    """
    读取evaluation_results_containment_errors.csv文件，找到type列为FN的行，
    读取对应的text文件内容，并提取class、entity、raw_text三个变量。
    
    Returns:
        list: 包含字典的列表，每个字典包含class、entity、raw_text三个键
    """
    # 读取CSV文件
    csv_path = "evaluation_results_containment_errors.csv"
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"CSV文件不存在: {csv_path}")
    
    df = pd.read_csv(csv_path)
    
    # 筛选type列为FN的行
    fn_rows = df[df['type'] == 'FN'].copy()
    
    results = []
    
    for _, row in fn_rows.iterrows():
        # 获取field、entry和row_index
        field = row['field']
        entry = row['entry'] 
        row_index = row['row_index']
        
        # 构造对应的文本文件路径 (格式: ./dev/00xx.txt)
        text_file_path = f"./train/{row_index:04d}.txt"
        
        # 读取文本文件内容
        try:
            with open(text_file_path, 'r', encoding='utf-8') as f:
                text_content = f.read()
        except FileNotFoundError:
            print(f"警告: 文本文件不存在: {text_file_path}")
            text_content = ""
        except Exception as e:
            print(f"警告: 读取文件 {text_file_path} 时出错: {e}")
            text_content = ""
        
        # 创建结果字典
        result = {
            'class': field,      # field对应class
            'entity': entry,     # entry对应entity  
            'raw_text': text_content  # 文本文件内容对应raw_text
        }
        
        results.append(result)
    
    return results

def load_both_data():
    """
    读取evaluation_results_containment_errors.csv文件，找到type列为FP和FN的行，
    读取对应的text文件内容，并提取class、entity、raw_text三个变量。
    
    Returns:
        dict: 包含'FP'和'FN'两个键，值为对应的数据列表
    """
    # 读取CSV文件
    csv_path = "evaluation_results_containment_errors.csv"
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"CSV文件不存在: {csv_path}")
    
    df = pd.read_csv(csv_path)
    
    # 筛选type列为FP和FN的行
    fp_rows = df[df['type'] == 'FP'].copy()
    fn_rows = df[df['type'] == 'FN'].copy()
    
    def process_rows(rows):
        results = []
        for _, row in rows.iterrows():
            # 获取field、entry和row_index
            field = row['field']
            entry = row['entry'] 
            row_index = row['row_index']
            
            # 构造对应的文本文件路径 (格式: ./dev/00xx.txt)
            text_file_path = f"./train/{row_index:04d}.txt"
            
            # 读取文本文件内容
            try:
                with open(text_file_path, 'r', encoding='utf-8') as f:
                    text_content = f.read()
            except FileNotFoundError:
                print(f"警告: 文本文件不存在: {text_file_path}")
                text_content = ""
            except Exception as e:
                print(f"警告: 读取文件 {text_file_path} 时出错: {e}")
                text_content = ""
            
            # 创建结果字典
            result = {
                'class': field,      # field对应class
                'entity': entry,     # entry对应entity  
                'raw_text': text_content  # 文本文件内容对应raw_text
            }
            
            results.append(result)
        
        return results
    
    return {
        'FP': process_rows(fp_rows),
        'FN': process_rows(fn_rows)
    }

# System prompts for LLM conversation
FP_SYSTEM_PROMPT = """You are a data validation model that determines whether the given data pairs comply with the following specified rules and returns the corresponding results (TP, FP).

(Note: TP means the classified entity is contained in true value, FP means the true value is not contained in raw text)
you should only output "TP" or "FP".

INPUT FORMAT:
  Class:(class)
  Classified entity: (classified entity)
  Raw Text: (raw text)

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
  Class:STARTING_MATERIAL
  Classified entity: N-hydroxy succinimide
  Raw Text: Preparation Example 7 Preparation of Compound 7
12.12 g of Compound 7 was prepared in the same manner as in Preparation Example 1, except that Compound A (10 g, 31.53 mmol) and 2-bromonaphthalene (4.15 g, 34.69 mmol) were used. (87%)
MS[M+H]+=444
Answer:TP

Example 2:
  Class:REAGENT_CATALYST
  Classified entity: di-tert-butyldicarbonate
  Raw Text: Step 2: (R)-tert-Butyl (2-(8-(benzyloxy)-2-oxo-1,2-dihydroquinolin-5-yl)-2-((tert-butyldimethylsilyl)oxy)ethyl)((1-benzylpiperidin-4-yl)methyl)carbamate
A stirred solution of (R)-8-(benzyloxy)-5-(2-(((1-benzylpiperidin-4-yl)methyl)amino)-1-((tert-butyldimethylsilyl)oxy)ethyl)quinolin-2(1H)-one (2.65 g, 4.33 mmol) in DCM (25 mL) was added with a solution of di-tert-butyldicarbonate (1.13 g, 5.18 mmol) in DCM (5 mL). The reaction mixture was stirred at room temperature for 16 hours. The solvent was evaporated under reduced pressure and the residue purified by flash column chromatography (eluent-100% DCM to 30:1 DCM/7M NH3/MeOH) to afford the title compound (2.83 g, 92%).
Answer:FP

Example 3:
  Class:EXAMPLE_LABEL
  Classified entity: 25
  Raw Text: Method 12
1,1-Dioxo-3,3-dibutyl-5-phenyl-7-methylthio-8-[N-((R)-α-{N-[1-(R)-2-(R)-1-(t-butoxycarbonyl)-1-hydroxy-prop-2-yl]carbamoyl}benzyl)carbamoylmethoxy]-2,3,4,5-tetrahydro-1,2,5-benzothiadiazepine
1,1-Dioxo-3,3-dibutyl-5-phenyl-7-methylthio-8-[N-((R)-α-carboxybenzyl) carbamoylmethoxy]-2,3,4,5-tetrahydro-1,2,5-benzothiadiazepine (Example 25; 50 mg, 0.078 mmol) and tert-butyl (2R,3R)-3-amino-2-hydroxybutanoate (15 mg, 0.086 mmol) were dissolved in DCM (2ml) and DMF (1ml) and N-methylmorpholine (17.2p1, 0.156 mmol) and TBTU (45 mg, 0.14 mmol) were added. The reaction mixture was stirred for 4 hours. The reaction mixture was put directly on an Isolute column (2g, silica). The product was eluted with a stepwise gradient using DCM:EtOAc 100:0, 95:5, 90:10 then 80:20 to give the title compound (33 mg, 53%). M/z 797.3.
Answer:FP

Example 4:
  Class:OTHER_COMPOUND
  Classified entity: C18 column
  Raw Text: c) A mixture of 4-t-butylbenzene-1-sulfonyl chloride (0.070 g, 0.30 mmol), 3-(difluoromethyl)-1-(quinolin-5-yl)-1H-pyrazol-5-amine (0.045 g, 0.17 mmol), and DMAP (0.020 g, 0.17 mmol) in pyridine (2 mL) was heated at 80° C. for 5 h with stirring. After cooling to room temperature, the reaction mixture was concentrated in vacuo. The crude residue was purified by flash chromatography (SiO2, 5% methanol in ethyl acetate), followed by reverse phase HPLC (C18 column, acetonitrile-H2O with 0.1% TFA as eluent) to give the title compound as a white solid (0.040 g, 0.085 mmol, 53%).
Answer:FP"""

FN_SYSTEM_PROMPT = """You are a data validation model that determines whether the given data pairs comply with the following specified rules and returns the corresponding results (TP, FN).

(Note: TP means the classified entity is contained in true value, FN means the absent value is contained in raw text)
you should only output "TP" or "FN".

INPUT FORMAT:
  Class:(class)
  Classified entity: (classified entity)
  Raw Text: (raw text)

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
  Class:STARTING_MATERIAL
  Classified entity: di-tert-butyldicarbonate
  Raw Text: Step 2: (R)-tert-Butyl (2-(8-(benzyloxy)-2-oxo-1,2-dihydroquinolin-5-yl)-2-((tert-butyldimethylsilyl)oxy)ethyl)((1-benzylpiperidin-4-yl)methyl)carbamate
A stirred solution of (R)-8-(benzyloxy)-5-(2-(((1-benzylpiperidin-4-yl)methyl)amino)-1-((tert-butyldimethylsilyl)oxy)ethyl)quinolin-2(1H)-one (2.65 g, 4.33 mmol) in DCM (25 mL) was added with a solution of di-tert-butyldicarbonate (1.13 g, 5.18 mmol) in DCM (5 mL). The reaction mixture was stirred at room temperature for 16 hours. The solvent was evaporated under reduced pressure and the residue purified by flash column chromatography (eluent-100% DCM to 30:1 DCM/7M NH3/MeOH) to afford the title compound (2.83 g, 92%).
Answer:FN

Example 2:
  Class:STARTING_MATERIAL
  Classified entity: N-hydroxy succinimide
  Raw Text: Synthesis of Compound 34
Compound 33 (260.1 mg, 1.0 mmol) and EDCI (210.9 mg, 1.1 mmol), N-hydroxy succinimide (126.6 mg, 1.1 mmol) was dissolved in DMF (14 mL). The solution was stirred overnight at room temperature. Upon completion of the reaction, the solvent was removed under reduced pressure. The solid residue was purified by column chromatography with CH2Cl2/MeOH (10:1) as eluent to give the product 34 as a light brown solid (273 mg, 76.4%). LC-MS m/z (ES+), 358.11 (M+H)+.
Answer:TP

Example 3:
  Class:EXAMPLE_LABEL
  Classified entity: 5
  Raw Text: Method 12
Intermediate 5: 7-Chloro-5-(4,4,5,5-tetramethyl-1,3,2-dioxaborolan-2-yl)indolin-2-one
Step A: 5-Bromo-7-chloroindolin-2-one. To a cooled (0° C.) solution of 7-chloroindolin-2-one (1.0 g, 6.0 mmol) in TFA (11 mL) was added N-bromosuccinimide (1.0 g, 6.0 mmol) portionwise, and the resulting mixture was stirred at 0° C. for 6 h. The solvent was removed in vacuo and the residue was diluted and evaporated successively with DCM (25 mL) and EtOAc (25 mL). The crude product was triturated with EtOH to provide the title compound as a white solid (861 mg, 58%).
Answer:FN

Example 4:
  Class:OTHER_COMPOUND
  Classified entity: 2-(7-bromo-2,3-dihydrobenzofuran-5-yl)ethan-1-ol
  Raw Text: (a). 2-(7-bromo-2,3-dihydrobenzofuran-5-yl)ethan-1-ol
To a solution of 2-(2,3-dihydrobenzofuran-5-yl)acetic acid (4 g, 22.4 mmol) in methanol (40 mL) was added sulfuric acid (219 mg, 2.24 mmol). The reaction mixture was heated to 70° C. and stirred at that temperature for 2 h. The mixture was concentrated and the residue was added ethyl acetate (50 mL). The solution was washed with brine, then the organic phase was dried over anhydrous sodium sulfate, filtered and concentrated in vacuo to provide methyl 2-(2,3-dihydrobenzofuran-5-yl)acetate (4.0 g, yield: 93%) as a yellow oil.
Answer:FN
"""

# Legacy system prompt (kept for backward compatibility)
SYSTEM_PROMPT = FP_SYSTEM_PROMPT

def format_prompt(class_name: str, entity: str, raw_text: str) -> str:
    """
    格式化用于LLM对话的prompt
    """
    return f"""Class:{class_name}
Classified entity: {entity}
Raw Text: {raw_text}"""

def call_llm(prompt: str, api_key: str = None, model: str = "gpt-3.5-turbo", endpoint: str = None, system_prompt: str = None) -> str:
    """
    调用LLM进行分类，统一使用OpenAI兼容模式
    
    Args:
        prompt: 格式化的输入prompt
        api_key: API密钥
        model: 使用的模型
        endpoint: API endpoint URL
        system_prompt: 系统提示词，如果未提供则使用默认的FP_SYSTEM_PROMPT
    
    Returns:
        LLM的回复
    """
    if system_prompt is None:
        system_prompt = FP_SYSTEM_PROMPT
        
    try:
        # 统一使用OpenAI兼容的API调用方式
        return call_openai_compatible_api(prompt, api_key, model, endpoint, system_prompt)
    
    except Exception as e:
        print(f"调用LLM时出错: {e}")
        return "ERROR"

def call_openai_compatible_api(prompt: str, api_key: str, model: str, endpoint: str, system_prompt: str) -> str:
    """
    调用OpenAI兼容的API
    """
    try:
        from openai import OpenAI
        
        # 创建客户端
        if endpoint:
            client = OpenAI(
                api_key=api_key,
                base_url=endpoint
            )
        else:
            client = OpenAI(api_key=api_key)
        
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            temperature=0,
        )
        # 调试：打印响应类型和内容 (已禁用)
        # print(f"  调试信息 - 响应类型: {type(response)}")
        # print(f"  调试信息 - 响应内容: {str(response)[:200]}...")
        
        # 处理不同类型的响应
        if hasattr(response, 'choices') and response.choices:
            # 标准OpenAI格式
            return response.choices[0].message.content.strip()
        elif isinstance(response, str):
            # 直接返回字符串响应
            return response.strip()
        elif isinstance(response, dict):
            # 字典格式响应
            if 'choices' in response and response['choices']:
                return response['choices'][0]['message']['content'].strip()
            elif 'content' in response:
                return response['content'].strip()
            elif 'text' in response:
                return response['text'].strip()
            elif 'message' in response:
                return response['message'].strip()
        else:
            print(f"  未知响应格式: {type(response)}")
            return "ERROR"
        
    except ImportError:
        print("错误: 需要安装openai模块来使用OpenAI兼容的API")
        return "ERROR"
    except Exception as e:
        print(f"调用OpenAI兼容API时出错: {e}")
        print(f"错误类型: {type(e)}")
        return "ERROR"

def evaluate_fp_data(api_key: str = None, model: str = "gpt-3.5-turbo", endpoint: str = None) -> pd.DataFrame:
    """
    评估FP数据，调用LLM进行分类，返回完整的DataFrame
    
    Args:
        api_key: OpenAI API密钥
        model: 使用的模型
        endpoint: API endpoint URL
    
    Returns:
        包含所有原始数据和新评估结果的DataFrame
    """
    # 读取原始CSV文件
    csv_path = "evaluation_results_containment_errors.csv"
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"CSV文件不存在: {csv_path}")
    
    df = pd.read_csv(csv_path)
    
    # 添加corrected_label列，初始化为空字符串
    df['corrected_label'] = ''
    
    # 获取FP行的索引
    fp_indices = df[df['type'] == 'FP'].index
    
    print(f"开始评估 {len(fp_indices)} 条FP记录...")
    print(f"使用模型: {model}")
    if endpoint:
        print(f"API Endpoint: {endpoint}")
    
    for idx_count, df_idx in enumerate(fp_indices):
        print(f"处理第 {idx_count+1}/{len(fp_indices)} 条记录 (索引: {df_idx})...")
        
        row = df.loc[df_idx]
        field = row['field']
        entry = row['entry']
        row_index = row['row_index']
        
        # 读取对应的文本文件
        text_file_path = f"./train/{row_index:04d}.txt"
        
        try:
            with open(text_file_path, 'r', encoding='utf-8') as f:
                text_content = f.read()
        except FileNotFoundError:
            print(f"  警告: 文本文件不存在: {text_file_path}")
            text_content = ""
        except Exception as e:
            print(f"  警告: 读取文件 {text_file_path} 时出错: {e}")
            text_content = ""
        
        # 格式化prompt并调用LLM (使用FP专用的system prompt)
        prompt = format_prompt(field, entry, text_content)
        llm_response = call_llm(prompt, api_key, model, endpoint, FP_SYSTEM_PROMPT)
        
        # 更新DataFrame中的corrected_label列
        df.loc[df_idx, 'corrected_label'] = llm_response
        
        print(f"  - Class: {field}")
        print(f"  - Entity: {entry}")
        print(f"  - LLM Response: {llm_response}")
        print()
    
    return df

def evaluate_fn_data(api_key: str = None, model: str = "gpt-3.5-turbo", endpoint: str = None) -> pd.DataFrame:
    """
    评估FN数据，调用LLM进行分类，返回完整的DataFrame
    
    Args:
        api_key: OpenAI API密钥
        model: 使用的模型
        endpoint: API endpoint URL
    
    Returns:
        包含所有原始数据和新评估结果的DataFrame
    """
    # 读取原始CSV文件
    csv_path = "evaluation_results_containment_errors.csv"
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"CSV文件不存在: {csv_path}")
    
    df = pd.read_csv(csv_path)
    
    # 添加corrected_label列，初始化为空字符串
    df['corrected_label'] = ''
    
    # 获取FN行的索引
    fn_indices = df[df['type'] == 'FN'].index
    
    print(f"开始评估 {len(fn_indices)} 条FN记录...")
    print(f"使用模型: {model}")
    if endpoint:
        print(f"API Endpoint: {endpoint}")
    
    for idx_count, df_idx in enumerate(fn_indices):
        print(f"处理第 {idx_count+1}/{len(fn_indices)} 条记录 (索引: {df_idx})...")
        
        row = df.loc[df_idx]
        field = row['field']
        entry = row['entry']
        row_index = row['row_index']
        
        # 读取对应的文本文件
        text_file_path = f"./train/{row_index:04d}.txt"
        
        try:
            with open(text_file_path, 'r', encoding='utf-8') as f:
                text_content = f.read()
        except FileNotFoundError:
            print(f"  警告: 文本文件不存在: {text_file_path}")
            text_content = ""
        except Exception as e:
            print(f"  警告: 读取文件 {text_file_path} 时出错: {e}")
            text_content = ""
        
        # 格式化prompt并调用LLM (使用FN专用的system prompt)
        prompt = format_prompt(field, entry, text_content)
        llm_response = call_llm(prompt, api_key, model, endpoint, FN_SYSTEM_PROMPT)
        
        # 更新DataFrame中的corrected_label列
        df.loc[df_idx, 'corrected_label'] = llm_response
        
        print(f"  - Class: {field}")
        print(f"  - Entity: {entry}")
        print(f"  - LLM Response: {llm_response}")
        print()
    
    return df

def evaluate_both_data(api_key: str = None, model: str = "gpt-3.5-turbo", endpoint: str = None) -> pd.DataFrame:
    """
    同时评估FP和FN数据，调用LLM进行分类，返回完整的DataFrame
    
    Args:
        api_key: OpenAI API密钥
        model: 使用的模型
        endpoint: API endpoint URL
    
    Returns:
        包含所有原始数据和新评估结果的DataFrame
    """
    # 读取原始CSV文件
    csv_path = "evaluation_results_containment_errors.csv"
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"CSV文件不存在: {csv_path}")
    
    df = pd.read_csv(csv_path)
    
    # 添加corrected_label列，初始化为空字符串
    df['corrected_label'] = ''
    
    # 获取FP和FN行的索引
    fp_indices = df[df['type'] == 'FP'].index.tolist()
    fn_indices = df[df['type'] == 'FN'].index.tolist()
    all_indices = fp_indices + fn_indices
    
    print(f"开始评估 {len(fp_indices)} 条FP记录和 {len(fn_indices)} 条FN记录，共 {len(all_indices)} 条记录...")
    print(f"使用模型: {model}")
    if endpoint:
        print(f"API Endpoint: {endpoint}")
    
    for idx_count, df_idx in enumerate(all_indices):
        row_type = df.loc[df_idx, 'type']
        print(f"处理第 {idx_count+1}/{len(all_indices)} 条记录 (索引: {df_idx}, 类型: {row_type})...")
        
        row = df.loc[df_idx]
        field = row['field']
        entry = row['entry']
        row_index = row['row_index']
        
        # 读取对应的文本文件
        text_file_path = f"./train/{row_index:04d}.txt"
        
        try:
            with open(text_file_path, 'r', encoding='utf-8') as f:
                text_content = f.read()
        except FileNotFoundError:
            print(f"  警告: 文本文件不存在: {text_file_path}")
            text_content = ""
        except Exception as e:
            print(f"  警告: 读取文件 {text_file_path} 时出错: {e}")
            text_content = ""
        
        # 格式化prompt并调用LLM (根据类型使用不同的system prompt)
        prompt = format_prompt(field, entry, text_content)
        if row_type == 'FP':
            llm_response = call_llm(prompt, api_key, model, endpoint, FP_SYSTEM_PROMPT)
        else:  # FN
            llm_response = call_llm(prompt, api_key, model, endpoint, FN_SYSTEM_PROMPT)
        
        # 更新DataFrame中的corrected_label列
        df.loc[df_idx, 'corrected_label'] = llm_response
        
        print(f"  - Type: {row_type}")
        print(f"  - Class: {field}")
        print(f"  - Entity: {entry}")
        print(f"  - LLM Response: {llm_response}")
        print()
    
    return df

def save_results(df: pd.DataFrame, output_file: str = "evaluation_results_containment_errors_FP.csv", result_type: str = "FP"):
    """
    保存评估结果到CSV文件，保持原有结构
    
    Args:
        df: 包含评估结果的DataFrame
        output_file: 输出文件名
        result_type: 结果类型，"FP", "FN" 或 "BOTH"
    """
    df.to_csv(output_file, index=False, encoding='utf-8')
    print(f"结果已保存到: {output_file}")
    
    if result_type == "BOTH":
        # 统计FP和FN的综合结果
        fp_rows = df[df['type'] == 'FP']
        fn_rows = df[df['type'] == 'FN']
        
        print(f"\n=== 综合评估结果统计 ===")
        
        # FP统计
        total_fp = len(fp_rows)
        fp_corrected_tp = len(fp_rows[fp_rows['corrected_label'] == 'TP'])
        fp_corrected_fp = len(fp_rows[fp_rows['corrected_label'] == 'FP'])
        fp_errors = len(fp_rows[fp_rows['corrected_label'] == 'ERROR'])
        fp_not_evaluated = len(fp_rows[fp_rows['corrected_label'] == ''])
        
        print(f"FP记录总数: {total_fp}")
        print(f"  LLM判定为TP: {fp_corrected_tp}")
        print(f"  LLM判定为FP: {fp_corrected_fp}")
        print(f"  评估出错: {fp_errors}")
        print(f"  未评估: {fp_not_evaluated}")
        if total_fp > 0:
            print(f"  FP->TP转换率: {fp_corrected_tp/total_fp*100:.1f}%")
        
        # FN统计
        total_fn = len(fn_rows)
        fn_corrected_tp = len(fn_rows[fn_rows['corrected_label'] == 'TP'])
        fn_corrected_fp = len(fn_rows[fn_rows['corrected_label'] == 'FP'])
        fn_errors = len(fn_rows[fn_rows['corrected_label'] == 'ERROR'])
        fn_not_evaluated = len(fn_rows[fn_rows['corrected_label'] == ''])
        
        print(f"\nFN记录总数: {total_fn}")
        print(f"  LLM判定为TP: {fn_corrected_tp}")
        print(f"  LLM判定为FP: {fn_corrected_fp}")
        print(f"  评估出错: {fn_errors}")
        print(f"  未评估: {fn_not_evaluated}")
        if total_fn > 0:
            print(f"  FN->TP转换率: {fn_corrected_tp/total_fn*100:.1f}%")
        
        # 总计
        total_records = total_fp + total_fn
        total_corrected_tp = fp_corrected_tp + fn_corrected_tp
        total_errors = fp_errors + fn_errors
        print(f"\n总记录数: {total_records}")
        print(f"总TP数: {total_corrected_tp}")
        print(f"总错误数: {total_errors}")
        if total_records > 0:
            print(f"总体TP率: {total_corrected_tp/total_records*100:.1f}%")
    
    else:
        # 原有的单类型统计逻辑
        target_rows = df[df['type'] == result_type]
        total_records = len(target_rows)
        
        if result_type == "FP":
            corrected_tp = len(target_rows[target_rows['corrected_label'] == 'TP'])
            corrected_fp = len(target_rows[target_rows['corrected_label'] == 'FP'])
            errors = len(target_rows[target_rows['corrected_label'] == 'ERROR'])
            not_evaluated = len(target_rows[target_rows['corrected_label'] == ''])
            
            print(f"\n=== 评估结果统计 ===")
            print(f"原始FP记录总数: {total_records}")
            print(f"LLM判定为TP: {corrected_tp}")
            print(f"LLM判定为FP: {corrected_fp}")
            print(f"评估出错: {errors}")
            print(f"未评估: {not_evaluated}")
            
            if total_records > 0:
                print(f"FP->TP转换率: {corrected_tp/total_records*100:.1f}%")
        
        elif result_type == "FN":
            corrected_tp = len(target_rows[target_rows['corrected_label'] == 'TP'])
            corrected_fp = len(target_rows[target_rows['corrected_label'] == 'FP'])
            errors = len(target_rows[target_rows['corrected_label'] == 'ERROR'])
            not_evaluated = len(target_rows[target_rows['corrected_label'] == ''])
            
            print(f"\n=== 评估结果统计 ===")
            print(f"原始FN记录总数: {total_records}")
            print(f"LLM判定为TP: {corrected_tp}")
            print(f"LLM判定为FP: {corrected_fp}")
            print(f"评估出错: {errors}")
            print(f"未评估: {not_evaluated}")
            
            if total_records > 0:
                print(f"FN->TP转换率: {corrected_tp/total_records*100:.1f}%")

def main():
    """
    主函数，提供多种使用方式
    """
    import argparse
    
    parser = argparse.ArgumentParser(description="评估FP/FN数据")
    parser.add_argument("--mode", choices=["preview", "evaluate"], default="preview", 
                       help="运行模式: preview(预览数据) 或 evaluate(调用LLM评估)")
    parser.add_argument("--type", choices=["FP", "FN", "BOTH"], default="BOTH",
                       help="数据类型: FP(假正例), FN(假负例) 或 BOTH(同时处理FP和FN)")
    parser.add_argument("--api-key", type=str,
                       default=os.getenv("OPENAI_API_KEY", ""),
                       help="OpenAI API密钥（默认从 .env 文件读取）")
    parser.add_argument("--model", type=str, 
                       default=os.getenv("OPENAI_MODEL", "o3"),
                       help="使用的模型")
    parser.add_argument("--endpoint", type=str,
                       default=os.getenv("OPENAI_BASE_URL", "https://api.o3.fan/v1/"),
                       help="API endpoint URL")
    parser.add_argument("--output", type=str, 
                       help="输出文件名 (如未指定，将自动生成)")
    
    args = parser.parse_args()
    
    # 如果未指定输出文件名，自动生成
    if not args.output:
        args.output = f"evaluation_results_containment_errors_{args.type}.csv"
    
    if args.mode == "preview":
        # 预览模式：只展示数据，不调用LLM
        try:
            if args.type == "FP":
                data = load_fp_data()
                print(f"找到 {len(data)} 条FP记录")
                preview_data = data
            elif args.type == "FN":
                data = load_fn_data()
                print(f"找到 {len(data)} 条FN记录")
                preview_data = data
            else:  # BOTH
                both_data = load_both_data()
                fp_count = len(both_data['FP'])
                fn_count = len(both_data['FN'])
                print(f"找到 {fp_count} 条FP记录和 {fn_count} 条FN记录，共 {fp_count + fn_count} 条记录")
                # 合并数据用于预览，FP在前，FN在后
                preview_data = both_data['FP'][:2] + both_data['FN'][:1]  # 显示前2条FP和1条FN
            
            # 打印前几条记录作为示例
            display_count = min(3, len(preview_data)) if args.type != "BOTH" else 3
            for i, data_item in enumerate(preview_data[:display_count]):
                print(f"\n=== 记录 {i+1} ===")
                print(f"Class: {data_item['class']}")
                print(f"Entity: {data_item['entity']}")
                print(f"Raw text length: {len(data_item['raw_text'])} characters")
                print(f"Raw text preview: {data_item['raw_text'][:200]}...")
                print()
                print("Formatted prompt:")
                print(format_prompt(data_item['class'], data_item['entity'], data_item['raw_text'])[:500] + "...")
                print()
                
        except Exception as e:
            print(f"错误: {e}")
            
    elif args.mode == "evaluate":
        # 评估模式：调用LLM进行评估
        if not args.api_key:
            print("错误: 评估模式需要提供API密钥。请在项目的 .env 文件中设置 OPENAI_API_KEY，或通过 --api-key 参数传入")
            return
            
        try:
            # 根据类型调用不同的评估函数
            if args.type == "FP":
                df_with_results = evaluate_fp_data(args.api_key, args.model, args.endpoint)
            elif args.type == "FN":
                df_with_results = evaluate_fn_data(args.api_key, args.model, args.endpoint)
            else:  # BOTH
                df_with_results = evaluate_both_data(args.api_key, args.model, args.endpoint)
            
            # 保存结果
            save_results(df_with_results, args.output, args.type)
            
        except Exception as e:
            print(f"错误: {e}")

if __name__ == "__main__":
    main()