import streamlit as st
import zipfile
import shutil
import os
import xml.sax.saxutils as saxutils
from datetime import datetime
import requests

# =========================
# Textos padrão completos
# =========================
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
# CSS moderno
# =========================
st.markdown("""
<style>
.main > div.block-container { max-width: 60% !important; margin:auto;}
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
    font-weight:bold; 
    color:#8B0000; 
    font-size:24px;
    display:inline-block;
    width:35px;
    height:35px;
    text-align:center;
    border:2px solid #8B0000;
    border-radius:50%;
    margin-right:8px;
}
.stTextArea>div>div>textarea, .stTextInput>div>input {
    background-color: #FFECEC; 
    color: #8B0000; 
    padding:12px; 
    border-radius:8px;
    font-size:15px;
}
.stButton>button {
    background-color: #8B0000; 
    color: white; 
    padding:0.6em 1.5em; 
    border-radius:12px; 
    font-weight:bold;
    transition: all 0.3s ease;
}
.stButton>button:hover {
    background-color:#a30000;
    transform: scale(1.05);
}
</style>
""", unsafe_allow_html=True)

# =========================
# Cabeçalho com título + imagem
# =========================
col1, col2 = st.columns([4, 1])
with col1:
    st.markdown("<div class='header-bar'><h2>CECIA - Coordenação do Curso de Engenharia da Computação com Inteligência Artificial</h2></div>", unsafe_allow_html=True)
with col2:
    st.image("cecia.png", width=120)

st.info("⚠️ Os textos abaixo são exemplos. Substitua pelo conteúdo que desejar. 🎨")

# =========================
# Seleção de disciplina
# =========================
st.markdown("<span class='section-number'>1️⃣</span> Selecione a Disciplina", unsafe_allow_html=True)
api_url = "https://api.github.com/repos/ceciaUFSJ/planos-ensino/contents/modelos"
r = requests.get(api_url)
arquivos_json = r.json()
disciplinas = [f['name'] for f in arquivos_json if f['name'].lower().endswith('.odt')]
disciplina_selecionada = st.selectbox("Disciplina:", disciplinas) if disciplinas else st.error("❌ Nenhum modelo ODT encontrado.")

# =========================
# Ano e semestre
# =========================
hoje = datetime.now()
ano_atual = hoje.year
mes_atual = hoje.month
semestre_sugerido = "2º" if mes_atual < 7 else "1º"
ano_sugerido = ano_atual if mes_atual < 7 else ano_atual + 1

# =========================
# Campos do plano
# =========================
st.markdown("<span class='section-number'>2️⃣</span> Preencha os campos do plano", unsafe_allow_html=True)
docente = st.text_input("Docente Responsável:", "João A. B. Cardoso")
coordenador = st.text_input("Coordenador do Curso:", "Mario C. D. Silva")
ano_oferecimento = st.text_input("Ano de Oferecimento:", str(ano_sugerido))
semestre_oferecimento = st.text_input("Semestre de Oferecimento:", semestre_sugerido)
conteudo_programatico = st.text_area("Conteúdo Programático:", texto_conteudo_programatico, height=300)
metodologia = st.text_area("Metodologia de Ensino:", texto_metodologia_padrao, height=220)
controle_avaliacao = st.text_area("Controle de Frequência e Avaliação:", texto_controle_avaliacao, height=250)

# =========================
# Funções auxiliares
# =========================
def transformar_em_paragrafos_justificados(texto):
    texto = saxutils.escape(texto)
    return "</text:p><text:p text:style-name=\"Justificado\">".join(texto.split("\n"))

def gerar_odt():
    git_url_raw = f"https://raw.githubusercontent.com/ceciaUFSJ/planos-ensino/main/modelos/{disciplina_selecionada}"
    r = requests.get(git_url_raw)
    with open("PLANO_BASE.odt", "wb") as f:
        f.write(r.content)

    pasta = "odt_temp"
    if os.path.exists(pasta):
        shutil.rmtree(pasta)
    os.mkdir(pasta)

    with zipfile.ZipFile("PLANO_BASE.odt", 'r') as zip_ref:
        zip_ref.extractall(pasta)

    caminho_xml = os.path.join(pasta, "content.xml")
    with open(caminho_xml, "r", encoding="utf-8") as f:
        xml = f.read()

    if "style:name=\"Justificado\"" not in xml:
        estilo = """
        <style:style style:name="Justificado" style:family="paragraph">
            <style:paragraph-properties fo:text-align="justify"/>
            <style:text-properties fo:font-size="10pt"/>
        </style:style>
        """
        xml = xml.replace("</office:automatic-styles>", estilo + "\n</office:automatic-styles>")

    xml = xml.replace("drrrr", saxutils.escape(docente))
    xml = xml.replace("dcccc", saxutils.escape(coordenador))
    xml = xml.replace("ANOof", saxutils.escape(ano_oferecimento))
    xml = xml.replace("SEof", saxutils.escape(semestre_oferecimento))
    xml = xml.replace("cccc", transformar_em_paragrafos_justificados(conteudo_programatico))
    xml = xml.replace("mmmm", transformar_em_paragrafos_justificados(metodologia))
    xml = xml.replace("ffff", transformar_em_paragrafos_justificados(controle_avaliacao))

    with open(caminho_xml, "w", encoding="utf-8") as f:
        f.write(xml)

    novo_odt = f"{os.path.splitext(disciplina_selecionada)[0]}_{docente.replace(' ','_')}.odt"
    with zipfile.ZipFile(novo_odt, 'w', zipfile.ZIP_DEFLATED) as zip_out:
        for folder, _, files_ in os.walk(pasta):
            for file in files_:
                full = os.path.join(folder, file)
                zip_out.write(full, os.path.relpath(full, pasta))

    return novo_odt

# =========================
# Botão gerar ODT
# =========================
st.markdown("<span class='section-number'>3️⃣</span> Gerar ODT", unsafe_allow_html=True)
if st.button("Gerar ODT"):
    odt_gerado = gerar_odt()
    st.success("✅ ODT gerado com sucesso!")

    with open(odt_gerado, "rb") as f:
        st.download_button(
            label="📥 Baixar ODT",
            data=f,
            file_name=odt_gerado,
            mime="application/vnd.oasis.opendocument.text"
        )
