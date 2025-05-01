# UnitAPI Simple DSL Configuration for Interactive Keyboard Client
# This configuration sets up a client to send custom text to the keyboard server on PC1

version "1.0"

# Load extensions
load client version=">=1.0.0" config={timeout:5000}
load keyboard version=">=1.0.0" config={layout:"us", hotkeys:true}
load input_processing version=">=1.0.0" config={interactive:true}

# Define devices
device remote-keyboard type=remote_keyboard with typing,hotkeys,function_keys
device user-input type=input_source with text_input,command_input

# Define client pipeline
pipeline keyboard-client-interactive from user-input to remote-keyboard:
  # Connect to the keyboard server
  connect host="localhost" port=7890 device_id="keyboard_01"
  
  # Set up interactive input
  prompt message="Enter text to send to remote keyboard (or 'exit' to quit):"
  
  # Process input
  on input:
    if input="exit":
      exit
    else:
      # Send text to remote keyboard
      execute command="type_text" params={text:input} target=remote-keyboard
      # Add a newline after the text
      execute command="press_key" params={key:"enter"} target=remote-keyboard
    end
  end
  
  # Loop to continue accepting input
  loop interval=0 # Process input immediately
end

# Start the interactive keyboard client pipeline
start keyboard-client-interactive
