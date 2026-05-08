import kagglehub

kagglehub.login() # KGAT_65a4ed039196fd33a020e9cf4ef3e18c
# Download latest version
path = kagglehub.competition_download('m5-forecasting-accuracy')

print("Path to competition files:", path)
