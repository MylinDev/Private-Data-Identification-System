import spacy
import warnings

warnings.filterwarnings('ignore')

#    """Classe responsável pelo carregamento e gerenciamento do modelo spaCy."""
class SpacyLoader:
    def __init__(self):
        self.nlp = None
        self._load_spacy_model()
    
#              Carrega modelo spaCy pt_core_news_lg (transformer-based).
    def _load_spacy_model(self):
        try:
            self.nlp = spacy.load('pt_core_news_lg')
            print(" Modelo spaCy pt_core_news_lg carregado com sucesso")
        except OSError:
            print(" ERRO: Modelo spaCy não encontrado!")
            print(" Execute: python -m spacy download pt_core_news_lg") # Primeiro passo é o sucesso nessa execuçao.
            raise
    
    def get_nlp(self):
        return self.nlp