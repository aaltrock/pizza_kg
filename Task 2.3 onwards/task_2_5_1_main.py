"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
TASK 2.5 SUBTASK 1 MAIN SCRIPT
By Aaron Altrock
Note: where external codes are used, these are referenced at the corresponding 
locations
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
import owlready2 as rdy
import re
import rdflib
from rdflib.namespace import Namespace
from rdflib.namespace import OWL, RDF, RDFS, XSD
from rdflib import URIRef, BNode, Literal
import logging
from enum import Enum


# Return ontology class name (RDFS label) and class as tuple
def get_class_name(onto):
    res_ls = []
    for cl in onto.classes():
        res_ls += [(cl.name.lower(), cl)]

    if len(res_ls) > 0:
        res_ls = [(nm, 'class', cl) for nm, cl in res_ls]
    return res_ls


# Return the individuals under a list of classes in a given ontology
def get_class_individual(onto, class_ls):
    # Return as dictionary {(class name, class): [(indidual name, individual), ...]}
    res_ls = []
    for cl_nm, _, cl in class_ls:
        print('Extracting class individuals for class: {}...'.format(cl_nm), end='\r')
        __res_ls = onto.search(is_a=cl)
        __res_ls = [(res.name, 'class_ind', res, cl_nm, cl) for res in __res_ls]
        res_ls += __res_ls
    return res_ls


# Return ontology object property including name
def get_obj_prop(onto):
    res_ls = [(p.name.lower(), p) for p in onto.object_properties()]
    if len(res_ls) > 0:
        res_ls = [(nm, 'obj_prop', p) for nm, p in res_ls]
    return res_ls


# Return ontology data property including name
def get_data_prop(onto):
    res_ls = [(p.name.lower(), p) for p in onto.data_properties()]
    if len(res_ls) > 0:
        res_ls = [(nm, 'data_prop', p) for nm, p in res_ls]
    return res_ls


def main():
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
            TASK 2.5 SUBTASK SPARQL.1
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    print('TASK 2.5 SUBTASK SPARQL.1\n')
    # Load in reference and local (from task 2.4) ontologies
    ref_file_path = 'pizza.owl'
    loc_file_path = '2.4_sparql1_g.owl.xml'
    
    ref_onto = rdy.get_ontology(ref_file_path)
    ref_onto.load()

    loc_onto = rdy.get_ontology(loc_file_path)
    loc_onto.load()

    # Get classes
    ref_cl_ls = get_class_name(ref_onto)
    loc_cl_ls = get_class_name(loc_onto)

    # Get object properties
    ref_obj_prop_ls = get_obj_prop(ref_onto)
    loc_obj_prop_ls = get_obj_prop(loc_onto)

    # Get data properties
    ref_data_prop_ls = get_data_prop(ref_onto)
    loc_data_prop_ls = get_data_prop(loc_onto)

    # Get individuals for all classes
    ref_cl_ind_ls = get_class_individual(ref_onto, ref_cl_ls)
    loc_cl_ind_ls = get_class_individual(loc_onto, loc_cl_ls)

    # Combine lists of classes, object and data properties and individuals by class
    ref_onto_ls = ref_cl_ls + ref_obj_prop_ls + ref_data_prop_ls + ref_cl_ind_ls
    loc_onto_ls = loc_cl_ls + loc_obj_prop_ls + loc_data_prop_ls + loc_cl_ind_ls

    # String based matching labels of the same (e.g. class v class) and different elements (e.g. class v individual)
    print('Performing string based matching of labels with same type and across different types...', end='\r')

    # Set thresholds to control Regex subset string match
    max_len_diff = 8    # Max length difference between two strings to recognise Regex subset match
    min_len = 5         # Min length to perform Regex match

    # Approach to determine TP, FP and FN adapted based on
    # Source: E. Jiménez-Ruiz, “INM713 Semantic Web Technologies and Knowledge Graphs
    # Laboratory 8: Ontology Alignment,” 2021.

    tp_exact_match_ls = []
    tp_subset_match_ls = []
    fp_match_ls = []
    fn_match_ls = []
    # Compare every element in local ontology for exact or subset match (to within a tolerance)
    for l_tup in loc_onto_ls:
        __exact_match_ls = []
        __subset_match_ls = []
        for r_tup in ref_onto_ls:
            # Difference in length between ref and local labels
            len_diff = len(l_tup[0]) - len(r_tup[0])

            # If exact string match
            if l_tup[0] == r_tup[0]:
                is_same_type = True if l_tup[1] == r_tup[1] else False
                __exact_match_ls += [(len_diff, is_same_type, l_tup, r_tup)]

            # If local label string is a subset of reference label,
            # and lengths of both exceed min length thresholds set
            # and length difference (positive polarity) within threshold
            elif re.search(l_tup[0], r_tup[0]) is not None and \
                    len(l_tup[0]) >= min_len and len(r_tup[0]) >= min_len\
                    and (len_diff**2)**.5 <= max_len_diff:
                is_same_type = True if l_tup[1] == r_tup[1] else False
                __subset_match_ls += [(len_diff, is_same_type, l_tup, r_tup)]

        # If exact/subset match found of local element in ref element, then TRUE POSITIVE
        if len(__exact_match_ls) > 0:
            tp_exact_match_ls += __exact_match_ls
        if len(__subset_match_ls) > 0:
            tp_subset_match_ls += __subset_match_ls

        # If no match found, FALSE POSITIVE, in local but not in ref ontology
        if len(__exact_match_ls) + len(__subset_match_ls) == 0:
            fp_match_ls += [l_tup]
    # Reverse to compare every element in the reference ontology for exact or subset match
    for r_tup in ref_onto_ls:
        __match_ls = []
        for l_tup in loc_onto_ls:
            if re.search(r_tup[0], l_tup[0]) is not None:
                __match_ls += [r_tup]
        # In reference ontology but not in local onto to be FALSE NEGATIVE
        if len(__match_ls) == 0:
            fn_match_ls += [r_tup]

    # Calculate True +ve
    tp = len(tp_exact_match_ls) + len(tp_subset_match_ls)

    # Calculate True +ve based on exact string matches
    tp_exact = len(tp_exact_match_ls)
    tp_exact_diff_type = len([r for r in tp_exact_match_ls if not r[1]])    # Where different types
    tp_exact_same_type = len([r for r in tp_exact_match_ls if r[1]])        # Where same type

    # Calculate True +ve based on subset string matches
    tp_subset = len(tp_subset_match_ls)
    tp_subset_diff_type = len([r for r in tp_subset_match_ls if not r[1]])  # Where different types
    tp_subset_same_type = len([r for r in tp_subset_match_ls if r[1]])      # Where same type

    # Calculate False +ve and -ve
    fp = len(fp_match_ls)
    fn = len(fn_match_ls)

    print('No. of True +ve: {}'.format(tp))
    print('\tBy exact string match: {}'.format(tp_exact))
    print('\t\tOf which both local and reference ontologies have the same type: {}'.format(tp_exact_same_type))
    print('\t\tOf which both local and reference ontologies have different types: {}'.format(tp_exact_diff_type))
    print('\tBy subset Regex match: {}'.format(tp_subset))
    print('\tbased on thresholds - min length {} and max char length difference {}'.format(min_len, max_len_diff))
    print('\t\tOf which both local and reference ontologies have the same type: {}'.format(tp_subset_same_type))
    print('\t\tOf which both local and reference ontologies have different types: {}'.format(tp_subset_diff_type))
    print('No. of False +ve: {}'.format(fp))
    print('No. of False -ve: {}'.format(fn))

    # Calculate precision, recall and f1 score while handing div by 0 error
    precision = tp / (tp + fn) if (tp + fn) != 0 else .0
    recall = tp / (tp + fp) if (tp + fp) != 0 else .0
    f1 = tp / (tp + .5 * (fp + fn)) if (fp + fn) != 0 else .0

    print('Precision: {}'.format(precision))
    print('Recall: {}'.format(recall))
    print('F1 score: {}'.format(f1))

    # Analyse by types where match is find to determine appropriate equivalence to define

    # Extract local and reference onto types for each exact match result
    print('Exact match - different types exist:')
    print(list(set([(tup[2][1], tup[3][1]) for tup in tp_exact_match_ls])))

    # Extract local and reference onto types for each exact match result
    print('Subset match - different types exist:')
    print(list(set([(tup[2][1], tup[3][1]) for tup in tp_subset_match_ls])))

    print('TRUE +VE exact match listings:')
    for tup in tp_exact_match_ls:
        print('\t', tup)
    print('TRUE +VE subset match listings:')
    for tup in tp_subset_match_ls:
        print('\t', tup)

    # BUILD EQUIVALENCE TO THE TWO ONTOLOGIES
    print('Read in the refrence and local files as RDF graphs...', end='\r')
    # Load the local and reference ontologies as RDFLib graph
    ref_g = rdflib.Graph().parse(ref_file_path)
    loc_g = rdflib.Graph().parse(loc_file_path)

    # Union the two graphs
    print('Union the two RDF graphs...', end='\r')
    uni_g = ref_g + loc_g

    # Prefix
    aa = Namespace('http://www.city.ac.uk/ds/inm713/aaron_altrock#')
    uni_g.bind('aa', aa)

    # Equivalence only graph
    print('Create a new RDF graph for the equivalent class and property triples...', end='\r')
    eqi_g = rdflib.Graph()
    eqi_g.bind('aa', aa)

    # For each match result, construct equivalence
    for len_diff, is_diff_type, loc_tup, ref_tup in tp_exact_match_ls + tp_subset_match_ls:
        print('Constructing equivalence between {}/{} and {}/{}...'.format(loc_tup[2],
                                                                        loc_tup[1],
                                                                        ref_tup[2],
                                                                        ref_tup[1]), end='\r')
        loc_type = loc_tup[1]
        ref_type = ref_tup[1]

        # Construct an equivalence
        # Class v Class
        if loc_type == 'class' and ref_type == 'class':
            # class in loc owl:equivalentClass in ref
            s = URIRef(loc_tup[2].iri)
            p = OWL.equivalentClass
            o = URIRef(ref_tup[2].iri)
            uni_g.add((s, p, o))
            eqi_g.add((s, p, o))

        # Class Individual v Class
        if loc_type == 'class_ind' and ref_type == 'class':
            # class in loc owl:equivalentClass in ref
            s = URIRef(ref_tup[2].iri)
            p = OWL.equivalentClass
            o = URIRef(loc_tup[2].iri)
            uni_g.add((s, p, o))
            eqi_g.add((s, p, o))

        # Class Individual v Class Individual
        if loc_type == 'class_ind' and ref_type == 'class_ind':
            # class in loc owl:sameAs in ref
            s = URIRef(loc_tup[2].iri)
            p = OWL.sameAs
            o = URIRef(ref_tup[2].iri)
            uni_g.add((s, p, o))
            eqi_g.add((s, p, o))

        # Class v Object Property
        if loc_type == 'class' and ref_type == 'obj_prop':
            # object in ref owl:equivalentProperty class in local
            s = URIRef(ref_tup[2].iri)
            p = OWL.equivalentProperty
            o = URIRef(loc_tup[2].iri)
            uni_g.add((s, p, o))
            eqi_g.add((s, p, o))

        # Class Individual v Object Property
        if loc_type == 'class_ind' and ref_type == 'obj_prop':
            # object in ref owl:equivalentProperty class individual in local
            s = URIRef(ref_tup[2].iri)
            p = OWL.equivalentProperty
            o = URIRef(loc_tup[2].iri)
            uni_g.add((s, p, o))
            eqi_g.add((s, p, o))

    # Save extended graph to Turtle format
    uni_g.serialize(destination='2.5_oa1_union_g.ttl', format='ttl')
    print('Saved the unioned graph to 2.5_oa1_union_g.ttl.')
    eqi_g.serialize(destination='2.5_oa1_equivalence_g.ttl', format='ttl')
    print('Saved the equivalence triples to 2.5_oa1_equivalence_g.ttl.')

    # Save extended graph to OWL format
    uni_g.serialize(destination='2.5_oa1_union_g.owl.xml', format='xml')
    print('Saved the unioned graph to 2.5_oa1_union_g.owl.xml.')
    eqi_g.serialize(destination='2.5_oa1_equivalence_g.owl.xml', format='xml')
    print('Saved the equivalence triples to 2.5_oa1_equivalence_g.owl.xml.')

    print('END')


if __name__ == '__main__':
    main()
