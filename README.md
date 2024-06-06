# Yotube_Video_Downloader
Baixe vídeos do YouTube em seu celular,apenas usando o interpretador python QPython que pode ser obtido na play store.




#modo de uso 

instale o [QPython](https://play.google.com/store/apps/details?id=org.qpython.qpy) , após instalar abra a página de projetos,e clique em add.
<br>
# instalação das bibliotecas 
abra `QPYPI` , `PIP CLIENT` , irá abrir um terminal de instalação das libs python usando o `pip`.
cole este código e execute.
```
pip install requests
pip install pytube
```
# Criar Novo projeto no QPython e colar o código abaixo;
<br>
copie e cole este código no seu QPython.

```

"""
---------------------------------------------------------
Autor  : PauloCesar0073
Licença: MINT
versão  :1.0.3
Descrição:
Este aplicativo baixa vídeos do YouTube a partir de um link fornecido pelo usuário.

Funcionalidades:
- Solicita permissões necessárias para acessar a internet e escrever no armazenamento externo.
- Lê a URL do vídeo do YouTube fornecida pelo usuário.
- Obtém o link de streaming do vídeo.
- Faz o download do vídeo e salva na pasta Download do dispositivo.
- Exibe notificações e mensagens de progresso durante o download.
- baixa tanto playlists quanto videos individuais 
Dependências:
- Conexão com a Internet.
- Bibliotecas do Python: os, 
androidhelper,
 requests, re, qpy,ssl, urllib,pytube

Como usar:
1. Abra o YouTube, clique em compartilhar e copie o link do vídeo.
2. Abra o aplicativo, cole o link no campo de entrada e clique em "Baixar".
3. Aguarde o download finalizar. Os vídeos são salvos na pasta Download.
---------------------------------------------------------
"""
import qpy
import androidhelper
import requests
import re
from pytube import Playlist 
import os
import ssl
import sys
# Criar um contexto SSL sem verificação
ssl._create_default_https_context = ssl._create_unverified_context

try:
    import urllib.request as ur
except:
    import urllib as ur
from qsl4ahelper.fullscreenwrapper2 import *

droid = androidhelper.Android()


# Lista de permissões necessárias
permissions = [
    "android.permission.WRITE_EXTERNAL_STORAGE",
    
    "android.permission.INTERNET"
    
    
]
droid.requestPermissions(permissions)






####CONTANTS
YOUTUBE_URL_PATTERN = r'(?:youtube\.com\/(?:[^\/\n\s]+\/\S+\/|(?:v|e(?:mbed)?)\/|\S*?[?&]v=)|youtu\.be\/)([a-zA-Z0-9_-]{11})'
YOUTUBE_PLAYER_ENDPOINT = "https://www.youtube.com/youtubei/v1/player"
YOUTUBE_PLAYER_KEY = "AIzaSyAO_FJ2SlqU8Q4STEHLGCilw_Y9_11qcW8"
YOUTUBE_CLIENT_VERSION = "17.43.36"
YOUTUBE_CLIENT_USER_AGENT = f"com.google.android.youtube/{YOUTUBE_CLIENT_VERSION} (Linux; U; Android 13)"
YOUTUBE_PLAYER_HEADERS = {
    "X-Youtube-Client-Name": "3",
    "X-Youtube-Client-Version": YOUTUBE_CLIENT_VERSION,
    "Origin": "https://www.youtube.com",
    "Content-Type": "application/json",
    "User-Agent": YOUTUBE_CLIENT_USER_AGENT
}


def youtube_parse(url):
    url = obter_id_youtube(url)
    video_id = url.split("/")[-1]

    headers = YOUTUBE_PLAYER_HEADERS.copy()
    headers["Referer"] = url

    params = {
        "token": YOUTUBE_PLAYER_KEY,
        "prettyPrint": "false"
    }

    payload = {
        "context": {
            "client": {
                "clientName": "ANDROID",
                "clientVersion": YOUTUBE_CLIENT_VERSION,
                "androidSdkVersion": 33,
                "userAgent": YOUTUBE_CLIENT_USER_AGENT,
                "hl": "en",
                "timeZone": "UTC",
                "utcOffsetMinutes": 0
            }
        },
        "playbackContext": {
            "contentPlaybackContext": {
                "html5Preference": "HTML5_PREF_WANTS"
            }
        },
        "videoId": video_id
    }

    try:
        response = requests.post(YOUTUBE_PLAYER_ENDPOINT, 
        	headers=headers, params=params, json=payload,
        	verify=False)
        response.raise_for_status()
        data = response.json()

        playability_status = data.get("playabilityStatus", {})
        if playability_status.get("status") != "OK":
            return None

        streaming_data = data.get("streamingData", {})
        formats = streaming_data.get("formats", [])

        best_format = max(formats, key=lambda x: x.get("itag", 0))
        stream_uri = best_format.get("url",0)
        
        video_details = data.get("videoDetails", {})
        title = video_details.get("title", "")
        
        return {
            "video_id": video_id,
            "title": title,
            "uri": stream_uri
        }
    except Exception as e:
        print(f"Error parsing YouTube video: {e}")
        return None
def removeTags(uri):
    # Define a expressão regular para encontrar a tag '&t=' seguida por qualquer coisa até o final da string
    regex = r'&t=.*$'

    # Use re.sub para substituir a correspondência da expressão regular por uma string vazia
    cleaned_url = re.sub(regex, '', uri)
    if cleaned_url:
        return cleaned_url
    else:
        return uri
        
        
def obter_uris(video_id):
  video_info = youtube_parse(video_id)
  return video_info

def get_content_length(uri):
  
  
    try:
        response = requests.head(uri)  # Faz uma requisição HEAD para obter os metadados sem baixar o arquivo
        content_length = int(response.headers.get('content-length', False))  # Tamanho total do arquivo em bytes
        return content_length
    except requests.RequestException as e:
        print(f"Ocorreu um erro ao obter o tamanho do arquivo de {uri}: {e}")
        return False
        
        
        
        
        

def obter_id_youtube(url):
    """
    Obtém o ID do vídeo do YouTube a partir de uma URL.

    :param url: URL do vídeo do YouTube.
    :return: ID do vídeo do YouTube, ou None se não for possível extrair o ID.
    """
    # Expressão regular para capturar o ID do vídeo em diferentes tipos de URLs do YouTube
    regex = (
        r'(?:youtube\.com\/(?:[^\/\n\s]+\/\S+\/|(?:v|e(?:mbed)?)\/|\S*?[?&]v=|live\/|shorts\/)?|youtu\.be\/)'
        r'([a-zA-Z0-9_-]{11})'  # Captura o ID do vídeo (11 caracteres alfanuméricos)
    )

    # Use re.search para encontrar o padrão na URL fornecida
    match = re.search(regex, url)

    if match:
        video_id = match.group(1)  # Captura o ID do vídeo

        # Verifica se é uma URL de vídeo regular, transmissão ao vivo ou vídeo curto (shorts)
        if 'live/' in url:
            return f"https://www.youtube.com/live/{video_id}"
        elif 'shorts/' in url:
            return f"https://www.youtube.com/shorts/{video_id}"
        else:
            return f"https://www.youtube.com/embed/{video_id}"
    else:
        return None  # Retorna None se não encontrar correspondência

def remover_caracteres_invalidos(nome):
    # Lista de caracteres inválidos para nomes de arquivos
    caracteres_invalidos = r'[<>:"/\\|?*]'
    # Substitui os caracteres inválidos por um caractere de espaço em branco
    nome_limpo = re.sub(caracteres_invalidos, ' ', nome)

    return nome_limpo
    
    
def porcentagem_download(tamanho_baixado, tamanho_total):
    porcentagem = (tamanho_baixado / tamanho_total) * 100
    return porcentagem
        
class MainScreen(Layout):
    def __init__(self):
        super(MainScreen, self).__init__(str("""<?xml version="1.0" encoding="utf-8"?>
<LinearLayout
    xmlns:android="http://schemas.android.com/apk/res/android"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    android:background="#e0e0e0"
    android:orientation="vertical">
    <Space
            android:layout_width="16dp"
            android:layout_height="wrap_content"/>


    <!-- Entrada de URL -->
    <LinearLayout
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:orientation="horizontal"
        android:gravity="center_vertical"
        android:padding="16px">
       

        <TextView
            android:layout_width="wrap_content"
            android:layout_height="wrap_content"
            android:textSize="13px"
            android:text="Digite a URL do Vídeo/Playlist:"
            android:textColor="#212121"/>

        <EditText
            android:id="@+id/url_input"
            android:layout_width="0dp"
            android:layout_height="wrap_content"
            android:layout_weight="1"
            android:hint="  ➡️ URL AQUI ⬅️"
            android:textColorHint="#757575"
            android:textColor="#212121"
            android:textSize="13px"
            android:background="#e0e0e0"/>
    </LinearLayout>

    <!-- Vídeos Salvos -->
    <TextView
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:textSize="13px"
        android:text="Vídeos Salvos na pasta Download"
        android:textColor="#415d01"
        android:gravity="center_vertical"
        android:padding="16px"/>

    <!-- Título do vídeo e progresso do download -->
    <LinearLayout
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:orientation="horizontal"
        android:padding="16px"
        android:background="#e0e0e0">

        <TextView
            android:id="@+id/video_title"
            android:layout_width="0dp"
            android:layout_height="wrap_content"
            android:layout_weight="1"
            android:textSize="13px"
            android:textColor="#212121"
            android:padding="9px"/>
    </LinearLayout>

    <!-- Botões -->
    <LinearLayout
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:orientation="horizontal"
        android:padding="16px"
        android:background="#e0e0e0">

        <Button
            android:id="@+id/but_exit"
            android:layout_width="0dp"
            android:layout_height="wrap_content"
            android:layout_weight="1"
            android:text="Sair❌️"
            android:textSize="20px"
            android:background="#56ccf2"
            android:textColor="#ffffff"/>

        <Space
            android:layout_width="20dp"
            android:layout_height="wrap_content"/>

        <Button
            android:id="@+id/but_download"
            android:layout_width="0dp"
            android:layout_height="wrap_content"
            android:layout_weight="1"
            android:text="Baixar✅️"
            android:textSize="20px"
            android:background="#317212"
            android:textColor="#ffffff"/>
    </LinearLayout>

    <!-- Footer -->
    <LinearLayout
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:orientation="vertical"
        android:padding="16px"
        android:background="#ffffff"
        android:layout_gravity="bottom">

       <Button
    android:id="@+id/but_visit_site"
    android:layout_width="wrap_content"
    android:layout_height="wrap_content"
    android:text="Desenvolvido por PauloCesar0073©️"
    android:textSize="9px"
    android:textColor="#187771"
    android:background="@android:color/transparent"
    android:padding="10px"
    android:textAllCaps="false"
    android:textStyle="normal"/>
      <TextView
            android:layout_width="match_parent"
            android:layout_height="wrap_content"
            android:textSize="12px"
            android:text="Atenção! compartilhar os vídeos baixados estará a correr riscos , de responder legalmente por direitos autorais"
            android:textColor="#d20000"
            android:padding="3px"/>

        <TextView
            android:layout_width="match_parent"
            android:layout_height="wrap_content"
            android:textSize="9px"
            android:text="Versão 1.0.3"
            android:textColor="#212121"
            android:gravity="center_vertical"
            android:padding="16px"/>

        <TextView
            android:layout_width="match_parent"
            android:layout_height="wrap_content"
            android:textSize="13px"
            android:text="Funcionalidades atuais:"
            android:textColor="#212121"
            android:padding="3px"/>
             <TextView
            android:layout_width="match_parent"
            android:layout_height="wrap_content"
            android:textSize="13px"
            android:textColor="#212121"
            android:paddingStart="16px"
            android:paddingEnd="16px"
            android:paddingBottom="8px"
            android:text=""/>

        <TextView
            android:layout_width="match_parent"
            android:layout_height="wrap_content"
            android:textSize="13px"
            android:textColor="#212121"
            android:paddingStart="16px"
            android:paddingEnd="16px"
            android:paddingBottom="8px"
            android:text="• Download de Shorts😱"/>
           <TextView
            android:layout_width="match_parent"
            android:layout_height="wrap_content"
            android:textSize="13px"
            android:textColor="#212121"
            android:paddingStart="16px"
            android:paddingEnd="16px"
            android:paddingBottom="8px"
            android:text="• Download de Vídeos Individuais😱"/>
   
   
   
    <TextView
            android:layout_width="match_parent"
            android:layout_height="wrap_content"
            android:textSize="13px"
            android:textColor="#212121"
            android:paddingStart="16px"
            android:paddingEnd="16px"
            android:paddingBottom="8px"
            android:text="• Suporte a download de playlists 😱"/>
  <TextView
            android:layout_width="match_parent"
            android:layout_height="wrap_content"
            android:textSize="13px"
            android:textColor="#212121"
            android:paddingStart="16px"
            android:paddingEnd="16px"
            android:paddingBottom="8px"
            android:text="• Resolução de até 4k 😱"/>
    <TextView
            android:layout_width="match_parent"
            android:layout_height="wrap_content"
            android:textSize="13px"
            android:textColor="#212121"
            android:paddingStart="16px"
            android:paddingEnd="16px"
            android:paddingBottom="8px"
            android:text="• Formato de saída MP4 😱"/>
   
   
    </LinearLayout>
</LinearLayout>
"""), "Youtube Downloader")
    def download_video(self, uri, title, tamanho, index, total_videos, tp):
        # Diretório de armazenamento externo do aplicativo
        download_dir = os.path.join(os.getenv('EXTERNAL_STORAGE'), 'Download')
        
        # Cria o diretório de salvamento se não existir
        if not os.path.exists(download_dir):
            os.makedirs(download_dir)
            
        # Nome do arquivo substituindo caracteres inválidos por '_'
        file_path = os.path.join(download_dir, f'{remover_caracteres_invalidos(title)}.mp4')
        
        # Verifica se o arquivo já existe
        if os.path.exists(file_path):
            self.views.video_title.text = f"O vídeo {title} já existe!"
            droid.makeToast("O vídeo já existe.")
            return True
        
        # Solicitar permissão de escrita em tempo de execução
        # request_permission(Permission.WRITE_EXTERNAL_STORAGE) 
        response = requests.get(uri, stream=True)
        block_size = 1024  # Tamanho dos blocos de leitura do stream (1 KB)
        
        # Barra de progresso com mensagem de progresso
        downloaded_size = 0
        self.views.url_input.text = ""
        
        with open(file_path, 'wb') as f:
            for data in response.iter_content(block_size):
                downloaded_size += len(data)
                f.write(data)
                
                if index and tp == 1:
                    self.views.video_title.text = f"\nBaixando: {title}.mp4\n\nProgresso: {porcentagem_download(int(downloaded_size), tamanho):.0f}%   ({downloaded_size / (1024 * 1024):.2f} MB/{tamanho / (1024 * 1024):.2f} MB)"
                    
                if index and tp == 2:
                    self.views.video_title.text = f"\nBaixando O Vídeo {index} de {total_videos} Vídeos Da Playlist\n\nTítulo Do Vídeo: {title}.mp4\n\nProgresso: {porcentagem_download(int(downloaded_size), tamanho):.0f}%   ({downloaded_size / (1024 * 1024):.2f} MB/{tamanho / (1024 * 1024):.2f} MB)"
                    
        # Mostra uma mensagem de conclusão após o download
        self.views.video_title.text = f'\n\n\nVídeo Foi Baixado Com Sucesso!'
        
        # Define o título e a mensagem da notificação
        title1 = "Vídeo Baixado com sucesso!"
        message = f"{title}.mp4"
        
        # Exibe a notificação com título, mensagem e URI do vídeo
        droid.notify(title1, message, title)
        droid.makeToast("Vídeo baixado com sucesso.")
        
        return True


    def baixar_playlist(self, link):
        diretorio = os.path.join(os.getenv('EXTERNAL_STORAGE'), 'Download')
        playlist = Playlist(link)
        total_videos = len(playlist.video_urls)
    
        if not os.path.exists(diretorio):
            os.makedirs(diretorio)
    
        for index, video_url in enumerate(playlist.video_urls, start=1):
            try:
                while True:
                    idd = obter_id_youtube(video_url)
                    data = obter_uris(idd)
                    tamanho = get_content_length(data["uri"])
                    dados = youtube_parse(video_url)
                    
                    if isinstance(tamanho, int) and tamanho > 0 and dados:  # Verifica se tamanho é um número inteiro e positivo
                        
                        self.views.video_title.text = f'\n\n\nBaixando o vídeo {index}.{dados["title"]} da playlist🔁'
                        self.download_video(dados["uri"], remover_caracteres_invalidos(f'{index}.{dados["title"]}'), tamanho, index, total_videos, 2)  
                        break  # Sai do loop enquanto se os dados são válidos
                    else:
                        print("Tamanho inválido ou não encontrado, tentando novamente...")
                        continue
            except Exception as e:
                droid = FullScreenWrapper2App.get_android_instance()
                self.views.video_title.text = f"Ocorreu um erro {e}, tente novamente!"
                break
    def on_show(self):
        self.views.but_exit.add_event(click_EventHandler(self.views.but_exit, self.exit))
        self.views.but_download.add_event(click_EventHandler(self.views.but_download, self.download))
        self.views.but_visit_site.add_event(click_EventHandler(self.views.but_visit_site, self.visit_site))
        
    def exit(self, view, dummy):
        droid = FullScreenWrapper2App.get_android_instance()
        droid.makeToast("Exit")
        FullScreenWrapper2App.close_layout()

    def download(self, view, dummy):
        droid = androidhelper.Android()
        # Ocultar um elemento
        # Obter o ID do recurso da barra de progresso     
        droid.dialogCreateHorizontalProgress(title="ba",message="..",maximum_progress=100)
        #Exibir um elemento	
        #droid(R.id.progress, View.VISIBLE);

        url = self.views.url_input.text.strip()        
        
        if not url:
            droid = FullScreenWrapper2App.get_android_instance()
            droid.makeToast("Por favor, insira uma URL.")
            return

        try:
            if (url.startswith('https://www.youtube.com/watch?v=') or
                        url.startswith('https://youtu.be/') or
                        url.startswith('https://www.youtube.com') or
                        url.startswith('https://m.youtube.com') or
                        url.startswith('https://youtube.com/shorts/')):
                while True:
                
                    idd = obter_id_youtube(url)   
                    data = obter_uris(idd)
                    tamanho = get_content_length(data["uri"])
                    dados = youtube_parse(url)
     
                    
                    if isinstance(tamanho, int) and tamanho > 0 and dados:  # Verifica se tamanho é um número inteiro e positivo
                        
                      self.views.video_title.text = f'\n\n\nBaixando....'
                      p = self.download_video(dados["uri"], remover_caracteres_invalidos(dados["title"]),tamanho,1,1,1	)         
                      if p:
                          break
                    else:
                        print("Tamanho inválido ou não encontrado, tentando novamente...")
                        continue
            
            elif 'playlist' in url:
                self.baixar_playlist(url)
                
            else:
                droid = FullScreenWrapper2App.get_android_instance()
                droid.makeToast("URL inválida ou vídeo não encontrado.")
        except Exception as e:
            droid = FullScreenWrapper2App.get_android_instance()
            self.views.video_title.text = f"Ocorreu um erro tente novamente!"
            droid.makeToast("Erro ao verificar a URL: {}".format(str(e)))
    def visit_site(self, view, dummy):
        url = "https://github.com/PauloCesar0073"
        droid = FullScreenWrapper2App.get_android_instance()
        droid.startActivity('android.intent.action.VIEW',url)



if __name__ == '__main__':
    FullScreenWrapper2App.initialize(droid)
    FullScreenWrapper2App.show_layout(MainScreen())
    FullScreenWrapper2App.eventloop()


```
# veja os passos no vídeo abaixo
[![Assista ao vídeo](https://img.youtube.com/vi/5xKnsRBDtkc/0.jpg)](https://www.youtube.com/watch?v=5xKnsRBDtkc)
