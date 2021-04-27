"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
TASK 2.5 SUBTASK 2 MAIN SCRIPT
By Aaron Altrock
Note: where external codes are used, these are referenced at the corresponding 
locations
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
import owlready2 as rdy
import logging
from enum import Enum

if __name__ == '__main__':
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
                TASK 2.5 SUBTASK OA.2
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    print('TASK 2.5 SUBTASK OA.2\n')
    # Adapted from source: E.Jiménez - Ruiz, “INM713 Semantic Web Technologies and Knowledge
    # Graphs Laboratory 5: Modelling OWL 2 Ontologies with Protégé, [Online]”
    file_path = '2.2_protege_pizza_ontology.owl.xml'
    onto = rdy.get_ontology(file_path)
    onto.load()
    with onto:
        rdy.sync_reasoner_hermit(infer_property_values=True)
    incon_res = list(onto.inconsistent_classes())
    print('Ontology {} found {} class or property inconsistencies:'.format(file_path, len(incon_res)))
    for incon_cls in incon_res:
        print(incon_cls)

    # Source: J.-B. Lamy, “Docs - Inconsistent classes and ontologies,” [Online].
    # Available: https://owlready2.readthedocs.io/en/latest/reasoning.html?highlight=inconsistent#inconsistent-classes-and-ontologies.
    for c in onto.classes():
        for rdy.Nothing in c.equivalent_to:
            print('Inconsistent: owl:Nothing in {}.equivalent_to'.format(c.name))

    file_path = 'pizza.owl'
    onto = rdy.get_ontology(file_path)
    onto.load()
    with onto:
        rdy.sync_reasoner_hermit(infer_property_values=True)
    incon_res = list(onto.inconsistent_classes())
    print('Ontology {} found {} class or property inconsistencies:'.format(file_path, len(incon_res)))
    for incon_cls in incon_res:
        print(incon_cls)

    # Source: J.-B. Lamy, “Docs - Inconsistent classes and ontologies,” [Online].
    # Available: https://owlready2.readthedocs.io/en/latest/reasoning.html?highlight=inconsistent#inconsistent-classes-and-ontologies.
    for c in onto.classes():
        for rdy.Nothing in c.equivalent_to:
            print('Inconsistent: owl:Nothing in {}.equivalent_to'.format(c.name))

    file_path = '2.4_sparql1_g.owl.xml'
    onto = rdy.get_ontology(file_path)
    onto.load()
    with onto:
        rdy.sync_reasoner_hermit(infer_property_values=True)
    incon_res = list(onto.inconsistent_classes())
    print('Ontology {} found {} class or property inconsistencies:'.format(file_path, len(incon_res)))
    for incon_cls in incon_res:
        print(incon_cls)

    # Source: J.-B. Lamy, “Docs - Inconsistent classes and ontologies,” [Online].
    # Available: https://owlready2.readthedocs.io/en/latest/reasoning.html?highlight=inconsistent#inconsistent-classes-and-ontologies.
    for c in onto.classes():
        for rdy.Nothing in c.equivalent_to:
            print('Inconsistent: owl:Nothing in {}.equivalent_to'.format(c.name))

    file_path = '2.5_oa1_union_g.owl.xml'
    onto = rdy.get_ontology(file_path)
    onto.load()
    with onto:
        rdy.sync_reasoner_hermit(infer_property_values=True)
    incon_res = list(onto.inconsistent_classes())
    print('Ontology {} found {} class or property inconsistencies:'.format(file_path, len(incon_res)))
    for incon_cls in incon_res:
        print(incon_cls)

    # Source: J.-B. Lamy, “Docs - Inconsistent classes and ontologies,” [Online].
    # Available: https://owlready2.readthedocs.io/en/latest/reasoning.html?highlight=inconsistent#inconsistent-classes-and-ontologies.
    for c in onto.classes():
        for rdy.Nothing in c.equivalent_to:
            print('Inconsistent: Nothing in {}.equivalent_to'.format(c.name))

    print('END')


    # """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    #                 TASK 2.5 SUBTASK OA.2.b
    # """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    # # Reasoning including the generated RDF data, create a query to return the pizza with the type pizza:MetaPizza
    #
    # # Created ontologies '2.4_sparql1_g.ttl' and aligned ontology '2.5_oa1_union_g.ttl'
    # # both with data did not return any inconsistencies.
    #
    # # Created ontology:
    #
    # #

    print('END')
