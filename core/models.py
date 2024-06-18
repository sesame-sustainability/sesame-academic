import core.db as db
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String, Index
from sqlalchemy.orm import relationship

class User(db.Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, unique=True)
    email = Column(String, nullable=False, unique=True)
    name = Column(String)
    institution = Column(String)
    hashed_password = Column(String, nullable=False)

class Utility(db.Base):
    __tablename__ = 'utilities'

    id = Column(Integer, primary_key=True, unique=True)
    utlsrvid = Column(String, nullable=False, unique=True)
    name = Column(String)

class BalancingAuthority(db.Base):
    __tablename__ = 'balancing_authorities'

    id = Column(Integer, primary_key=True, unique=True, autoincrement=True)
    name = Column(String, nullable=False)
    code = Column(String, nullable=False, index=True, unique=True)

class Plant(db.Base):
    __tablename__ = 'plants'

    id = Column(Integer, primary_key=True, unique=True, autoincrement=True)

    utility_id = Column(Integer, ForeignKey('utilities.id'), nullable=False)
    utility = relationship('Utility')

    balancing_authority_id = Column(Integer, ForeignKey('balancing_authorities.id'), nullable=True)
    balancing_authority = relationship('BalancingAuthority')

    orispl = Column(Integer, nullable=False, index=True, unique=True)
    state = Column(String, nullable=False)
    name = Column(String, nullable=False)
    nerc_region = Column(String, nullable=False)
    subregion_acronym = Column(String)
    subregion_name = Column(String)
    isorto = Column(String)
    county_name = Column(String)
    latitude = Column(Float)
    longitude = Column(Float)
    num_units = Column(Integer)
    num_generators = Column(Integer)
    primary_fuel = Column(String)
    nameplate_capacity = Column(Float)
    power_to_heat_ratio = Column(Float)

class Egrid(db.Base):
    __tablename__ = 'egrid'

    id = Column(Integer, primary_key=True, unique=True, autoincrement=True)

    plant_id = Column(Integer, ForeignKey('plants.id'), nullable=False, index=True)
    plant = relationship('Plant')

    year = Column(Integer, nullable=False)

    annual_nox_rate = Column(Float)
    ozone_season_nox_rate = Column(Float)
    annual_so2_rate = Column(Float)
    annual_co2_rate = Column(Float)
    annual_ch4_rate = Column(Float)
    annual_n2o_rate = Column(Float)
    annual_co2_equivalent_rate = Column(Float)
    annual_hg_rate = Column(Float)
    nominal_heat_rate = Column(Float)

class ARP(db.Base):
    __tablename__ = 'arp'

    plant_id = Column(Integer, ForeignKey('plants.id'), nullable=False, index=True, primary_key=True)
    plant = relationship('Plant')

    unit = Column(Integer, nullable=False, primary_key=True)
    timestamp = Column(DateTime(timezone=False), nullable=False, primary_key=True)

    gload = Column(Float)
    so2_mass= Column(Float)
    nox_mass = Column(Float)
    co2_mass = Column(Float)
    heat_input = Column(Float)
