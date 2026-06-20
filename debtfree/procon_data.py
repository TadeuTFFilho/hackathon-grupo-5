"""
Dados de contato do PROCON e Defensoria Pública por estado.
Fonte: sites oficiais dos órgãos — verificar periodicamente para atualização.
"""

PROCON_BY_STATE = {
    "SP": {
        "procon": {
            "name": "PROCON-SP",
            "phone": "151",
            "website": "https://www.procon.sp.gov.br",
            "address": "Rua Barra Funda, 930 — Barra Funda, São Paulo/SP",
        },
        "defensoria": {
            "name": "Defensoria Pública do Estado de SP",
            "phone": "(11) 3105-0919",
            "website": "https://www.defensoria.sp.def.br",
            "address": "Praça do Carmo s/n — Sé, São Paulo/SP",
        },
    },
    "RJ": {
        "procon": {
            "name": "PROCON-RJ",
            "phone": "151",
            "website": "https://www.procon.rj.gov.br",
            "address": "Av. Erasmo Braga, 115 — Centro, Rio de Janeiro/RJ",
        },
        "defensoria": {
            "name": "Defensoria Pública do Estado do RJ",
            "phone": "(21) 2334-6200",
            "website": "https://www.dpge.rj.gov.br",
            "address": "Rua Acre, 60 — Centro, Rio de Janeiro/RJ",
        },
    },
    "MG": {
        "procon": {
            "name": "PROCON-MG",
            "phone": "151",
            "website": "https://www.procon.mg.gov.br",
            "address": "Rua dos Guajajaras, 40 — Centro, Belo Horizonte/MG",
        },
        "defensoria": {
            "name": "Defensoria Pública do Estado de MG",
            "phone": "(31) 3330-7000",
            "website": "https://www.defensoria.mg.def.br",
            "address": "Rua Álvares Cabral, 1740 — Santo Agostinho, Belo Horizonte/MG",
        },
    },
    "RS": {
        "procon": {
            "name": "PROCON-RS",
            "phone": "151",
            "website": "https://www.procon.rs.gov.br",
            "address": "Av. Borges de Medeiros, 1501 — Centro Histórico, Porto Alegre/RS",
        },
        "defensoria": {
            "name": "Defensoria Pública do Estado do RS",
            "phone": "(51) 3211-0600",
            "website": "https://www.dpe.rs.gov.br",
            "address": "Av. João Pessoa, 1020 — Farroupilha, Porto Alegre/RS",
        },
    },
    "BA": {
        "procon": {
            "name": "PROCON-BA",
            "phone": "151",
            "website": "https://www.procon.ba.gov.br",
            "address": "Rua General Labatut, 273 — Barris, Salvador/BA",
        },
        "defensoria": {
            "name": "Defensoria Pública do Estado da BA",
            "phone": "(71) 3116-6900",
            "website": "https://www.defensoria.ba.def.br",
            "address": "Rua Conselheiro Dantas, 31 — Comércio, Salvador/BA",
        },
    },
    "PR": {
        "procon": {
            "name": "PROCON-PR",
            "phone": "151",
            "website": "https://www.procon.pr.gov.br",
            "address": "Rua Marechal Deodoro, 936 — Centro, Curitiba/PR",
        },
        "defensoria": {
            "name": "Defensoria Pública do Estado do PR",
            "phone": "(41) 3200-2400",
            "website": "https://www.defensoriapublica.pr.def.br",
            "address": "Av. Marechal Floriano Peixoto, 96 — Centro, Curitiba/PR",
        },
    },
    "PE": {
        "procon": {
            "name": "PROCON-PE",
            "phone": "151",
            "website": "https://www.procon.pe.gov.br",
            "address": "Rua do Riachuelo, 105 — Boa Vista, Recife/PE",
        },
        "defensoria": {
            "name": "Defensoria Pública do Estado de PE",
            "phone": "(81) 3184-0500",
            "website": "https://www.defensoria.pe.def.br",
            "address": "Rua do Imperador Pedro II, 297 — Santo Antônio, Recife/PE",
        },
    },
    "CE": {
        "procon": {
            "name": "DECON-CE (PROCON Estadual)",
            "phone": "151",
            "website": "https://www.procon.ce.gov.br",
            "address": "Av. Bezerra de Menezes, 1700 — São Gerardo, Fortaleza/CE",
        },
        "defensoria": {
            "name": "Defensoria Pública do Estado do CE",
            "phone": "(85) 3101-0500",
            "website": "https://www.defensoria.ce.def.br",
            "address": "Av. Pontes Vieira, 2625 — Dionísio Torres, Fortaleza/CE",
        },
    },
    "GO": {
        "procon": {
            "name": "PROCON-GO",
            "phone": "151",
            "website": "https://www.procon.go.gov.br",
            "address": "Rua 82, 394 — Setor Sul, Goiânia/GO",
        },
        "defensoria": {
            "name": "Defensoria Pública do Estado de GO",
            "phone": "(62) 3096-9300",
            "website": "https://www.defensoria.go.def.br",
            "address": "Rua 23, 465 — Setor Leste Universitário, Goiânia/GO",
        },
    },
    "DF": {
        "procon": {
            "name": "PROCON-DF",
            "phone": "151",
            "website": "https://www.procon.df.gov.br",
            "address": "SCS, Quadra 6, Bloco A, Ed. Carioca — Asa Sul, Brasília/DF",
        },
        "defensoria": {
            "name": "Defensoria Pública do Distrito Federal",
            "phone": "(61) 3318-7600",
            "website": "https://www.defensoria.df.gov.br",
            "address": "SGAN 909, Lote C — Asa Norte, Brasília/DF",
        },
    },
    "AM": {
        "procon": {
            "name": "PROCON-AM",
            "phone": "151",
            "website": "https://www.procon.am.gov.br",
            "address": "Rua Ferreira Pena, 179 — Centro, Manaus/AM",
        },
        "defensoria": {
            "name": "Defensoria Pública do Estado do AM",
            "phone": "(92) 3655-0500",
            "website": "https://www.defensoria.am.def.br",
            "address": "Av. André Araújo, 681 — Aleixo, Manaus/AM",
        },
    },
    "SC": {
        "procon": {
            "name": "PROCON-SC",
            "phone": "151",
            "website": "https://www.procon.sc.gov.br",
            "address": "Av. Mauro Ramos, 266 — Centro, Florianópolis/SC",
        },
        "defensoria": {
            "name": "Defensoria Pública do Estado de SC",
            "phone": "(48) 3665-1500",
            "website": "https://www.defensoria.sc.def.br",
            "address": "Rua Paschoal Apóstolo Pítsica, 4860 — Agronômica, Florianópolis/SC",
        },
    },
    # Fallback para estados sem dados específicos
    "DEFAULT": {
        "procon": {
            "name": "PROCON do seu município",
            "phone": "151",
            "website": "https://www.justica.gov.br/seus-direitos/consumidor/procons",
            "address": "Consulte a prefeitura local para o endereço do PROCON municipal",
        },
        "defensoria": {
            "name": "Defensoria Pública Estadual",
            "phone": "129",
            "website": "https://anadep.org.br/wtk/pagina/materia?idMateria=50191",
            "address": "Acesse defensoria.gov.br para encontrar a unidade mais próxima",
        },
    },
}
