import  pickle

with (open("C:\Danika\git\out-of-sight\data\Locate\Locate__99914b932b-data.pkl", "rb")) as openfile:
    l = pickle.load(openfile)
with (open("C:\Danika\git\out-of-sight\data\Read\Read__99914b932b-data.pkl", "rb")) as openfile:
    r = pickle.load(openfile)
with (open("C:\Danika\git\out-of-sight\data\DisplayImageOCR\DisplayImageOCR__99914b932b-data.pkl", "rb")) as openfile:
    d = pickle.load(openfile)

print(type(l['roi_lpCnt']))
print(l['roi_lpCnt'])
print('..............')
print(type(r['lpText_lpCnt']))
print(r['lpText_lpCnt'])
print('..............')
print(type(d['lpCnt']))
print(d['lpCnt'])
