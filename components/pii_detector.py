from typing import Dict, List
from .detectors.Documentos_detectors import DocumentDetectors
from .detectors.DadosPessoais_detectors import PersonalDataDetectors
from .detectors.Financeiro_detectors import FinancialDetectors
from .detectors.Contatos_detectors import ContactDetectors
from .detectors.Localiza_Propriedades_detectors import LocationDetectors
from .detectors.Processos_detectors import ProcessDetectors
from .detectors.Ner_detectors import NERDetectors
from .utils.scoring_system import PIIScoringSystem
from .utils.file_processor import FileProcessor
import warnings
warnings.filterwarnings('ignore')

#    Detector híbrido de Identificações Pessoais para textos em PT-BR (PII)
class PIIDetector:
    
#           Inicializa o detector com threshold de classificação.    
    def __init__(self, threshold: int = 30):
        self.threshold = threshold
        
#         Inicializa todos os detectores especializados
        self.document_detectors = DocumentDetectors()
        self.personal_data_detectors = PersonalDataDetectors()
        self.financial_detectors = FinancialDetectors()
        self.contact_detectors = ContactDetectors()
        self.location_detectors = LocationDetectors()
        self.process_detectors = ProcessDetectors()
        self.ner_detectors = NERDetectors()
        
#         Sistema de scoring
        self.scoring_system = PIIScoringSystem(threshold)
        
#         Processador de arquivos
        self.file_processor = FileProcessor()
    
#                                         ==================== MÉTODO PRINCIPAL ====================

#        Detecta todas as categorias de PII em um texto.    
    def detectar_pii(self, texto: str) -> Dict:
        if not texto or not isinstance(texto, str):
            return {
                'entidades': {},
                'score': 0,
                'classificacao': 'PUBLICO',
                'resumo': []
            }
        
#         Executa todos os detectores
        entidades = {
            'cpf': self.document_detectors.detectar_cpf(texto),
            'rg': self.document_detectors.detectar_rg(texto),
            'cnh': self.document_detectors.detectar_cnh(texto),
            'titulo_eleitor': self.document_detectors.detectar_titulo_eleitor(texto),
            'cnpj': self.document_detectors.detectar_cnpj(texto),
            'matricula': self.document_detectors.detectar_matricula(texto),            
            'data_nascimento': self.personal_data_detectors.detectar_data_nascimento(texto),
            'filiacao': self.personal_data_detectors.detectar_filiacao(texto),
            'assinatura': self.personal_data_detectors.detectar_assinatura(texto),            
            'dados_bancarios': self.financial_detectors.detectar_dados_bancarios(texto),
            'cartao_credito': self.financial_detectors.detectar_cartao_credito(texto),            
            'email': self.contact_detectors.detectar_email(texto),
            'telefone': self.contact_detectors.detectar_telefone(texto),            
            'placa_veiculo': self.location_detectors.detectar_placa_veiculo(texto),
            'endereco': self.location_detectors.detectar_endereco(texto),
            'inscricao_imobiliaria': self.location_detectors.detectar_inscricao_imobiliaria(texto),            
            'processo_sei': self.process_detectors.detectar_processo_sei(texto),
            'protocolo_lai': self.process_detectors.detectar_protocolo_lai(texto),
            'ocorrencia': self.process_detectors.detectar_ocorrencia(texto),
            'processo_generico': self.process_detectors.detectar_processo_generico(texto),            
            'nomes': self.ner_detectors.detectar_nomes(texto),
            'saude': self.ner_detectors.detectar_termos_saude(texto)
        }
        
#         Calcula score e classificação
        score, resumo = self.scoring_system.calcular_score(entidades)
        classificacao = self.scoring_system.classificar(score)       
        return {
            'entidades': entidades,
            'score': score,
            'classificacao': classificacao,
            'resumo': resumo
        }
    
#                                    ==================== PROCESSAMENTO EM LOTE ====================

#        Processa arquivo Excel/CSV com textos e gera resultado classificado.    
    def processar_arquivo(self, arquivo_entrada: str, arquivo_saida: str = None):
        return self.file_processor.processar_arquivo(
            arquivo_entrada, 
            arquivo_saida, 
            detector_callback=self.detectar_pii
        )