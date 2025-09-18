from src.networks.base_network import BaseNetwork
from tqdm import tqdm
from itertools import combinations


class FrenteNetwork(BaseNetwork):
    def build_network(self):
        # Adicione todos os deputados como nós
        for dep_id, dep_nome in self.df[['id_deputado', 'nome_deputado']].drop_duplicates().itertuples(index=False):
            partido = self.df.loc[self.df['id_deputado'] == dep_id, 'siglaPartido_deputado'].iloc[0]
            uf = self.df.loc[self.df['id_deputado'] == dep_id, 'siglaUf_deputado'].iloc[0]
            self.G.add_node(dep_id, nome=dep_nome, partido=partido, uf=uf)

        # Para cada par de deputados, conte quantas frentes compartilham
        deputados = self.df[['id_deputado', 'nome_deputado']].drop_duplicates()['id_deputado'].tolist()
        # Crie um dicionário: id_deputado -> set de frentes (titulo)
        dep_frentes = self.df.groupby('id_deputado')['titulo'].apply(set).to_dict()
        for dep1, dep2 in tqdm(combinations(deputados, 2), desc="Construindo rede de frentes"):
            # Interseção das frentes
            frentes_compartilhadas = dep_frentes.get(dep1, set()) & dep_frentes.get(dep2, set())
            peso = len(frentes_compartilhadas)
            if peso > 0:
                self.G.add_edge(dep1, dep2, weight=peso)