#!/usr/bin/python
#

import ftplib

servidor_id = "192.168.20.20"
servidor_user = "sonda"
servidor_pass = "660738"

try:
    conexion = ftplib.FTP(servidor_id)
    conexion.login(servidor_user,servidor_pass)
    print("++ Conexoin extablecida")
except Exception as e:
    print ("-- Conexoin no extablecida" + str(e))

# Para visualizar el contenido del del ftp
conexion.retrlines("LIST")

# Funcion para envio de archivos
def ftpSend():
    #path= "Sonda_30Setiembre.db"
    with  open(path,"rb") as file:
        conexion.storbinary(f"STOR Sonda_30Setiembre.db", file)
    file.close()
    conexion.quit()