# UnitAPI HCL Configuration for Microphone Devices

version = "1.0"

extension "microphone" {
  version = ">=1.0.0"
  config {
    sample_rate = 44100
    channels = 2
    format = "wav"
  }
}

extension "audio_processing" {
  version = ">=1.0.0"
  config {
    noise_reduction = true
    echo_cancellation = true
    voice_activity_detection = true
  }
}

device "desktop-mic" {
  type = "microphone"
  capabilities = ["recording", "streaming"]
  metadata = {
    location = "office"
    model = "Blue Yeti"
  }
}

device "rpi-mic" {
  type = "raspberry_pi_microphone"
  capabilities = ["recording", "streaming", "voice_commands"]
  metadata = {
    location = "living_room"
    model = "ReSpeaker 4-Mic Array"
  }
}

pipeline "voice-recorder" {
  source = "desktop-mic"
  
  step "record" {
    duration = 60  # seconds
    sample_rate = 44100
    channels = 2
  }
  
  step "process" {
    noise_reduction = true
    normalize = true
  }
  
  step "save" {
    format = "mp3"
    path = "/recordings/voice_memo.mp3"
  }
}

pipeline "voice-assistant" {
  source = "rpi-mic"
  
  step "listen" {
    mode = "continuous"
    wake_word = "hey_assistant"
  }
  
  step "recognize" {
    engine = "local"
    language = "en-US"
    timeout = 5  # seconds
  }
  
  step "process_command" {
    commands = ["lights", "music", "weather", "news"]
    fallback = "I didn't understand that command"
  }
  
  step "respond" {
    voice = "female"
    speed = 1.0
  }
}
