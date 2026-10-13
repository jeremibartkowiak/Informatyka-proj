import os

JWT_KEY = os.getenv("JWT_KEY", "SuperSecretDefaultSecurityKeyForInformatykaProj2026WithEnoughLength!!")
JWT_ISSUER = os.getenv("JWT_ISSUER", "SmartTravelApp")
JWT_AUDIENCE = os.getenv("JWT_AUDIENCE", "SmartTravelAppUsers")
JWT_EXPIRE_HOURS = 8

# SQLite domyślnie; można podać np. postgresql+psycopg://... lub mssql+pyodbc://...
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./smarttravel.db")
