import pyttsx3
from gtts import gTTS
import os
import threading
import tempfile
import platform

class VoiceAlertSystem:
    def __init__(self):
        self.engine = pyttsx3.init()
        self.engine.setProperty('rate', 150)
        self.engine.setProperty('volume', 1.0)
        
        # Set female voice
        voices = self.engine.getProperty('voices')
        for voice in voices:
            if 'female' in voice.name.lower() or 'zira' in voice.name.lower():
                self.engine.setProperty('voice', voice.id)
                break
        
        # Alert messages in multiple languages
        self.alerts = {
            'near_miss': {
                'english': 'Warning! Worker detected near moving vehicle.',
                'hindi': 'चेतावनी! कार्यकर्ता चलते वाहन के पास पाया गया।',
                'tamil': 'எச்சரிக்கை! நகரும் வாகனத்திற்கு அருகில் தொழிலாளி கண்டறியப்பட்டது.'
            },
            'fire': {
                'english': 'Critical alert! Fire detected. Evacuate immediately.',
                'hindi': 'गंभीर चेतावनी! आग का पता चला। तुरंत निकल जाएं।',
                'tamil': 'முக்கிய எச்சரிக்கை! தீ கண்டறியப்பட்டது. உடனடியாக வெளியேறவும்.'
            },
            'fall': {
                'english': 'Emergency! Worker fall detected. Medical assistance required.',
                'hindi': 'आपातकाल! कार्यकर्ता गिर गया। चिकित्सा सहायता की आवश्यकता है।',
                'tamil': 'அவசரநிலை! தொழிலாளி விழுந்தது கண்டறியப்பட்டது. மருத்துவ உதவி தேவை.'
            },
            'zone_violation': {
                'english': 'Alert! Unauthorized entry in restricted zone.',
                'hindi': 'चेतावनी! प्रतिबंधित क्षेत्र में अनधिकृत प्रवेश।',
                'tamil': 'எச்சரிக்கை! தடைசெய்யப்பட்ட பகுதியில் அங்கீகரிக்கப்படாத நுழைவு.'
            },
            'no_helmet': {
                'english': 'Safety violation! Worker without helmet detected.',
                'hindi': 'सुरक्षा उल्लंघन! बिना हेलमेट के कार्यकर्ता पाया गया।',
                'tamil': 'பாதுகாப்பு மீறல்! தலைக்கவசம் இல்லாத தொழிலாளி கண்டறியப்பட்டது.'
            },
            'collision': {
                'english': 'Danger! Vehicle collision detected.',
                'hindi': 'खतरा! वाहन टक्कर का पता चला।',
                'tamil': 'ஆபத்து! வாகன மோதல் கண்டறியப்பட்டது.'
            },
            'theft': {
                'english': 'Security alert! Suspicious activity detected.',
                'hindi': 'सुरक्षा चेतावनी! संदिग्ध गतिविधि का पता चला।',
                'tamil': 'பாதுகாப்பு எச்சரிக்கை! சந்தேகத்திற்குரிய செயல்பாடு கண்டறியப்பட்டது.'
            }
        }
    
    def speak_pyttsx3(self, text, language='english'):
        """Speak using pyttsx3 (works for English)"""
        try:
            self.engine.say(text)
            self.engine.runAndWait()
        except Exception as e:
            print(f"Error in pyttsx3: {e}")
    
    def speak_gtts(self, text, language='en'):
        """Speak using Google TTS (works for all languages)"""
        try:
            # Language codes
            lang_codes = {
                'english': 'en',
                'hindi': 'hi',
                'tamil': 'ta'
            }
            
            lang_code = lang_codes.get(language, 'en')
            
            # Create temporary file
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.mp3')
            temp_path = temp_file.name
            temp_file.close()
            
            # Generate speech
            tts = gTTS(text=text, lang=lang_code, slow=False)
            tts.save(temp_path)
            
            # Play audio using system command
            if platform.system() == 'Windows':
                os.system(f'start /min wmplayer "{temp_path}"')
            elif platform.system() == 'Darwin':  # macOS
                os.system(f'afplay "{temp_path}"')
            else:  # Linux
                os.system(f'mpg123 "{temp_path}"')
            
            # Clean up after a delay (in background)
            def cleanup():
                import time
                time.sleep(5)
                try:
                    os.remove(temp_path)
                except:
                    pass
            threading.Thread(target=cleanup, daemon=True).start()
            
        except Exception as e:
            print(f"Error in gTTS: {e}")
    
    def announce(self, alert_type, language='english', use_gtts=True):
        """Announce alert in specified language"""
        if alert_type not in self.alerts:
            print(f"Unknown alert type: {alert_type}")
            return
        
        message = self.alerts[alert_type].get(language, self.alerts[alert_type]['english'])
        
        # Use gTTS for Hindi and Tamil, pyttsx3 for English
        if language in ['hindi', 'tamil'] or use_gtts:
            threading.Thread(target=self.speak_gtts, args=(message, language), daemon=True).start()
        else:
            threading.Thread(target=self.speak_pyttsx3, args=(message,), daemon=True).start()
    
    def announce_custom(self, message, language='english'):
        """Announce custom message"""
        if language == 'english':
            threading.Thread(target=self.speak_pyttsx3, args=(message,), daemon=True).start()
        else:
            threading.Thread(target=self.speak_gtts, args=(message, language), daemon=True).start()

# Global instance
voice_system = VoiceAlertSystem()

def test_voice_system():
    """Test voice alerts"""
    print("Testing voice alerts...")
    
    # Test English
    print("Testing English...")
    voice_system.announce('near_miss', 'english')
    
    # Test Hindi
    print("Testing Hindi...")
    voice_system.announce('fire', 'hindi')
    
    # Test Tamil
    print("Testing Tamil...")
    voice_system.announce('fall', 'tamil')

if __name__ == '__main__':
    test_voice_system()
