# UnitAPI Simple DSL Configuration for Input Devices (Keyboard and Mouse)

version "1.0"

# Load extensions
load keyboard version=">=1.0.0" config={layout:"us", hotkeys:true}
load mouse version=">=1.0.0" config={sensitivity:1.2, acceleration:true}
load input_processing version=">=1.0.0" config={macros:true, gestures:true}

# Define devices
device main-keyboard type=keyboard with typing,hotkeys,function_keys
device gaming-keyboard type=gaming_keyboard with typing,hotkeys,rgb_lighting,macro_keys
device main-mouse type=mouse with movement,buttons,scrolling
device gaming-mouse type=gaming_mouse with movement,buttons,scrolling,dpi_switching,rgb_lighting
device rpi-keyboard type=raspberry_pi_keyboard with typing,remote_control
device rpi-mouse type=raspberry_pi_mouse with movement,buttons

# Define pipelines
pipeline keyboard-control from main-keyboard:
  capture key_events
  filter modifiers=ctrl,alt,shift
  process debounce=true
  execute action="system_control"
end

pipeline text-input from main-keyboard:
  capture key_events
  filter modifiers=none
  process layout_mapping=true
  forward destination="active_application"
end

pipeline mouse-control from main-mouse:
  capture mouse_events
  process smoothing=true
  execute action="cursor_control"
end

pipeline gaming-macros from gaming-keyboard to gaming-mouse:
  capture key_events
  filter keys=f1-f12,macro_keys
  process macro_expansion=true
  execute action="game_commands"
end

pipeline remote-keyboard from main-keyboard to rpi-keyboard:
  capture key_events
  filter keys=all
  process compression=true
  forward destination="tcp://192.168.1.100:5001"
end

pipeline remote-mouse from main-mouse to rpi-mouse:
  capture mouse_events
  process sampling_rate=30
  forward destination="tcp://192.168.1.100:5002"
end

# Combined input device pipeline
pipeline combined-input from main-keyboard,main-mouse:
  capture all_events
  process correlation=true
  on keyboard.key_press=ctrl+left_click:execute action="context_menu"
  on mouse.right_click:execute action="context_menu"
  on keyboard.key_press=alt+tab:execute action="window_switcher"
end

# Start commands (optional)
# start keyboard-control
# start mouse-control
