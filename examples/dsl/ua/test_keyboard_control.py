#!/usr/bin/env python3
"""
UnitAPI DSL Keyboard Control Test

This script demonstrates how to use UnitAPI DSL to control a keyboard
using the .ua configuration format.
"""

import os
import sys
import asyncio
import logging
import argparse
from pathlib import Path

# Add the directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from unitapi.main import unitapi as UnitAPI
from unitapi.config.loader import ConfigLoader
from unitapi.dsl.validators.schema import validate_config_with_details
from unitapi.dsl.runtime.executor import DSLExecutor

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def run_server(config_path):
    """Run the keyboard server using the specified configuration file"""
    logger.info(f"Starting keyboard server with configuration: {config_path}")
    
    # Load the configuration
    config = ConfigLoader.load(str(config_path))
    
    # Validate the configuration
    is_valid, error = validate_config_with_details(config)
    if not is_valid:
        logger.error(f"Invalid server configuration: {error}")
        return None
    
    # Initialize UnitAPI
    unitapi = UnitAPI()
    
    # Set up executor
    executor = DSLExecutor(unitapi)
    
    # Execute the configuration
    await executor.execute_config(config)
    logger.info("Server configuration executed successfully")
    
    return executor

async def run_client(config_path):
    """Run the keyboard client using the specified configuration file"""
    logger.info(f"Starting keyboard client with configuration: {config_path}")
    
    # Load the configuration
    config = ConfigLoader.load(str(config_path))
    
    # Validate the configuration
    is_valid, error = validate_config_with_details(config)
    if not is_valid:
        logger.error(f"Invalid client configuration: {error}")
        return None
    
    # Initialize UnitAPI
    unitapi = UnitAPI()
    
    # Set up executor
    executor = DSLExecutor(unitapi)
    
    # Execute the configuration
    await executor.execute_config(config)
    logger.info("Client configuration executed successfully")
    
    return executor

async def main():
    """Main function to test keyboard control using UnitAPI DSL"""
    parser = argparse.ArgumentParser(description='UnitAPI DSL Keyboard Control Test')
    parser.add_argument('--mode', choices=['server', 'client', 'interactive'], required=True,
                        help='Run mode: server, client, or interactive')
    parser.add_argument('--server-config', default='keyboard_server.ua',
                        help='Path to the server configuration file')
    parser.add_argument('--client-config', default='keyboard_client.ua',
                        help='Path to the client configuration file')
    parser.add_argument('--interactive-config', default='keyboard_client_interactive.ua',
                        help='Path to the interactive client configuration file')
    parser.add_argument('--host', default='localhost',
                        help='Server host (for client mode)')
    parser.add_argument('--port', type=int, default=7890,
                        help='Server port (for client mode)')
    parser.add_argument('--text', default='Hello from UnitAPI DSL!',
                        help='Text to type (for client mode)')
    
    args = parser.parse_args()
    
    # Resolve configuration file paths
    config_dir = Path(__file__).parent
    server_config_path = config_dir / args.server_config
    client_config_path = config_dir / args.client_config
    interactive_config_path = config_dir / args.interactive_config
    
    # Update host and port in client configurations if specified
    if args.host != 'localhost' or args.port != 7890:
        if args.mode in ['client', 'interactive']:
            config_path = client_config_path if args.mode == 'client' else interactive_config_path
            if config_path.exists():
                with open(config_path, 'r') as f:
                    content = f.read()
                
                # Replace host and port
                content = content.replace('host="localhost"', f'host="{args.host}"')
                content = content.replace('port=7890', f'port={args.port}')
                
                with open(config_path, 'w') as f:
                    f.write(content)
                
                logger.info(f"Updated {args.mode} configuration with host={args.host}, port={args.port}")
    
    # Update text in client configuration if specified
    if args.text != 'Hello !' and args.mode == 'client':
        if client_config_path.exists():
            with open(client_config_path, 'r') as f:
                content = f.read()
            
            # Replace text
            content = content.replace('text:"Hello !"', f'text:"{args.text}"')
            
            with open(client_config_path, 'w') as f:
                f.write(content)
            
            logger.info(f"Updated client configuration with text='{args.text}'")
    
    try:
        if args.mode == 'server':
            # Run server
            if not server_config_path.exists():
                logger.error(f"Server configuration file not found: {server_config_path}")
                return
            
            executor = await run_server(server_config_path)
            if executor:
                logger.info("Keyboard server is running. Press Ctrl+C to stop.")
                try:
                    while True:
                        await asyncio.sleep(1)
                except KeyboardInterrupt:
                    logger.info("Stopping keyboard server...")
                finally:
                    await executor.stop_all()
                    await executor.cleanup()
        
        elif args.mode == 'client':
            # Run client
            if not client_config_path.exists():
                logger.error(f"Client configuration file not found: {client_config_path}")
                return
            
            executor = await run_client(client_config_path)
            if executor:
                logger.info("Client executed successfully.")
                await executor.stop_all()
                await executor.cleanup()
        
        elif args.mode == 'interactive':
            # Run interactive client
            if not interactive_config_path.exists():
                logger.error(f"Interactive client configuration file not found: {interactive_config_path}")
                return
            
            executor = await run_client(interactive_config_path)
            if executor:
                logger.info("Interactive client is running. Follow the prompts to send text.")
                try:
                    while True:
                        await asyncio.sleep(1)
                except KeyboardInterrupt:
                    logger.info("Stopping interactive client...")
                finally:
                    await executor.stop_all()
                    await executor.cleanup()
    
    except Exception as e:
        logger.error(f"Error: {e}")
        import traceback
        logger.error(traceback.format_exc())

if __name__ == "__main__":
    asyncio.run(main())
