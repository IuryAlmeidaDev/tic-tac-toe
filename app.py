import tkinter as tk
from tkinter import messagebox, ttk
import random
import math
import threading
import time

# --- Classes do Algoritmo Genético (do código original) ---

class EstrategiaOponente:
    """Diferentes níveis de oponentes para treinar contra."""
    
    @staticmethod
    def aleatorio(tabuleiro):
        validas = obter_jogadas_validas(tabuleiro)
        return random.choice(validas) if validas else -1
    
    @staticmethod
    def defensivo(tabuleiro):
        validas = obter_jogadas_validas(tabuleiro)
        if not validas:
            return -1
        
        for pos in validas:
            temp = tabuleiro.copy()
            temp[pos] = 1
            if verificar_vitoria(temp) == 1:
                return pos
        
        for pos in validas:
            temp = tabuleiro.copy()
            temp[pos] = 2
            if verificar_vitoria(temp) == 2:
                return pos
        
        if 4 in validas:
            return 4
        
        cantos = [0, 2, 6, 8]
        cantos_validos = [c for c in cantos if c in validas]
        if cantos_validos:
            return random.choice(cantos_validos)
        
        return random.choice(validas)
    
    @staticmethod
    def inteligente(tabuleiro):
        validas = obter_jogadas_validas(tabuleiro)
        if not validas:
            return -1
        
        for pos in validas:
            temp = tabuleiro.copy()
            temp[pos] = 2
            if verificar_vitoria(temp) == 2:
                return pos
        
        for pos in validas:
            temp = tabuleiro.copy()
            temp[pos] = 1
            if verificar_vitoria(temp) == 1:
                return pos
        
        melhor_pos = None
        max_ameacas = 0
        
        for pos in validas:
            temp = tabuleiro.copy()
            temp[pos] = 2
            ameacas = contar_ameacas(temp, 2)
            if ameacas > max_ameacas:
                max_ameacas = ameacas
                melhor_pos = pos
        
        if melhor_pos is not None:
            return melhor_pos
        
        if 4 in validas:
            return 4
        
        cantos = [0, 2, 6, 8]
        cantos_validos = [c for c in cantos if c in validas]
        if cantos_validos:
            return random.choice(cantos_validos)
        
        return random.choice(validas)

def criar_tabuleiro():
    return [0] * 9

def verificar_vitoria(tabuleiro):
    linhas_vitoria = [
        (0, 1, 2), (3, 4, 5), (6, 7, 8),
        (0, 3, 6), (1, 4, 7), (2, 5, 8),
        (0, 4, 8), (2, 4, 6)
    ]
    for a, b, c in linhas_vitoria:
        if tabuleiro[a] == tabuleiro[b] == tabuleiro[c] and tabuleiro[a] != 0:
            return tabuleiro[a]
    
    if 0 not in tabuleiro:
        return -1
        
    return 0

def contar_ameacas(tabuleiro, jogador):
    linhas = [
        (0, 1, 2), (3, 4, 5), (6, 7, 8),
        (0, 3, 6), (1, 4, 7), (2, 5, 8),
        (0, 4, 8), (2, 4, 6)
    ]
    ameacas = 0
    for a, b, c in linhas:
        valores = [tabuleiro[a], tabuleiro[b], tabuleiro[c]]
        if valores.count(jogador) == 2 and valores.count(0) == 1:
            ameacas += 1
    return ameacas

def obter_jogadas_validas(tabuleiro):
    return [i for i, valor in enumerate(tabuleiro) if valor == 0]

class CromossomoAvancado:
    def __init__(self):
        self.prioridades = list(range(1, 10))
        random.shuffle(self.prioridades)
        
        self.peso_centro = random.uniform(0, 10)
        self.peso_cantos = random.uniform(0, 10)
        self.peso_laterais = random.uniform(0, 10)
        self.peso_bloqueio = random.uniform(0, 10)
        self.peso_ataque = random.uniform(0, 10)
        self.agressividade = random.uniform(0, 1)
    
    def escolher_jogada(self, tabuleiro):
        validas = obter_jogadas_validas(tabuleiro)
        if not validas:
            return -1
        
        for pos in validas:
            temp = tabuleiro.copy()
            temp[pos] = 1
            if verificar_vitoria(temp) == 1:
                return pos
        
        bloqueio_necessario = None
        for pos in validas:
            temp = tabuleiro.copy()
            temp[pos] = 2
            if verificar_vitoria(temp) == 2:
                bloqueio_necessario = pos
                break
        
        if bloqueio_necessario is not None and random.random() > self.agressividade:
            return bloqueio_necessario
        
        melhor_pontuacao = float('-inf')
        melhor_posicao = None
        
        for pos in validas:
            pontuacao = 0
            
            idx_prioridade = self.prioridades.index(pos + 1)
            pontuacao += (9 - idx_prioridade) * 2
            
            if pos == 4:
                pontuacao += self.peso_centro
            elif pos in [0, 2, 6, 8]:
                pontuacao += self.peso_cantos
            else:
                pontuacao += self.peso_laterais
            
            temp = tabuleiro.copy()
            temp[pos] = 1
            ameacas_criadas = contar_ameacas(temp, 1)
            pontuacao += ameacas_criadas * self.peso_ataque
            
            ameacas_oponente = contar_ameacas(tabuleiro, 2)
            if pos == bloqueio_necessario:
                pontuacao += self.peso_bloqueio
            
            pontuacao += random.uniform(-1, 1)
            
            if pontuacao > melhor_pontuacao:
                melhor_pontuacao = pontuacao
                melhor_posicao = pos
        
        return melhor_posicao if melhor_posicao is not None else random.choice(validas)
    
    def copy(self):
        novo = object.__new__(CromossomoAvancado)
        novo.prioridades = self.prioridades.copy()
        novo.peso_centro = self.peso_centro
        novo.peso_cantos = self.peso_cantos
        novo.peso_laterais = self.peso_laterais
        novo.peso_bloqueio = self.peso_bloqueio
        novo.peso_ataque = self.peso_ataque
        novo.agressividade = self.agressividade
        return novo

# --- Interface Gráfica ---

class JogoDaVelhaGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Jogo da Velha - IA Evoluída (AG)")
        self.root.geometry("900x800")
        self.root.configure(bg='#2c3e50')
        
        self.melhor_ia = None
        self.tabuleiro = criar_tabuleiro()
        self.jogador_atual = 1
        self.game_mode = None
        self.primeiro_jogador = None
        self.placar = {'X': 0, 'O': 0, 'Empates': 0}
        self.ia_pensando = False
        self.botoes = []
        
        self.criar_tela_inicial()
    
    def criar_tela_inicial(self):
        self.limpar_tela()
        
        # Título
        titulo = tk.Label(
            self.root,
            text="🧬 JOGO DA VELHA 🧬",
            font=('Arial', 32, 'bold'),
            bg='#2c3e50',
            fg='#ecf0f1'
        )
        titulo.pack(pady=30)
        
        subtitulo = tk.Label(
            self.root,
            text="Inteligência Artificial Evoluída\ncom Algoritmo Genético",
            font=('Arial', 14),
            bg='#2c3e50',
            fg='#bdc3c7'
        )
        subtitulo.pack(pady=10)
        
        # Frame para botões
        frame_botoes = tk.Frame(self.root, bg='#2c3e50')
        frame_botoes.pack(pady=50)
        
        # Botão Treinar IA
        btn_treinar = tk.Button(
            frame_botoes,
            text="🧠 Treinar IA com AG",
            font=('Arial', 16, 'bold'),
            bg='#9b59b6',
            fg='white',
            padx=30,
            pady=15,
            command=self.treinar_ia,
            cursor='hand2',
            relief='raised',
            bd=3
        )
        btn_treinar.pack(pady=10)
        
        # Botão Jogar contra IA
        btn_ia = tk.Button(
            frame_botoes,
            text="🤖 Jogar contra IA",
            font=('Arial', 16, 'bold'),
            bg='#3498db',
            fg='white',
            padx=30,
            pady=15,
            command=lambda: self.escolher_modo('ia'),
            cursor='hand2',
            relief='raised',
            bd=3,
            state='disabled' if not self.melhor_ia else 'normal'
        )
        btn_ia.pack(pady=10)
        self.btn_jogar_ia = btn_ia
        
        # Botão 2 Jogadores
        btn_pvp = tk.Button(
            frame_botoes,
            text="👥 2 Jogadores",
            font=('Arial', 16, 'bold'),
            bg='#1abc9c',
            fg='white',
            padx=30,
            pady=15,
            command=lambda: self.escolher_modo('pvp'),
            cursor='hand2',
            relief='raised',
            bd=3
        )
        btn_pvp.pack(pady=10)
        
        # Rodapé
        rodape = tk.Label(
            self.root,
            text="IFMT - Algoritmos Genéticos",
            font=('Arial', 10),
            bg='#2c3e50',
            fg='#7f8c8d'
        )
        rodape.pack(side='bottom', pady=20)
    
    def treinar_ia(self):
        self.limpar_tela()
        
        titulo = tk.Label(
            self.root,
            text="🧬 TREINAMENTO EM ANDAMENTO",
            font=('Arial', 24, 'bold'),
            bg='#2c3e50',
            fg='#ecf0f1'
        )
        titulo.pack(pady=30)
        
        self.label_geracao = tk.Label(
            self.root,
            text="Preparando população inicial...",
            font=('Arial', 14),
            bg='#2c3e50',
            fg='#bdc3c7'
        )
        self.label_geracao.pack(pady=20)
        
        # Barra de progresso
        self.progress = ttk.Progressbar(
            self.root,
            length=500,
            mode='determinate',
            maximum=50
        )
        self.progress.pack(pady=20)
        
        self.texto_status = tk.Text(
            self.root,
            width=70,
            height=15,
            font=('Courier', 10),
            bg='#34495e',
            fg='#ecf0f1',
            state='disabled'
        )
        self.texto_status.pack(pady=20)
        
        # Inicia treinamento em thread separada
        thread = threading.Thread(target=self.executar_treinamento)
        thread.daemon = True
        thread.start()
    
    def executar_treinamento(self):
        TAMANHO_POPULACAO = 200
        NUM_GERACOES = 100
        NUM_JOGOS_FITNESS = 100
        
        populacao = [CromossomoAvancado() for _ in range(TAMANHO_POPULACAO)]
        
        for geracao in range(NUM_GERACOES):
            # Calcula fitness
            fitnesses = []
            for cromossomo in populacao:
                vitorias = 0
                empates = 0
                
                for _ in range(NUM_JOGOS_FITNESS):
                    resultado = self.simular_jogo_treinamento(cromossomo)
                    if resultado == 1:
                        vitorias += 1
                    elif resultado == -1:
                        empates += 1
                
                fitness = (vitorias * 3) + (empates * 1)
                fitnesses.append({'fitness': fitness, 'vitorias': vitorias, 'empates': empates})
            
            # Encontra melhor
            fitness_valores = [f['fitness'] for f in fitnesses]
            idx_melhor = fitness_valores.index(max(fitness_valores))
            melhor_local = populacao[idx_melhor]
            melhor_fitness = fitnesses[idx_melhor]
            
            # Atualiza interface
            self.root.after(0, self.atualizar_treinamento, geracao, melhor_fitness)
            
            # Nova geração
            nova_populacao = [melhor_local.copy()]
            
            while len(nova_populacao) < TAMANHO_POPULACAO:
                pai1 = self.selecao_torneio(populacao, fitnesses)
                pai2 = self.selecao_torneio(populacao, fitnesses)
                
                filho = self.crossover(pai1, pai2)
                filho = self.mutacao(filho, 0.1)
                nova_populacao.append(filho)
            
            populacao = nova_populacao
        
        self.melhor_ia = melhor_local
        self.root.after(0, self.finalizar_treinamento)
    
    def simular_jogo_treinamento(self, cromossomo):
        tabuleiro = criar_tabuleiro()
        jogador_atual = 1
        
        while verificar_vitoria(tabuleiro) == 0:
            if jogador_atual == 1:
                jogada = cromossomo.escolher_jogada(tabuleiro)
            else:
                jogada = EstrategiaOponente.inteligente(tabuleiro)
            
            if jogada == -1:
                break
            
            tabuleiro[jogada] = jogador_atual
            jogador_atual = 3 - jogador_atual
        
        return verificar_vitoria(tabuleiro)
    
    def selecao_torneio(self, populacao, fitnesses, tamanho=3):
        indices = random.sample(range(len(populacao)), tamanho)
        candidatos = [(populacao[i], fitnesses[i]['fitness']) for i in indices]
        candidatos.sort(key=lambda x: x[1], reverse=True)
        return candidatos[0][0]
    
    def crossover(self, pai1, pai2):
        filho = object.__new__(CromossomoAvancado)
        filho.prioridades = [0] * 9
        
        tamanho = len(pai1.prioridades)
        ponto1 = random.randint(0, tamanho - 2)
        ponto2 = random.randint(ponto1 + 1, tamanho - 1)
        
        secao_central = pai1.prioridades[ponto1:ponto2 + 1]
        filho.prioridades[ponto1:ponto2 + 1] = secao_central
        
        restantes = [gene for gene in pai2.prioridades if gene not in secao_central]
        idx = 0
        for i in range(tamanho):
            if filho.prioridades[i] == 0:
                filho.prioridades[i] = restantes[idx]
                idx += 1
        
        alpha = random.random()
        filho.peso_centro = alpha * pai1.peso_centro + (1 - alpha) * pai2.peso_centro
        filho.peso_cantos = alpha * pai1.peso_cantos + (1 - alpha) * pai2.peso_cantos
        filho.peso_laterais = alpha * pai1.peso_laterais + (1 - alpha) * pai2.peso_laterais
        filho.peso_bloqueio = alpha * pai1.peso_bloqueio + (1 - alpha) * pai2.peso_bloqueio
        filho.peso_ataque = alpha * pai1.peso_ataque + (1 - alpha) * pai2.peso_ataque
        filho.agressividade = alpha * pai1.agressividade + (1 - alpha) * pai2.agressividade
        
        return filho
    
    def mutacao(self, cromossomo, taxa):
        if random.random() < taxa:
            idx1, idx2 = random.sample(range(9), 2)
            cromossomo.prioridades[idx1], cromossomo.prioridades[idx2] = \
                cromossomo.prioridades[idx2], cromossomo.prioridades[idx1]
        
        if random.random() < taxa:
            atributos = ['peso_centro', 'peso_cantos', 'peso_laterais', 
                        'peso_bloqueio', 'peso_ataque']
            attr = random.choice(atributos)
            valor = getattr(cromossomo, attr)
            setattr(cromossomo, attr, max(0, min(10, valor + random.gauss(0, 1))))
        
        return cromossomo
    
    def atualizar_treinamento(self, geracao, fitness_info):
        self.label_geracao.config(
            text=f"Geração {geracao + 1}/50 - Vitórias: {fitness_info['vitorias']}/50"
        )
        self.progress['value'] = geracao + 1
        
        self.texto_status.config(state='normal')
        self.texto_status.insert(
            'end',
            f"Gen {geracao+1:2d} | Fitness: {fitness_info['fitness']:4.0f} | "
            f"V: {fitness_info['vitorias']:2d} E: {fitness_info['empates']:2d}\n"
        )
        self.texto_status.see('end')
        self.texto_status.config(state='disabled')
    
    def finalizar_treinamento(self):
        messagebox.showinfo(
            "Treinamento Concluído!",
            "✅ A IA foi treinada com sucesso!\n\n"
            "Agora você pode jogar contra ela!"
        )
        self.criar_tela_inicial()
    
    def escolher_modo(self, modo):
        self.game_mode = modo
        self.cara_ou_coroa()
    
    def cara_ou_coroa(self):
        self.limpar_tela()
        
        titulo = tk.Label(
            self.root,
            text="🪙 CARA OU COROA?",
            font=('Arial', 28, 'bold'),
            bg='#2c3e50',
            fg='#ecf0f1'
        )
        titulo.pack(pady=30)
        
        instrucao = tk.Label(
            self.root,
            text="Quem começa a partida?",
            font=('Arial', 16),
            bg='#2c3e50',
            fg='#bdc3c7'
        )
        instrucao.pack(pady=20)
        
        frame_moedas = tk.Frame(self.root, bg='#2c3e50')
        frame_moedas.pack(pady=50)
        
        btn_cara = tk.Button(
            frame_moedas,
            text="🟡\nCARA",
            font=('Arial', 20, 'bold'),
            bg='#f39c12',
            fg='white',
            width=10,
            height=5,
            command=lambda: self.girar_moeda('cara'),
            cursor='hand2'
        )
        btn_cara.pack(side='left', padx=20)
        
        btn_coroa = tk.Button(
            frame_moedas,
            text="⚪\nCOROA",
            font=('Arial', 20, 'bold'),
            bg='#95a5a6',
            fg='white',
            width=10,
            height=5,
            command=lambda: self.girar_moeda('coroa'),
            cursor='hand2'
        )
        btn_coroa.pack(side='left', padx=20)
    
    def girar_moeda(self, escolha):
        self.limpar_tela()
        
        label_girando = tk.Label(
            self.root,
            text="🪙 Girando a moeda...",
            font=('Arial', 24, 'bold'),
            bg='#2c3e50',
            fg='#ecf0f1'
        )
        label_girando.pack(expand=True)
        
        self.root.after(2000, lambda: self.mostrar_resultado_moeda(escolha))
    
    def mostrar_resultado_moeda(self, escolha):
        resultado = random.choice(['cara', 'coroa'])
        
        self.limpar_tela()
        
        if escolha == resultado:
            texto = f"✅ Resultado: {resultado.upper()}!\n\nVocê começa! (X)"
            self.primeiro_jogador = 1
            self.jogador_atual = 1
        else:
            texto = f"❌ Resultado: {resultado.upper()}!\n\n"
            if self.game_mode == 'ia':
                texto += "A IA começa! (O)"
                self.primeiro_jogador = 2
                self.jogador_atual = 2
            else:
                texto += "Jogador O começa!"
                self.primeiro_jogador = 2
                self.jogador_atual = 2
        
        label_resultado = tk.Label(
            self.root,
            text=texto,
            font=('Arial', 20, 'bold'),
            bg='#2c3e50',
            fg='#ecf0f1'
        )
        label_resultado.pack(expand=True)
        
        self.root.after(2000, self.iniciar_jogo)
    
    def iniciar_jogo(self):
        self.limpar_tela()
        self.tabuleiro = criar_tabuleiro()
        self.botoes = []
        
        # Header
        frame_header = tk.Frame(self.root, bg='#2c3e50')
        frame_header.pack(pady=20)
        
        btn_menu = tk.Button(
            frame_header,
            text="← Menu",
            font=('Arial', 12),
            bg='#34495e',
            fg='white',
            command=self.criar_tela_inicial,
            cursor='hand2'
        )
        btn_menu.pack(side='left', padx=20)
        
        self.label_status = tk.Label(
            frame_header,
            text=f"Vez de: {'X' if self.jogador_atual == 1 else 'O'}",
            font=('Arial', 18, 'bold'),
            bg='#2c3e50',
            fg='#ecf0f1'
        )
        self.label_status.pack(side='left', padx=50)
        
        # Placar
        frame_placar = tk.Frame(frame_header, bg='#34495e', relief='raised', bd=2)
        frame_placar.pack(side='left', padx=20)
        
        tk.Label(frame_placar, text="Placar", font=('Arial', 10, 'bold'), 
                bg='#34495e', fg='white').pack()
        tk.Label(frame_placar, text=f"X: {self.placar['X']}", 
                font=('Arial', 10), bg='#34495e', fg='#3498db').pack()
        tk.Label(frame_placar, text=f"O: {self.placar['O']}", 
                font=('Arial', 10), bg='#34495e', fg='#e74c3c').pack()
        tk.Label(frame_placar, text=f"Empates: {self.placar['Empates']}", 
                font=('Arial', 10), bg='#34495e', fg='#95a5a6').pack()
        
        # Tabuleiro
        frame_tabuleiro = tk.Frame(self.root, bg='#2c3e50')
        frame_tabuleiro.pack(expand=True)
        
        for i in range(9):
            btn = tk.Button(
                frame_tabuleiro,
                text='',
                font=('Arial', 48, 'bold'),
                width=4,
                height=2,
                bg='#ecf0f1',
                fg='#2c3e50',
                command=lambda idx=i: self.fazer_jogada(idx),
                cursor='hand2',
                relief='raised',
                bd=3
            )
            btn.grid(row=i//3, column=i%3, padx=5, pady=5)
            self.botoes.append(btn)
        
        # Se IA começa, faz jogada
        if self.game_mode == 'ia' and self.jogador_atual == 2:
            self.root.after(1000, self.jogada_ia)
    
    def fazer_jogada(self, posicao):
        if self.tabuleiro[posicao] != 0 or self.ia_pensando:
            return
        
        self.tabuleiro[posicao] = self.jogador_atual
        simbolo = 'X' if self.jogador_atual == 1 else 'O'
        cor = '#3498db' if self.jogador_atual == 1 else '#e74c3c'
        self.botoes[posicao].config(text=simbolo, fg=cor, state='disabled')
        
        resultado = verificar_vitoria(self.tabuleiro)
        if resultado != 0:
            self.fim_de_jogo(resultado)
            return
        
        self.jogador_atual = 3 - self.jogador_atual
        self.label_status.config(text=f"Vez de: {'X' if self.jogador_atual == 1 else 'O'}")
        
        if self.game_mode == 'ia' and self.jogador_atual == 2:
            self.root.after(800, self.jogada_ia)
    
    def jogada_ia(self):
        self.ia_pensando = True
        self.label_status.config(text="🤖 IA pensando...")
        
        posicao = self.melhor_ia.escolher_jogada(self.tabuleiro)
        
        if posicao != -1:
            self.tabuleiro[posicao] = 2
            self.botoes[posicao].config(text='O', fg='#e74c3c', state='disabled')
            
            resultado = verificar_vitoria(self.tabuleiro)
            if resultado != 0:
                self.fim_de_jogo(resultado)
                self.ia_pensando = False
                return
            
            self.jogador_atual = 1
            self.label_status.config(text="Vez de: X")
        
        self.ia_pensando = False
    
    def fim_de_jogo(self, resultado):
        if resultado == 1:
            vencedor = 'X'
            self.placar['X'] += 1
            mensagem = "🎉 X Venceu!"
            if self.game_mode == 'ia':
                mensagem += "\n\nParabéns, você ganhou da IA!"
            # Vencedor joga primeiro na próxima
            self.primeiro_jogador = 1
        elif resultado == 2:
            vencedor = 'O'
            self.placar['O'] += 1
            mensagem = "🎉 O Venceu!"
            if self.game_mode == 'ia':
                mensagem += "\n\n🤖 A IA venceu!"
            else:
                mensagem += "\n\nParabéns Jogador O!"
            # Vencedor joga primeiro na próxima
            self.primeiro_jogador = 2
        else:
            vencedor = None
            self.placar['Empates'] += 1
            mensagem = "🤝 Empate (Velha)!"
            # Em caso de empate, alterna quem começa
            self.primeiro_jogador = 3 - self.primeiro_jogador
        
        for btn in self.botoes:
            btn.config(state='disabled')
        
        # Informa quem vai começar na próxima partida
        proximo = "X" if self.primeiro_jogador == 1 else "O"
        if self.game_mode == 'ia':
            proximo_texto = "Você" if self.primeiro_jogador == 1 else "A IA"
        else:
            proximo_texto = f"Jogador {proximo}"
        
        mensagem += f"\n\nPróxima partida: {proximo_texto} começa!"
        
        resposta = messagebox.askyesno("Fim de Jogo", mensagem + "\n\nJogar novamente?")
        
        if resposta:
            self.jogador_atual = self.primeiro_jogador
            self.iniciar_jogo()
        else:
            self.criar_tela_inicial()
    
    def limpar_tela(self):
        for widget in self.root.winfo_children():
            widget.destroy()

# --- Execução ---
if __name__ == "__main__":
    root = tk.Tk()
    app = JogoDaVelhaGUI(root)
    root.mainloop()