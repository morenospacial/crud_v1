import MySQLdb
db = MySQLdb.connect(host="localhost",    # tu host, usualmente localhost
                     user="root",         # tu usuario
                     passwd="",  # tu password
                     db="crud")        # el nombre de la base de datos

class Tabla:
    def __init__(self,tabla,campos):
        self.nombre_tabla = tabla
        self.campos = campos

# Debes crear un objeto Cursor. Te permitirá
# ejecutar todos los queries que necesitas
cur = db.cursor()
cur1 = db.cursor()
vcampos = []
vtablas = []
# Usa todas las sentencias SQL que quieras
cur.execute("SHOW TABLES")
# Imprimir la primera columna de todos los registros
for row in cur.fetchall():
    cur1.execute ("SHOW COLUMNS FROM " + row[0])
    
    vcampos=[]
    for campo in cur1.fetchall():
        vcampos.append(campo[0])
    obj = Tabla(row[0],vcampos)
    vtablas.append(obj)

cur.close()
cur1.close()

for tablita in vtablas:
    print ('Tabla: ' + tablita.nombre_tabla)
    for campo in tablita.campos:
        print('Campo:' + campo)
    print ("\n")