import rdflib
from rdflib.namespace import Namespace
from rdflib.namespace import OWL, RDF, RDFS, FOAF, XSD
from rdflib import URIRef, BNode, Literal
import rdflib.tools.csv2rdf as csvrdf
import pandas as pd
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


"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
        TASK 2.3 TABULAR DATA TO KNOWLEDGE GRAPH (TASK RDF)
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""


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

objects_ls = [aa.derives, aa.follows_in_style_of, aa.has_city_of, aa.has_in_city,
              aa.has_topping, aa.has_state, aa.has_venue_at,
              aa.is_derived_from, aa.is_followed_in_style_by, aa.is_in_country,
              aa.is_in_organisation, aa.is_in_state, aa.is_topping_of,
              aa.is_sold_by, aa.locates_in, aa.sells]

for obj in objects_ls:
    g.add((obj, RDF.type, OWL.ObjectProperty))

"""
Data Properties Triples
"""

data_prop_ls = [aa.address, aa.cost, aa.description, aa.postcode]

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
stop_words_ls = ['pizza', 'base', 'dough', 'topping', 'any', 'item', 'max', 'daily', 'whip', 'meal', 'no', 'optional',
                 'inch', 'day', 'top', 'each', 'size', 'make', 'free', 'off', 'love', 'and', 'pricing', 'specialty',
                 'week', 'long', 'freshly', 'creation', 'add', 'combination', 'hearty', 'oven', 'pan', 'topping',
                 'menu', 'order', 'time', 'create', 'small', 'medium', 'large', 'value', 'get', 'equal']

# Post topping NER cleansing (lower, lemma, remove digits, remove specific stop words)
clean_df = ner.clean_topping_ner(clean_df, stop_words_ls)

# Unroll to keep tokens only as the toppings listing
clean_df['toppings'] = clean_df['spacy_ner_clean'].apply(lambda ls: [tkn for tkn, tag in ls] if ls is not None else None)

# Create new variables 'organisation' and 'venue'
clean_df['organisation'] = clean_df['name'].copy()
clean_df['venue'] = clean_df.apply(lambda row: row['name'] + ', ' + row['postcode'], axis=1)

# Create new variable to make menu item specific to each venue
clean_df['venue menu item'] = clean_df.apply(lambda row: row['menu item'] + ', ' + row['venue'], axis=1)

# Save output to Excel file for record
clean_df.reset_index(inplace=True, drop=True)
clean_df.to_excel('clean_df.xlsx', index=False)
print('Saved cleaned data frame to file clean_df.xlsx for record.')


"""
Individuals Triples
"""

# For any two given columns to be subject and object and a given predicate, iterate each row to add as triple
def add_individual_triples(g, df, subj_nm, subj_xsd_type, pred, obj_nm, obj_xsd_type):
    # Distinct pairing of subjects and objects
    __df = df[[subj_nm, obj_nm]].copy().drop_duplicates()
    # For every pair of subject and object, build literals and triple to add to graph
    for i, row in __df.iterrows():
        subj_lit = Literal(row[subj_nm], datatype=subj_xsd_type)
        obj_lit = Literal(row[obj_nm], datatype=obj_xsd_type)
        g.add((subj_lit, pred, obj_lit))
    return g


# For a given data frame, explode the nested list column after stripping rows with no content
def explode_subj_obj_df(df, col_ls, explode_col_nm, rm_duplicates=True):
    __df = df[col_ls].copy()
    # Strip None and list len of 0 rows
    __df['to_keep'] = [False if val_ls is None else True for val_ls in __df[explode_col_nm]]
    __df = __df[__df['to_keep']]
    __df['to_keep'] = [False if len(val_ls) == 0 else True for val_ls in __df[explode_col_nm]]
    __df = __df[__df['to_keep']]
    __df.drop(columns='to_keep', inplace=True)

    # Explode to unroll nested list in each row to each row as a list member
    __df = __df.explode(column=explode_col_nm)

    # Remove duplicates
    if rm_duplicates:
        __df.drop_duplicates(inplace=True)
    return __df


# state has_city_of city - for every pair of state, city, add triples
print('Building and adding triples for state has_city_of city...', end='\r')
g = add_individual_triples(g, clean_df, 'state', XSD.string, aa.has_city_of, 'city', XSD.string)

# city is_in state
print('Building and adding triples for city is_in state...', end='\r')
g = add_individual_triples(g, clean_df, 'city', XSD.string, aa.is_in, 'state', XSD.string)

# menuItem has_topping ingredient
# First build a data frame of menuItem specific to venue to ingredients (topping)
__menu_itm_topng_df = explode_subj_obj_df(clean_df, ['venue menu item', 'toppings'], 'toppings')
print('Building and adding triples for menuItem has_topping ingredient...', end='\r')
g = add_individual_triples(g, __menu_itm_topng_df, 'venue menu item', XSD.string,
                           aa.has_topping, 'toppings', XSD.string)

# country has_state state
print('Building and adding triples for country has_state state...', end='\r')
g = add_individual_triples(g, clean_df, 'country', XSD.string,
                           aa.has_state, 'state', XSD.string)

# organisation has_venue_at venue
print('Building and adding triples for organisation has_venue_at venue...', end='\r')
g = add_individual_triples(g, clean_df, 'organisation', XSD.string,
                           aa.has_venue_at, 'venue', XSD.string)

# genericDish is_derived_from menuItem
__menu_itm_cat_df = explode_subj_obj_df(clean_df, ['venue menu item', 'pizza_cat'], 'pizza_cat')
print('Building and adding triples for genericDish is_derived_from menuItem...', end='\r')
g = add_individual_triples(g, __menu_itm_cat_df, 'pizza_cat', XSD.string,
                           aa.is_derived_from, 'venue menu item', XSD.string)

# venueStyle is_followed_in_style_by venue
__venue_style_df = explode_subj_obj_df(clean_df, ['venue', 'categories'], 'categories')
print('Building and adding triples for genericDish is_derived_from menuItem...', end='\r')
g = add_individual_triples(g, __venue_style_df, 'categories', XSD.string,
                           aa.is_followed_in_style_by, 'venue', XSD.string)

# state is_in_country country
print('Building and adding triples for state is_in_country country...', end='\r')
g = add_individual_triples(g, clean_df, 'state', XSD.string,
                           aa.is_in_country, 'country', XSD.string)

# venue is_in_organisation organisation
print('Building and adding triples for venue is_in_organisation organisation...', end='\r')
g = add_individual_triples(g, clean_df, 'venue', XSD.string,
                           aa.is_in_organisation, 'organisation', XSD.string)

# ingredient is_topping_of menuItem
print('Building and adding triples for ingredient is_topping_of menuItem...', end='\r')
g = add_individual_triples(g, __menu_itm_topng_df, 'toppings', XSD.string,
                           aa.is_topping_of, 'venue menu item', XSD.string)

# menuItem is_sold_by venue
print('Building and adding triples for menuItem is_sold_by venue...', end='\r')
g = add_individual_triples(g, clean_df, 'venue menu item', XSD.string,
                           aa.is_sold_by, 'venue', XSD.string)

# venue locates_in city
print('Building and adding triples for venue locates_in city...', end='\r')
g = add_individual_triples(g, clean_df, 'venue', XSD.string,
                           aa.locates_in, 'city', XSD.string)

# venue sells menuItem
print('Building and adding triples for venue sells menuItem...', end='\r')
g = add_individual_triples(g, clean_df, 'venue', XSD.string,
                           aa.sells, 'venue menu item', XSD.string)


"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
        TASK 2.4 SPARQL & REASONING (TASK SPARQL)
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""



print('END')