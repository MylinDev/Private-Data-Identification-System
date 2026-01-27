import re
from typing import List
from ..validators.Documentos_validador import DocumentValidators
from ..utils.context_data import ContextData

#                                         ==================== DETECTORES REGEX ====================

class DocumentDetectors:
    """Detectores para documentos pessoais (CPF, RG, CNH, etc.)."""
    
    def __init__(self):
        self.context_data = ContextData()
        self.validators = DocumentValidators()
    
#            Detecta CPFs pelo formato (com ou sem validação de dígitos).    
    def detectar_cpf(self, texto: str) -> List[str]:
        cpfs_encontrados = []
        
#         Padrão COM contexto "CPF" (mais confiável - aceita mesmo se validação falhar)
#         Aceita 1 ou 2 dígitos finais (para CPFs mal formatados como 129.180.122-6)
        padrao_contexto = r'(?i)CPF[:\s]*\d{3}[.\s]?\d{3}[.\s]?\d{3}[-\s]?\d{1,2}'
        matches_com_contexto = re.findall(padrao_contexto, texto) 
        for match in matches_com_contexto:
            cpf_raw = re.sub(r'(?i)^CPF[:\s]*', '', match)
            cpf_numeros = re.sub(r'\D', '', cpf_raw)
            if len(cpf_numeros) >= 10 and len(cpf_numeros) <= 11:
                if cpf_numeros != cpf_numeros[0] * len(cpf_numeros):
                    if len(cpf_numeros) == 10:
                        cpf_raw_corrigido = cpf_raw.replace('-', '-0') if '-' in cpf_raw else cpf_raw
                        cpfs_encontrados.append(cpf_raw)
                    else:
                        cpfs_encontrados.append(cpf_raw)
        
#         Padrão SEM contexto - Opção 1: APENAS válidos (atual - evita falsos positivos)
        padrao_sem_contexto = r'\b\d{3}[.\s]?\d{3}[.\s]?\d{3}[-\s]?\d{2}\b'
        
        for match in re.finditer(padrao_sem_contexto, texto):
            cpf_raw = match.group()
            
#         Pula se já foi encontrado com contexto
            cpf_numeros_atual = re.sub(r'\D', '', cpf_raw)
            if any(re.sub(r'\D', '', cpf) == cpf_numeros_atual for cpf in cpfs_encontrados):
                continue
            
            cpf_numeros = re.sub(r'\D', '', cpf_raw)
            if len(cpf_numeros) == 11 and cpf_numeros != cpf_numeros[0] * 11:
                #CPFs com erro de digitação ainda são dados sensíveis
                cpfs_encontrados.append(cpf_raw)
        
        return list(set(cpfs_encontrados))  # Remove duplicatas
    
#            Detecta RG (padrões variados por estado).    
    def detectar_rg(self, texto: str) -> List[str]:
        rg_encontrados = []
        padroes = [
            r'\bRG[:\s]*\d{1,2}\.?\d{3}\.?\d{3}-?[0-9X]\b', 
            r'\b\d{1,2}\.?\d{3}\.?\d{3}-?[0-9X]\b',         
        ]
        for padrao in padroes:
            for match in re.finditer(padrao, texto, re.IGNORECASE):
                rg_raw = match.group()
                pos = match.start()
                janela = texto[max(0, pos-30):min(len(texto), pos+30)].lower() 
                if 'rg' in janela or 'registro geral' in janela:
                    rg_encontrados.append(rg_raw)
        return list(set(rg_encontrados))

#            Detecta CNH (Carteira Nacional de Habilitação) - 11 dígitos.
    def detectar_cnh(self, texto: str) -> List[str]:
        cnh_encontradas = []
        padroes = [
            r'\bCNH[:\s]*\d{11}\b', 
            r'\b\d{11}\b'  
        ]
        for padrao in padroes:
            for match in re.finditer(padrao, texto, re.IGNORECASE):
                cnh_raw = match.group()
                pos = match.start()
                janela = texto[max(0, pos-30):min(len(texto), pos+30)].lower()
                if any(palavra in janela for palavra in ['cnh', 'habilitação', 'habilitacao', 'carteira nacional']):
                    cnh_encontradas.append(cnh_raw)
        return list(set(cnh_encontradas))
    
#            Detecta Título de Eleitor - 12 dígitos.    
    def detectar_titulo_eleitor(self, texto: str) -> List[str]:
        titulos = []
        padroes = [
            r'\bTítulo[:\s]*\d{12}\b',
            r'\bTITULO[:\s]*\d{12}\b',
            r'\b\d{12}\b' 
        ]
        for padrao in padroes:
            for match in re.finditer(padrao, texto, re.IGNORECASE):
                titulo_raw = match.group()
                pos = match.start()
                janela = texto[max(0, pos-30):min(len(texto), pos+30)].lower()
                if any(palavra in janela for palavra in ['título', 'titulo', 'eleitor', 'eleitoral', 'tse']):
                    titulos.append(titulo_raw)  
        return list(set(titulos))
    
#            Detecta CNPJ com contexto.    
    def detectar_cnpj(self, texto: str) -> List[str]:
        cnpjs_validos = []
        
#         Padrão: palavra "CNPJ" seguida de número com 14 dígitos
        padrao = r'CNPJ[:\s]*\d{2}\.?\d{3}\.?\d{3}/?\d{4}-?\d{2}'
        matches = re.findall(padrao, texto, re.IGNORECASE) 
        for match in matches:
            numeros = re.sub(r'\D', '', match)
            if len(numeros) == 14:
                cnpjs_validos.append(match)
        return list(set(cnpjs_validos))

#           Detecta matrículas funcionais.    
    def detectar_matricula(self, texto: str) -> List[str]:
        matriculas = []
        
#         Busca palavra "matrícula" seguida de número
        padrao = r'[Mm]atr[íi]cula[:\s]*\d{1,2}\.?\d{3,5}-?\d{1,2}'
        matches = re.findall(padrao, texto)
        return list(set(matches))