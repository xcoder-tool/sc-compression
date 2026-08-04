import os

from sc_compression import Decompressor

if not os.path.exists("in"):
    os.mkdir("in")

if not os.path.exists("out"):
    os.mkdir("out")


for filename in os.listdir("in"):
    with open("in/" + filename, "rb") as f:
        file_data = f.read()
        f.close()
    with open("out/" + filename, "wb") as f:
        f.write(Decompressor.decompress(file_data))
        f.close()
