Hotel Management System
Overview
The Hotel Management System is a web-based application designed to streamline the operations of a hotel. It helps manage bookings, guests, rooms, invoices, and services, providing a professional and user-friendly interface. Built with Django, this system ensures efficiency, reliability, and scalability.

Features
Guest Management: Add, view, edit, and delete guest details.
Room Management: Manage room types, availability, and occupancy status.
Booking Management: Handle check-ins, check-outs, and extensions of stay.
Invoice Management: Automatically generate and update invoices for guests, including room and service charges.
Services Management: Add services to guest invoices (e.g., laundry, dining).
Daily Reports: Generate reports summarizing daily bookings, revenue, and room occupancy.
Dynamic Homepage: Display available rooms and navigation to key sections of the system.
User Authentication: Secure login and roles for staff and administrators.
Technologies Used
Backend: Django (Python)
Frontend: HTML, CSS, JavaScript
Database: SQLite (or Postgres/MySQL for production)
Other Tools: Bootstrap for styling, Docker for deployment (optional)
Prerequisites
Python 3.8 or higher
Django 4.x or higher
A web browser
Git (optional for cloning the repository)
Installation
Clone the repository:
git clone https:[//github.com/username/hotel-management-system.git](https://github.com/caseykingsley77/TSHotel.git
Navigate to the project directory:
cd hotel-management-system
Create a virtual environment and activate it:
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
Install dependencies:
pip install -r requirements.txt
Apply migrations to set up the database:
python manage.py migrate
Create a superuser:
python manage.py createsuperuser
Start the development server:
python manage.py runserver
Usage
Open your browser and go to http://127.0.0.1:8000.
Log in using the superuser credentials.
Explore the system's features:
Homepage: View available rooms and navigate to various sections.
Guests: Add and manage guest details.
Bookings: Manage check-ins, check-outs, and extensions.
Invoices: View and update guest invoices with room and service charges.
Reports: Access daily reports for analysis.
Screenshots
(Optional: Add screenshots of the system here for better visualization.)

Deployment
For production:

Set up a Postgres database and update settings.py.
Use a web server like Nginx or Apache with Gunicorn or uWSGI.
(Optional) Deploy using Docker:
docker-compose up --build
Contributing
Contributions are welcome! Please fork the repository and submit a pull request for review.

License
This project is licensed under the MIT License. See the LICENSE file for more details.

Contact
For questions or support, please contact:

Name: Ezennia O. Kingsley
Email: caseykingsley77@gmail.com
