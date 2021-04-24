import re
from nltk.corpus import stopwords
import spacy as sp

# For categories explode the delimited string into lists for each row
def __explode_str(s, delim=','):
    if len(s) > 0:
        return s.split(delim)
    elif s is None:
        return s
    else:
        return ''

"""
Helper func to clean up venue categories:
- lower case
- strip tokens shorter than three characters
- remove ' and' prefix in token
- substitute words
- split string to list by ' ' delimiter
- remove delimited list with repeated tokens, digits, punctuations & English common words
"""

# Cleaning function for pizza categories per the above description
def __post_cat_clean(df, stop_words_ls=[], cat_sub_words_ls=[]):
    print('Cleaning up venue categories...', end='\r')
    df_ls = []
    for i, row in df.iterrows():
        ls = row['categories']
        res_ls = []
        for token in ls:
            token = token.lower()
            if len(token) > 3:
                # If contains ',' strip
                token = re.sub(',', '', token)

                # If contains ' and' at beginning, strip
                token = re.sub('^ and ', '', token)

                # Substitute words
                for orig_token, replace_token in cat_sub_words_ls:
                    token = re.sub(orig_token, replace_token, token)

                # If there is a space, split string and remove duplicate tokens
                if re.search(' ', token) is not None:
                    __ls = list(set(token.split(' ')))
                    res_ls += __ls
                else:
                    res_ls += [token]

                # Strip punctuations and digits
                res_ls = [re.sub(r'\d', '', token) for token in res_ls]
                res_ls = [re.sub(r'\W', '', token) for token in res_ls]

                # Strip custom stop words
                res_ls = [token for token in res_ls if token not in stop_words_ls]

                # Remove token of zero length
                res_ls = [token for token in res_ls if len(token) > 0]

                # Remove general stop words
                gen_stp_wds_ls = list(stopwords.words('english'))
                res_ls = [token for token in res_ls if token not in gen_stp_wds_ls]

                # Remove duplicate tokens
                res_ls = list(set(res_ls))
        df_ls += [res_ls]
    return df_ls


# Clean up pizza categories
def clean_venue_cat(df, cat_stop_words_ls=[], cat_sub_words_ls=[]):
    # Categories: Exploding nested string into list
    cat_ls = [__explode_str(s) for s in df['categories']]
    df['categories'] = cat_ls

    # Categories: Remove duplicate category labels
    df['categories'] = __post_cat_clean(df, cat_stop_words_ls, cat_sub_words_ls)

    return df
