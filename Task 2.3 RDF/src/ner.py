# Named Entity Recognition (NER)

import pandas as pd
import spacy as sp
import nltk
from nltk.corpus import stopwords
import en_core_web_sm
import random
from spacy.util import minibatch
from spacy.training import Example
import re


def run_ner(src_df, trn_data_file_nm, sheet_nm):
    # Set random seed
    random.seed(0)

    label_nm = 'TOPPING'
    train_iter_nr = 50  # No. of training iterations
    batch_sz = 2

    # Load pre-trained library
    nlp = sp.load('en_core_web_sm')

    # Load NER pipeline component
    ner = nlp.get_pipe('ner')

    # Load NLTK files Punkt sentence tokeniser and part of speech tagger
    nltk.download('punkt')
    nltk.download('averaged_perceptron_tagger')

    # Load Spacy
    nlp = en_core_web_sm.load()

    # Load pre-trained Spacy model
    # NOTE: In the terminal run: python -m spacy download en_core_web_sm to download pre-trained model
    nlp = sp.load('en_core_web_sm')

    # Training data for NER of food items
    trn_data_df = pd.read_excel(trn_data_file_nm, sheet_name=sheet_nm, engine='openpyxl')

    # Explode the string of position indexes for each sample sentence to list of tuples of indexes
    trn_data_df['pos_labels'] = [val if not pd.isna(val) else None for val in trn_data_df['pos_labels']]
    trn_data_df['labels'] = [pos_str.split(';') if pos_str is not None else None for pos_str in trn_data_df['pos_labels']]
    trn_data_df['labels'] = [[tuple([int(val) for val in pos.split(',')] + [label_nm]) for pos in pos_ls]
                             if pos_ls is not None else [] for pos_ls in trn_data_df['labels']]

    # Compile training data set
    trn_data_ls = trn_data_df.apply(lambda row: (row['text_corpus'], {'entities': row['labels']}), axis=1)

    # Run training on spaCy NER model
    # Add the new label to ner
    ner.add_label(label_nm)

    # Resume training from pre-trained model
    optimizer = nlp.resume_training()
    move_names = list(ner.move_names)

    # List of pipes you want to train
    pipe_exceptions = ['ner', 'trf_wordpiecer', 'trf_tok2vec']

    # List of pipes which should remain unaffected in training
    other_pipes = [pipe for pipe in nlp.pipe_names if pipe not in pipe_exceptions]

    # Customised based on source: https://www.machinelearningplus.com/nlp/training-custom-ner-model-in-spacy/
    # Customised additionally to make compatible to spaCy v3.0 source: https://spacy.io/api/data-formats#dict-input
    with nlp.disable_pipes(*other_pipes):
        for i, iteration in enumerate(range(train_iter_nr)):
            print('Training under iteration: {}...'.format(i), end='\r', flush=True)
            # shuffling examples  before every iteration
            random.shuffle(trn_data_ls)
            losses = {}
            batches = minibatch(trn_data_ls, size=batch_sz)
            for batch in batches:
                # For each element in batch train NLP language model
                for text, annotation in batch:
                    doc = nlp.make_doc(text)
                    example = Example.from_dict(doc, annotation)
                    nlp.update([example], drop=.5, losses=losses)
                    # Print out details only at first round
                    if i == 0:
                        print('text: {}'.format(text))
                        print('annotation: {}'.format(annotation))
                        print('losses: {}'.format(losses))

    # Apply NLTK and Spacy NER to the source data frame
    # NER by NLTK over item description text corpora
    def prepare_text_nltk(txt):
        if txt is not None:
            # Source: https://towardsdatascience.com/named-entity-recognition-with-nltk-and-spacy-8c4a7d88e7da
            tokens = nltk.word_tokenize(text=txt)
            sent = nltk.pos_tag(tokens)
            return sent
        else:
            return None

    src_df['nltk_ner_init'] = src_df['item description'].apply(prepare_text_nltk)

    # NER by Spacy over item description text corpora
    def ner_spacy(txt):
        if txt is not None:
            # Source: https://towardsdatascience.com/named-entity-recognition-with-nltk-and-spacy-8c4a7d88e7da
            doc = nlp(txt)
            return [(tkn.text, tkn.label_) for tkn in doc.ents]

    src_df['spacy_ner_init'] = src_df['item description'].apply(ner_spacy)

    return src_df, nlp


# Post NER cleansing for pizza topping entity tags
def clean_topping_ner(src_df, stop_words_ls=[]):
    print('Cleaning topping entities...', end='\r')
    # Load spaCy model to lemmatise later
    spcy = sp.load('en_core_web_sm')

    # Set lower case to all tokens
    def to_lower(ls):
        if ls is not None:
            return [(tkn.lower(), tag) for tkn, tag in ls]
        else:
            return None

    print('Set all entity tokens to lower case...', end='\r')
    src_df['spacy_ner_clean'] = src_df['spacy_ner_init'].apply(to_lower)

    # lemmatisation
    def to_lemma(ls, nlp):
        if ls is not None:
            res_ls = []
            for tkn, tag in ls:
                sen = nlp(tkn)
                for __tkn in sen:
                    res_ls += [(__tkn.lemma_, tag)]
            return res_ls
        else:
            return None

    print('Lemmatise entity tokens...', end='\r')
    src_df['spacy_ner_clean'] = src_df['spacy_ner_clean'].apply(lambda ls: to_lemma(ls, spcy))

    # Remove English stop words
    def rm_stop_words(ls, gen_stp_wds_ls):
        if ls is not None:
            res_ls = [(tkn, tag) for tkn, tag in ls if tkn not in gen_stp_wds_ls]
            return res_ls
        else:
            return None

    print('Remove English stop words...', end='\r')
    gen_stp_wds_ls = list(stopwords.words('english'))
    src_df['spacy_ner_clean'] = src_df['spacy_ner_clean'].apply(lambda ls: rm_stop_words(ls, gen_stp_wds_ls))

    # Remove any tokens containing digits (e.g. weight)
    def rm_non_alpha_tokens(ls):
        if ls is not None:
            res_ls = [(tkn, tag) for tkn, tag in ls if re.search(r'\d', tkn) is None]
            res_ls = [(tkn, tag) for tkn, tag in res_ls if re.match(r'\W', tkn) is None]
            return res_ls
        else:
            return None

    print('Remove tokens containing non-alpha characters...', end='\r')
    src_df['spacy_ner_clean'] = src_df['spacy_ner_clean'].apply(rm_non_alpha_tokens)

    # Remove tokens for exactly e.g. 'pizza' or 'topping' for a given stop words list
    def rm_pizza_token(ls, __stop_words_ls):
        if ls is not None:
            return [(tkn, tag) for tkn, tag in ls if tkn not in __stop_words_ls]
        else:
            return None
    print('Remove tokens as "pizza" or "topping"...', end='\r')
    src_df['spacy_ner_clean'] = src_df['spacy_ner_clean'].apply(lambda ls: rm_pizza_token(ls, stop_words_ls))

    return src_df
