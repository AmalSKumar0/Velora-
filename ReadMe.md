# Velora - Digital Art Marketplace

Welcome to the **Velora** repository! Velora is a comprehensive web platform built with Django that connects clients looking for custom digital artwork with talented artists.

## Documentation

For an in-depth look at how Velora is structured and operates, please refer to the files in the `documentation/` directory:

*   **[Features & Workflows](documentation/features.md)**: A detailed breakdown of user roles (Admin, Artist, Client), portfolio management, and escrow payment systems.
*   **[Architecture & Order Flow](documentation/architecture.md)**: Flowcharts and sequence diagrams detailing the exact life cycle of an order from request to final delivery.

## Getting Started

### Prerequisites
- Python 3.x
- MySQL
- Environment Variables (`.env` file configured with `SECRET_KEY`, `DEBUG`, database credentials, and Razorpay API keys)

### Installation

1.  Clone the repository and navigate into the project directory.
2.  Install the dependencies:
    ```bash
    pip install -r requirements.txt
    ```
3.  Set up your `.env` file based on the environment variables required in `artwork_system/settings.py`.
4.  Run migrations to set up the database schema:
    ```bash
    python manage.py makemigrations
    python manage.py migrate
    ```
5.  Start the development server:
    ```bash
    python manage.py runserver
    ```
## Screenshots

## Technology Stack
*   **Backend:** Django (Python)
*   **Database:** MySQL
*   **Payments:** Razorpay Integration
*   **PDF Generation:** WeasyPrint (for Admin Reports)
*   **Frontend:** HTML, TailwindCSS, JavaScript