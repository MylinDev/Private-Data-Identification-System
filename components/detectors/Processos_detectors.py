import re
from typing import List
from ..utils.context_data import ContextData

class ProcessDetectors:
#        Detectores para processos administrativos e protocolos.
    
    def __init__(self):
        self.context_data = ContextData()
    
#            Detecta números de processos em contexto pessoal.   
    def detectar_processo_sei(self, texto: str) -> List[str]:
#         Padrão: 00015-01009853/2026-01
        padrao = r'\d{5}-\d{8}/\d{4}-\d{2}'
        processos = re.findall(padrao, texto)
        return list(set(processos))
    
#            Detecta protocolos LAI (Lei de Acesso à Informação).   
    def detectar_protocolo_lai(self, texto: str) -> List[str]:
#        Formato: LAI-258789/2025, LAI-258453/2026 
        padrao = r'LAI-\d{6}/\d{4}'
        protocolos = re.findall(padrao, texto, re.IGNORECASE)
        return list(set(protocolos))
    
#            Detecta números de ocorrências policiais/CBMDF.    
    def detectar_ocorrencia(self, texto: str) -> List[str]:
        ocorrencias = []
        padrao1 = r'ocorr[êe]ncia[\s:]+(?:n[ºo°]\.?\s*)?\d{13,20}'
        matches1 = re.findall(padrao1, texto, re.IGNORECASE)
        ocorrencias.extend(matches1)
        
#         Padrão: números longos isolados que podem ser ocorrências
#         Busca contexto de "atendida", "CBMDF", "polícia"
        if 'atendida' in texto.lower() or 'cbmdf' in texto.lower() or 'pol[íi]cia' in texto.lower():
            padrao2 = r'\b\d{13,20}\b'
            matches2 = re.findall(padrao2, texto)
            ocorrencias.extend(matches2)
        return list(set(ocorrencias))
    
#            Detecta processos administrativos e judiciais (evita confusão com datas).    
    def detectar_processo_generico(self, texto: str) -> List[str]:
        processos = []
        
#        Padrão 1: 0315-000009878/2023-15 (processo judicial/administrativo completo)
        padrao1 = r'\d{4}-\d{9,12}/\d{4}-\d{2}'
        matches1 = re.findall(padrao1, texto)
        processos.extend(matches1)
        padrao2 = r'\b\d{4}-\d{4,9}/\d{4}\b'
        matches2 = re.findall(padrao2, texto)

#         Filtra para evitar datas tipo "1234-567890/2019" que seja mês-dia/ano
        for match in matches2:
            processos.append(match)
        if 'processo' in texto.lower():
            padrao3 = r'\d{6,7}/\d{4}-\d{2}'
            matches3 = re.findall(padrao3, texto)

#             Filtra datas (verifica se o primeiro número é mês válido 01-12)
            for match in matches3:
                primeiro_num = int(match.split('/')[0][:2])
                if primeiro_num > 12 or len(match.split('/')[0]) > 2:
                    processos.append(match)
        padrao4 = r'\d{7}-\d{2}\.\d{4}\.\d{1,2}\.\d{2}\.\d{4}'
        matches4 = re.findall(padrao4, texto)
        processos.extend(matches4)
        return list(set(processos))