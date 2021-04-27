import rdflib
from rdflib.namespace import Namespace
from rdflib.namespace import OWL, RDF, RDFS, XSD
from rdflib import URIRef, BNode, Literal
import pandas as pd
import spacy as sp
import nltk
import en_core_web_sm
import urllib

# Import other function scripts:
# 1. Clean up city and states columns
# 2. Perform Named Entity Recognition (NER) over pizza toppings
# 3. Identify pizza categories based on text token frequencies
# 4. Clean up venue categories
from . import city_states, ner, pizza_types, venue_cat


# Helper function to make URI in URL formats (e.g. ' ' to %20)
def make_url(base='www.city.ac.uk/ds/inm713/aaron_altrock', label=''):
    return 'http://' + urllib.parse.quote(base) + '#' + urllib.parse.quote(label)


# For any two given columns to be subject and object and a given predicate, iterate each row to add as triple
def add_individual_triples(ns, g, df, subj_nm, subj_cls_type, pred, obj_nm, obj_cls_type, value_ns):
    # Distinct pairing of subjects and objects
    __df = df[[subj_nm, obj_nm]].copy().drop_duplicates()
    # For every pair of subject and object, build literals and triple to add to graph
    for i, row in __df.iterrows():
        # Make subjects and objects as URI base on the base URI, BNode but None values
        if row[subj_nm] is not None:
            subj_uri = ns[urllib.parse.quote(row[subj_nm])]
            subj_lit = Literal(row[subj_nm])
        else:
            subj_uri = BNode()
            subj_lit = BNode()
        if row[obj_nm] is not None:
            obj_uri = ns[urllib.parse.quote(row[obj_nm])]
            obj_lit = Literal(row[obj_nm])
        else:
            obj_uri = BNode()
            obj_lit = BNode()

        # Add triples - define class type
        g.add((subj_uri, RDF.type, subj_cls_type))
        g.add((obj_uri, RDF.type, obj_cls_type))

        # Add triples - capture original value
        g.add((subj_uri, RDFS.label, subj_lit))
        g.add((obj_uri, RDFS.label, obj_lit))

        # Add triple - subject, predicate, object
        g.add((subj_uri, pred, obj_uri))
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

# Make triples to add to graph
def make_g():
    # Load NLTK files Punkt sentence tokeniser, part of speech tagger and stop words vocabulary
    nltk.download('punkt')
    nltk.download('averaged_perceptron_tagger')
    nltk.download('stopwords')

    # Instantiate two knowledge graph object
    # 1. internal URI only graph to add triples for country, state, city
    # 2. external URI only graph to exclude triples for country, state city.
    #    These are added in task RDF.3 with external URIs.
    int_g = rdflib.Graph()
    ext_g = rdflib.Graph()

    # Load in the csv file
    src_file_nm = 'INM713_coursework_data_pizza_8358_1_reduced.csv'
    src_df = pd.read_csv(src_file_nm, header=0)
    print('Loaded in the file {}: {} by {}'.format(src_file_nm, src_df.shape[0], src_df.shape[1]))

    """
    DEFINE PREFIXES
    """

    # Prefix
    aa = Namespace('http://www.city.ac.uk/ds/inm713/aaron_altrock#')
    int_g.bind('aa', aa)
    ext_g.bind('aa', aa)

    """
    Classes Triples
    """

    classes_ls = [aa.location, aa.genericDish, aa.ingredient,
                  aa.menuItem, aa.organisation, aa.venue, aa.venueStyle, aa.label]

    # External graph to exclude country, state, city - will add later in task RDF.3
    for cls in classes_ls:
        ext_g.add((cls, RDF.type, OWL.Class))

    # Add for internal URIs graph
    classes_ls += [aa.city, aa.country, aa.state]
    for cls in classes_ls:
        int_g.add((cls, RDF.type, OWL.Class))

    """
    Object Triples
    """

    objects_ls = [aa.derives, aa.follows_in_style_of, aa.has_city_of, aa.has_in_city,
                  aa.has_topping, aa.has_state, aa.has_venue_at,
                  aa.is_derived_from, aa.is_followed_in_style_by, aa.is_in_country,
                  aa.is_in_organisation, aa.is_in_state, aa.is_topping_of,
                  aa.is_sold_by, aa.locates_in, aa.sells]

    for obj in objects_ls:
        int_g.add((obj, RDF.type, OWL.ObjectProperty))
        ext_g.add((obj, RDF.type, OWL.ObjectProperty))


    """
    Column clean up
    """

    clean_df = src_df.copy()

    # Make country listing to full listing (US to United States)
    clean_df['country_full'] = [c if c != 'US' else 'United States' for c in clean_df['country']]

    # Read in the zip code ranges
    zip_rng_df = pd.read_excel('zip_code_ranges.xlsx', header=0)
    clean_df = city_states.clean(clean_df, zip_rng_df)

    # Map state abbreviation to full name
    st_state_dct = list(zip_rng_df[['State Name', 'ST']].drop_duplicates().apply(lambda r: (r['State Name'], r['ST']), axis=1))
    st_state_dct = {st: state for state, st in st_state_dct}
    clean_df['state_full'] = clean_df['state'].apply(lambda st: st_state_dct.get(st) if st is not None else st)

    # impute blank zip codes with '0' (placeholder), not leaving it None so that venue data are filled
    clean_df['postcode'] = clean_df['postcode'].apply(str)
    clean_df['postcode'] = [pcd if len(pcd) > 0 else '0' for pcd in clean_df['postcode']]

    # replace city with city, state convention
    clean_df['city'] = clean_df['city_state'].copy()

    """
    Create new variables for the triples
    """
    # Item description - set to string and replace NaN to None
    clean_df['item description'] = [None if pd.isna(v) else str(v) for v in clean_df['item description']]

    # Pizza type based on top n most frequent words in menu item names, exclude common and stop words
    pizza_type_stop_words_ls = ['and', 'with', 'large', 'medium', 'small', 'pizza', 'ingredient']
    clean_df = pizza_types.make_pizza_types(clean_df, pizza_type_stop_words_ls, top_n_cut_off=15)

    """
    Run NLP to identify pizza toppings
    """
    # Run NLTK and spaCy NER (inc training NER model with pizza toppings)
    clean_df, nlp = ner.run_ner(clean_df, trn_data_file_nm='ner_training_data.xlsx', sheet_nm='trn_data_items_ingredient')

    # bespoke stop words listing to rid
    stop_words_ls = ['pizza', 'base', 'dough', 'topping', 'any', 'item', 'max', 'daily', 'whip', 'meal', 'no', 'optional',
                     'inch', 'day', 'top', 'each', 'size', 'make', 'free', 'off', 'love', 'and', 'pricing', 'specialty',
                     'week', 'long', 'freshly', 'creation', 'add', 'combination', 'hearty', 'oven', 'pan', 'topping',
                     'menu', 'order', 'time', 'create', 'small', 'medium', 'large', 'value', 'get', 'equal', 'coupon',
                     'offer', 'dish', 'ingredient']

    # Post topping NER cleansing (lower, lemma, remove digits, remove specific stop words)
    clean_df = ner.clean_topping_ner(clean_df, stop_words_ls)

    # Unroll to keep tokens only as the toppings listing
    clean_df['toppings'] = clean_df['spacy_ner_clean'].apply(lambda ls: [tkn for tkn, tag in ls] if ls is not None else None)

    # Create new variables 'organisation' and 'venue'
    clean_df['organisation'] = clean_df['name'].copy()
    clean_df['venue'] = clean_df.apply(lambda row: row['name'] + '__' + row['postcode'], axis=1)

    # Create new variable to make menu item specific to each venue
    clean_df['venue menu item'] = clean_df.apply(lambda row: row['menu item'] + '__' + row['venue'], axis=1)

    """
    Run NLP to clean and filter venue categories
    """
    # Categories: Exploding nested string into list and clean up, and remove specific stop words
    cat_sub_words_ls = [('take out', 'take-out'), ('fast food', 'fast-food')]

    cat_stop_words_ls = ['place', 'restaurants', 'pizza', ',', '&', 'and', 'venue', 'area', 'food', 'ingredient']

    clean_df = venue_cat.clean_venue_cat(clean_df, cat_stop_words_ls, cat_sub_words_ls, nlp)

    """
    Save cleaned data frame (with new features) to file for record
    """
    # Save output to Excel file for record
    clean_df.reset_index(inplace=True, drop=True)
    clean_df.to_excel('clean_df.xlsx', index=False)
    print('Saved cleaned data frame to file clean_df.xlsx for record.')

    """
    Individuals Triples
    """

    # menuItem has_topping ingredient
    # First build a data frame of menuItem specific to venue to ingredients (topping)
    __menu_itm_topng_df = explode_subj_obj_df(clean_df, ['venue menu item', 'toppings'], 'toppings')
    print('Building and adding triples for menuItem has_topping ingredient...', end='\r')
    int_g = add_individual_triples(aa, int_g, __menu_itm_topng_df, 'venue menu item', aa.menuItem, aa.has_topping,
                                   'toppings', aa.ingredient, aa.label)
    ext_g = add_individual_triples(aa, ext_g, __menu_itm_topng_df, 'venue menu item', aa.menuItem, aa.has_topping,
                                   'toppings', aa.ingredient, aa.label)

    # organisation has_venue_at venue
    print('Building and adding triples for organisation has_venue_at venue...', end='\r')
    int_g = add_individual_triples(aa, int_g, clean_df, 'organisation', aa.organisation,
                                   aa.has_venue_at, 'venue', aa.venue, aa.label)
    ext_g = add_individual_triples(aa, ext_g, clean_df, 'organisation', aa.organisation,
                                   aa.has_venue_at, 'venue', aa.venue, aa.label)

    # genericDish is_derived_from menuItem
    __menu_itm_cat_df = explode_subj_obj_df(clean_df, ['venue menu item', 'pizza_cat'], 'pizza_cat')
    print('Building and adding triples for genericDish is_derived_from menuItem...', end='\r')
    int_g = add_individual_triples(aa, int_g, __menu_itm_cat_df, 'pizza_cat', aa.genericDish,
                                   aa.is_derived_from, 'venue menu item', aa.menuItem, aa.label)
    ext_g = add_individual_triples(aa, ext_g, __menu_itm_cat_df, 'pizza_cat', aa.genericDish,
                                   aa.is_derived_from, 'venue menu item', aa.menuItem, aa.label)

    # venueStyle is_followed_in_style_by venue
    __venue_style_df = explode_subj_obj_df(clean_df, ['venue', 'categories'], 'categories')
    print('Building and adding triples for venueStyle is_followed_in_style_by venue...', end='\r')
    int_g = add_individual_triples(aa, int_g, __venue_style_df, 'categories', aa.category,
                                   aa.is_followed_in_style_by, 'venue', aa.venue, aa.label)
    ext_g = add_individual_triples(aa, ext_g, __venue_style_df, 'categories', aa.category,
                                   aa.is_followed_in_style_by, 'venue', aa.venue, aa.label)

    # venue follows_in_style_of venueStyle
    __venue_style_df = explode_subj_obj_df(clean_df, ['venue', 'categories'], 'categories')
    print('Building and adding triples for venue follows_in_style_of venueStyle...', end='\r')
    int_g = add_individual_triples(aa, int_g, __venue_style_df, 'venue', aa.venue,
                                   aa.follows_in_style_of, 'categories', aa.category, aa.label)
    ext_g = add_individual_triples(aa, ext_g, __venue_style_df, 'venue', aa.venue,
                                   aa.follows_in_style_of, 'categories', aa.category, aa.label)


    # venue is_in_organisation organisation
    print('Building and adding triples for venue is_in_organisation organisation...', end='\r')
    int_g = add_individual_triples(aa, int_g, clean_df, 'venue', aa.venue, aa.is_in_organisation,
                                   'organisation', aa.organisation, aa.label)
    ext_g = add_individual_triples(aa, ext_g, clean_df, 'venue', aa.venue, aa.is_in_organisation,
                                   'organisation', aa.organisation, aa.label)

    # ingredient is_topping_of menuItem
    print('Building and adding triples for ingredient is_topping_of menuItem...', end='\r')
    int_g = add_individual_triples(aa, int_g, __menu_itm_topng_df, 'toppings', aa.ingredient, aa.is_topping_of,
                                   'venue menu item', aa.menuItem, aa.label)
    ext_g = add_individual_triples(aa, ext_g, __menu_itm_topng_df, 'toppings', aa.ingredient, aa.is_topping_of,
                                   'venue menu item', aa.menuItem, aa.label)

    # menuItem is_sold_by venue
    print('Building and adding triples for menuItem is_sold_by venue...', end='\r')
    int_g = add_individual_triples(aa, int_g, clean_df, 'venue menu item', aa.menuItem, aa.is_sold_by,
                                   'venue', aa.venue, aa.label)
    ext_g = add_individual_triples(aa, ext_g, clean_df, 'venue menu item', aa.menuItem, aa.is_sold_by,
                                   'venue', aa.venue, aa.label)

    # venue sells menuItem
    print('Building and adding triples for venue sells menuItem...', end='\r')
    int_g = add_individual_triples(aa, int_g, clean_df, 'venue', aa.venue, aa.sells,
                                   'venue menu item', aa.menuItem, aa.label)
    ext_g = add_individual_triples(aa, ext_g, clean_df, 'venue', aa.venue, aa.sells,
                                   'venue menu item', aa.menuItem, aa.label)

    # Below update the graph with internal URIs only - the external URI will add in the next coursework task
    # country has_state state
    print('Building and adding triples for country has_state state...', end='\r')
    int_g = add_individual_triples(aa, int_g, clean_df, 'country_full', aa.country, aa.has_state,
                                   'state_full', aa.state, aa.label)

    # state is_in_country country
    print('Building and adding triples for state is_in_country country...', end='\r')
    int_g = add_individual_triples(aa, int_g, clean_df, 'state_full', aa.state, aa.is_in_country,
                                   'country_full', aa.country, aa.label)

    # state has_city_of city - for every pair of state, city, add triples
    print('Building and adding triples for state has_city_of city...', end='\r')
    int_g = add_individual_triples(aa, int_g, clean_df, 'state_full', aa.state, aa.has_city_of,
                                   'city_state', aa.city, aa.label)

    # city is_in state
    print('Building and adding triples for city is_in state...', end='\r')
    int_g = add_individual_triples(aa, int_g, clean_df, 'city_state', aa.city, aa.is_in_state,
                                   'state_full', aa.state, aa.label)

    # venue locates_in city
    print('Building and adding triples for venue locates_in city...', end='\r')
    int_g = add_individual_triples(aa, int_g, clean_df, 'venue', aa.venue, aa.locates_in,
                                   'city_state', aa.city, aa.label)

    # city has_in_city venue
    print('Building and adding triples for city has_in_city venue...', end='\r')
    int_g = add_individual_triples(aa, int_g, clean_df, 'city_state', aa.city, aa.has_in_city,
                                   'venue', aa.venue, aa.label)

    """
    Data Properties Triples
    """

    data_prop_ls = [aa.address, aa.cost, aa.description, aa.postcode]

    for data_prop in data_prop_ls:
        int_g.add((data_prop, RDF.type, OWL.DatatypeProperty))
        ext_g.add((data_prop, RDF.type, OWL.DatatypeProperty))

    """
    Data Properties Triples
    """
    # For every row in source file, add data properties (cost, address, post code and item description)
    for i, row in clean_df.iterrows():
        # if costs is captured, venue menu item :cost cost
        if row['item value'] is not None and not pd.isna(row['item value']):
            cost_lit = Literal(row['item value'], datatype=XSD.double)
        else:
            cost_lit = BNode()
        menu_item = URIRef(make_url(label=row['venue menu item']))
        int_g.add((menu_item, aa.cost, cost_lit))
        ext_g.add((menu_item, aa.cost, cost_lit))

        # if description exists, menu item :item description description
        if row['item description'] is not None:
            descr_lit = Literal(row['item description'], datatype=XSD.string)
        else:
            descr_lit = BNode()
        int_g.add((menu_item, aa.description, descr_lit))
        ext_g.add((menu_item, aa.description, descr_lit))

        # venue :address address
        if row['address'] is not None:
            addr_lit = Literal(row['address'], datatype=XSD.string)
        else:
            addr_lit = BNode()
        venue = URIRef(make_url(label=row['venue']))
        int_g.add((venue, aa.address, addr_lit))
        ext_g.add((venue, aa.address, addr_lit))

        # venue :postcode postcode
        if row['postcode'] is not None and row['postcode'] != 'nan':
            postcode_lit = Literal(row['postcode'], datatype=XSD.string)
        else:
            postcode_lit = BNode()
        int_g.add((venue, aa.postcode, postcode_lit))
        ext_g.add((venue, aa.postcode, postcode_lit))

    """
        Returns:
        - src_df: original data
        - clean_df: cleaned data with new features
        - int_g: graph entirely from internal URIs with aa namespace
        - ext_g: graph with internal URIs but for country, state and city to use external URI ref later
        - aa: internal namespace for use later
    """
    return src_df, clean_df, int_g, ext_g, aa

