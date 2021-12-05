# [Library Instance]
import kivy
import pandas as pd
import numpy as np
import math
import socket
import samsungctl
from kivy.lang import Builder
from plyer import gps
from kivy.app import App
from kivy.properties import StringProperty
from kivy.clock import mainthread
from kivy.utils import platform
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.properties import ObjectProperty

# [PeT Instance]
class PeT():
    # [Instance I] Definição das variáveis a serem utilizadas na classe PeT (Projeto em Telemática)
    '''
    lat = Latitude do usuário
    lng = Longitude do usuário
    dataset = Dataset utilizado pelo sistema
    duplicate_distances = Memória utilizada para armazenar canais com mais de uma localidade
    current_channel_and_angle = Memória pra o canal eo ângulo atual - Descartad
    '''
    def __init__(self):
        self.lat = None
        self.lng = None
        self.dataset = None
        self.duplicate_distances = {}
        # Formato Canal, Ângulo
        self.current_channel_and_angle = [None, None]
        self.address = None
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.config = {
                    "name": "samsungctl",
                    "description": "PC",
                    "id": "",
                    "host": "192.168.1.6",
                    "port": 55000,
                    "method": "legacy",
                    "timeout": 0,
                }

    # [Instance II] Definição do método get_location, responsável por obter a localização do dispositivo final do usuário
    '''
    Nesse exemplo se faz uso da biblioteca geocoder responsável por utilizar o IP do usuário para obter uma localidade aproximada.
    Nota importante: Localidade aproximada não é o objetivo do trabalho, e sim a localização exata a partir do GPS do dispositivo do usuário.
        Como esse código está em desenvolvimento, por questões de debug e funcionamento será considerado esse código.
    '''
    def set_location(self, lat, lng):
        self.lat, self.lng = float(lat), float(lng)

    # [Instance III] Definição do método set_dataset, responsável por fazer uso da definição do arquivo xml presente na documentação da ANATEL.
    '''
    Esse método recebia, anteriormente, o parâmetro database, porém uma vez que os cálculos serão fixos e constantes, não será necessário tal variação.
    '''
    def set_dataset(self):
        #cgpb = pd.read_csv('canais_cgepb.csv', decimal=',')
        cgpb = pd.DataFrame({'Canal':[3,7,9,11,13,19,23,40], 'Entidade':['TV Paraíba','TV Bandeirantes','TV Borborema','TV Maior','TV Correios','TV Itararé','Rede Vida','TV Arapuan'],
                             'Latitude':[-7.192571123978,-7.123883803736,-7.217070207424,-7.222914069005,-7.122831775000,-7.237743934188,-7.123883803736,-7.213289372426],
                             'Longitude':[-35.895872345969,-34.876077492192,-35.885146445421,-35.881199368674,-34.877917127244,-35.878669875343,-34.876077492192,-35.892873245577]})

        # Realizando o print do DataFrame
        self.dataset = cgpb

    # [Instance IV] Definição do método get_distance, responsável por calcular a distância aproximada entre dois pontos
    '''
    Essa função recebe dois argumentos, a latitude e a longitude do ponto da emissora. Esses cálculos serão feitos com base 
    na localizção calculada pela [Instance II]. Se é utilizado a biblioteca geopy.distance para realizar tais cálculos.
    '''
    #def get_distance(self,lat, lng):
        #return geopy.distance.geodesic((self.lat,self.lng), (lat, lng)).km

    # [Instance V] Definição do método get_bearingangle, responsável por calcular o ângulo entre dois pontos tomando o norte como referência
    '''
    Assim como a [Instance III], esse método faz uso da localização já armazenada do usuário na memória para em seguida calcular o ângulo entre os pontos.
    '''
    def get_bearingangle(self, lat, lng):
        dlng = (float(lng) - self.lng)
        x = math.cos(math.radians(float(lat))) * math.sin(math.radians(dlng))
        y = math.cos(math.radians(self.lat)) * math.sin(math.radians(float(lat))) - \
            math.sin(math.radians(self.lat)) * math.cos(math.radians(float(lat))) * math.cos(math.radians(dlng))
        brng = np.arctan2(x, y)
        return np.degrees(brng)

    # [Instance VI] Definição do método seach_duplicates, responsável por fazer a leitura do dataset para ver se existe algum canal com mais de uma localidade
    '''
    Esse método ele é bem simples, faz uma varredura do dataset procurando valores repetidos, armazena em um dicionário auxiliar para evitar processamentos posteirores,
    em casos do canal ser escolhido novamente, não ser feito o cálculo presente aqui de novo.
    '''
    def search_duplicates(self):
        # Criação da variável duplicates, que armazena os canais duplicados presentes no dataset
        duplicates = self.dataset[self.dataset['Entidade'].duplicated(keep=False) == True].sort_values('Entidade')

        # Criação do dicionário com base nos valore duplicados
        for value in duplicates["Entidade"].values:
            if value in self.duplicate_distances:
                self.duplicate_distances[value] = [self.duplicate_distances[value][0] + 1, self.duplicate_distances[value][1], self.duplicate_distances[value][2], self.duplicate_distances[value][3]]
            else:
                # Contador, Distância (que será um número grande pra ajudar na lógica), Lat, Lng
                self.duplicate_distances[value] = [1, 100, 0, 0]

        # Preenchimento dos dados no dicionário
        for value in duplicates.values:
            # value[0] é a chave do dicionário
            if self.duplicate_distances[value[0]][1] > self.get_distance(value[2], value[3]):
                self.duplicate_distances[value[0]][1] = self.get_distance(value[2], value[3])
                self.duplicate_distances[value[0]][2], self.duplicate_distances[value[0]][3] = value[2], value[3]

    # [Instance VII] Definição do método set_positioning, responsável por fazer o processametno dos dados de entrada com base no canal selecionado para fazer o posicionamento
    '''
    Como previsto na premissa do projeto, essa função faz o recebimento do canal selecionado no dispositivo final do usuário e faz o
    cálculo do ângulo a ser movimentado tomando como base os cálculos feitos abaixo.
    '''
    def set_positioning(self, channel):
        # Faz a coleta da linha que tem o canal selecionado
        row = self.dataset.loc[self.dataset['Canal'] == channel]
        # Pega o nome do canal selecionado (pra utilizar posteriormente)
        channel_name = [nome for nome in row.loc[row['Canal'] == channel]["Entidade"]][0]
        # Faz a leitura do nome no DF
        if channel_name in self.duplicate_distances:
            angle = self.get_bearingangle(self.duplicate_distances[channel_name][2],self.duplicate_distances[channel_name][3])
            self.current_channel_and_angle[0], self.current_channel_and_angle[1] = channel, angle
            # Retorna o ângulo para continuação do código
            return angle
        else:
            angle = self.get_bearingangle(float(row["Latitude"]), float(row["Longitude"]))
            self.current_channel_and_angle[0], self.current_channel_and_angle[1] = channel, angle
            # Retorna o ângulo para continuação do código
            return angle

    # [Instance VIII] Definição do método set_socket, responsável por estabelecer conexão entre os módulos
    '''
    Será definido, por questões de debug, um ip estático, mas conforme for sendo apliado o código, o mesmo será
    desenvolvido de forma com que o cliente aplique um broadcast UDP, em busca do servidor, para que assim consiga um retorno
    do ip para estabelecer uma conexão TCP.
    '''
    def set_socket(self):
        self.client_socket.connect(self.address)

    # [PeTdroid HUD Instance]
'''
Separação das telas do aplicativo
MainWindow - Tela principal
SecondWindow - Tela secundária
WindowManager - Tela de gerenciamento entre as telas
'''
class MainWindow(Screen):
    espip = ObjectProperty(None)
    tvip = ObjectProperty(None)

    def set_ip(self):
        # Setando o IP
        PCore.address = ((self.espip.text, 53530))
        # Setando o socket
        PCore.set_socket()
        # Setando o IP da TV no arquivo config do Samsungctl
        PCore.config["Host"] = self.tvip.text

        # Debug
        #print(PCore.address,PCore.config)

class SecondWindow(Screen):
    channel_list = ""

    # Método responsável por somar os valores selecionados pelo usuário para definir o canal
    def get_channel(self, channel):
        self.channel_list = self.channel_list + str(channel)

    # Método responsável por definir o canal selecionado
    '''
    Nesse método pretende-se iniciar o processo de aplicação do Socket, quando disponibilizado pelo ESP
    '''
    def set_channel(self):
        try:
            angle = str(PCore.set_positioning(int(self.channel_list)))
            self.channel_angle.text = (format(float(angle),".1f"))
            # Envia o ângulo para o ESP8299 [Módulo III]
            PCore.client_socket.sendall(str(np.floor(float(angle))).encode())
            # Criando a instância do controle remoto a partir das configurações presentes no objeto PeT()
            with samsungctl.Remote(PCore.config) as remote:
                tamanho_canal = len(self.channel_list)
                if tamanho_canal >= 2:
                    for numero in self.channel_list:
                        numero_canal = "KEY_" + numero
                        remote.control(numero_canal)
                else:
                    numero_canal = "KEY_" + self.channel_list
                    remote.control(numero_canal)
        except IndexError:
            self.channel_angle.text = "Canal não encontrado"
            pass
        self.channel_list = ""

    # Método estético para limpeza do ângulo printado
    def blank_menu(self):
        self.channel_angle.text = ""

class WindowManager(ScreenManager):
    pass

# Inicialização do arquivo da HUD definido em PeT_UI.kv
kv = Builder.load_file("PeT_UI.kv")

# [PeTdroid aplication Instance]
class MyApp(App):

    # Definição de variáveis que serão responsáveis por armazenar dados coletados pelo GPS
    gps_location = StringProperty()
    gps_status = StringProperty('Click Start to get GPS location updates')

    # [Instance I] Solicitação de permissões ao android
    '''
    Esse método, pré-estabelecido pelo exemplo do github [EGH], tem como intuito solicitar permissões ao android para
    acesso definitivo a variáveis importantes do sistema, como exemplo o GPS 
    '''
    def request_android_permissions(self):
        from android.permissions import request_permissions, Permission

        def callback(permissions, results):
            if all([res for res in results]):
                print("callback. All permissions granted.")
            else:
                print("callback. Some permissions refused.")

        request_permissions([Permission.ACCESS_COARSE_LOCATION,
                             Permission.ACCESS_FINE_LOCATION], callback)

    # [Instance II] Criação do núcleo/core do aplicativo [EGH]
    '''
    Esse método tem como intuito realizar um teste de verificação quanto ao dispositivo de acesso para em seguida
    seguir com o processo de coleta dos dados, definidos em gps.configure
    '''
    def build(self):
        try:
            gps.configure(on_location=self.on_location,
                          on_status=self.on_status)
        except NotImplementedError:
            import traceback
            traceback.print_exc()
            # Retorno, por exemplo, caso tente rodar no PC (windows, linux, etc)
            self.gps_status = 'GPS is not implemented for your platform'

        # Caso a plataforma seja um android, solicitar as permissões de acesso ao GPS
        if platform == "android":
            print("gps.py: Android detected. Requesting permissions")
            self.request_android_permissions()

        return kv

    # [Instance III] Definição dos métodos Start e Stop usados na leitura da localização
    '''
    Uma nota importante quanto a essa instância é que ela, uma vez invocada, não requer mais um rechamado, pois
    os dados da localização serão coletados inicialmente
    '''
    def start(self, minTime, minDistance):
        gps.start(minTime, minDistance)
    def stop(self):
        gps.stop()

    # [Instance IV] Definição dos métodos Location e Status, resposáveis por coletar informações ao GPS
    '''
    O método on_location coleta informações como latitude, longitude, altitude ou até mesmo precisão, porém
    só será utilizado nesse programa a lat e lng, definidas em 0 e 1 na lista latlng abaixo criada.
    
    O método on_status serve para, a partir do status mencionado acima (start e stop) retornar dados referentes 
    ao gps ativo.
    
    Ambos os métodos são definidos pelo [EGH + PET]
    '''
    @mainthread
    def on_location(self, **kwargs):
        count = 0
        latlng = []
        while count <= 1:
            for k, v in kwargs.items():
                # Depois setar os valores do código tomnando como base apenas o V, porque o K é a nomenclatura do valor
                self.gps_location = '\n'.join(['{}={}'.format(k, v)])
                latlng.append(v)
            count = count + 1
        # Definição da latitude e longitude objeto PeT
        PCore.set_location(latlng[0],latlng[1])
    @mainthread
    def on_status(self, stype, status):
        self.gps_status = 'type={}\n{}'.format(stype, status)

    # [Instance V] Métodos complementares a [Instance III]
    def on_pause(self):
        gps.stop()
        return True
    def on_resume(self):
        gps.start(1000, 0)
        pass

# [Inicialization Instance]
if __name__ == "__main__":
    # Inicialização do objeto PeT
    PCore = PeT()
    # Linha de coordenadas aleatórias - debug
    #PCore.set_location(-7.239837,-35.916125047)
    # Definição do data_set já definido
    PCore.set_dataset()
    # Inicialização do aplicativo
    MyApp().run()