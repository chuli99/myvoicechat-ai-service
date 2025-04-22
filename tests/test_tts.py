# load_test_tts.py
import time
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed

URL = "http://127.0.0.1:8000/tts/"
PAYLOAD = {
    "model": "F5TTS_v1_Base",
    "ref_audio_path": "audios/audioStefano.mp3",
    "ref_text": "Mientras más corto es el audio, el modelo es mejor.",
    "gen_text": "Perhaps they are driven by the delicious blend of flavors, or it could be the appealing visual presentation. At the end of the day, our choices in food reflect our personal preferences and sometimes, even our lifestyle or belief system.Perhaps they are driven by the delicious blend of flavors, or it could be the appealing visual presentation. At the end of the day, our choices in food reflect our personal preferences and sometimes, even our lifestyle or belief system.Perhaps they are driven by the delicious blend of flavors, or it could be the appealing visual presentation. At the end of the day, our choices in food reflect our personal preferences and sometimes, even our lifestyle or belief system.I was a closeted teenager in Catholic school when he was elected, and as he preached compassion over the years I felt like I could tangibly sense the people around me change their viewpoints on queerness. So many of my family members, including my godfather, changed their minds without knowing at the time that I was queer. I think it made me feel a lot more secure in my self when I did decide to start coming out a few years ago.I was a closeted teenager in Catholic school when he was elected, and as he preached compassion over the years I felt like I could tangibly sense the people around me change their viewpoints on queerness. So many of my family members, including my godfather, changed their minds without knowing at the time that I was queer. I think it made me feel a lot more secure in my self when I did decide to start coming out a few years ago."
}

def send_request(idx):
    start = time.time()
    resp = requests.post(URL, json=PAYLOAD)
    elapsed = time.time() - start
    return idx, resp.status_code, elapsed

def main(connections=5):
    print(f"Enviando {connections} peticiones concurrentes...")
    with ThreadPoolExecutor(max_workers=connections) as exe:
        futures = [exe.submit(send_request, i) for i in range(connections)]
        for f in as_completed(futures):
            idx, status, t = f.result()
            print(f"→ Request {idx}: status {status}, time {t:.2f}s")

if __name__ == "__main__":
    main(connections=10)