# CargoHub REST API

This repository contains the development of a Warehouse Management System (WMS) for CargoHub, a company specializing in the handling and storage of goods.

## Background

CargoHub previously used a custom-built software solution for processing data and managing critical process flows via an API. However, the software lacks essential components such as documentation, tests, and repositories, making further development challenging. Additionally, the original development company is no longer active, leaving us with the responsibility to map, document, and enhance the software.

## Features

### Warehouse

Manage warehouse operations including storage and retrieval of goods.

### Transfer

Handle the transfer of goods between different locations.

### Shipment

Manage the shipment process including tracking and delivery.

### Client

Manage client information and interactions.

### Supplier

Handle supplier information and orders.

### Order

Manage customer orders and processing.

### Inventory

Track and manage inventory levels and stock.

### Location

Manage different storage locations within the warehouse.

### Item

Handle individual items including details and specifications.

### Item group

Manage groups of items for easier categorization.

### Item type

Define and manage different types of items.

### Item line

Handle specific lines of items within orders.

## Setup

1. Clone the repository:

   ```bash
   git clone https://github.com/Stef-Buurman/CargoHubGLR.git
   cd CargoHubGLR
   ```

2. Create a virtual environment:

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. Install the project dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Set up the database:

   ```bash
   cd app
   python create_db.py
   ```

5. Run the development server:
   ```bash
   python main.py
   ```

## Usage

To use the REST API, follow these steps:

1. Ensure the development server is running:

   ```bash
   python main.py
   ```

2. Use a tool like `curl` or Postman to interact with the API. For example, to get a list of items:

   ```bash
   curl -X GET http://127.0.0.1:8000/api/v2/items
   ```

3. Refer to the API documentation for detailed information on available endpoints and their usage using the following url:
   ```bash
   http://127.0.0.1:8000/docs
   ```
