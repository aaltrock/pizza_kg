import pandas as pd
import numpy as np
import pprint as pp
import spacy as sp
import nltk
from nltk.corpus import stopwords
import en_core_web_sm
import random
import re


def make_pizza_types(src_df, cust_stp_wds_ls=[], top_n_cut_off=15):
    print('Creating pizza categories based on menu item names...', end='\r')
    random.seed(0)
    tokens_ls = list(src_df['menu item'].apply(nltk.tokenize.word_tokenize))
    tokens_ls = [x.lower() for y in tokens_ls for x in y]

    # Strip tokens with punctuation and digits
    tokens_ls = [tkn for tkn in tokens_ls if re.search(r'\d', tkn) is None]
    tokens_ls = [tkn for tkn in tokens_ls if re.match(r'\W', tkn) is None]

    # Remove general stop words
    gen_stp_wds_ls = list(stopwords.words('english'))
    tokens_ls = [tkn for tkn in tokens_ls if tkn not in gen_stp_wds_ls]

    # Remove customised stop words
    tokens_ls = [tkn for tkn in tokens_ls if tkn not in cust_stp_wds_ls]

    # Turn to data frame to summarise by count
    df = pd.DataFrame(tokens_ls, columns=['menu_item'])
    df['freq'] = [1] * df.shape[0]
    df = df.groupby('menu_item').count().reset_index().sort_values(by='freq', ascending=False)
    df.reset_index(inplace=True)

    # Based on frequency, keep menu item as the pizza category name for top n freq cases, otherwise 'Others' category
    cat_ls = []
    for i, row in df.iterrows():
        if i < top_n_cut_off:
            cat_ls += [row['menu_item']]
        else:
            cat_ls += ['Others']
    df['pizza_cat'] = cat_ls

    # Create a mapping dictionary
    cat_ls = list(set(cat_ls))      # Distinct set of pizza type
    print('Pizza categories:')
    pp.pprint(cat_ls)

    def get_pizza_type(menu_item, stop_words_ls, cat_ls):
        __menu_item = menu_item.lower()
        # If menu item has no name for pizza or only called 'pizza' then call 'generic'
        if menu_item is None or menu_item == 'pizza':
            return 'generic'
        else:
            # Break down to each word then match against pizza category name, return matches
            menu_item_tkn_ls = nltk.tokenize.word_tokenize(__menu_item)

            menu_item_tkn_ls = [tkn for tkn in menu_item_tkn_ls if re.search(r'\d', tkn) is None]
            menu_item_tkn_ls = [tkn for tkn in menu_item_tkn_ls if re.match(r'\W', tkn) is None]

            # Remove stop words
            menu_item_tkn_ls = [tkn for tkn in menu_item_tkn_ls if tkn not in stop_words_ls]

            # Pizza categories if found a match to pizza name
            type_ls = [cat for cat in cat_ls if cat in menu_item_tkn_ls]

            # Remove duplicate categories, if any
            type_ls = list(set(type_ls))

            # Re-check to remove stop words after merging back to the main data frame
            type_ls = [cat for cat in type_ls if cat not in stop_words_ls]

            # Where there is another category other than 'generic' remove 'generic'
            if len(type_ls) > 1 and 'generic' in type_ls:
                type_ls = [cat for cat in type_ls if cat != 'generic']

        return type_ls

    # For each menu item, tokenize, remove stop words to match with pizza categories
    src_df['pizza_cat'] = src_df.apply(lambda r: get_pizza_type(r['menu item'], cust_stp_wds_ls, cat_ls), axis=1)

    # Impute any menu items not categorised
    src_df['pizza_cat'] = [ls if len(ls) > 0 else ['others'] for ls in src_df['pizza_cat']]

    return src_df
