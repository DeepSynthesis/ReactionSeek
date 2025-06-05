# Automatically collecting reaction data

## extract_gpt.py
This script is used to extract reaction data using OpenAI API foramt. The script input should be a json file at least contains "Title" and "Procedure", for example:

```json
{
    "volume96article1": {
        "Title": "Title information of the reaction procedure.",
        "Procedure": "The reaction of 1,2-dimethoxyethane with sodium ethoxide in dry ether is an elimination reaction to form ethene and methoxide ion."
    },
}
```

After prepared your input files, you should edit this part of script:

```python
if __name__ == '__main__':

    openai.proxy = {
                    'http': '',#your http proxy
                    'https': ''#your https proxy
    }
    openai.api_key = ""#your api key
    openai.base_url = "https://api.openai.com/v1"#your api base url
    model = 'gpt-3.5-turbo-16k'#your model
    volumes = ["Volume26-30"]#names of json files
    start = time.perf_counter()
    main(volumes, model)
    end = time.perf_counter()
    print('runningtime:' + str(end - start))
```

Then run the script:

```bash
python extract_gpt.py
```

## strcuturelize.py
This script is used to structurelize the initial output csv file to a csv table containing Index, Reactants, Reactant amounts, Products, Product amounts, Solvents, Reaction temperature, Reaction time and Yield. The input file should be the output csv file of extract_gpt.py. 

After prepared your input files, you should edit this part of script:

```python
if __name__ == '__main__':
    volumes = ["Volume96-100"]#your json name(same as the first step)
    start = time.perf_counter()
    main(volumes)
    end = time.perf_counter()
    print('runningtime:' + str(end - start))
```

Then run the script:

```bash
python strcuturelize.py
```

The output file "xxx_table.csv" is the structured csv file.