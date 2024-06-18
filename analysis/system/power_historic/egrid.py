import core.db as db
from core.models import Utility, BalancingAuthority, Plant, Egrid
import numpy as np
import os
import pandas as pd
import sys
from tqdm import tqdm

import settings

def import_row(row):
    utlsrvid = str(row['UTLSRVID'])
    utility = Utility.query.filter(Utility.utlsrvid == utlsrvid).first()
    if utility is None:
        utility = Utility(
            utlsrvid=utlsrvid,
            name=row['UTLSRVNM']
        )
        db.save(utility)

    balancing_authority = None

    if 'BACODE' in row:
        bacode = row['BACODE']
        if bacode is not None:
            balancing_authority = BalancingAuthority.query.filter(BalancingAuthority.code == bacode).first()
            if balancing_authority is None:
                balancing_authority = BalancingAuthority(
                    code=bacode,
                    name=row['BANAME'],
                )
                db.save(balancing_authority)

    orispl = str(row['ORISPL'])
    plant = Plant.query.filter(Plant.orispl == orispl).first()
    if plant is None:
        plant = Plant(
            orispl=orispl,
            utility=utility,
            balancing_authority=balancing_authority,
            state=row['PSTATABB'],
            name=row['PNAME'],
            nerc_region=row['NERC'],
            subregion_acronym=row['SUBRGN'],
            subregion_name=row['SRNAME'],
            isorto=row['ISORTO'],
            county_name=row['CNTYNAME'],
            latitude=row['LAT'],
            longitude=row['LON'],
            num_units=row.get('NUMUNT'),
            num_generators=row.get('NUMGEN'),
            primary_fuel=row['PLPRMFL'],
            nameplate_capacity=row['NAMEPCAP'],
            power_to_heat_ratio=row.get('PWRTOHT'),
        )
        db.save(plant)

    year = row.get('YEAR')
    if year is not None:
        egrid = Egrid.query.filter(Egrid.plant == plant, Egrid.year == year).first()
        if egrid is None:
            egrid = Egrid(
                year=year,
                plant=plant,
                annual_nox_rate=row['PLNOXRTA'],
                ozone_season_nox_rate=row['PLNOXRTO'],
                annual_so2_rate=row['PLSO2RTA'],
                annual_co2_rate=row['PLCO2RTA'],
                annual_ch4_rate=row['PLCH4RTA'],
                annual_n2o_rate=row['PLN2ORTA'],
                annual_co2_equivalent_rate=row['PLC2ERTA'],
                annual_hg_rate=row['PLHGRTA'],
                nominal_heat_rate=row['PLHTRT'],
            )
            db.save(egrid)

def import_spreadsheet(path, sheet_name, header=1):
    print(f'reading spreadsheet: {path}')
    df = pd.read_excel(path, sheet_name=sheet_name, header=header, keep_default_na=False, na_values=[None, '', 'N/A', '--']).replace({ np.nan: None })
    print(f'importing {sheet_name}')
    with tqdm(total=len(df)) as pbar:
        for idx, row in df.iterrows():
            import_row(row)
            pbar.update(1)
