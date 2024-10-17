
class Proceso:
    # Inicializa los atributos del proceso con el constructor __init__
    def __init__(self, pid, at, bt, queue, priority):
        self.pid = pid          # Identificador del proceso
        self.at = at            # Arrival Time (Tiempo de llegada)
        self.bt = bt            # Burst Time (Tiempo de ejecución)
        self.queue = queue      # Número de la cola en la que se encuentra el proceso
        self.priority = priority # Prioridad del proceso
        self.ct = 0             # Completion Time (Tiempo de finalización)
        self.wt = 0             # Waiting Time (Tiempo de espera)
        self.rt = 0             # Response Time (Tiempo de respuesta)
        self.tat = 0            # Turnaround Time (Tiempo de retorno)
        self.rct = bt           # Remaining Completion Time (Tiempo restante)
        self.first_ex = None    # Tiempo de la primera ejecución

class Planificador:
    # Inicializa el planificador con una lista de procesos
    def __init__(self, procesos):
        self.procesos = procesos

    # Algoritmo First-Come, First-Served (FCFS)
    def fcfs(self, procesos, tiempo_cpu=0):
        # Ordena los procesos por tiempo de llegada (AT) y, si es igual, por prioridad (mayor primero)
        procesos_ord = sorted(procesos, key=lambda proc: (proc.at, -proc.priority))
        #Recorre la lista de procesos ordenados y calcula las métricas de cada proceso
        for proceso in procesos_ord:
            proceso.ct = proceso.bt + tiempo_cpu  # CT
            proceso.tat = proceso.ct - proceso.at  # TAT
            proceso.wt = tiempo_cpu - proceso.at  # WT
            proceso.rt = tiempo_cpu  # RT
            tiempo_cpu += proceso.bt  # Actualiza el tiempo de la CPU
        return procesos_ord

    # Algoritmo Shortest Job First (SJF)
    def sjf(self, procesos, tiempo_cpu=0):
        procesos_ord = sorted(procesos, key=lambda proc: (proc.at, -proc.priority))
        procesos_finalizados = []
        while procesos_ord:  
            # Procesos disponibles de acuerdo a su AT y el tiempo de la CPU
            disponibles = [proc for proc in procesos_ord if proc.at <= tiempo_cpu]
            if disponibles:
                # Escoge el proceso con menor Burst Time
                proceso = min(disponibles, key=lambda proc: proc.bt)  
                procesos_ord.remove(proceso) # Elimina el proceso de la lista de procesos
                proceso.ct = proceso.bt + tiempo_cpu  
                proceso.tat = proceso.ct - proceso.at  
                proceso.wt = tiempo_cpu - proceso.at  
                proceso.rt = tiempo_cpu  
                tiempo_cpu += proceso.bt  
                procesos_finalizados.append(proceso) #Agrega el proceso a lista de finalizados
            else:
                tiempo_cpu += 1  # Si no hay procesos disponibles, el CPU avanza un tiempo
        return procesos_finalizados

    # Algoritmo Shortest Time to Completion First (STCF)
    def stcf(self, procesos, tiempo_cpu=0):
        procesos_ord = sorted(procesos, key=lambda proc: (proc.at, -proc.priority))
        procesos_finalizados = []
        while procesos_ord:
            disponibles = [proc for proc in procesos_ord if proc.at <= tiempo_cpu]  
            if disponibles:
                # Escoge el proceso con menor tiempo restante
                proceso = min(disponibles, key=lambda proc: proc.rct)  
                if proceso.rt == 0:
                    proceso.rt = tiempo_cpu  # Asigna el tiempo de respuesta de acuerdo al tiempo de CPU actual
                proceso.rct -= 1  # Decrementa el tiempo restante
                tiempo_cpu += 1  # Actualiza el tiempo del CPU
                if proceso.rct == 0:
                    proceso.ct = tiempo_cpu  
                    proceso.tat = proceso.ct - proceso.at 
                    proceso.wt = proceso.tat - proceso.bt  
                    procesos_finalizados.append(proceso)
                    procesos_ord.remove(proceso)
            else:
                tiempo_cpu += 1  # Si no hay procesos disponibles, el CPU avanza un tiempo 
        return procesos_finalizados

    # Algoritmo Round Robin
    def round_robin(self, procesos, quantum, tiempo_cpu=0):
        procesos_ord = sorted(procesos, key=lambda proc: (proc.at, -proc.priority))
        cant_procesos = len(procesos_ord) #Cantidad de procesos
        cola = procesos_ord[:]  # Copia de la lista de procesos en una cola
        completados = []
        #Hace mientras queden procesos por ejecutar
        while len(completados) != cant_procesos:
            disponibles = [proc for proc in cola if proc.at <= tiempo_cpu]  
            if disponibles:
                proceso = disponibles.pop(0)  # Toma el primer proceso disponible
                cola.remove(proceso) #Lo quita de la cola
                # Establece el tiempo de la primera ejecución del proceso
                if proceso.first_ex is None:
                    proceso.first_ex = tiempo_cpu  
                #Evalua si el tiempo restante del proceso es mayor al quantum
                if proceso.rct > quantum:
                    tiempo_cpu += quantum  # Actualiza el tiempo de la CPU
                    proceso.rct -= quantum  # Reduce el tiempo restante según el quantum
                    cola.append(proceso)  # Reingresa el proceso en la cola porque no ha terminado
                else:
                    tiempo_cpu += proceso.rct
                    proceso.ct = tiempo_cpu 
                    proceso.tat = proceso.ct - proceso.at  
                    proceso.wt = proceso.tat - proceso.bt  
                    proceso.rt = proceso.first_ex  
                    completados.append(proceso)
            else:
                tiempo_cpu += 1  # Si no hay procesos disponibles, el CPU avanza un tiempo
        return completados

    # Algoritmo Multi-Level Queue (MLQ)
    def mlq(self, quantum1, quantum2, alg):
        # Dividir procesos por colas
        procesos_cola1 = [proc for proc in self.procesos if proc.queue == 1]
        procesos_cola2 = [proc for proc in self.procesos if proc.queue == 2]
        procesos_cola3 = [proc for proc in self.procesos if proc.queue == 3]

        # Cola 1: Round Robin con quantum1
        procesos_cola1 = self.round_robin(procesos_cola1, quantum1, 0)
        #Se actualiza el tiempo CPU de acuerdo al máximo CT de los procesos de la cola 1 para pasarlo a la cola 2
        tiempo_cpu = max(proc.ct for proc in procesos_cola1) 

        # Cola 2: Round Robin con quantum2
        procesos_cola2 = self.round_robin(procesos_cola2, quantum2, tiempo_cpu)
        tiempo_cpu = max(proc.ct for proc in procesos_cola2) #se actualiza nuevamente para pasar al siguiente algoritmo

        # Cola 3: Algoritmo seleccionado
        if alg == 'SJF':
            procesos_cola3 = self.sjf(procesos_cola3, tiempo_cpu)
        elif alg == 'FCFS':
            procesos_cola3 = self.fcfs(procesos_cola3, tiempo_cpu)
        elif alg == 'STCF':
            procesos_cola3 = self.stcf(procesos_cola3, tiempo_cpu)

        # Retorna la lista de procesos finalizados
        return procesos_cola1 + procesos_cola2 + procesos_cola3

class Main:
    # Función para leer el archivo de entrada con los procesos
    def leer_txt(archivo):
        procesos = []
        with open(archivo, 'r') as file:
            for linea in file:
                if linea.startswith('#') or not linea:  # Ignora comentarios y líneas vacías
                    continue
                datos = linea.split('; ')  # Divide la línea en atributos
                pid = datos[0]
                bt = int(datos[1])
                at = int(datos[2])
                queue = int(datos[3])
                priority = int(datos[4])
                procesos.append(Proceso(pid, at, bt, queue, priority))  # Crea un objeto Proceso
        return procesos
    
    # Función para escribir el archivo de salida con los resultados
    def escribir_txt(resultados):
        promedios = {
            'wt': 0,
            'ct': 0,
            'rt': 0,
            'tat': 0
        }
    
        # Abre el archivo de salida para escribir
        with open('salida.txt', mode='w') as archivo_txt:
            archivo_txt.write(f"#Etiquetas = PID;BT;AT;Q;P;WT;CT;RT;TAT\n")  # Comentario etiquetas
    
            # Escribe los resultados de las metricas de cada proceso
            for proceso in resultados:
                promedios['wt'] += proceso.wt
                promedios['ct'] += proceso.ct
                promedios['rt'] += proceso.rt
                promedios['tat'] += proceso.tat
    
                archivo_txt.write(f"{proceso.pid}; {proceso.bt}; {proceso.at}; {proceso.queue}; "
                                  f"{proceso.priority}; {proceso.wt}; {proceso.ct}; {proceso.rt}; {proceso.tat}\n")
    
            # Escribe los promedios totales calculados
            archivo_txt.write(f"WT={promedios['wt']/len(resultados)}; "
                              f"CT={promedios['ct']/len(resultados)}; "
                              f"RT={promedios['rt']/len(resultados)}; "
                              f"TAT={promedios['tat']/len(resultados)}")
    
    # Lectura del archivo de entrada y ejecución del planificador
    procesos = leer_txt("mlq002.txt")
    planificador = Planificador(procesos)
    resultados = planificador.mlq(quantum1=1, quantum2=3, alg='SJF')
    escribir_txt(resultados)
    
    