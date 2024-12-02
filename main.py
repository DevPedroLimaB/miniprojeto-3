import random
from queue import Queue
import pandas as pd
import matplotlib.pyplot as plt
import os

# Configuração inicial
NUM_SERVIDORES = 3
CAPACIDADE_SERVIDORES = [5, 7, 10]  # Capacidade de cada servidor
NUM_TIMESTEPS = 100  # Número de iterações da simulação
REQ_POR_TIMESTEP = (10, 20)  # Geração aleatória de solicitações por timestep
PROB_FALHA = 0.1  # Probabilidade de falha para cada atendente
BUFFER_LIMITE = 50  # Limite do buffer de solicitações

# Classes principais
class Atendente:
    def __init__(self, tipo, id):
        self.tipo = tipo
        self.id = id
        self.ativo = True

class Servidor:
    def __init__(self, nome, capacidade):
        self.nome = nome
        self.capacidade = capacidade
        self.atendentes = []
        self.filas = {"vendas": Queue(), "suporte": Queue()}

    def adicionar_atendente(self, atendente):
        if len(self.atendentes) < self.capacidade:
            self.atendentes.append(atendente)

    def processar_solicitacoes(self):
        atendimentos_realizados = 0
        for tipo in ["vendas", "suporte"]:
            while not self.filas[tipo].empty():
                atendente_disponivel = next((a for a in self.atendentes if a.tipo == tipo and a.ativo), None)
                if atendente_disponivel:
                    self.filas[tipo].get()
                    atendimentos_realizados += 1
                else:
                    break
        return atendimentos_realizados

class Supervisor:
    def __init__(self, servidores):
        self.servidores = servidores

    def monitorar(self, timestep):
        for servidor in self.servidores:
            for atendente in servidor.atendentes:
                if random.random() < PROB_FALHA:
                    atendente.ativo = False
                    print(f"Falha no atendente {atendente.id} ({atendente.tipo}) no {servidor.nome} no timestep {timestep}.")

# Simulação
def simular():
    # Inicializar servidores
    servidores = []
    for i in range(NUM_SERVIDORES):
        servidor = Servidor(f"Servidor-{i+1}", CAPACIDADE_SERVIDORES[i])
        servidores.append(servidor)
        # Adicionar atendentes aleatórios
        for _ in range(servidor.capacidade):
            tipo = "suporte" if random.random() < 0.5 else "vendas"
            servidor.adicionar_atendente(Atendente(tipo, f"{servidor.nome}-{_}"))
    
    supervisor = Supervisor(servidores)
    buffer_global = Queue(maxsize=BUFFER_LIMITE)
    logs = []
    
    for timestep in range(NUM_TIMESTEPS):
        print(f"\nTimestep {timestep+1}")
        
        # Gerar solicitações
        num_solicitacoes = random.randint(*REQ_POR_TIMESTEP)
        for _ in range(num_solicitacoes):
            tipo = "suporte" if random.random() < 0.5 else "vendas"
            if buffer_global.full():
                print("Buffer global estourou! Simulação encerrada por falha.")
                return logs
            buffer_global.put(tipo)
        
        # Distribuir solicitações entre servidores
        while not buffer_global.empty():
            tipo = buffer_global.get()
            servidores_disponiveis = [s for s in servidores if not s.filas[tipo].full()]
            if servidores_disponiveis:
                servidor = random.choice(servidores_disponiveis)
                servidor.filas[tipo].put(tipo)
        
        # Processar solicitações e monitorar falhas
        atendimentos = 0
        for servidor in servidores:
            atendimentos += servidor.processar_solicitacoes()
        
        supervisor.monitorar(timestep)
        
        # Registrar logs
        logs.append({
            "timestep": timestep,
            "atendimentos": atendimentos,
            "buffer_restante": buffer_global.qsize()
        })
    
    return logs

# Analisar Resultados
def analisar_logs(logs):
    df = pd.DataFrame(logs)
    
    # Salvar logs em CSV
    output_path = "outputs"
    os.makedirs(output_path, exist_ok=True)
    df.to_csv(f"{output_path}/logs.csv", index=False)
    
    # Gráfico de linha: Atendimentos por timestep
    plt.figure(figsize=(10, 5))
    plt.plot(df["timestep"], df["atendimentos"], label="Atendimentos")
    plt.xlabel("Timestep")
    plt.ylabel("Atendimentos")
    plt.title("Atendimentos por Timestep")
    plt.legend()
    plt.savefig(f"{output_path}/atendimentos_por_timestep.png")
    plt.show()

# Main
if __name__ == "__main__":
    logs = simular()
    if logs:
        analisar_logs(logs)
        print("Simulação concluída. Resultados salvos na pasta 'outputs'.")
