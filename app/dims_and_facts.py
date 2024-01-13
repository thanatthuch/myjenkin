from collections import namedtuple
from pathlib import Path
from typing import List
# import os

import numpy as np
import pandas as pd

# List of all tables used in the original database
TABLES = [
    "addresses",
    "birthdates",
    "cities",
    "countries",
    "cuisines",
    "districts",
    "food",
    "orders",
    "promos",
    "restaurants",
    "states",
    "users",
]

# Path to the directory where tables' CSV files are stored
TABLES_DIR_PATH = Path(__file__).parent / "tables"

# Structure holding initial database
MultiDimDatabase = namedtuple(
    "MultiDimDatabase",
    [
        "addresses",
        "birthdates",
        "cities",
        "countries",
        "cuisines",
        "districts",
        "food",
        "orders",
        "promos",
        "restaurants",
        "states",
        "users",
    ],
)
ReducedDatabase = namedtuple(
    "ReducedDatabase", ["orders", "users", "food", "promos", "restaurants", "addresses"]
)


# --- Task #1 ---
def load_tables(tables_dir_path: Path, tables: List[str]) -> List[pd.DataFrame]:
    dfs = []
    for table in tables:
        file_path = tables_dir_path / f"{table}.csv"
        if file_path.exists() and file_path.is_file():
            df = pd.read_csv(file_path)
            df = df.set_index([df.keys()[0]])
            dfs.append(df)

    return dfs


# --- Task # 2 ---
def reduce_dims(db: MultiDimDatabase) -> ReducedDatabase:
    #Addresss merge
    db_reduced = []
    df_addresses = pd.DataFrame(db.addresses)
    df_addresses = df_addresses.merge(
        db.districts, left_on='district_id', right_index=True, how='left')
    df_addresses = df_addresses.merge(
        db.cities, left_on='city_id', right_index=True, how='left')
    df_addresses = df_addresses.rename(
        columns={'name_x': 'district', 'name_y': 'city'})
    df_addresses = df_addresses.merge(
        db.states, left_on='state_id', right_index=True, how='left')
    df_addresses = df_addresses.merge(
        db.countries, left_on='country_id', right_index=True, how='left')
    df_addresses = df_addresses.rename(
        columns={'name_x': 'state', 'name_y': 'country'})
    df_addresses.drop(['district_id', 'city_id', 'state_id',
                    'country_id'], axis=1, inplace=True)

    df_addresses = df_addresses.astype(
        {'city': object, 'country': object, 'district': object, 'state': object, 'street': object})
    
    db.orders['ordered_at'] = pd.to_datetime(db.orders['ordered_at'], format='%Y-%m-%d %H:%M:%S')

    df_food = pd.DataFrame(db.food)
    df_food = df_food.rename(columns={'cuisine_id': 'cuisine'})
    df_food = df_food.astype({'name': object, 'cuisine': object, 'price': float})



    birthdates_df = pd.DataFrame(db.birthdates)
    birthdates_df.index.name = 'birthdate'



    users_df = pd.DataFrame(db.users)
    users_df = users_df.rename(columns={'birthdate_id': 'birthdate'})

    users_df = users_df.astype({'first_name': object, 'last_name': object})
    users_df['birthdate'] = pd.to_datetime(
        users_df['birthdate'], format='%d/%m/%Y')
    users_df['registred_at'] = pd.to_datetime(users_df['registred_at'])


    columns_list = ['country', 'state', 'city', 'district', 'street']
    df_addresses = df_addresses.reindex(columns=columns_list)
    db_reduced.append(df_addresses)

    for table in db[1:]:
        if table.index.name == 'food_id':
            db_reduced.append(df_food)
        elif table.index.name == 'birthdate_id':
            db_reduced.append(birthdates_df)
        elif table.index.name == 'user_id':
            db_reduced.append(users_df)
        else:
            db_reduced.append(table)

    pd.set_option('display.max_columns', None)
    pd.set_option('display.max_rows', None)

    return ReducedDatabase(
        addresses=db_reduced[0],
        food=db_reduced[6],
        orders=db_reduced[7],
        promos=db_reduced[8],
        restaurants=db_reduced[9],
        users=db_reduced[11],
    )

# --- Task #3 ---
def create_orders_by_meal_type_age_cuisine_table(db: ReducedDatabase) -> pd.DataFrame:
    create_orders = db.orders
    create_orders = create_orders.merge(db.food, left_on='food_id', right_index=True, how='left')
    create_orders = create_orders.merge(db.users, left_on='user_id', right_index=True, how='left')

    create_orders['ordered_at'] = pd.to_datetime(create_orders['ordered_at'])
    create_orders['meal_type'] = 'dinner'
    create_orders.loc[(create_orders['ordered_at'].dt.hour >= 6) & (create_orders['ordered_at'].dt.hour < 10), 'meal_type'] = 'breakfast'
    create_orders.loc[(create_orders['ordered_at'].dt.hour >= 10) & (create_orders['ordered_at'].dt.hour <= 16), 'meal_type'] = 'lunch'


    create_orders['birthdate'] = pd.to_datetime(create_orders['birthdate'], format='%d/%m/%Y')
    create_orders['user_age'] = 'old'
    create_orders.loc[(create_orders['birthdate'].dt.year >= 1995), 'user_age'] = 'young'
    create_orders.loc[(create_orders['birthdate'].dt.year >= 1970) & (create_orders['birthdate'].dt.year < 1995), 'user_age'] = 'adult'

    create_orders = create_orders.rename(columns={'cuisine': 'food_cuisine'})

    create_orders.drop(
        [
            'user_id', 
            'address_id', 
            'restaurant_id', 
            'food_id',
            'ordered_at', 
            'promo_id','name',
            'price', 
            'first_name', 
            'last_name', 
            'birthdate', 
            'registred_at'
        ], axis=1, inplace=True
    )

    create_orders = create_orders.astype({'food_cuisine': object})

    pd.set_option('display.max_columns', None)
    pd.set_option('display.max_rows', None)

    return create_orders


TABLES_SCHEMA = {
    "addresses": {"index": "address_id", "columns": ["district_id", "street"]},
    "birthdates": {"index": "birthdate_id", "columns": ["year", "month", "day"]},
    "cities": {"index": "city_id", "columns": ["name", "state_id"]},
    "countries": {"index": "country_id", "columns": ["name"]},
    "cuisines": {"index": "cuisine_id", "columns": ["name"]},
    "districts": {"index": "district_id", "columns": ["name", "city_id"]},
    "food": {"index": "food_id", "columns": ["name", "cuisine_id", "price"]},
    "orders": {
        "index": "order_id",
        "columns": [
            "user_id",
            "address_id",
            "restaurant_id",
            "food_id",
            "ordered_at",
            "promo_id",
        ],
    },
    "promos": {"index": "promo_id", "columns": ["discount"]},
    "restaurants": {"index": "restaurant_id", "columns": ["name", "address_id"]},
    "states": {"index": "state_id", "columns": ["name", "country_id"]},
    "users": {
        "index": "user_id",
        "columns": ["first_name", "last_name", "birthdate_id", "registred_at"],
    },
}

TABLES = sorted(TABLES_SCHEMA.keys())
def load_all_tables(tables_dir_path: Path = TABLES_DIR_PATH) -> List[pd.DataFrame]:
    res = load_tables(tables_dir_path, list(TABLES_SCHEMA.keys()))
    return res


def get_reduced_db() -> ReducedDatabase:
    return reduce_dims(MultiDimDatabase(*load_all_tables()))
x = get_reduced_db()

print(x.orders['ordered_at'])