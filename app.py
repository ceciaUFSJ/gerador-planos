import streamlit as st
import requests
import os
import zipfile
import shutil
import xml.sax.saxutils as saxutils
import subprocess
from datetime import datetime

st.title("Gerador de Plano de Ensino")

# =========================
# Textos padrões
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
# Buscar modelos ODT do GitHub
# =========================
api_url = "https://api.github.com/repos/ceciaUFSJ/planos-ensino/contents/modelos"
r = requests.get(api_url)
arquivos_json = r.json()
arquivos_odt = [f['name'] for f in arquivos_json if f['name'].lower().endswith('.odt')]

if not arquivos_odt:
    st.error("❌ Nenhum arquivo ODT encontrado no repositório.")
    st.stop()

# =========================
# Cálculo automático de ano e semestre
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
# Campos de entrada
# =========================
docente = st.text_input("DOCENTE RESPONSÁVEL:", "João A. B. Cardoso")
coordenador = st.text_input("COORDENADOR DO CURSO:", "Mario C. D. Silva")
ano_oferta = st.text_input("ANO DE OFERECIMENTO:", str(ano_sugerido))
semestre_oferta = st.text_input("SEMESTRE DE OFERECIMENTO:", semestre_sugerido)

conteudo_programatico = st.text_area("CONTEÚDO PROGRAMÁTICO:", texto_conteudo_programatico, height=330)
metodologia = st.text_area("METODOLOGIA DE ENSINO:", texto_metodologia_padrao, height=240)
controle_avaliacao = st.text_area("CONTROLE DE FREQUÊNCIA E AVALIAÇÃO:", texto_controle_avaliacao, height=260)

odt_modelo = st.selectbox("Escolha o modelo ODT:", arquivos_odt)

# =========================
# Funções auxiliares
# =========================
def transformar_em_paragrafos_justificados(texto):
    texto = saxutils.escape(texto)
    return "</text:p><text:p text:style-name=\"Justificado\" fo:font-size=\"10pt\">".join(texto.split("\n"))

def gerar_odt_preenchido():
    git_url_raw = f"https://raw.githubusercontent.com/ceciaUFSJ/planos-ensino/main/modelos/{odt_modelo}"
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
            <style:paragraph-properties fo:text-align="justify" fo:font-size="10pt"/>
        </style:style>
        """
        xml = xml.replace("</office:automatic-styles>", estilo + "\n</office:automatic-styles>")

    xml = xml.replace("drrrr", saxutils.escape(docente))
    xml = xml.replace("dcccc", saxutils.escape(coordenador))
    xml = xml.replace("ANOof", saxutils.escape(ano_oferta))
    xml = xml.replace("SEof", saxutils.escape(semestre_oferta))
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
# Botão de gerar ODT/PDF
# =========================
if st.button("Gerar ODT/PDF"):
    odt_gerado = gerar_odt_preenchido()

    pdf_gerado = False
    try:
        subprocess.run(["libreoffice", "--headless", "--convert-to", "pdf", odt_gerado], check=True)
        pdf_gerado = True
    except:
        st.warning("⚠ PDF não pôde ser gerado. Baixe o ODT e converta localmente se necessário.")

    st.success("✅ Arquivo ODT gerado com sucesso!")
    st.download_button("Baixar ODT", open(odt_gerado, "rb").read(), file_name=odt_gerado)

    if pdf_gerado and os.path.exists("documento_preenchido.pdf"):
        st.download_button("Baixar PDF", open("documento_preenchido.pdf", "rb").read(), file_name="documento_preenchido.pdf")
