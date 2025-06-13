"""
Cliente completo para el servicio de traducción de audio
Incluye versiones síncronas y asíncronas para integración con FastAPI
"""

import requests
import httpx
import asyncio
import io
from pathlib import Path
from typing import Optional, Dict, Any, BinaryIO

class AudioTranslationClient:
    """Cliente síncrono para interactuar con el servicio de traducción de audio"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url.rstrip('/')
        self.translate_url = f"{self.base_url}/translate-audio/"
        self.info_url = f"{self.base_url}/translate-audio/info"
    
    def translate_audio_file(
        self,
        audio_file_path: str,
        voice_reference_path: str,
        source_lang: str,
        target_lang: str,
        model: str = "F5TTS_v1_Base",
        save_to: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Traduce un archivo de audio y retorna el archivo traducido
        
        Args:
            audio_file_path: Ruta al archivo de audio a traducir
            voice_reference_path: Ruta al archivo de referencia de voz
            source_lang: Código del idioma de origen (ej: 'es', 'en')
            target_lang: Código del idioma de destino (ej: 'es', 'en')
            model: Modelo TTS a utilizar
            save_to: Ruta donde guardar el archivo traducido (opcional)
            
        Returns:
            Dict con información del proceso y datos del archivo
        """
        try:
            # Preparar archivos para el upload
            with open(audio_file_path, 'rb') as audio_file, \
                 open(voice_reference_path, 'rb') as voice_file:
                
                files = {
                    'audio_file': (Path(audio_file_path).name, audio_file, 'audio/mpeg'),
                    'voice_reference_file': (Path(voice_reference_path).name, voice_file, 'audio/mpeg')
                }
                
                data = {
                    'source_lang': source_lang,
                    'target_lang': target_lang,
                    'model': model
                }
                
                # Hacer la petición
                response = requests.post(
                    self.translate_url, 
                    files=files, 
                    data=data, 
                    timeout=300
                )
                
                if response.status_code == 200:
                    # Obtener información de los headers
                    headers = response.headers
                    result = {
                        'success': True,
                        'transcribed_text': headers.get('X-Transcribed-Text', ''),
                        'translated_text': headers.get('X-Translated-Text', ''),
                        'source_lang': headers.get('X-Source-Lang', source_lang),
                        'target_lang': headers.get('X-Target-Lang', target_lang),
                        'total_time': float(headers.get('X-Total-Time', 0)),
                        'audio_content': response.content,
                        'content_type': response.headers.get('content-type', 'audio/wav'),
                        'filename': response.headers.get('content-disposition', '').split('filename=')[-1].strip('"') if 'content-disposition' in response.headers else f'translated_{source_lang}_to_{target_lang}.wav'
                    }
                    
                    # Guardar archivo si se especifica una ruta
                    if save_to:
                        with open(save_to, 'wb') as f:
                            f.write(response.content)
                        result['saved_to'] = save_to
                    
                    return result
                    
                else:
                    return {
                        'success': False,
                        'error': f"Error {response.status_code}: {response.text}"
                    }
                    
        except Exception as e:
            return {
                'success': False,
                'error': f"Error de conexión: {str(e)}"
            }
    
    def translate_audio_bytes(
        self,
        audio_bytes: bytes,
        audio_filename: str,
        voice_reference_bytes: bytes,
        voice_reference_filename: str,
        source_lang: str,
        target_lang: str,
        model: str = "F5TTS_v1_Base"
    ) -> Dict[str, Any]:
        """
        Traduce audio desde bytes en memoria (útil para APIs web)
        
        Args:
            audio_bytes: Contenido del archivo de audio como bytes
            audio_filename: Nombre del archivo de audio
            voice_reference_bytes: Contenido del archivo de referencia como bytes
            voice_reference_filename: Nombre del archivo de referencia
            source_lang: Código del idioma de origen
            target_lang: Código del idioma de destino
            model: Modelo TTS a utilizar
            
        Returns:
            Dict con información del proceso y datos del archivo
        """
        try:
            files = {
                'audio_file': (audio_filename, io.BytesIO(audio_bytes), 'audio/mpeg'),
                'voice_reference_file': (voice_reference_filename, io.BytesIO(voice_reference_bytes), 'audio/mpeg')
            }
            
            data = {
                'source_lang': source_lang,
                'target_lang': target_lang,
                'model': model
            }
            
            response = requests.post(
                self.translate_url,
                files=files,
                data=data,
                timeout=300
            )
            
            if response.status_code == 200:
                headers = response.headers
                return {
                    'success': True,
                    'transcribed_text': headers.get('X-Transcribed-Text', ''),
                    'translated_text': headers.get('X-Translated-Text', ''),
                    'source_lang': headers.get('X-Source-Lang', source_lang),
                    'target_lang': headers.get('X-Target-Lang', target_lang),
                    'total_time': float(headers.get('X-Total-Time', 0)),
                    'audio_content': response.content,
                    'content_type': response.headers.get('content-type', 'audio/wav'),
                    'filename': f'translated_{source_lang}_to_{target_lang}.wav'
                }
            else:
                return {
                    'success': False,
                    'error': f"Error {response.status_code}: {response.text}"
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f"Error de conexión: {str(e)}"
            }
    
    def get_translation_info(
        self,
        audio_file_path: str,
        voice_reference_path: str,
        source_lang: str,
        target_lang: str,
        model: str = "F5TTS_v1_Base"
    ) -> Dict[str, Any]:
        """
        Obtiene información detallada del proceso sin descargar el archivo
        """
        try:
            with open(audio_file_path, 'rb') as audio_file, \
                 open(voice_reference_path, 'rb') as voice_file:
                
                files = {
                    'audio_file': (Path(audio_file_path).name, audio_file, 'audio/mpeg'),
                    'voice_reference_file': (Path(voice_reference_path).name, voice_file, 'audio/mpeg')
                }
                
                data = {
                    'source_lang': source_lang,
                    'target_lang': target_lang,
                    'model': model
                }
                
                response = requests.post(
                    self.info_url,
                    files=files,
                    data=data,
                    timeout=300
                )
                
                if response.status_code == 200:
                    return {
                        'success': True,
                        **response.json()
                    }
                else:
                    return {
                        'success': False,
                        'error': f"Error {response.status_code}: {response.text}"
                    }
                    
        except Exception as e:
            return {
                'success': False,
                'error': f"Error de conexión: {str(e)}"
            }


# Ejemplo de uso
if __name__ == "__main__":
    client = AudioTranslationClient("http://localhost:8000")
    
    # Ejemplo 1: Traducir y guardar archivo
    result = client.translate_audio_file(
        audio_file_path="audios/audioStefano.mp3",
        voice_reference_path="audios/audioStefano.mp3",
        source_lang="es",
        target_lang="en",
        save_to="translated_output.wav"
    )
    
    if result['success']:
        print(f"✅ Traducción exitosa!")
        print(f"📝 Texto transcrito: {result['transcribed_text']}")
        print(f"🌐 Texto traducido: {result['translated_text']}")
        print(f"⏱️ Tiempo total: {result['total_time']}s")
        print(f"💾 Guardado en: {result.get('saved_to', 'memoria')}")
    else:
        print(f"❌ Error: {result['error']}")

# ============================================================================
# CLIENTE ASÍNCRONO PARA FASTAPI
# ============================================================================

class AsyncAudioTranslationClient:
    """Cliente asíncrono para integración con FastAPI"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url.rstrip('/')
        self.client = httpx.AsyncClient(timeout=300.0)
    
    async def translate_audio_and_get_file(
        self,
        audio_file: BinaryIO,
        voice_reference_file: BinaryIO,
        source_lang: str,
        target_lang: str,
        model: str = "F5TTS_v1_Base"
    ) -> tuple[bytes, dict]:
        """
        Envía archivos al servicio de traducción y retorna el archivo traducido y metadatos
        """
        files = {
            'audio_file': ('audio.wav', audio_file, 'audio/wav'),
            'voice_reference_file': ('voice_ref.wav', voice_reference_file, 'audio/wav')
        }
        
        data = {
            'source_lang': source_lang,
            'target_lang': target_lang,
            'model': model
        }
        
        response = await self.client.post(
            f"{self.base_url}/translate-audio/",
            files=files,
            data=data
        )
        
        if response.status_code != 200:
            raise Exception(f"Error {response.status_code}: {response.text}")
        
        # Extraer metadatos de los headers
        metadata = {
            'transcribed_text': response.headers.get('X-Transcribed-Text', ''),
            'translated_text': response.headers.get('X-Translated-Text', ''),
            'source_lang': response.headers.get('X-Source-Lang', source_lang),
            'target_lang': response.headers.get('X-Target-Lang', target_lang),
            'total_time': response.headers.get('X-Total-Time', '0'),
            'content_type': response.headers.get('content-type', 'audio/wav'),
            'filename': self._extract_filename_from_headers(response.headers)
        }
        
        return response.content, metadata
    
    async def translate_audio_from_uploadfile(
        self,
        audio_file,  # FastAPI UploadFile
        voice_reference_file,  # FastAPI UploadFile
        source_lang: str,
        target_lang: str
    ) -> tuple[bytes, dict]:
        """
        Traduce audio desde objetos UploadFile de FastAPI
        """
        # Leer contenido de los UploadFile
        audio_content = await audio_file.read()
        voice_content = await voice_reference_file.read()
        
        # Resetear posición para uso posterior si es necesario
        await audio_file.seek(0)
        await voice_reference_file.seek(0)
        
        return await self.translate_audio_and_get_file(
            audio_file=io.BytesIO(audio_content),
            voice_reference_file=io.BytesIO(voice_content),
            source_lang=source_lang,
            target_lang=target_lang
        )
    
    async def get_translation_info(
        self,
        audio_file: BinaryIO,
        voice_reference_file: BinaryIO,
        source_lang: str,
        target_lang: str,
        model: str = "F5TTS_v1_Base"
    ) -> dict:
        """
        Obtiene información detallada del proceso de traducción sin descargar el archivo
        """
        files = {
            'audio_file': ('audio.wav', audio_file, 'audio/wav'),
            'voice_reference_file': ('voice_ref.wav', voice_reference_file, 'audio/wav')
        }
        
        data = {
            'source_lang': source_lang,
            'target_lang': target_lang,
            'model': model
        }
        
        response = await self.client.post(
            f"{self.base_url}/translate-audio/info",
            files=files,
            data=data
        )
        
        if response.status_code != 200:
            raise Exception(f"Error {response.status_code}: {response.text}")
        
        return response.json()
    
    async def download_translated_audio(self, audio_id: str) -> bytes:
        """
        Descarga un audio traducido usando su ID
        """
        response = await self.client.get(
            f"{self.base_url}/translate-audio/download/{audio_id}"
        )
        
        if response.status_code != 200:
            raise Exception(f"Error {response.status_code}: Audio no encontrado")
        
        return response.content
    
    def _extract_filename_from_headers(self, headers) -> str:
        """Extrae el nombre del archivo desde los headers"""
        content_disposition = headers.get('content-disposition', '')
        if 'filename=' in content_disposition:
            return content_disposition.split('filename=')[-1].strip('"')
        return 'translated_audio.wav'
    
    async def close(self):
        """Cierra el cliente HTTP"""
        await self.client.aclose()

# ============================================================================
# EJEMPLOS DE USO PARA FASTAPI
# ============================================================================

# Ejemplo de endpoint en tu backend FastAPI
async def ejemplo_endpoint_fastapi():
    """
    Ejemplo de cómo usar el cliente asíncrono en un endpoint de FastAPI
    """
    from fastapi import FastAPI, UploadFile, File, Form
    from fastapi.responses import StreamingResponse
    
    app = FastAPI()
    client = AsyncAudioTranslationClient()
    
    @app.post("/traducir-audio")
    async def traducir_audio(
        audio_file: UploadFile = File(...),
        voice_reference_file: UploadFile = File(...),
        source_lang: str = Form(...),
        target_lang: str = Form(...)
    ):
        try:
            # Traducir usando el cliente asíncrono
            translated_audio, metadata = await client.translate_audio_from_uploadfile(
                audio_file=audio_file,
                voice_reference_file=voice_reference_file,
                source_lang=source_lang,
                target_lang=target_lang
            )
            
            # Retornar como streaming response
            return StreamingResponse(
                io.BytesIO(translated_audio),
                media_type="audio/wav",
                headers={
                    "Content-Disposition": f"attachment; filename={metadata['filename']}",
                    "X-Transcribed-Text": metadata['transcribed_text'],
                    "X-Translated-Text": metadata['translated_text']
                }
            )
            
        except Exception as e:
            return {"error": str(e)}
    
    @app.on_event("shutdown")
    async def shutdown():
        await client.close()

# ============================================================================
# EJEMPLO DE USO DIRECTO
# ============================================================================
