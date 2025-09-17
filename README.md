# Praça Pública - Cliente Python para API da Câmara dos Deputados

O **Praça Pública** é uma plataforma de dados abertos dedicada a organizar, analisar e tornar acessíveis as informações sobre políticos brasileiros — incluindo votações, proposições legislativas e posicionamentos públicos. O projeto utiliza inteligência artificial para classificar essas informações em um espaço vetorial de ideias políticas, permitindo que cidadãos visualizem alinhamentos ideológicos, comparem representantes e entendam melhor como as decisões são tomadas.

Este repositório contém um cliente Python completo para a API de Dados Abertos da Câmara dos Deputados, implementando **todos os endpoints disponíveis** da API oficial.

## 🚀 Funcionalidades

### ✅ Endpoints Implementados (100% Completo)

#### **Deputados**
- `get_deputados()` - Lista e busca de deputados
- `get_deputado(id)` - Informações detalhadas de um deputado
- `get_deputado_despesas(id, ano)` - Despesas parlamentares
- `get_deputado_discursos(id)` - Discursos do deputado
- `get_deputado_eventos(id)` - Eventos com participação do deputado
- `get_deputado_frentes(id)` - Frentes parlamentares do deputado
- `get_deputado_historico(id)` - Histórico de mudanças parlamentares
- `get_deputado_mandatos_externos(id)` - Outros cargos eletivos
- `get_deputado_ocupacoes(id)` - Empregos e atividades anteriores
- `get_deputado_orgaos(id)` - Órgãos dos quais é integrante
- `get_deputado_profissoes(id)` - Profissões declaradas
- `get_deputado_proposicoes(id)` - Proposições do deputado
- `get_deputado_votacoes(id)` - Votações do deputado

#### **Proposições Legislativas**
- `get_proposicoes()` - Lista configurável de proposições
- `get_proposicao(id)` - Informações detalhadas de uma proposição
- `get_proposicao_autores(id)` - Autores da proposição
- `get_proposicao_tramitacoes(id)` - Histórico de tramitação
- `get_proposicao_votacoes(id)` - Votações da proposição
- `get_proposicao_temas(id)` - Temas da proposição
- `get_proposicao_relacionadas(id)` - Proposições relacionadas

#### **Votações**
- `get_votacoes()` - Lista de votações da Câmara
- `get_votacao(id)` - Informações detalhadas de uma votação
- `get_votacao_votos(id)` - Votos individuais dos parlamentares
- `get_votacao_orientacoes(id)` - Orientações das lideranças

#### **Partidos Políticos**
- `get_partidos()` - Lista de partidos
- `get_partido(id)` - Informações de um partido
- `get_partido_membros(id)` - Membros do partido
- `get_partido_lideres(id)` - Líderes do partido

#### **Órgãos Legislativos**
- `get_orgaos()` - Lista de comissões e órgãos
- `get_orgao(id)` - Informações de um órgão
- `get_orgao_membros(id)` - Membros do órgão
- `get_orgao_eventos(id)` - Eventos do órgão
- `get_orgao_votacoes(id)` - Votações do órgão

#### **Eventos**
- `get_eventos()` - Lista de eventos da Câmara
- `get_evento(id)` - Informações de um evento
- `get_evento_deputados(id)` - Deputados participantes
- `get_evento_orgaos(id)` - Órgãos organizadores
- `get_evento_pauta(id)` - Pauta do evento
- `get_evento_votacoes(id)` - Votações do evento

#### **Frentes Parlamentares**
- `get_frentes()` - Lista de frentes parlamentares
- `get_frente(id)` - Informações de uma frente
- `get_frente_membros(id)` - Membros da frente

#### **Grupos Interparlamentares**
- `get_grupos()` - Lista de grupos interparlamentares
- `get_grupo(id)` - Informações de um grupo
- `get_grupo_membros(id)` - Membros do grupo
- `get_grupo_historico(id)` - Histórico do grupo

#### **Legislaturas**
- `get_legislaturas()` - Lista de legislaturas
- `get_legislatura(id)` - Informações de uma legislatura
- `get_legislatura_lideres(id)` - Líderes da legislatura
- `get_legislatura_mesa(id)` - Mesa diretora da legislatura

#### **Blocos Partidários**
- `get_blocos()` - Lista de blocos partidários
- `get_bloco(id)` - Informações de um bloco
- `get_bloco_partidos(id)` - Partidos do bloco

#### **Referências e Dados Auxiliares**
- `get_referencias_*()` - Mais de 20 endpoints de referências
- `get_tipos_proposicao()` - Tipos de proposições
- `get_tipos_votacao()` - Tipos de votações
- `get_situacoes_proposicao()` - Situações de tramitação
- `get_temas_proposicao()` - Temas disponíveis
- E muitos outros...

## 🛠️ Instalação e Configuração

### Pré-requisitos
- Python 3.8 ou superior
- pip (gerenciador de pacotes Python)

### 1. Configuração do Ambiente Virtual

```bash
# Criar ambiente virtual
python -m venv venv

# Ativar ambiente virtual
# No Windows:
venv\Scripts\activate
# No Linux/Mac:
source venv/bin/activate
```

### 2. Instalação para Desenvolvimento

```bash
# Instalar dependências
pip install -r requirements.txt

# Instalar o projeto em modo desenvolvimento
pip install -e .
```

### 3. Verificação da Instalação

```bash
# Testar importação
python -c "from src.clients.camara_client import CamaraClient; print('✅ Cliente instalado com sucesso!')"
```

## 📖 Uso Básico

```python
from src.clients.camara_client import CamaraClient

# Criar instância do cliente
client = CamaraClient()

# Buscar todos os deputados
deputados = client.get_deputados()
print(f"Total de deputados: {len(deputados)}")

# Buscar deputados de uma legislatura específica
deputados_56 = client.get_deputados(idLegislatura=56)

# Buscar informações de um deputado específico
deputado = client.get_deputado(204379)
print(f"Nome: {deputado['nomeCivil']}")

# Buscar proposições de um deputado
proposicoes = client.get_deputado_proposicoes(204379)

# Buscar votações recentes
votacoes = client.get_votacoes(dataInicio='2025-01-01', dataFim='2025-03-31')

# Fechar conexão
client.close()
```

## 🧪 Testes e Validação

### Notebook de Testes
O projeto inclui um notebook Jupyter (`notebooks/test_camara_api.ipynb`) com exemplos práticos de uso de todos os endpoints implementados, incluindo:

- ✅ Busca de deputados e filtros por legislatura
- ✅ Análise de despesas parlamentares
- ✅ Consulta de discursos e eventos
- ✅ Exploração de frentes parlamentares e ocupações
- ✅ Análise de proposições e tramitações
- ✅ Consulta de votações e orientações
- ✅ Exploração de órgãos e lideranças

### Executar Testes
```bash
# Ativar ambiente virtual
venv\Scripts\activate

# Executar notebook
jupyter notebook notebooks/test_camara_api.ipynb
```

## 🔧 Configuração Avançada

### Personalizar Configurações
```python
from src.clients.camara_client import CamaraClient, CamaraConfig

# Configuração personalizada
config = CamaraConfig(
    timeout=60,  # Timeout em segundos
    max_retries=5,  # Número máximo de tentativas
    user_agent="MeuApp/1.0"  # User-Agent personalizado
)

client = CamaraClient(config)
```

### Uso com Context Manager
```python
with CamaraClient() as client:
    deputados = client.get_deputados()
    # Conexão é fechada automaticamente
```

## 📊 Exemplos de Análise de Dados

### Análise de Votações por Partido
```python
# Buscar votações recentes
votacoes = client.get_votacoes(dataInicio='2025-01-01', dataFim='2025-03-31')

# Para cada votação, analisar votos por partido
for votacao in votacoes[:5]:  # Primeiras 5 votações
    votos = client.get_votacao_votos(votacao['id'])
    orientacoes = client.get_votacao_orientacoes(votacao['id'])
    print(f"Votação: {votacao['descricao']}")
    print(f"Total de votos: {len(votos)}")
```

### Análise de Proposições por Tema
```python
# Buscar proposições de 2025
proposicoes = client.get_proposicoes(ano=2025)

# Analisar temas das proposições
for proposicao in proposicoes[:10]:
    temas = client.get_proposicao_temas(proposicao['id'])
    print(f"Proposição {proposicao['siglaTipo']} {proposicao['numero']}/{proposicao['ano']}")
    print(f"Temas: {[tema['tema'] for tema in temas]}")
```

## 🏗️ Estrutura do Projeto

```
pracapublica/
├── src/
│   └── clients/
│       └── camara_client.py    # Cliente principal da API
├── notebooks/
│   └── test_camara_api.ipynb   # Notebook de testes e exemplos
├── requirements.txt             # Dependências Python
├── pyproject.toml              # Configuração do projeto
└── README.md                   # Este arquivo
```

## 📋 Dependências

- `requests>=2.31.0` - Cliente HTTP
- `httpx>=0.24.0` - Cliente HTTP assíncrono
- `pydantic>=2.0.0` - Validação de dados
- `python-dotenv>=1.0.0` - Gerenciamento de variáveis de ambiente
- `pandas>=2.0.0` - Manipulação de dados (opcional)

## 🤝 Contribuição

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.

## 🔗 Links Úteis

- [API de Dados Abertos da Câmara](https://dadosabertos.camara.leg.br/swagger/api.html)
- [Documentação da API](https://dadosabertos.camara.leg.br/api/v2)
- [Portal de Dados Abertos](https://dadosabertos.camara.leg.br/)

## 📞 Suporte

Para dúvidas, sugestões ou problemas, abra uma [issue](https://github.com/seu-usuario/pracapublica/issues) no repositório.

---

**Praça Pública** - Democratizando o acesso à informação política brasileira através de dados abertos e inteligência artificial.
