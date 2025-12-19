import sys
import time
from pprint import pprint
import pymongo
from bson import CodecOptions
from bson.objectid import ObjectId
from pymongo.encryption import ClientEncryption
from pymongo.collection import Collection


def find_one(client_db: pymongo.collection.Collection, client_encryption_: ClientEncryption, oid: str):
    # Buscamos el documento por id.
    doc = client_db.find_one({'_id': ObjectId(oid)})
    # Comprobamos que existen campos cifrados.
    print("Encrypted document: %s" % (doc,))
    # TODO 3: descifrar los campos cifrados del documento encontrado. Devolver el documento con los campos en claro
    encryptedBirthYear = doc["birth year"]
    encryptedGender = doc["gender"]
    decryptedBirthYear = client_encryption_.decrypt(encryptedBirthYear)
    decryptedGender = client_encryption_.decrypt(encryptedGender)
    doc["birth year"] = decryptedBirthYear
    doc["gender"] = decryptedGender
    print("Documento desencriptado: ")
    return doc


def get_client_encryption(path_master_key: str, target_collection) -> ClientEncryption:
    # Abrimos el fichero donde se encuentra la clave maestra y la leemos.
    with open(path_master_key, "rb") as f:
        local_master_key = f.read()
    # TODO 1: obtener kms provider
    kmsProviders = { "local": {"key": local_master_key},}
    # TODO 2: obtener y devolver un objeto ClientEncryption
    codec_options = CodecOptions()
    client_encryption = ClientEncryption(kmsProviders, key_vault_namespace="encryption.__keyVault", key_vault_client=client, codec_options=codec_options)
    return client_encryption


if __name__ == '__main__':
    # Obtenemos el id del documento que queremos seleccionar por línea de comandos.
    id_ = sys.argv[1]
    # Conectamos con la BD.
    # Es posible que sea necesario especificar aquí alguna opción adicional para conectar a la BD,
    # dependiendo de la configuración.
    client = pymongo.MongoClient("mongodb://localhost:27017/")

    # Obtenemos un cliente que nos permitirá cifrar y descifrar campos de los documentos de la colección seleccionada.
    collection = client["CityBikeURJC"]["encryptedViajes"]
    path = ("C:/Users/Juan_/OneDrive/Escritorio/Ciber 2024-2025/1er Cuatrimestre/Seguridad Base de "
            "datos/Practica1/master-key.txt")
    client_encryption = get_client_encryption(path, collection)

    print(f"Retrieving object with id '{id_}':\n")
    pprint(find_one(collection, client_encryption, id_))

    print("\nRealizando 20,000 consultas...\n")
    ids = list(collection.find().limit(20000).distinct("_id"))  # Obtener hasta 20,000 IDs únicos
    iterations = 20000
    total_time = 0

    for i in range(iterations):
        start_time = time.time()  # Marca el inicio del tiempo
        oid = ids[i % len(ids)]  # Rota sobre la lista de IDs
        find_one(collection, client_encryption, str(oid))  # Consulta con el ID actual
        end_time = time.time()  # Marca el fin del tiempo
        total_time += (end_time - start_time)

    # Calcular tiempo total y promedio
    average_time = total_time / iterations

    print(f"Tiempo total para {iterations} consultas: {total_time:.2f} segundos")
    print(f"Tiempo promedio por consulta: {average_time:.6f} segundos")

