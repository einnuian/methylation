#!/usr/bin/env python3
"""
Methylation Report Generator
Processes methylation data from raw export files and generates formatted Excel reports.
"""

import tkinter as tk
from tkinter import filedialog
from pathlib import Path
import sys
from data_parser import parse_qpcr_csv, get_all_samples
from report_generator import generate_report_win32, get_control_selection, extract_plate_info
from cli.settings import load_settings, save_setting


def get_template_file(assay_type):
    """
    Read the report template configured for an assay type.

    No template ships with the tool, so one must be chosen with
    `methyl config set-template` before any report can be generated.

    Args:
        assay_type (str): Detected assay type, e.g. 'BWS'

    Returns:
        Path: Path to the configured template, or None if none has been set
    """
    configured = load_settings().get(f"template_{assay_type.lower()}")

    return Path(configured) if configured else None


def get_saved_directory(key):
    """
    Read a remembered directory from the shared settings file.

    Args:
        key (str): Settings key holding the directory, e.g. 'last_directory'

    Returns:
        str: The saved directory if it still exists, otherwise None
    """
    saved = load_settings().get(key)

    # Discard the saved directory if it has since been moved or deleted
    if saved and Path(saved).exists():
        return saved

    return None


def detect_assay_type(filename):
    """
    Detect the assay type (BWS or RSS) from the filename.

    Args:
        filename (str): Name of the file

    Returns:
        tuple: (assay_type, target1_name, target2_name)
               e.g., ('BWS', 'ICR1', 'ICR2')
    """
    filename_upper = filename.upper()

    if filename_upper.startswith('BWS'):
        return 'BWS', 'ICR1', 'ICR2'
    elif filename_upper.startswith('RSS'):
        return 'RSS', 'PEG1', 'GRB'
    else:
        # Default to BWS if cannot detect
        print(f"Warning: Could not detect assay type from filename: {filename}")
        print("Defaulting to BWS (ICR1/ICR2)")
        return 'BWS', 'ICR1', 'ICR2'


def select_file(target_name, initial_dir=None):
    """
    Opens a file dialog to select a raw export file for a specific target.

    Args:
        target_name (str): Name of the target (e.g., "Target 1", "Target 2")
        initial_dir (Path or str, optional): Initial directory for the file dialog

    Returns:
        Path: Path to the selected file, or None if cancelled
    """
    # Determine initial directory
    if initial_dir and Path(initial_dir).exists():
        start_dir = initial_dir
    elif (Path.cwd() / "data").exists():
        start_dir = Path.cwd() / "data"
    else:
        start_dir = Path.cwd()

    # Create a root window and hide it
    root = tk.Tk()
    root.withdraw()

    # Open file dialog
    file_path = filedialog.askopenfilename(
        title=f"Select Raw Export File for {target_name}",
        filetypes=[
            ("CSV files", "*.csv"),
            ("All files", "*.*")
        ],
        initialdir=start_dir
    )

    # Destroy the root window
    root.destroy()

    # Return Path object or None
    return Path(file_path) if file_path else None


def select_output_directory(initial_dir=None):
    """
    Opens a directory dialog to choose where the generated reports are written.

    Args:
        initial_dir (Path or str, optional): Initial directory for the dialog

    Returns:
        Path: Path to the chosen directory, or None if cancelled
    """
    # Determine initial directory
    if initial_dir and Path(initial_dir).exists():
        start_dir = initial_dir
    else:
        start_dir = Path.cwd()

    # Create a root window and hide it
    root = tk.Tk()
    root.withdraw()

    # Open directory dialog
    dir_path = filedialog.askdirectory(
        title="Select Destination Folder for the Reports",
        initialdir=start_dir
    )

    # Destroy the root window
    root.destroy()

    # Return Path object or None
    return Path(dir_path) if dir_path else None


def main():
    """Main entry point for the methylation report generator."""
    print("Methylation Report Generator")
    print("=" * 50)
    print("\nThis tool processes qPCR data from two targets.")
    print("You will be prompted to select:")
    print("  1. Target 1 raw data file")
    print("  2. Target 2 raw data file")
    print("  3. Destination folder for the reports")
    print("=" * 50)

    # Load configuration
    last_dir = get_saved_directory('last_directory')

    if last_dir:
        print(f"\nLast used directory: {last_dir}")

    # Select Target 1 file
    print("\nStep 1: Select Target 1 raw data file...")
    target1_file = select_file("Target 1", initial_dir=last_dir)

    if not target1_file:
        print("No file selected for Target 1. Exiting.")
        sys.exit(0)

    # Check if Target 1 file exists
    if not target1_file.exists():
        print(f"Error: File not found: {target1_file}")
        sys.exit(1)

    print(f"Target 1 file: {target1_file.name}")
    print(f"File size: {target1_file.stat().st_size} bytes")

    # Use the directory from Target 1 for Target 2
    last_dir = str(target1_file.parent)

    # Select Target 2 file
    print("\nStep 2: Select Target 2 raw data file...")
    target2_file = select_file("Target 2", initial_dir=last_dir)

    if not target2_file:
        print("No file selected for Target 2. Exiting.")
        sys.exit(0)

    # Check if Target 2 file exists
    if not target2_file.exists():
        print(f"Error: File not found: {target2_file}")
        sys.exit(1)

    print(f"Target 2 file: {target2_file.name}")
    print(f"File size: {target2_file.stat().st_size} bytes")

    # Save the directory for next time
    save_setting('last_directory', str(target2_file.parent))

    # Detect assay type from the first file
    print("\n" + "=" * 50)
    print("Detecting assay type...")
    assay_type, target1_name, target2_name = detect_assay_type(target1_file.name)
    print(f"  Assay type: {assay_type}")
    print(f"  Targets: {target1_name}, {target2_name}")
    print("=" * 50)

    # Locate the template for the detected assay type before prompting for anything else,
    # so a missing template is reported without the user working through the prompts first
    template_file = get_template_file(assay_type)
    if template_file is None:
        print(f"\nError: No {assay_type} template has been set.")
        print(f"Choose one with: methyl config set-template {assay_type.lower()}")
        sys.exit(1)

    if not template_file.exists():
        print(f"\nError: Template file not found: {template_file}")
        print(f"Choose a new one with: methyl config set-template {assay_type.lower()}")
        sys.exit(1)
    print(f"\nUsing template: {template_file.name}")

    # Let the user choose where the reports are written, defaulting to the last choice
    print("\nStep 3: Select the destination folder for the reports...")
    output_dir = select_output_directory(
        initial_dir=get_saved_directory('last_output_directory') or str(target2_file.parent)
    )

    if not output_dir:
        print("No destination folder selected. Exiting.")
        sys.exit(0)

    save_setting('last_output_directory', str(output_dir))
    print(f"Reports will be saved to: {output_dir}")

    # Identify target files based on filename
    print("\n" + "=" * 50)
    print("Identifying target files...")
    if target1_name in target1_file.name.upper():
        target1_file_sorted = target1_file
        target2_file_sorted = target2_file
        print(f"  {target1_name}: {target1_file_sorted.name}")
        print(f"  {target2_name}: {target2_file_sorted.name}")
    elif target2_name in target1_file.name.upper():
        target1_file_sorted = target2_file
        target2_file_sorted = target1_file
        print(f"  {target1_name}: {target1_file_sorted.name}")
        print(f"  {target2_name}: {target2_file_sorted.name}")
    else:
        print(f"Warning: Could not identify {target1_name}/{target2_name} from filenames")
        print("Assuming:")
        target1_file_sorted = target1_file
        target2_file_sorted = target2_file
        print(f"  {target1_name}: {target1_file_sorted.name}")
        print(f"  {target2_name}: {target2_file_sorted.name}")

    print("=" * 50)

    # Parse data files
    print("\nParsing qPCR data files...")
    try:
        target1_data = parse_qpcr_csv(target1_file_sorted)
        print(f"  {target1_name}: {len(target1_data)} rows parsed")

        target2_data = parse_qpcr_csv(target2_file_sorted)
        print(f"  {target2_name}: {len(target2_data)} rows parsed")

        # Get list of all samples
        all_samples = get_all_samples(target1_data, target2_data)
        print(f"\nFound {len(all_samples)} unique samples")

        # Filter out control samples and NTC for the sample list
        positive_control = load_settings()["positive_control"]
        test_samples = [s for s in all_samples if not s.startswith('Control ')
                       and s != positive_control and s != 'NTC']

        print(f"Test samples available: {len(test_samples)}")

    except Exception as e:
        print(f"Error parsing data files: {e}")
        sys.exit(1)

    # Sample selection
    print("\n" + "=" * 50)
    print("Sample Selection")
    print("=" * 50)
    print(f"\nFound {len(test_samples)} test samples")
    print()
    print("Options:")
    print("  A. Process ALL samples (batch mode)")
    print("  S. Select specific sample")
    print("  0. Exit")
    print()

    # First, ask if they want all or specific
    while True:
        mode_choice = input("Enter choice (A/S/0): ").strip().upper()

        if mode_choice == '0':
            print("Exiting.")
            sys.exit(0)
        elif mode_choice == 'A':
            # Generate for all samples
            selected_samples = test_samples
            print(f"\nSelected: ALL {len(test_samples)} samples")
            break
        elif mode_choice == 'S':
            # Show list for individual selection
            print("\nAvailable test samples:")
            for i, sample in enumerate(test_samples, 1):
                print(f"  {i}. {sample}")
            print()

            while True:
                try:
                    choice = input(f"Select sample number (1-{len(test_samples)}): ").strip()
                    choice_num = int(choice)

                    if 1 <= choice_num <= len(test_samples):
                        # Generate for single sample
                        selected_samples = [test_samples[choice_num - 1]]
                        print(f"\nSelected: {selected_samples[0]}")
                        break
                    else:
                        print(f"Invalid choice. Please enter 1-{len(test_samples)}")
                except ValueError:
                    print("Invalid input. Please enter a number.")
            break
        else:
            print("Invalid choice. Please enter A, S, or 0.")

    # Get control selections
    print()
    target1_controls, target2_controls = get_control_selection(target1_name, target2_name, assay_type)

    # Extract plate information for filename
    plate_number, date_mmddyy, initials = extract_plate_info(target1_file_sorted.name)

    # Create the destination folder only once there is something to write into it
    output_dir.mkdir(parents=True, exist_ok=True)

    # Generate reports
    print("\n" + "=" * 50)
    print(f"Generating reports for {len(selected_samples)} sample(s)...")
    print("=" * 50)
    print()

    for i, sample_name in enumerate(selected_samples, 1):
        print(f"[{i}/{len(selected_samples)}] Processing: {sample_name}")

        # Create output filename: {sample_name}_{plate_number}_{initials}.xlsm
        safe_name = sample_name.replace(" ", "_").replace("/", "-")
        output_file = output_dir / f"{safe_name}_{plate_number}_{initials}.xlsm"

        try:
            generate_report_win32(
                target1_file_sorted, target2_file_sorted, template_file, output_file, sample_name,
                target1_controls, target2_controls, target1_name, target2_name
            )
            print(f"  ✓ Report saved: {output_file.name}")
            print()
        except Exception as e:
            print(f"  ✗ Error generating report: {e}")
            print()

    print("=" * 50)
    print("Report Generation Complete!")
    print(f"Output directory: {output_dir}")
    print("=" * 50)


if __name__ == "__main__":
    main()
