import rdflib
from rdflib.namespace import Namespace
from rdflib.namespace import OWL, RDF, RDFS, XSD
from rdflib import URIRef, BNode, Literal
from src import int_triples
import urllib

# Import other function scripts:
# 1. Clean up city and states columns
# 2. Perform Named Entity Recognition (NER) over pizza toppings
# 3. Identify pizza categories based on text token frequencies
# 4. Clean up venue categories
from lab.lookup import DBpediaLookup, GoogleKGLookup, WikidataAPI

# Levenstein distance
import Levenshtein as lv


# Create triples based on external URI found and add to graph
def add_ext_uri_triples(g, int_ns, ext_ns, df, subj_nm, subj_cls_type, subj_dct,
                        pred, obj_nm, obj_cls_type, obj_dct, value_ns, base_uri='dbpedia.org/resource'):
    # Distinct pairing of subjects and objects
    __df = df[[subj_nm, obj_nm]].copy().drop_duplicates()

    # For every pair of subject and object, build literals and triple to add to graph
    for i, row in __df.iterrows():

        # If subject/object searched for external URI then use external URI
        # If not using external URI (ie rely on internal URI) then set tuple results as None
        if subj_dct is not None:
            subj_uri_tup = subj_dct.get(row[subj_nm])
        else:
            subj_uri_tup = None

        if obj_dct is not None:
            obj_uri_tup = obj_dct.get(row[obj_nm])
        else:
            obj_uri_tup = None

        # If subject has None original values, create Blank Nodes
        if row[subj_nm] is not None:
            # If external URI is found create URI object, else make internal URI object for subjects and objects
            if subj_uri_tup is not None:
                # Literals to map URIRef to entity names
                subj_lit = Literal(row[subj_nm])
                subj_ext_lit = Literal(subj_uri_tup[2])

                # Extract the ID of the entity from external URI
                subj_uri_id = subj_uri_tup[-1].split('/')[-1]
                subj_uri = ext_ns[subj_uri_id]
            # If external URI is not found, use internal literal and URI
            else:
                subj_lit = Literal(row[subj_nm])
                subj_uri = int_ns[urllib.parse.quote(row[subj_nm])]
                subj_ext_lit = BNode()
        # Create Blank Nodes
        else:
            subj_lit = BNode()
            subj_uri = BNode()
            subj_ext_lit = BNode()

        # If object has None original values, create Blank Nodes
        if row[obj_nm] is not None:
            # If external URI is found, use external URI
            if obj_uri_tup is not None:
                # Literals to map URIRef to entity names
                obj_lit = Literal(row[obj_nm])

                # literal to retain the original external URI label
                obj_ext_lit = Literal(obj_uri_tup[2])

                # Extract the ID of the entity from external URI
                obj_uri_id = obj_uri_tup[-1].split('/')[-1]
                obj_uri = ext_ns[obj_uri_id]

            # If external URI is not found, use internal literal and URI
            else:
                obj_lit = Literal(row[obj_nm])
                obj_uri = int_ns[urllib.parse.quote(row[obj_nm])]
                obj_ext_lit = BNode()
        else:
            obj_lit = BNode()
            obj_uri = BNode()
            obj_ext_lit = BNode()

        # Add triples - define class type
        g.add((subj_uri, RDF.type, subj_cls_type))
        g.add((obj_uri, RDF.type, obj_cls_type))

        # Add triples - capture original data value
        g.add((subj_uri, RDFS.label, subj_lit))
        g.add((obj_uri, RDFS.label, obj_lit))

        # Add triples - capture original external URI value
        g.add((subj_uri, value_ns, subj_ext_lit))
        g.add((obj_uri, value_ns, obj_ext_lit))

        # Add triple - subject, predicate, object
        g.add((subj_uri, pred, obj_uri))
    return g


# Adapted from source: E.Jiménez - Ruiz, “INM713 Semantic Web Technologies and Knowledge Graphs Laboratory 6: Exposing
# Tabular Data as an RDF - based Knowledge Graph,” City, University of London, London, 2019.
def get_ext_url(name, top_n=5, api_choice='dbpedia'):
    if api_choice == 'wiki':
        api = WikidataAPI()
    elif api_choice == 'dbpedia':
        api = DBpediaLookup()
    else:
        api = GoogleKGLookup()

    entities = api.getKGEntities(name, top_n)
    # For each entity found, match by Levenstein distance and find the nearest match by label
    nearest_dist = -1
    nearest_ent = None
    for i, ent in enumerate(entities):
        lv_dist = lv.distance(ent.label, name)
        # Replace existing entity if current one is nearer match
        if (i == 0) or (lv_dist < nearest_dist):
            nearest_ent = ent
            nearest_dist = lv_dist

    # If some result is found, return the label and URI
    if nearest_ent is not None:
        return 'ext', nearest_dist, nearest_ent.label, nearest_ent.ident
    else:
        return None


# Define name space
def make_ext_g(ext_uri_g, clean_df, aa):
    external_src = 'wiki'  # External source
    ext_base = 'http://www.wikidata.org/entity/'
    ex = Namespace(ext_base)
    ext_uri_g.bind('ex', ex)

    # Get distinct lists of 'country', 'state', 'city'
    country_ls = list(clean_df['country_full'])
    state_ls = list(clean_df.apply(lambda r: r['state_full'] if r['state_full'] is not None else None, axis=1))
    city_state_ls = list(clean_df['city_state'])

    # Remove None and duplicates.  For country list add '.' after each letter as abbreviation
    country_ls = list(set([c for c in country_ls if c is not None]))
    state_ls = list(set([s for s in state_ls if s is not None]))
    city_state_ls = list(set([c for c in city_state_ls if c is not None]))

    # For each city find matching external URI
    return_nr = 5  # No. of results to return in each search

    print('Looking up external URI for country...', end='\r')
    country_dct = {ct: get_ext_url(ct, return_nr, external_src) for ct in country_ls}
    __uri_found = len([y for x, y in country_dct.items() if y is not None])
    print('{} countries with {} external URI found'.format(len(country_ls), __uri_found))

    print('Looking up external URI for state...', end='\r')
    state_dct = {st: get_ext_url(st, return_nr, external_src) for st in state_ls}
    __uri_found = len([y for x, y in state_dct.items() if y is not None])
    print('{} states with {} external URI found'.format(len(state_ls), __uri_found))

    city_state_dct = {}
    for i, cy in enumerate(city_state_ls):
        print('Looking up external URI for city: {} ({}/{})...'.format(cy, i, len(city_state_ls)), end='\r')
        city_state_dct.update({cy: get_ext_url(cy, return_nr, external_src)})

    __uri_found = len([y for x, y in city_state_dct.items() if y is not None])
    print('{} cities with {} external URI found'.format(len(city_state_ls), __uri_found))

    # impute labels with no external URI found by adding internal URI based on the original label instead
    # -1 set for fuzzy matching results
    print('Impute country, state and city without external URI found...', end='\r')
    country_dct = {orig_label: tup if tup is not None else ('int', -1, orig_label, int_triples.make_url(label=orig_label)) \
            for orig_label, tup in country_dct.items()}
    state_dct = {orig_st: tup if tup is not None else ('int', -1, orig_st, int_triples.make_url(label=orig_st)) \
            for orig_st, tup in state_dct.items()}
    city_state_dct = {orig_city: tup if tup is not None else ('int', -1, orig_city, int_triples.make_url(label=orig_city)) \
            for orig_city, tup in city_state_dct.items()}

    # Add triples to graph
    # country has_state state
    print('Building and adding triples for country has_state state...', end='\r')
    ext_uri_g = add_ext_uri_triples(ext_uri_g, aa, ex, clean_df, 'country_full', aa.country, country_dct, aa.has_state,
                                    'state_full', aa.state, state_dct, aa.label, ext_base)

    # state is_in_country country
    print('Building and adding triples for state is_in_country country...', end='\r')
    ext_uri_g = add_ext_uri_triples(ext_uri_g, aa, ex, clean_df, 'state_full', aa.state, state_dct, aa.is_in_country,
                                    'country_full', aa.country, country_dct, aa.label, ext_base)

    # state has_city_of city - for every pair of state, city, add triples
    print('Building and adding triples for state has_city_of city...', end='\r')
    ext_uri_g = add_ext_uri_triples(ext_uri_g, aa, ex, clean_df, 'state_full', aa.state, state_dct, aa.has_city_of,
                                    'city_state', aa.city, city_state_dct, aa.label, ext_base)

    # city is_in state
    print('Building and adding triples for city is_in state...', end='\r')
    ext_uri_g = add_ext_uri_triples(ext_uri_g, aa, ex, clean_df, 'city_state', aa.city, city_state_dct, aa.is_in_state,
                                    'state_full', aa.state, state_dct, aa.label, ext_base)

    # venue locates_in city
    print('Building and adding triples for venue locates_in city...', end='\r')
    ext_uri_g = add_ext_uri_triples(ext_uri_g, aa, ex, clean_df, 'venue', aa.venue, None, aa.locates_in,
                                    'city_state', aa.city, city_state_dct, aa.label, ext_base)

    # city has_in_city venue
    print('Building and adding triples for city has_in_city venue...', end='\r')
    ext_uri_g = add_ext_uri_triples(ext_uri_g, aa, ex, clean_df, 'city_state', aa.city, city_state_dct, aa.has_in_city,
                                    'venue', aa.venue, None, aa.label, ext_base)


    return ext_uri_g
