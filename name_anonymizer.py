"""
Main module for the name anonymizer.
You should use your name pre-defined name list to initialize the anonymizer.
"""

import json
import os
from typing import Any, Dict, Optional, Union, List, Tuple

import pandas as pd
from presidio_analyzer import (AnalyzerEngine, PatternRecognizer,
                               RecognizerRegistry)
from presidio_anonymizer import AnonymizerEngine
from presidio_anonymizer.entities import OperatorConfig
from tqdm import tqdm


def initialize_anonymizer(deny_list: Optional[List[str]] = None, 
                          flair_recognizer: Any = None) -> Dict[str, Union[AnalyzerEngine, AnonymizerEngine, Dict[str, OperatorConfig]]]:
    """
    Initializes and configures an anonymizer with optional deny list and flair recognizer.

    Parameters
    ----------
    deny_list : list of str, optional
        List of names or phrases to be explicitly denied (i.e., redacted).
    flair_recognizer : Any, optional
        A recognizer based on the Flair NLP framework, if available.

    Returns
    -------
    dict
        A dictionary containing the following:
        - 'analyzer' : AnalyzerEngine
            The analyzer engine initialized with the given recognizers.
        - 'anonymizer' : AnonymizerEngine
            The anonymizer engine.
        - 'config' : dict of str to OperatorConfig
            Configuration for the anonymizer for each entity type.
        - 'entities' : list of str
            List of entity types that the analyzer recognizes.
    """
    registry = RecognizerRegistry()
    registry.load_predefined_recognizers()
    analyzer_entites=['PERSON']

    if deny_list:
        deny_list_recognizer = PatternRecognizer(supported_entity="PREDEFINED_NAME", deny_list=deny_list)
        registry.add_recognizer(deny_list_recognizer)

    if flair_recognizer:
        registry.add_recognizer(flair_recognizer)

    analyzer = AnalyzerEngine(registry=registry)
    anonymizer = AnonymizerEngine()

    anonymizer_config = {
        "PERSON": OperatorConfig("replace", {"new_value": "[name redacted]"})
    }

    if deny_list:
        anonymizer_config["PREDEFINED_NAME"] = OperatorConfig("replace", {"new_value": "[name redacted]"})
        analyzer_entites.append('PREDEFINED_NAME')

    return {
        "analyzer": analyzer,
        "anonymizer": anonymizer,
        "config": anonymizer_config,
        "entities": analyzer_entites
    }

def anonymize_text(text_to_anonymize: str, 
                   engine_config: Dict[str, Union[AnalyzerEngine, AnonymizerEngine, Dict[str, OperatorConfig]]]) -> Tuple[str, Any]:
    """
    Anonymizes the given text using the specified engine configuration.

    Parameters
    ----------
    text_to_anonymize : str
        The text to be anonymized.
    engine_config : dict
        Configuration for the anonymization process, containing:
        - 'analyzer' : AnalyzerEngine
            The analyzer engine initialized with the given recognizers.
        - 'anonymizer' : AnonymizerEngine
            The anonymizer engine.
        - 'config' : dict of str to OperatorConfig
            Configuration for the anonymizer for each entity type.
        - 'entities' : list of str
            List of entity types that the analyzer recognizes.

    Returns
    -------
    tuple of str and Any
        The anonymized text and the results from the analyzer.
    """
    analyzer = engine_config["analyzer"]
    anonymizer = engine_config["anonymizer"]
    config = engine_config["config"]
    entites = engine_config["entities"]

    analyzer_results = analyzer.analyze(text=text_to_anonymize, entities = entites, language='en')
    anonymized_result = anonymizer.anonymize(text=text_to_anonymize,
                                             analyzer_results=analyzer_results,
                                             operators=config)

    return anonymized_result.text, analyzer_results

def anonymize_dataframe_column(df: pd.DataFrame, column_name: str, new_column_name: str, engine_config: Dict[str, Union[AnalyzerEngine, AnonymizerEngine, Dict[str, OperatorConfig]]]) -> pd.DataFrame:
    """
    Anonymizes the specified column in a DataFrame using the provided engine configuration.
    The results are stored in a new column.

    Parameters
    ----------
    df : pd.DataFrame
        The DataFrame containing the column to be anonymized.
    column_name : str
        The name of the column in the DataFrame to be anonymized.
    new_column_name : str
        The name of the new column where the anonymized values will be stored.
    engine_config : dict
        Configuration for the anonymization process, containing:
        - 'analyzer' : AnalyzerEngine
            The analyzer engine initialized with the given recognizers.
        - 'anonymizer' : AnonymizerEngine
            The anonymizer engine.
        - 'config' : dict of str to OperatorConfig
            Configuration for the anonymizer for each entity type.
        - 'entities' : list of str
            List of entity types that the analyzer recognizes.

    Returns
    -------
    pd.DataFrame
        The DataFrame with the new column containing anonymized values.
    """
    df[column_name] = df[column_name].astype(str)
    anonymized_values = []

    for value in tqdm(df[column_name], desc=f"Anonymizing {column_name}"):
        anonymized_value, ent_list = anonymize_text(value, engine_config)
        for n in ent_list:
          if n.entity_type != 'PREDEFINED_NAME' and n.entity_type != 'PERSON':
            print("Edage Case Found!")
            print(n)
        anonymized_values.append(anonymized_value)

    df[new_column_name] = anonymized_values

    return df