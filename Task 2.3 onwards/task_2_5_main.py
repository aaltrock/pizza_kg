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
def calc_scores(ref_ls, local_ls):
    # Set True and False +ve and -ve to zero
    tp, tn, fp, fn = 0, 0, 0, 0
    # Note: for completeness added true -ve but will always be zero

    # Check for value in ref and local lists
    for v1 in local_ls:
        if v1 in ref_ls:
            tp += 1     # Both have in their lists
        else:
            fp += 1     # In local list but not in ref list

    for v2 in ref_ls:
        if v2 not in local_ls:
            fn += 1     # In ref list but not in local list

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
def extract_class(g, delim='#'):
    cls_ls = []
    # Extract classes by finding the RDF.type definition triples with OWL.class
    for s, p, o in g:
        if p == RDF.type and o == OWL.Class and type(s) != BNode:
            cls_ls += [s]

    # Get the entity from URI based on delimiter
    cls_ls = [(uri.split(delim)[-1], uri, 'class') for uri in cls_ls]

    return cls_ls


def main():
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
            TASK 2.5 SUBTASK SPARQL.1
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    # Load in the two ontologies - own and external reference OWLs
    ref_g = rdflib.Graph()
    local_g = rdflib.Graph()

    ref_g.parse('pizza.owl.xml', format='xml')
    local_g.parse('2.4_sparql1_g.ttl', format='ttl')

    # Check similarity by class
    # Extract classes from both graphs
    ext_cls_ls = extract_class(ref_g)
    own_cls_ls = extract_class(local_g)

    # Extract objects from both graphs

    # Extract properties from both graphs

    # Extract individuals from both graphs

    # Match by every permutation among class, obj, properties, individuals


    # Calculate based on if own defined ontology exists in the external one (the standard)
    cls_f1 = calc_scores(own_cls_ls, ext_cls_ls)

    print('Lexical based matching scores between classes:')
    pprint.pprint(cls_f1)

    # Check similarity by object


    # Check similarity by properties


    # Check similarity by individuals



    print('END')

if __name__ == '__main__':
    main()
