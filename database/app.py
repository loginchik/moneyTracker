# https://blog.osull.com/2022/10/28/async-postgresql-with-fastapi-dependency-injection-sqlalchemy/ 

import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, Depends
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.staticfiles import StaticFiles

from routers import users, expenses, revenues, web
from config import settings

from depends import db 


connection_vars = dict()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await db.setup()

    # Working process
    yield

    # Shutdown 
    await db.shutdown()


app = FastAPI(lifespan=lifespan, debug=True, title='Money Tracker API')

static_path = os.path.abspath('../frontend/static')
app.mount('/static', StaticFiles(directory=static_path), name='static')

app.add_middleware(TrustedHostMiddleware, allowed_hosts=['*'])

app.include_router(users.users_router)
app.include_router(expenses.expense_router)
app.include_router(revenues.revenues_router)
app.include_router(web.web_router)

@app.get(path='/')
def start_page():
    return 'Hello, world!'
