# Test Images for Fluently

All images sourced from Unsplash (free license, no attribution required) and Pexels (free license).

## Handwritten Text (tests vision/handwriting pipeline)

| File | Source | Description |
|------|--------|-------------|
| `handwritten_text_01.jpg` | Unsplash | Handwritten text on paper |
| `handwritten_letter_02.jpg` | Unsplash | Person writing with pen |
| `handwritten_notes_03.jpg` | Unsplash | Notebook with handwritten notes |
| `handwritten_note_pexels_01.jpg` | Pexels | Handwritten note on white paper |
| `notebook_handwritten_pexels_02.jpg` | Pexels | Open handwritten notebook |
| `handwritten_paper_pexels_03.jpg` | Pexels | Handwritten note on paper |

## Printed Text / Signs (tests OCR pipeline)

| File | Source | Description |
|------|--------|-------------|
| `printed_sign_french_01.jpg` | Unsplash | French signage |
| `printed_menu_01.jpg` | Unsplash | Printed menu/text |

## Multilingual Signs (tests language detection + translation)

| File | Source | Description |
|------|--------|-------------|
| `japanese_sign_01.jpg` | Unsplash | Japanese street/text |
| `street_sign_spanish_01.jpg` | Unsplash | Spanish street sign |
| `korean_sign_01.jpg` | Unsplash | Korean text/signage |
| `arabic_text_01.jpg` | Unsplash | Arabic calligraphy/text |

## Usage

These images test the full range of Fluently's image translation:
- **Handwritten**: Exercises the vision model pipeline (27b or 12b fallback)
- **Printed**: Exercises the Tesseract OCR pipeline
- **Multilingual**: Exercises language detection + cross-language translation
