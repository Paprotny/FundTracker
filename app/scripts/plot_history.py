import pandas as pd
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from app.models import HistoricalPrice, Asset
from app.analytics.charts import plot_asset_history

DATABASE_URL = "sqlite:///./portfolio.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine)
db = SessionLocal()

query = (
    db.query(
        HistoricalPrice.date,
        HistoricalPrice.value_pln,
        Asset.symbol
    )
    .join(Asset, Asset.id == HistoricalPrice.asset_id)
)

df = pd.read_sql(query.statement, db.bind)

db.close()

plot_asset_history(df, symbol="APR")