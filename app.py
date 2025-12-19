import streamlit as st
import zipfile
import shutil
import os
import xml.sax.saxutils as saxutils
from datetime import datetime
import requests

# =========================
# Textos padrão
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
...
"""

texto_controle_avaliacao = """• Cem pontos distribuídos ao longo do semestre:
a) 2 Provas – 30 pontos cada;
b) Listas de exercícios e práticas – 10 pontos;
c) Trabalho Prático – 30 pontos.
...
"""

# =========================
# Página e CSS
# =========================
st.set_page_config(page_title="CECIA - Gerador de Planos de Ensino", layout="wide")

st.markdown(
    """
    <style>
    /* Fundo e cores */
    body, .css-18e3th9 {background-color: #8B0000; color: #FFF8F0;}
    .stApp {background-color: #8B0000;}
    
    /* Cabeçalho */
    h1, h2, h3, h4, h5, h6 {color: #FFDAB9;}
    
    /* Textareas */
    .stTextArea>div>div>textarea {background-color: #FFF5F0; color: #000; border-radius:8px;}
    
    /* Botões */
    .stButton>button {
        background-color: #FF6347;
        color: white;
        border-radius:8px;
        padding: 0.5em 1em;
        font-weight:bold;
        transition: transform 0.2s;
    }
    .stButton>button:hover {
        transform: scale(1.05);
        background-color: #FF4500;
    }
    
    /* Avisos */
    .stWarning {background-color:#FFA07A; color:black;}
    
    /* Containers */
    .stContainer {padding: 1rem; border-radius:10px;}
    </style>
    """, unsafe_allow_html=True
)

# =========================
# Cabeçalho
# =========================
st.markdown(
    "<h2 style='text-align:center'>CECIA - Coordenação do Curso de Engenharia da Computação com Inteligência Artificial</h2>",
    unsafe_allow_html=True
)

st.title("📝 Gerador de Plano de Ensino")

st.warning("⚠️ Os textos abaixo são apenas exemplos. Substitua pelos conteúdos desejados.")

# =========================
# Seleção de disciplina
# =========================
st.subheader("1️⃣ Selecione a Disciplina")

api_url = "https://api.github.com/repos/ceciaUFSJ/planos-ensino/contents/modelos"
r = requests.get(api_url)
arquivos_json = r.json()

disciplinas = [f['name'] for f in arquivos_json if f['name'].lower().endswith('.odt')]

if not disciplinas:
    st.error("❌ Nenhum modelo de disciplina (ODT) encontrado.")
else:
    disciplina_selecionada = st.selectbox("Disciplina:", disciplinas)

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
with st.container():
    st.subheader("2️⃣ Preencha os campos do plano")

    docente = st.text_input("Docente Responsável:", "João A. B. Cardoso")
    coordenador = st.text_input("Coordenador do Curso:", "Mario C. D. Silva")
    ano_oferecimento = st.text_input("Ano de Oferecimento:", str(ano_sugerido))
    semestre_oferecimento = st.text_input("Semestre de Oferecimento:", semestre_sugerido)

    conteudo_programatico = st.text_area("Conteúdo Programático:", texto_conteudo_programatico, height=330)
    metodologia = st.text_area("Metodologia de Ensino:", texto_metodologia_padrao, height=240)
    controle_avaliacao = st.text_area("Controle de Frequência e Avaliação:", texto_controle_avaliacao, height=260)

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

    novo_odt = "documento_preenchido.odt"
    with zipfile.ZipFile(novo_odt, 'w', zipfile.ZIP_DEFLATED) as zip_out:
        for folder, _, files_ in os.walk(pasta):
            for file in files_:
                full = os.path.join(folder, file)
                zip_out.write(full, os.path.relpath(full, pasta))

    return novo_odt

# =========================
# Botão gerar ODT
# =========================
st.subheader("3️⃣ Gerar ODT")

if st.button("Gerar ODT"):
    odt_gerado = gerar_odt()
    st.success("✅ ODT gerado com sucesso!")

    # Novo nome: disciplina + docente
    nome_saida = f"{os.path.splitext(disciplina_selecionada)[0]}_{docente.replace(' ', '_')}.odt"

    with open(odt_gerado, "rb") as f:
        st.download_button(
            label="📥 Baixar ODT",
            data=f,
            file_name=nome_saida,
            mime="application/vnd.oasis.opendocument.text"
        )
