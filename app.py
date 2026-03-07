import streamlit as st
import pandas as pd
from pathlib import Path
import sys
import warnings

warnings.filterwarnings('ignore')

# Adiciona raiz do projeto ao path
sys.path.insert(0, str(Path(__file__).parent))

from components.pii_detector import PIIDetector
from components.utils.masker import ENTITY_CONFIG

# ========================== CONFIGURAÇÃO DA PÁGINA ==========================

st.set_page_config(
    page_title="Detector de Dados Pessoais",
    page_icon="🔐",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS customizado
st.markdown("""
<style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 700;
        color: #1a1a2e;
        text-align: center;
        padding: 1rem 0;
    }
    .sub-header {
        font-size: 1.1rem;
        color: #555;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 12px;
        color: white;
        text-align: center;
    }
    .metric-card h2 { margin: 0; font-size: 2.5rem; }
    .metric-card p { margin: 0.3rem 0 0; font-size: 0.95rem; opacity: 0.9; }
    .privado-badge {
        background: #FF4444;
        color: white;
        padding: 4px 12px;
        border-radius: 20px;
        font-weight: bold;
        font-size: 0.85rem;
    }
    .publico-badge {
        background: #44BB44;
        color: white;
        padding: 4px 12px;
        border-radius: 20px;
        font-weight: bold;
        font-size: 0.85rem;
    }
    .highlight-box {
        background: #fafafa;
        border: 1px solid #e0e0e0;
        border-radius: 8px;
        padding: 1rem;
        margin: 0.5rem 0;
        line-height: 1.8;
        font-size: 0.95rem;
    }
    .legenda-item {
        display: inline-block;
        margin: 4px 8px 4px 0;
        padding: 3px 10px;
        border-radius: 4px;
        color: white;
        font-size: 0.8rem;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# ========================== INICIALIZAÇÃO ==========================

@st.cache_resource
def carregar_detector(threshold):
    return PIIDetector(threshold=threshold)

# ========================== SIDEBAR ==========================

with st.sidebar:
    st.markdown("## ⚙️ Configurações")
    threshold = st.slider(
        "Threshold de classificação",
        min_value=10, max_value=100, value=30, step=5,
        help="Score mínimo para classificar como PRIVADO. Menor = mais conservador."
    )
    
    st.markdown("---")
    st.markdown("## 🎨 Legenda de Cores")
    categorias = {
        'Documentos': ['cpf', 'rg', 'cnh', 'cnpj', 'titulo_eleitor', 'matricula'],
        'Dados Pessoais': ['nomes', 'data_nascimento', 'filiacao', 'assinatura'],
        'Financeiro': ['dados_bancarios', 'cartao_credito'],
        'Contato': ['email', 'telefone'],
        'Localização': ['placa_veiculo', 'endereco', 'inscricao_imobiliaria'],
        'Processos': ['processo_sei', 'protocolo_lai', 'ocorrencia', 'processo_generico'],
        'Saúde': ['saude'],
    }
    for grupo, tipos in categorias.items():
        st.markdown(f"**{grupo}**")
        for tipo in tipos:
            cfg = ENTITY_CONFIG.get(tipo, {})
            cor = cfg.get('color', '#999')
            label = cfg.get('label', tipo)
            st.markdown(
                f'<span class="legenda-item" style="background:{cor}">{label}</span>',
                unsafe_allow_html=True
            )
    
    st.markdown("---")
    st.markdown("### 📊 Sobre")
    st.markdown(
        "Sistema híbrido de detecção de PII usando **Regex + spaCy NER + Scoring**. "
        "Desenvolvido para o Hackathon CapacitaDF."
    )

# ========================== CONTEÚDO PRINCIPAL ==========================

st.markdown('<div class="main-header">🔐 Detector de Dados Pessoais</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="sub-header">Sistema automatizado de detecção e anonimização de informações pessoais identificáveis (PII)</div>',
    unsafe_allow_html=True
)

# Tabs
tab_texto, tab_arquivo = st.tabs(["📝 Análise de Texto", "📁 Análise de Arquivo"])

# ========================== TAB 1: TEXTO INDIVIDUAL ==========================

with tab_texto:
    st.markdown("### Cole um texto para análise")
    
    texto_input = st.text_area(
        "Texto para análise",
        height=200,
        placeholder="Ex: O requerente João da Silva, CPF 123.456.789-01, residente na Rua das Flores, 123, solicita acesso aos documentos do processo SEI 00015-01009853/2026-01...",
        label_visibility="collapsed"
    )
    
    col_btn, col_exemplo = st.columns([1, 3])
    with col_btn:
        analisar = st.button("🔍 Analisar", type="primary", use_container_width=True)
    with col_exemplo:
        usar_exemplo = st.button("📋 Usar texto de exemplo")
    
    if usar_exemplo:
        texto_input = (
            "O requerente João da Silva, CPF 123.456.789-01, nascido em 15/03/1990, "
            "residente na Rua das Flores, 123, Brasília-DF, CEP 70000-000, "
            "telefone (61) 99999-8888, email joao.silva@email.com, "
            "solicita acesso aos documentos do processo SEI 00015-01009853/2026-01. "
            "Protocolo LAI-258789/2025. Mãe: Maria Aparecida da Silva. "
            "O requerente é diabético e possui prontuário no Hospital Regional."
        )
        st.rerun()
    
    if analisar and texto_input:
        detector = carregar_detector(threshold)
        resultado = detector.detectar_pii(texto_input)
        
        # Métricas
        col1, col2, col3 = st.columns(3)
        
        with col1:
            badge = "privado-badge" if resultado['classificacao'] == 'PRIVADO' else "publico-badge"
            st.markdown(
                f'<div class="metric-card"><h2><span class="{badge}">{resultado["classificacao"]}</span></h2>'
                f'<p>Classificação</p></div>',
                unsafe_allow_html=True
            )
        
        with col2:
            total_entidades = sum(len(v) for v in resultado['entidades'].values() if v)
            st.markdown(
                f'<div class="metric-card"><h2>{total_entidades}</h2>'
                f'<p>Entidades Detectadas</p></div>',
                unsafe_allow_html=True
            )
        
        with col3:
            st.markdown(
                f'<div class="metric-card"><h2>{resultado["score"]}</h2>'
                f'<p>Score de Sensibilidade</p></div>',
                unsafe_allow_html=True
            )
        
        st.markdown("---")
        
        # Texto com highlight
        col_orig, col_mask = st.columns(2)
        
        with col_orig:
            st.markdown("#### 🔍 Texto Original — Entidades Destacadas")
            st.markdown(
                f'<div class="highlight-box">{resultado["texto_highlight"]}</div>',
                unsafe_allow_html=True
            )
        
        with col_mask:
            st.markdown("#### 🛡️ Texto Anonimizado")
            st.markdown(
                f'<div class="highlight-box">{resultado["texto_mascarado"]}</div>',
                unsafe_allow_html=True
            )
        
        # Detalhes das entidades
        st.markdown("---")
        st.markdown("#### 📋 Entidades Encontradas")
        
        entidades_com_valor = {k: v for k, v in resultado['entidades'].items() if v}
        if entidades_com_valor:
            cols = st.columns(min(len(entidades_com_valor), 4))
            for i, (tipo, valores) in enumerate(entidades_com_valor.items()):
                cfg = ENTITY_CONFIG.get(tipo, {'label': tipo, 'color': '#999'})
                with cols[i % len(cols)]:
                    st.markdown(
                        f'<span class="legenda-item" style="background:{cfg["color"]}">{cfg["label"]}</span>',
                        unsafe_allow_html=True
                    )
                    for v in valores:
                        st.code(v, language=None)
        else:
            st.info("Nenhuma entidade sensível detectada.")

# ========================== TAB 2: ARQUIVO ==========================

with tab_arquivo:
    st.markdown("### Faça upload de um arquivo Excel ou CSV")
    
    arquivo = st.file_uploader(
        "Arraste ou selecione o arquivo",
        type=['xlsx', 'xls', 'csv'],
        label_visibility="collapsed"
    )
    
    if arquivo:
        # Lê arquivo
        if arquivo.name.endswith('.csv'):
            df = pd.read_csv(arquivo)
        else:
            df = pd.read_excel(arquivo, engine='openpyxl')
        
        st.success(f"✅ {len(df)} registros carregados")
        
        # Identifica coluna de texto
        coluna_texto = None
        for col in df.columns:
            if 'texto' in col.lower() or 'conteúdo' in col.lower() or 'conteudo' in col.lower():
                coluna_texto = col
                break
        if coluna_texto is None:
            coluna_texto = df.columns[1] if len(df.columns) > 1 else df.columns[0]
        
        coluna_texto = st.selectbox("Coluna de texto:", df.columns.tolist(), index=df.columns.tolist().index(coluna_texto))
        
        if st.button("🚀 Processar Arquivo", type="primary", use_container_width=True):
            detector = carregar_detector(threshold)
            
            progress = st.progress(0, text="Processando...")
            resultados = []
            
            for idx, row in df.iterrows():
                texto = str(row[coluna_texto]) if pd.notna(row[coluna_texto]) else ""
                resultado = detector.detectar_pii(texto)
                entidades_str = ', '.join(resultado['resumo']) if resultado['resumo'] else 'Nenhuma'
                
                resultados.append({
                    'ID': row[df.columns[0]],
                    'Texto Original': texto,
                    'Texto Anonimizado': resultado.get('texto_mascarado', texto),
                    'Entidades': entidades_str,
                    'Classificação': resultado['classificacao'],
                    'Score': resultado['score'],
                    '_highlight': resultado.get('texto_highlight', texto),
                    '_entidades_raw': resultado['entidades']
                })
                
                progress.progress((idx + 1) / len(df), text=f"Processando {idx + 1}/{len(df)}...")
            
            progress.empty()
            df_resultado = pd.DataFrame(resultados)
            st.session_state['df_resultado'] = df_resultado
            st.success("✅ Processamento concluído!")
        
        # Exibe resultados se existirem
        if 'df_resultado' in st.session_state:
            df_resultado = st.session_state['df_resultado']
            
            # Métricas gerais
            st.markdown("---")
            st.markdown("### 📊 Resultado da Classificação")
            
            total = len(df_resultado)
            privados = (df_resultado['Classificação'] == 'PRIVADO').sum()
            publicos = (df_resultado['Classificação'] == 'PUBLICO').sum()
            score_medio = df_resultado['Score'].mean()
            
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Total de Registros", total)
            col2.metric("🔴 PRIVADO", f"{privados} ({privados/total*100:.1f}%)")
            col3.metric("🟢 PÚBLICO", f"{publicos} ({publicos/total*100:.1f}%)")
            col4.metric("Score Médio", f"{score_medio:.1f}")
            
            # Gráfico de pizza
            st.markdown("---")
            col_chart, col_bar = st.columns(2)
            
            with col_chart:
                import plotly.express as px
                fig = px.pie(
                    values=[privados, publicos],
                    names=['PRIVADO', 'PÚBLICO'],
                    color_discrete_sequence=['#FF4444', '#44BB44'],
                    title='Distribuição de Classificação'
                )
                fig.update_layout(height=350)
                st.plotly_chart(fig, use_container_width=True)
            
            with col_bar:
                # Contagem por tipo de entidade
                contagem_entidades = {}
                for _, row in df_resultado.iterrows():
                    raw = row['_entidades_raw']
                    for tipo, valores in raw.items():
                        if valores:
                            contagem_entidades[tipo] = contagem_entidades.get(tipo, 0) + len(valores)
                
                if contagem_entidades:
                    df_ent = pd.DataFrame(
                        list(contagem_entidades.items()),
                        columns=['Tipo', 'Quantidade']
                    ).sort_values('Quantidade', ascending=True)
                    
                    cores = [ENTITY_CONFIG.get(t, {}).get('color', '#999') for t in df_ent['Tipo']]
                    fig2 = px.bar(
                        df_ent, x='Quantidade', y='Tipo', orientation='h',
                        title='Entidades Mais Detectadas',
                        color='Tipo',
                        color_discrete_map={t: ENTITY_CONFIG.get(t, {}).get('color', '#999') for t in df_ent['Tipo']}
                    )
                    fig2.update_layout(height=350, showlegend=False)
                    st.plotly_chart(fig2, use_container_width=True)
            
            # Tabela de resultados
            st.markdown("---")
            st.markdown("### 📋 Resultados Detalhados")
            
            filtro = st.selectbox("Filtrar por:", ["Todos", "PRIVADO", "PUBLICO"])
            df_display = df_resultado.copy()
            if filtro != "Todos":
                df_display = df_display[df_display['Classificação'] == filtro]
            
            for _, row in df_display.iterrows():
                badge = "🔴 PRIVADO" if row['Classificação'] == 'PRIVADO' else "🟢 PÚBLICO"
                with st.expander(f"ID {row['ID']} — {badge} — Score: {row['Score']} — {row['Entidades']}"):
                    c1, c2 = st.columns(2)
                    with c1:
                        st.markdown("**🔍 Original — Entidades Destacadas**")
                        st.markdown(
                            f'<div class="highlight-box">{row["_highlight"]}</div>',
                            unsafe_allow_html=True
                        )
                    with c2:
                        st.markdown("**🛡️ Texto Anonimizado**")
                        st.markdown(
                            f'<div class="highlight-box">{row["Texto Anonimizado"]}</div>',
                            unsafe_allow_html=True
                        )
            
            # Download
            st.markdown("---")
            df_download = df_resultado[['ID', 'Texto Original', 'Texto Anonimizado', 'Entidades', 'Classificação', 'Score']]
            
            csv_data = df_download.to_csv(index=False).encode('utf-8')
            st.download_button(
                "⬇️ Baixar resultado (CSV)",
                csv_data,
                file_name="resultado_pii.csv",
                mime="text/csv",
                use_container_width=True
            )
