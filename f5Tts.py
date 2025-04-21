import subprocess

COMANDO = [
    "f5-tts_infer-cli",
    "--model", "F5TTS_v1_Base",
    "--ref_audio", "audios/audioStefano.mp3",
    "--ref_text", "Mientras más corto es el audio, el modelo es mejor.",
    "--gen_text", "这是一种策略，也是一种智慧。万变不离其宗，只要你把握住当前的游戏规则，就能玩转整个局势。“记住，预知敌情，了解自己，方能成就一番伟业。”我认真地对你说，希望你能明白这个道理。",
]

resultado = subprocess.run(COMANDO, capture_output=True, text=True)
print("STDOUT:", resultado.stdout)
print("STDERR:", resultado.stderr)