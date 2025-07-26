import os
import pyaudio
from google.cloud import speech

# 🔑 Google Cloud STT 서비스 키 JSON 경로
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'curious-arch-447209-j4-1bd9c946b299.json'

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
    keywords = ["도와줘", "살려줘", "살려주세요"]
    return any(keyword in transcript for keyword in keywords)

def listen_and_detect():
    """실시간 STT 결과에서 키워드 감지"""
    requests = mic_stream()
    responses = client.streaming_recognize(streaming_config, requests)

    for response in responses:
        for result in response.results:
            if result.is_final:
                transcript = result.alternatives[0].transcript.strip()
                print(f"🎧 인식된 문장: {transcript}")

                if detect_keyword(transcript):
                    print("🚨 [긴급 키워드 감지]:", transcript)
                else:
                    print("✅ 일반 음성, 무시함")

# 🟢 실행
listen_and_detect()
