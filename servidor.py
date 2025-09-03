import socket
import sys
import threading
import random
import time 
HOST = "localhost"  # Direccion ip del host (En este caso la wifi)
PORT = 65432  # Puerto al que se conectará el cliente
buffer_size = 1024
tablero=[]
global hilo_nombre
hilo_nombre=[]
global hilo_caracter
hilo_caracter=[]
global n
n = 0
global contador_jugadas
contador_jugadas=0
#global contador_jugadas
contador_jugadas = 0 #Se utiliza para contar las casillas que son acertadas por el usuario
#global controlador
controlador = 1

def servirPorSiempre(socketTcp, listaconexiones, barrier, condicion_turno,first_candado):
    i = 0
    try:
        while True:
            client_conn, client_addr = socketTcp.accept()
            print("Usuario Conectado: ", client_addr)
            listaconexiones.append(client_conn)
            thread_read = threading.Thread(name='jugador-%s' % i,target=recibir_datos, args=[client_conn, client_addr, barrier,condicion_turno,first_candado])
            thread_read.start()
            gestion_conexiones(listaConexiones)
            i = i + 1
    except Exception as e:
        print(e)

def gestion_conexiones(listaconexiones):
    for conn in listaconexiones:
        if conn.fileno() == -1:
            listaconexiones.remove(conn)
    print("hilos activos:", threading.active_count())
    print("enum", threading.enumerate())
    print("conexiones: ", len(listaconexiones))
    print(listaconexiones)


def recibir_datos(conn, addr, barrier, condicion_turno,first_candado):
    global contador_jugadas
    global hilo_nombre
    global hilo_caracter
    #global controlador
    try:
        id = barrier.wait()
        cur_thread = threading.current_thread() #Se obtiene el hilo actual que se está ejecutando
        print("el hilo que se va aejecutar es = ",cur_thread.name)
        if(cur_thread.name == 'jugador-0'):
            conn.sendall(b'1')
            crearTablero(tablero,conn)
        else:
            conn.sendall(b'0')
            while True:
                print("N es esto: ",n)
                if n==0:
                    time.sleep(3)
                else:
                    conn.sendall(str(n).encode('utf-8'))
                    break
            #conn.sendall(str(n).encode('utf-8'))
        print("Tablero actual")
        print(n)
        mostrarTablero(tablero) #Se usa para mostrar el tablero 0's son casillas vacias y 1's son las minas
        first_candado.acquire()
        conn.sendall(b'0')
        caracter = conn.recv(buffer_size).decode('utf-8')
        hilo_nombre.append(cur_thread.name)
        hilo_caracter.append(caracter)
        first_candado.release()
        print("El hilo nombres es: ",hilo_nombre)
        print("El hilo de caracteres es: ",hilo_caracter)   
        flag=1
        while flag:
            posicion = hilo_nombre.index(cur_thread.name)
            print("El hilo que va a adquirir el semaforo es: ",cur_thread.name)
            condicion_turno[posicion].acquire()
            print("El hilo que entro es: ",cur_thread.name)
            print("la posicion es", posicion)
            for con in listaConexiones:
                if (con == conn):
                    con.sendall(b'0')
                else:
                    con.sendall(b'1')
            print("Recibiendo datos del jugador {} en el {}".format(addr, cur_thread.name))
            coordenadas = conn.recv(buffer_size) #Se reciben las coordenadas del cliente en formato (**,**)
            print(coordenadas) 
            filas = int(coordenadas[1:3])-1 
            print(filas)
            columnas = int(coordenadas[4:6])-1
            print(columnas)
            if filas >= n or columnas >= n: #Excepcion fuera de rango
                print("Fuera de rango")
                codigo='3' #Se envia respuesta al cliente de código 3
                print("Tablero actual")
                mostrarTablero(tablero)  
            else:
                condicion = tablero[filas][columnas] 
                if condicion != 1 and condicion!=2:  #Se verifica que la casilla no tenga minas
                    print("Casilla válida")
                    tablero[filas][columnas] = 2 #Se coloca la jugada en la casilla
                    contador_jugadas = contador_jugadas + 1 #Se incrementa el contador de las jugadas
                    condicion_gane = (n*n)-m #Se necesita cumplir la condicion para ganar
                    if contador_jugadas == condicion_gane:  #Se verifica el número de jugadas
                        codigo = '1'   #Si gana, se envía el código 1 al usuario
                        flag=0 #En caso de ganar se sale del ciclo del juego y acaba
                    else:
                        codigo='2' #En dado caso de que todavía no gane se sigue en el juego y se envia el codigo 2
                elif condicion == 1: #Condicion para cuando se encuentra una mina
                    print("Se ha encontrado una mina")
                    codigo='4' #Se envía el codigo 4 para el usuario
                    flag = 0 #Se sale del ciclo del juego
                elif condicion == 2: #Condicion para cuando la casilla ya se ha elegido
                    print("Casilla ya elegida")
                    codigo='5'
                print("Tablero actual")
                mostrarTablero(tablero) 
            codigo2 = coordenadas.decode('utf-8') +','+codigo+','+hilo_caracter[posicion]
            print("El codigo 2 es: ",codigo2)
            for con in listaConexiones:
                if (con == conn):
                    con.sendall(codigo.encode('utf-8'))
                else:
                    con.sendall(codigo2.encode('utf-8'))  
            if(posicion == (len(hilo_nombre)-1)):
                condicion_turno[0].release()
            else:
                condicion_turno[posicion+1].release()  
    except Exception as e:
        print(e)
    finally:
        conn.close()


def mostrarTablero(tablero): #Funcion para mostrar el tablero
    for filaT in tablero:
        for v in filaT:
            print(v, end=" ")
        print()

def crearTablero(tablero,conn):
    print("Esperando dificultad")
    global n
    global m
    dificultad = conn.recv(buffer_size) #Se recibe la dificultad
    dificultad = dificultad.lower() #Como la dificultad es una cadena, se convierten a minúsculas para las condiciones siguientes
    if dificultad==b'principiante': #Condiciones para crear el tablero
        print("Eligio principiante")
        n = 9 #Longitud del tablero
        m = 10 #Minas a poner
        conn.sendall(str(n).encode('utf-8')) #Servidor envía la longitud del tablero al cliente
    elif dificultad==b'avanzado':
        print("Eligio avanzado")
        n = 16
        m = 40
        conn.sendall(str(n).encode('utf-8'))
    elif dificultad==b'prueba' : #Tablero para pruebas, mas pequeño
        print("Entro a la prueba")
        n = 3
        m = 4
        conn.sendall(str(n).encode('utf-8'))
    print("Creando tablero...")
    #tablero = [] #Se empieza a crear el tablero
    for i in range(n):
        tablero.append([])
        for j in range(n):
            tablero[i].append(0) #Se rellena con 0's
    print("Poniendo minas...")
    i = 1
    while i <= m: #Se ponen las minas
        rand1 = random.randint(0,n-1) #Se crean posciciones de manera aleatoria
        rand2 = random.randint(0,n-1)
        if tablero[rand1][rand2] == 0: #Se pueden repetir, por lo que debemos confirmar que la casilla esté vacía
            tablero[rand1][rand2] = 1
        else :
            minascontrolador = 1
            while minascontrolador: #En caso de repetirse, iterar hasta obtener una casilla vacía
                rand1 = random.randint(0,n-1)
                rand2 = random.randint(0,n-1)
                if tablero[rand1][rand2] == 1:
                    minascontrolador = 1
                else:
                    tablero[rand1][rand2] = 1
                    minascontrolador = 0
        i = i + 1


listaConexiones = []
host, port, numConn = sys.argv[1:4]

if len(sys.argv) != 4:
    print("usage:", sys.argv[0], "<host> <port> <num_connections>")
    sys.exit(1)

serveraddr = (host, int(port))
print("El numero de conexiones es: ",numConn)
barrier = threading.Barrier(int(numConn)) #Configuracion de la barrera
condicion_turno = []
for i in range(int(numConn)):
    if(i==1):
        semaforo = threading.Semaphore(1)
        condicion_turno.append(semaforo)
    else:
        semaforo = threading.Semaphore(0)
        condicion_turno.append(semaforo)
first_candado = threading.Lock()
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as TCPServerSocket:
    TCPServerSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) #Sirve para establecer opciones en un socket existente, permite reultilizacion de direccion del socket
    TCPServerSocket.bind(serveraddr)
    TCPServerSocket.listen(int(numConn))
    print("El servidor para el juego del Buscaminas está disponible para partidas: ")
    servirPorSiempre(TCPServerSocket, listaConexiones,barrier, condicion_turno,first_candado)
