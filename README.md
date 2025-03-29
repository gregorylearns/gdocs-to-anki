# GDocs to Anki Converter

A desktop app that converts Google Docs tables (exported as `.zip`) into Anki decks (`.apkg`), making flashcard creation simple and fast.

HTML to markdown conversion is done by this [binary](https://github.com/JohannesKaufmann/html-to-markdown). This is the easiest conversion from html to md that i've found that works. Currently working on a python implementation of it. But as of now, this is what works.

## Features

- Converts Google Docs tables to Anki flashcards
- Easy file selection and deck naming
- Quick access to `collections.media` and exported images
- Automatic update check from GitHub

## Installation

### Download

Download from the [releases](/releases/latest) page.

### Building

- Python 3.8+
- Libraries: `PyQt6`, `html2md2csv`

#### Steps

1. Clone the repo:
   ```bash
   git clone https://github.com/yourusername/gdocs-to-anki.git
   cd gdocs-to-anki
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the app:
   ```bash
   python main.py
   ```

## Usage
1. Format your google docs to have a 3-column table
- Those in the first column will be removed
- In the second column is Front of the Card
- Third Column is the back of the card
2. Select ZIP file: Export a Google Doc as .zip and choose it.
2. Name your deck: Enter a deck name.
3. Create deck: Click "Create .apkg" to generate your Anki deck.

## Roadmap

1. Remove reliance on the html2md binaries by working on own bs4 or other parsing
2. Integrate to anki as an addon - AnkiHub


## Contribution
We welcome contributions! Please create a pull request.

## License
This project is licensed under the GNU GPLv3 License. See the [LICENSE](LICENSE) file for details.

## Support
If you encounter any issues or have any questions, feel free to open an issue in this repository or contact us at support@example.com.

## Credits
Made with ❤️ for batch syncytium.

## Disclaimer
This software is provided "as is", without warranty of any kind, express or implied, including but not limited to the warranties of merchantability, fitness for a particular purpose, and non-infringement. In no event shall the authors or copyright holders be liable for any claim, damages, or other liability arising from, out of, or in connection with the software or the use or other dealings in the software.