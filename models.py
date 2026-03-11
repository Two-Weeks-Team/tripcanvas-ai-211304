import os
from sqlalchemy import create_engine, Column, Integer, String, Text, ForeignKey, Table
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
from dotenv import load_dotenv

load_dotenv()

# Resolve database URL with prefix adjustments
db_url = (
    os.getenv("DATABASE_URL")
    or os.getenv("POSTGRES_URL")
    or "sqlite:///./app.db"
)

if db_url.startswith("postgresql+asyncpg://"):
    db_url = db_url.replace("postgresql+asyncpg://", "postgresql+psycopg://")
elif db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql+psycopg://")

connect_args = {}
if not db_url.startswith("sqlite"):
    if "localhost" not in db_url and "127.0.0.1" not in db_url:
        connect_args["sslmode"] = "require"

engine = create_engine(db_url, connect_args=connect_args, future=True, echo=False)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

Base = declarative_base()

# Prefix for all tables to avoid collisions in a shared DB
TABLE_PREFIX = "tripcanvas_ai_211304_"

class User(Base):
    __tablename__ = f"{TABLE_PREFIX}users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    trips = relationship("Trip", back_populates="owner")

class Trip(Base):
    __tablename__ = f"{TABLE_PREFIX}trips"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    owner_id = Column(Integer, ForeignKey(f"{TABLE_PREFIX}users.id"))
    owner = relationship("User", back_populates="trips")
    destinations = relationship(
        "Destination",
        secondary=f"{TABLE_PREFIX}trip_destinations",
        back_populates="trips",
    )

class Destination(Base):
    __tablename__ = f"{TABLE_PREFIX}destinations"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    country = Column(String)
    description = Column(Text)
    trips = relationship(
        "Trip",
        secondary=f"{TABLE_PREFIX}trip_destinations",
        back_populates="destinations",
    )

# Association table for many‑to‑many Trip ↔ Destination
trip_destinations = Table(
    f"{TABLE_PREFIX}trip_destinations",
    Base.metadata,
    Column("trip_id", Integer, ForeignKey(f"{TABLE_PREFIX}trips.id"), primary_key=True),
    Column("destination_id", Integer, ForeignKey(f"{TABLE_PREFIX}destinations.id"), primary_key=True),
)
