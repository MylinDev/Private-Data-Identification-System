import re
from typing import List
from ..validators.Documentos_validador import DocumentValidators
from ..utils.context_data import ContextData

class FinancialDetectors:
#     Detectores para dados financeiros e bancários.
    
    def __init__(self):
        self.context_data = ContextData()
        self.validators = DocumentValidators()
    
#            Detecta dados bancários (agência, conta, banco).    
    def detectar_dados_bancarios(self, texto: str) -> List[str]:
        dados_bancarios = []
        
#         Padrões de dados bancários
        padroes = [
            r'(?:ag[êe]ncia|ag\.)\s*[:]?\s*\d{4}[-]?\d?',
            r'(?:conta|c/c|cc)\s*[:]?\s*\d{4,}[-]?\d?',
            r'(?:banco)\s*[:]?\s*\d{3}',
            r'\b\d{4}[-]\d\s+\d{5,}[-]\d\b'
        ]
        for padrao in padroes:
            for match in re.finditer(padrao, texto, re.IGNORECASE):
                dados_bancarios.append(match.group())
        
        return list(set(dados_bancarios))

#            Detecta números de cartão de crédito     
    def detectar_cartao_credito(self, texto: str) -> List[str]:
        cartoes = []
        
#         Padrões de cartão de crédito: 16 dígitos com ou sem espaços/hífens
        padroes = [
            r'\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b'
        ]
        
        for padrao in padroes:
            for match in re.finditer(padrao, texto):
                cartao_raw = match.group()
                digitos = re.sub(r'\D', '', cartao_raw)
                if len(digitos) == 16:
                    pos = match.start()
                    janela = texto[max(0, pos-50):min(len(texto), pos+50)].lower()
                    
#                     Contexto + Validação Luhn
                    contexto_ok = any(palavra in janela for palavra in [
                        'cartão', 'cartao', 'crédito', 'credito', 'card', 
                        'visa', 'master', 'elo', 'débito', 'debito', 'pagamento'
                    ])
                    if contexto_ok:
                        cartoes.append(cartao_raw)
        return list(set(cartoes))