import time
from bson import codec_options, CodecOptions
from pymongo import MongoClient, ASCENDING
from pymongo.encryption import ClientEncryption
import bson


def obtain_master_key():
    """Lee la clave maestra desde un archivo"""
    path = "C:/Users/Juan_/OneDrive/Escritorio/Ciber 2024-2025/1er Cuatrimestre/Seguridad Base de datos/Practica1/master-key.txt"
    with open(path, "rb") as f:
        local_master_key = f.read()
    return local_master_key


if __name__ == '__main__':
    client = MongoClient("mongodb://localhost:27017/")

    key_vault_coll = "__keyVault"
    key_vault_db = "encryption"

    # Eliminar las colecciones anteriores para empezar desde cero
    print("Eliminando bases de datos y colecciones previas...")
    client.drop_database(key_vault_db)
    client["CityBikeURJC"].drop_collection("encryptedViajes")
    print("Colecciones eliminadas.")

    # Crear índice en la colección __keyVault
    print("Creando índice en __keyVault...")
    client[key_vault_db][key_vault_coll].create_index(
        [("keyAltNames", ASCENDING)],
        unique=True,
        partialFilterExpression={"keyAltNames": {"$exists": True}},
    )
    print("Índice creado en __keyVault.")

    # Obtener la clave maestra
    print("Obteniendo la clave maestra...")
    local_master_key = obtain_master_key()
    kms_provider = {
        "local": {
            "key": local_master_key
        },
    }
    print("Clave maestra obtenida.")

    # Crear la colección encryptedViajes
    print("Creando la colección encryptedViajes...")
    encryptedCollection = client["CityBikeURJC"]["encryptedViajes"]
    print("Colección encryptedViajes creada.")

    # Configurar el cliente de cifrado
    print("Configurando el cliente de cifrado...")
    codec_options = CodecOptions()
    client_encryption = ClientEncryption(
        kms_provider,
        key_vault_namespace="encryption.__keyVault",
        key_vault_client=client,
        codec_options=codec_options
    )
    print("Cliente de cifrado configurado.")

    # Crear una clave de datos para cifrar
    print("Creando clave de cifrado...")
    data_key_id = client_encryption.create_data_key("local")
    print(f"Clave de cifrado creada: {data_key_id}")

    # Iterar sobre los documentos de la colección Viajes y cifrar
    total = client["CityBikeURJC"]["Viajes"].estimated_document_count()
    if total == 0:
        print("La colección 'Viajes' está vacía. Finalizando el proceso.")
        exit()

    count = 0
    max_time_seconds = 30
    start_time = time.time()
    algoritmo = "AEAD_AES_256_CBC_HMAC_SHA_512-Deterministic"

    print(f"Procesando documentos en la colección 'Viajes'... Total estimado: {total}")
    for document in client["CityBikeURJC"]["Viajes"].find():
        try:
            if "birth year" not in document or "gender" not in document:
                print(f"Documento {document.get('_id', 'desconocido')} omitido: faltan campos requeridos.")
                continue

            # Cifrar los campos
            birthYear = document["birth year"]
            encrypted_birth_year = client_encryption.encrypt(
                birthYear, algoritmo, data_key_id
            )
            genero = document["gender"]
            encrypted_gender = client_encryption.encrypt(
                genero, algoritmo, data_key_id
            )

            # Crear un nuevo documento cifrado
            encrypted_document = document
            encrypted_document["birth year"] = encrypted_birth_year
            encrypted_document["gender"] = encrypted_gender

            # Insertar en la colección encryptedViajes
            encryptedCollection.insert_one(encrypted_document)
            count += 1

            # Imprimir progreso
            if count % 10000 == 0:
                print(f"Encrypted {count} out of {total} documents in {round(time.time() - start_time, 2)} seconds...")

            # Detener después de un tiempo máximo
            if time.time() - start_time > max_time_seconds:
                print(f"Tiempo máximo alcanzado. Se cifraron {count} documentos antes de detenerse.")
                break
        except Exception as e:
            print(f"Error al procesar el documento {document.get('_id', 'desconocido')}: {e}")

    print(f"Proceso finalizado. Se cifraron {count} documentos en un tiempo total de {round(time.time() - start_time, 2)} segundos.")
    print(f"Documentos omitidos o con errores: {total - count}.")

    # Verificar colecciones finales
    print("Colecciones creadas:")
    print(client["CityBikeURJC"].list_collection_names())
    key_vault_count = client["encryption"]["__keyVault"].count_documents({})
    print(f"Claves en '__keyVault': {key_vault_count}")
    encrypted_count = encryptedCollection.count_documents({})
    print(f"Documentos en 'encryptedViajes': {encrypted_count}")
