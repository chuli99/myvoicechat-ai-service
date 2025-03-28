import subprocess

COMANDO = [
    "f5-tts_infer-cli",
    "--model", "F5TTS_v1_Base",
    "--ref_audio", "audios/audioJulian.ogg",
    "--ref_text", "Mientras mas corto es el audio, el modelo es mejor.",
    "--gen_text", "Me and the devil. Walking side by side. And, though I have grown serene And strong since then, I think that God has willed A still renewable fear…"
]
#ref_text: Transcripción del audio de referencia
#gen_text: Texto a sintetizar con la voz clonada
resultado = subprocess.run(COMANDO, capture_output=True, text=True)
print(resultado.stdout)

