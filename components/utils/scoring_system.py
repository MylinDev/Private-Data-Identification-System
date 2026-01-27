from typing import Dict, List, Tuple

#                                     ==================== SISTEMA DE SCORING ====================

class PIIScoringSystem:
# '''     Sistema de pontuação para classificação de identificadores Pessoais. Decidi Adicionar outros possiveis dados pessoais,
#      Mesmo que não esstejam no Excel disponibilizado para o Hackathon.
    
    def __init__(self, threshold: int = 30):
        self.threshold = threshold
    
#            Calcula score de sensibilidade baseado nas entidades detectadas.   
    def calcular_score(self, entidades: Dict[str, List]) -> Tuple[int, List[str]]:
        score = 0
        resumo = []
#         CPF
        if entidades['cpf']:
            score += 100
            resumo.append(f"CPF ({len(entidades['cpf'])})")
#         CNPJ
        if entidades.get('cnpj'):
            score += 90
            resumo.append(f"CNPJ ({len(entidades['cnpj'])})")
#         RG
        if entidades['rg']:
            score += 80
            resumo.append(f"RG ({len(entidades['rg'])})")
        
#         Dados Bancários (MUITO sensível)
        if entidades.get('dados_bancarios'):
            score += 95
            resumo.append(f"Dados Bancários ({len(entidades['dados_bancarios'])})")

#         Cartão de Crédito (MUITO sensível)
        if entidades.get('cartao_credito'):
            score += 95
            resumo.append(f"Cartão ({len(entidades['cartao_credito'])})")
        
#         CNH (sensível)
        if entidades.get('cnh'):
            score += 80
            resumo.append(f"CNH ({len(entidades['cnh'])})")
        
#         Título de Eleitor (sensível)
        if entidades.get('titulo_eleitor'):
            score += 75
            resumo.append(f"Título Eleitor ({len(entidades['titulo_eleitor'])})")
        
#         Data de Nascimento (sensível)
        if entidades.get('data_nascimento'):
            score += 70
            resumo.append(f"Data Nasc ({len(entidades['data_nascimento'])})")
        
#         Filiação (sensível)
        if entidades.get('filiacao'):
            score += 70
            resumo.append(f"Filiação ({len(entidades['filiacao'])})")
        
#         Ocorrências (sensível - número de atendimento)
        if entidades.get('ocorrencia'):
            score += 70
            resumo.append(f"Ocorrência ({len(entidades['ocorrencia'])})")
        
#         Processo SEI (aumentado de 25 para 65)
        if entidades['processo_sei']:
            score += 65
            resumo.append(f"Processo SEI ({len(entidades['processo_sei'])})")
        
#         Processo Genérico
        if entidades.get('processo_generico'):
            score += 60
            resumo.append(f"Processo ({len(entidades['processo_generico'])})")
        
#         Protocolo LAI
        if entidades.get('protocolo_lai'):
            score += 60
            resumo.append(f"Protocolo LAI ({len(entidades['protocolo_lai'])})")
        
#         Dados de saúde (sensível)
        if entidades['saude']:
            score += 60
            resumo.append(f"Saúde ({len(entidades['saude'])} termos)")
        
#         Endereço/CEP
        if entidades.get('endereco'):
            score += 55
            resumo.append(f"Endereço ({len(entidades['endereco'])})")
        
#         Placa de Veículo
        if entidades.get('placa_veiculo'):
            score += 55
            resumo.append(f"Placa ({len(entidades['placa_veiculo'])})")
        
#         Inscrição Imobiliária/IPTU
        if entidades.get('inscricao_imobiliaria'):
            score += 55
            resumo.append(f"Inscr.Imob ({len(entidades['inscricao_imobiliaria'])})")
        
#         Nomes
        if entidades['nomes']:
            score += 50
            resumo.append(f"Nome ({len(entidades['nomes'])})")
        
#         Assinatura
        if entidades.get('assinatura'):
            score += 50
            resumo.append(f"Assinatura ({len(entidades['assinatura'])})")
        
#         Email
        if entidades['email']:
            score += 40
            resumo.append(f"Email ({len(entidades['email'])})")
        
#         Telefone
        if entidades['telefone']:
            score += 40
            resumo.append(f"Telefone ({len(entidades['telefone'])})")
        
#         Matrícula funcional
        if entidades['matricula']:
            score += 35
            resumo.append(f"Matrícula ({len(entidades['matricula'])})")
        
        return score, resumo

#        Classifica baseado no score e threshold.    
    def classificar(self, score: int) -> str:
        return 'PRIVADO' if score >= self.threshold else 'PUBLICO'