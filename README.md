# Name Anonymizer

This project anonymizes names in text data using the `presidio-analyzer` and `presidio-anonymizer` libraries. It supports the addition of a custom deny list and the use of the Flair NLP framework for name recognition. By default, it applies `spacy en_core_web_lg` model.

## Features
- Anonymize names in single strings of text or entire columns in a DataFrame.
- Customize the anonymization process with a pre-defined name list to ensure specific names are always anonymized.
- Integrate with the Flair NLP framework for advanced name recognition (optional).

## Set up
To set up the environment to use the Name Anonymizer, you need to install the required packages and download the necessary language models. Run the following commands in your terminal:

```bash
pip install -r requirements.txt
python -m spacy download en_core_web_lg
```

## Example Usage
Below is an example of how to use the Name Anonymizer with a pre-defined list of names and a CSV file containing data that needs anonymization.
```python
import os
import pandas as pd
from name_anonymizer import initialize_anonymizer, anonymize_text, anonymize_dataframe_column

# Load a pre-defined list of names to anonymize.
file_path = os.path.join('./', 'predefined_name_list.txt') # Replace with the path to your pre-defined name list.
with open(file_path, 'r') as file:
    lines = file.readlines()
PREDEFINED_NAME_LIST = [line.strip() for line in lines]

# Initialize the anonymizer with the pre-defined list.
engine_config_with_deny_list = initialize_anonymizer(PREDEFINED_NAME_LIST)

# Load the CSV file you want to anonymize a column in.
file_path = "" # Replace with the path to your CSV file.
df = pd.read_csv(file_path, low_memory=False)

# Anonymize a specific column and store the results in a new column.
df = anonymize_dataframe_column(df, "Column you want to anonymize", "Name for the anonymized column", engine_config_with_deny_list)

```
