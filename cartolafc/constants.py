import json

MERCADO_ABERTO = 1
MERCADO_FECHADO = 2

CAMPEONATO = 'campeonato'
TURNO = 'turno'
MES = 'mes'
RODADA = 'rodada'
PATRIMONIO = 'patrimonio'

# dict_prem = {"primeiro_turno": {"lider": ''},
#              "liberta_prim_turno": {"campeao": '', "vice": ''},
#              "segundo_turno": {'lider': ''},
#              "liberta_seg_turno": {"campeao": '', "vice": ''},
#              "geral": {"campeao": '', "seg_lugar": '', "terc_lugar": '', "quarto_lugar": ''}
#              }
dict_prem = {}
with open('static/dict_prem.json', encoding='utf-8', mode='r') as currentFile:
    data = currentFile.read().replace('\n', '')
    for k, v in json.loads(data).items():
        dict_prem[k] = v

with open('./tmp/dict_prem.json', encoding='utf-8', mode='r') as currentFile:
    data = currentFile.read().replace('\n', '')
    for k, v in json.loads(data).items():
        dict_prem[k] = v

rodadas_campeonato = range(1, 39)
rodadas_primeiro_turno = range(1, 20)
rodadas_segundo_turno = range(20, 39)
# rodadas_liberta_prim_turno = range(6, 12)
rodadas_liberta_prim_turno = range(2, 12)
rodadas_oitavas_prim_turno = range(12, 14)
rodadas_quartas_prim_turno = range(14, 16)
rodadas_semis_prim_turno = range(16, 18)
rodadas_finais_prim_turno = range(18, 20)
rodadas_liberta_seg_turno = range(25, 31)
rodadas_oitavas_seg_turno = range(31, 33)
rodadas_quartas_seg_turno = range(33, 35)
rodadas_semis_seg_turno = range(35, 37)
rodadas_finais_seg_turno = range(37, 39)

grupo_liberta_prim_turno = [44558779, 1241021, 1893918, 1889674,
                            19190102, 47620752, 219929, 279314,
                            1245808, 44509672, 18796615, 13957925,
                            47803719, 25582672, 48733, 3646412, 8912058,
                            315637, 71375, 1235701, 977136, 28919430]

list_oitavas_prim_turno = ['1245808', '71375', '3646412', '28919430', '977136', '1241021', '219929', '44558779',
                           '25588958',
                           '44514741', '44509672', '579336', '19317259', '13957925', '315637', '1889674']

list_quartas_prim_turno = ['1245808', '219929', '3646412', '977136', '315637', '25588958', '28919430', '1241021']

list_semis_prim_turno = ['219929', '3646412', '25588958', '28919430']

list_finais_prim_turno = ['3646412', '28919430']

grupo_liberta_seg_turno = [28919430, 1241021, 219929, 18796615,
                           48733, 14439636, 44558779, 25588958,
                           3646412, 19317259, 44514741, 44509672,
                           1245808, 1889674, 579336, 25582672,
                           13957925, 1893918, 19190102, 1235701,
                           71375, 315637, 977136, 8912058]

premios = {
    'prem_camp_geral': 945.00,
    'prem_vice_geral': 420.00,
    'prem_terc_geral': 210.00,
    'prem_quarto_geral': 105.00,
    'prem_camp_turno': 210.00,
    'prem_camp_mm': 393.75,
    'prem_vice_mm': 131.25
}

# list_oitavas_seg_turno = ['1245808', '44558779', '71375', '44514741', '1241021', '219929', '19190102', '8912058', '48733', '13957925', '1889674', '44509672', '977136', '18796615', '1893918', '3646412']

list_quartas_seg_turno = []

list_semis_seg_turno = []

list_finais_seg_turno = []

dict_matamata = {
    "oitavas": [],
    "quartas": [],
    "semis": [],
    "finais": []
}
with open('static/dict_matamata.json', mode='r') as currentFile:
    data = currentFile.read().replace('\n', '')
    for k, v in json.loads(data).items():
        dict_prem[k] = v

list_oitavas_seg_turno = []
