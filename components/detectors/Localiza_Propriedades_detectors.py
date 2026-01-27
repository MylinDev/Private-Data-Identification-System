import re
from typing import List
from ..utils.context_data import ContextData

class LocationDetectors:
#     Detectores para dados de localização e propriedades.
    
    def __init__(self):
        self.context_data = ContextData()
    
#            Detecta placas de veículo (formato antigo e Mercosul).    
    def detectar_placa_veiculo(self, texto: str) -> List[str]:
        placas = []
        
#         Padrões de placa brasileira
        padroes = [
            r'\b[A-Z]{3}[-\s]?\d[A-Z]\d{2}\b',
            r'\b[A-Z]{3}[-\s]?\d{4}\b',
        ]
        for padrao in padroes:
            for match in re.finditer(padrao, texto):
                placa_raw = match.group()
                placa_limpa = re.sub(r'[\s-]', '', placa_raw)
                if len(placa_limpa) >= 7 and placa_limpa[:3].isalpha():
                    pos = match.start()
                    janela = texto[max(0, pos-40):min(len(texto), pos+40)].lower()

#                     Aceita se tem contexto de veículo OU se formato é muito específico
                    contexto_veiculo = any(palavra in janela for palavra in [
                        'placa', 'veículo', 'veiculo', 'carro', 'moto', 'automóvel',
                        'automovel', 'caminhão', 'caminhao', 'van', 'ônibus', 'onibus'
                    ])
                    
#                     Formato Mercosul 
                    formato_mercosul = bool(re.match(r'^[A-Z]{3}\d[A-Z]\d{2}$', placa_limpa))
                    if contexto_veiculo or formato_mercosul:
                        placas.append(placa_raw)
        return list(set(placas))
    
#            Detecta endereços (com ou sem CEP, mas com contexto).    
    def detectar_endereco(self, texto: str) -> List[str]:
        enderecos = []
        padrao_cep_contexto = r'CEP[:\s]*\d{5}-?\d{3}'
        ceps_com_contexto = re.findall(padrao_cep_contexto, texto, re.IGNORECASE)
        enderecos.extend(ceps_com_contexto)
        
#         Padrões de endereço de rua COM CONTEXTO (palavra "endereço" ou "localizado")
        if 'endere' in texto.lower() or 'localizado' in texto.lower() or 'cobrança' in texto.lower():
            padroes_rua = [
                r'(?:Av\.|Avenida)\s+[\w\s]+,?\s+\d+',
                r'(?:R\.|Rua)\s+[\w\s]+,?\s+\d+',
                r'(?:Pç\.|Praça)\s+[\w\s]+,?\s+\d+',
                r'(?:Trav\.|Travessa)\s+[\w\s]+,?\s+\d+'
            ]
            for padrao in padroes_rua:
                matches = re.findall(padrao, texto, re.IGNORECASE)
                enderecos.extend(matches)
        
#         Busca padrões de endereço estruturados
        padroes_endereco = [
            r'(?:endere[çc]o[:\s]+)?SAS QUADRA \d+[\s\w,.-]+',
            r'(?:endere[çc]o[:\s]+)?Rua [\w\s]+,?\s*\d+',
            r'(?:endere[çc]o[:\s]+)?Quadra \d+[\s\w,.-]+',
            r'(?:endere[çc]o[:\s]+)?Lote \d+[\s\w,.-]+',
            r'Comercial [IVXLCDM]+,\s*Rua \d+',
            r'localizado[\s\w]+(?:Rua|Quadra|SAS|Av\.)'
        ]
        for padrao in padroes_endereco:
            matches = re.findall(padrao, texto, re.IGNORECASE)
            enderecos.extend(matches)
        return list(set(enderecos))

#            Detecta inscrições imobiliárias e IPTUs.    
    def detectar_inscricao_imobiliaria(self, texto: str) -> List[str]:
        inscricoes = []
        
#         Padrão: "inscrição" + "IPTU" ou "imobiliária" + número
        padroes = [
            r'inscri[çc][ãa]o\s+IPTU[\s:]+n[ºo°]\.?\s*\d{8,12}',
            r'inscri[çc][ãa]o\s+imobili[áa]ria[\s:]+n[ºo°]\.?\s*\d{8,12}',
            r'IPTU[\s:]+n[ºo°]\.?\s*\d{8,12}',
            r'inscri[çc][ãa]o[\s:]+\d{4,12}[-]?\d{0,2}'
        ]
        
        for padrao in padroes:
            matches = re.findall(padrao, texto, re.IGNORECASE)
            inscricoes.extend(matches)
        return list(set(inscricoes))