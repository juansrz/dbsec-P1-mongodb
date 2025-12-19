import sys
import time
from pprint import pprint
import pymongo
from bson.objectid import ObjectId
from pymongo.collection import Collection


def find_one(client_db: pymongo.collection.Collection, oid: str):
    return client_db.find_one({'_id': ObjectId(oid)})


if __name__ == '__main__':
    # Obtenemos el id del documento que queremos seleccionar por línea de comandos
    id_ = sys.argv[1]
    # Conectamos con la BD.
    # Es posible que sea necesario especificar aquí alguna opción adicional para conectar a la BD,
    # dependiendo de la configuración
    client = pymongo.MongoClient()

    print(f"Retrieving object with id '{id_}':\n")
    # Vamos a realizar la búsqueda sobre la collección "Viajes" de la BD "CityBikeURJC".
    viajes_collection = client["CityBikeURJC"]["Viajes"]
    pprint(find_one(viajes_collection, id_))

 # Medir el tiempo total para 20,000 consultas
    ids = list(viajes_collection.find().limit(20000).distinct("_id"))
    iterations = 20000
    total_time = 0
    # Calcular tiempo total y promedio
    for i in range(iterations):
        start_time = time.time()
        oid = ids[i % len(ids)]
        viajes_collection.find_one({'_id': ObjectId(oid)})
        end_time = time.time()  # Marca el fin del tiempo
        total_time += (end_time - start_time)


    average_time = total_time / iterations

    print(f"Tiempo total para {iterations} consultas: {total_time:.2f} segundos")
    print(f"Tiempo promedio por consulta: {average_time:.6f} segundos")