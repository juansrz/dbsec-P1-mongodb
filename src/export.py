from pymongo import MongoClient
import csv

# Conexión a MongoDB
client = MongoClient("mongodb://localhost:27017/")  # Ajusta la conexión si es necesario
db = client["Practica1"]  # Base de datos
collection = db["Viajes_por_hora"]  # Colección

# Consulta los datos
cursor = collection.find()

# Ruta del archivo CSV
output_file = "resultados.csv"

# Escribir datos en el archivo CSV
with open(output_file, "w", newline="") as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(["hour", "total_trips"])  # Encabezados
    for doc in cursor:
        writer.writerow([doc["_id"], doc["total_trips"]])

print(f"Datos exportados a {output_file}")
