import os

if __name__ == '__main__':
    path = "master-key.txt"
    file_bytes = os.urandom(96)
    with open(path, "wb") as f:
        f.write(file_bytes)
