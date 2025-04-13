import subprocess

COMANDO = [
    "f5-tts_infer-cli",
    "--model", "F5TTS_v1_Base",
    "--ref_audio", "audios/audioStefano.mp3",
    "--ref_text", "Mientras más corto es el audio, el modelo es mejor.",
    "--gen_text", "Dealing with family secrets is never easy. Yet, sometimes, omission is a form of protection, intending to safeguard some from the harsh truths. One day, I hope you understand the reasons behind my actions. Until then, Anna, please, bear with me.",
]

resultado = subprocess.run(COMANDO, capture_output=True, text=True)
print("STDOUT:", resultado.stdout)
print("STDERR:", resultado.stderr)
