"""
Creates a small, FAKE sample database for the "Ask your data" project.

Run this ONCE before starting the app:

    python create_database.py

It creates a file called transport.db with four tables:
transportation_companies, buses, drivers, and tickets.

IMPORTANT: This is pretend data inspired by transportation operations
during Hajj and Umrah. It does NOT contain real company, driver, vehicle,
or ticket data.

Never point this project at real company data. Letting an AI run generated
SQL against real systems can create security and privacy risks. A small,
clean database also makes the AI more reliable and easier to test.
"""

import sqlite3

conn = sqlite3.connect("transport.db")
conn.execute("PRAGMA foreign_keys = ON")
cur = conn.cursor()

# Start fresh every time this script runs.
# Child tables must be dropped before the parent table.
cur.executescript(
    """
    DROP TABLE IF EXISTS tickets;
    DROP TABLE IF EXISTS drivers;
    DROP TABLE IF EXISTS buses;
    DROP TABLE IF EXISTS transportation_companies;

    CREATE TABLE transportation_companies (
        id              INTEGER PRIMARY KEY,
        company_name    TEXT NOT NULL,
        city            TEXT NOT NULL,
        operation_type  TEXT NOT NULL
                        CHECK (
                            operation_type IN (
                                'Hajj',
                                'Umrah',
                                'Hajj and Umrah'
                            )
                        ),
        license_number  TEXT NOT NULL UNIQUE,
        company_status  TEXT NOT NULL
                        CHECK (
                            company_status IN (
                                'Active',
                                'Suspended',
                                'Inactive'
                            )
                        )
    );

    CREATE TABLE buses (
        id               INTEGER PRIMARY KEY,
        company_id       INTEGER NOT NULL,
        plate_number     TEXT NOT NULL UNIQUE,
        operating_number TEXT NOT NULL UNIQUE,
        model_year       INTEGER NOT NULL
                         CHECK (model_year BETWEEN 2000 AND 2030),
        seats             INTEGER NOT NULL
                         CHECK (seats > 0),
        ownership_type   TEXT NOT NULL
                         CHECK (
                             ownership_type IN (
                                 'Owned',
                                 'Rented'
                             )
                         ),
        bus_status       TEXT NOT NULL
                         CHECK (
                             bus_status IN (
                                 'Active',
                                 'Maintenance',
                                 'Inactive'
                             )
                         ),
        FOREIGN KEY (company_id)
            REFERENCES transportation_companies(id)
            ON UPDATE CASCADE
            ON DELETE RESTRICT
    );

    CREATE TABLE drivers (
        id              INTEGER PRIMARY KEY,
        company_id      INTEGER NOT NULL,
        driver_name     TEXT NOT NULL,
        identity_number TEXT NOT NULL UNIQUE,
        nationality     TEXT NOT NULL,
        driver_type     TEXT NOT NULL
                        CHECK (
                            driver_type IN (
                                'Citizen',
                                'Resident',
                                'Border Number',
                                'External Driver'
                            )
                        ),
        contract_type   TEXT NOT NULL
                        CHECK (
                            contract_type IN (
                                'Permanent',
                                'Seasonal',
                                'Temporary'
                            )
                        ),
        driver_status   TEXT NOT NULL
                        CHECK (
                            driver_status IN (
                                'Active',
                                'Inactive',
                                'Suspended'
                            )
                        ),
        FOREIGN KEY (company_id)
            REFERENCES transportation_companies(id)
            ON UPDATE CASCADE
            ON DELETE RESTRICT
    );

    CREATE TABLE tickets (
        id             INTEGER PRIMARY KEY,
        company_id     INTEGER NOT NULL,
        ticket_type    TEXT NOT NULL
                       CHECK (
                           ticket_type IN (
                               'Bus Breakdown',
                               'Driver Complaint',
                               'Route Violation',
                               'Safety Issue',
                               'Delay'
                           )
                       ),
        classification TEXT NOT NULL
                       CHECK (
                           classification IN (
                               'Operational',
                               'Technical',
                               'Safety',
                               'Administrative'
                           )
                       ),
        ticket_status  TEXT NOT NULL
                       CHECK (
                           ticket_status IN (
                               'Open',
                               'In Progress',
                               'Closed',
                               'Cancelled'
                           )
                       ),
        city           TEXT NOT NULL,
        ticket_date    TEXT NOT NULL,
        description    TEXT NOT NULL,
        FOREIGN KEY (company_id)
            REFERENCES transportation_companies(id)
            ON UPDATE CASCADE
            ON DELETE RESTRICT
    );
    """
)

transportation_companies = [
    (1, "Al Noor Transportation", "Mecca", "Hajj and Umrah", "LIC-1001", "Active"),
    (2, "Al Safa Bus Company", "Jeddah", "Umrah", "LIC-1002", "Active"),
    (3, "Tawaf Transportation", "Mecca", "Hajj", "LIC-1003", "Active"),
    (4, "Al Madinah Fleet", "Medina", "Umrah", "LIC-1004", "Active"),
    (5, "Pilgrim Road Transport", "Jeddah", "Hajj and Umrah", "LIC-1005", "Suspended"),
    (6, "Mina Mobility Company", "Mecca", "Hajj", "LIC-1006", "Active"),
]

buses = [
    (1, 1, "MKA-1021", "BUS-1001", 2023, 50, "Owned", "Active"),
    (2, 1, "MKA-1022", "BUS-1002", 2021, 45, "Owned", "Maintenance"),
    (3, 1, "MKA-1023", "BUS-1003", 2024, 52, "Rented", "Active"),
    (4, 2, "JED-2031", "BUS-2001", 2022, 50, "Owned", "Active"),
    (5, 2, "JED-2032", "BUS-2002", 2020, 45, "Rented", "Active"),
    (6, 3, "MKA-3041", "BUS-3001", 2023, 55, "Owned", "Active"),
    (7, 3, "MKA-3042", "BUS-3002", 2019, 50, "Owned", "Inactive"),
    (8, 4, "MED-4051", "BUS-4001", 2024, 48, "Owned", "Active"),
    (9, 4, "MED-4052", "BUS-4002", 2022, 52, "Rented", "Active"),
    (10, 5, "JED-5061", "BUS-5001", 2021, 45, "Owned", "Inactive"),
    (11, 5, "JED-5062", "BUS-5002", 2023, 50, "Owned", "Maintenance"),
    (12, 6, "MKA-6071", "BUS-6001", 2024, 55, "Owned", "Active"),
    (13, 6, "MKA-6072", "BUS-6002", 2023, 52, "Owned", "Active"),
    (14, 6, "MKA-6073", "BUS-6003", 2020, 48, "Rented", "Maintenance"),
]

drivers = [
    (1, 1, "Ahmed Al Harbi", "DRV-100001", "Saudi", "Citizen", "Permanent", "Active"),
    (2, 1, "Mohammed Hassan", "DRV-100002", "Egyptian", "Resident", "Seasonal", "Active"),
    (3, 1, "Khaled Saleh", "DRV-100003", "Saudi", "Citizen", "Permanent", "Suspended"),
    (4, 2, "Omar Farouk", "DRV-200001", "Egyptian", "Resident", "Permanent", "Active"),
    (5, 2, "Yousef Ali", "DRV-200002", "Saudi", "Citizen", "Temporary", "Active"),
    (6, 3, "Faisal Al Zahrani", "DRV-300001", "Saudi", "Citizen", "Permanent", "Active"),
    (7, 3, "Bilal Khan", "DRV-300002", "Pakistani", "Resident", "Seasonal", "Active"),
    (8, 3, "Mahmoud Nasser", "DRV-300003", "Jordanian", "External Driver", "Seasonal", "Inactive"),
    (9, 4, "Abdullah Al Otaibi", "DRV-400001", "Saudi", "Citizen", "Permanent", "Active"),
    (10, 4, "Imran Ahmed", "DRV-400002", "Indian", "Resident", "Temporary", "Active"),
    (11, 5, "Hassan Mustafa", "DRV-500001", "Sudanese", "Border Number", "Seasonal", "Inactive"),
    (12, 5, "Saad Al Mutairi", "DRV-500002", "Saudi", "Citizen", "Permanent", "Suspended"),
    (13, 6, "Nasser Al Qahtani", "DRV-600001", "Saudi", "Citizen", "Permanent", "Active"),
    (14, 6, "Usman Ali", "DRV-600002", "Pakistani", "Resident", "Seasonal", "Active"),
    (15, 6, "Tariq Mahmoud", "DRV-600003", "Egyptian", "Resident", "Temporary", "Active"),
]

tickets = [
    (1, 1, "Bus Breakdown", "Technical", "Closed", "Mecca", "2026-05-02", "Bus stopped because of an engine issue near Mina."),
    (2, 1, "Delay", "Operational", "In Progress", "Mecca", "2026-05-05", "Bus arrived late at the assigned pickup point."),
    (3, 2, "Driver Complaint", "Administrative", "Closed", "Jeddah", "2026-05-08", "A passenger reported inappropriate driver communication."),
    (4, 2, "Route Violation", "Operational", "Open", "Mecca", "2026-05-12", "Bus entered a route that was not assigned to the company."),
    (5, 3, "Safety Issue", "Safety", "Closed", "Mecca", "2026-05-15", "Emergency exit inspection was required."),
    (6, 3, "Bus Breakdown", "Technical", "In Progress", "Mecca", "2026-05-18", "Air-conditioning system stopped working."),
    (7, 4, "Delay", "Operational", "Cancelled", "Medina", "2026-05-21", "The delay report was submitted by mistake."),
    (8, 4, "Driver Complaint", "Administrative", "Open", "Medina", "2026-05-25", "Driver documents require additional verification."),
    (9, 5, "Safety Issue", "Safety", "Open", "Jeddah", "2026-06-01", "Vehicle inspection certificate has expired."),
    (10, 5, "Route Violation", "Operational", "Closed", "Mecca", "2026-06-03", "The company used an incorrect designated route."),
    (11, 6, "Bus Breakdown", "Technical", "Closed", "Mecca", "2026-06-06", "A tyre was replaced before the trip continued."),
    (12, 6, "Delay", "Operational", "In Progress", "Mecca", "2026-06-09", "Traffic congestion caused a delayed departure."),
    (13, 1, "Safety Issue", "Safety", "Open", "Mecca", "2026-06-12", "Seatbelt inspection is required for one bus."),
    (14, 2, "Bus Breakdown", "Technical", "Closed", "Jeddah", "2026-06-14", "Battery failure was fixed by the maintenance team."),
    (15, 3, "Driver Complaint", "Administrative", "Cancelled", "Mecca", "2026-06-18", "The complaint was duplicated."),
    (16, 4, "Route Violation", "Operational", "In Progress", "Medina", "2026-06-22", "The assigned route requires investigation."),
    (17, 6, "Safety Issue", "Safety", "Closed", "Mecca", "2026-06-25", "Safety equipment was checked and approved."),
    (18, 1, "Delay", "Operational", "Closed", "Mecca", "2026-07-01", "The company provided a valid reason for the delay."),
]

cur.executemany(
    """
    INSERT INTO transportation_companies
    (id, company_name, city, operation_type, license_number, company_status)
    VALUES (?, ?, ?, ?, ?, ?)
    """,
    transportation_companies,
)

cur.executemany(
    """
    INSERT INTO buses
    (id, company_id, plate_number, operating_number, model_year, seats,
     ownership_type, bus_status)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """,
    buses,
)

cur.executemany(
    """
    INSERT INTO drivers
    (id, company_id, driver_name, identity_number, nationality, driver_type,
     contract_type, driver_status)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """,
    drivers,
)

cur.executemany(
    """
    INSERT INTO tickets
    (id, company_id, ticket_type, classification, ticket_status, city,
     ticket_date, description)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """,
    tickets,
)

conn.commit()
conn.close()

print(
    "Created transport.db with",
    len(transportation_companies),
    "transportation companies,",
    len(buses),
    "buses,",
    len(drivers),
    "drivers, and",
    len(tickets),
    "tickets.",
)