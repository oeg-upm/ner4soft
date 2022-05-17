import owncloud
import os

oc = owncloud.Client("https://delicias.dia.fi.upm.es/nextcloud/")
oc.login(input("user: "), input("password: "))
os.makedirs("models", exist_ok=True)
oc.get_file("ner4soft/model.zip","models/model.zip")