import os

from step_1_cir import cas_standard
from step_2_1_pubchem import pubchem_standardize
from step_2_2_pubchem_cas_check import pubchem_standard_cas_check
from step_2_3_pubchem_name_check import pubchem_standard_name_check
from step_3_1_get_opsin_names import get_opsin_names
from step_3_3_get_opsin import get_opsin
from step_4_1_glm_name_process import glm_name_process
from step_4_2_pubchem_after_glm import pubchem_after_glm
from step_4_3_get_pubchem_after_glm import get_pubchem_after_glm
from step_5_name_remove_cas import name_remove_cas
from step_6_reaction_match import reaction_match
from step_6_alt_fuzzy_reaction_match import fuzzy_reaction_match


def main(api_key, model='glm-4'):
    # Step 1: CAS standardization
    cas_standard('raw_names', 'names_cir')

    # Step 2: PubChem standardization
    pubchem_standardize('names_cir', 'names_cir_pub')
    pubchem_standard_cas_check('names_cir_pub', 'names_cir_pub_cas_ckecked_pub')
    pubchem_standard_name_check('names_cir_pub_cas_ckecked_pub', 'names_cir_pub_cas_ckecked_pub_name_pub')

    # Step 3: OPSIN standardization
    get_opsin_names('names_cir_pub_cas_ckecked_pub_name_pub', 'names_cir_pub_cas_ckecked_pub_name_pub_preopsin')
    os.system('java -jar opsin-cli-2.8.0-jar-with-dependencies.jar -osmi input.txt output.txt')
    get_opsin('names_cir_pub_cas_ckecked_pub_name_pub', 'names_cir_pub_cas_ckecked_pub_name_pub_preopsin', 'names_cir_pub_cas_ckecked_pub_name_pub_opsin')
    
    # Step 4: GLM standardization
    glm_name_process('names_cir_pub_cas_ckecked_pub_name_pub_opsin', 'names_cir_pub_cas_ckecked_pub_name_pub_opsin_prename', api_key, model)
    pubchem_after_glm('names_cir_pub_cas_ckecked_pub_name_pub_opsin_prename', 'names_cir_pub_cas_ckecked_pub_name_pub_opsin_prename_pubchemdata')
    get_pubchem_after_glm('names_cir_pub_cas_ckecked_pub_name_pub_opsin', 'names_cir_pub_cas_ckecked_pub_name_pub_opsin_prename_pubchemdata', 'names_cir_pub_cas_ckecked_pub_name_pub_opsin_glm_pubchem')
    
    # Step 5: Remove CAS from names
    name_remove_cas('names_cir_pub_cas_ckecked_pub_name_pub_opsin_glm_pubchem', 'names_cir_pub_cas_ckecked_pub_name_pub_opsin_glm_pubchem_final')

    # Step 6: Reaction matching
    reaction_match('raw_names', 'names_cir_pub_cas_ckecked_pub_name_pub_opsin_glm_pubchem_final', 'names_cir_pub_cas_ckecked_pub_name_pub_opsin_glm_pubchem_smiles')
    fuzzy_reaction_match('raw_names', 'names_cir_pub_cas_ckecked_pub_name_pub_opsin_glm_pubchem_final', 'names_cir_pub_cas_ckecked_pub_name_pub_opsin_glm_pubchem_smiles')
    
    print('Done!')

if __name__ == '__main__':
    api_key = 'your_api_key'# Your GLM-4 API key.
    model = 'glm-4'
    main(api_key, model)