from pymongo import MongoClient
from pymongo.encryption import ClientEncryption
from bson import CodecOptions, Binary
import bson


def obtain_master_key():
    path = ("C:/Users/Juan_/OneDrive/Escritorio/Ciber 2024-2025/1er Cuatrimestre/Seguridad Base de "
            "datos/Practica1/master-key.txt")
    with open(path, "rb") as f:
        local_master_key = f.read()
    return local_master_key


def buscar_por_año_nacimiento(client, año):
    # Configurar el cliente de cifrado
    print("Configurando el cliente de cifrado...")
    local_master_key = obtain_master_key()
    kms_provider = {
        "local": {
            "key": local_master_key
        },
    }
    codec_options = CodecOptions()
    client_encryption = ClientEncryption(
        kms_provider,
        key_vault_namespace="encryption.__keyVault",
        key_vault_client=client,
        codec_options=codec_options
    )
    print("Cliente de cifrado configurado.")

    # Cifrar el año de nacimiento para realizar la búsqueda
    algoritmo = "AEAD_AES_256_CBC_HMAC_SHA_512-Deterministic"
    try:
        data_key = client["encryption"]["__keyVault"].find_one()
        if not data_key:
            print("Error: No se encontró una clave de cifrado en '__keyVault'.")
            return []
        data_key_id = data_key["_id"]
        encrypted_birth_year = client_encryption.encrypt(año, algoritmo, data_key_id)
    except Exception as e:
        print(f"Error al cifrar el año {año}: {e}")
        return []

    # Buscar los documentos con el año de nacimiento cifrado
    encrypted_collection = client["CityBikeURJC"]["encryptedViajes"]
    resultado = list(encrypted_collection.find({"birth year": encrypted_birth_year}))

    return resultado


if __name__ == '__main__':
    client = MongoClient("mongodb://localhost:27017/")
    año = input("Ingrese el año de nacimiento que desea buscar: ")

    # Verificar que el año ingresado es un valor válido
    if not año.isdigit():
        print("Error: El valor ingresado debe ser un año válido.")
    else:
        # Buscar los documentos correspondientes
        documentos = buscar_por_año_nacimiento(client, int(año))

        # Mostrar los documentos encontrados
        if documentos:
            print(f"Se encontraron {len(documentos)} documentos:")
            for doc in documentos:
                print(doc)
        else:
            print("No se encontraron documentos para el año ingresado.")
