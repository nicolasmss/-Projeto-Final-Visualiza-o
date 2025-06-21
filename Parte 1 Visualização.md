# Introdução
Este relatório concentra-se exclusivamente na investigação da Questão de Pesquisa 2: **Quais variáveis demográficas e clínicas estão associadas a maiores atrasos na criação da Fístula Arteriovenosa (FAV) em pacientes submetidos à diálise crônica em Porto Alegre?**
# Objetivo Específico

Caracterizar as associações entre variáveis demográficas (idade, sexo, escolaridade) e clínicas (comorbidades, urgência inicial do procedimento, modalidade de acesso pré‑FAV) com o tempo decorrido até a criação da FAV em pacientes que iniciaram hemodiálise crônica.
**Perspectivas de resultados e aplicações**

Espera-se identificar perfis de pacientes com maior vulnerabilidade a atrasos na confecção de FAV. Esses insights poderão subsidiar:
- Diretrizes de encaminhamento precoce para avaliação vascular.
- Protocolos de triagem diferenciada em populações de risco.
- Alocação de recursos para capacitação de equipes cirúrgicas em unidades com maior demanda.
# Contextualização e relevância

A Doença Renal Crônica (DRC) impõe elevada carga ao sistema de saúde devido ao crescente número de pacientes que necessitam de terapia de substituição renal. A FAV, considerando o seu papel central na hemodiálise — proporcionando acesso vascular durável e de baixo risco de complicações —, deve ser confeccionada em tempo oportuno. A ocorrência de atrasos na sua criação pode:
- Aumentar a dependência de cateteres centrais, elevando risco de infecção e trombose.
- Gerar custos adicionais hospitalares e ambulatoriais.
- Comprometer a qualidade de vida e prognóstico de longo prazo dos pacientes.

Em Porto Alegre, onde se concentram diversos centros de tratamento renal, entender os determinantes do atraso permite otimizar processos clínicos e administrativas, direcionar recursos e aprimorar protocolos de encaminhamento pré‑cirúrgico.

**Definições conceituais**
- **Tempo de Espera para FAV**: intervalo, em dias, entre a primeira sessão de hemodiálise registrada e a data de confecção cirúrgica da FAV.
- **Variáveis demográficas**:
    - _Idade:_ anos completos no momento do início da diálise.
    - _Sexo:_ masculino ou feminino.
    - _Escolaridade:_ categorizada em fundamental, médio ou superior.
- **Variáveis clínicas**:
    - _Comorbidades:_ presença de diabetes mellitus, hipertensão arterial sistêmica ou doença cardiovascular.
    - _Urgência inicial:_ se a primeira diálise foi realizada em caráter eletivo ou de urgência.
    - _Modalidade de acesso pré‑FAV:_ uso de cateter venoso central versus acesso temporário.

# Coleta dos dados
< Nicolas preenche aqui >
# Entendimento dos dados através de uma análise exploratória visual
**Fontes de dados**
- Base SIH‑RD do DATASUS (2008–2024) filtrada para internações e procedimentos de hemodiálise em Porto Alegre.
- Dicionário de dados do DATASUS (GitHub).
**Análise estatística**
- Estatística descritiva: distribuição de idade, proporções por sexo e plano de saúde.
- Testes bivariados (χ² para categóricas, ANOVA ou Kruskal–Wallis para contínuas) para verificar diferenças no tempo de espera.
- Regressão multivariada (Cox ou modelo de riscos proporcionais) para estimar razão de risco de atraso em função das variáveis demográficas e clínicas.]
# Preparação e pré-processamento de dados, que pode também incluir o enriquecimento dos dados se necessário
**Pré‑processamento**
- Remoção de registros duplicados e inconsistentes.
- Exclusão de casos com valores ausentes em variáveis-chave (> 30%).
- Remoção de atributos com valores constantes

# Estudo do ambiente de desenvolvimento e projeto das representações visuais que serão implementadas
