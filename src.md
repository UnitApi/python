unitapi/
│
├── pyproject.toml
├── setup.py
├── README.md
├── LICENSE
├── requirements.txt
├── requirements-dev.txt
│
├── unitapi/
│   ├── __init__.py
│   │
│   ├── core/
│   │   ├── __init__.py
│   │   ├── server.py
│   │   └── client.py
│   │
│   ├── devices/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── microphone.py
│   │   ├── camera.py
│   │   ├── gpio.py
│   │   └── remote_speaker.py
│   │
│   ├── protocols/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── mqtt.py
│   │   └── websocket.py
│   │
│   └── security/
│       ├── __init__.py
│       ├── authentication.py
│       ├── encryption.py
│       └── access_control.py
│
├── tests/
│   ├── __init__.py
│   ├── test_server.py
│   ├── test_client.py
│   └── test_devices.py
│
├── docs/
│   ├── index.md
│   ├── installation.md
│   └── usage.md
│
└── examples/
    ├── device_discovery.py
    ├── remote_control.py
    └── stream_processing.py