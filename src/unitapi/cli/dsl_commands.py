import click
import asyncio
import sys
import os
from pathlib import Path
from typing import Dict, Any, Optional

from unitapi.config.loader import ConfigLoader
from unitapi.dsl.validators.schema import validate_config_with_details
from unitapi.dsl.runtime.executor import DSLExecutor


@click.group()
def dsl():
    """DSL configuration commands for UnitAPI"""
    pass


@dsl.command()
@click.argument("config_file", type=click.Path(exists=True))
@click.option("--dry-run", is_flag=True, help="Validate without executing")
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose output")
def run(config_file, dry_run, verbose):
    """Run UnitAPI from DSL configuration file"""
    try:
        # Load configuration
        click.echo(f"Loading configuration from {config_file}")
        config = ConfigLoader.load(config_file)

        # Validate configuration
        is_valid, error = validate_config_with_details(config)
        if not is_valid:
            click.echo(f"✗ Configuration is invalid: {error}", err=True)
            sys.exit(1)

        click.echo(f"✓ Configuration is valid")
        click.echo(f"  Version: {config.get('version')}")
        click.echo(f"  Extensions: {len(config.get('extensions', []))}")
        click.echo(f"  Devices: {len(config.get('devices', []))}")
        click.echo(f"  Pipelines: {len(config.get('pipelines', []))}")

        if dry_run:
            click.echo("Dry run completed successfully")
            return

        # Initialize UnitAPI
        click.echo("Initializing UnitAPI")
        from unitapi import UnitAPI

        unitapi = UnitAPI()

        # Set up executor
        executor = DSLExecutor(unitapi)

        # Run configuration
        async def run_async():
            click.echo("Executing configuration")
            await executor.execute_config(config)
            click.echo("Configuration executed successfully")

            # Keep running until interrupted
            try:
                click.echo("Press Ctrl+C to stop")
                while True:
                    await asyncio.sleep(1)
            except KeyboardInterrupt:
                click.echo("\nStopping...")
                await executor.stop_all()
                await executor.cleanup()

        asyncio.run(run_async())

    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        if verbose:
            import traceback

            click.echo(traceback.format_exc(), err=True)
        sys.exit(1)


@dsl.command()
@click.argument("config_file", type=click.Path(exists=True))
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose output")
def validate(config_file, verbose):
    """Validate DSL configuration file"""
    try:
        # Load configuration
        click.echo(f"Loading configuration from {config_file}")
        config = ConfigLoader.load(config_file)

        # Validate configuration
        is_valid, error = validate_config_with_details(config)

        if is_valid:
            click.echo(f"✓ Configuration is valid")
            click.echo(f"  Version: {config.get('version')}")
            click.echo(f"  Extensions: {len(config.get('extensions', []))}")
            click.echo(f"  Devices: {len(config.get('devices', []))}")
            click.echo(f"  Pipelines: {len(config.get('pipelines', []))}")
        else:
            click.echo(f"✗ Configuration is invalid: {error}", err=True)
            sys.exit(1)

    except Exception as e:
        click.echo(f"✗ Validation error: {e}", err=True)
        if verbose:
            import traceback

            click.echo(traceback.format_exc(), err=True)
        sys.exit(1)


@dsl.command()
@click.argument("source_file", type=click.Path(exists=True))
@click.argument("target_format", type=click.Choice(["yaml", "hcl", "star", "ua"]))
@click.option("--output", "-o", help="Output file (default: stdout)")
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose output")
def convert(source_file, target_format, output, verbose):
    """Convert between DSL formats"""
    try:
        # Convert configuration
        click.echo(f"Converting {source_file} to {target_format}")
        result = ConfigLoader.convert_file(source_file, target_format, output)

        # Output result
        if output:
            click.echo(f"Converted to {output}")
        else:
            click.echo(result)

    except Exception as e:
        click.echo(f"Conversion error: {e}", err=True)
        if verbose:
            import traceback

            click.echo(traceback.format_exc(), err=True)
        sys.exit(1)


@dsl.command()
@click.argument("format", type=click.Choice(["yaml", "hcl", "star", "ua"]))
@click.option("--output", "-o", help="Output file (default: stdout)")
def template(format, output):
    """Generate template configuration in specified format"""
    templates = {
        "yaml": """# UnitAPI YAML Configuration
version: "1.0"

extensions:
  - !extension
    name: keyboard
    version: ">=1.0.0"
    config:
      layout: "us"

devices:
  - !device
    id: "pc-main"
    device_type: "computer"
    capabilities: ["keyboard", "mouse", "display"]

pipelines:
  - !pipeline
    name: "example"
    source: "pc-main"
    steps:
      - action: "capture"
        params:
          device: "keyboard"
""",
        "hcl": """# UnitAPI HCL Configuration

version = "1.0"

extension "keyboard" {
  version = ">=1.0.0"
  config {
    layout = "us"
  }
}

device "pc-main" {
  type = "computer"
  capabilities = ["keyboard", "mouse", "display"]
}

pipeline "example" {
  source = "pc-main"
  
  step "capture" {
    device = "keyboard"
  }
}
""",
        "star": """# UnitAPI Starlark Configuration

VERSION = "1.0"

keyboard_ext = extension(
    name = "keyboard",
    version = ">=1.0.0",
    config = {
        "layout": "us"
    }
)

pc_main = device(
    id = "pc-main",
    type = "computer",
    capabilities = ["keyboard", "mouse", "display"]
)

example_pipeline = pipeline(
    name = "example",
    source = pc_main.id,
    steps = [
        step("capture", device="keyboard"),
    ]
)
""",
        "ua": """# UnitAPI Simple DSL Configuration

version "1.0"

# Load extensions
load keyboard version=">=1.0.0" config={layout:"us"}

# Define devices
device pc-main type=computer with keyboard,mouse,display

# Define pipelines
pipeline example from pc-main:
  capture keyboard
end
""",
    }

    template = templates[format]

    if output:
        with open(output, "w") as f:
            f.write(template)
        click.echo(f"Template written to {output}")
    else:
        click.echo(template)


@dsl.command()
@click.option(
    "--format",
    "-f",
    type=click.Choice(["yaml", "hcl", "star", "ua"]),
    default="yaml",
    help="Format to use for the new configuration",
)
@click.option("--output", "-o", help="Output file (default: unitapi.{format})")
def init(format, output):
    """Initialize a new UnitAPI DSL configuration"""
    if not output:
        output = f"unitapi.{format}"

    if os.path.exists(output):
        if not click.confirm(f"File {output} already exists. Overwrite?"):
            click.echo("Aborted")
            return

    # Generate template
    template_cmd = template.callback(format=format, output=output)

    click.echo(f"Initialized new UnitAPI DSL configuration in {output}")
    click.echo("Edit this file to configure your UnitAPI setup")
    click.echo(f"Then run: unitapi dsl run {output}")


@dsl.command()
@click.option("--list", "list_deps", is_flag=True, help="List required dependencies")
@click.option("--install", is_flag=True, help="Install required dependencies")
def deps(list_deps, install):
    """Manage DSL dependencies"""
    dependencies = {
        "yaml": ["pyyaml>=6.0"],
        "hcl": ["python-hcl2>=3.0.5"],
        "star": ["starlark>=0.4.0"],
        "schema": ["pydantic>=1.9.0"],
    }

    if list_deps:
        click.echo("Required dependencies for UnitAPI DSL:")
        for category, deps in dependencies.items():
            click.echo(f"\n{category.upper()} format:")
            for dep in deps:
                click.echo(f"  - {dep}")

    if install:
        import subprocess

        click.echo("Installing dependencies...")
        all_deps = []
        for deps in dependencies.values():
            all_deps.extend(deps)

        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install"] + all_deps)
            click.echo("Dependencies installed successfully")
        except subprocess.CalledProcessError as e:
            click.echo(f"Error installing dependencies: {e}", err=True)
            sys.exit(1)


@dsl.command()
@click.argument("config_file", type=click.Path(exists=True))
@click.option(
    "--format",
    "-f",
    type=click.Choice(["yaml", "hcl", "star", "ua"]),
    default="yaml",
    help="Output format",
)
def info(config_file, format):
    """Display information about a DSL configuration"""
    try:
        # Load configuration
        config = ConfigLoader.load(config_file)

        # Display information
        click.echo(f"Configuration: {config_file}")
        click.echo(f"Format: {Path(config_file).suffix[1:]}")
        click.echo(f"Version: {config.get('version')}")

        # Extensions
        click.echo("\nExtensions:")
        for ext in config.get("extensions", []):
            click.echo(f"  - {ext.name} (version: {ext.version})")
            if ext.config:
                click.echo(f"    Config: {ext.config}")

        # Devices
        click.echo("\nDevices:")
        for device in config.get("devices", []):
            click.echo(f"  - {device.id} (type: {device.device_type})")
            if device.capabilities:
                click.echo(f"    Capabilities: {', '.join(device.capabilities)}")

        # Pipelines
        click.echo("\nPipelines:")
        for pipeline in config.get("pipelines", []):
            click.echo(f"  - {pipeline.name}")
            if pipeline.source:
                click.echo(f"    Source: {pipeline.source}")
            if pipeline.target:
                click.echo(f"    Target: {pipeline.target}")
            if pipeline.steps:
                click.echo(f"    Steps:")
                for step in pipeline.steps:
                    click.echo(f"      - {step.action}")
                    if step.params:
                        click.echo(f"        Params: {step.params}")

    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)
