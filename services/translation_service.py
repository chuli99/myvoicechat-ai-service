import time
import torch
from transformers import M2M100ForConditionalGeneration, M2M100Tokenizer

# Modelo y tokenizador como variables globales para cargarlos solo una vez
_m2m100_model = None
_m2m100_tokenizer = None

def get_translation_model():
    global _m2m100_model, _m2m100_tokenizer
    
    if _m2m100_model is None or _m2m100_tokenizer is None:
        # Configurar dispositivo (GPU si está disponible, CPU en caso contrario)
        device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        print(f"Cargando modelo de traducción en dispositivo: {device}")
        
        # Cargar modelo y tokenizador
        _m2m100_model = M2M100ForConditionalGeneration.from_pretrained("facebook/m2m100_418M")
        _m2m100_model = _m2m100_model.to(device)
        _m2m100_tokenizer = M2M100Tokenizer.from_pretrained("facebook/m2m100_418M")
        
    return _m2m100_model, _m2m100_tokenizer, torch.device('cuda' if torch.cuda.is_available() else 'cpu')

def translate_text(request) -> dict:
    start_time = time.time()
    
    # Obtener texto y lenguajes
    text = request.text
    source_lang = request.source_lang
    target_lang = request.target_lang
    
    # Obtener modelo, tokenizador y dispositivo
    model, tokenizer, device = get_translation_model()
    
    # Configurar idioma de origen
    tokenizer.src_lang = source_lang
    
    # Codificar texto
    encoded_text = tokenizer(text, return_tensors="pt").to(device)
    
    # Generar traducción
    generated_tokens = model.generate(
        **encoded_text, 
        forced_bos_token_id=tokenizer.get_lang_id(target_lang)
    )
    
    # Decodificar traducción
    translated_text = tokenizer.batch_decode(generated_tokens, skip_special_tokens=True)[0]
    
    # Calcular tiempo de respuesta
    response_time = round(time.time() - start_time, 2)
    
    # Preparar respuesta
    return {
        "original_text": text,
        "translated_text": translated_text,
        "source_lang": source_lang,
        "target_lang": target_lang,
        "response_time": response_time
    }