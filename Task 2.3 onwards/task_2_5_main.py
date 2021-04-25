"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
TASK 2.5 MAIN SCRIPT
By Aaron Altrock
Note: where external codes are used, these are referenced at the corresponding 
locations
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
from owlready2 import *
import rdflib
from rdflib.namespace import OWL, RDF, RDFS, XSD
from rdflib import URIRef, BNode, Literal
import pprint


# Function adapted based on
# Source: E. Jiménez-Ruiz, “INM713 Semantic Web Technologies and Knowledge Graphs
# Laboratory 8: Ontology Alignment,” 2021.
def calc_scores(ls_1, ls_2):
    # Set True and False +ve and -ve to zero
    tp, tn, fp, fn = 0, 0, 0, 0
    # Note: for completeness added true -ve but will always be zero

    # Check for value in list 1 that it is in list 2
    for v1 in ls_1:
        if v1 in ls_2:
            tp += 1     # Both have in their lists
        else:
            fp += 1     # In list 1 but not in 2

    for v2 in ls_2:
        if v2 in ls_1:
            fn += 1     # In list 2 but not in 1

    # Calculate precision, recall and f1 score while handing div by 0 error
    precision = tp/(tp + fn) if (tp + fn) != 0 else .0
    recall = tp/(tp + fp) if (tp + fp) != 0 else .0
    f1 = tp/(tp + .5 * (fp + fn)) if (fp + fn) != 0 else .0

    # Pack scores to dict and return
    res_dct = {'tp': tp, 'tn': tn, 'fp': fp, 'fn': fn, 'f1': f1,
               'precision': precision,
               'recall': recall}
    return res_dct


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

    cls_f1 = calc_scores(ext_cls_ls, own_cls_ls)

    print('Lexical matching scores between classes:')
    pprint.pprint(cls_f1)

    # Check similarity by object

    # Check similarity by properties


    print('END')

if __name__ == '__main__':
    main()
