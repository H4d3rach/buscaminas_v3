import socket
import time 

#HOST = input("Ingrese la ip del host: ")
#PORT = int(input("Ingrese el puerto de salida: "))
HOST = "localhost"
PORT = 65432
buffer_size = 1024
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as TCPClientSocket:
    TCPClientSocket.connect((HOST, PORT))
    inicio = time.time()
    print("**************Bienvenido al jugo del Buscaminas******************")
    print("Esperando a los jugadores restantes...")
    determinacion_dificultad = TCPClientSocket.recv(buffer_size)
    print(determinacion_dificultad)
    if(int(determinacion_dificultad) == 1):
        dificultad_i = input("Ingrese la dificultad (Ej. Principiante / Avanzado): ")
        TCPClientSocket.sendall(dificultad_i.encode('utf-8'))
        print("Esperando al servidor")
    else:
        print("Su compañero elegirá la dificultad del juego")
    confirmacion = TCPClientSocket.recv(buffer_size)
    if confirmacion :
        print("Partida confirmada en breve se aparecerá el tablero")
        n = int(confirmacion)
        if n == 9:
            print("Su dificultad es principiante")
        elif n==16:
            print("Su dificultad es avanzado")
    elif not confirmacion:
        print("El otro jugador todavia no escoge la dificultad")
    tablero = []
    for i in range(n):
        tablero.append([])
        for j in range(n):
            tablero[i].append('-')
    def mostrarTablero(tablero):
        filas = 0
        columnas = 0
        counter1 = 1
        counter2 = 1
        while filas <= n :
            columnas = 0
            while columnas <= n :
                if filas == 0 and columnas == 0:
                    print(" ", end=" ")
                elif filas == 0 and columnas !=0:
                    print(str(counter1).zfill(2), end=" ")
                    counter1 = counter1 + 1
                elif filas != 0 and columnas ==0:
                    print(str(counter2).zfill(2), end=" ")
                    counter2 = counter2 + 1
                elif filas !=0 and columnas != 0 :
                    print(tablero[filas-1][columnas-1],end="  ")
                columnas = columnas + 1
            print("")
            filas = filas + 1
    controlador = 1
    confchar = int(TCPClientSocket.recv(buffer_size))
    print("Esto es confchar: ",confchar)
    caracter=input("Elija su caracter de tiro: ")
    TCPClientSocket.sendall(caracter.encode('utf-8'))
    while controlador:
        print("Esperando el turno")
        first_resp = int(TCPClientSocket.recv(buffer_size))
        print("Esto es firstresp",first_resp)
        if(first_resp==0):
            print("**************Buscaminas*****************")
            mostrarTablero(tablero)        
            tiro=input("Ingrese la coordenada de su tiro Ej((**,**)): ")
            print("El tiro es", tiro)
            TCPClientSocket.sendall(tiro.encode('utf-8'))
            resp_server = int(TCPClientSocket.recv(buffer_size))
            print("La respuesta del server es",resp_server)
            if resp_server == 4:
                print("Chispas encontraste una mina ")
                tablero[int(tiro[1:3])-1][int(tiro[4:6])-1] = '*'
                mostrarTablero(tablero)
                controlador=0
            elif resp_server == 1:
                print("Felicidades has ganado el juego :) ")
                tablero[int(tiro[1:3])-1][int(tiro[4:6])-1]=caracter
                i = 0
                while i < n:
                    j = 0
                    while j < n:
                        if tablero[i][j]=='-':
                            tablero[i][j]='*'
                        j = j +1
                    i = i + 1        
                mostrarTablero(tablero)
                controlador=0
            elif resp_server == 2:
                tablero[int(tiro[1:3])-1][int(tiro[4:6])-1]=caracter
                mostrarTablero(tablero)
            elif resp_server == 3:
                print("La casilla está fuera de rango ")
                mostrarTablero(tablero)
            elif resp_server == 5:
                print("La casilla ya ha sido ocupada antes ")
                mostrarTablero(tablero)
        else:
            print("Un jugador está tirando")
            resp_server = TCPClientSocket.recv(buffer_size)
            print("El respserver es = ",resp_server)
            filas = int(resp_server[1:3])-1
            columnas = int(resp_server[4:6])-1
            codigo = int(resp_server[8:9])
            charr = resp_server.decode('utf-8')
            newcaracter = charr[10:11]
            print(filas)
            print(columnas)
            print(codigo)
            print(newcaracter)
            if(codigo == 1):
                print("El jugador ",newcaracter," dio el tiro de gane")
                tablero[filas][columnas]=newcaracter
                i = 0
                while i < n:
                    j = 0
                    while j < n:
                        if tablero[i][j]=='-':
                            tablero[i][j]='*'
                        j = j +1
                    i = i + 1        
                mostrarTablero(tablero)
                controlador=0
            elif(codigo == 2):
                tablero[filas][columnas]=newcaracter
            elif(codigo == 3):
                print("El jugador ",newcaracter," dio una tirada fuera de rango")
            elif(codigo==4):
                print("Malas noticias, el jugador ",newcaracter," encontro una mina x.x")
                tablero[filas][columnas] = '*'
                mostrarTablero(tablero)
                controlador=0
            elif(codigo==5):
                print("El jugador ",newcaracter," tiro en una casilla que ya se había ocupado antes")
                mostrarTablero(tablero)
    time.sleep(1)
    fin = time.time()
    tiempotranscurrido = fin - inicio
    print("El tiempo desde que se conectó al servidor fue: ",tiempotranscurrido," segundos") 
            