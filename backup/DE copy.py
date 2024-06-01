from utils.constantes import SIZE_POBLATION, GENERATIONS
from core.Restricciones import Restricciones
from core.Algoritmo import Algoritmo
from tqdm import tqdm
import numpy as np


class DE(Algoritmo):
    # Poblacion
    poblacion = []
    # Fitness de los individuos de la poblacion
    fitness = np.zeros(SIZE_POBLATION)
    # Numero de infracciones que ocasiono un individuo de la poblacion
    noViolaciones = np.zeros(SIZE_POBLATION)
    
    # Factor de escalado
    F = 0.5
    # Tasa de recombinacion
    CR = 0.9

    def __init__(
        self,
        limite,  # Funcion para limitar la poblacion
        evaluar,  # Funcion para evaluar la poblacion
        superior,  # Limite Superior de la poblacion
        inferior,  # Limite inferior de la poblacion
        restriccion_de_funcion,  # Funcion para restringir la funcion objectiva
        g_funcs=[],  # Lista de funciones de desigualdad
        h_funcs=[],  # Lista de funciones de igualdad
    ):
        # Funcion limite a ocupar
        self.limite = limite
        # Funcion objetiva para obtener el fitness
        self.evaluar = evaluar
        # Limites superiores e inferiores
        self.superior = superior
        self.inferior = inferior
        # Funcion para restricciones funcionales
        self.restriccion_de_funcion = restriccion_de_funcion
        # Lista de restricciones de desigualdad
        self.g_funcs = g_funcs
        # Lista de restricciones de igualdad
        self.h_funcs = h_funcs
        
        # Creacion aleatoria de la poblacion
        self.poblacion = self.generar(self.superior, self.inferior)
        
        # Calculo de fitness y suma de violaciones
        self.calcularFitnessYSumaDeViolaciones()


    # Calculo del fitness para cada individuo de la poblacion
    # y calcular la suma de violaciones que tuvo el individuo
    def calcularFitnessYSumaDeViolaciones(self):
        # Calculo del fitness para cada particula
        for index, individuo in enumerate(self.poblacion):
            # Obtener el fitness
            fitness = self.evaluar(individuo)
            # Guardar fitness de la poblacion
            self.fitness[index] = fitness
            # Obtener la suma de violaciones
            total_de_violaciones = Restricciones.suma_violaciones(
                self.g_funcs, self.h_funcs, individuo
            )
            
            self.noViolaciones[index] = total_de_violaciones
    
    # Operador de mutacion        
    def mutacionDeIndividuo(self, idx):
        # Crear una lista de indices excluyendo a idx esto para no seleccionar idx
        index = [i for i in range(SIZE_POBLATION) if i != idx]
        # Selecciona tres individuos para mutar
        r1, r2, r3 = self.poblacion[np.random.choice(index, 3, replace=False)]
        # Genera el individuo mutado
        mutado = r1 + self.F * (r2 - r3)
         # Crear una lista de índices excluyendo a idx
        indices = np.arange(len(self.poblacion))
        indices = np.delete(indices, idx)
        
        # Selecciona tres índices al azar
        r1, r2, r3 = np.random.choice(indices, 3, replace=False)
        
        # Selecciona los individuos correspondientes
        X_r1 = self.poblacion[r1]
        X_r2 = self.poblacion[r2]
        X_r3 = self.poblacion[r3]
        
        # Genera el individuo mutado siguiendo la ecuación correcta
        mutado = X_r1 + self.F * (X_r2 - X_r3)
        
        # Regresar individuo mutado
        return mutado

    # Operador de cruzar
    def cruzeDeIndividuos(self, target, mutante):
        D = len(target)
        trial = np.copy(target)
        j_rand = np.random.randint(D)

        for j in range(D):
            if np.random.rand() < self.CR or j == j_rand:
                trial[j] = mutante[j]

        return trial

    
    # Operador de seleccion
    def seleccionDeIndividuos(self, idx, trial):
        current_fitness = self.evaluar(trial)
        
        current_violaciones = Restricciones.suma_violaciones(
                self.g_funcs, self.h_funcs, trial
        )
        
        
        # Se compara con los fitness 
        if not self.restriccion_de_funcion(current_fitness, current_violaciones, self.fitness[idx], self.noViolaciones[idx]):
            # Si es mejor se guarda en la poblacion idx
            self.fitness[idx] = current_fitness
            # Y se guarda el individuo de prueba en la poblacion
            self.noViolaciones[idx] = current_violaciones
            # Se guarda la violaciones del individuo de prueba
            self.poblacion[idx] = trial
   

    def reporte(self):
        best_idx = np.argmin(self.fitness)
        
        print("================================")
        print("Solución Óptima")
        print("Individuo:", self.poblacion[best_idx])
        print("Aptitud (Fitness):", self.fitness[best_idx])
        print("Num Violaciones:", self.noViolaciones[best_idx])
        print("================================")
    
    # Funcion principal para ejecutar el algoritmo
    def run(self):
        for _ in tqdm(range(GENERATIONS), desc="Evolucionando"):
            for i in range(SIZE_POBLATION):
                objetivo = self.poblacion[i]
                mutante = self.mutacionDeIndividuo(i)
                prueba = self.cruzeDeIndividuos(objetivo, mutante)
                prueba = self.limite(self.superior, self.inferior, prueba)
                self.seleccionDeIndividuos(i, prueba)
        
        self.reporte()