"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
TASK 2.6 MAIN SCRIPT
By Aaron Altrock
Note: where external codes are used, these are referenced at the corresponding 
locations
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
from gensim.models import KeyedVectors

# Adapted from source: E. Jiménez-Ruiz, “GitHub city-knowledge-graph repository lab 9,” [Online].
# Available: https://github.com/city-knowledge-graphs/python/tree/main/lab9.

embedding_path = './Standalone_0.1/output_embedding/'
wv = KeyedVectors.load(embedding_path + '2.5_oal.embedding', mmap='r')


vector = wv['pizza']  # Get numpy vector of a word
print(vector)


#cosine similarity
similarity = wv.similarity('pizza', 'http://www.co-ode.org/ontologies/pizza/pizza.owl#Pizza')
print(similarity)

similarity = wv.similarity('http://www.co-ode.org/ontologies/pizza/pizza.owl#Margherita', 'margherita')
print(similarity)





#Most similar cosine similarity
result = wv.most_similar(positive=['margherita', 'pizza'])
print(result)

#Most similar entities: cosmul
result = wv.most_similar_cosmul(positive=['margherita'])
print(result)



#
#
# wv = KeyedVectors.load("pizza.embeddings", mmap='r')
#
# vector = wv['pizza']  # Get numpy vector of a word
# print(vector)
#
# for key in wv.wv.vocab:
#     print(key)
#
# similarity = wv.similarity('pizza', 'giuseppe')
#
# print(similarity)
#
#
# similarity = wv.similarity('ham', 'mushroom')
#
# print(similarity)
#
#
#
# similarity = wv.similarity('tomato', 'pizza')
# print(similarity)
#
#
# similarity = wv.similarity('http://www.co-ode.org/ontologies/pizza/pizza.owl#TomatoTopping', 'http://www.co-ode.org/ontologies/pizza/pizza.owl#Pizza')
# print(similarity)
#
# similarity = wv.similarity('http://www.co-ode.org/ontologies/pizza/pizza.owl#TomatoTopping', 'http://www.co-ode.org/ontologies/pizza/pizza.owl#Margherita')
# print(similarity)
#
#
# similarity = wv.similarity('pizza', 'http://www.co-ode.org/ontologies/pizza/pizza.owl#Pizza')
# print(similarity)
#
#
# result = wv.most_similar_cosmul(positive=['margherita'])
#
# most_similar_key, similarity = result[0]  # look at the first match
#
# print(f"{most_similar_key}: {similarity:.4f}")
# print(result)
#
# #https://radimrehurek.com/gensim/models/keyedvectors.html
