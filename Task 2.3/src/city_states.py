# Clean up City and State for data ETL
import pandas as pd


def clean(src_df, zip_rng_df):
    print('Cleaning up city and state fields...', end='\r')

    # States - backfill where it is not a valid state
    # remove invalid US states
    states_ls = ['AK', 'AL', 'AR', 'AS', 'AZ', 'CA', 'CO', 'CT', 'DC', 'DE', 'FL', 'FM', 'GA',
                 'GU', 'HI', 'IA', 'ID', 'IL', 'IN', 'KS', 'KY', 'LA', 'MA', 'MD', 'ME', 'MH',
                 'MI', 'MN', 'MO', 'MP', 'MS', 'MT', 'NC', 'ND', 'NE', 'NH', 'NJ', 'NM', 'NV',
                 'NY', 'OH', 'OK', 'OR', 'PA', 'PR', 'PW', 'RI', 'SC', 'SD', 'TN', 'TX', 'UT',
                 'VA', 'VI', 'VT', 'WA', 'WI', 'WV', 'WY']

    # Return state if valid, otherwise return None
    def __clean_state(st, st_ls):
        if st in st_ls:
            return st
        else:
            return None

    src_df['state'] = [__clean_state(st, states_ls) for st in src_df['state']]

    # If state is None, then try to back-fill with zip code
    def __impute_state(row, __zip_rng_df):
        state = None
        if row['state'] is not None:
            return row['state']
        elif row['postcode'] is not None:
            # Try to convert post code to integer then search for the state
            try:
                __postcode = int(row['postcode'])
                for i, z_row in __zip_rng_df.iterrows():
                    # If zip code within the range, then set state
                    if (__postcode >= z_row['Zip Min']) and (__postcode >= z_row['Zip Max']):
                        state = z_row['ST']
            # Return None if invalid post code
            except ValueError:
                state = None
            return state
        else:
            return None

    src_df['state'] = src_df.apply(lambda row: __impute_state(row, zip_rng_df), axis=1)

    # City - To change to City, State naming convention to ensure uniqueness
    def __make_city_state(row):
        if row['city'] is not None and row['state'] is not None:
            return row['city'] + ', ' + row['state']
        # If no state is found then add US
        elif row['city'] is not None and row['state'] is None:
            return row['city'] + ', US'
        # Return None if city name is not included
        else:
            return None

    src_df['city_state'] = src_df.apply(lambda row: __make_city_state(row), axis=1)

    return src_df
