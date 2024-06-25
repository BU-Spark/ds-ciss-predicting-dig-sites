""" Mass creates randomized test sites that are predicted to be actual ones """
import warnings
from pathlib import Path
from multiprocessing import Pool, cpu_count

import numpy as np
import pandas as pd
import xgboost as xgb
from sklearn.model_selection import train_test_split
from tqdm import tqdm

warnings.filterwarnings('ignore')

DATA_PATH = Path().cwd() / 'analysis' / 'data' if Path().cwd().name != 'analysis' else Path().cwd() / 'data'

def clean_waw(df: pd.DataFrame):
    """ Aggregates the WAW columns and returns a new dataframe with the wetness values """
    wcols = [col for col in df.columns if 'WAW' in col]
    waw = df[wcols + ['OBJECTID']]
    df.drop(columns=wcols, inplace=True)

    waw['Wetness'] = waw[waw.drop(['OBJECTID'], axis=1).columns].apply(
        lambda x: ''.join(x.dropna().astype(str)),
        axis=1
    )

    waw = waw[waw['Wetness'] != ''][['OBJECTID', 'Wetness']]
    waw['Wetness'] = waw['Wetness'].astype(float).astype(np.uint8)
    return pd.merge(df, waw, on='OBJECTID', how='inner')


def not_site_criteria(df: pd.DataFrame):
    """ Applies the criteria for a site to be considered a site """
    df.loc[(df['Elevation'] > 400), 'Is_Site'] = 0
    df.loc[(df['Elevation'] <= 400), 'Is_Site'] = 1
    # test.loc[(test['Elevation'] < 50), 'Is_Site'] = 0


    df.loc[(df['NEAR_DIST_Chert'] > 20000), 'Is_Site'] = 0
    df.loc[(df['NEAR_DIST_Coastal'] > 6000), 'Is_Site'] = 0
    # test.loc[(test['NEAR_DIST_Canals'] < 20000), 'Is_Site'] = 0
    # test.loc[(test['NEAR_DIST_River_Net'] < 20000), 'Is_Site'] = 0

    df['Is_Site'] = df['Is_Site'].astype(np.uint8)

    return df


def generate_random_mix(known_df, test_df, rng_mix=0.01, rng_seed=None):
    """ Generates a mix of random sites and actual sites """
    rng = np.random.default_rng(rng_seed)

    rng_selection = test_df[test_df['Is_Site'] == 0]
    rng_nums = rng.choice(
        a=rng_selection.index, 
        size=int(np.ceil(test_df['Is_Site'].value_counts()[0]*rng_mix)), # round up
        replace=False
    )

    # df_cut = df.drop(index=rng_nums) # pyright: ignore[reportArgumentType, reportCallIssue]

    return pd.concat([known_df, rng_selection.loc[rng_nums]], ignore_index=True)


def gen_model(train_df: pd.DataFrame, test_df: pd.DataFrame, cleaned_test: pd.DataFrame):
    """ Generates a model from the training data and returns the predictions """
    model = xgb.XGBClassifier(
        tree_method='hist',
        early_stopping_rounds=10,
    )

    train_df = generate_random_mix(train_df, test_df)

    x_train, x_test, y_train, y_test = train_test_split(
        train_df.drop(columns=['Is_Site']),
        train_df['Is_Site'],
        test_size=0.25,
        stratify=train_df['Is_Site']
    )

    model.fit(x_train, y_train, eval_set=[(x_test, y_test)], verbose=False)

    outcome = test_df.drop(columns=['Is_Site'])
    outcome['prediction'] = model.predict(outcome)

    linked = outcome.merge(cleaned_test[['OBJECTID', 'x', 'y']], left_index=True, right_index=True)

    return linked[(linked['y'] <= 43.57) & (linked['prediction'] == 1)]

if __name__ == "__main__":
    TEST_SHEET = 'test_points_extracted.xls'
    test_sites = pd.read_excel(DATA_PATH / TEST_SHEET, engine='calamine', dtype_backend='pyarrow')

    test_sites.drop(columns=[col for col in test_sites.columns if 'NEAR_FID' in col], inplace=True)

    if any('WAW' in col for col in test_sites.columns):
        test_cleaned = clean_waw(test_sites)

    else:
        test_cleaned = test_sites.copy()

    test_sites['Slope'] = test_sites['Slope'].astype('uint8[pyarrow]')
    test_sites['Wetness'] = test_sites['Wetness'].astype('uint8[pyarrow]')

    test_cleaned.dropna(inplace=True)

    known_sites = pd.read_excel(
        DATA_PATH / 'known_sites_augmented.xls',
        engine='calamine',
        dtype_backend='pyarrow'
    )

    known_sites.rename(columns={
            i: i.replace('sites_XYTableToPoint_', '') for i in known_sites.columns if 'XYTableToPoint' in i
        }, inplace=True)

    known_sites.rename(columns={
        'Elevation__Masl_': 'Elevation',
        'Dd_ns': 'y',
        'Dd_ew': 'x',
        }, inplace=True)

    known_sites.drop(
        columns=['Dd', 'Dms'] + [col for col in known_sites.columns if 'NEAR_FID' in col], 
        inplace=True
    )

    known_sites_cleaned = clean_waw(known_sites).drop(
        columns=[
            'Geographical_Region', 
            'Geographical_Location', 
            'Period_New', 
            'Site_Type'
        ]
    )

    known_sites_cleaned['Slope'] = known_sites_cleaned['Slope'].astype('uint8[pyarrow]')
    known_sites_cleaned['Wetness'] = known_sites_cleaned['Wetness'].astype('uint8[pyarrow]')

    cols = known_sites_cleaned.columns
    known_sites_cleaned = known_sites_cleaned[
        cols[:3].to_list() + [cols[-2]] + cols[3:-2].to_list() + [cols[-1]]
    ]

    # Needs to be forced as some values in Elevation_Raster are floats/doubles
    known_sites_cleaned['Elevation'] = known_sites_cleaned['Elevation'].astype('double[pyarrow]')
    known_sites_cleaned.Elevation.fillna(known_sites_cleaned.Elevation_Raster, inplace=True)
    known_sites_cleaned.Elevation.fillna(0, inplace=True)

    known_sites_cleaned.drop(columns=['Elevation_Raster'], inplace=True)

    known_sites_cleaned['Is_Site'] = 1

    known = known_sites_cleaned.drop(columns=['OBJECTID', 'x', 'y', 'Site_Name'])
    test = test_cleaned.drop(columns=['OBJECTID', 'x', 'y'])

    col_order = [
        'Elevation', 
        'Wetness', 
        'Temp', 
        'Slope', 
        'NEAR_DIST_Chert', 
        'NEAR_DIST_Canals', 
        'NEAR_DIST_River_Net',
        'NEAR_DIST_Coastal'
    ]

    known = known[col_order + ['Is_Site']]
    test = test[col_order]

    test.reset_index(drop=True, inplace=True)

    test = not_site_criteria(test)

    collection_df = pd.DataFrame(columns=list(test.columns) + ['OBJECTID', 'x', 'y'])

    with Pool(int(cpu_count()*1.5)) as p:
        PMAX = 5000

        with tqdm(total=PMAX, ncols=100, desc=f'Generating {PMAX} randomized simulations') as pbar:
            for i, result in enumerate(p.starmap(gen_model, [(known, test, test_cleaned)]*PMAX)):
                pbar.update()
                collection_df = pd.concat([collection_df, result], ignore_index=True)

    collection_df.to_parquet(DATA_PATH / 'mass_test.parquet', index=False)

    col_group = collection_df[['OBJECTID', 'prediction']].groupby('OBJECTID').sum()
    col_group.rename(columns={'prediction': 'count'}, inplace=True)

    collection_df.drop_duplicates(subset='OBJECTID', inplace=True)
    collection_df = collection_df.merge(col_group[['count']], left_on='OBJECTID', right_index=True)

    collection_df.to_parquet(DATA_PATH / 'mass_test_grouped.parquet', index=False)
