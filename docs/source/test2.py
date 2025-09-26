from csv import DictReader
from json import dump
from archery import mdict

res=mdict()
with open("/home/jul/Téléchargements/GEMESCAPEG.csv") as f:
    for l in DictReader(f):
        res+=mdict(by_ref = mdict({l["Referent"]: 1}), by_prenom=mdict({l["Prenom"]:1}))

dump(res, open("data.js", "w"), indent=4)
