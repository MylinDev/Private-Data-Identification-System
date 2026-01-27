import re
from typing import List
from ..utils.context_data import ContextData

class PersonalDataDetectors:

#    Detectores para dados pessoais como datas de nascimento, filiação, etc. 
    def __init__(self):
        self.context_data = ContextData()
    
#            Detecta datas de nascimento com contexto.    
    def detectar_data_nascimento(self, texto: str) -> List[str]:
        datas_nascimento = []
        
#         Padrões de data DD/MM/AAAA ou DD-MM-AAAA
        padroes = [
            r'\b\d{2}[/-]\d{2}[/-]\d{4}\b',
            r'\b\d{2}[/-]\d{2}[/-]\d{2}\b'
        ]
        for padrao in padroes:
            for match in re.finditer(padrao, texto):
                data_raw = match.group()
                pos = match.start()
                janela = texto[max(0, pos-50):min(len(texto), pos+50)].lower()
                if any(palavra in janela for palavra in ['nascimento', 'nascido', 'nascida', 'nasc.', 'data nasc', 'dt nasc', 'dn:']):
                    datas_nascimento.append(data_raw)
        
        return list(set(datas_nascimento))
    
#             Detecta informações de filiação (nome dos pais).  
    def detectar_filiacao(self, texto: str) -> List[str]:
        filiacoes = []
        
#         Padrões de filiação
        padroes_contexto = [
            r'(?:mãe|mae|mother)\s*[:]?\s*([A-ZÁÀÂÃÉÈÊÍÏÓÔÕÖÚÇÑ][a-záàâãéèêíïóôõöúçñ]+(?:\s+[A-ZÁÀÂÃÉÈÊÍÏÓÔÕÖÚÇÑ][a-záàâãéèêíïóôõöúçñ]+)+)',
            r'(?:pai|father)\s*[:]?\s*([A-ZÁÀÂÃÉÈÊÍÏÓÔÕÖÚÇÑ][a-záàâãéèêíïóôõöúçñ]+(?:\s+[A-ZÁÀÂÃÉÈÊÍÏÓÔÕÖÚÇÑ][a-záàâãéèêíïóôõöúçñ]+)+)',
            r'(?:filiação|filiacao|filho\s+de)\s*[:]?\s*([A-ZÁÀÂÃÉÈÊÍÏÓÔÕÖÚÇÑ][a-záàâãéèêíïóôõöúçñ]+(?:\s+[A-ZÁÀÂÃÉÈÊÍÏÓÔÕÖÚÇÑ][a-záàâãéèêíïóôõöúçñ]+)+)'
        ]
        
        for padrao in padroes_contexto:
            for match in re.finditer(padrao, texto, re.IGNORECASE):
                filiacao = match.group(1) if match.lastindex else match.group()
                if len(filiacao) >= 10:  # Pelo menos 2 nomes
                    filiacoes.append(filiacao)
        
        return list(set(filiacoes))
    
#            Detecta menções a assinaturas ou dados assinados.    
    def detectar_assinatura(self, texto: str) -> List[str]:
        assinaturas = []
        
#         Padrões de contexto de assinatura
        padroes = [
            r'(?:assinatura|assinado por|signed by)\s*[:]?\s*([A-ZÁÀÂÃÉÈÊÍÏÓÔÕÖÚÇÑ][a-záàâãéèêíïóôõöúçñ]+(?:\s+[A-ZÁÀÂÃÉÈÊÍÏÓÔÕÖÚÇÑ][a-záàâãéèêíïóôõöúçñ]+)+)',
            r'(?:ass\.|assinatura digital)'
        ]
        for padrao in padroes:
            for match in re.finditer(padrao, texto, re.IGNORECASE):
                assinatura = match.group(1) if match.lastindex else match.group()
                assinaturas.append(assinatura)
        return list(set(assinaturas))