# Sistema de Detecção em dados Privados.

Sistema automatizado para identificação e classificação de dados sensíveis em textos em português brasileiro, desenvolvido para análise de pedidos de acesso à informação e documentos governamentais.

---
##  Índice

- [Sobre o Projeto](#sobre-o-projeto)
- [Funcionalidades](#funcionalidades)
- [Instalação](#instalação)
- [Como Usar](#como-usar)
- [Estrutura de Saída](#estrutura-de-saída)
- [Configuração](#configuração)
- [Exemplos](#exemplos)
- [Resolução de Problemas](#resolução-de-problemas)
- [Estrutura do Projeto](#estrutura-do-projeto)

----------------------------------------------------------------------------------------------------

##  Sobre o Projeto

Este sistema foi desenvolvido para automatizar a detecção de informações pessoais sensíveis em textos, permitindo que órgãos públicos e empresas classifiquem automaticamente documentos quanto ao nível de privacidade.

### O que o sistema detecta?

O detector identifica Dados privados, incluindo:

- **Documentos**: CPF, RG, CNH, Título de Eleitor, CNPJ, Matrículas
- **Dados Pessoais**: Data de nascimento, filiação, assinaturas
- **Dados Financeiros**: Dados bancários (agência/conta), números de cartão de crédito
- **Contatos**: E-mails, telefones (fixo e celular)
- **Localização**: Endereços completos, placas de veículos, inscrições imobiliárias
- **Processos**: Processos SEI, protocolos LAI, ocorrências, processos genéricos
- **NER (Reconhecimento de Entidades)**: Nomes de pessoas, termos relacionados à saúde

### Como funciona?

O sistema analisa cada texto e:
1. **Detecta** entidades sensíveis usando padrões regex e NLP (spaCy)
2. **Calcula um score** de sensibilidade (0-100+) -> (Escolhi essa abordagem pois talvez um endereço
                                                    incompleto não entre como dado privado.)
3. **Classifica** o documento como **PÚBLICO** ou **PRIVADO**
4. **Gera um relatório** em Excel com todas as detecções

----------------------------------------------------------------------------------------------------

##  Funcionalidades

- **Detecção híbrida**: Combina regex (precisão) + NLP (contexto)
  **Validação inteligente**: CPF e outros documentos com validação de dígitos verificadores
  **Análise de contexto**: Detecta contexto ao redor das entidades (ex: "CPF: 123.456.789-01")
  **Processamento em lote**: Analisa centenas de textos em segundos
  **Relatório detalhado**: Excel com classificação, score e lista de entidades encontradas
 **Configurável**: Threshold de classificação ajustável

----------------------------------------------------------------------------------------------------
## Instalação

### 1. Clone ou baixe o projeto

```bash
git clone <url-do-repositorio>
cd "Hackathon-CapacitaDF-MarlonMBraga"
```

### 2. Instale as dependências Python

```bash
pip install -r requirements.txt
```

**Dependências instaladas:**
- `pandas` - Manipulação de dados tabulares
- `openpyxl` - Leitura/escrita de arquivos Excel
- `spacy` - Biblioteca de NLP para detecção de nomes
- `scikit-learn` - Ferramentas de machine learning (usado no scoring)
- `unidecode` - Normalização de textos com acentos

### 3. Baixe o modelo spaCy (IMPORTANTE!)

```bash
python -m spacy download pt_core_news_lg
```

>  **ATENÇÃO**: Este download tem ~500MB e é **obrigatório** para a detecção de nomes funcionar. O modelo usa transformers para reconhecimento de entidades em português.

### 4. Verifique a instalação

Execute o sistema sem arquivo para testar:

```bash
python Main.py
```

Se aparecer a mensagem `"ERRO: Arquivo de dados não encontrado!"`, a instalação está correta! ✅

-------------------------------------------------------------------------------------------------------------------

## Como Usar

### Passo 1: Prepare seu arquivo de dados

O sistema aceita dois formatos:
- **Excel**: `.xlsx` ou `.xls`
- **CSV**: `.csv` (separado por vírgula)
**Estrutura necessária:**
- **Coluna 1**: ID único de cada registro (ex: "1", "2", "3"...)
- **Coluna 2+**: Uma coluna contendo os textos a serem analisados -> De preferência a segunda coluna deve ser chamada "Texto Mascarado"

>  **Funcionalidade**: O sistema detecta automaticamente a coluna de texto procurando por nomes como "texto", "conteúdo", "conteudo". Se não encontrar, usa a segunda coluna.

### Passo 2: Coloque o arquivo na pasta correta

Copie seu arquivo para a pasta **`PastaExcel/`** na raiz do projeto:

```
Hackathon-CapacitaDF-MarlonMBraga/
├── Main.py
├── PastaExcel/          ← COLOQUE SEU ARQUIVO AQUI
│   └── meu_arquivo.xlsx
└── ...
```

### Passo 3: Execute o sistema

```bash
python Main.py
```

### Passo 4: Aguarde o processamento

Você verá uma saída como:

```
======================================================================
  SISTEMA DE DETECÇÃO 
======================================================================

 Lendo arquivo: PastaExcel\meu_arquivo.xlsx
  150 registros carregados
 OK-> Coluna de texto identificada: 'Texto'

 Processando textos...

   Processados: 10/150
   Processados: 20/150
   ...
   Processados: 150/150

======================================================================
  RESULTADO DA CLASSIFICAÇÃO
======================================================================
  Total de registros: 150
   PRIVADO: 87 (58.0%)
   PUBLICO: 63 (42.0%)
======================================================================

 Resultado salvo em: Resultado\resultado.xlsx

 Processamento concluído com sucesso!
```

----------------------------------------------------------------------------------------------------

##  Estrutura de Saída

### Localização do arquivo de resultado

O arquivo será salvo em:
```
Hackathon-CapacitaDF-MarlonMBraga/
└── Resultado/
    └── resultado.xlsx    ← ARQUIVO DE SAÍDA
```

### Colunas do arquivo Excel gerado

| Coluna | Descrição | Exemplo |
|--------|-----------|---------|
| **ID** | ID original do registro | 1 |
| **Texto Mascarado** | Texto original (sem mascaramento ainda) | "CPF: 123.456.789-01" |
| **ENTIDADES_ENCONTRADAS** | Lista de entidades detectadas | "CPF (1), Email (2)" |
| **CLASSIFICACAO** | PÚBLICO ou PRIVADO | PRIVADO |
| **SCORE** | Pontuação de sensibilidade (0-100+) | 100 |

### Interpretação da classificação

- **PRIVADO** (Score ≥ 30): Contém dados sensíveis que identificam pessoas
- **PUBLICO** (Score < 30): Não contém dados sensíveis significativos

**Exemplos de scores:**
- CPF detectado → **Score = 100** (muito sensível)
- Email detectado → **Score = 40** (moderadamente sensível)
- RG detectado → **Score = 80** (sensível)
- Apenas data genérica → **Score = 5** (baixa sensibilidade)

------------------------------------------------------------------------------------------------------

##  Configuração

### Ajustar o threshold de classificação

Edite o arquivo [Main.py](Main.py#L28):

```python
# Linha 28
detector = PIIDetector(threshold=30)  # Padrão: 30

# Exemplos:
# threshold=20  → Mais sensível (classifica mais como PRIVADO)
# threshold=50  → Menos sensível (classifica mais como PUBLICO)
```

### Customizar pesos de entidades

Edite o arquivo [components/utils/scoring_system.py](components/utils/scoring_system.py):

```python
# Exemplo: CPF vale 100 pontos
if entidades['cpf']:
    score += 100  # Altere este valor

# Exemplo: Email vale 40 pontos
if entidades['email']:
    score += 40  # Altere este valor
```

----------------------------------------------------------------------------------------------------

##  Resolução de Problemas

### Erro: "Modelo spaCy não encontrado"

**Solução:**
```bash
python -m spacy download pt_core_news_lg
```

### Erro: "Arquivo de dados não encontrado"

**Solução:**
1. Verifique se o arquivo está na pasta `PastaExcel/`
2. Certifique-se de que é `.xlsx`, `.xls` ou `.csv`
3. Verifique se a pasta está configurada corretamente em [components/config.py](components/config.py)
---

## Estrutura do Projeto

```## 
Hackathon-CapacitaDF-MarlonMBraga/
├── Main.py                          # Ponto de entrada principal
├── requirements.txt                 # Dependências Python
├── README.md                        # Documentação do projeto
├── PastaExcel/                      # Pasta de entrada (coloque arquivos aqui)
│   └── README.txt                   # Instruções de uso
├── Resultado/                       # Pasta de saída (resultados)
│   └── resultado.xlsx               # Arquivo de resultado gerado
└── components/                      # Módulos do sistema
    ├── config.py                    # Configuração (pasta de entrada)
    ├── pii_detector.py              # Classe principal do detector
    ├── detectors/                   # Detectores especializados
    │   ├── Contatos_detectors.py    # Email, telefone
    │   ├── DadosPessoais_detectors.py # Data nasc, filiação
    │   ├── Documentos_detectors.py  # CPF, RG, CNH, etc.
    │   ├── Financeiro_detectors.py  # Dados bancários, cartões
    │   ├── Localiza_Propriedades_detectors.py # Endereços, placas
    │   ├── Ner_detectors.py         # Nomes (NLP), termos saúde
    │   └── Processos_detectors.py   # Processos SEI, LAI, etc.
    ├── utils/                       #  Utilitários
    │   ├── context_data.py          # Dados de contexto (palavras-chave)
    │   ├── file_processor.py        # Processamento de Excel/CSV
    │   ├── scoring_system.py        # Sistema de pontuação
    │   └── spacy_loader.py          # Carregador do modelo spaCy
    └── validators/                  # Validadores (dígitos verificadores)
        └── Documentos_validador.py  # Validação de CPF, CNPJ, etc.
```

-------------------------------------------------------------------------------------------------------

## Olá avaliadores, espero que gostem do projeto, curti bastante criar ele, para qualquer dúvida podem me mandar mensagem.



