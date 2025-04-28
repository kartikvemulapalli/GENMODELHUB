from django.urls import path 
from django.conf import settings
from django.conf.urls.static import static
from .views import (
    login_view, register_view, logout_view, dashboard_view, 
    image_generator_view, chatbot_view, team_view, profile_view, menu_view, 
    speech_generator_view, generate_speech, translate_page, translate_text,
    generate_story_view, preprocess_csv, process_voice, stop_speaking, voice_assistant_view,generate_poem,codegenerator_view,text_summarization_view
)

urlpatterns = [
    # Authentication URLs
    path("register/", register_view, name="register"),
    path("login/", login_view, name="login"),
    path("logout/", logout_view, name="logout"),

    # Dashboard and Profile
    path("dashboard/", dashboard_view, name="dashboard"),
    path("profile/", profile_view, name="profile"),

    # Chatbot and AI interactions
    path("chatbot/", chatbot_view, name="chatbot"),
     path("codegenerator/", codegenerator_view, name="codegenerator"),
    path("generate_image/", image_generator_view, name="generate_image"),  

    # Miscellaneous pages
    path("menu/", menu_view, name="menu"),
    path("team/", team_view, name="team"),  

    # Home page
    path("", register_view, name="home"),

    # Speech Generator URLs
    path("speech_generator/", speech_generator_view, name="speech_generator"),
    path("generate_speech/", generate_speech, name="generate_speech"),

    # Translation
    path("translate/", translate_text, name="translate_text"),  # API endpoint
    path("translation/", translate_page, name="translation"),  # UI page

    # Story Generator
    path("story_form/", generate_story_view, name="story_form"), 

    # CSV Processing
    path("preprocess_csv/", preprocess_csv, name="preprocess_csv"),
    path("summarize/", text_summarization_view, name="text_summarization"),

    # Voice Assistant
    path('voice_assistant/', voice_assistant_view, name='voice_assistant'),
    path('process_voice/', process_voice, name='process_voice'),
    path('stop_speaking/', stop_speaking, name='stop_speaking'),
    path('generate-poem/', generate_poem, name='generate_poem'),

    
]

# Serve media files in development mode
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
