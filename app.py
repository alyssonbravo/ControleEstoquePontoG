import tkinter as tk
from tkinter import ttk
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Conectar ao banco de dados
conn = sqlite3.connect('estoque_ponto_g.db')
cursor = conn.cursor()

# Funções de inserção de dados na interface
def adicionar_entrada():
    produto = entry_produto.get()
    quantidade = int(entry_quantidade.get())
    preco_unitario = float(entry_preco.get())
    data = entry_data.get()
    inserir_entrada(produto, quantidade, preco_unitario, data)
    atualizar_tabela()

def adicionar_saida():
    produto = entry_produto.get()
    quantidade = int(entry_quantidade.get())
    preco_unitario = float(entry_preco.get())
    data = entry_data.get()
    inserir_saida(produto, quantidade, preco_unitario, data)
    atualizar_tabela()

# Função para atualizar a tabela na interface
def atualizar_tabela():
    for row in tree.get_children():
        tree.delete(row)
    estoque_atual = calcular_estoque()
    for index, row in estoque_atual.iterrows():
        tree.insert("", "end", values=(row['produto'], row['estoque_atual']))

# Funções para inserção de dados no banco de dados
def inserir_entrada(produto, quantidade, preco_unitario, data):
    cursor.execute('''
        INSERT INTO entradas (produto, quantidade, preco_unitario, data)
        VALUES (?, ?, ?, ?)
    ''', (produto, quantidade, preco_unitario, data))
    conn.commit()

def inserir_saida(produto, quantidade, preco_unitario, data):
    cursor.execute('''
        INSERT INTO saidas (produto, quantidade, preco_unitario, data)
        VALUES (?, ?, ?, ?)
    ''', (produto, quantidade, preco_unitario, data))
    conn.commit()

# Função para calcular o estoque atual
def calcular_estoque():
    entradas = pd.read_sql_query('SELECT * FROM entradas', conn)
    saidas = pd.read_sql_query('SELECT * FROM saidas', conn)

    total_entradas = entradas.groupby('produto')['quantidade'].sum()
    total_saidas = saidas.groupby('produto')['quantidade'].sum()

    estoque_atual = pd.DataFrame(total_entradas).join(pd.DataFrame(total_saidas), lsuffix='_entradas', rsuffix='_saidas')
    estoque_atual.fillna(0, inplace=True)
    estoque_atual['estoque_atual'] = estoque_atual['quantidade_entradas'] - estoque_atual['quantidade_saidas']

    estoque_atual.reset_index(inplace=True)
    estoque_atual = estoque_atual[['produto', 'estoque_atual']]
    return estoque_atual

# Interface gráfica com Tkinter
root = tk.Tk()
root.title("Sistema de Controle de Estoque")

# Labels e Entradas
label_produto = tk.Label(root, text="Produto:")
label_produto.grid(row=0, column=0)
entry_produto = tk.Entry(root)
entry_produto.grid(row=0, column=1)

label_quantidade = tk.Label(root, text="Quantidade:")
label_quantidade.grid(row=1, column=0)
entry_quantidade = tk.Entry(root)
entry_quantidade.grid(row=1, column=1)

label_preco = tk.Label(root, text="Preço Unitário:")
label_preco.grid(row=2, column=0)
entry_preco = tk.Entry(root)
entry_preco.grid(row=2, column=1)

label_data = tk.Label(root, text="Data (YYYY-MM-DD):")
label_data.grid(row=3, column=0)
entry_data = tk.Entry(root)
entry_data.grid(row=3, column=1)

# Botões para adicionar entradas e saídas
botao_adicionar_entrada = tk.Button(root, text="Adicionar Entrada", command=adicionar_entrada)
botao_adicionar_entrada.grid(row=4, column=0)

botao_adicionar_saida = tk.Button(root, text="Adicionar Saída", command=adicionar_saida)
botao_adicionar_saida.grid(row=4, column=1)

# Tabela de exibição do estoque atual
tree = ttk.Treeview(root, columns=('Produto', 'Estoque Atual'), show='headings')
tree.heading('Produto', text='Produto')
tree.heading('Estoque Atual', text='Estoque Atual')
tree.grid(row=5, column=0, columnspan=2)

# Atualizar a tabela ao iniciar
atualizar_tabela()

root.mainloop()

# Fechar a conexão com o banco de dados ao encerrar
conn.close()
