"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
TASK 2.5 MAIN SCRIPT
By Aaron Altrock
Note: where external codes are used, these are referenced at the corresponding 
locations
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

import rdflib
from rdflib.namespace import OWL, RDF, RDFS, XSD
from rdflib import URIRef, BNode, Literal

def calc_f_score(v1, v2):

    return None


# Extract classes (excluding blank nodes)
def extract_class(g):
    cls_ls = []
    for s, p, o in g:
        if p == RDF.type and o == OWL.Class and type(s) != BNode:
            cls_ls += [s]
    return cls_ls


def main():
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
            TASK 2.5 SUBTASK SPARQL.1
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    # Load in the two ontologies - own and external OWLs
    ext_g = rdflib.Graph()
    own_g = rdflib.Graph()

    ext_g.parse('pizza.owl.xml', format='xml')
    own_g.parse('2.4_sparql1_g.ttl', format='ttl')

    # Check similarity by class
    # Extract classes from both graphs
    ext_cls_ls = extract_class(ext_g)
    own_cls_ls = extract_class(own_g)

    # Check similarity by object

    # Check similarity by properties


    print('END')

if __name__ == '__main__':
    main()
