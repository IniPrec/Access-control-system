<<<<<<< HEAD
# Access Control System

A Django-based web application designed to manage and monitor access control within a facility. This system allows administrators to control entry and exit points, manage user permissions, and maintain logs of access events.
=======
# Access-control-system

A Django-based web application designed to manage and monitor access control within a university. This system allows administrators to control entry and exit points, manage user permissions, and maintain logs of access events.
>>>>>>> 91a4d54d9e0dc4a46d318dceeb97270c5d222c4d

## Features

* **User Management**: Create, update, and delete user profiles with specific access rights.
* **Access Points Control**: Define and manage various entry and exit points within the facility.
* **Access Logs**: Maintain detailed logs of all access events for auditing purposes.
* **Media Integration**: Capture and associate images with access events for enhanced security.

## Project Structure
<<<<<<< HEAD

=======
>>>>>>> 91a4d54d9e0dc4a46d318dceeb97270c5d222c4d
```
access-control-system/
├── access_control_system/    # Main Django project directory
├── core/                     # Application logic and models
├── media/                    # Uploaded media files
├── photo/                    # Directory for storing captured photos
├── Simulators/               # Simulation scripts or tools
├── db.sqlite3                # SQLite database file
├── manage.py                 # Django management script
└── README.md                 # Project documentation
```

## Installation
<<<<<<< HEAD

1. **Clone the repository**:

=======
1. Clone the repository:
>>>>>>> 91a4d54d9e0dc4a46d318dceeb97270c5d222c4d
   ```bash
   git clone https://github.com/IniPrec/Access-control-system.git
   cd Access-control-system
   ```
<<<<<<< HEAD

2. **Create a virtual environment**:

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

4. **Apply migrations**:

   ```bash
   python manage.py migrate
   ```

5. **Run the development server**:

   ```bash
   python manage.py runserver
   ```

6. **Access the application**:

   Open your browser and navigate to `http://127.0.0.1:8000/`
=======
2. Create a virtual environment:
   ```bash
   python -m venv venv
   .env\Script\Activate.ps1
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Apply migrations:
   ```bash
   python manage.py migrate
   ```
5. Run the development server:
   ```bash
   python manage.py runserver
   ```
6. Access the application:
   Open your browser and navigate to http://127.0.0.1:8000/
>>>>>>> 91a4d54d9e0dc4a46d318dceeb97270c5d222c4d

## Usage

* **Admin Panel**: Access the Django admin interface at `http://127.0.0.1:8000/admin/` to manage users and access points.
* **Access Logs**: View and filter access logs to monitor entry and exit events.
* **Media Files**: Captured images are stored in the `media/` directory and can be reviewed as needed.

<<<<<<< HEAD
## Contributing

Contributions are welcome! Please fork the repository and submit a pull request for any enhancements or bug fixes.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Acknowledgments

This project was inspired by the need for a customizable and efficient access control system suitable for various facilities.
=======
## Acknowledgment
>>>>>>> 91a4d54d9e0dc4a46d318dceeb97270c5d222c4d
