from transformers import M2M100ForConditionalGeneration, M2M100Tokenizer
import torch
import time

# Configurar dispositivo (GPU si está disponible, CPU en caso contrario)
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
print(f"Usando dispositivo: {device}")

# Textos de ejemplo más complejos
english_text = "The intricate patterns of technological innovation often reflect deeper societal changes, challenging our understanding of progress and human interaction in the digital age."
spanish_text = "Las complejas estructuras de los ecosistemas naturales nos recuerdan la fragilidad del equilibrio ambiental y la importancia de preservar la biodiversidad para las generaciones futuras."

# Cargar el modelo y el tokenizador
print("Cargando modelo...")
start_time = time.time()
model = M2M100ForConditionalGeneration.from_pretrained("facebook/m2m100_418M")
model = model.to(device)  # Mover el modelo a GPU
tokenizer = M2M100Tokenizer.from_pretrained("facebook/m2m100_418M")
load_time = time.time() - start_time
print(f"Modelo cargado en {load_time:.2f} segundos")

# Traducir de inglés a chino
print("\nTraduciendo de inglés a chino...")
start_time = time.time()
tokenizer.src_lang = "en"
encoded_en = tokenizer(english_text, return_tensors="pt").to(device)  # Mover tensores a GPU
generated_tokens = model.generate(**encoded_en, forced_bos_token_id=tokenizer.get_lang_id("zh"))
chinese_translation = tokenizer.batch_decode(generated_tokens, skip_special_tokens=True)[0]
translation_time = time.time() - start_time
print(f"Traducción completada en {translation_time:.2f} segundos")

print("Inglés a Chino:")
print(f"Original: {english_text}")
print(f"Traducción: {chinese_translation}")
print("-" * 80)

# Traducir de español a inglés
print("\nTraduciendo de español a inglés...")
start_time = time.time()
tokenizer.src_lang = "es"
encoded_es = tokenizer(spanish_text, return_tensors="pt").to(device)  # Mover tensores a GPU
generated_tokens = model.generate(**encoded_es, forced_bos_token_id=tokenizer.get_lang_id("en"))
english_translation = tokenizer.batch_decode(generated_tokens, skip_special_tokens=True)[0]
translation_time = time.time() - start_time
print(f"Traducción completada en {translation_time:.2f} segundos")

print("Español a Inglés:")
print(f"Original: {spanish_text}")
print(f"Traducción: {english_translation}")