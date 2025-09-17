"""
Cliente Python para a API de Dados Abertos da Câmara dos Deputados
https://dadosabertos.camara.leg.br/swagger/api.html
"""

import requests
import httpx
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
from datetime import datetime
import json
import logging

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class CamaraConfig:
    """Configurações para o cliente da API da Câmara"""
    base_url: str = "https://dadosabertos.camara.leg.br/api/v2"
    timeout: int = 30
    max_retries: int = 3
    user_agent: str = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"

class CamaraAPIError(Exception):
    """Exceção customizada para erros da API da Câmara"""
    pass

class CamaraClient:
    """
    Cliente para a API de Dados Abertos da Câmara dos Deputados
    
    Este cliente fornece métodos para acessar dados sobre:
    - Deputados (dados, despesas, discursos, eventos, frentes, histórico, mandatos externos, ocupações, órgãos, profissões, proposições, votações)
    - Proposições legislativas (dados, autores, relatorias, relacionadas, tramitações, votações, temas)
    - Votações (dados, votos, orientações)
    - Partidos (dados, membros, líderes)
    - Órgãos (dados, membros, eventos, votações)
    - Eventos (dados, deputados, órgãos, pauta, votações)
    - Frentes parlamentares (dados, membros)
    - Grupos interparlamentares (dados, membros, histórico)
    - Legislaturas (dados, líderes, mesa)
    - Blocos partidários (dados, partidos)
    - Referências completas (tipos, situações, temas, códigos, etc.)
    """
    
    def __init__(self, config: Optional[CamaraConfig] = None):
        """
        Inicializa o cliente da API da Câmara
        
        Args:
            config: Configurações personalizadas (opcional)
        """
        self.config = config or CamaraConfig()
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': self.config.user_agent,
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        })
    
    def _make_request(self, endpoint: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Faz uma requisição para a API da Câmara
        
        Args:
            endpoint: Endpoint da API (ex: '/deputados')
            params: Parâmetros da query string
            
        Returns:
            Dados retornados pela API
            
        Raises:
            CamaraAPIError: Em caso de erro na requisição
        """
        url = f"{self.config.base_url}{endpoint}"
        
        try:
            logger.info(f"Fazendo requisição para: {url}")
            response = self.session.get(
                url, 
                params=params, 
                timeout=self.config.timeout
            )
            response.raise_for_status()
            
            return response.json()
            
        except requests.exceptions.RequestException as e:
            error_msg = f"Erro na requisição para {url}: {str(e)}"
            logger.error(error_msg)
            raise CamaraAPIError(error_msg) from e
        except json.JSONDecodeError as e:
            error_msg = f"Erro ao decodificar JSON da resposta: {str(e)}"
            logger.error(error_msg)
            raise CamaraAPIError(error_msg) from e
    
    def _get_paginated_data(self, endpoint: str, params: Optional[Dict] = None, 
                           max_pages: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Obtém dados paginados da API
        
        Args:
            endpoint: Endpoint da API
            params: Parâmetros da query string
            max_pages: Número máximo de páginas a buscar (None = todas)
            
        Returns:
            Lista com todos os dados das páginas
        """
        all_data = []
        page = 1
        
        while True:
            if max_pages and page > max_pages:
                break
                
            current_params = params.copy() if params else {}
            current_params['pagina'] = page
            current_params['itens'] = 100  # Máximo de itens por página
            
            try:
                response = self._make_request(endpoint, current_params)
                
                if 'dados' not in response:
                    break
                    
                data = response['dados']
                if not data:
                    break
                    
                all_data.extend(data)
                
                # Verifica se há mais páginas
                links = response.get('links', [])
                has_next = any(link.get('rel') == 'next' for link in links)
                
                if not has_next:
                    break
                    
                page += 1
                
            except CamaraAPIError:
                break
        
        return all_data
    
    # ==================== DEPUTADOS ====================
    
    def get_deputados(self, 
                     id: Optional[int] = None,
                     nome: Optional[str] = None,
                     siglaUf: Optional[str] = None,
                     siglaPartido: Optional[str] = None,
                     idLegislatura: Optional[int] = None,
                     dataInicio: Optional[str] = None,
                     dataFim: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Obtém lista de deputados
        
        Args:
            id: ID do deputado
            nome: Nome do deputado
            siglaUf: Sigla da UF
            siglaPartido: Sigla do partido
            idLegislatura: ID da legislatura
            dataInicio: Data de início (formato YYYY-MM-DD)
            dataFim: Data de fim (formato YYYY-MM-DD)
            
        Returns:
            Lista de deputados
        """
        params = {}
        if id is not None:
            params['id'] = id
        if nome is not None:
            params['nome'] = nome
        if siglaUf is not None:
            params['siglaUf'] = siglaUf
        if siglaPartido is not None:
            params['siglaPartido'] = siglaPartido
        if idLegislatura is not None:
            params['idLegislatura'] = idLegislatura
        if dataInicio is not None:
            params['dataInicio'] = dataInicio
        if dataFim is not None:
            params['dataFim'] = dataFim
            
        return self._get_paginated_data('/deputados', params if params else None)
    
    def get_deputado(self, deputado_id: int) -> Dict[str, Any]:
        """
        Obtém dados de um deputado específico
        
        Args:
            deputado_id: ID do deputado
            
        Returns:
            Dados do deputado
        """
        return self._make_request(f'/deputados/{deputado_id}')
    
    def get_deputado_despesas(self, deputado_id: int, ano: int, 
                             mes: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Obtém despesas de um deputado
        
        Args:
            deputado_id: ID do deputado
            ano: Ano das despesas
            mes: Mês das despesas (opcional)
            
        Returns:
            Lista de despesas
        """
        params = {'ano': ano}
        if mes:
            params['mes'] = mes
            
        return self._get_paginated_data(f'/deputados/{deputado_id}/despesas', params)
    
    def get_deputado_discursos(self, deputado_id: int,
                               idLegislatura: Optional[int] = None,
                               dataInicio: Optional[str] = None,
                               dataFim: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Obtém discursos de um deputado
        Retorna uma lista de informações sobre os pronunciamentos feitos pelo deputado identificado por {id} que tenham sido registrados, em quaisquer eventos, nos sistemas da Câmara.

        Caso os parâmetros de tempo (dataInicio, dataFim e idLegislatura) não sejam configurados na requisição, são buscados os discursos ocorridos nos sete dias anteriores ao da requisição.

        Args:
            deputado_id: ID do deputado
            idLegislatura: ID da legislatura (opcional)
            dataInicio: Data de início (formato YYYY-MM-DD, opcional)
            dataFim: Data de fim (formato YYYY-MM-DD, opcional)
            ordenarPor: Campo para ordenação (opcional)
            ordenarDesc: Ordenação descendente (True/False, opcional)
        
        Returns:
            Lista de discursos
        """
        params = {}
        if idLegislatura is not None:
            params['idLegislatura'] = idLegislatura
        if dataInicio is not None:
            params['dataInicio'] = dataInicio
        if dataFim is not None:
            params['dataFim'] = dataFim
        
        return self._get_paginated_data(f'/deputados/{deputado_id}/discursos', params if params else None)

    def get_deputado_eventos(self, deputado_id: int,
                            id: Optional[int] = None,
                            dataInicio: Optional[str] = None,
                            dataFim: Optional[str] = None,
                            idOrgao: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Obtém eventos de um deputado
        
        Args:
            deputado_id: ID do deputado
            id: ID do evento
            dataInicio: Data de início (formato YYYY-MM-DD)
            dataFim: Data de fim (formato YYYY-MM-DD)
            idOrgao: ID do órgão
            
        Returns:
            Lista de eventos
        """
        params = {}
        if id is not None:
            params['id'] = id
        if dataInicio is not None:
            params['dataInicio'] = dataInicio
        if dataFim is not None:
            params['dataFim'] = dataFim
        if idOrgao is not None:
            params['idOrgao'] = idOrgao
            
        return self._get_paginated_data(f'/deputados/{deputado_id}/eventos', params if params else None)

    def get_deputado_frentes(self, deputado_id: int) -> List[Dict[str, Any]]:
        """
        Obtém frentes parlamentares de um deputado
        
        Args:
            deputado_id: ID do deputado
            
        Returns:
            Lista de frentes parlamentares
        """
        return self._make_request(f'/deputados/{deputado_id}/frentes', {})['dados']

    def get_deputado_ocupacoes(self, deputado_id: int) -> List[Dict[str, Any]]:
        """
        Obtém ocupações de um deputado
        
        Args:
            deputado_id: ID do deputado
            
        Returns:
            Lista de ocupações
        """
        return self._make_request(f'/deputados/{deputado_id}/ocupacoes', {})['dados']

    def get_deputado_orgaos(self, deputado_id: int,
                           id: Optional[int] = None,
                           dataInicio: Optional[str] = None,
                           dataFim: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Obtém órgãos de um deputado
        
        Args:
            deputado_id: ID do deputado
            id: ID do órgão
            dataInicio: Data de início (formato YYYY-MM-DD)
            dataFim: Data de fim (formato YYYY-MM-DD)
            
        Returns:
            Lista de órgãos
        """
        params = {}
        if id is not None:
            params['id'] = id
        if dataInicio is not None:
            params['dataInicio'] = dataInicio
        if dataFim is not None:
            params['dataFim'] = dataFim
            
        return self._get_paginated_data(f'/deputados/{deputado_id}/orgaos', params if params else None)

    def get_deputado_profissoes(self, deputado_id: int) -> List[Dict[str, Any]]:
        """
        Obtém profissões de um deputado
        
        Args:
            deputado_id: ID do deputado
            
        Returns:
            Lista de profissões
        """
        return self._make_request(f'/deputados/{deputado_id}/profissoes', {})['dados']

    def get_deputado_historico(self, deputado_id: int, 
                            dataInicio: Optional[str] = None,
                            dataFim: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Obtém histórico de mudanças no exercício parlamentar de um deputado
        
        Args:
            deputado_id: ID do deputado
            
        Returns:
            Lista de mudanças no exercício parlamentar
        """
        params = {}
        if dataInicio is not None:
            params['dataInicio'] = dataInicio
        if dataFim is not None:
            params['dataFim'] = dataFim
        return self._make_request(f'/deputados/{deputado_id}/historico', params)['dados']

    def get_deputado_mandatos_externos(self, deputado_id: int) -> List[Dict[str, Any]]:
        """
        Obtém outros cargos eletivos já exercidos pelo parlamentar
        
        Args:
            deputado_id: ID do deputado
            
        Returns:
            Lista de mandatos externos
        """
        return self._make_request(f'/deputados/{deputado_id}/mandatosExternos', {})['dados']

    def get_deputado_proposicoes(self, deputado_id: int,
                                id: Optional[int] = None,
                                sigla: Optional[str] = None,
                                numero: Optional[int] = None,
                                ano: Optional[int] = None,
                                siglaTipo: Optional[str] = None,
                                codTema: Optional[int] = None,
                                dataInicio: Optional[str] = None,
                                dataFim: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Obtém proposições de um deputado
        
        Args:
            deputado_id: ID do deputado
            id: ID da proposição
            sigla: Sigla da proposição
            numero: Número da proposição
            ano: Ano da proposição
            siglaTipo: Sigla do tipo de proposição
            codTema: Código do tema
            dataInicio: Data de início (formato YYYY-MM-DD)
            dataFim: Data de fim (formato YYYY-MM-DD)
            
        Returns:
            Lista de proposições
        """
        params = {}
        if id is not None:
            params['id'] = id
        if sigla is not None:
            params['sigla'] = sigla
        if numero is not None:
            params['numero'] = numero
        if ano is not None:
            params['ano'] = ano
        if siglaTipo is not None:
            params['siglaTipo'] = siglaTipo
        if codTema is not None:
            params['codTema'] = codTema
        if dataInicio is not None:
            params['dataInicio'] = dataInicio
        if dataFim is not None:
            params['dataFim'] = dataFim
            
        return self._make_request(f'/deputados/{deputado_id}/proposicoes', params if params else None)['dados']
    
    def get_deputado_votacoes(self, deputado_id: int,
                            id: Optional[int] = None,
                            idProposicao: Optional[int] = None,
                            dataInicio: Optional[str] = None,
                            dataFim: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Obtém votações de um deputado
        
        Args:
            deputado_id: ID do deputado
            id: ID da votação
            idProposicao: ID da proposição
            dataInicio: Data de início (formato YYYY-MM-DD)
            dataFim: Data de fim (formato YYYY-MM-DD)
            
        Returns:
            Lista de votações
        """
        params = {}
        if id is not None:
            params['id'] = id
        if idProposicao is not None:
            params['idProposicao'] = idProposicao
        if dataInicio is not None:
            params['dataInicio'] = dataInicio
        if dataFim is not None:
            params['dataFim'] = dataFim
            
        return self._get_paginated_data(f'/deputados/{deputado_id}/votacoes', params if params else None)
    
    # ==================== PROPOSIÇÕES ====================
    
    def get_proposicoes(self,
                       id: Optional[Union[int, List[int], str]] = None,
                       siglaTipo: Optional[Union[str, List[str]]] = None,
                       numero: Optional[Union[int, List[int], str]] = None,
                       ano: Optional[Union[int, List[int], str]] = None,
                       codTipo: Optional[Union[int, List[int], str]] = None,
                       idDeputadoAutor: Optional[Union[int, List[int], str]] = None,
                       autor: Optional[str] = None,
                       siglaPartidoAutor: Optional[Union[str, List[str]]] = None,
                       idPartidoAutor: Optional[int] = None,
                       siglaUfAutor: Optional[Union[str, List[str]]] = None,
                       keywords: Optional[Union[str, List[str]]] = None,
                       tramitacaoSenado: Optional[bool] = None,
                       dataInicio: Optional[str] = None,
                       dataFim: Optional[str] = None,
                       dataApresentacaoInicio: Optional[str] = None,
                       dataApresentacaoFim: Optional[str] = None,
                       codSituacao: Optional[Union[int, List[int], str]] = None,
                       codTema: Optional[Union[int, List[int], str]] = None
                       ) -> List[Dict[str, Any]]:
        """
        Obtém lista de proposições
        
        Args:
            id: ID da proposição
            siglaTipo: Sigla do tipo de proposição
            numero: Número da proposição
            ano: Ano da proposição
            codTipo: Código do tipo de proposição
            idDeputadoAutor: ID do deputado autor
            autor: Nome do autor
            siglaPartidoAutor: Sigla do partido do autor
            idPartidoAutor: ID do partido do autor
            siglaUfAutor: Sigla da UF do autor
            keywords: Palavras-chave
            tramitacaoSenado: Se tem tramitação no Senado
            dataInicio: Data de início (formato YYYY-MM-DD)
            dataFim: Data de fim (formato YYYY-MM-DD)
            dataApresentacaoInicio: Data de apresentação inicial (formato YYYY-MM-DD)
            dataApresentacaoFim: Data de apresentação final (formato YYYY-MM-DD)
            codSituacao: Código da situação
            codTema: Código do tema

        Returns:
            Lista de proposições
        """
        params = {}
        if id is not None:
            params['id'] = id
        if siglaTipo is not None:
            params['siglaTipo'] = siglaTipo
        if numero is not None:
            params['numero'] = numero
        if ano is not None:
            params['ano'] = ano
        if codTipo is not None:
            params['codTipo'] = codTipo
        if idDeputadoAutor is not None:
            params['idDeputadoAutor'] = idDeputadoAutor
        if autor is not None:
            params['autor'] = autor
        if siglaPartidoAutor is not None:
            params['siglaPartidoAutor'] = siglaPartidoAutor
        if idPartidoAutor is not None:
            params['idPartidoAutor'] = idPartidoAutor
        if siglaUfAutor is not None:
            params['siglaUfAutor'] = siglaUfAutor
        if keywords is not None:
            params['keywords'] = keywords
        if tramitacaoSenado is not None:
            params['tramitacaoSenado'] = tramitacaoSenado
        if dataInicio is not None:
            params['dataInicio'] = dataInicio
        if dataFim is not None:
            params['dataFim'] = dataFim
        if dataApresentacaoInicio is not None:
            params['dataApresentacaoInicio'] = dataApresentacaoInicio
        if dataApresentacaoFim is not None:
            params['dataApresentacaoFim'] = dataApresentacaoFim
        if codSituacao is not None:
            params['codSituacao'] = codSituacao
        if codTema is not None:
            params['codTema'] = codTema
            
        return self._get_paginated_data('/proposicoes', params if params else None)
    
    def get_proposicao(self, proposicao_id: int) -> Dict[str, Any]:
        """
        Obtém dados de uma proposição específica
        
        Args:
            proposicao_id: ID da proposição
            
        Returns:
            Dados da proposição
        """
        return self._make_request(f'/proposicoes/{proposicao_id}')['dados']
    
    def get_proposicao_autores(self, proposicao_id: int) -> List[Dict[str, Any]]:
        """
        Obtém autores de uma proposição
        
        Args:
            proposicao_id: ID da proposição
            
        Returns:
            Lista de autores
        """
        return self._make_request(f'/proposicoes/{proposicao_id}/autores')['dados']
    
    def get_proposicao_tramitacoes(self, proposicao_id: int) -> List[Dict[str, Any]]:
        """
        Obtém tramitações de uma proposição
        
        Args:
            proposicao_id: ID da proposição
            
        Returns:
            Lista de tramitações
        """
        return self._make_request(f'/proposicoes/{proposicao_id}/tramitacoes')['dados']
    
    def get_proposicao_votacoes(self, proposicao_id: int) -> List[Dict[str, Any]]:
        """
        Obtém votações de uma proposição
        
        Args:
            proposicao_id: ID da proposição
            
        Returns:
            Lista de votações
        """
        return self._make_request(f'/proposicoes/{proposicao_id}/votacoes')['dados']

    def get_proposicao_temas(self, proposicao_id: int) -> List[Dict[str, Any]]:
        """
        Obtém temas de uma proposição
        
        Args:
            proposicao_id: ID da proposição
            
        Returns:
            Lista de temas
        """
        return self._make_request(f'/proposicoes/{proposicao_id}/temas')['dados']

    def get_proposicao_relacionadas(self, proposicao_id: int) -> List[Dict[str, Any]]:
        """
        Obtém proposições relacionadas a uma proposição específica
        
        Args:
            proposicao_id: ID da proposição
            
        Returns:
            Lista de proposições relacionadas
        """
        return self._make_request(f'/proposicoes/{proposicao_id}/relacionadas')['dados']
    
    # ==================== VOTAÇÕES ====================
    
    def get_votacoes(self,
                    id: Optional[int] = None,
                    idProposicao: Optional[int] = None,
                    dataInicio: Optional[str] = None,
                    dataFim: Optional[str] = None,
                    idOrgao: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Obtém lista de votações
        
        Args:
            id: ID da votação
            idProposicao: ID da proposição
            dataInicio: Data de início (formato YYYY-MM-DD)
            dataFim: Data de fim (formato YYYY-MM-DD)
            idOrgao: ID do órgão
            
        Returns:
            Lista de votações
        """
        params = {}
        if id is not None:
            params['id'] = id
        if idProposicao is not None:
            params['idProposicao'] = idProposicao
        if dataInicio is not None:
            params['dataInicio'] = dataInicio
        if dataFim is not None:
            params['dataFim'] = dataFim
        if idOrgao is not None:
            params['idOrgao'] = idOrgao
            
        return self._get_paginated_data('/votacoes', params if params else None)
    
    def get_votacao(self, votacao_id: int) -> Dict[str, Any]:
        """
        Obtém dados de uma votação específica
        
        Args:
            votacao_id: ID da votação
            
        Returns:
            Dados da votação
        """
        return self._make_request(f'/votacoes/{votacao_id}')['dados']
    
    def get_votacao_votos(self, votacao_id: int) -> List[Dict[str, Any]]:
        """
        Obtém votos de uma votação
        
        Args:
            votacao_id: ID da votação
            
        Returns:
            Lista de votos
        """
        return self._make_request(f'/votacoes/{votacao_id}/votos')['dados']

    def get_votacao_orientacoes(self, votacao_id: int) -> List[Dict[str, Any]]:
        """
        Obtém orientações de uma votação
        
        Args:
            votacao_id: ID da votação
            
        Returns:
            Lista de orientações
        """
        return self._make_request(f'/votacoes/{votacao_id}/orientacoes')['dados']
    
    # ==================== PARTIDOS ====================
    
    def get_partidos(self,
                    id: Optional[int] = None,
                    sigla: Optional[str] = None,
                    nome: Optional[str] = None,
                    dataInicio: Optional[str] = None,
                    dataFim: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Obtém lista de partidos
        
        Args:
            id: ID do partido
            sigla: Sigla do partido
            nome: Nome do partido
            dataInicio: Data de início (formato YYYY-MM-DD)
            dataFim: Data de fim (formato YYYY-MM-DD)
            
        Returns:
            Lista de partidos
        """
        params = {}
        if id is not None:
            params['id'] = id
        if sigla is not None:
            params['sigla'] = sigla
        if nome is not None:
            params['nome'] = nome
        if dataInicio is not None:
            params['dataInicio'] = dataInicio
        if dataFim is not None:
            params['dataFim'] = dataFim
            
        return self._get_paginated_data('/partidos', params if params else None)
    
    def get_partido(self, partido_id: int) -> Dict[str, Any]:
        """
        Obtém dados de um partido específico
        
        Args:
            partido_id: ID do partido
            
        Returns:
            Dados do partido
        """
        return self._make_request(f'/partidos/{partido_id}')['dados']
    
    def get_partido_membros(self, partido_id: int,
                          id: Optional[int] = None,
                          nome: Optional[str] = None,
                          siglaUf: Optional[str] = None,
                          dataInicio: Optional[str] = None,
                          dataFim: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Obtém membros de um partido
        
        Args:
            partido_id: ID do partido
            id: ID do deputado
            nome: Nome do deputado
            siglaUf: Sigla da UF
            dataInicio: Data de início (formato YYYY-MM-DD)
            dataFim: Data de fim (formato YYYY-MM-DD)
            
        Returns:
            Lista de membros
        """
        params = {}
        if id is not None:
            params['id'] = id
        if nome is not None:
            params['nome'] = nome
        if siglaUf is not None:
            params['siglaUf'] = siglaUf
        if dataInicio is not None:
            params['dataInicio'] = dataInicio
        if dataFim is not None:
            params['dataFim'] = dataFim
            
        return self._get_paginated_data(f'/partidos/{partido_id}/membros', params if params else None)

    def get_partido_lideres(self, partido_id: int) -> List[Dict[str, Any]]:
        """
        Obtém líderes de um partido
        
        Args:
            partido_id: ID do partido
            
        Returns:
            Lista de líderes
        """
        return self._get_paginated_data(f'/partidos/{partido_id}/lideres')
    
    # ==================== ÓRGÃOS ====================
    
    def get_orgaos(self,
                  id: Optional[int] = None,
                  sigla: Optional[str] = None,
                  nome: Optional[str] = None,
                  dataInicio: Optional[str] = None,
                  dataFim: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Obtém lista de órgãos
        
        Args:
            id: ID do órgão
            sigla: Sigla do órgão
            nome: Nome do órgão
            dataInicio: Data de início (formato YYYY-MM-DD)
            dataFim: Data de fim (formato YYYY-MM-DD)
            
        Returns:
            Lista de órgãos
        """
        params = {}
        if id is not None:
            params['id'] = id
        if sigla is not None:
            params['sigla'] = sigla
        if nome is not None:
            params['nome'] = nome
        if dataInicio is not None:
            params['dataInicio'] = dataInicio
        if dataFim is not None:
            params['dataFim'] = dataFim
            
        return self._get_paginated_data('/orgaos', params if params else None)
    
    def get_orgao(self, orgao_id: int) -> Dict[str, Any]:
        """
        Obtém dados de um órgão específico
        
        Args:
            orgao_id: ID do órgão
            
        Returns:
            Dados do órgão
        """
        return self._make_request(f'/orgaos/{orgao_id}')['dados']
    
    def get_orgao_membros(self, orgao_id: int,
                        id: Optional[int] = None,
                        nome: Optional[str] = None,
                        siglaUf: Optional[str] = None,
                        siglaPartido: Optional[str] = None,
                        dataInicio: Optional[str] = None,
                        dataFim: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Obtém membros de um órgão
        
        Args:
            orgao_id: ID do órgão
            id: ID do deputado
            nome: Nome do deputado
            siglaUf: Sigla da UF
            siglaPartido: Sigla do partido
            dataInicio: Data de início (formato YYYY-MM-DD)
            dataFim: Data de fim (formato YYYY-MM-DD)
            
        Returns:
            Lista de membros
        """
        params = {}
        if id is not None:
            params['id'] = id
        if nome is not None:
            params['nome'] = nome
        if siglaUf is not None:
            params['siglaUf'] = siglaUf
        if siglaPartido is not None:
            params['siglaPartido'] = siglaPartido
        if dataInicio is not None:
            params['dataInicio'] = dataInicio
        if dataFim is not None:
            params['dataFim'] = dataFim
            
        return self._get_paginated_data(f'/orgaos/{orgao_id}/membros', params if params else None)

    def get_orgao_eventos(self, orgao_id: int,
                         id: Optional[int] = None,
                         dataInicio: Optional[str] = None,
                         dataFim: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Obtém eventos de um órgão
        
        Args:
            orgao_id: ID do órgão
            id: ID do evento
            dataInicio: Data de início (formato YYYY-MM-DD)
            dataFim: Data de fim (formato YYYY-MM-DD)
            
        Returns:
            Lista de eventos
        """
        params = {}
        if id is not None:
            params['id'] = id
        if dataInicio is not None:
            params['dataInicio'] = dataInicio
        if dataFim is not None:
            params['dataFim'] = dataFim
            
        return self._get_paginated_data(f'/orgaos/{orgao_id}/eventos', params if params else None)

    def get_orgao_votacoes(self, orgao_id: int) -> List[Dict[str, Any]]:
        """
        Obtém votações de um órgão
        
        Args:
            orgao_id: ID do órgão
            
        Returns:
            Lista de votações
        """
        return self._get_paginated_data(f'/orgaos/{orgao_id}/votacoes')
    
    # ==================== EVENTOS ====================
    
    def get_eventos(self,
                   id: Optional[int] = None,
                   dataInicio: Optional[str] = None,
                   dataFim: Optional[str] = None,
                   idOrgao: Optional[int] = None,
                   idTipoEvento: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Obtém lista de eventos
        
        Args:
            id: ID do evento
            dataInicio: Data de início (formato YYYY-MM-DD)
            dataFim: Data de fim (formato YYYY-MM-DD)
            idOrgao: ID do órgão
            idTipoEvento: ID do tipo de evento
            
        Returns:
            Lista de eventos
        """
        params = {}
        if id is not None:
            params['id'] = id
        if dataInicio is not None:
            params['dataInicio'] = dataInicio
        if dataFim is not None:
            params['dataFim'] = dataFim
        if idOrgao is not None:
            params['idOrgao'] = idOrgao
        if idTipoEvento is not None:
            params['idTipoEvento'] = idTipoEvento
            
        return self._get_paginated_data('/eventos', params if params else None)
    
    def get_evento(self, evento_id: int) -> Dict[str, Any]:
        """
        Obtém dados de um evento específico
        
        Args:
            evento_id: ID do evento
            
        Returns:
            Dados do evento
        """
        return self._make_request(f'/eventos/{evento_id}')['dados']
    
    def get_evento_deputados(self, evento_id: int) -> List[Dict[str, Any]]:
        """
        Obtém deputados de um evento
        
        Args:
            evento_id: ID do evento
            
        Returns:
            Lista de deputados
        """
        return self._get_paginated_data(f'/eventos/{evento_id}/deputados')

    def get_evento_orgaos(self, evento_id: int) -> List[Dict[str, Any]]:
        """
        Obtém órgãos de um evento
        
        Args:
            evento_id: ID do evento
            
        Returns:
            Lista de órgãos
        """
        return self._get_paginated_data(f'/eventos/{evento_id}/orgaos')

    def get_evento_pauta(self, evento_id: int) -> List[Dict[str, Any]]:
        """
        Obtém pauta de um evento
        
        Args:
            evento_id: ID do evento
            
        Returns:
            Lista de itens da pauta
        """
        return self._get_paginated_data(f'/eventos/{evento_id}/pauta')

    def get_evento_votacoes(self, evento_id: int) -> List[Dict[str, Any]]:
        """
        Obtém votações de um evento
        
        Args:
            evento_id: ID do evento
            
        Returns:
            Lista de votações
        """
        return self._get_paginated_data(f'/eventos/{evento_id}/votacoes')
    
    # ==================== FRENTES PARLAMENTARES ====================
    
    def get_frentes(self,
                   id: Optional[int] = None,
                   titulo: Optional[str] = None,
                   dataInicio: Optional[str] = None,
                   dataFim: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Obtém lista de frentes parlamentares
        
        Args:
            id: ID da frente
            titulo: Título da frente
            dataInicio: Data de início (formato YYYY-MM-DD)
            dataFim: Data de fim (formato YYYY-MM-DD)
            
        Returns:
            Lista de frentes parlamentares
        """
        params = {}
        if id is not None:
            params['id'] = id
        if titulo is not None:
            params['titulo'] = titulo
        if dataInicio is not None:
            params['dataInicio'] = dataInicio
        if dataFim is not None:
            params['dataFim'] = dataFim
            
        return self._get_paginated_data('/frentes', params if params else None)

    def get_frente(self, frente_id: int) -> Dict[str, Any]:
        """
        Obtém dados de uma frente parlamentar específica
        
        Args:
            frente_id: ID da frente
            
        Returns:
            Dados da frente parlamentar
        """
        return self._make_request(f'/frentes/{frente_id}')['dados']

    def get_frente_membros(self, frente_id: int,
                          id: Optional[int] = None,
                          nome: Optional[str] = None,
                          siglaUf: Optional[str] = None,
                          siglaPartido: Optional[str] = None,
                          dataInicio: Optional[str] = None,
                          dataFim: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Obtém membros de uma frente parlamentar
        
        Args:
            frente_id: ID da frente
            id: ID do deputado
            nome: Nome do deputado
            siglaUf: Sigla da UF
            siglaPartido: Sigla do partido
            dataInicio: Data de início (formato YYYY-MM-DD)
            dataFim: Data de fim (formato YYYY-MM-DD)
            
        Returns:
            Lista de membros
        """
        params = {}
        if id is not None:
            params['id'] = id
        if nome is not None:
            params['nome'] = nome
        if siglaUf is not None:
            params['siglaUf'] = siglaUf
        if siglaPartido is not None:
            params['siglaPartido'] = siglaPartido
        if dataInicio is not None:
            params['dataInicio'] = dataInicio
        if dataFim is not None:
            params['dataFim'] = dataFim
            
        return self._get_paginated_data(f'/frentes/{frente_id}/membros', params if params else None)
    
    # ==================== GRUPOS INTERPARLAMENTARES ====================
    
    def get_grupos(self,
                  id: Optional[int] = None,
                  titulo: Optional[str] = None,
                  dataInicio: Optional[str] = None,
                  dataFim: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Obtém lista de grupos interparlamentares
        
        Args:
            id: ID do grupo
            titulo: Título do grupo
            dataInicio: Data de início (formato YYYY-MM-DD)
            dataFim: Data de fim (formato YYYY-MM-DD)
            
        Returns:
            Lista de grupos interparlamentares
        """
        params = {}
        if id is not None:
            params['id'] = id
        if titulo is not None:
            params['titulo'] = titulo
        if dataInicio is not None:
            params['dataInicio'] = dataInicio
        if dataFim is not None:
            params['dataFim'] = dataFim
            
        return self._get_paginated_data('/grupos', params if params else None)

    def get_grupo(self, grupo_id: int) -> Dict[str, Any]:
        """
        Obtém dados de um grupo interparlamentar específico
        
        Args:
            grupo_id: ID do grupo
            
        Returns:
            Dados do grupo interparlamentar
        """
        return self._make_request(f'/grupos/{grupo_id}')['dados']

    def get_grupo_membros(self, grupo_id: int,
                         id: Optional[int] = None,
                         nome: Optional[str] = None,
                         siglaUf: Optional[str] = None,
                         siglaPartido: Optional[str] = None,
                         dataInicio: Optional[str] = None,
                         dataFim: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Obtém membros de um grupo interparlamentar
        
        Args:
            grupo_id: ID do grupo
            id: ID do deputado
            nome: Nome do deputado
            siglaUf: Sigla da UF
            siglaPartido: Sigla do partido
            dataInicio: Data de início (formato YYYY-MM-DD)
            dataFim: Data de fim (formato YYYY-MM-DD)
            
        Returns:
            Lista de membros
        """
        params = {}
        if id is not None:
            params['id'] = id
        if nome is not None:
            params['nome'] = nome
        if siglaUf is not None:
            params['siglaUf'] = siglaUf
        if siglaPartido is not None:
            params['siglaPartido'] = siglaPartido
        if dataInicio is not None:
            params['dataInicio'] = dataInicio
        if dataFim is not None:
            params['dataFim'] = dataFim
            
        return self._get_paginated_data(f'/grupos/{grupo_id}/membros', params if params else None)

    def get_grupo_historico(self, grupo_id: int) -> List[Dict[str, Any]]:
        """
        Obtém histórico de um grupo interparlamentar
        
        Args:
            grupo_id: ID do grupo
            
        Returns:
            Lista de variações de estado do grupo
        """
        return self._get_paginated_data(f'/grupos/{grupo_id}/historico')
    
    # ==================== LEGISLATURAS ====================
    
    def get_legislaturas(self) -> List[Dict[str, Any]]:
        """
        Obtém lista de legislaturas
        
        Returns:
            Lista de legislaturas
        """
        return self._get_paginated_data('/legislaturas')

    def get_legislatura(self, legislatura_id: int) -> Dict[str, Any]:
        """
        Obtém dados de uma legislatura específica
        
        Args:
            legislatura_id: ID da legislatura
            
        Returns:
            Dados da legislatura
        """
        return self._make_request(f'/legislaturas/{legislatura_id}')['dados']

    def get_legislatura_lideres(self, legislatura_id: int) -> List[Dict[str, Any]]:
        """
        Obtém líderes de uma legislatura
        
        Args:
            legislatura_id: ID da legislatura
            
        Returns:
            Lista de líderes
        """
        return self._get_paginated_data(f'/legislaturas/{legislatura_id}/lideres')

    def get_legislatura_mesa(self, legislatura_id: int) -> List[Dict[str, Any]]:
        """
        Obtém mesa diretora de uma legislatura
        
        Args:
            legislatura_id: ID da legislatura
            
        Returns:
            Lista de membros da mesa diretora
        """
        return self._make_request(f'/legislaturas/{legislatura_id}/mesa', {})['dados']
    
    # ==================== BLOCOS PARTIDÁRIOS ====================
    
    def get_blocos(self) -> List[Dict[str, Any]]:
        """
        Obtém lista de blocos partidários
        
        Returns:
            Lista de blocos partidários
        """
        return self._get_paginated_data('/blocos')

    def get_bloco(self, bloco_id: int) -> Dict[str, Any]:
        """
        Obtém dados de um bloco partidário específico
        
        Args:
            bloco_id: ID do bloco
            
        Returns:
            Dados do bloco partidário
        """
        return self._make_request(f'/blocos/{bloco_id}')['dados']

    def get_bloco_partidos(self, bloco_id: int) -> List[Dict[str, Any]]:
        """
        Obtém partidos de um bloco
        
        Args:
            bloco_id: ID do bloco
            
        Returns:
            Lista de partidos do bloco
        """
        return self._get_paginated_data(f'/blocos/{bloco_id}/partidos')
    
    # ==================== REFERÊNCIAS ====================
    
    def get_referencias(self, tipo: str) -> List[Dict[str, Any]]:
        """
        Obtém dados de referência
        
        Args:
            tipo: Tipo de referência (ex: 'tiposProposicao', 'tiposVotacao', etc.)
            
        Returns:
            Lista de dados de referência
        """
        return self._get_paginated_data(f'/referencias/{tipo}')
    
    def get_tipos_proposicao(self) -> List[Dict[str, Any]]:
        """Obtém tipos de proposição"""
        return self.get_referencias('tiposProposicao')
    
    def get_tipos_votacao(self) -> List[Dict[str, Any]]:
        """Obtém tipos de votação"""
        return self.get_referencias('tiposVotacao')
    
    def get_situacoes_proposicao(self) -> List[Dict[str, Any]]:
        """Obtém situações de proposição"""
        return self.get_referencias('situacoesProposicao')
    
    def get_temas_proposicao(self) -> List[Dict[str, Any]]:
        """Obtém temas de proposição"""
        return self.get_referencias('proposicoes/codTema')

    def get_referencias_deputados(self) -> List[Dict[str, Any]]:
        """Obtém referências de deputados"""
        return self.get_referencias('deputados')

    def get_referencias_proposicoes(self) -> List[Dict[str, Any]]:
        """Obtém referências de proposições"""
        return self.get_referencias('proposicoes')

    def get_referencias_eventos(self) -> List[Dict[str, Any]]:
        """Obtém referências de eventos"""
        return self.get_referencias('eventos')

    def get_referencias_votacoes(self) -> List[Dict[str, Any]]:
        """Obtém referências de votações"""
        return self.get_referencias('votacoes')

    def get_referencias_partidos(self) -> List[Dict[str, Any]]:
        """Obtém referências de partidos"""
        return self.get_referencias('partidos')

    def get_referencias_orgaos(self) -> List[Dict[str, Any]]:
        """Obtém referências de órgãos"""
        return self.get_referencias('orgaos')

    def get_referencias_frentes(self) -> List[Dict[str, Any]]:
        """Obtém referências de frentes parlamentares"""
        return self.get_referencias('frentes')

    def get_referencias_grupos(self) -> List[Dict[str, Any]]:
        """Obtém referências de grupos interparlamentares"""
        return self.get_referencias('grupos')

    # Referências específicas de deputados
    def get_referencias_deputados_cod_situacao(self) -> List[Dict[str, Any]]:
        """Obtém códigos de situação de exercício parlamentar"""
        return self.get_referencias('deputados/codSituacao')

    def get_referencias_deputados_cod_tipo_profissao(self) -> List[Dict[str, Any]]:
        """Obtém códigos de atividades profissionais"""
        return self.get_referencias('deputados/codTipoProfissao')

    def get_referencias_deputados_sigla_uf(self) -> List[Dict[str, Any]]:
        """Obtém siglas e nomes dos estados e DF"""
        return self.get_referencias('deputados/siglaUF')

    def get_referencias_deputados_tipo_despesa(self) -> List[Dict[str, Any]]:
        """Obtém tipos de despesas da Cota Parlamentar"""
        return self.get_referencias('deputados/tipoDespesa')

    def get_referencias_situacoes_deputado(self) -> List[Dict[str, Any]]:
        """Obtém situações de exercício parlamentar"""
        return self.get_referencias('situacoesDeputado')

    # Referências específicas de proposições
    def get_referencias_proposicoes_cod_situacao(self) -> List[Dict[str, Any]]:
        """Obtém códigos de situação de tramitação"""
        return self.get_referencias('proposicoes/codSituacao')

    def get_referencias_proposicoes_cod_tema(self) -> List[Dict[str, Any]]:
        """Obtém códigos de temas"""
        return self.get_referencias('proposicoes/codTema')

    def get_referencias_proposicoes_cod_tipo_autor(self) -> List[Dict[str, Any]]:
        """Obtém códigos de tipos de autor"""
        return self.get_referencias('proposicoes/codTipoAutor')

    def get_referencias_proposicoes_cod_tipo_tramitacao(self) -> List[Dict[str, Any]]:
        """Obtém códigos de tipos de tramitação"""
        return self.get_referencias('proposicoes/codTipoTramitacao')

    def get_referencias_proposicoes_sigla_tipo(self) -> List[Dict[str, Any]]:
        """Obtém siglas de tipos de proposições"""
        return self.get_referencias('proposicoes/siglaTipo')

    def get_referencias_situacoes_proposicao(self) -> List[Dict[str, Any]]:
        """Obtém situações de tramitação"""
        return self.get_referencias('situacoesProposicao')

    def get_referencias_tipos_autor(self) -> List[Dict[str, Any]]:
        """Obtém tipos de autores"""
        return self.get_referencias('tiposAutor')

    def get_referencias_tipos_tramitacao(self) -> List[Dict[str, Any]]:
        """Obtém tipos de tramitação"""
        return self.get_referencias('tiposTramitacao')

    # Referências específicas de órgãos
    def get_referencias_orgaos_cod_situacao(self) -> List[Dict[str, Any]]:
        """Obtém códigos de situação de órgãos"""
        return self.get_referencias('orgaos/codSituacao')

    def get_referencias_orgaos_cod_tipo_orgao(self) -> List[Dict[str, Any]]:
        """Obtém códigos de tipos de órgãos"""
        return self.get_referencias('orgaos/codTipoOrgao')

    def get_referencias_situacoes_orgao(self) -> List[Dict[str, Any]]:
        """Obtém situações de órgãos"""
        return self.get_referencias('situacoesOrgao')

    def get_referencias_tipos_orgao(self) -> List[Dict[str, Any]]:
        """Obtém tipos de órgãos"""
        return self.get_referencias('tiposOrgao')

    # Referências específicas de eventos
    def get_referencias_eventos_cod_situacao_evento(self) -> List[Dict[str, Any]]:
        """Obtém códigos de situação de eventos"""
        return self.get_referencias('eventos/codSituacaoEvento')

    def get_referencias_eventos_cod_tipo_evento(self) -> List[Dict[str, Any]]:
        """Obtém códigos de tipos de eventos"""
        return self.get_referencias('eventos/codTipoEvento')

    def get_referencias_situacoes_evento(self) -> List[Dict[str, Any]]:
        """Obtém situações de eventos"""
        return self.get_referencias('situacoesEvento')

    def get_referencias_tipos_evento(self) -> List[Dict[str, Any]]:
        """Obtém tipos de eventos"""
        return self.get_referencias('tiposEvento')

    # Referências gerais
    def get_referencias_uf(self) -> List[Dict[str, Any]]:
        """Obtém siglas e nomes dos estados e DF"""
        return self.get_referencias('uf')
    
    def close(self):
        """Fecha a sessão HTTP"""
        self.session.close()
    
    def __enter__(self):
        """Context manager entry"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()
