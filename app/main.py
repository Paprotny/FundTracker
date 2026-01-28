from fastapi import FastAPI
from app.database import Base,engine
from app.routers import assets,transactions,pricecache,update_prices,portfolio
from app.database import Base,engine

Base.metadata.create_all(bind=engine)

app = FastAPI()

#Connecting routers
app.include_router(assets.router, prefix="/assets", tags=["Assets"])
app.include_router(transactions.router, prefix="/transactions", tags=["Transactions"])
app.include_router(pricecache.router, prefix="/prices", tags=["Prices"])
app.include_router(update_prices.router, prefix="/update_prices", tags=["Update Prices"])
app.include_router(portfolio.router, tags=["Portfolio"]) 
