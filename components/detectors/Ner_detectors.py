from typing import List
from ..utils.context_data import ContextData
from ..utils.spacy_loader import SpacyLoader

#                                     ==================== DETECTOR NER (NOMES) ====================

class NERDetectors:
#      Detectores baseados em NLP usando spaCy.
    
    def __init__(self):
        self.context_data = ContextData()
        self.spacy_loader = SpacyLoader()
    
#            Detecta nomes de pessoas usando spaCy NER (entidades PERSON).    
    def detectar_nomes(self, texto: str) -> List[str]:
        nlp = self.spacy_loader.get_nlp()
        if not nlp:
            return []
        
        doc = nlp(texto)
        nomes_encontrados = []
        for ent in doc.ents:
            if ent.label_ == 'PER':  # PERSON entity
                nome = ent.text.strip()
                
#                # Filtros de qualidade
                palavras = nome.split()
                if len(palavras) < 2:
                    continue
                
#           Verificar contexto de primeira pessoa ou rótulo
                inicio_ent = ent.start_char
                janela = texto[max(0, inicio_ent-100):min(len(texto), inicio_ent+100)].lower()
                tem_contexto_pessoa = any(ctx in janela for ctx in self.context_data.contexto_pessoa)
                if tem_contexto_pessoa:
                    nomes_encontrados.append(nome)
                else:
                    nomes_encontrados.append(nome)
        return list(set(nomes_encontrados))
    
#            Detecta termos relacionados a dados sensíveis de saúde.    
    def detectar_termos_saude(self, texto: str) -> List[str]:
        texto_lower = texto.lower()
        termos_encontrados = []
        for termo in self.context_data.termos_saude:
            if termo in texto_lower:
                termos_encontrados.append(termo)
        return termos_encontrados