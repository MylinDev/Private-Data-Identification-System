from typing import Set

#                                     ==================== CONSTANTES DE CONTEXTO ====================

class ContextData:
#        Classe com conjuntos de dados contextuais para detecção de PII.
    
    def __init__(self):
#                Palavras-chave de contexto sensível
        self.termos_saude: Set[str] = {
            'câncer', 'cancer', 'asmático', 'asmatico', 'diabético', 'diabetico',
            'hipertensão', 'hipertensao', 'HIV', 'AIDS', 'doença', 'doenca',
            'prontuário', 'prontuario', 'laudo', 'diagnóstico', 'diagnostico',
            'tratamento', 'cirurgia', 'internação', 'internacao', 'Huntington',
            'prescrição', 'prescricao', 'exame', 'CID', 'hospitalar'
        }
        
        self.contexto_pessoa: Set[str] = {
            'meu nome', 'me chamo', 'eu sou', 'sou', 'chamo-me',
            'nome:', 'requerente:', 'mãe:', 'mae:', 'pai:',
            'aluna:', 'aluno:', 'servidor:', 'servidora:',
            'cidadão:', 'cidadao:', 'cliente:', 'paciente:',
            'representada:', 'representado:', 'interessado:', 'solicitante:',
            'proprietária:', 'proprietário:', 'procuração', 'titular:'
        }
        
#                 DDDs brasileiros válidos
        self.ddds_validos: Set[str] = {
            '11', '12', '13', '14', '15', '16', '17', '18', '19','21', '22', '24','27','28','31', '32',
            '33', '34', '35', '37', '38','41', '42', '43', '44', '45', '46', '47', '48', '49','51', 
            '53', '54', '55','61','62', '64','63','65','66','67','68','69','71','73', '74','75','77',
            '79','81','82','83','84','85','86','87','88','89','91','92','93','94','95','96','97','98','99'
        }