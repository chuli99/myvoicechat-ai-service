pip install f5-tts
git clone https://github.com/SWivid/F5-TTS.git
cd F5-TTS
pip install -e .
pip install torch==2.4.0+cu124 torchaudio==2.4.0+cu124 --extra-index-url https://download.pytorch.org/whl/cu124
