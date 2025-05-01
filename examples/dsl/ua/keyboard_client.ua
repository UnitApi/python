# UnitAPI Simple DSL Configuration for Keyboard Client
# This configuration sets up a client to send text to the keyboard server on PC1

version "1.0"

# Load extensions
load client version=">=1.0.0" config={timeout:5000}
load keyboard version=">=1.0.0" config={layout:"us", hotkeys:true}

# Define devices
device remote-keyboard type=remote_keyboard with typing,hotkeys,function_keys

# Define client pipeline
pipeline keyboard-client:
  # Connect to the keyboard server
  connect host="localhost" port=7890 device_id="keyboard_01"
  
  # Define text input command
  command name="type_text" params={text:"Hello from UnitAPI DSL!"} target=remote-keyboard
  
  # Define key press command
  command name="press_key" params={key:"enter"} target=remote-keyboard
  
  # Define hotkey command
  command name="press_hotkey" params={keys:["ctrl", "a"]} target=remote-keyboard
end

# Start the keyboard client pipeline
start keyboard-client
