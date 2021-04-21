import rdflib
from rdflib.namespace import Namespace
from rdflib.namespace import OWL, RDF, RDFS, FOAF, XSD
from rdflib import URIRef, BNode, Literal
import rdflib.tools.csv2rdf as csvrdf
import pandas as pd
import numpy as np
import pprint as pp
import spacy as sp
import nltk
import en_core_web_sm
import random
from src import ner, city_states, pizza_types


# Set random seed
random.seed(0)

# Load NLTK files Punkt sentence tokeniser, part of speech tagger and stop words vocabulary
nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')
nltk.download('stopwords')

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
DEFINE PREFIXES
"""

# Prefix
aa = Namespace('http://www.city.ac.uk/ds/inm713/aaron_altrock#')
g.bind('aa', aa)

"""
Classes Triples
"""

classes_ls = [aa.location, aa.city, aa.country, aa.genericDish, aa.ingredient,
              aa.menuItem, aa.organisation, aa.state, aa.venue, aa.venueStyle]

for cls in classes_ls:
    g.add((cls, RDF.type, OWL.Class))

"""
Object Triples
"""

objects_ls = [aa.derives, aa.in_style_of, aa.has_city_of, aa.has_in_city,
              aa.has_ingredient_of, aa.has_state, aa.has_venue_at,
              aa.is_derived_from, aa.is_followed_in_style_by, aa.is_in_country,
              aa.is_in_organisation, aa.is_in_state, aa.is_ingredient_of,
              aa.is_sold_by, aa.locates_in, aa.sells]

for obj in objects_ls:
    g.add((obj, RDF.type, OWL.ObjectProperty))

"""
Data Properties Triples
"""

data_prop_ls = [aa.address, aa.cost, aa.description, aa.is_pizza_topping, aa.postcode]

for data_prop in data_prop_ls:
    g.add((data_prop, RDF.type, OWL.DatatypeProperty))

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

# Pizza type based on top n most frequent words in menu item names, exclude common and stop words
pizza_type_stop_words_ls = ['and', 'with', 'large', 'medium', 'small', 'pizza']
clean_df = pizza_types.make_pizza_types(clean_df, pizza_type_stop_words_ls, top_n_cut_off=15)

"""
Run NLP to identify pizza toppings
"""

# Run NLTK and spcCy NER (inc training NER model with pizza toppings)
clean_df = ner.run_ner(clean_df, trn_data_file_nm='ner_training_data.xlsx', sheet_nm='trn_data_items_ingredient')

# bespoke stop words listing to rid
stop_words_ls = ['pizza', 'topping', 'any', 'item', 'max', 'daily', 'whip', 'meal', 'no', 'optional',
                 'inch', 'day', 'top', 'each', 'size', 'make', 'free', 'off', 'love', 'and', 'pricing', 'specialty',
                 'week', 'long', 'freshly', 'creation', 'add', 'combination', 'hearty', 'oven', 'pan', 'topping',
                 'menu', 'order', 'time', 'create', 'small', 'medium', 'large', 'value', 'get', 'equal']

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
Class Triples
"""


"""
Individuals Triples
"""


"""
SOP Triples
"""

# state has_city_of city

# city is_in state

# menuItem has_ingredient_of

# country has_state state

# organisation has_venue_at venue

# genericDish is_derived_from menuItem

# venueStyle is_followed_in_style_by venue

# state is_in_country country

# venue is_in_organisation organisation

# city is_in_state state

# ingredient is_ingredient_of menuItem

# menuItem is_sold_by venue

# venue locates_in city

# venue sells menuItem




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