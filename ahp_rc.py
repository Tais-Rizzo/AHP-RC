import streamlit as st
import pandas as pd
import numpy as np
from PIL import Image
import re

# Configuração da página
st.set_page_config(
    page_title="Mundo da Geomática - AHP",
        # layout="wide",
)

# Esconder o menu e definir cor do texto
hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            body, p, div, h1, h2, h3, h4, h5, li, a {
                color: black; /* Define a cor do texto para preto */
            }
            .centered-container {
                width: 100%; /* Ajuste o valor conforme necessário */
                margin: 0px;
                padding: 0px;
            }
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)

# Adicionar container centralizado
st.markdown('<div class="centered-container">', unsafe_allow_html=True)

st.markdown(
    """
    <div style="background-color: #000080; padding: 6px; margin: 3px;">
        <p style="font-size: 18px; color: #ffffff; font-family: 'Roboto'; text-align: center; margin: 0;">
           <b> MG - AHP
        </p>
    </div>
    </p>
    """,
    unsafe_allow_html=True
)

# Dados da tabela
data = {
    "VALORES": ["1/9", "1/7", "1/5", "1/3", "1", "3", "5", "7", "9"],
    "IMPORTÂNCIA MÚTUA": [
        "Extremamente menos importante que",
        "Muito fortemente menos importante que",
        "Fortemente menos importante que",
        "Moderadamente menos importante que",
        "Igualmente importante a",
        "Moderadamente mais importante que",
        "Fortemente mais importante que",
        "Muito fortemente mais importante que",
        "Extremamente mais importante que"
    ]
}

# Criar DataFrame
df = pd.DataFrame(data)

# Exibir a tabela em um expander
with st.expander("Escala de comparadores"):
    
    st.table(df)
    st.write("Fonte: Saaty (1977), apud Rosot (2000).")

# Dados da tabela
data2 = {
    "n": list(range(1, 16)),
    "IR": [0.00, 0.00, 0.58, 0.90, 1.12, 1.24, 1.32, 1.41, 1.45, 1.49, 1.51, 1.48, 1.56, 1.57, 1.59]
}

# Criar DataFrame
df2 = pd.DataFrame(data2)
df2['IR'] = df2['IR'].round(2)

# Exibir a tabela em um expander
with st.expander("Tabela de valores de IR"):
    st.write("Valores de IR para matrizes quadradas de ordem n.")
    st.table(df2)
    st.write("Fonte: Saaty (1991).")

# Inicializando a lista de variáveis e a matriz
if 'variables' not in st.session_state:
    st.session_state.variables = []
if 'matrix' not in st.session_state:
    st.session_state.matrix = pd.DataFrame()

# Função para adicionar uma nova variável
def add_variable(new_variable):
    if not new_variable:
        st.warning("O nome da variável não pode estar vazio.")
    elif not re.match("^[A-Za-z0-9_ ]*$", new_variable):
        st.warning("O nome da variável não pode conter caracteres especiais.")
    elif new_variable in st.session_state.variables:
        st.warning(f"A variável '{new_variable}' já foi inserida.")
    elif len(st.session_state.variables) >= 15:
        st.warning("Não é possível adicionar mais variáveis. O limite é 15.")
    else:
        st.session_state.variables.append(new_variable)
        size = len(st.session_state.variables)
        if size > 1:
            new_matrix = pd.DataFrame(np.ones((size, size)), index=st.session_state.variables, columns=st.session_state.variables)
            new_matrix.iloc[:-1, :-1] = st.session_state.matrix
            st.session_state.matrix = new_matrix
        else:
            st.session_state.matrix = pd.DataFrame(np.ones((1, 1)), index=st.session_state.variables, columns=st.session_state.variables)

# Função para calcular a Razão de Consistência (RC)
def calculate_consistency_ratio(matrix):
    n = len(matrix)
    if n < 2:
        return None, None  # Não é possível calcular RC para matrizes menores que 2x2

    # Valores de Saaty para ICA
    saaty_ica = {1: 0, 2: 0, 3: 0.58, 4: 0.9, 5: 1.12, 6: 1.24, 7: 1.32, 8: 1.41, 9: 1.45, 10: 1.49}

    # Calculando o vetor de prioridades (autovetor)
    eigvals, eigvecs = np.linalg.eig(matrix)
    max_eigval = np.max(eigvals).real
    eigvec = eigvecs[:, np.argmax(eigvals)].real
    priorities = eigvec / np.sum(eigvec)

    # Calculando o Índice de Consistência (IC)
    ic = (max_eigval - n) / (n - 1)

    # Recuperando o Índice de Consistência Aleatória (ICA)
    ica = saaty_ica.get(n, 1.49)  # Valor padrão se n > 10

    # Calculando a Razão de Consistência (RC)
    rc = ic / ica
    return rc, priorities

# Função para calcular os pesos estatísticos
def calculate_weights(matrix):
    normalized_matrix = matrix / matrix.sum(axis=0)
    weights = normalized_matrix.mean(axis=1)
    return weights

# Função para ajustar a matriz mantendo a diagonal principal em 1 e calculando os valores acima da diagonal
def adjust_matrix(matrix):
    for i in range(len(matrix)):
        for j in range(i + 1, len(matrix)):
            matrix.iloc[i, j] = 1 / matrix.iloc[j, i]
    return matrix

# Formulário para adicionar nova variável
with st.form(key='add_variable_form'):
    cols = st.columns([4, 1, 1])
    new_variable = cols[0].text_input("Digite o nome da nova variável:", placeholder="Ex: Declividade")
    cols[1].text("")
    cols[1].text("")
    submit_button = cols[1].form_submit_button(label='Adicionar')

    cols[2].text("")
    cols[2].text("")
    remove_button = cols[2].form_submit_button(label='Remover')
    if submit_button and new_variable:
        add_variable(new_variable)
    if remove_button and st.session_state.variables:
        st.session_state.variables.pop()
        if len(st.session_state.variables) > 0:
            size = len(st.session_state.variables)
            st.session_state.matrix = st.session_state.matrix.iloc[:size, :size]
        else:
            st.session_state.matrix = pd.DataFrame()

# Apresentando o DataFrame editável
if len(st.session_state.variables) > 0:
    # Editando DataFrame

    edited_df = st.data_editor(st.session_state.matrix)  # 👈 DataFrame editável

    # Botão para confirmar edições e fazer cálculos
    if st.button("Confirmar edições e calcular"):
        # Criando uma nova matriz ajustada a partir da matriz editada
        new_matrix = pd.DataFrame(edited_df.values, index=st.session_state.variables, columns=st.session_state.variables)
        adjusted_matrix = adjust_matrix(new_matrix)

        # Calculando e exibindo a Razão de Consistência e os pesos estatísticos
        rc, priorities = calculate_consistency_ratio(adjusted_matrix.values)
        weights = calculate_weights(adjusted_matrix.values)
        if rc is not None:
            
            st.write("Pesos Estatísticos (Prioridades):")
            results_df = pd.DataFrame({
                "Fatores": st.session_state.variables,
                "Peso Estatístico": weights
            })

            cols2 = st.columns(2)

            
            with cols2[0]:
                st.data_editor(adjusted_matrix)

                st.write(f"Razão de Consistência: {rc:.4f}")

                if rc < 0.10:
                    st.write(f"<p style='color: blue;'>{rc:.4f} < 0.10 (consistência aceitável)</p>", unsafe_allow_html=True)
                else:
                    st.write(f"<p style='color: red;'>{rc:.4f} ≥ 0.10 (consistência não aceitável)</p>", unsafe_allow_html=True)
            with cols2[1]:
                st.write(results_df) 

        else:
            st.write("Não é possível calcular a Razão de Consistência para matrizes menores que 2x2.")


def local_css(file_name):
    with open(file_name) as f:
        st.markdown('<style>{}</style>'.format(f.read()), unsafe_allow_html=True)

local_css("style.css")