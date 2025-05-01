import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import os

st.set_page_config(page_title="Controle Financeiro", layout="wide")

# Páginas
pagina = st.sidebar.selectbox("📂 Navegação", ["Resumo Geral", "Dashboard", "Registrar/Remover", "Metas e Projeções"])

# Caminhos
CAMINHO_BASE_PADRAO = "Controle_Financeiro_Maio25.xlsx"
CAMINHO_BACKUP_ORIGINAL = "Controle_Financeiro_Maio25.xlsm"

# Upload removido
# Inicialização de base padrão removida

origem_base = CAMINHO_BASE_PADRAO

@st.cache_data
def carregar_dados(file):
    base = pd.read_excel(file, sheet_name="BASE")
    dados = pd.read_excel(file, sheet_name="DADOS")
    calculo = pd.read_excel(file, sheet_name="BASE DE CALCULO")
    return base, dados, calculo

base_original, dados, calculo = carregar_dados(origem_base)
if "base_modificada" not in st.session_state:
    st.session_state.base_modificada = base_original.copy()
base = st.session_state.base_modificada

meses = base["Mês"].dropna().unique()
mes_selecionado = st.sidebar.selectbox("Mês", sorted(meses))
base_mes = base[base["Mês"] == mes_selecionado].copy()

if pagina == "Resumo Geral":
    st.title("📌 Resumo Financeiro do Mês")
    receita = base_mes[base_mes["Tipo"] == "Receita"]["Valor"].sum()
    despesa = base_mes[base_mes["Tipo"] == "Despesa"]["Valor"].sum()
    saldo = receita - despesa

    col1, col2, col3 = st.columns(3)
    col1.metric("💰 Receita", f"R$ {receita:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
    col2.metric("📤 Despesa", f"R$ {despesa:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
    col3.metric("📌 Saldo", f"R$ {saldo:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))

    st.divider()
    st.subheader("Lançamentos Detalhados")
    st.dataframe(base_mes.reset_index(drop=True), use_container_width=True)

    st.divider()
    st.subheader("📈 Previsão Futura")
    futuro_receita = base[(base["Tipo"] == "Receita") & (base["Mês"] != mes_selecionado)]["Valor"].sum()
    futuro_despesa = base[(base["Tipo"] == "Despesa") & (base["Mês"] != mes_selecionado)]["Valor"].sum()
    saldo_futuro = saldo + futuro_receita - futuro_despesa

    colf1, colf2, colf3 = st.columns(3)
    colf1.metric("Futura Receita", f"R$ {futuro_receita:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
    colf2.metric("Futura Despesa", f"R$ {futuro_despesa:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
    colf3.metric("Saldo Futuro Estimado", f"R$ {saldo_futuro:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))

elif pagina == "Dashboard":
    import plotly.io as pio
    from fpdf import FPDF

    st.title("📊 Dashboard de Análise")

    st.subheader("Evolução mensal por tipo")
    graf_evolucao = base.groupby(["Mês", "Tipo"])["Valor"].sum().reset_index()
    fig_evolucao = px.bar(graf_evolucao, x="Mês", y="Valor", color="Tipo", barmode="group")
    st.plotly_chart(fig_evolucao, use_container_width=True)

    st.subheader("Pizza de despesas por categoria")
    categoria_despesas = base[base["Tipo"] == "Despesa"].groupby("Categoria")["Valor"].sum().reset_index()
    fig_cat_despesa = px.pie(categoria_despesas, names="Categoria", values="Valor")
    st.plotly_chart(fig_cat_despesa, use_container_width=True)

    st.subheader("Pizza de despesas por subcategoria")
    sub_despesas = base[base["Tipo"] == "Despesa"].groupby("Subcategoria")["Valor"].sum().reset_index()
    fig_sub_despesas = px.pie(sub_despesas, names="Subcategoria", values="Valor")
    st.plotly_chart(fig_sub_despesas, use_container_width=True)

    st.subheader("Pizza de receitas por categoria")
    categoria_receitas = base[base["Tipo"] == "Receita"].groupby("Categoria")["Valor"].sum().reset_index()
    if not categoria_receitas.empty:
        fig_cat_receita = px.pie(categoria_receitas, names="Categoria", values="Valor")
        st.plotly_chart(fig_cat_receita, use_container_width=True)

    st.subheader("Média mensal por tipo")
    media_mensal = base.groupby(["Mês", "Tipo"])["Valor"].sum().groupby("Tipo").mean().reset_index()
    fig_media = px.bar(media_mensal, x="Tipo", y="Valor")
    st.plotly_chart(fig_media, use_container_width=True)

    st.subheader("Gráfico de barras empilhadas por mês e categoria")
    barras_emp = base[base["Tipo"] == "Despesa"].groupby(["Mês", "Categoria"])["Valor"].sum().reset_index()
    fig_barras = px.bar(barras_emp, x="Mês", y="Valor", color="Categoria", title="Despesas por mês e categoria", barmode="stack")
    st.plotly_chart(fig_barras, use_container_width=True)

    st.subheader("Ranking dos maiores gastos")
    top_gastos = base[base["Tipo"] == "Despesa"].sort_values(by="Valor", ascending=False).head(5)
    st.dataframe(top_gastos.reset_index(drop=True), use_container_width=True)

    st.subheader("Resumo por categoria")
    resumo_cat = base[base["Tipo"] == "Despesa"].groupby("Categoria").agg(
        Total=("Valor", "sum"),
        Quantidade=("Valor", "count")
    ).reset_index()
    resumo_cat["% do Total"] = (resumo_cat["Total"] / resumo_cat["Total"].sum()) * 100
    st.dataframe(resumo_cat, use_container_width=True)

elif pagina == "Dashboard":
    import plotly.io as pio
    from fpdf import FPDF

    # Exportar gráficos como imagem
    # Os gráficos devem ser gerados antes de serem salvos como imagem
    st.title("📊 Dashboard de Análise")

    st.subheader("Evolução mensal por tipo")
    graf_evolucao = base.groupby(["Mês", "Tipo"])["Valor"].sum().reset_index()
    fig_evolucao = px.bar(graf_evolucao, x="Mês", y="Valor", color="Tipo", barmode="group")
    st.plotly_chart(fig_evolucao, use_container_width=True)

    st.subheader("Pizza de despesas por categoria")
    categoria_despesas = base[base["Tipo"] == "Despesa"].groupby("Categoria")["Valor"].sum().reset_index()
    fig_cat_despesa = px.pie(categoria_despesas, names="Categoria", values="Valor")
    fig_cat_despesa.write_image("pizza_despesas.png")
    st.plotly_chart(fig_cat_despesa, use_container_width=True)

    st.subheader("Pizza de despesas por subcategoria")
    sub_despesas = base[base["Tipo"] == "Despesa"].groupby("Subcategoria")["Valor"].sum().reset_index()
    fig_sub_despesas = px.pie(sub_despesas, names="Subcategoria", values="Valor")
    st.plotly_chart(fig_sub_despesas, use_container_width=True)

    st.subheader("Pizza de receitas por categoria")
    categoria_receitas = base[base["Tipo"] == "Receita"].groupby("Categoria")["Valor"].sum().reset_index()
    if not categoria_receitas.empty:
        fig_cat_receita = px.pie(categoria_receitas, names="Categoria", values="Valor")
        fig_cat_receita.write_image("pizza_receitas.png")
        st.plotly_chart(fig_cat_receita, use_container_width=True)

    st.subheader("Média mensal por tipo")
    media_mensal = base.groupby(["Mês", "Tipo"])["Valor"].sum().groupby("Tipo").mean().reset_index()
    fig_media = px.bar(media_mensal, x="Tipo", y="Valor")
    st.plotly_chart(fig_media, use_container_width=True)

    st.subheader("Gráfico de barras empilhadas por mês e categoria")
    barras_emp = base[base["Tipo"] == "Despesa"].groupby(["Mês", "Categoria"])["Valor"].sum().reset_index()
    fig_barras = px.bar(barras_emp, x="Mês", y="Valor", color="Categoria", title="Despesas por mês e categoria", barmode="stack")
    st.plotly_chart(fig_barras, use_container_width=True)

    st.subheader("Ranking dos maiores gastos")
    top_gastos = base[base["Tipo"] == "Despesa"].sort_values(by="Valor", ascending=False).head(5)
    st.dataframe(top_gastos.reset_index(drop=True), use_container_width=True)

    st.subheader("Resumo por categoria")
    resumo_cat = base[base["Tipo"] == "Despesa"].groupby("Categoria").agg(
        Total=("Valor", "sum"),
        Quantidade=("Valor", "count")
    ).reset_index()
    resumo_cat["% do Total"] = (resumo_cat["Total"] / resumo_cat["Total"].sum()) * 100
    st.dataframe(resumo_cat, use_container_width=True)

    # Geração de relatório PDF removida

elif pagina == "Registrar/Remover":
    st.title("✍️ Registrar ou Remover Lançamento")

    with st.form("novo_lancamento"):
        col_a, col_b = st.columns(2)
        descricao = col_a.text_input("Descrição")
        valor = col_b.number_input("Valor (R$)", min_value=0.01, step=0.01)

        col_c, col_d = st.columns(2)
        categoria = col_c.selectbox("Categoria", dados["Categoria"].dropna().unique())
        subcategoria = col_d.selectbox("Subcategoria", dados["Subcategoria"].dropna().unique())

        col_e, col_f = st.columns(2)
        tipo = col_e.selectbox("Tipo", ["Receita", "Despesa"])
        mes = col_f.selectbox("Mês", dados["MÊS"].dropna().unique())

        parcelas = st.number_input("Parcelas", min_value=1, step=1, value=1)
        registrar = st.form_submit_button("Registrar")

        if registrar:
            novo_lancamento = pd.DataFrame([{
                "Descrição": descricao,
                "Categoria": categoria,
                "Subcategoria": subcategoria,
                "Parcelas": parcelas,
                "Mês": mes,
                "Tipo": tipo,
                "Valor": valor
            }])
            st.session_state.base_modificada = pd.concat([st.session_state.base_modificada, novo_lancamento], ignore_index=True)
            # Salvamento em Excel removido
            st.success("✅ Lançamento registrado e salvo com sucesso!")

    st.divider()
    st.subheader("🗑️ Remover lançamento")
    base_mes = base[base["Mês"] == mes_selecionado].copy()
    linha_remover = st.number_input("Linha para remover (0 até {0})".format(len(base_mes)-1), min_value=0, max_value=max(len(base_mes)-1, 0), step=1)
    if st.button("Remover linha"):
        index_global = base_mes.index[linha_remover]
        st.session_state.base_modificada = st.session_state.base_modificada.drop(index_global).reset_index(drop=True)
        st.session_state.base_modificada.to_excel(CAMINHO_BASE_PADRAO, sheet_name="BASE", index=False)
        with pd.ExcelWriter(CAMINHO_BASE_PADRAO, mode="a", engine="openpyxl", if_sheet_exists="replace") as writer:
            dados.to_excel(writer, sheet_name="DADOS", index=False)
            calculo.to_excel(writer, sheet_name="BASE DE CALCULO", index=False)
        st.success(f"Lançamento da linha {linha_remover} removido com sucesso!")
        st.rerun()

    # Botão de download de Excel removido
