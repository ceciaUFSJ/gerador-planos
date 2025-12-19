# =========================
# app.py - Gerador de Planos de Ensino (ODT + Word)
# =========================

import streamlit as st
import zipfile
import shutil
import os
import xml.sax.saxutils as saxutils
from datetime import datetime
import requests
import pypandoc

# =========================
# 1) Textos padrões
# =========================

texto_metodologia_padrao = """• Aulas expositivas com apresentação de conteúdo, discussão de problemas e aplicações;
• Aprendizagem por meio de solução de problemas;
• Desenvolvimento de algoritmos de forma dinâmica durante as aulas;
• Revisões de exemplos e atividades práticas que possam estimular o desenvolvimento de uma análise crítica das diversas técnicas estudadas;
• Estudos-de-casos que realcem a importância da disciplina e sua aplicação em problemas reais;
• Exercícios extraclasse, provas e trabalhos práticos individuais e em grupos, para aprendizado aprofundado dos conceitos e técnicas estudadas.
"""

texto_conteudo_programatico = """1 Nivelamento
1.1 Revisão de Algoritmos e Estruturas de Dados I, utilizando as linguagens C/C++
1.2 Ponteiros: declaração, inicialização, alocação e desalocação
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
# 2) Configuração da página e CSS
# =========================
st.set_page_config(page_title="Gerador de Plano de Ensino")

# Fundo vermelho tijolo e textos claros
st.markdown(
    """
    <style>
    .main {
        background-color: #B22222;
        color: white;
    }
    h1, h2, h3, h4, h5, h6, .stText {
        color: white;
    }
    .css-1d391kg {  /* Streamlit inputs */
        background-color: #FFE4E1;
        color: black;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# =========================
# 3) Cabeçalho do CECIA
# =========================
st.markdown(
    "<h2 style='text-align:center'>CECIA - Coordenação do Curso de Engenharia da Computação com Inteligência Artificial</h2>",
    unsafe_allow_html=True
)

st.title("📝 Gerador de Plano de Ensino")

# =========================
# 4) Mensagem de aviso
# =========================
st.warning("⚠️ Os textos mostrados abaixo são **exemplos**. Substitua pelo conteúdo que desejar.")

# =========================
# 5) Seleção de disciplina (modelo ODT)
# =========================
st.subheader("1️⃣ Selecione a Disciplina")

api_url = "https://api.github.com/repos/ceciaUFSJ/planos-ensino/contents/modelos"
r = requests.get(api_url)
arquivos_json = r.json()

disciplinas = [f['name'] for f in arquivos_json if f['name'].lower().endswith('.odt')]

if not disciplinas:
    st.error("❌ Nenhum modelo de disciplina (ODT) encontrado no repositório.")
else:
    disciplina_selecionada = st.selectbox("Disciplina:", disciplinas)

# =========================
# 6) Cálculo automático de ANO e SEMESTRE
# =========================
hoje = datetime.now()
ano_atual = hoje.year
mes_atual = hoje.month

if mes_atual < 7:
    semestre_sugerido = "2º"
    ano_sugerido = ano_atual
else:
    semestre_sugerido = "1º"
    ano_sugerido = ano_atual + 1

# =========================
# 7) Campos do plano
# =========================
st.subheader("2️⃣ Preencha os campos do plano")

docente = st.text_input("Docente Responsável:", "João A. B. Cardoso")
coordenador = st.text_input("Coordenador do Curso:", "Mario C. D. Silva")
ano_oferecimento = st.text_input("Ano de Oferecimento:", str(ano_sugerido))
semestre_oferecimento  = st.text_input("Semestre de Oferecimento:", semestre_sugerido)

conteudo_programatico = st.text_area("Conteúdo Programático:", texto_conteudo_programatico, height=330)
metodologia = st.text_area("Metodologia de Ensino:", texto_metodologia_padrao, height=240)
controle_avaliacao = st.text_area("Controle de Frequência e Avaliação:", texto_controle_avaliacao, height=260)

# =========================
# 8) Funções auxiliares
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

    novo_odt = "documento_preenchido.odt"
    with zipfile.ZipFile(novo_odt, 'w', zipfile.ZIP_DEFLATED) as zip_out:
        for folder, _, files_ in os.walk(pasta):
            for file in files_:
                full = os.path.join(folder, file)
                zip_out.write(full, os.path.relpath(full, pasta))

    return novo_odt

# =========================
# 9) Botão de geração e download
# =========================
st.subheader("3️⃣ Gerar ODT ou Word")

if st.button("Gerar Arquivo"):
    odt_gerado = gerar_odt()
    st.success("✅ ODT gerado com sucesso!")
    with open(odt_gerado, "rb") as f:
        st.download_button(
            label="📥 Baixar ODT",
            data=f,
            file_name=odt_gerado,
            mime="application/vnd.oasis.opendocument.text"
        )
    # Gerar Word (DOCX)
    docx_gerado = "documento_preenchido.docx"
    pypandoc.convert_file(odt_gerado, 'docx', outputfile=docx_gerado)
    with open(docx_gerado, "rb") as f:
        st.download_button(
            label="📥 Baixar Word",
            data=f,
            file_name=docx_gerado,
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )

