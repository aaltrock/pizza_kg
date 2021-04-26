"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
TASK 2.5 SUBTASK 2 MAIN SCRIPT
By Aaron Altrock
Note: where external codes are used, these are referenced at the corresponding 
locations
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
import owlready2 as rdy
import logging
from enum import Enum

# Source: E.Jiménez - Ruiz, “INM713 Semantic Web Technologies and Knowledge
# Graphs Laboratory 5: Modelling OWL 2 Ontologies with Protégé, [Online]”
class Reasoner(Enum):
    HERMIT = 0  # Not really adding the right set of entailments
    PELLET = 1  # Slow for large ontologies
    STRUCTURAL = 2  # Basic domain/range propagation
    NONE = 3  # No reasoning

class Onto(object):

    def __init__(self, file_path):
        logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.DEBUG)
        self.file_path = file_path
        self.onto = rdy.get_ontology(file_path)
        self.class_nr = None
        self.class_unsat_nr = None

    def reason_onto(self, reasoner=Reasoner.NONE, memory_java='10240'):
        self.onto.load()

        # Work out the number of classes in ontology
        self.class_nr = len(list(self.onto.classes()))

        # Set memory and logging level
        rdy.reasoning.JAVA_MEMORY = memory_java
        rdy.set_log_level(9)

        if reasoner == Reasoner.PELLET:
            try:
                with self.onto:  # it does add inferences to ontology

                    # Is this wrt data assertions? Check if necessary
                    # infer_property_values = True, infer_data_property_values = True
                    logging.info("Classifying ontology with Pellet...")
                    rdy.reasoning.sync_reasoner_pellet()  # it does add inferences to ontology

                    self.class_unsat_nr = len(list(self.onto.inconsistent_classes()))
                    logging.info("Ontology successfully classified.")
                    if self.class_unsat_nr > 0:
                        logging.warning("There are " + str(self.class_unsat_nr) + " unsatisfiabiable classes.")
            except:
                logging.info("Classifying with Pellet failed.")

        elif reasoner == Reasoner.HERMIT:

            try:
                with self.onto:  # it does add inferences to ontology
                    logging.info("Classifying ontology with HermiT...")
                    rdy.reasoning.sync_reasoner()  # HermiT doe snot work very well....

                    unsat = len(list(self.onto.inconsistent_classes()))
                    logging.info("Ontology successfully classified.")
                    if unsat > 0:
                        logging.warning("There are " + str(unsat) + " unsatisfiabiable classes.")

            except:
                logging.info("Classifying with HermiT failed.")


if __name__ == '__main__':
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
                TASK 2.5 SUBTASK OA.2
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    print('TASK 2.5 SUBTASK OA.2\n')

    # 1) created ontology - extended ontology from task 2.4
    file_path = '2.4_sparql1_g.ttl'
    local_onto = Onto(file_path)
    local_onto.reason_onto(reasoner=Reasoner.PELLET)

    # 2) pizza.owl reference ontology
    file_path = 'pizza.owl'
    ref_onto = Onto(file_path)
    ref_onto.reason_onto(reasoner=Reasoner.PELLET)

    # 3) aligned ontology with data
    file_path = '2.5_oa1_union_g.ttl'
    union_onto = Onto(file_path)
    union_onto.reason_onto(reasoner=Reasoner.PELLET)

    # 4) computed alignment (without the data)
    file_path = '2.5_oa1_equivalence_g.ttl'
    algn_onto = Onto(file_path)
    algn_onto.reason_onto(reasoner=Reasoner.PELLET)

    print('Created ontology from task 2.4 2.4_sparql1_g.ttl: {} classes; {} unsatisfiable classes;'
          .format(local_onto.class_nr, local_onto.class_unsat_nr))

    print('Reference ontology pizza.owl: {} classes; {} unsatisfiable classes;'
          .format(ref_onto.class_nr, ref_onto.class_unsat_nr))

    print('Aligned ontology (with data) ontology pizza.owl: {} classes; {} unsatisfiable classes;'
          .format(union_onto.class_nr, union_onto.class_unsat_nr))

    print('Alignment ontology (without data) ontology pizza.owl: {} classes; {} unsatisfiable classes;'
          .format(algn_onto.class_nr, algn_onto.class_unsat_nr))


    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
                    TASK 2.5 SUBTASK OA.2.a
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    # To be performed in Protégé for pizza.owl that returned three unsatisfiable classes.

    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
                    TASK 2.5 SUBTASK OA.2.b
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    # Reasoning including the generated RDF data, create a query to return the pizza with the type pizza:MetaPizza

    # Created ontologies '2.4_sparql1_g.ttl' and aligned ontology '2.5_oa1_union_g.ttl'
    # both with data did not return any inconsistencies.

    # Created ontology:

    #

    print('END')
