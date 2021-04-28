"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
TASK 2.5 SUBTASK 2 MAIN SCRIPT
By Aaron Altrock
Note: where external codes are used, these are referenced at the corresponding 
locations
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
import owlready2 as rdy
import logging
from enum import Enum


# Source: J.-B. Lamy, “Docs - Inconsistent classes and ontologies,” [Online].
# Available: https://owlready2.readthedocs.io/en/latest/reasoning.html?highlight=inconsistent#inconsistent-classes-and-ontologies
# Return inconsistencies using Hermit reasoner
def find_incon(onto, check_equivalent_nothing=True,
               print_res=True, debug=1, infer_property_values=True):

    try:
        with onto:
            rdy.sync_reasoner_hermit(debug=debug, infer_property_values=infer_property_values)
        incon_res_ls = list(onto.inconsistent_classes())
        print('Ontology found {} classes or property inconsistencies:'.format(len(incon_res_ls)))
        if print_res:
            for incon_cls in incon_res_ls:
                print(incon_cls)
    except Exception as e:
        print('ERROR: ' + str(type(e)))
    finally:
        incon_res_ls = []

    return incon_res_ls


if __name__ == '__main__':
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
                TASK 2.5 SUBTASK OA.2
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    print('TASK 2.5 SUBTASK OA.2\n')
    # Adapted from source: E.Jiménez - Ruiz, “INM713 Semantic Web Technologies and Knowledge
    # Graphs Laboratory 5: Modelling OWL 2 Ontologies with Protégé, [Online]”
    # Reference ontology
    file_path = 'pizza.owl'
    print('\nReference ontology: {}'.format(file_path))
    ref_onto = rdy.get_ontology(file_path)
    ref_onto.load()
    # ref_onto_res_ls, ref_cls_equi_nothing_ls = find_incon(ref_onto)
    ref_onto_res_ls = find_incon(ref_onto)

    file_path = '2.2_protege_pizza_ontology.owl.xml'
    print('\nCreated ontology (Task 2.2) - without pizza types: {}'.format(file_path))
    created_protege_onto = rdy.get_ontology(file_path)
    created_protege_onto.load()
    # created_protege_onto_res_ls, created_protege_cls_equi_nothing_ls = find_incon(created_protege_onto)
    created_protege_onto_res_ls = find_incon(created_protege_onto)

    file_path = '2.3_rdf2_python_int_uri_g.owl.xml'
    print('\nCreated ontology (Task 2.3) with pizza types and other entities: {}'.format(file_path))
    created_enrich_onto = rdy.get_ontology(file_path)
    created_enrich_onto.load()
    # created_enrich_onto_res_ls, created_enrich_cls_equi_nothing_ls = find_incon(created_enrich_onto)
    created_enrich_onto_res_ls = find_incon(created_enrich_onto)

    # computed alignment
    file_path = '2.5_oa1_union_g.owl.xml'
    print('\nReference ontology: {}'.format(file_path))
    algn_onto = rdy.get_ontology(file_path)
    algn_onto.load()
    # algn_onto_res_ls, algn_cls_equi_nothing_ls = find_incon(algn_onto)
    algn_onto_enrich_onto_res_ls = find_incon(algn_onto)

    print('END')


    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
                    TASK 2.5 SUBTASK OA.2.b
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    # Create a query to return the pizza with type pizza:MeatyPizza
    print('\nTASK 2.5 SUBTASK OA.2.b')
    # Meaty pizza

    # Helper func to perform reasoning and extract classes
    def extract_infer(onto, search_class_str):
        # Hermit reasoner
        with onto:
            rdy.sync_reasoner_hermit()

        parent_dct = {}
        instances_dct = {}
        children_dct = {}
        # Get inferred classes and pack into dictionaries for parents, instances and children
        for cl in onto.classes():
            # Parents
            parent_dct.update({str(cl): onto.get_parents_of(cl)})

            # Instances
            instances_dct.update({str(cl): onto.get_instances_of(cl)})

            # Children
            children_dct.update({str(cl): onto.get_children_of(cl)})

        # Get pizzaMeatyPizza parents
        print('Parents of ' + search_class_str)
        if parent_dct.get(search_class_str) is not None:
            for parent in parent_dct.get(search_class_str):
                print(parent)
        else:
            print('None returned')

        # Get instances of pizzaMeatyPizza - expected no return as there were no instances
        print('\nInstances of ' + search_class_str)
        if instances_dct.get(search_class_str) is not None:
            for inst in instances_dct.get(search_class_str):
                print(inst)
        else:
            print('None returned')

        # Get pizzaMeatyPizza children
        print('\nChildren of ' + search_class_str)
        if children_dct.get(search_class_str) is not None:
            for chd in children_dct.get(search_class_str):
                print(chd)
        else:
            print('None returned')

        return parent_dct, instances_dct, children_dct


    # Run over the cleaned up reference ontology pizza.owl
    file_path = 'pizza_cleaned.owl'
    print('\nReference ontology: {}'.format(file_path))
    ref_onto = rdy.get_ontology(file_path)
    ref_onto.load()

    _, _, _ = extract_infer(ref_onto, 'pizza.MeatyPizza')

    # Run over the generated data
    file_path = '2.2_protege_pizza_ontology.owl.xml'
    print('\nGenerated data: {}'.format(file_path))
    ref_onto = rdy.get_ontology(file_path)
    ref_onto.load()

    _, _, _ = extract_infer(ref_onto, 'pizza.MeatyPizza')

    # Run over the data
    file_path = '2.3_rdf2_python_int_uri_g.owl.xml'
    print('\nGenerated data: {}'.format(file_path))
    ref_onto = rdy.get_ontology(file_path)
    ref_onto.load()

    _, _, _ = extract_infer(ref_onto, 'pizza.MeatyPizza')
    _, _, _ = extract_infer(ref_onto, 'genericDish.meat')


    print('END')
