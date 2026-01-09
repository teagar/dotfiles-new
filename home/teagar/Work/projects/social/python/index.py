import tkinter as tk
import random
import math
import json
import os
import time
# import playsound  # apenas Windows, em Linux usar `playsound`

# ================= CONFIGURAÇÕES ==================
REMOVER_POR_VEZ = 10
SOM_ATIVO = False
FISICA_ATIVA = True
ARQUIVO_REMOVIDOS = "removidas.json"

# ================= BANCO DE DADOS ==================
# Exemplo reduzido: você pode carregar todas as cidades de um arquivo
cidades_por_estado = {
    "MG": ["Belo Horizonte", "Uberlândia", "Contagem", "Juiz de Fora", "Betim"],
    "SP": ["São Paulo", "Campinas", "Santos", "Ribeirão Preto", "Sorocaba"],
    "RJ": ["Rio de Janeiro", "Niterói", "Petrópolis", "Volta Redonda", "Campos"]
}

# Bandeiras fictícias por estado (use imagens reais depois)
bandeiras_estados = {
    "MG": "⚪🔺⚪",
    "SP": "⚫⚪",
    "RJ": "🌊🌞"
}

# Carregar removidos
if os.path.exists(ARQUIVO_REMOVIDOS):
    with open(ARQUIVO_REMOVIDOS, "r", encoding="utf-8") as f:
        cidades_removidas = json.load(f)
else:
    cidades_removidas = []

# Filtrar cidades ainda válidas
for estado in cidades_por_estado:
    cidades_por_estado[estado] = [c for c in cidades_por_estado[estado] if c not in cidades_removidas]

# ================= INTERFACE ==================
root = tk.Tk()
root.title("Roleta de Cidades do Brasil")

canvas = tk.Canvas(root, width=600, height=600, bg="white")
canvas.pack()

center_x, center_y = 300, 300
raio = 250

# Junta todas cidades disponíveis
todas_cidades = []
for estado, cidades in cidades_por_estado.items():
    for cidade in cidades:
        todas_cidades.append((estado, cidade))

num_setores = len(todas_cidades)

def desenhar_roleta(angulo_offset=0):
    canvas.delete("all")
    if num_setores == 0:
        canvas.create_text(center_x, center_y, text="SEM CIDADES", font=("Arial", 20, "bold"))
        return

    angulo_por_setor = 360 / num_setores

    for i, (estado, cidade) in enumerate(todas_cidades):
        angulo_inicial = i * angulo_por_setor + angulo_offset
        angulo_final = angulo_inicial + angulo_por_setor

        cor = "#%06x" % random.randint(0, 0xFFFFFF)

        canvas.create_arc(center_x - raio, center_y - raio,
                          center_x + raio, center_y + raio,
                          start=angulo_inicial, extent=angulo_por_setor,
                          fill=cor, outline="black")

        # Nome da cidade
        angulo_texto = math.radians(angulo_inicial + angulo_por_setor / 2)
        x_text = center_x + (raio - 70) * math.cos(angulo_texto)
        y_text = center_y - (raio - 70) * math.sin(angulo_texto)
        canvas.create_text(x_text, y_text, text=cidade, font=("Arial", 8))

    # Ponteiro
    canvas.create_polygon(center_x, center_y - raio - 20,
                          center_x - 15, center_y - raio,
                          center_x + 15, center_y - raio,
                          fill="red")

def tocar_som():
    if SOM_ATIVO:
        winsound.Beep(1000, 50)

def girar_roleta():
    global todas_cidades, cidades_removidas

    if not todas_cidades:
        return

    voltas = random.randint(5, 10)
    passos = num_setores * voltas + random.randint(0, num_setores - 1)

    for i in range(passos):
        desenhar_roleta(i * (360 / num_setores))
        tocar_som()
        root.update()
        time.sleep(0.02 if FISICA_ATIVA else 0.001)

    indice_final = passos % num_setores
    selecionada = todas_cidades[indice_final]

    # Remover cidades
    removidas = []
    for _ in range(REMOVER_POR_VEZ):
        if todas_cidades:
            cidade = todas_cidades.pop(indice_final % len(todas_cidades))
            removidas.append(cidade[1])
            cidades_removidas.append(cidade[1])

    # Salvar no arquivo
    with open(ARQUIVO_REMOVIDOS, "w", encoding="utf-8") as f:
        json.dump(cidades_removidas, f, ensure_ascii=False, indent=2)

    desenhar_roleta()
    mostrar_removidas(removidas)

def mostrar_removidas(removidas):
    win = tk.Toplevel(root)
    win.title("Cidades Eliminadas")
    for cidade in removidas:
        estado = None
        for est, lista in cidades_por_estado.items():
            if cidade in lista:
                estado = est
                break
        bandeira = bandeiras_estados.get(estado, "🏳️")
        tk.Label(win, text=f"{cidade} {bandeira}", font=("Arial", 12)).pack()

btn = tk.Button(root, text="GIRAR ROLETA", font=("Arial", 14, "bold"), command=girar_roleta)
btn.pack(pady=20)

desenhar_roleta()

root.mainloop()
