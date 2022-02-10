import  pickle

with (open("C:\Danika\git\out-of-sight\data\OCR\OCR__99914b932b-data.pkl", "rb")) as openfile:
    a = pickle.load(openfile)

print(type(a[2][0]))