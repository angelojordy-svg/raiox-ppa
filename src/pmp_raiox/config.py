"""Caminhos, mapas de referencia e constantes do raio-x."""

from __future__ import annotations

import os
from pathlib import Path

RAIZ_PROJETO = Path(__file__).resolve().parents[2]
RAIZ_WORKSPACE = RAIZ_PROJETO.parents[1]
DADOS = Path(os.environ.get("PMP_DATA_ROOT", RAIZ_WORKSPACE / "_dados"))
SAIDA = DADOS / "Saida" / "raiox"
ENTRADA = SAIDA / "entrada"
PPA_PADRAO = DADOS / "Saida" / "ppa_2026_2029.xlsx"

UG_NOMES = {
    "001": "Prefeitura Municipal de Parauapebas",
    "002": "Câmara Municipal de Parauapebas",
    "003": "Fundo Municipal de Saúde",
    "004": "Fundo Municipal de Educação",
    "005": "Fundo Municipal de Assistência Social",
    "006": "Fundo Municipal de Meio Ambiente",
    "007": "Fundo Municipal dos Direitos da Criança e Adolescente",
    "008": "Fundo Municipal de Habitação de Interesse Social",
    "009": "Fundo Municipal de Cultura",
    "010": "SAAEP — Serviço Autônomo de Água e Esgoto",
    "011": "Fundo Municipal dos Direitos da Mulher",
    "012": "Fundo Municipal da Pessoa com Deficiência",
    "013": "Fundo Municipal de Integração e Protagonismo Juvenil",
    "016": "Fundo de Manutenção e Desenvolvimento da Educação Básica — FUNDEB",
    "017": "Fundo Municipal de Desenvolvimento do Turismo",
    "019": "Fundo Municipal da Pessoa Idosa",
    "020": "Secretaria Municipal de Cultura",
    "021": "Secretaria Municipal de Desenvolvimento",
    "022": "Secretaria Municipal de Esportes e Lazer",
    "023": "Secretaria Municipal de Administração",
    "024": "Secretaria Municipal de Serviços Urbanos",
    "025": "Secretaria Municipal de Meio Ambiente e Sustentabilidade",
    "026": "Secretaria Municipal de Obras",
    "027": "Secretaria Municipal de Produção Rural",
    "029": "Secretaria Municipal de Habitação e Interesse Social",
    "030": "Secretaria Municipal de Mineração, Energia, Ciência e Tecnologia",
    "031": "Secretaria Municipal de Segurança Institucional e Defesa do Cidadão",
    "032": "Secretaria Especial de Governo",
    "033": "PROSAP — Programa Municipal de Saneamento Ambiental",
    "034": "Fundo Municipal de Regularização Fundiária",
    "035": "Fundo Especial de Custeio de Iluminação Pública",
    "036": "Secretaria Municipal da Juventude",
    "037": "Secretaria Municipal de Turismo",
    "041": "Fundo Municipal de Defesa do Consumidor",
    "042": "Fundo Municipal de Segurança Alimentar e Nutricional",
}

UG_SLUGS = {
    "001": "prefeitura",
    "002": "camara",
    "003": "saude",
    "004": "educacao",
    "005": "assistencia_social",
    "006": "meio_ambiente_fundo",
    "007": "crianca_adolescente",
    "008": "habitacao_fundo",
    "009": "cultura_fundo",
    "010": "saaep",
    "011": "mulher",
    "012": "pessoa_deficiencia",
    "013": "juventude_fundo",
    "016": "fundeb",
    "017": "turismo_fundo",
    "019": "pessoa_idosa",
    "020": "cultura",
    "021": "desenvolvimento",
    "022": "esportes",
    "023": "administracao",
    "024": "servicos_urbanos",
    "025": "meio_ambiente",
    "026": "obras",
    "027": "producao_rural",
    "029": "habitacao",
    "030": "mineracao",
    "031": "seguranca",
    "032": "governo",
    "033": "prosap",
    "034": "regularizacao_fundiaria",
    "035": "iluminacao",
    "036": "juventude",
    "037": "turismo",
    "041": "defesa_consumidor",
    "042": "seguranca_alimentar",
}

UO_NOMES_OFICIAIS = {
    ("001", "CENTRAL DE LICITACOES E CONTRATOS"): "Central de Licitações e Contratos",
    ("001", "GABINETE DO PREFEITO"): "Gabinete do Prefeito",
    ("001", "PROCURADORIA GERAL DO MUNICIPIO"): "Procuradoria Geral do Município",
    ("001", "SECRETARIA MUNICIPAL DE FAZENDA"): "Secretaria Municipal de Fazenda",
    ("001", "VICE GABINETE DO EXECUTIVO"): "Vice-Gabinete do Executivo",
    ("001", "CONTROLADORIA GERAL DO MUNICIPIO"): "Controladoria Geral do Município",
    ("003", "FUNDO MUNICIPAL DE SAUDE"): "Fundo Municipal de Saúde",
    ("003", "SECRETARIA MUNICIPAL DE SAUDE"): "Secretaria Municipal de Saúde",
    ("004", "FUNDO MUNICIPAL DE EDUCACAO"): "Fundo Municipal de Educação",
    ("004", "SECRETARIA MUNICIPAL DE EDUCACAO"): "Secretaria Municipal de Educação",
    ("005", "FUNDO MUNICIPAL DE ASSISTENCIA SOCIAL"): "Fundo Municipal de Assistência Social",
    ("005", "SECRETARIA MUN DE ASSISTENCIA SOCIAL"): "Secretaria Municipal de Assistência Social",
    ("006", "FUNDO MUNICIPAL DO MEIO AMBIENTE"): "Fundo Municipal de Meio Ambiente",
    ("007", "FUNDO DOS DIR DA CRIANCA E ADOLESCENTE"): (
        "Fundo dos Direitos da Criança e Adolescente"
    ),
    ("008", "FUNDO MUN DE HABITACAO E INTER SOCIAL"): (
        "Fundo Municipal de Habitação e Interesse Social"
    ),
    ("009", "FUNDO MUNICIPAL DE CULTURA"): "Fundo Municipal de Cultura",
    ("010", "SAAEP SERVICO AUTONOMO DE AGUA E ESGOTO"): (
        "SAAEP — Serviço Autônomo de Água e Esgoto"
    ),
    ("011", "FUNDO MUNICIPAL DOS DIREITOS DA MULHER"): (
        "Fundo Municipal dos Direitos da Mulher"
    ),
    ("012", "FUNDO MUN DA PESSOA COM DEFICIENCIA"): (
        "Fundo Municipal da Pessoa com Deficiência"
    ),
    ("013", "FUNDO MUN DE INTEG E PROTAG JUVENIL"): (
        "Fundo Municipal de Integração e Protagonismo Juvenil"
    ),
    ("016", "FUNDEB"): "FUNDEB",
    ("017", "FUNDO DE DESENVOLVIMENTO DO TURISMO"): (
        "Fundo Municipal de Desenvolvimento do Turismo"
    ),
    ("019", "FUNDO DA PESSOA IDOSA"): "Fundo Municipal da Pessoa Idosa",
    ("020", "SECRETARIA MUNICIPAL DE CULTURA"): "Secretaria Municipal de Cultura",
    ("021", "SECRETARIA MUNICIPAL DE DESENVOLVIMENTO"): (
        "Secretaria Municipal de Desenvolvimento"
    ),
    ("022", "SECRETARIA MUNICIPAL DE ESPORTES E LAZER"): (
        "Secretaria Municipal de Esportes e Lazer"
    ),
    ("023", "SECRETARIA MUNICIPAL DE ADMINISTRACAO"): (
        "Secretaria Municipal de Administração"
    ),
    ("024", "SECRETARIA MUNICIPAL DE SERVICOS URBANOS"): (
        "Secretaria Municipal de Serviços Urbanos"
    ),
    ("025", "SECRETARIA MUNICIPAL DO MEIO AMBIENTE"): (
        "Secretaria Municipal de Meio Ambiente e Sustentabilidade"
    ),
    ("026", "SECRETARIA MUNICIPAL DE OBRAS"): "Secretaria Municipal de Obras",
    ("027", "SECRETARIA MUNICIPAL DE PRODUCAO RURAL"): (
        "Secretaria Municipal de Produção Rural"
    ),
    ("029", "SEC MUN DE HABITACAO E DE INTER SOCIAL"): (
        "Secretaria Municipal de Habitação e Interesse Social"
    ),
    ("030", "SEC MUN DE MINER ENERGIA CIENCIA E TECNO"): (
        "Secretaria Municipal de Mineração, Energia, Ciência e Tecnologia"
    ),
    ("031", "SEC MUN DESEG INSTIT E DEFESA DO CIDADAO"): (
        "Secretaria Municipal de Segurança Institucional e Defesa do Cidadão"
    ),
    ("032", "SECRETARIA ESPECIAL DE GOVERNO"): "Secretaria Especial de Governo",
    ("033", "PROSAP PROG DE SANEAM AMBIENT RIO PARAUA"): (
        "PROSAP — Programa Municipal de Saneamento Ambiental"
    ),
    ("034", "FUNDO MUNIC DE REGULARIZACAO FUNDIARIA"): (
        "Fundo Municipal de Regularização Fundiária"
    ),
    ("035", "FUNDO ESPECIAL DE CUSTEIO DE ILUMINACAO"): (
        "Fundo Especial de Custeio de Iluminação Pública"
    ),
    ("036", "SECRETARIA MUNICIPAL DA JUVENTUDE"): "Secretaria Municipal da Juventude",
    ("037", "SECRETARIA MUNICIPAL DE TURISMO"): "Secretaria Municipal de Turismo",
    ("041", "FUNDO MUNICIPAL DE DEFESA DO CONSUMIDOR"): (
        "Fundo Municipal de Defesa do Consumidor"
    ),
    ("042", "FUNDO DE SEGUR ALIMENTAR E NUTRICIONAL"): (
        "Fundo Municipal de Segurança Alimentar e Nutricional"
    ),
}

PROGRAMAS_SEM_EXECUCAO = {
    "6014": ("041", "provisório"),
    "6022": ("004", "provisório"),
    "6032": ("005", "provisório"),
    "6033": ("005", "provisório"),
    "6053": ("011", "provisório"),
    "6072": ("030", "provisório"),
    "6074": ("025", "provisório"),
}

PROGRAMAS_SEM_UG = {
    "6005": "Fundo Especial de Promoção dos Direitos Indígenas — FEPPI",
    "6083": "Fundo Municipal de Investimentos Sustentáveis, Negócios Ecológicos e Economia de Carbono",
    "6084": "Fundo de Incentivo às Ações de Ensino Superior",
    "6085": "Fundo de Incentivo às Ações de Ensino Superior",
}

PROGRAMAS_EXCLUIDOS = {
    "6034-A": "Abraçando o Autismo — excluído da revisão do PPA",
    "6066-A": "Programa excluído da revisão do PPA",
}

DONOS_COMPARTILHADOS = {
    "6013": "001",
    "6023": "004",
    "6024": "004",
    "6025": "004",
}

PROGRAMA_FORA_PPA = "6200"

FONTES = {
    "15000000": "Recursos não vinculados de impostos",
    "15001001": "Receita de imposto e transferências — Educação",
    "15001002": "Receita de imposto e transferências — Saúde",
    "15003112": "Emenda parlamentar impositiva municipal individual",
    "15003122": "Emenda parlamentar impositiva municipal de bancada",
    "15010000": "Outros recursos não vinculados",
    "15400000": "Transferências do FUNDEB — Impostos",
    "15401070": "Transferências do FUNDEB — Impostos 70%",
    "15410000": "Transferência do FUNDEB — Complementação da União — VAAF",
    "15411070": "Transferência do FUNDEB 70% — Complementação da União — VAAF",
    "15500000": "Transferência do Salário-Educação",
    "15520000": "Transferência de recursos do PNAE",
    "15530000": "Transferência de recursos do PNATE",
    "15690000": "Outras transferências do FNDE",
    "16000000": "Transferência SUS — Bloco de manutenção",
    "16010000": "Transferência SUS — Bloco de estruturação",
    "16040000": "Transferência de ações de saúde e combate às endemias",
    "16210000": "Transferência SUS — Governo Estadual",
    "16600000": "Transferência de recursos do FNAS",
    "16610000": "Transferência de recursos do Fundo Estadual de Assistência Social",
    "17080000": "Transferência de compensação financeira por recursos minerais",
    "17200000": "Transferência de petróleo e gás — FEP",
    "17470000": "Outras vinculações de transferências da União",
    "17491020": "Transferência LC 176/2020 — AFM Lei Kandir",
    "17491060": "Transferência do Estado — cota-parte ICMS Verde",
    "17500000": "CIDE",
    "17510000": "Contribuição de iluminação pública",
    "17520000": "Recursos vinculados ao trânsito",
    "17530000": "Taxas, contribuições e preços públicos",
    "17550000": "Alienação de bens e ativos — administração direta",
    "18990000": "Outros recursos vinculados",
}

NATUREZAS = {
    "3.1.90.04.00": "Contratação por tempo determinado",
    "3.1.90.11.00": "Vencimentos e vantagens fixas — pessoal civil",
    "3.1.90.13.00": "Obrigações patronais",
    "3.1.90.16.00": "Outras despesas variáveis — pessoal civil",
    "3.1.90.94.00": "Indenizações e restituições trabalhistas",
    "3.2.90.21.00": "Juros sobre a dívida por contrato",
    "3.3.90.14.00": "Diárias — civil",
    "3.3.90.30.00": "Material de consumo",
    "3.3.90.33.00": "Passagens e despesas com locomoção",
    "3.3.90.36.00": "Outros serviços de terceiros — pessoa física",
    "3.3.90.39.00": "Outros serviços de terceiros — pessoa jurídica",
    "3.3.90.46.00": "Auxílio-alimentação",
    "3.3.90.48.00": "Outros auxílios financeiros a pessoas físicas",
    "3.3.90.49.00": "Auxílio-transporte",
    "3.3.90.91.00": "Sentenças judiciais",
    "3.3.90.92.00": "Despesas de exercícios anteriores",
    "3.3.90.93.00": "Indenizações e restituições",
    "4.4.90.51.00": "Obras e instalações",
    "4.4.90.52.00": "Equipamentos e material permanente",
    "4.6.90.71.00": "Principal da dívida contratual resgatado",
}

CATEGORIAS_NATUREZA = {
    "3.1": "Pessoal e encargos sociais",
    "3.2": "Juros e encargos da dívida",
    "3.3": "Outras despesas correntes",
    "4.4": "Investimentos",
    "4.5": "Inversões financeiras",
    "4.6": "Amortização da dívida",
}


def nome_ug(codigo: str) -> str:
    return UG_NOMES.get(codigo, codigo)


def slug_ug(codigo: str) -> str:
    return UG_SLUGS.get(codigo, f"ug_{codigo}")


def nome_uo(codigo_ug: str, nome_normalizado: str, nome_contas: str = "") -> str:
    return UO_NOMES_OFICIAIS.get(
        (codigo_ug, nome_normalizado),
        nome_contas or nome_normalizado.title(),
    )
