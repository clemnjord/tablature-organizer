import os
import re
import sys
import logging
from datetime import datetime
from pathlib import Path
from os import listdir
import click


# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')


@click.command()
@click.option('--input', required=True, help='Input folder containing tablatures.', type=click.Path(exists=True, file_okay=False))
@click.option('--output', required=True, help='Output folder for organized tablatures.', type=click.Path(file_okay=False))
def organize_tabs(input: str, output: str) -> None:
    """
    Organizes tablatures by moving files into artist-specific folders.

    Args:
        input (str): The input directory path.
        output (str): The output directory path.
    """
    input_dir = Path(input)
    output_dir = Path(output)

    if output_dir in input_dir.parents:
        logging.error("Output directory is inside input directory. Aborting to prevent recursion.")
        sys.exit(1)

    only_files = [f for f in input_dir.iterdir() if f.is_file()]

    for file in only_files:
        store_file(file, input_dir, output_dir)

    logging.info("Tablature organization complete!")


def store_file(filepath: Path, input_dir: Path, output_dir: Path):
    """
    Store the tablature file in the appropriate artist folder based on its name.

    Args:
        filename (str): The name of the file to be moved.
        input_dir (Path): The directory from which to move the file.
        output_dir (Path): The base directory where artist folders are created.
    """
    tablature_regex = r"(.+)\s-\s.+[.]{1}\w+$"
    match = re.fullmatch(tablature_regex, filepath.name)

    if not match:
        logging.warning(f"Filename '{filepath.name}' does not match expected pattern. Skipping.")
        return

    artist = get_artist(filepath.name)
    output_dir = create_folder(artist, output_dir)
    move_file(filepath, output_dir)


def get_artist(filename: str) -> str:
    """
        Extract and reformat the artist's name from the filename.

        Args:
            filename (str): The name of the file to extract the artist from.

        Returns:
            str: The reformatted artist name.
        """
    artist_regex = r"(.+?)\s-\s"
    match = re.match(artist_regex, filename)

    if not match:
        raise ValueError(f"Unable to extract artist from '{filename}'.")

    return reformat_artist(match.group(1))


def reformat_artist(name: str) -> str:
    """
    Reformat the artist's name, handling special cases for 'The'.

    Args:
        name (str): The artist's name.

    Returns:
        str: Reformatted artist name.
    """
    match = re.match(r"(?i)^the\s+(.+)", name)

    if match:
        rest_of_name = match.group(1).title()
        return f"{rest_of_name}, The"
    else:
        return name.title()

def create_folder(artist_name: str, output_dir: Path) -> Path:
    """
    Create a directory for the artist if it doesn't exist.

    Args:
        artist_name (str): The name of the artist.
        output_dir (Path): The base output directory.

    Returns:
        Path: The path to the artist's folder.
    """
    artist_dir = output_dir.joinpath(artist_name)
    artist_dir.mkdir(parents=True, exist_ok=True)
    return artist_dir


def move_file(filepath: Path, output_dir: Path):
    """
    Move a file to the specified output directory, appending a timestamp if it already exists.

    Args:
        filepath (Path): The path to the file to be moved.
        output_dir (Path): The target directory.
    """
    target_path = output_dir.joinpath(filepath.name)

    if target_path.exists():
        timestamp = datetime.now().strftime("_%d%m%Y_%H%M%S")
        target_path = output_dir.joinpath(filepath.stem + timestamp + filepath.suffix)
        logging.info(f"File '{filepath.name}' already exists. Renaming to '{target_path.name}'.")

    try:
        filepath.rename(target_path)
        logging.info(f"Moved '{filepath.name}' to '{target_path.parent}'.")
    except Exception as e:
        logging.error(f"Failed to move '{filepath.name}' to '{target_path.parent}': {e}")


if __name__ == "__main__":
    organize_tabs()

