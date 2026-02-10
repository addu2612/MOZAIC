from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1 import auth, projects, accounts, incidents, demo
#from app.webhooks import sentry_webhook, cloudwatch_webhook
from app.core.config import settings
app = FastAPI(title=settings.PROJECT_NAME)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API routes
app.include_router(auth.router, prefix=f"{settings.API_V1_STR}/auth", tags=["auth"])
app.include_router(projects.router, prefix=f"{settings.API_V1_STR}/projects", tags=["projects"])
app.include_router(accounts.router, prefix=f"{settings.API_V1_STR}/accounts", tags=["accounts"])
app.include_router(incidents.router, prefix=f"{settings.API_V1_STR}/incidents", tags=["incidents"])

# Demo routes (no auth) for teacher meeting
app.include_router(demo.router, prefix=f"{settings.API_V1_STR}/demo", tags=["demo"])

# Webhooks
#app.include_router(sentry_webhook.router, prefix="/webhooks", tags=["webhooks"])
#app.include_router(cloudwatch_webhook.router, prefix="/webhooks", tags=["webhooks"])

@app.get("/")
async def root():
    return {"message": "MOZAIC API"}