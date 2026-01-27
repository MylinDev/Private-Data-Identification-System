import re
from typing import List
from ..utils.context_data import ContextData

class ContactDetectors:

    #    Detectores para informações de contato (email, telefone).
    def __init__(self):
        self.context_data = ContextData()
    
#            Detecta endereços de email (RFC 5322 simplificado).    
    def detectar_email(self, texto: str) -> List[str]:
        # Padrão para emails
        padrao = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(padrao, texto)
        return list(set(emails))

#            Detecta telefones brasileiros (fixo e celular com DDD).
    def detectar_telefone(self, texto: str) -> List[str]:
        telefones = []
        
#         Padrões FORMATADOS
        padroes_formatados = [
            r'\(\d{2}\)\s*9?\d{4}-?\d{4}',  # (61) 99999-9999
            r'\b\d{2}\s+9\d{4}[-\s]?\d{4}\b',
        ]
        for padrao in padroes_formatados:
            for match in re.finditer(padrao, texto):
                numeros = re.sub(r'\D', '', match.group())
                if len(numeros) in [10, 11] and numeros[:2] in self.context_data.ddds_validos:
                    telefones.append(match.group())
        
#         Padrões NÃO FORMATADOS , EXIGE contexto
        padrao_solto = r'\b\d{10,11}\b'
        for match in re.finditer(padrao_solto, texto):
            numeros = match.group()
            
#             Pula se já foi detectado na versão formatada
            if any(re.sub(r'\D', '', tel) == numeros for tel in telefones):
                continue
            
#             Valida DDD
            if numeros[:2] not in self.context_data.ddds_validos:
                continue
            
#             EXIGE contexto de telefone
            pos = match.start()
            janela = texto[max(0, pos-40):min(len(texto), pos+40)].lower()
            
            contexto_telefone = any(palavra in janela for palavra in [
                'telefone', 'fone', 'celular', 'whatsapp', 'contato', 
                'ligar', 'tel:', 'cel:', 'mobile', 'ramal'
            ])
            
            if contexto_telefone and len(numeros) in [10, 11]:
                telefones.append(numeros)
        
        return list(set(telefones))