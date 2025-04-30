import sys
import os

print("Python Path:")
for path in sys.path:
    print(path)

print("\nTrying to find unitapi package:")
try:
    import unitapi
    print(f"unitapi package found at: {unitapi.__file__}")
    try:
        import unitapi.core
        print(f"unitapi.core found at: {unitapi.core.__file__}")
    except ImportError as e:
        print(f"Failed to import unitapi.core: {e}")
except ImportError as e:
    print(f"Failed to import unitapi: {e}")

print("\nChecking if src/unitapi/core exists:")
core_path = os.path.join(os.getcwd(), 'src', 'unitapi', 'core')
print(f"Looking for: {core_path}")
print(f"Directory exists: {os.path.exists(core_path)}")
if os.path.exists(core_path):
    print("Contents:")
    print(os.listdir(core_path))
