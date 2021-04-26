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
    print('TASK 2.4 SUBTASK SPARQL.1')
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

    # Prefix
    aa = Namespace('http://www.city.ac.uk/ds/inm713/aaron_altrock#')
    extend_g.bind('aa', aa)

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

    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
            TASK 2.4 SUBTASK SPARQL.2
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    print('\nTASK 2.4 SUBTASK SPARQL.2')
    # All restaurant details that sell pizzas without tomato (white pizza)
    # Logics:
    # - Must have ingredients or pizza type found; and
    # - No explicit ingredient of tomato; and
    # - Either white pizza type or not margherita (as it has tomato topping)
    query_str = """SELECT DISTINCT
        ?orgName
        ?venueName
        ?address
        ?cityName
        ?postcode
        ?stateName
        ?countryName
        ?categoryName
        ?menuItemName
        ?cost
        ?genericDishName
        ?toppingName
    WHERE {?venue a aa:venue .
        ?genericDish a aa:genericDish .

        ?venue aa:is_in_organisation ?org .
        ?org rdfs:label ?orgName .

        ?venue rdfs:label ?venueName .
        ?venue aa:sells ?menuItem .
        ?venue aa:locates_in ?city .

        ?city rdfs:label ?cityName .
        ?city aa:is_in_state ?state .
        ?state rdfs:label ?stateName .
        ?state aa:is_in_country ?country .
        ?country rdfs:label ?countryName .

        ?venue aa:postcode ?postcode .
        ?venue aa:address ?address .

        ?category aa:is_followed_in_style_by ?venue .
        ?category rdfs:label ?categoryName .

        ?menuItem rdfs:label ?menuItemName .
        ?menuItem aa:has_topping ?topping .
        ?menuItem aa:cost ?cost .

        ?genericDish aa:is_derived_from ?menuItem .
        ?genericDish rdfs:label ?genericDishName .

        ?menuItem aa:has_topping ?topping .
        ?topping rdfs:label ?toppingName .

        ?topping rdfs:label ?toppingName .
        FILTER ((?toppingName != "tomato") && ((?genericDishName = "white") || (?genericDishName != "margherita")))
    }
    """

    print('SPARQL.2 query - : All restaurant details that sell pizzas without tomato (white pizza)')
    print(query_str)

    res = extend_g.query(query_str)
    res.serialize('Task_2.4_SPARQL.2.csv', format='csv')
    print('Task 2.4 results saved to Task_2.4_SPARQL.2.csv')

    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
                TASK 2.4 SUBTASK SPARQL.3
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    print('\nTASK 2.4 SUBTASK SPARQL.3')
    # Average price of a Magherita pizza
    query_str = """SELECT ?genericDishName (avg(?cost) as ?avgCost) WHERE {
                ?menuItem a aa:menuItem .
                ?menuItem aa:cost ?cost .
                ?genericDish aa:is_derived_from ?menuItem  .
                ?genericDish rdfs:label ?genericDishName .
                FILTER (?genericDishName = "margherita")
                }
                """
    print('SPARQL.3 query - : Average price of a margherita pizza')
    print(query_str)
    res = extend_g.query(query_str)
    for row in res:
        print('Average price of a margherita pizza: {}'.format(row[1]))

    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
                    TASK 2.4 SUBTASK SPARQL.4
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    print('\nTASK 2.4 SUBTASK SPARQL.4')
    # No. of restaurants by city, sorted by state and number of restaurants
    # Logic:
    # Use venue rather than organisation as to count actual number of physical restaurants rather than chains
    # Filter out any unknown locations, names
    query_str = """SELECT ?stateName ?cityName (count(?venue) as ?venueCount)
                    { SELECT ?stateName ?cityName ?venue WHERE {
                        ?state a aa:state .
                        ?state rdfs:label ?stateName .
                        ?city rdfs:label ?cityName .
                        ?venue aa:locates_in ?city .
                        ?city aa:is_in_state ?state .
                        FILTER (!isBlank(?state) && !isBlank(?venue) && !isBlank(?city))
                        }
                    }
                GROUP BY ?stateName ?cityName
                ORDER BY ?stateName ?venueCount
                """
    print('SPARQL.4 query - : Per state, city, the count of venues')
    print(query_str)
    res = extend_g.query(query_str)
    res.serialize('Task_2.4_SPARQL.4.csv', format='csv')
    for s, c, n in res:
        print(s, c, n)

    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
                        TASK 2.4 SUBTASK SPARQL.5
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    print('\nTASK 2.4 SUBTASK SPARQL.5')
    # No. of restaurants with missing post code
    # Logic:
    # Use venue additional to organisation in case an organisation has more than one venues
    # Venue is 1:1 mapped to postcode
    query_str = """SELECT DISTINCT ?orgName ?venueName ?address ?cityName WHERE {
                    ?venue a aa:venue .
                    ?venue aa:is_in_organisation ?org .
                    ?org rdfs:label ?orgName .
                    ?venue rdfs:label ?venueName .
                    ?venue aa:postcode ?postcode .
                    ?venue aa:address ?address .
                    ?venue aa:locates_in ?city .
                    ?city rdfs:label ?cityName .
                    FILTER (isBlank(?postcode))
                    }
                    ORDER BY ?orgName ?address
                """
    print('SPARQL.5 query - : No. of restaurants with missing post code')
    print(query_str)
    res = extend_g.query(query_str)
    res.serialize('Task_2.4_SPARQL.5.csv', format='csv')
    for o, v, a, c in res:
        print(o, '\t', v, '\t', a, '\t', c)

    print('END')

if __name__ == '__main__':
    main()
