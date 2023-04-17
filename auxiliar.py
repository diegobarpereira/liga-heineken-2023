import collections
import json
import requests
import cartolafc
import timeit
from concurrent.futures import ThreadPoolExecutor, as_completed
import datetime

from cartolafc.constants import rodadas_oitavas_seg_turno, dict_matamata
from flask_app import get_class_liberta_seg_turno

api = cartolafc.Api(
    glb_id='172581de631e18dbb95b8cf269b20a102535a4f6f49734977304a6f6d435879637544565066395663524855335f6f6e4e72737a6539465467467232674b417a51326c396644726179763752737652364e6b5f3066636d6547504c705879554548582d6d564b673d3d3a303a646965676f2e323031312e382e35')

rod = api.mercado().rodada_atual
mercado_status = api.mercado().status.nome
rodadas = range(1, rod)

# todos_ids = [1241021, 1893918, 1245808, 8912058, 1889674, 13957925, 71375, 48733,
#              3646412, 219929, 1235701, 25582672, 25588958, 315637, 18796615,
#              19190102, 579336, 44514741, 44509672, 14439636, 279314, 28919430,
#              19317259, 44558779, 977136]

todos_ids = []
if api.mercado().status.nome != 'Mercado em manutenção':
    ligas = api.liga('liga-heineken-2023')

    for lig in ligas.times:
        todos_ids.append(lig.ids)


def get_times(id_):
    data = []

    if rod == 1:
        for r in range(1, 2):
            data.append(requests.get(f'https://api.cartolafc.globo.com/time/id/{id_}/{r}').json())

    else:

        if mercado_status == 'Mercado aberto':

            for r in range(1, rod):
                data.append(requests.get(f'https://api.cartolafc.globo.com/time/id/{id_}/{r}').json())

        if mercado_status == 'Final de temporada':
            for r in range(1, rod + 1):
                data.append(requests.get(f'https://api.cartolafc.globo.com/time/id/{id_}/{r}').json())

    return data


def salvar_times_rodadas():
    outer_dict = {}
    teams = []

    with ThreadPoolExecutor(max_workers=40) as executor:
        times = executor.map(get_times, todos_ids)
        for time in times:
            teams.append(time)

    if mercado_status == 'Mercado fechado' and rod == 1:

        for rodada in range(1, 2):
            inner_dict = {}
            for d in teams:
                for data in d:
                    if data['rodada_atual'] == rodada:
                        inner_dict[data['time']['time_id']] = 0

            outer_dict[rodada] = inner_dict

    if mercado_status == 'Mercado aberto':

        for rodada in range(1, rod):
            inner_dict = {}
            for d in teams:
                for data in d:
                    if data['rodada_atual'] == rodada:
                        inner_dict[data['time']['time_id']] = data['pontos']

            outer_dict[rodada] = inner_dict

    if mercado_status == 'Final de temporada':
        for rodada in range(1, rod + 1):
            inner_dict = {}
            for d in teams:
                for data in d:
                    if data['rodada_atual'] == rodada:
                        inner_dict[data['time']['time_id']] = data['pontos']

            outer_dict[rodada] = inner_dict

    with open(f'static/times_rodada.json', 'w') as f:
        json.dump(outer_dict, f)


def get_escudo():
    dict_foto = {}
    times = []
    for id_ in todos_ids:
        times.append(api.time(id_))

    for time in times:
        dict_foto[time.info.id] = time.info.foto

    with open(f'static/escudos.json', 'w') as f:
        json.dump(dict_foto, f)


def get_nomes():
    dict_nome = {}
    times = []
    for id_ in todos_ids:
        times.append(api.time(id_))

    for time in times:
        dict_nome[time.info.id] = time.info.nome

    with open(f'static/nomes.json', 'w', encoding='utf-8') as f:
        json.dump(dict_nome, f, ensure_ascii=False)


def get_times_rodada():
    dict_time = {}
    with open('static/times_rodada.json', encoding='utf-8', mode='r') as currentFile:
        data = currentFile.read().replace('\n', '')

        for k, v in json.loads(data).items():
            dict_time[k] = v

    return dict_time


def salvar_participantes():
    participantes = {}
    with open('static/escudos.json', encoding='utf-8', mode='r') as currentFile:
        escudos = currentFile.read().replace('\n', '')

    with open('static/nomes.json', encoding='utf-8', mode='r') as currentFile:
        nomes = currentFile.read().replace('\n', '')

    for chave, valor in get_times_rodada().items():
        for c, v in json.loads(escudos).items():
            for id, nome in json.loads(nomes).items():
                if chave == str(1):
                    for v1, v2 in valor.items():
                        if v1 == c:
                            if v1 == id:
                                participantes[nome] = v

    with open(f'static/participantes.json', 'w') as f:
        json.dump(participantes, f)


def get_sem_capitao():
    dict_capitao = {}
    time_ids = []
    sem_capitao = {}

    for key, value in get_times_rodada().items():
        time_ids = [v[0] for v in value.items()]

    with ThreadPoolExecutor(max_workers=40) as executor:
        times = executor.map(get_times, time_ids)

        for d in times:
            for data in d:
                pts = 0
                time_nome = data['time']['nome']
                time_id = data['time']['time_id']
                for at in data['atletas']:
                    pts += at['pontos_num']

                # if time_nome in dict_capitao:
                #     dict_capitao[time_nome].append(pts)
                # else:
                #     dict_capitao[time_nome] = [pts]

                if time_id in dict_capitao:
                    dict_capitao[time_id].append(pts)
                else:
                    dict_capitao[time_id] = [pts]

    ordenar_dict = sorted(dict_capitao.items(), key=lambda t: sum(t[1]), reverse=True)
    for k in ordenar_dict:
        sem_capitao[k[0]] = sum(k[1])

    with open(f'static/sem_capitao.json', 'w') as f:
        json.dump(sem_capitao, f)


def retornar_estats_liga():
    dict_time_stats = {}
    dict_time_stats_ = {}

    with ThreadPoolExecutor(max_workers=40) as executor:
        times = executor.map(get_times, todos_ids)

        for d in times:
            for data in d:

                scout = {'PI': 0, 'I': 0, 'PP': 0, 'PC': 0, 'FC': 0, 'CA': 0, 'CV': 0, 'GC': 0, 'GS': 0, 'G': 0, 'A': 0,
                         'FT': 0, 'FD': 0, 'FF': 0, 'FS': 0, 'PS': 0, 'DS': 0, 'SG': 0, 'DE': 0, 'DP': 0}
                scout_points = {'PI': -0.1, 'I': -0.1, 'PP': -4, 'PC': -1, 'FC': -0.3, 'CA': -1, 'CV': -3, 'GC': -3,
                                'GS': -1, 'G': 8, 'A': 5, 'FT': 3, 'FD': 1.2, 'FF': 0.8, 'FS': 0.5, 'PS': 1, 'DS': 1.2,
                                'SG': 5, 'DE': 1, 'DP': 7}

                for at in data['atletas']:
                    if data['time']['nome'] in dict_time_stats:
                        dict_time_stats[data['time']['nome']].append(at['scout'])
                    else:
                        dict_time_stats[data['time']['nome']] = [at['scout']]

                for dts in dict_time_stats[data['time']['nome']]:
                    if (type(dts)) is dict:
                        for k, v in dts.items():
                            if k in scout.keys():
                                scout[k] = scout.get(k, 0) + dts[k]
                            else:
                                scout[k] = 0

                    dict_time_stats_[data['time']['nome']] = [scout, ' ',
                                                              {key: "{:.2f}".format(
                                                                  scout_points[key] * scout.get(key, 0))
                                                                  for key in scout_points.keys()}]

    with open(f'static/times_stats.json', 'w') as f:
        json.dump(dict_time_stats_, f)


def json_default(value):
    if isinstance(value, datetime.date):
        return dict(year=value.year, month=value.month, day=value.day)
    else:
        return value.__dict__


def get_partidas():
    list_partidas = []

    for partidas in api.partidas(rod):
        list_partidas.append(partidas)

        with open(f'static/partidas.json', 'w', encoding='utf-8') as f:
            json.dump(list_partidas, f, default=json_default, ensure_ascii=False)


start_time = timeit.default_timer()
# get_escudo()
# get_nomes()
# salvar_participantes()
# get_partidas()

########################### rodar_tudo


def rodar_tudo():
    get_sem_capitao()
    salvar_times_rodadas()
    retornar_estats_liga()
    get_partidas()
########################### rodar_tudo


# salvar_times_rodadas()

rodar_tudo()
#
# dict_matamata_oitavas = {}
# # list_oitavas_seg_turno = []
#
# # if not dict_matamata['oitavas']:
# #     dict_matamata['oitavas'] = get_class_liberta_seg_turno()
# #
# #     with open(f'static/dict_matamata.json', 'w') as f:
# #         json.dump(dict_matamata, f)
#
# with open('static/dict_matamata.json', encoding='utf-8', mode='r') as currentFile:
#     data_matamata = currentFile.read().replace('\n', '')
#
#     for x, y in json.loads(data_matamata).items():
#         dict_matamata_oitavas[x] = y
#
# if len(dict_matamata_oitavas['oitavas']) == 0:
#     dict_matamata['oitavas'] = get_class_liberta_seg_turno()
#
#     with open(f'static/dict_matamata.json', 'w') as f:
#         json.dump(dict_matamata, f)
#
#     list_oitavas_seg_turno = dict_matamata['oitavas']
#
# else:
#     list_oitavas_seg_turno = dict_matamata_oitavas['oitavas']
#
# print(list_oitavas_seg_turno)

# print(get_class_liberta_seg_turno())

# dict_prem = {"primeiro_turno": {"lider": ''},
#              "liberta_prim_turno": {"campeao": '', "vice": ''},
#              "segundo_turno": {'lider': ''},
#              "liberta_seg_turno": {"campeao": '', "vice": ''},
#              "geral": {"campeao": '', "seg_lugar": '', "terc_lugar": '', "quarto_lugar": ''}
#              }
#
#
# def add_nome():
#
#     dict_prem['primeiro_turno']['lider'] = 'Diego'
#
#     with open(f'static/dict_prem.json', 'w', encoding='utf-8') as f:
#         json.dump(dict_prem, f)
#
#
# def add_liberta():
#
#     dict_prem['liberta_prim_turno']['campeao'] = 'Diego 2'
#     dict_prem['liberta_prim_turno']['vice'] = 'Diego 3'
#
#     with open(f'static/dict_prem.json', 'w', encoding='utf-8') as f:
#         json.dump(dict_prem, f)
#
#
# add_liberta()
# add_nome()
#

# dict_matamata = {
#     "oitavas": [],
#     "quartas": [],
#     "semis": [],
#     "finais": []
# }
# with open(f'static/dict_matamata.json', 'w', encoding='utf-8') as f:
#     json.dump(dict_matamata, f)

# for x in range(37, 39):
#     print(x)


print(timeit.default_timer() - start_time)

# dict_nome_escudo_pontos = {"Christimao": 11, "Peix\u00e3o Irado": 10, "Diego Pereira FC": 12, "Markitos Bar": 13, "0VINTE1 FC": 14, "oSantista": 15, "Denoris F.C.": 16, "Ra\u00e7a Tim\u00e3o!!!": 17, "Gabitreta F C": 18, "Camisa21FC": 19, "Eae Malandro FC": 20, "JevyGoal": 21, "JUNA FUTEBOL CLUBE": 22, "Real Beach Soccer": 23, "Golden Lions FC": 24, "ThiagoRolo FC": 25, "CFDS06": 26, "Rod Santos FC": 27, "FAFA SHOW FC": 28, "ArrascaMaisDez": 29, "AvantiHulkFc": 30, "Gonella Verde ": 31, "Xanpion": 32, "S\u00f3h Taapa FC": 33, "RIVA 77 ": 34}
#
# dict_teste = {'Peixão Irado': ['https://s3.glbimg.com/v1/AUTH_58d78b787ec34892b5aaa0c7a146155f/cartola_svg_199/escudo/be/54/52/00015cb0cc-580f-4a3b-993b-d7dc872d3bbe20220310145452', [77.25, 108.919921875, 92.08984375, 49.7099609375, 42.7099609375, 78.0400390625, 93.3798828125, 73.81005859375, 29.43994140625, 115.66015625, 62.739990234375, 96.8701171875, 83.83984375, 82.39990234375, 39.669921875, 79.5498046875, 56.8701171875, 98.14013671875, 74.3701171875, 30.3800048828125, 76.8701171875]], 'Christimao': ['https://s3.glbimg.com/v1/AUTH_58d78b787ec34892b5aaa0c7a146155f/cartola_svg_100/escudo/56/28/25/0046e18a00-c022-4a79-a1a3-23e02915135620180322132825', [116.330078125, 104.35009765625, 30.1800537109375, 54.81005859375, 64.7998046875, 106.77978515625, 90.27978515625, 75.3798828125, 31.5999755859375, 79.9599609375, 34.419921875, 92.8701171875, 81.0400390625, 59.659912109375, 56.169921875, 75.8798828125, 59.570068359375, 112.83984375, 77.02001953125, 61.97998046875, 79.47021484375]], 'Diego Pereira FC': ['https://s3.glbimg.com/v1/AUTH_58d78b787ec34892b5aaa0c7a146155f/cartola_svg_180/escudo/9d/17/35/00d2bb4ea0-e8d3-4292-843e-7ef3c0c0109d20200921081735', [81.4501953125, 127.35009765625, 59.590087890625, 57.14990234375, 46.010009765625, 100.22021484375, 73.89990234375, 72.7900390625, 43.85009765625, 99.35986328125, 56.0400390625, 85.56982421875, 108.43994140625, 69.64990234375, 75.27001953125, 101.27001953125, 71.77001953125, 93.14013671875, 96.509765625, 89.080078125, 83.8701171875]], 'Markitos Bar': ['https://s3.glbimg.com/v1/AUTH_58d78b787ec34892b5aaa0c7a146155f/cartola_svg_191/escudo/6e/20/50/00fe5cef85-2032-4348-b47f-6a4bb2c35c6e20210529182050', [94.5498046875, 64.5400390625, 62.8798828125, 51.0400390625, 45.68994140625, 71.89013671875, 67.18994140625, 73.25, 41.550048828125, 86.009765625, 44.02001953125, 87.14013671875, 75.22021484375, 63.659912109375, 25.550048828125, 19.2900390625, 46.139892578125, 86.240234375, 61.5400390625, 65.6298828125, 51.199951171875]], '0VINTE1 FC': ['https://s3.glbimg.com/v1/AUTH_58d78b787ec34892b5aaa0c7a146155f/cartola_svg_199/escudo/c1/03/43/00a6842184-e625-4da0-ac9b-d9f8fc475fc120220311000343', [48.75, 83.5498046875, 63.360107421875, 57.510009765625, 60.889892578125, 91.43994140625, 89.97998046875, 81.35009765625, 21.5999755859375, 105.759765625, 36.429931640625, 98.7001953125, 68.83984375, 96, 70.56982421875, 88.009765625, 70.27001953125, 102.8701171875, 116.2900390625, 75.3798828125, 81.8701171875]], 'oSantista': ['https://s3.glbimg.com/v1/AUTH_58d78b787ec34892b5aaa0c7a146155f/cartola_svg_171/escudo/65/07/51/008f8748c4-3687-4382-b394-2da82ce7c06520200807120751', [99.85009765625, 97.259765625, 72.4599609375, 69.60986328125, 50.22998046875, 116.919921875, 85.39990234375, 90.47998046875, 31, 110.4599609375, 52.239990234375, 88.8701171875, 86.14013671875, 81.5498046875, 62.469970703125, 64.47021484375, 65.169921875, 107.64013671875, 83.490234375, 99.5400390625, 79.0498046875]], 'Denoris F.C.': ['https://s3.glbimg.com/v1/AUTH_58d78b787ec34892b5aaa0c7a146155f/cartola_svg_200/escudo/8d/48/07/0075b78f19-2721-4b95-b29d-82654ac0618d20220320144807', [98.25, 96.64990234375, 55.080078125, 64.009765625, 56, 109.419921875, 78.3798828125, 96.18017578125, 30.550048828125, 120.9599609375, 49.469970703125, 78.27001953125, 84.33984375, 84.66015625, 75.4501953125, 88.02001953125, 74.25, 77.240234375, 88.77001953125, 78.77978515625, 52.050048828125]], 'Raça Timão!!!': ['https://s3.glbimg.com/v1/AUTH_58d78b787ec34892b5aaa0c7a146155f/cartola_svg_185/escudo/e0/26/06/00e346c37f-2729-4c11-a4f3-e816469b79e020210502142606', [100.9501953125, 134.0498046875, 52.47998046875, 61.14990234375, 52.300048828125, 104.14013671875, 100.8798828125, 62.280029296875, 31.550048828125, 104.4599609375, 50.739990234375, 80.8701171875, 96.93994140625, 70, 73.77001953125, 89.3798828125, 65.3701171875, 105.240234375, 95.31005859375, 87.14013671875, 75.3701171875]], 'Gabitreta F C': ['https://s3.glbimg.com/v1/AUTH_58d78b787ec34892b5aaa0c7a146155f/cartola_svg_188/escudo/ba/24/18/00f9742c5c-169f-4773-bba0-061b80f7bbba20210526012418', [88.5498046875, 78.4599609375, 51.3798828125, 93.10986328125, 54.199951171875, 117.52001953125, 87.18017578125, 70.89013671875, 34.14990234375, 124.85986328125, 49.4599609375, 79.27001953125, 110.5400390625, 79.2001953125, 70.27001953125, 108.47021484375, 48.27001953125, 109.0400390625, 68.2099609375, 78.64013671875, 79.47021484375]], 'Camisa21FC': ['https://s3.glbimg.com/v1/AUTH_58d78b787ec34892b5aaa0c7a146155f/cartola_svg_186/escudo/2f/29/31/0060f57adb-95c1-476d-b10f-9bd87240802f20210511102931', [102.35009765625, 66.85009765625, 38.050048828125, 48.75, 44.7900390625, 93.52001953125, 80.7900390625, 65.9501953125, 28.449951171875, 120.9599609375, 62.820068359375, 108.06982421875, 94.33984375, 76.10009765625, 69.8701171875, 84.18017578125, 71.06982421875, 100.64013671875, 73.18994140625, 73.080078125, 77.4501953125]], 'Eae Malandro FC': ['https://s3.glbimg.com/v1/AUTH_58d78b787ec34892b5aaa0c7a146155f/cartola_svg_108/escudo/10/58/07/00f612a4ab-2fff-45fb-b94e-e94a40ec251020180411105807', [37.64990234375, 102.66015625, 62.780029296875, 71.10986328125, 60.2099609375, 81.68994140625, 75.68017578125, 62.179931640625, 21.449951171875, 80.259765625, 50.7900390625, 37.760009765625, 91.56005859375, 72.4599609375, 48.5400390625, 76.2001953125, 81.06982421875, 87.33984375, 76.60986328125, 66.83984375, 72.27001953125]], 'JevyGoal': ['https://s3.glbimg.com/v1/AUTH_58d78b787ec34892b5aaa0c7a146155f/cartola_svg_201/escudo/7b/18/04/0079af2740-7050-485f-b648-a4bc15b13c7b20220329231804', [75.5498046875, 61.860107421875, 44.590087890625, 50.31005859375, 44.989990234375, 84.419921875, 68.35009765625, 52.909912109375, 39.85009765625, 62.81005859375, 42.97998046875, 61.340087890625, 106.509765625, 74.9599609375, 47.969970703125, 68.169921875, 66.9501953125, 79.740234375, 87.009765625, 63.840087890625, 68.33984375]], 'JUNA FUTEBOL CLUBE': ['https://s3.glbimg.com/v1/AUTH_58d78b787ec34892b5aaa0c7a146155f/cartola_svg_201/escudo/4b/27/24/00fbc29f61-e850-4c0a-9704-b0d531e8774b20220328102724', [85.35009765625, 105.9599609375, 65.85009765625, 65.33984375, 55.610107421875, 105.81982421875, 65.2998046875, 75.41015625, 22.300048828125, 125.06005859375, 49.93994140625, 90.39990234375, 78.64990234375, 95.2998046875, 46.8701171875, 76.1201171875, 67.27001953125, 130.1396484375, 93.47021484375, 92.83984375, 83.8701171875]], 'Real Beach Soccer': ['https://s3.glbimg.com/v1/AUTH_58d78b787ec34892b5aaa0c7a146155f/cartola_svg_200/escudo/26/47/16/00ed7d2db6-4df4-4c32-b450-0c2d057e612620220317154716', [86.25, 108.4501953125, 74.4501953125, 59.81005859375, 62.199951171875, 88.5, 75.39990234375, 70.7900390625, 40.75, 94.35986328125, 59.239990234375, 92.3701171875, 98.64013671875, 82.60009765625, 45.27001953125, 79.72021484375, 60.27001953125, 84.240234375, 79.31005859375, 59.679931640625, 75.5498046875]], 'Golden Lions FC': ['https://s3.glbimg.com/v1/AUTH_58d78b787ec34892b5aaa0c7a146155f/cartola_svg_202/escudo/25/02/11/000ba604a1-93a0-4a47-b744-32a75059002520220402120211', [73.64990234375, 65.0498046875, 51.780029296875, 65.41015625, 65.6201171875, 76.7001953125, 61.35009765625, 66.8798828125, 36.35009765625, 115.9599609375, 37.469970703125, 100.77001953125, 106.75, 82.7001953125, 35.570068359375, 83.68017578125, 57.949951171875, 92.64013671875, 98.91015625, 97.419921875, 64.0498046875]], 'ThiagoRolo FC': ['https://s3.glbimg.com/v1/AUTH_58d78b787ec34892b5aaa0c7a146155f/cartola_svg_166/escudo/69/05/42/00d7c123ab-b3d9-4fa3-b90d-9cbbf403f06920200725110542', [109.25, 97.9599609375, 37.97998046875, 64.7099609375, 60.409912109375, 96.3798828125, 82.10009765625, 69.89013671875, 37.75, 40.889892578125, 48.77001953125, 72.27001953125, 92.83984375, 79.7001953125, 98.60986328125, 77.77001953125, 63.77001953125, 79.0400390625, 92.08984375, 58.080078125, 82.75]], 'CFDS06': ['https://s3.glbimg.com/v1/AUTH_58d78b787ec34892b5aaa0c7a146155f/cartola_svg_200/escudo/b5/22/43/00deb362e1-8623-46e1-bfd3-4d57e0014ab520220317212243', [85.0498046875, 57.85009765625, 43.18994140625, 59.64990234375, 56.68994140625, 86.919921875, 99.580078125, 78.85009765625, 40.35009765625, 88.66015625, 51.68994140625, 90.669921875, 65.33984375, 81.66015625, 33.43994140625, 100.8798828125, 74.06982421875, 134.33984375, 56.760009765625, 85.64013671875, 82.25]], 'Rod Santos FC': ['https://s3.glbimg.com/v1/AUTH_58d78b787ec34892b5aaa0c7a146155f/cartola_svg_199/escudo/ac/15/04/00789e74f4-9f20-4d32-aeda-19381e5060ac20220311101504', [76.5498046875, 88.66015625, 52.7900390625, 80.009765625, 47.97998046875, 93.31982421875, 63.679931640625, 73.7900390625, 42.64990234375, 100.259765625, 56.219970703125, 77.77001953125, 94.25, 64.64990234375, 65.669921875, 105.56982421875, 63.3701171875, 103.740234375, 91.60986328125, 84.240234375, 82.35009765625]], 'FAFA SHOW FC': ['https://s3.glbimg.com/v1/AUTH_58d78b787ec34892b5aaa0c7a146155f/cartola_svg_199/escudo/29/01/41/00719c8c57-1258-4828-b489-9a2b38e6202920220310160141', [82.43994140625, 92.919921875, 53.89990234375, 46.25, 42.110107421875, 102.7998046875, 73.490234375, 84.4501953125, 35.89990234375, 127.85986328125, 53.64990234375, 73.2001953125, 84.64013671875, 73.759765625, 44.8701171875, 54.280029296875, 55.570068359375, 73.83984375, 90, 93.740234375, 78.169921875]], 'ArrascaMaisDez': ['https://s3.glbimg.com/v1/AUTH_58d78b787ec34892b5aaa0c7a146155f/cartola_svg_202/escudo/d1/01/24/009252f09a-3361-4186-9b72-4642a6f615d120220405100124', [63.35009765625, 86.14990234375, 41.64990234375, 13.010009765625, 68.41015625, 102.2900390625, 60.389892578125, 64.2900390625, 35.1201171875, 116.259765625, 49.820068359375, 71.39990234375, 98.56005859375, 76.89990234375, 32.590087890625, 35.27001953125, 53.35009765625, 97.0400390625, 99.91015625, 60.840087890625, 73.7998046875]], 'AvantiHulkFc': ['https://s3.glbimg.com/v1/AUTH_58d78b787ec34892b5aaa0c7a146155f/cartola_svg_187/escudo/26/39/19/003ff8b4c5-2857-40eb-a767-cd493d41332620210518093919', [82.259765625, 69.1201171875, 48.179931640625, 51.010009765625, 50.60009765625, 90.919921875, 77.93017578125, 79.97998046875, 46.14990234375, 76.22998046875, 46.43994140625, 80.83984375, 88.83984375, 59.699951171875, 46.070068359375, 85.419921875, 30.0699462890625, 90.66015625, 72.52001953125, 84.33984375, 79.169921875]], 'Gonella Verde ': ['https://s3.glbimg.com/v1/AUTH_58d78b787ec34892b5aaa0c7a146155f/cartola_svg_202/escudo/1f/15/07/003d74c959-552d-4913-9722-99905131fe1f20220405171507', [93.35009765625, 87.16015625, 57.18994140625, 69.009765625, 50.97998046875, 116.72021484375, 80.77978515625, 76.990234375, 36.550048828125, 112.4599609375, 57.969970703125, 111.10009765625, 98.14013671875, 78.2001953125, 61.169921875, 92.4501953125, 63.77001953125, 96.64013671875, 92.2099609375, 90.5400390625, 75.3701171875]], 'Xanpion': ['https://s3.glbimg.com/v1/AUTH_58d78b787ec34892b5aaa0c7a146155f/cartola_svg_183/escudo/4a/27/40/00a3e45e44-1721-4be8-97f7-356569aefd4a20210427182740', [95.9501953125, 95.33984375, 49.8798828125, 60.7099609375, 48.110107421875, 88.7001953125, 87.7900390625, 66.77978515625, 38.75, 100.35986328125, 47.85009765625, 98.3701171875, 86.43994140625, 83.0498046875, 56.27001953125, 71.919921875, 63.8701171875, 112.14013671875, 100.91015625, 84.97998046875, 73.4501953125]], 'Sóh Taapa FC': ['https://s3.glbimg.com/v1/AUTH_58d78b787ec34892b5aaa0c7a146155f/cartola_svg_200/escudo/5d/09/28/00ede8fe0a-584f-4bad-9e46-7be85b23a75d20220318150928', [98.85009765625, 79.9599609375, 45.85009765625, 54.409912109375, 44.909912109375, 95.31982421875, 90.8798828125, 70.7099609375, 17.949951171875, 117.85986328125, 52.280029296875, 68.77001953125, 84.93994140625, 84, 67.06982421875, 103.6201171875, 71.3701171875, 111.0400390625, 105.39013671875, 82.64013671875, 77.97021484375]], 'RIVA 77 ': ['https://s3.glbimg.com/v1/AUTH_58d78b787ec34892b5aaa0c7a146155f/cartola_svg_190/escudo/77/16/19/00343ae962-b9ba-4a9e-b60b-98e185482d7720210528221619', [86.14990234375, 68.16015625, 54.090087890625, 61.949951171875, 50.18994140625, 89.7099609375, 102.39013671875, 85.18994140625, 40.75, 81.16015625, 55.409912109375, 113.06982421875, 85.9501953125, 80.5, 62.780029296875, 85.919921875, 70.27001953125, 91.0400390625, 88.7099609375, 51.489990234375, 57.949951171875]]}
# dict_keys = list(dict_teste.keys())
# for c, v in dict_nome_escudo_pontos.items():
#     for i in range(0, len(dict_teste)):
#         if c == dict_keys[i]:
#             dict_teste[dict_keys[i]][1].append(v)
# print(dict_teste)


