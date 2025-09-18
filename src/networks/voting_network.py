from src.networks.base_network import BaseNetwork
from tqdm import tqdm
from itertools import combinations

class VotingNetwork(BaseNetwork):
    def build_network(self):
        # Adicione todos os deputados como nós
        for dep_id, dep_nome in self.df[['id_deputado', 'nome']].drop_duplicates().itertuples(index=False):
            partido = self.df.loc[self.df['id_deputado'] == dep_id, 'siglaPartido'].iloc[0]
            uf = self.df.loc[self.df['id_deputado'] == dep_id, 'siglaUf'].iloc[0]
            self.G.add_node(dep_id, nome=dep_nome, partido=partido, uf=uf)

        # Agrupe por id da votação
        for votacao_id, grupo in tqdm(self.df.groupby('id')):
            # Crie um dicionário: id_deputado -> tipoVoto
            votos = grupo.set_index('id_deputado')['tipoVoto'].to_dict()
            deputados = list(votos.keys())
            # Para cada par de deputados, compare o voto
            for dep1, dep2 in combinations(deputados, 2):
                if not self.G.has_edge(dep1, dep2):
                    self.G.add_edge(dep1, dep2, weight=0)
                if votos[dep1] == votos[dep2]:
                    self.G[dep1][dep2]['weight'] += 1
                else:
                    self.G[dep1][dep2]['weight'] -= 1