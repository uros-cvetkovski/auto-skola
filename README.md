# Driving School — Desktop Application

A desktop application for managing driving school operations, developed as a student project.

## About

The application provides records management for candidates, instructors, lessons, and exams with a modern dark UI.

## Technologies

- **Python 3.11**
- **CustomTkinter** — modern GUI framework
- **SQLite** — local database
- **Pillow** — image and icon processing

## Features

- **Dashboard** — overview of key statistics
- **Candidates** — adding, viewing, and managing candidates
- **Instructors** — instructor and category records
- **Lessons** — scheduling and tracking driving lessons
- **Exams** — records for theory and practical exams

## Getting Started

### Prerequisites

```bash
pip install customtkinter pillow
```

### Running the Application

```bash
git clone https://github.com/uros-cvetkovski/auto-skola.git
cd auto-skola
python main.py
```

## Project Structure

```
auto_skola/
├── main.py              # Application entry point
├── database/
│   └── db_manager.py    # SQLite database management
├── models/
│   ├── kandidat.py
│   ├── instruktor.py
│   └── cas_ispit.py
├── views/
│   ├── dashboard_view.py
│   ├── kandidati_view.py
│   ├── instruktori_view.py
│   ├── casovi_view.py
│   └── ispiti_view.py
└── assets/
    └── icons/
```

## Screenshots

![Dashboard](assets/icons/dashboard_screenshot.png)
![Candidates](assets/icons/kandidati_screenshot.png)

## Author

**Uroš Cvetkovski** — [github.com/uros-cvetkovski](https://github.com/uros-cvetkovski)
