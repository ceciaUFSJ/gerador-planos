import streamlit as st
import zipfile
import shutil
import os
import xml..sax.saxutils as saxutils
from datetime import datetime
import requests
import time

# =========================
# Função para criar número em círculo vermelho UFSJ
def numero_circulo(num):
    return f"""
    <span style="
        display: inline-block;
        width: 2em;
        height: 2em;
        line-height: 2em;
        border-radius: 50%;
        background-color: #8B0000; /* vermelho UFSJ */
        color: white;
        text-align: center;
        font-weight: bold;
        margin-right: 0.3em;
    ">{num}</span>
    """

# =========================
# Textos padrão completos
texto_metodologia_padrao = """• Aulas expositivas com apresentação de conteúdo, discussão de problemas e aplicações;
• Aprendizagem por meio de solução de problemas;
• Desenvolvimento de algoritmos de forma dinâmica durante as aulas;
• Revisões de exemplos e atividades práticas que possam estimular a análise crítica;
• Estudos-de-casos que realcem a importância da disciplina;
• Exercícios extraclasse, provas e trabalhos práticos individuais e em grupos.
"""

texto_conteudo_programatico = """1 Nivelamento
1.1 Revisão de Algoritmos e Estruturas de Dados I, utilizando C/C++
1.2 Ponteiros
1.3 Vetores, Matrizes e Structs

2 Somatórios
2.1 Notação e manipulação de somas
2.2 Exemplos computacionais

3 Introdução
3.1 Noções de complexidade, contagem de operações
3.2 Pesquisa sequencial, binária e interpolada
3.3 Algoritmo de ordenação por seleção

4 Tempo de execução de programas
4.1 Definições
4.2 Complexidade de tempo x complexidade de espaço
4.3 Função de complexidade
4.4 Comportamento assintótico de um programa
4.5 Classes de comportamento assintótico
4.6 Técnicas de análise de algoritmos

5 Ordenação em memória principal
5.1 Método da bolha
5.2 Inserção
5.3 Seleção
5.4 Quicksort
5.6 Mergesort
5.7 Comparação entre os Métodos

6 Tipos abstratos de dados
6.1 Listas
6.2 Pilhas
6.3 Filas
"""

texto_controle_avaliacao = """• Cem pontos distribuídos ao longo do semestre da seguinte maneira:
a) 2 Provas – cada uma valendo 30 pontos – total de 60 pontos;
b) n listas de exercícios e práticas de laboratório ao longo do período – totalizando 10 pontos;
c) Trabalho Prático – 30 pontos.

• Prova Substitutiva: o aluno que ficar abaixo da média de 60% ao final do semestre, ou vier a perder alguma aplicação de prova, poderá submeter-se a uma prova de substituição/reposição no valor de 30 pontos. Neste caso, a nota da prova substitutiva substituirá a nota da menor prova realizada pelo aluno, ou irá repor a nota da prova perdida. Essa prova abordará todo o conteúdo da disciplina. Ao final do semestre, o aluno que não atingir 60 pontos totais não será aprovado.

• Será feito o controle de presença em todas as aulas por meio de chamadas. Por tratar-se de um curso presencial, o comparecimento do corpo discente às aulas é obrigatório. Em nenhuma hipótese será concedido abono de faltas, exceto nos casos previstos na legislação e no estatuto da universidade. O discente que não comparecer a, no mínimo, 75% das aulas será reprovado por infrequência.
"""

# =========================
# Configuração da página
# =========================
st.set_page_config(page_title="CECIA - Gerador de Planos", layout="wide")

# =========================
# CSS atualizado
st.markdown("""
<style>
.main > div.block-container { max-width: 90% !important; margin:auto;}
.header-bar {
    background-color: #FFECEC;  
    padding: 15px 20px;
    border-radius: 10px;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 20px;
    box-shadow: 0 4px 6px rgba(0,0,0,0.1);
}
.header-bar h2 {
    color: #8B0000;
    margin: 0;
    font-size: 22px;
    text-align: center;
}
.section-number {
    font-weight: bold; 
    color: #8B0000; 
    font-size: 24px;
    display: inline-block;
    width: 35px;
    height: 35px;
    text-align: center;
    border: 2px solid #8B0000;
    border-radius: 50%;
    margin-right: 8px;
}
.stTextArea>div>div>textarea, .stTextInput>div>input {
    background-color: white;  /* fundo branco */
    color: #8B0000;           /* texto vermelho UFSJ */
    padding: 12px; 
    border-radius: 8px;
    font-size: 15px;
    border: 1px solid #8B0000; /* borda vermelha opcional */
}
.stButton>button {
    background-color: #8B0000; 
    color: white; 
    padding: 0.6em 1.5em; 
    border-radius: 12px; 
    font-weight: bold;
    transition: all 0.3s ease;
}
.stButton>button:hover {
    background-color: #a30000;
    transform: scale(1.05);
}
</style>
""", unsafe_allow_html=True)

# =========================
# Cabeçalho com título + imagem
col1, col2 = st.columns([2, 1])  # 2 partes texto, 1 parte imagem

with col1:
    st.markdown(
        "<h2 style='color:#8B0000;'>CECIA - Coordenação do Curso de Engenharia da Computação com Inteligência Artificial</h2>",
        unsafe_allow_html=True
    )

with col2:
    st.image("cecia.png", width=120)  # imagem à direita

st.info("⚠️ Os textos abaixo são exemplos. Substitua pelo conteúdo que desejar.")

# =========================
# Seção 1️⃣ - Seleção de disciplina
st.markdown(f"{numero_circulo(1)} **Selecione a Disciplina**", unsafe_allow_html=True)

# Adicionando um timestamp para evitar cache
timestamp = int(time.time())
api_url = f"https://api.github.com/repos/ceciaUFSJ/planos-ensino/contents/modelos?ts={timestamp}"
r = requests.get(api_url)
arquivos_json = r.json()
disciplinas = [f['name'] for f in arquivos_json if f['name'].lower().endswith('.odt')]

if not disciplinas:
    st.error("❌ Nenhum modelo de disciplina (ODT) encontrado.")
else:
    disciplina_selecionada = st.selectbox("Disciplina:", disciplinas)

# =========================
# Ano e semestre
hoje = datetime.now()
ano_atual = hoje.year
mes_atual = hoje.month
semestre_sugerido = "2º" if mes_atual < 7 else "1º"
ano_sugerido = ano_atual if mes_atual < 7 else ano_atual + 1

# =========================
# Seção 2️⃣ - Campos do plano
st.markdown(f"{numero_circulo(2)} **Preencha os campos do plano**", unsafe_allow_html=True)

docente = st.text_input("Docente Responsável:", "João A. B. Cardoso")
coordenador = st.text_input("Coordenador do Curso:", "Pedro Mitsuo Shiroma")
ano_oferecimento = st.text_input("Ano de Oferecimento:", str(ano_sugerido))
semestre_oferecimento = st.text_input("Semestre de Oferecimento:", semestre_sugerido)
conteudo_programatico = st.text_area("Conteúdo Programático:", texto_conteudo_programatico, height=300)
metodologia = st.text_area("Metodologia de Ensino:", texto_metodologia_padrao, height=220)
controle_avaliacao = st.text_area("Controle de Frequência e Avaliação:", texto_controle_avaliacao, height=250)

# =========================
# Funções auxiliares
def transformar_em_paragrafos_justificados(texto):
    texto = saxutils.escape(texto)
    return "</text:p><text:p text:style-name=\"Justificado\">".join(texto.split("\n"))

def
