import time
import torch
from transformers import M2M100ForConditionalGeneration, M2M100Tokenizer

# Modelo y tokenizador como variables globales para cargarlos solo una vez
_m2m100_model = None
_m2m100_tokenizer = None
_is_preloaded = False  # Nueva bandera para indicar si el modelo fue precargado

def get_translation_model(force_load=False):
    global _m2m100_model, _m2m100_tokenizer, _is_preloaded
    
    # Si el modelo ya está cargado (ya sea por precarga o carga normal),
    # simplemente lo devolvemos sin recargarlo
    if (_m2m100_model is not None and _m2m100_tokenizer is not None) and not force_load:
        return _m2m100_model, _m2m100_tokenizer, torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    
    # Si llegamos aquí, necesitamos cargar el modelo
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"Cargando modelo de traducción en dispositivo: {device}")
    
    # Cargar modelo y tokenizador
    _m2m100_model = M2M100ForConditionalGeneration.from_pretrained("facebook/m2m100_418M")
    _m2m100_model = _m2m100_model.to(device)
    _m2m100_tokenizer = M2M100Tokenizer.from_pretrained("facebook/m2m100_418M")
    _is_preloaded = True
    
    return _m2m100_model, _m2m100_tokenizer, device

def translate_text(request) -> dict:
    start_time = time.time()
    
    # Obtener texto y lenguajes
    text = request.text
    source_lang = request.source_lang
    target_lang = request.target_lang
    
    # Obtener modelo, tokenizador y dispositivo, sin forzar recarga
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