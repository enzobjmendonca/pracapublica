from abc import ABC, abstractmethod
import pandas as pd
import networkx as nx
import pandas as pd

class BaseNetwork(ABC):
    def __init__(self, df: pd.DataFrame):
        self.df = df
        self.G = nx.Graph()

    @abstractmethod
    def build_network(self):
        pass

    def get_network(self) -> nx.Graph:
        return self.G

    def get_sorted_edges(self) -> list[tuple[int, int, dict]]:
        return sorted(self.G.edges(data=True), key=lambda x: x[2]['weight'])

    