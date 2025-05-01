# UnitAPI Simple DSL Configuration for Keyboard Server
# This configuration sets up a keyboard server on PC1

version "1.0"

# Load extensions
load keyboard version=">=1.0.0" config={layout:"us", hotkeys:true}
load server version=">=1.0.0" config={host:"0.0.0.0", port:7890}

# Define devices
device local-keyboard type=keyboard with typing,hotkeys,function_keys

# Define server pipeline
pipeline keyboard-server from local-keyboard:
  # Register the keyboard device with the server
  register device=local-keyboard id="keyboard_01" name="PC1 Keyboard"
  
  # Set up command handlers
  handle command="type_text" action="keyboard.type_text"
  handle command="press_key" action="keyboard.press_key"
  handle command="press_hotkey" action="keyboard.press_hotkey"
  
  # Start the server
  start_server host="0.0.0.0" port=7890
end

# Start the keyboard server pipeline
start keyboard-server
