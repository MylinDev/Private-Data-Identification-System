import re
from typing import Dict, List

#                               ==================== SISTEMA DE MASCARAMENTO ====================

# Mapeamento de cada tipo de entidade para o rótulo de substituição e cor do highlight
ENTITY_CONFIG = {
    'cpf':                   {'label': '[CPF OCULTO]',              'color': '#FF4444'},
    'rg':                    {'label': '[RG OCULTO]',               'color': '#FF6644'},
    'cnh':                   {'label': '[CNH OCULTA]',              'color': '#FF6644'},
    'titulo_eleitor':        {'label': '[TÍTULO OCULTO]',           'color': '#FF8844'},
    'cnpj':                  {'label': '[CNPJ OCULTO]',             'color': '#FF4444'},
    'matricula':             {'label': '[MATRÍCULA OCULTA]',        'color': '#FFAA44'},
    'data_nascimento':       {'label': '[DATA NASC. OCULTA]',       'color': '#FF8844'},
    'filiacao':              {'label': '[FILIAÇÃO OCULTA]',         'color': '#FF8844'},
    'assinatura':            {'label': '[ASSINATURA OCULTA]',       'color': '#FFAA44'},
    'dados_bancarios':       {'label': '[DADOS BANCÁRIOS OCULTOS]', 'color': '#FF2222'},
    'cartao_credito':        {'label': '[CARTÃO OCULTO]',           'color': '#FF2222'},
    'email':                 {'label': '[EMAIL OCULTO]',            'color': '#44AAFF'},
    'telefone':              {'label': '[TELEFONE OCULTO]',         'color': '#44AAFF'},
    'placa_veiculo':         {'label': '[PLACA OCULTA]',            'color': '#FFCC44'},
    'endereco':              {'label': '[ENDEREÇO OCULTO]',         'color': '#FFCC44'},
    'inscricao_imobiliaria': {'label': '[INSCRIÇÃO OCULTA]',        'color': '#FFCC44'},
    'processo_sei':          {'label': '[PROCESSO SEI OCULTO]',     'color': '#AA88FF'},
    'protocolo_lai':         {'label': '[PROTOCOLO LAI OCULTO]',    'color': '#AA88FF'},
    'ocorrencia':            {'label': '[OCORRÊNCIA OCULTA]',       'color': '#AA88FF'},
    'processo_generico':     {'label': '[PROCESSO OCULTO]',         'color': '#AA88FF'},
    'nomes':                 {'label': '[NOME OCULTO]',             'color': '#44DD88'},
    'saude':                 {'label': '[DADO SAÚDE OCULTO]',       'color': '#FF66AA'},
}


class PIIMasker:
    """Mascara (anonimiza) dados pessoais detectados no texto."""

    def mascarar_texto(self, texto: str, entidades: Dict[str, List[str]]) -> str:
        """Substitui cada entidade detectada pelo seu rótulo de mascaramento."""
        texto_mascarado = texto
        # Ordena entidades do maior para o menor para evitar substituições parciais
        substituicoes = []
        for tipo, valores in entidades.items():
            if tipo not in ENTITY_CONFIG or not valores:
                continue
            label = ENTITY_CONFIG[tipo]['label']
            for valor in valores:
                substituicoes.append((valor, label))

        # Ordena pela posição no texto (do final para o início) para não invalidar índices
        substituicoes.sort(key=lambda x: texto_mascarado.rfind(x[0]), reverse=True)

        for valor, label in substituicoes:
            texto_mascarado = texto_mascarado.replace(valor, label)

        return texto_mascarado

    def gerar_html_highlight(self, texto: str, entidades: Dict[str, List[str]]) -> str:
        """Gera HTML com cada entidade destacada em sua cor correspondente."""
        # Coleta todas as ocorrências com posição
        marcacoes = []
        for tipo, valores in entidades.items():
            if tipo not in ENTITY_CONFIG or not valores:
                continue
            config = ENTITY_CONFIG[tipo]
            for valor in valores:
                inicio = 0
                while True:
                    pos = texto.find(valor, inicio)
                    if pos == -1:
                        break
                    marcacoes.append((pos, pos + len(valor), tipo, valor, config['color']))
                    inicio = pos + 1

        if not marcacoes:
            return _escape_html(texto)

        # Remove sobreposições mantendo a marcação mais longa
        marcacoes.sort(key=lambda x: (x[0], -(x[1] - x[0])))
        filtradas = []
        ultimo_fim = 0
        for m in marcacoes:
            if m[0] >= ultimo_fim:
                filtradas.append(m)
                ultimo_fim = m[1]

        # Constrói HTML
        partes = []
        pos_atual = 0
        for inicio, fim, tipo, valor, cor in filtradas:
            if inicio > pos_atual:
                partes.append(_escape_html(texto[pos_atual:inicio]))
            label = ENTITY_CONFIG[tipo]['label']
            partes.append(
                f'<span style="background-color:{cor};color:#fff;padding:2px 6px;'
                f'border-radius:4px;font-weight:bold" title="{label}">'
                f'{_escape_html(valor)}</span>'
            )
            pos_atual = fim
        if pos_atual < len(texto):
            partes.append(_escape_html(texto[pos_atual:]))

        return ''.join(partes)


def _escape_html(text: str) -> str:
    """Escapa caracteres especiais para HTML."""
    return (text
            .replace('&', '&amp;')
            .replace('<', '&lt;')
            .replace('>', '&gt;')
            .replace('"', '&quot;'))
