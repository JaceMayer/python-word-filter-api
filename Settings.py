#SQL Database URI
SQLALCHEMY_DATABASE_URI = "mysql+mysqldb://UserName:Password@127.0.0.1/WordFiler"
#FastAPI App Name
app_title = "Word Filter"
#FastAPI App Description
app_desc = "An API allowing you to filter words from your service"
#FastAPI App Version
app_ver = "1"
#JWT Access Token Duration
ACCESS_TOKEN_EXPIRE_MINUTES = 30
#JWT Secret Key
JWT_SECRET = "SecretKey"
#JWT Algorithm
JWT_ALGO = "HS256"
#API Endpoint Prefix (/api/v1/login)
API_PREFIX = "/api/v1/"
#Show Backend endpoints within the OpenAPI Spec
SHOW_SECURED_ENDPOINTS = False
