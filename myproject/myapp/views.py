from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout, get_user_model
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, FileResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.core.files.storage import FileSystemStorage

import os
import json
import time
import requests
import tempfile
import pandas as pd
from together import Together
from gtts import gTTS

from .forms import RegisterForm, LoginForm
from .models import CustomUser, Profile

# Initialize Together AI Client
client = Together(api_key=settings.TOGETHER_API_KEY2)

###########################################--Img-Gen--################################################

def generate_image(prompt):
    """Generates an image using Together AI's Stable Diffusion XL."""
    for _ in range(3):  # Retry up to 3 times
        try:
            response = client.images.generate(
                prompt=prompt,
                model="stabilityai/stable-diffusion-xl-base-1.0",
                steps=30,
                n=1
            )
            if response and hasattr(response, 'data') and response.data:
                image_data = response.data[0]
                # Get image URL from response
                if hasattr(image_data, 'url'):
                    # Download image from URL
                    img_response = requests.get(image_data.url)
                    if img_response.status_code == 200:
                        # Ensure the directory exists
                        image_dir = os.path.join(settings.MEDIA_ROOT, "generated_images")
                        os.makedirs(image_dir, exist_ok=True)
                        # Sanitize filename and save image
                        image_filename = f"{prompt[:50].replace(' ', '_')}.png"
                        image_path = os.path.join(image_dir, image_filename)
                        # Save the image
                        with open(image_path, "wb") as f:
                            f.write(img_response.content)
                        return f"/media/generated_images/{image_filename}"
        except Exception as e:
            print(f"Image generation failed: {e}")
            time.sleep(3)
    return None

def image_generator_view(request):
    """Handles image generation requests."""
    if request.method == "POST":
        prompt = request.POST.get("prompt", "").strip()
        if not prompt:
            return JsonResponse({"error": "No prompt provided"})
        image_url = generate_image(prompt)
        if image_url:
            return JsonResponse({"image_url": image_url})
        else:
            return JsonResponse({"error": "Failed to generate image"})
    return render(request, "image_generator.html")

###########################################--Auth--################################################

def team_view(request):
    return render(request, 'team.html')

def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            name = form.cleaned_data['name']
            password = form.cleaned_data['password']  # Store as plain text (for testing only)
            user = CustomUser.objects.create(email=email, name=name, password=password)
            return redirect('login')
    else:
        form = RegisterForm()
    return render(request, 'register.html', {'form': form})

def login_view(request):
    error = None  # Initialize error message variable
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            User = get_user_model()
            try:
                user = User.objects.get(email=email)  # Check if email exists
                if user.password == password:  # Plain-text password comparison
                    login(request, user)
                    return redirect('dashboard')
                else:
                    error = "Invalid password"  # Incorrect password
            except User.DoesNotExist:
                error = "Email not found"  # Email doesn't exist
    else:
        form = LoginForm()
    return render(request, 'login.html', {'form': form, 'error': error})

def logout_view(request):
    logout(request)
    return redirect('login')

def dashboard_view(request):
    return render(request, 'dashboard.html')

def profile_view(request):
    """Displays user profile if it exists."""
    try:
        profile_data = Profile.objects.get(user=request.user)
    except Profile.DoesNotExist:
        profile_data = None
    return render(request, 'profile.html', {'profile': profile_data, 'user': request.user})

def menu_view(request):
    return render(request, 'menu.html')

#############################################--chatbot--#########################################

def get_together_response(user_input):
    """Sends a request to the Together AI API using Llama 3.3 70B model."""
    try:
        response = client.chat.completions.create(
            model="meta-llama/Llama-3.3-70B-Instruct-Turbo-Free",
            messages=[{"role": "user", "content": user_input}]
        )
        # Extract chatbot response
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Error: API request failed - {str(e)}"

def process_chatbot_command(user_input):
    try:
        # Detect command type from user input
        if any(keyword in user_input.lower() for keyword in ['generate image', 'create image', 'draw']):
            # Extract the image description after the command
            prompt = user_input.lower()
            for cmd in ['generate image', 'create image', 'draw']:
                if cmd in prompt:
                    prompt = prompt.split(cmd)[-1].strip()
                    break
            # Generate the image
            image_url = generate_image(prompt)
            if image_url:
                return {
                    'type': 'image',
                    'content': image_url,
                    'message': f"Here's your generated image based on: {prompt}"
                }
            return {'type': 'text', 'content': "Sorry, I couldn't generate the image. Please try again with a different description."}
        elif any(keyword in user_input.lower() for keyword in ['translate', 'translation']):
            text = user_input.lower().split('translate')[-1].strip()
            translated_text = translate_text(text)
            return {'type': 'text', 'content': translated_text}
        elif any(keyword in user_input.lower() for keyword in ['generate story', 'write story']):
            story = generate_story_view(user_input)
            return {'type': 'text', 'content': story}
        # Default to normal chatbot response using Together AI
        response = get_together_response(user_input)
        return {'type': 'text', 'content': response}
    except Exception as e:
        return {'type': 'text', 'content': f"An error occurred: {str(e)}"}

def chatbot_view(request):
    if request.method == "POST":
        user_input = request.POST.get("message", "")
        response = process_chatbot_command(user_input)
        return JsonResponse(response)
    return render(request, "chatbot.html")

###########################################--codegenerator--#########################################

def process_codegenerator_command(user_input, uploaded_file=None):
    try:
        if uploaded_file:
            file_path = handle_uploaded_file(uploaded_file)
            return {'type': 'text', 'content': f"File '{uploaded_file.name}' uploaded successfully! Path: {file_path}"}
        elif any(keyword in user_input.lower() for keyword in ['generate code', 'write code', 'create script']):
            code_response = get_together_response(user_input)
            return {'type': 'text', 'content': code_response}
        # Default to normal chatbot response using Together AI
        response = get_together_response(user_input)
        return {'type': 'text', 'content': response}
    except Exception as e:
        return {'type': 'text', 'content': f"An error occurred: {str(e)}"}

def codegenerator_view(request):
    if request.method == "POST":
        user_input = request.POST.get("command", "")
        uploaded_file = request.FILES.get("file")
        response = process_codegenerator_command(user_input, uploaded_file)
        return JsonResponse(response)
    return render(request, "codegenerator.html")

def handle_uploaded_file(f):
    """Saves uploaded file to media directory."""
    upload_path = os.path.join(settings.MEDIA_ROOT, 'uploads')
    os.makedirs(upload_path, exist_ok=True)
    file_path = os.path.join(upload_path, f.name)
    with open(file_path, 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)
    return file_path

#################################--Speech generator--################################

def speech_generator_view(request):
    """Render the speech generator UI."""
    return render(request, "speech_generator.html")

@csrf_exempt
def generate_speech(request):
    """Convert text to speech using gTTS and serve the generated audio."""
    if request.method != "POST":
        return JsonResponse({"error": "Use POST to send text data"}, status=405)
    try:
        data = json.loads(request.body.decode("utf-8"))
        text = data.get("text", "").strip()
        if not text:
            return JsonResponse({"error": "No text provided"}, status=400)
        # Generate speech using gTTS
        tts = gTTS(text=text, lang="en")
        # Store audio in a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_audio:
            audio_path = temp_audio.name
            tts.save(audio_path)
        # Serve the generated audio file
        response = FileResponse(open(audio_path, "rb"), content_type="audio/mp3")
        response["Content-Disposition"] = 'attachment; filename="speech.mp3"'
        return response
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON format"}, status=400)
    except Exception as e:
        return JsonResponse({"error": f"Speech generation failed: {str(e)}"}, status=500)

##############################--Translation--#######################################

# Supported Languages Mapping
LANGUAGE_MAPPING = {
    "fr": "French",
    "es": "Spanish",
    "de": "German",
    "hi": "Hindi",
    "it": "Italian",
    "pt": "Portuguese",
    "nl": "Dutch",
}

# Together AI API URL
TOGETHER_API_URL = "https://api.together.xyz/v1/completions"

def translate_page(request):
    """Render the translation UI."""
    return render(request, "translation.html")

@csrf_exempt
def translate_text(request):
    """Handles text translation using Together AI API."""
    if request.method == "POST":
        try:
            data = request.POST
            text = data.get("text", "").strip()
            target_language = data.get("language", "").strip()
            if not text or not target_language:
                return JsonResponse({"error": "Missing text or language"}, status=400)
            if target_language not in LANGUAGE_MAPPING:
                return JsonResponse({"error": "Unsupported language"}, status=400)
            
            # Constructing a prompt
            prompt = (
                f"Translate this English sentence to {LANGUAGE_MAPPING[target_language]}.\n\n"
                f"English: {text}\n"
                f"{LANGUAGE_MAPPING[target_language]}:"
            )
            
            # API request payload
            payload = {
                "model": "meta-llama/Llama-3.3-70B-Instruct-Turbo-Free",
                "prompt": prompt,
                "max_tokens": 50,  # Limit response length
                "temperature": 0.3,  # Reduce randomness
                "stop": ["\n"],  # Stop at the first translation line
            }
            
            headers = {
                "Authorization": f"Bearer {settings.TOGETHER_API_KEY2}",
                "Content-Type": "application/json",
            }
            
            # Sending request to Together AI API
            response = requests.post(TOGETHER_API_URL, headers=headers, json=payload)
            
            # Handle API response
            if response.status_code == 200:
                result = response.json()
                translated_text = result.get("choices", [{}])[0].get("text", "").strip()
                return JsonResponse({"translated_text": translated_text})
            else:
                return JsonResponse(
                    {"error": f"API error: {response.status_code}, {response.text}"},
                    status=500
                )
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
    return JsonResponse({"error": "Invalid request method"}, status=400)

####################################--Story-Gen--######################################

def generate_story_view(request):
    story = None
    error = None
    if request.method == "POST":
        prompt = request.POST.get("prompt")
        if not prompt:
            error = "Story idea is required!"
        else:
            api_url = "https://api.together.xyz/v1/chat/completions"
            
            headers = {
                "Authorization": f"Bearer {settings.TOGETHER_API_KEY2}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": "meta-llama/Llama-3.3-70B-Instruct-Turbo-Free",
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 800,
                "temperature": 0.8,
                "top_p": 0.9,
            }
            
            retries = 3
            for attempt in range(retries):
                try:
                    response = requests.post(api_url, headers=headers, json=payload, timeout=60)
                    response_json = response.json()
                    
                    if response.status_code == 200:
                        story = response_json.get("choices", [{}])[0].get("message", {}).get("content", "No response received.")
                        break
                    elif response.status_code == 401:
                        error = "Unauthorized: Invalid Together AI API key."
                        break
                    elif response.status_code == 404:
                        error = "Model not found. Ensure the model name is correct."
                        break
                    elif response.status_code == 503:
                        error = "Together AI servers are busy. Retrying..."
                        time.sleep(2)
                    else:
                        error = f"Story generation failed. API returned {response.status_code}."
                        break
                except requests.RequestException as e:
                    error = f"Request error: {e}"
                    break
                    
    return render(request, "story_form.html", {"story": story, "error": error})

######################################--preprocess-csv--######################################

def preprocess_csv(request):
    processed_file_url = None
    error = None
    if request.method == "POST" and request.FILES.get("csv_file"):
        csv_file = request.FILES["csv_file"]
        fs = FileSystemStorage(location=settings.MEDIA_ROOT)  # Save in media directory
        file_path = fs.save(csv_file.name, csv_file)
        
        # Read CSV
        df = pd.read_csv(os.path.join(settings.MEDIA_ROOT, file_path))
        
        api_url = "https://api-inference.huggingface.co/models/NousResearch/Jellyfish-7B"
        headers = {"Authorization": f"Bearer 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"}
        
        # Process each row
        for i, row in df.iterrows():
            text = row.get("text", "")  # Assume column name is 'text'
            if text:
                payload = {"inputs": f"Clean and preprocess this text: {text}"}
                retries = 3
                
                for attempt in range(retries):
                    try:
                        response = requests.post(api_url, headers=headers, json=payload, timeout=60)
                        if response.status_code == 200:
                            df.at[i, "text"] = response.json()[0]["generated_text"]
                            break
                        elif response.status_code in [403, 404]:
                            error = "API access error. Check API key or model."
                            break
                        elif response.status_code == 503:
                            time.sleep(2)  # Wait and retry
                        else:
                            error = f"Error {response.status_code}"
                            break
                    except requests.RequestException as e:
                        error = f"Request error: {e}"
                        break
        
        # Save cleaned CSV
        processed_filename = f"processed_{csv_file.name}"
        processed_file_path = os.path.join(settings.MEDIA_ROOT, processed_filename)
        df.to_csv(processed_file_path, index=False)
        
        # Generate the URL for download
        processed_file_url = fs.url(processed_filename)
        
    return render(request, "preprocess_csv.html", {"processed_file": processed_file_url, "error": error})

##########################################--Voice-ASSIST--###########################################

def voice_assistant_view(request):
    """Render the voice assistant interface"""
    return render(request, 'voice_assistant.html')

@csrf_exempt
def process_voice(request):
    """Handle voice input from dashboard"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))
            query = data.get('query', '')
            
            if not query:
                return JsonResponse({'error': 'Empty query'}, status=400)
                
            # Check if it's an image generation request
            if any(keyword in query.lower() for keyword in ['generate image', 'create image', 'draw']):
                # Extract the image description after the command
                prompt = query.lower()
                for cmd in ['generate image', 'create image', 'draw']:
                    if cmd in prompt:
                        prompt = prompt.split(cmd)[-1].strip()
                        break
                
                # Generate the image using the existing function
                image_url = generate_image(prompt)
                if image_url:
                    return JsonResponse({
                        'reply': f"I've generated an image based on your description: {prompt}",
                        'type': 'image',
                        'image_url': image_url
                    })
                return JsonResponse({
                    'reply': "Sorry, I couldn't generate the image. Please try again.",
                    'type': 'text'
                })
                
            # For non-image requests, use the existing Together AI chat
            response = client.chat.completions.create(
                model="meta-llama/Llama-3-70b-chat-hf",
                messages=[{"role": "user", "content": query}],
                max_tokens=500
            )
            
            if response.choices and response.choices[0].message:
                return JsonResponse({
                    'reply': response.choices[0].message.content,
                    'type': 'text'
                })
                
            return JsonResponse({'error': 'Empty API response'}, status=500)
            
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON format'}, status=400)
        except Exception as e:
            print(f"Voice Processing Error: {str(e)}")
            return JsonResponse({'error': f'Server error: {str(e)}'}, status=500)
            
    return JsonResponse({'error': 'Method not allowed'}, status=405)

@csrf_exempt
def stop_speaking(request):
    if request.method == 'POST':
        return JsonResponse({'status': 'stopped'})
    return JsonResponse({'error': 'Invalid method'}, status=405)

#############################################--Text-Sum--#######################################

# Together AI API details
API_URL = "https://api.together.xyz/v1/chat/completions"
HEADERS = {
    "Authorization": f"Bearer {settings.TOGETHER_API_KEY2}",
    "Content-Type": "application/json"
}

def summarize_text(user_input):
    """Sends a request to Together AI API to summarize text using Meta Llama 3.3 70B."""
    payload = {
        "model": "meta-llama/Llama-3.3-70B-Instruct-Turbo-Free",
        "messages": [
            {"role": "system", "content": "You are an AI assistant that summarizes text."},
            {"role": "user", "content": f"Summarize the following text concisely:\n\n{user_input}"}
        ],
        "max_tokens": 100,
        "temperature": 0.2
    }
    
    try:
        response = requests.post(API_URL, headers=HEADERS, json=payload)
        response.raise_for_status()  # Catch errors early
        response_data = response.json()
        
        return response_data.get("choices", [{}])[0].get("message", {}).get("content", "No valid summary received.").strip()
    except requests.exceptions.RequestException as e:
        return f"Error: API request failed - {str(e)}"

def text_summarization_view(request):
    if request.method == "POST":
        user_input = request.POST.get("text", "").strip()
        if not user_input:
            return JsonResponse({"error": "No text provided for summarization."}, status=400)
            
        summary = summarize_text(user_input)
        return JsonResponse({"summary": summary})
        
    return render(request, "summarization.html")

############################--poem-Generation--#################################################

def generate_poem(request):
    if request.method == "POST":
        theme = request.POST.get("theme", "").strip()
        if not theme:
            return JsonResponse({"error": "Theme is required"}, status=400)
            
        payload = {
            "model": "meta-llama/Llama-3.3-70B-Instruct-Turbo-Free",
            "messages": [
                {"role": "system", "content": "You are an AI that generates structured poems based on a theme."},
                {"role": "user", "content": f"Write a structured poem about: {theme}"}
            ],
            "max_tokens": 200
        }
        
        try:
            response = requests.post(API_URL, headers=HEADERS, json=payload)
            response.raise_for_status()
            response_data = response.json()
            
            poem = response_data.get("choices", [{}])[0].get("message", {}).get("content", "No valid poem received.").strip()
            return JsonResponse({"poem": poem})
            
        except requests.exceptions.RequestException as e:
            return JsonResponse({"error": f"API request failed - {str(e)}"}, status=500)
            
    return render(request, "poem_generator.html")