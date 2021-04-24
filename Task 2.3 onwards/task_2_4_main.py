"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
TASK 2.4 MAIN SCRIPT
By Aaron Altrock
Note: where external codes are used, these are referenced at the corresponding 
locations
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

import rdflib
from rdflib.namespace import Namespace
from rdflib.namespace import OWL, RDF, RDFS, XSD
from rdflib import URIRef, BNode, Literal
import pandas as pd
import urllib

def main():
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
            TASK 2.4 SUBTASK SPARQL.1
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    # Load in task 2.3 data Turtle file
    data_g = rdflib.Graph()
    data_g.parse('2.3_rdf3_python_ext_uri_g.ttl', format='ttl')
    # print(data_g.serialize(format='turtle').decode('utf-8'))

    # Load in task 2.2 ontology Turtle file
    onto_g = rdflib.Graph()
    onto_g.parse('2.2_protege_pizza_ontology.ttl', format='ttl')
    # print(onto_g.serialize(format='turtle').decode('utf-8'))

    # Union the two graphs into extended graph
    extend_g = data_g + onto_g
    # print(extend_g.serialize(format='turtle').decode('utf-8'))

    # Do some reasoning
    query_str = """SELECT ?venueName ?menuItemName 
        WHERE {?venue a aa:venue .
            ?venue aa:locates_in ?city .
            ?city rdfs:label "Los Angeles, CA" .
            ?venue aa:sells ?menuItem .
            ?venue rdfs:label ?venueName .
            ?menuItem rdfs:label ?menuItemName
        }"""

    print('Sample query - Venues based in Los Angeles and the menu items that they sell:')
    print(query_str)

    res = extend_g.query(query_str)
    for row in res:
        print(row)   # Print literals

    # Save extended graph to Turtle format
    extend_g.serialize(destination='2.4_sparql1_g.ttl', format='ttl')

    print('END')

if __name__ == '__main__':
    main()
