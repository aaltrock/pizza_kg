"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
TASK 2.3 MAIN SCRIPT
By Aaron Altrock
Note: where external codes are used, these are referenced at the corresponding 
locations
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

import random
from src import int_triples, ext_triples


# Helper func to print a graph in Turtle format
def print_g(g):
    print(g.serialize(format='turtle').decode('utf-8'))


def main():
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
            TASK 2.3 SUBTASK RDF.2
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

    print('\nTASK 2.3 SUBTASK RDF.2')

    # Generate triples and add to two graphs
    # 1. graph with country, state and city info mapped to internal URI
    # 2. graph without country, state and city added for subtask RDF.3 to add external URIs
    src_df, clean_df, int_uri_g, ext_uri_g, aa = int_triples.make_g()

    # Save to Turtle .ttl file
    int_uri_g.serialize(destination='2.3_rdf2_python_int_uri_g.ttl', format='ttl')

    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
            TASK 2.3 SUBTASK RDF.3
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

    print('\nTASK 2.3 SUBTASK RDF.3')

    # With the graph generated from Task 2.3 RDF.2, to add triples relating to external URIs
    # Where external URIs not found, to create internal URIs to cover the gap
    ext_uri_g = ext_triples.make_ext_g(ext_uri_g, clean_df, aa)

    # Save to Turtle .ttl file
    ext_uri_g.serialize(destination='2.3_rdf3_python_ext_uri_g.ttl', format='ttl')

    print('END')


if __name__ == '__main__':
    # Set random seed
    random.seed(0)
    main()
