# Local Shop POS System

A Django-based Point of Sale (POS) and shop management system designed for local shop environments. The application features user roles, order management, stock tracking, and accountability tracking.

## Features

- **Multi-Role User Accounts**:
  - **Admin**: Full dashboard access, stock, sales, and user management.
  - **Attendant**: Add products to cart and create customer orders.
  - **Cashier**: Processes payments for pending orders.
  - **Dispatcher**: Dispatches paid orders to customers using a token system.
- **Inventory Tracking**: Manage products, prices, cost prices, and stock quantity levels.
- **Order Lifecycle**: Order status transitions from `Pending` -> `Paid` -> `Dispatched`.
- **Accountability Logging**: Logs user activity actions to maintain a transparent audit trail.
- **Token System**: Generates random 3-digit order tokens for smooth pickup and dispatch.

## Tech Stack

- **Backend**: Django 6.x
- **Frontend**: HTML5, CSS3, JavaScript (dynamic updates)
- **Database**: SQLite (default local DB)

## Setup and Installation

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/Nyisulya/local-shop.git
   cd local-shop
   ```

2. **Set up a Virtual Environment**:
   ```bash
   python -m venv venv
   # On Windows:
   .\venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Apply Database Migrations**:
   ```bash
   python manage.py migrate
   ```

5. **Start Development Server**:
   ```bash
   python manage.py runserver
   ```
   Open your browser and navigate to `http://127.0.0.1:8000/`.

## License

This project is open-source. Feel free to use and adapt it as needed.
