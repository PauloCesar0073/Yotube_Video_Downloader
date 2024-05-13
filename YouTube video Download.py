#-*-coding:utf8;-*-
#qpy:console
import qpy
import androidhelper
import requests
import re
try:
    import urllib.request as ur
except:
    import urllib as ur
from qsl4ahelper.fullscreenwrapper2 import *

droid = androidhelper.Android()

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

class MainScreen(Layout):
    def __init__(self):
        super(MainScreen, self).__init__(str("""<?xml version="1.0" encoding="utf-8"?>
<LinearLayout
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    android:background="#ff000000"
    android:orientation="vertical"
    xmlns:android="http://schemas.android.com/apk/res/android">
    
    <ImageView
        android:id="@+id/logo"
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:src="@drawable/youtube_logo"
        android:scaleType="centerInside"
        android:adjustViewBounds="true"
        android:layout_marginStart="16dp"
        android:layout_marginEnd="16dp"
        android:layout_marginTop="32dp"
        android:layout_marginBottom="16dp"/>

    <LinearLayout
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:orientation="horizontal"
        android:layout_marginStart="16dp"
        android:layout_marginEnd="16dp"
        android:layout_marginTop="16dp"> <!-- Movido para cima -->

        <TextView
            android:layout_width="0dp"
            android:layout_height="wrap_content"
            android:layout_weight="1"
            android:textSize="14px"
            android:text="Digite a URL do Vídeo:"
            android:textColor="#ffffffff"
            android:gravity="center_vertical"/>

        <EditText
            android:id="@+id/url_input"
            android:layout_width="0dp"
            android:layout_height="wrap_content"
            android:layout_weight="2"
            android:hint="Insira a URL aqui"
            android:textColorHint="#80ffffff"
            android:textColor="#ffffffff"/>
    </LinearLayout>

    <TextView
        android:id="@+id/video_title"
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:textSize="16sp"
        android:textColor="#ffffffff"
        android:gravity="center"
        android:paddingStart="16dp"
        android:paddingEnd="16dp"
        android:paddingBottom="16dp"/>

    <ListView
        android:id="@+id/data_list"
        android:layout_width="match_parent"
        android:layout_height="0dp"
        android:layout_weight="1"
        android:background="#ff000000"/>

    <LinearLayout
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:orientation="horizontal"
        android:layout_marginTop="16dp"> <!-- Movido para cima -->

        <Button
            android:layout_width="0dp"
            android:layout_height="wrap_content"
            android:text="Download"
            android:id="@+id/but_download"
            android:textSize="9px"
            android:background="#ffcc0000"
            android:textColor="#ffffffff"
            android:layout_weight="1"
            android:layout_margin="8dp"/>

        <Button
            android:layout_width="0dp"
            android:layout_height="wrap_content"
            android:text="Exit"
            android:id="@+id/but_exit"
            android:textSize="9px"
            android:background="#60bdb600"
            android:textColor="#ffffffff"
            android:layout_weight="1"
            android:layout_margin="8dp"/>
    </LinearLayout>
</LinearLayout>
"""), "Youtube Downloader")
    def download_video(self, uri, title):
        try:
            # Solicitar permissão de escrita em tempo de execução
            #request_permission(Permission.WRITE_EXTERNAL_STORAGE)
    
            response = requests.get(uri, stream=True)
            block_size = 1024  # Tamanho dos blocos de leitura do stream (1 KB)
    
            # Diretório de armazenamento externo do aplicativo
            download_dir = os.path.join(os.getenv('EXTERNAL_STORAGE'), 'Download')
           
            # Cria o diretório de salvamento se não existir
            if not os.path.exists(download_dir):
              os.makedirs(download_dir)
            # Nome do arquivo substituindo caracteres inválidos por '_'
            file_path = os.path.join(download_dir, f'{title}.mp4')
    
            # Barra de progresso com mensagem de progresso
            downloaded_size = 0
            with open(file_path, 'wb') as f:
                for data in response.iter_content(block_size):
                    downloaded_size += len(data)
                    f.write(data)
            
            # Mostra uma mensagem de conclusão após o download
            self.views.video_title.text = f'\n\n\nVídeo Foi Baixado Com Sucesso!'
            droid.makeToast("Vídeo baixado com sucesso.")    
          
            return True
    
        except requests.RequestException as e:
            droid.makeToast(f"Ocorreu um erro ao baixar o vídeo: {e}") #- mesma observação aqui
            return FalseFalse
    
    def on_show(self):
        self.views.but_exit.add_event(click_EventHandler(self.views.but_exit, self.exit))
        self.views.but_download.add_event(click_EventHandler(self.views.but_download, self.download))

    def on_close(self):
        pass
    def exit(self, view, dummy):
        droid = FullScreenWrapper2App.get_android_instance()
        droid.makeToast("Exit")
        FullScreenWrapper2App.close_layout()

    def download(self, view, dummy):
        url_input = self.views.url_input.text.strip()

        if not url_input:
            droid = FullScreenWrapper2App.get_android_instance()
            droid.makeToast("Por favor, insira uma URL.")
            return

        try:
            dados = youtube_parse(url_input)
            if dados:
                self.views.video_title.text = f'\n\n\nBaixando....'
                self.download_video(dados["uri"], dados["title"])

            else:
                droid = FullScreenWrapper2App.get_android_instance()
                droid.makeToast("URL inválida ou vídeo não encontrado.")
        except Exception as e:
            droid = FullScreenWrapper2App.get_android_instance()
            droid.makeToast("Erro ao verificar a URL: {}".format(str(e)))

if __name__ == '__main__':
    FullScreenWrapper2App.initialize(droid)
    FullScreenWrapper2App.show_layout(MainScreen())
    FullScreenWrapper2App.eventloop()