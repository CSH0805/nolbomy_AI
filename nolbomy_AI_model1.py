import os
import pyaudio
import datetime
import time
from google.cloud import speech

# ── 🔑 Google STT 설정 ──────────────────────────────
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = r"C:\Users\wwwe7\Desktop\nolbomy_AI\curious-arch-447209-j4-1bd9c946b299.json"

# ── 오디오(STT) 설정 ────────────────────────────────
RATE  = 16000
CHUNK = int(RATE / 10)  # 100ms

# ── STT 클라이언트 초기화 ────────────────────────────
client = speech.SpeechClient()
streaming_config = speech.StreamingRecognitionConfig(
    config=speech.RecognitionConfig(
        encoding          = speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz = RATE,
        language_code     = "ko-KR",
    ),
    interim_results=False
)

def mic_stream():
    """마이크 오디오 스트림 생성기"""
    p = pyaudio.PyAudio()
    stream = p.open(
        format=pyaudio.paInt16,
        channels=1,
        rate=RATE,
        input=True,
        frames_per_buffer=CHUNK
    )
    print("🎤 음성 듣는 중... (Ctrl+C로 종료)")
    while True:
        chunk = stream.read(CHUNK)
        yield speech.StreamingRecognizeRequest(audio_content=chunk)

def detect_keyword(text: str) -> bool:
    """긴급 키워드 감지"""
    kws = [
        "도와줘", "도 와줘", "도와 줘",
        "살 려 줘", "살 려줘", "살려 줘",
        "살려주세요", "살 려주세요", "살려 주세요",
        "살려주 세요", "살려주세 요", "살 려 주 세 요",
        "사람 살려"
    ]
    return any(k in text for k in kws)

def listen_and_detect():
    """STT + 키워드 감지 → print만"""
    try:
        requests_stream = mic_stream()
        responses = client.streaming_recognize(streaming_config, requests_stream)

        for response in responses:
            for result in response.results:
                if not result.is_final:
                    continue

                transcript = result.alternatives[0].transcript.strip()
                now = datetime.datetime.now().isoformat()
                print(f"🗣️ [{now}] 인식된 문장: {transcript}")

                if detect_keyword(transcript):
                    print("🚨 긴급 키워드 감지! SMS 전송 중...")  # SMS 안보내고 print만
    except Exception as e:
        print(f"❌ 음성 감지 중 오류: {e}")
        # 여기서 에러가 터져도 main에서 다시 실행

if __name__ == "__main__":
    print("🚀 STT 음성 키워드 감지 프로그램 시작!")
    while True:
        try:
            listen_and_detect()
        except Exception as e:
            print(f"❌ listen_and_detect()에서 예외 발생: {e}")
            print("🔄 3초 후 STT 재연결...")
            time.sleep(3)
