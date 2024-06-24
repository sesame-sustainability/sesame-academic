from datetime import datetime, time
import core.db as db
from core.models import Plant, ARP
import numpy as np
import os
import pandas as pd
import redis
import sys
from tqdm import tqdm
import us
from utils import LRUCache
import sqlalchemy

import settings

plant_ids = LRUCache(1000)

def import_row(row):
    orispl = str(row['ORISPL_CODE'])
    plant_id = plant_ids.get(orispl)
    if plant_id is None:
        plant = Plant.query.filter(Plant.orispl == orispl).first()
        if plant is None:
            raise Exception(f'plant not found: {orispl}')
        plant_id = plant.id
        plant_ids.set(orispl, plant_id)


    date = datetime.strptime(row['OP_DATE'], '%m-%d-%Y')
    hour = time(row['OP_HOUR'], 0)
    timestamp = datetime.combine(date, hour)
    unit = str(row['UNITID'])

    def update_arp_attrs(arp):
        arp.gload=row['GLOAD (MW)']
        arp.so2_mass=row['SO2_MASS (lbs)']
        arp.nox_mass=row['NOX_MASS (lbs)']
        arp.co2_mass=row['CO2_MASS (tons)']
        arp.heat_input=row['HEAT_INPUT (mmBtu)']

    try:
        arp = ARP(plant_id=plant_id, timestamp=timestamp, unit=unit)
        update_arp_attrs(arp)
        db.save(arp)
    except sqlalchemy.exc.IntegrityError as e:
        db.rollback()
        if e.orig.pgcode == '23505':
            arp = ARP.query.filter(ARP.plant_id == plant_id, ARP.timestamp == timestamp, ARP.unit == unit).first()
            update_arp_attrs(arp)
            db.save(arp)
        else:
            raise e


def import_csv(year, month, state):
    print(f'import: {month}/{year} {state}')

    data_dir = 'data'
    filename = f'{year}{state}{str(month).zfill(2)}.csv'
    path = os.path.join(data_dir, filename)

    df = pd.read_csv(path, keep_default_na=False, na_values=['']).replace({ np.nan: None })
    with tqdm(total=len(df)) as pbar:
        for idx, row in df.iterrows():
            try:
                import_row(row)
            except Exception as err:
                print("import error: {0}".format(err))
            pbar.update(1)
