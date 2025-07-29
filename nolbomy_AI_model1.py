import os
import pyaudio
from google.cloud import speech
import requests

# 🔑 Google Cloud STT 서비스 키 JSON 경로
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = r"C:\Users\wwwe7\Desktop\nolbomy_project_AItwo\nolbomy_AI\curious-arch-447209-j4-1bd9c946b299.json"

# 🎙️ 오디오 설정
RATE = 16000
CHUNK = int(RATE / 10)  # 100ms

client = speech.SpeechClient()

# 🎛️ STT 스트리밍 설정
streaming_config = speech.StreamingRecognitionConfig(
    config=speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=RATE,
        language_code="ko-KR",
    ),
    interim_results=False  # 중간 결과 무시
)

# 📡 MoceanAPI 설정 (✔️ API secret 추가됨)


from urllib.parse import urlencode

def send_sms(message):
    """MoceanAPI를 통해 SMS 전송 (디버깅 강화)"""
    url = "https://rest.moceanapi.com/rest/2/sms"
    params = {
        'mocean-api-key': MOCEAN_API_KEY,
        'mocean-api-secret': MOCEAN_API_SECRET,
        'mocean-from': '821077019623',  # 본인 번호로 변경 시도
        'mocean-to': RECEIVER_NUMBER,
        'mocean-text': message[:70]  # 메시지 길이 제한
    }

    print(f"🔍 전송 파라미터: {params}")
    
    encoded = urlencode(params)
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}

    response = requests.post(url, data=encoded, headers=headers)
    print(f"📊 응답 상태코드: {response.status_code}")
    print(f"📋 응답 내용: {response.text}")
    
    if response.status_code == 200:
        result = response.json()
        print("📨 SMS API 응답:", result)
        
        # MoceanAPI 응답 코드 확인
        if 'messages' in result:
            for msg in result['messages']:
                if msg.get('status') == '0':
                    print("✅ 메시지 전송 성공")
                else:
                    print(f"❌ 메시지 전송 실패: 상태코드 {msg.get('status')}, 오류: {msg.get('err-code')}")
    else:
        print("❌ HTTP 요청 실패:", response.text)

def mic_stream():
    """마이크에서 실시간 음성 수집"""
    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paInt16,
                    channels=1,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK)
    print("🎤 음성 듣는 중... (Ctrl+C로 종료)")

    while True:
        data = stream.read(CHUNK)
        yield speech.StreamingRecognizeRequest(audio_content=data)

def detect_keyword(transcript):
    """특정 키워드 포함 여부 확인"""
    keywords = [
        "도와줘", "도 와줘", "도와 줘",
        "살 려 줘", "살 려줘", "살려 줘",
        "살려주세요", "살 려주세요", "살려 주세요",
        "살려주 세요", "살려주세 요", "살 려 주 세 요",
        "사람 살려"
    ]
    return any(keyword in transcript for keyword in keywords)

def listen_and_detect():
    """실시간 STT 결과에서 키워드 감지 및 문자 전송"""
    requests_stream = mic_stream()
    responses = client.streaming_recognize(streaming_config, requests_stream)

    for response in responses:
        for result in response.results:
            if result.is_final:
                transcript = result.alternatives[0].transcript.strip()
                print(f"🎧 인식된 문장: {transcript}")

                if detect_keyword(transcript):
                    print("🚨 [긴급 키워드 감지]:", transcript)
                    sms_message = f"살려주세요 헤헿헤 다들 대머리 깍아라 헿"
                    send_sms(sms_message)
                else:
                    print("✅ 일반 음성, 무시함")

# 🟢 실행
if __name__ == "__main__":
    listen_and_detect()