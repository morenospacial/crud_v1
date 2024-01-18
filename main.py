from flask import Flask, render_template, request, url_for, flash
from werkzeug.utils import redirect
from flask_mysqldb import MySQL


app = Flask(__name__)
app.secret_key = 'many random bytes'

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'crud'

mysql = MySQL(app)

class Tabla:
        def __init__(self,tabla,campos):
            self.nombre_tabla = tabla
            self.campos = campos


tablaActiva = Tabla("sinnombre","nada")

# Debes crear un objeto Cursor. Te permitirá
# ejecutar todos los queries que necesitas



@app.route('/', methods= ['POST','GET'])
@app.route('/<tablaseleccionada>', methods= ['POST','GET'])
@app.route('/<tablaseleccionada>/', methods= ['POST','GET'])
@app.route('/<tablaseleccionada>/<Filtro>', methods= ['POST','GET'])
@app.route('/<tablaseleccionada>/<Filtro>/<pagina>', methods= ['POST','GET'])
def Index(tablaseleccionada=None, Filtro=None,pagina=None):
    
    print("index tabla seleccionada " + str(tablaseleccionada))
    vpaginador = 4
    if pagina == None:
        vpaginaActual = 0
    else:
        vpaginaActual = int(pagina)
        Filtro = None

    tablaActiva = Tabla(tablaseleccionada,"")

    cur1 = mysql.connection.cursor()
    cur1.execute("SHOW TABLES")
    data_tables = cur1.fetchall()
    print(data_tables)
    cur1.close()

    curtabla = mysql.connection.cursor()
    curcampo = mysql.connection.cursor()
    vcampos = []
    vtablas = []
    vnombrecampo = []
    cont=0
    # Usa todas las sentencias SQL que quieras
    curtabla.execute("SHOW TABLES")
    # Imprimir la primera columna de todos los registros
    for row in curtabla.fetchall():
        curcampo.execute ("SHOW COLUMNS FROM " + row[0])

        vcampos=[]
        vnombrecampo =[]
        for campo in curcampo.fetchall():
                vcampos.append([campo[0],campo[5],campo[3]])
                vnombrecampo.append(campo[0])

        obj = Tabla(row[0],vcampos)
        if tablaseleccionada ==None:
            if cont==0:
                tablaActiva = Tabla(row[0],vcampos)
            else:
                cont= cont + 1
        else:
            if tablaseleccionada == row[0]:
                tablaActiva = Tabla(row[0],vcampos)
        
        vtablas.append(obj)

    curtabla.close()
    curcampo.close()


    print("Filtro1: " + str(Filtro))


    query = "SELECT * FROM " + str(tablaActiva.nombre_tabla)
    querycount = "select count(*) as data from " + tablaActiva.nombre_tabla
    calculo = vpaginador * vpaginaActual
    vlimit = " limit " + str(vpaginador) + " OFFSET " + str(calculo)
    print("paginador " + str(vpaginador))
    print("vpaginaActual " + str(vpaginaActual))
    print("calculo " + str(calculo))
    print("query base: " + query)
    queryfiltro= ""
    if Filtro != None:
        queryfiltro =" where "
        for campo in tablaActiva.campos:
            queryfiltro = queryfiltro + campo[0] + " like '%" + str(Filtro) + "%' or "

        queryfiltro = queryfiltro[0:len(queryfiltro) -3]

        querycount = querycount + queryfiltro + vlimit

    query = query  + queryfiltro + vlimit
    print ("query: " + query)
    cur = mysql.connection.cursor()
    cur.execute(query)
    data = cur.fetchall()
    print(data)
    cur.close()

    vcanttotal = 0
    print ("querycount:" + querycount)
    curtotal = mysql.connection.cursor()
    curtotal.execute(querycount)
    datacount = curtotal.fetchall()
    for regcampo in datacount:
        vcanttotal = regcampo[0]

    print(vcanttotal)
    curtotal.close()





    localpaginas = []
    a=1
    if vcanttotal > vpaginador :
        vcantPagina = int(vcanttotal / vpaginador)
        vresto = vcanttotal % vpaginador
        if vresto >0 :
            vcantPagina = vcantPagina + 1
        print ('vcantPagina' + str(vcantPagina) )
        for a in range (vcantPagina):
            print ('a '+ str(a))
            localpaginas.append(a+1)




    vpaginadorlocal = []
    vpaginadorlocal.append([vcanttotal,localpaginas,vpaginaActual])

    print(localpaginas)
    for campo in tablaActiva.campos:
        if campo[2] == 'PRI':
            key = campo[0]

    print ("llave:" + key)



    return render_template('index.html', vtablaActiva=tablaActiva, vtablename = vtablas, vdata = data,vkey = key, vpaginador = vpaginadorlocal, vpaginas =localpaginas)



@app.route('/insert', methods = ['POST'])
def insert():
    if request.method == "POST":
        flash("Data Inserted Successfully")
        
        vtable = request.form['table']
        primaria  = request.form['llave']
        

        data = request.form
        columns = ', '.join(data.keys())
        placeholders = data.listvalues()

        
        cur = mysql.connection.cursor()
    
            
        columns = columns.replace('table,','')
        columns = columns.replace('llave,','')
        
    
        #campo_ = "dict_values([['" + vtable + "'],"
        campo_ = "dict_values([['" + vtable + "'], ['" + primaria + "'],"
    
        print (placeholders)
        print (campo_)
        placeholders = str(placeholders).replace(campo_,'')
        placeholders = str(placeholders).replace('[','')
        placeholders = str(placeholders).replace(']','')
        placeholders = str(placeholders).replace(')','')
        print (placeholders)
    
        query = f"INSERT INTO {vtable} ({columns}) VALUES ({placeholders})"
        print (query)
    
        cur.execute(query)
        
        mysql.connection.commit()
        return redirect(url_for('Index',tablaseleccionada = vtable))
    

@app.route('/delete/<string:id_data>/<vtable>/<vkey>', methods = ['GET'])
def delete(id_data,vtable=None,vkey=None):
    flash("Record Has Been Deleted Successfully")
    print("vamos a borrar :" + vtable)
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM "+ vtable+ " WHERE "+ vkey +"=%s", (id_data,))
    mysql.connection.commit()
    return redirect(url_for('Index',tablaseleccionada = vtable))



@app.route('/update', methods= ['POST', 'GET'])
def update():
    if request.method == 'POST':
        
        vtable = request.form['table']
        id  = request.form['id']
        primaria  = request.form['llave']
       
        data = request.form
        columns = ', '.join(data.keys())
        placeholders = data.listvalues()

        #verbd = bd()    
        cur = mysql.connection.cursor()
        
               
        columns = columns.replace('table,','')
        columns = columns.replace('llave,','')
        columns = columns.replace(primaria + ',','')
        print ("columnas:" + columns)
       
        campo_ = "dict_values([['" + id + "'], ['" + vtable + "'], ['" + primaria +"'],"
        print (placeholders)  
        print (campo_)     
        placeholders = str(placeholders).replace(campo_,'')
        placeholders = str(placeholders).replace('[','')
        placeholders = str(placeholders).replace(']','')
        placeholders = str(placeholders).replace(')','')
        
        print (placeholders)  
        lista_campos = columns.split(",")
        lista_valores = placeholders.split(",")
        a=0
        cont=0
        setcampos = ""
        for valor in lista_campos:
            if cont !=0 :
                setcampos = setcampos + valor + "=" + lista_valores[a] + ","
                cont = cont +1
            else:
                cont = cont+1
            a= a+1
        setcampos = setcampos[0:len(setcampos)-1]

        print ("setcampos :" + setcampos)

        query = "UPDATE "+ vtable + " SET " + setcampos + " WHERE "+ primaria + " =" + id 
        print (query)
        cur = mysql.connection.cursor()
        cur.execute(query)

        flash("Data Updated Successfully")
        return redirect(url_for('Index',tablaseleccionada = vtable))


@app.route('/buscar', methods = ['POST'])
def buscar():
    if request.method == 'POST':
        
        vtable = request.form['table']
        vfiltro = request.form['buscar']

        print("filtro a buscar:" + str(vfiltro))
        return redirect(url_for('Index',tablaseleccionada = vtable, Filtro = vfiltro))

#@app.route('/paginar/<string:id_pag>/', methods = ['POST'])

""" def paginar(id_pag=None):
    if request.method == 'POST':
        print("entro al pagine")
        vtable = request.form['table']
        vfiltro = request.form['buscar']

        print("tabla pag:" + vtable)

        print("filtro a buscar:" + str(vfiltro))
        #return redirect(url_for('Index',tablaseleccionada = vtable, Filtro = vfiltro)) """

if __name__ == "__main__":
    app.run(debug=True, port=5001)
