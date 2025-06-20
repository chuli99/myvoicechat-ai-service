import subprocess

COMANDO = [
    "f5-tts_infer-cli",
    "--model", "F5TTS_Spanish",
    "--ref_audio", "audios/audioStefano.mp3",
    "--ref_text", "Mientras más corto es el audio, el modelo es mejor.",
    "--gen_text", "Boca sos lo mas grande del multiverso.",
]

resultado = subprocess.run(COMANDO, capture_output=True, text=True)
print("STDOUT:", resultado.stdout)
print("STDERR:", resultado.stderr)