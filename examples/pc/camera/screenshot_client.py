#!/usr/bin/env python3
"""
Screenshot Example

This script demonstrates how to take a screenshot of the current screen.
"""

import asyncio
import argparse
import logging
import os
from datetime import datetime


class ScreenshotExample:
    def __init__(self, debug: bool = False):
        """
        Initialize screenshot example.

        Args:
            debug: Enable debug logging
        """
        # Configure logging
        log_level = logging.DEBUG if debug else logging.INFO
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(self.__class__.__name__)

    async def take_screenshot(self, output_file: str = None) -> bool:
        """
        Take a screenshot of the current screen.

        Args:
            output_file: Path to save the screenshot. If None, a timestamped filename will be used.

        Returns:
            Success status
        """
        # Generate default filename if not provided
        if not output_file:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"screenshot_{timestamp}.png"

        try:
            # Try to use PyAutoGUI for screenshots (cross-platform)
            self.logger.info("Attempting to use PyAutoGUI for screenshot...")
            import pyautogui
            
            screenshot = pyautogui.screenshot()
            screenshot.save(output_file)
            self.logger.info(f"Screenshot saved to {output_file}")
            return True
            
        except ImportError:
            self.logger.warning("PyAutoGUI not available, trying alternative methods...")
            
            # Try using PIL directly
            try:
                from PIL import ImageGrab
                
                self.logger.info("Taking screenshot with PIL...")
                screenshot = ImageGrab.grab()
                screenshot.save(output_file)
                self.logger.info(f"Screenshot saved to {output_file}")
                return True
                
            except ImportError:
                self.logger.warning("PIL not available, trying platform-specific methods...")
                
                # Try platform-specific methods
                import platform
                system = platform.system()
                
                if system == 'Linux':
                    # Try using scrot on Linux
                    try:
                        import subprocess
                        self.logger.info("Taking screenshot with scrot...")
                        subprocess.run(['scrot', output_file], check=True)
                        self.logger.info(f"Screenshot saved to {output_file}")
                        return True
                    except Exception as e:
                        self.logger.error(f"Failed to take screenshot with scrot: {e}")
                        
                    # Try using gnome-screenshot as an alternative
                    try:
                        import subprocess
                        self.logger.info("Taking screenshot with gnome-screenshot...")
                        subprocess.run(['gnome-screenshot', '-f', output_file], check=True)
                        self.logger.info(f"Screenshot saved to {output_file}")
                        return True
                    except Exception as e:
                        self.logger.error(f"Failed to take screenshot with gnome-screenshot: {e}")
                        
                elif system == 'Windows':
                    # Use PowerShell on Windows
                    try:
                        import subprocess
                        self.logger.info("Taking screenshot with Windows PowerShell...")
                        ps_cmd = (
                            "$OutputFile = '" + os.path.abspath(output_file).replace('\\', '\\\\') + "';"
                            "[void] [System.Reflection.Assembly]::LoadWithPartialName('System.Drawing');"
                            "[void] [System.Reflection.Assembly]::LoadWithPartialName('System.Windows.Forms');"
                            "$bounds = [System.Windows.Forms.Screen]::PrimaryScreen.Bounds;"
                            "$bitmap = New-Object System.Drawing.Bitmap $bounds.Width, $bounds.Height;"
                            "$graphics = [System.Drawing.Graphics]::FromImage($bitmap);"
                            "$graphics.CopyFromScreen($bounds.X, $bounds.Y, 0, 0, $bounds.Size);"
                            "$bitmap.Save($OutputFile);"
                            "$graphics.Dispose();"
                            "$bitmap.Dispose();"
                        )
                        subprocess.run(['powershell', '-Command', ps_cmd], check=True)
                        self.logger.info(f"Screenshot saved to {output_file}")
                        return True
                    except Exception as e:
                        self.logger.error(f"Failed to take screenshot with PowerShell: {e}")
                        
                elif system == 'Darwin':  # macOS
                    # Use screencapture on macOS
                    try:
                        import subprocess
                        self.logger.info("Taking screenshot with macOS screencapture...")
                        subprocess.run(['screencapture', output_file], check=True)
                        self.logger.info(f"Screenshot saved to {output_file}")
                        return True
                    except Exception as e:
                        self.logger.error(f"Failed to take screenshot with screencapture: {e}")
                
                self.logger.error("No screenshot method available for this platform")
                return False
                
        except Exception as e:
            self.logger.error(f"Failed to take screenshot: {e}")
            return False


async def main():
    """
    Run the screenshot example.
    """
    parser = argparse.ArgumentParser(description='Screenshot Example')
    parser.add_argument('--debug', action='store_true', help='Enable debug logging')
    parser.add_argument('--output', help='Output file path')
    
    args = parser.parse_args()
    
    example = ScreenshotExample(debug=args.debug)
    await example.take_screenshot(args.output)


if __name__ == "__main__":
    asyncio.run(main())
