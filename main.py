import os
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, FileResponse
from pydantic import BaseModel
from melo.api import TTS
from openvoice import se_extractor
from openvoice.api import ToneColorConverter
from huggingface_hub import hf_hub_download

app = FastAPI()

class VoiceRequest(BaseModel):
    text: str

# 1. Setup the checkpoint directories automatically
ckpt_converter = 'checkpoints/converter'
os.makedirs(ckpt_converter, exist_ok=True)

pth_path = os.path.join(ckpt_converter, 'checkpoint.pth')
json_path = os.path.join(ckpt_converter, 'config.json')

# 2. Native URL-free downloading utility 
if not os.path.exists(pth_path):
    hf_hub_download(repo_id="myshell-ai/OpenVoice", filename="converter/checkpoint.pth", local_dir="checkpoints")
if not os.path.exists(json_path):
    hf_hub_download(repo_id="myshell-ai/OpenVoice", filename="converter/config.json", local_dir="checkpoints")

# Load models into memory
tone_color_converter = ToneColorConverter(json_path, device='cpu')
tone_color_converter.load_checkpoint(pth_path)

# Extract audio traits from your voice sample file
target_se, audio_name = se_extractor.get_se('reference_speaker.wav', tone_color_converter, target_dir='processed')

@app.get("/", response_class=HTMLResponse)
async def read_item():
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Instant Free Voice Clone</title>
        <style>
            body { font-family: sans-serif; display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100vh; background: #f4f4f9; margin: 0; }
            .card { background: white; padding: 30px; border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); text-align: center; max-width: 400px; width: 100%; }
            input { width: 90%; padding: 12px; margin: 15px 0; border: 1px solid #ccc; border-radius: 6px; font-size: 16px; }
            button { background: #4CAF50; color: white; border: none; padding: 12px 24px; font-size: 16px; border-radius: 6px; cursor: pointer; transition: 0.2s; }
            button:hover { background: #45a049; }
            #status { margin-top: 15px; color: #666; font-size: 14px; }
        </style>
    </head>
    <body>
        <div class="card">
            <h2>Voice Cloner</h2>
            <p>Type text below to hear it in your cloned voice.</p>
            <input type="text" id="textInput" placeholder="Type here..." value="Hello! This is running completely free on Render.">
            <button onclick="speak()">Speak Out Loud</button>
            <div id="status"></div>
        </div>

        <script>
            async function speak() {
                const textInput = document.getElementById('textInput').value;
                const status = document.getElementById('status');
                if(!textInput) return alert('Please enter some text!');
                status.innerText = "Generating voice clone... (takes a few seconds)";
                try {
                    const response = await fetch('/clone', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ text: textInput })
                    });
                    if(!response.ok) throw new Error('Generation failed');
                    const blob = await response.blob();
                    const audioUrl = URL.createObjectURL(blob);
                    const audio = new Audio(audioUrl);
                    status.innerText = "Playing audio!";
                    audio.play();
                } catch(e) {
                    status.innerText = "Error generating audio.";
                    console.error(e);
                }
            }
        </script>
    </body>
    </html>
    """

@app.post("/clone")
async def clone_voice(payload: VoiceRequest):
    try:
        model = TTS(language='EN', device='cpu')
        speaker_ids = model.hps.data.spk2id
        base_output = "base_temp.wav"
        model.tts_to_file(payload.text, speaker_ids['EN-Default'], base_output, speed=1.0)
        
        src_se, _ = se_extractor.get_se(base_output, tone_color_converter, target_dir='processed')
        final_output = "cloned_output.wav"
        
        tone_color_converter.convert(
            model_src=base_output, 
            src_se=src_se, 
            tgt_se=target_se, 
            output_path=final_output
        )
        return FileResponse(final_output, media_type="audio/wav")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
