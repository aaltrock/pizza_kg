import rdflib
from rdflib.namespace import Namespace
from rdflib.namespace import OWL, RDF, RDFS, FOAF, XSD
from rdflib import URIRef, Literal
import rdflib.tools.csv2rdf as csvrdf
import pandas as pd
import numpy as np
import pprint as pp
import spacy as sp
import nltk
import en_core_web_sm
import random
from src import ner, city_states


# Set random seed
random.seed(0)

# Load NLTK files Punkt sentence tokeniser and part of speech tagger
nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')

# Load Spacy
nlp = en_core_web_sm.load()

# Load pre-trained Spacy model
# NOTE: In the terminal run: python -m spacy download en_core_web_sm to download pre-trained model
nlp = sp.load('en_core_web_sm')

"""
Initialise
"""

# Instantiate a knowledge graph object
g = rdflib.Graph()

# Load in the csv file
src_file_nm = 'INM713_coursework_data_pizza_8358_1_reduced.csv'
src_df = pd.read_csv(src_file_nm, header=0)
print('Loaded in the file {}: {} by {}'.format(src_file_nm, src_df.shape[0], src_df.shape[1]))


"""
Load in Turtle definition
"""

# # Parse Turtle from task 2.2 for some definitions
# g.parse('pizza_ontology.ttl', format='turtle')

# # Prefix
# pfx = 'http://www.city.ac.uk/ds/inm713/aaron_altrock'
# g.bind('aa', pfx)


"""
Column clean up
"""

clean_df = src_df.copy()

# Read in the zip code ranges
zip_rng_df = pd.read_excel('zip_code_ranges.xlsx', header=0)
clean_df = city_states.clean(clean_df, zip_rng_df)

# impute blank zip codes with '0' (placeholder), not leaving it None so that venue data are filled
clean_df['postcode'] = clean_df['postcode'].apply(str)
clean_df['postcode'] = [pcd if len(pcd) > 0 else '0' for pcd in clean_df['postcode']]


# For categories explode the delimited string into lists for each row
def __explode_str(s, delim=','):
    if len(s) > 0:
        return s.split(delim)
    elif s is None:
        return s
    else:
        return ''


"""
Create new variables for the triples
"""

# Categories: Exploding nested string into list
cat_ls = [__explode_str(s) for s in clean_df['categories']]
clean_df['categories'] = cat_ls

# Item description - set to string and replace NaN to None
clean_df['item description'] = [None if pd.isna(v) else str(v) for v in clean_df['item description']]


"""
Run NLP to identify pizza toppings
"""

# Run NLTK and spcCy NER (inc training NER model with pizza toppings)
clean_df = ner.run_ner(clean_df, trn_data_file_nm='ner_training_data.xlsx', sheet_nm='trn_data_items_ingredient')

# bespoke stop words listing to rid
stop_words_ls = ['pizza', 'topping', 'any', 'item', 'max', 'daily', 'whip', 'meal', 'no', 'optional',
                 'inch', 'day', 'top', 'each', 'size', 'make', 'free', 'off', 'love', 'and', 'pricing', 'specialty',
                 'week', 'long', 'freshly', 'creation', 'add', 'combination', 'hearty', 'oven', 'pan']

# Post topping NER cleansing (lower, lemma, remove digits, remove specific stop words)
clean_df = ner.clean_topping_ner(clean_df, stop_words_ls)

# Unroll to keep tokens only as the toppings listing
clean_df['toppings'] = clean_df['spacy_ner_clean'].apply(lambda ls: [tkn for tkn, tag in ls] if ls is not None else None)

# Create new variables 'organisation' and 'venue'
clean_df['organisation'] = clean_df['name'].copy()
clean_df['venue'] = clean_df.apply(lambda row: row['name'] + '_' + row['postcode'], axis=1)

# Save output to Excel file for record
clean_df.to_excel('clean_df.xlsx', index=False)
print('Saved cleaned data frame to file clean_df.xlsx for record.')

"""
Derive master lists of categories, menu items and item descriptions by splitting delimited strings
"""

# Retrieve master lists - removing duplicates:

# organisation
org_ls = list(set(clean_df['name']))

# venue (organisation + post code)
ven_ls = list(set(list(clean_df['venue'])))

# cities in state


# location (venue, address), (venue, city), (venue, postcode)


# categories

# menu items

# (pizza toppings) - item descriptoin
toppings_ls = [ls for ls in clean_df['toppings'] if ls is not None]
toppings_ls = list(set([x for y in toppings_ls for x in y]))



"""
For each column parse into triples except country as all were 'US'
"""



# city, belongs, state


# name -> organisation

# name + '_' + zip code -> venue

#  -> state has_state





print('END')