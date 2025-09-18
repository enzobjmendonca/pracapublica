from src.clients.camara_client import CamaraClient
import pandas as pd
from tqdm.auto import tqdm

class DataEnricher:
    def __init__(self):
        self.camara_client = CamaraClient()
    
    def get_despesas_legislatura(self, id_legislatura: list[int], ano: int) -> pd.DataFrame:
        """
        Obtém despesas de uma legislatura
        """
        deputados = self.camara_client.get_deputados(idLegislatura=id_legislatura)
        despesas = []
        for deputado in tqdm(deputados, desc="Coletando despesas"):
            despesas_deputado = pd.DataFrame(self.camara_client.get_deputado_despesas(deputado['id'], ano))
            despesas_deputado['id_deputado'] = deputado['id']
            despesas_deputado['nome_deputado'] = deputado['nome']
            despesas_deputado['siglaUf_deputado'] = deputado['siglaUf']
            despesas_deputado['siglaPartido_deputado'] = deputado['siglaPartido']
            despesas.append(despesas_deputado)
        return pd.concat(despesas)
    
    def get_despesas_partido(self, sigla_partido: list[str], id_legislatura: list[int], ano: int) -> pd.DataFrame:
        """
        Obtém despesas de um partido
        """
        deputados = self.camara_client.get_deputados(siglaPartido=sigla_partido, idLegislatura=id_legislatura)
        despesas = []
        for deputado in tqdm(deputados, desc="Coletando despesas"):
            despesas_deputado = pd.DataFrame(self.camara_client.get_deputado_despesas(deputado['id'], ano))
            despesas_deputado['id_deputado'] = deputado['id']
            despesas_deputado['nome_deputado'] = deputado['nome']
            despesas_deputado['siglaUf_deputado'] = deputado['siglaUf']
            despesas_deputado['siglaPartido_deputado'] = deputado['siglaPartido']
            despesas.append(despesas_deputado)
        return pd.concat(despesas)
    
    def get_frentes_legislatura(self, id_legislatura: list[int]) -> pd.DataFrame:
        """
        Obtém frentes de uma legislatura
        """
        deputados = self.camara_client.get_deputados(idLegislatura=id_legislatura)
        frentes = []
        for deputado in tqdm(deputados, desc="Coletando frentes"):
            frentes_deputado = pd.DataFrame(self.camara_client.get_deputado_frentes(deputado['id']))
            frentes_deputado['id_deputado'] = deputado['id']
            frentes_deputado['nome_deputado'] = deputado['nome']
            frentes_deputado['siglaUf_deputado'] = deputado['siglaUf']
            frentes_deputado['siglaPartido_deputado'] = deputado['siglaPartido']
            frentes.append(frentes_deputado)
        return pd.concat(frentes)
    
    def get_votos_periodo(self, dataInicio: str, dataFim: str) -> pd.DataFrame:
        """
        Obtém votos de um período
        """
        votos = []
        votacoes = self.camara_client.get_votacoes(dataInicio = dataInicio, dataFim = dataFim)
        for votacao in tqdm(votacoes, desc="Coletando votos"):
            votos_votacao = self.camara_client.get_votacao_votos(votacao['id'])
            enriched_votos = []
            for voto in votos_votacao:
                deputado = voto['deputado_']
                deputado['id_deputado'] = deputado['id']
                del deputado['id']
                del voto['deputado_']
                enriched_voto = {**votacao, **voto, **deputado}
                enriched_votos.append(enriched_voto)
            votos.append(pd.DataFrame(enriched_votos))
        return pd.concat(votos)