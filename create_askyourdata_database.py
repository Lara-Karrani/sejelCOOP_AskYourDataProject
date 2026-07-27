
"""
Creates a FAKE SQLite database for the "Ask Your Data" project.

The schema is inspired by Hajj and Umrah transportation operations and by the
training tasks, but it contains no real company, driver, vehicle, request, or
ticket data.

Run:
    python create_transport_database_v2.py

Output:
    askyourdata.db
"""

import random
import sqlite3
from datetime import date, timedelta

DB_FILE = "askyourdata.db"
random.seed(42)

conn = sqlite3.connect(DB_FILE)
conn.execute("PRAGMA foreign_keys = ON")
cur = conn.cursor()

cur.executescript(
    """
    DROP TABLE IF EXISTS tickets;
    DROP TABLE IF EXISTS requests;
    DROP TABLE IF EXISTS driver_season_map;
    DROP TABLE IF EXISTS bus_season_map;
    DROP TABLE IF EXISTS drivers;
    DROP TABLE IF EXISTS buses;
    DROP TABLE IF EXISTS seasons;
    DROP TABLE IF EXISTS contract_types;
    DROP TABLE IF EXISTS driver_types;
    DROP TABLE IF EXISTS nationalities;
    DROP TABLE IF EXISTS manufacturing_companies;
    DROP TABLE IF EXISTS bus_categories;
    DROP TABLE IF EXISTS transportation_companies;
    DROP TABLE IF EXISTS transportation_company_types;
    DROP TABLE IF EXISTS cities;

    CREATE TABLE cities (
        id          INTEGER PRIMARY KEY,
        city_name   TEXT NOT NULL UNIQUE
    );

    CREATE TABLE transportation_company_types (
        id          INTEGER PRIMARY KEY,
        type_name   TEXT NOT NULL UNIQUE
    );

    CREATE TABLE transportation_companies (
        id                       INTEGER PRIMARY KEY,
        company_name             TEXT NOT NULL UNIQUE,
        company_name_ar          TEXT NOT NULL,
        company_type_id          INTEGER NOT NULL,
        city_id                  INTEGER NOT NULL,
        district                 TEXT,
        commercial_registration  TEXT NOT NULL UNIQUE,
        license_number           TEXT NOT NULL UNIQUE,
        manager_name             TEXT NOT NULL,
        manager_mobile           TEXT NOT NULL,
        email                    TEXT NOT NULL UNIQUE,
        operation_type           TEXT NOT NULL
                                 CHECK (
                                     operation_type IN (
                                         'Hajj',
                                         'Umrah',
                                         'Hajj and Umrah',
                                         'Local Hajj',
                                         'External Hajj',
                                         'Local Hajj and Umrah',
                                         'External Hajj and Umrah'
                                     )
                                 ),
        company_status           TEXT NOT NULL
                                 CHECK (
                                     company_status IN (
                                         'Active',
                                         'Temporarily Suspended',
                                         'Permanently Suspended',
                                         'Inactive'
                                     )
                                 ),
        FOREIGN KEY (company_type_id)
            REFERENCES transportation_company_types(id),
        FOREIGN KEY (city_id)
            REFERENCES cities(id)
    );

    CREATE TABLE bus_categories (
        id              INTEGER PRIMARY KEY,
        category_name   TEXT NOT NULL UNIQUE
    );

    CREATE TABLE manufacturing_companies (
        id              INTEGER PRIMARY KEY,
        manufacturer_name TEXT NOT NULL UNIQUE
    );

    CREATE TABLE buses (
        id                  INTEGER PRIMARY KEY,
        company_id          INTEGER NOT NULL,
        manufacturer_id     INTEGER,
        category_id         INTEGER,
        license_serial_no   TEXT NOT NULL UNIQUE,
        plate_number        TEXT NOT NULL UNIQUE,
        operating_number    TEXT NOT NULL UNIQUE,
        chassis_number      TEXT NOT NULL UNIQUE,
        model_year          INTEGER NOT NULL
                            CHECK (model_year BETWEEN 2000 AND 2030),
        seats               INTEGER NOT NULL CHECK (seats > 0),
        passenger_seats     INTEGER NOT NULL CHECK (passenger_seats > 0),
        owner_identity_no   TEXT NOT NULL,
        ownership_type      TEXT NOT NULL
                            CHECK (ownership_type IN ('Owned', 'Rented')),
        inspection_expiry   TEXT NOT NULL,
        license_expiry      TEXT NOT NULL,
        bus_status          TEXT NOT NULL
                            CHECK (
                                bus_status IN (
                                    'Active',
                                    'Maintenance',
                                    'Out of Service',
                                    'Inactive'
                                )
                            ),
        FOREIGN KEY (company_id)
            REFERENCES transportation_companies(id),
        FOREIGN KEY (manufacturer_id)
            REFERENCES manufacturing_companies(id),
        FOREIGN KEY (category_id)
            REFERENCES bus_categories(id)
    );

    CREATE TABLE nationalities (
        id                INTEGER PRIMARY KEY,
        nationality_name  TEXT NOT NULL UNIQUE
    );

    CREATE TABLE driver_types (
        id                INTEGER PRIMARY KEY,
        driver_type_name  TEXT NOT NULL UNIQUE
    );

    CREATE TABLE contract_types (
        id                INTEGER PRIMARY KEY,
        contract_type_name TEXT NOT NULL UNIQUE
    );

    CREATE TABLE drivers (
        id                INTEGER PRIMARY KEY,
        company_id        INTEGER NOT NULL,
        nationality_id    INTEGER,
        driver_type_id    INTEGER NOT NULL,
        contract_type_id  INTEGER NOT NULL,
        identity_number   TEXT NOT NULL UNIQUE,
        first_name        TEXT NOT NULL,
        father_name       TEXT,
        last_name         TEXT NOT NULL,
        birth_date        TEXT NOT NULL,
        mobile_number     TEXT NOT NULL,
        driver_status     TEXT NOT NULL
                          CHECK (
                              driver_status IN (
                                  'Active',
                                  'Suspended',
                                  'Out of Service',
                                  'Inactive'
                              )
                          ),
        FOREIGN KEY (company_id)
            REFERENCES transportation_companies(id),
        FOREIGN KEY (nationality_id)
            REFERENCES nationalities(id),
        FOREIGN KEY (driver_type_id)
            REFERENCES driver_types(id),
        FOREIGN KEY (contract_type_id)
            REFERENCES contract_types(id)
    );

    CREATE TABLE seasons (
        id              INTEGER PRIMARY KEY,
        season_name     TEXT NOT NULL UNIQUE,
        season_type     TEXT NOT NULL
                        CHECK (season_type IN ('Hajj', 'Umrah')),
        start_date      TEXT NOT NULL,
        end_date        TEXT NOT NULL
    );

    CREATE TABLE bus_season_map (
        id                     INTEGER PRIMARY KEY,
        bus_id                 INTEGER NOT NULL,
        season_id              INTEGER NOT NULL,
        can_participate        INTEGER NOT NULL CHECK (can_participate IN (0, 1)),
        approved_participant   INTEGER NOT NULL CHECK (approved_participant IN (0, 1)),
        out_of_service         INTEGER NOT NULL CHECK (out_of_service IN (0, 1)),
        temporarily_stopped    INTEGER NOT NULL CHECK (temporarily_stopped IN (0, 1)),
        permanently_stopped    INTEGER NOT NULL CHECK (permanently_stopped IN (0, 1)),
        participation_status   TEXT NOT NULL
                               CHECK (
                                   participation_status IN (
                                       'New',
                                       'Eligible',
                                       'Approved',
                                       'Rejected',
                                       'Cancelled',
                                       'Stopped'
                                   )
                               ),
        UNIQUE (bus_id, season_id),
        FOREIGN KEY (bus_id) REFERENCES buses(id),
        FOREIGN KEY (season_id) REFERENCES seasons(id)
    );

    CREATE TABLE driver_season_map (
        id                     INTEGER PRIMARY KEY,
        driver_id              INTEGER NOT NULL,
        company_id             INTEGER NOT NULL,
        season_id              INTEGER NOT NULL,
        can_participate        INTEGER NOT NULL CHECK (can_participate IN (0, 1)),
        approved_participant   INTEGER NOT NULL CHECK (approved_participant IN (0, 1)),
        out_of_service         INTEGER NOT NULL CHECK (out_of_service IN (0, 1)),
        cancellation_requested INTEGER NOT NULL CHECK (cancellation_requested IN (0, 1)),
        temporarily_suspended  INTEGER NOT NULL CHECK (temporarily_suspended IN (0, 1)),
        participation_status   TEXT NOT NULL
                               CHECK (
                                   participation_status IN (
                                       'New',
                                       'Eligible',
                                       'Approved',
                                       'Rejected',
                                       'Cancelled',
                                       'Stopped'
                                   )
                               ),
        UNIQUE (driver_id, season_id),
        FOREIGN KEY (driver_id) REFERENCES drivers(id),
        FOREIGN KEY (company_id) REFERENCES transportation_companies(id),
        FOREIGN KEY (season_id) REFERENCES seasons(id)
    );

    CREATE TABLE requests (
        id                  INTEGER PRIMARY KEY,
        company_id          INTEGER NOT NULL,
        request_type        TEXT NOT NULL
                            CHECK (
                                request_type IN (
                                    'Add Bus',
                                    'Add Driver',
                                    'Bus Participation',
                                    'Driver Participation'
                                )
                            ),
        request_date        TEXT NOT NULL,
        request_status      TEXT NOT NULL
                            CHECK (
                                request_status IN (
                                    'New',
                                    'Waiting for Verification',
                                    'Waiting for Approval',
                                    'Approved',
                                    'Rejected'
                                )
                            ),
        bus_id              INTEGER,
        driver_id           INTEGER,
        comments            TEXT,
        FOREIGN KEY (company_id)
            REFERENCES transportation_companies(id),
        FOREIGN KEY (bus_id)
            REFERENCES buses(id),
        FOREIGN KEY (driver_id)
            REFERENCES drivers(id)
    );

    CREATE TABLE tickets (
        id              INTEGER PRIMARY KEY,
        company_id      INTEGER NOT NULL,
        ticket_type     TEXT NOT NULL
                        CHECK (
                            ticket_type IN (
                                'Bus Breakdown',
                                'Driver Complaint',
                                'Route Violation',
                                'Safety Issue',
                                'Delay'
                            )
                        ),
        classification  TEXT NOT NULL
                        CHECK (
                            classification IN (
                                'Operational',
                                'Technical',
                                'Safety',
                                'Administrative'
                            )
                        ),
        ticket_status   TEXT NOT NULL
                        CHECK (
                            ticket_status IN (
                                'Open',
                                'In Progress',
                                'Closed',
                                'Cancelled'
                            )
                        ),
        city_id         INTEGER NOT NULL,
        ticket_date     TEXT NOT NULL,
        description     TEXT NOT NULL,
        FOREIGN KEY (company_id)
            REFERENCES transportation_companies(id),
        FOREIGN KEY (city_id)
            REFERENCES cities(id)
    );

    CREATE INDEX idx_bus_company ON buses(company_id);
    CREATE INDEX idx_driver_company ON drivers(company_id);
    CREATE INDEX idx_request_company ON requests(company_id);
    CREATE INDEX idx_ticket_company ON tickets(company_id);
    CREATE INDEX idx_ticket_date ON tickets(ticket_date);
    """
)

cities = [
    (1, "Mecca"),
    (2, "Jeddah"),
    (3, "Medina"),
    (4, "Taif"),
    (5, "Mina"),
    (6, "Arafat"),
    (7, "Muzdalifah"),
]

company_types = [
    (1, "Transportation Company"),
    (2, "Bus Operator"),
    (3, "Seasonal Transport Provider"),
]

company_names = [
    ("Al Noor Transportation", "شركة النور للنقل"),
    ("Al Safa Bus Company", "شركة الصفا للحافلات"),
    ("Tawaf Transportation", "شركة الطواف للنقل"),
    ("Al Madinah Fleet", "أسطول المدينة"),
    ("Pilgrim Road Transport", "شركة طريق الحجاج"),
    ("Mina Mobility Company", "شركة منى للتنقل"),
    ("Arafat Transit", "شركة عرفات للنقل"),
    ("Zamzam Fleet Services", "شركة زمزم لخدمات الأسطول"),
    ("Mashaer Express", "شركة المشاعر السريعة"),
    ("Al Huda Mobility", "شركة الهدى للتنقل"),
    ("Rawdah Transport", "شركة الروضة للنقل"),
    ("Haramain Bus Services", "شركة الحرمين للحافلات"),
]

operations = [
    "Hajj", "Umrah", "Hajj and Umrah",
    "Local Hajj", "External Hajj",
    "Local Hajj and Umrah", "External Hajj and Umrah"
]
company_statuses = ["Active"] * 9 + ["Temporarily Suspended", "Permanently Suspended", "Inactive"]
districts = ["Al Aziziyah", "Al Naseem", "Al Rawdah", "Al Hamra", "Al Shati", "Al Awali"]

companies = []
for i, (name_en, name_ar) in enumerate(company_names, start=1):
    companies.append(
        (
            i,
            name_en,
            name_ar,
            ((i - 1) % 3) + 1,
            ((i - 1) % 4) + 1,
            districts[(i - 1) % len(districts)],
            f"CR-{4030000000 + i}",
            f"LIC-{1000 + i}",
            f"Manager {i}",
            f"9665{53000000 + i:08d}",
            f"contact{i}@example.com",
            operations[(i - 1) % len(operations)],
            company_statuses[i - 1],
        )
    )

bus_categories = [
    (1, "Standard Bus"),
    (2, "Luxury Coach"),
    (3, "Mini Bus"),
    (4, "Accessible Bus"),
]

manufacturers = [
    (1, "Mercedes-Benz"),
    (2, "Volvo"),
    (3, "MAN"),
    (4, "Scania"),
    (5, "Yutong"),
    (6, "Higer"),
]

nationalities = [
    (1, "Saudi"),
    (2, "Egyptian"),
    (3, "Pakistani"),
    (4, "Indian"),
    (5, "Sudanese"),
    (6, "Jordanian"),
    (7, "Bangladeshi"),
    (8, "Indonesian"),
]

driver_types = [
    (1, "Citizen"),
    (2, "Resident"),
    (3, "Border Number"),
    (4, "External Driver"),
]

contract_types = [
    (1, "Permanent"),
    (2, "Seasonal"),
    (3, "Temporary"),
]

seasons = [
    (1, "Hajj 1447", "Hajj", "2026-05-20", "2026-06-10"),
    (2, "Umrah 1447", "Umrah", "2026-01-01", "2026-12-31"),
]

cur.executemany("INSERT INTO cities VALUES (?, ?)", cities)
cur.executemany("INSERT INTO transportation_company_types VALUES (?, ?)", company_types)
cur.executemany(
    """
    INSERT INTO transportation_companies
    (id, company_name, company_name_ar, company_type_id, city_id, district,
     commercial_registration, license_number, manager_name, manager_mobile,
     email, operation_type, company_status)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """,
    companies,
)
cur.executemany("INSERT INTO bus_categories VALUES (?, ?)", bus_categories)
cur.executemany("INSERT INTO manufacturing_companies VALUES (?, ?)", manufacturers)
cur.executemany("INSERT INTO nationalities VALUES (?, ?)", nationalities)
cur.executemany("INSERT INTO driver_types VALUES (?, ?)", driver_types)
cur.executemany("INSERT INTO contract_types VALUES (?, ?)", contract_types)
cur.executemany("INSERT INTO seasons VALUES (?, ?, ?, ?, ?)", seasons)

# Generate buses.
buses = []
for i in range(1, 61):
    company_id = ((i - 1) % len(companies)) + 1
    manufacturer_id = ((i - 1) % len(manufacturers)) + 1
    category_id = ((i - 1) % len(bus_categories)) + 1
    model_year = random.randint(2012, 2026)
    seats = random.choice([30, 45, 48, 50, 52, 55])
    passenger_seats = max(1, seats - random.choice([0, 1, 2]))
    ownership_type = random.choice(["Owned", "Owned", "Rented"])
    bus_status = random.choice(["Active", "Active", "Active", "Maintenance", "Out of Service", "Inactive"])
    base_date = date(2026, 1, 1)
    inspection_expiry = base_date + timedelta(days=random.randint(30, 500))
    license_expiry = base_date + timedelta(days=random.randint(30, 700))
    buses.append(
        (
            i, company_id, manufacturer_id, category_id,
            f"LSN-{760000000 + i}",
            f"{random.choice(['MKA', 'JED', 'MED', 'TAF'])}-{1000 + i}",
            f"BUS-{company_id:02d}-{i:04d}",
            f"CHS-{2026000000 + i}",
            model_year, seats, passenger_seats,
            f"OWN-{700000000 + ((i - 1) % 20) + 1}",
            ownership_type,
            inspection_expiry.isoformat(),
            license_expiry.isoformat(),
            bus_status,
        )
    )

cur.executemany(
    """
    INSERT INTO buses
    (id, company_id, manufacturer_id, category_id, license_serial_no,
     plate_number, operating_number, chassis_number, model_year, seats,
     passenger_seats, owner_identity_no, ownership_type, inspection_expiry,
     license_expiry, bus_status)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """,
    buses,
)

first_names = ["Ahmed", "Mohammed", "Omar", "Faisal", "Yousef", "Khaled", "Nasser", "Bilal", "Imran", "Tariq"]
father_names = ["Ali", "Hassan", "Saleh", "Mahmoud", "Abdullah", "Mustafa"]
last_names = ["Al Harbi", "Al Otaibi", "Al Zahrani", "Khan", "Ahmed", "Nasser", "Ali", "Farouk"]

drivers = []
for i in range(1, 91):
    company_id = ((i - 1) % len(companies)) + 1
    nationality_id = None if i % 17 == 0 else ((i - 1) % len(nationalities)) + 1
    driver_type_id = ((i - 1) % len(driver_types)) + 1
    contract_type_id = ((i - 1) % len(contract_types)) + 1
    birth = date(1968, 1, 1) + timedelta(days=random.randint(0, 12000))
    driver_status = random.choice(["Active", "Active", "Active", "Suspended", "Out of Service", "Inactive"])
    drivers.append(
        (
            i,
            company_id,
            nationality_id,
            driver_type_id,
            contract_type_id,
            f"DRV-{1000000000 + i}",
            first_names[(i - 1) % len(first_names)],
            father_names[(i - 1) % len(father_names)],
            last_names[(i - 1) % len(last_names)],
            birth.isoformat(),
            f"9665{41000000 + i:08d}",
            driver_status,
        )
    )

cur.executemany(
    """
    INSERT INTO drivers
    (id, company_id, nationality_id, driver_type_id, contract_type_id,
     identity_number, first_name, father_name, last_name, birth_date,
     mobile_number, driver_status)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """,
    drivers,
)

bus_maps = []
for i, bus in enumerate(buses, start=1):
    bus_id = bus[0]
    season_id = 1 if i % 3 != 0 else 2
    can_participate = 1 if bus[-1] == "Active" else random.choice([0, 1])
    out_of_service = 1 if bus[-1] == "Out of Service" else 0
    approved = 1 if can_participate and not out_of_service and i % 4 == 0 else 0
    temporarily_stopped = 1 if i % 19 == 0 else 0
    permanently_stopped = 1 if i % 29 == 0 else 0
    if permanently_stopped or temporarily_stopped:
        status = "Stopped"
    elif approved:
        status = "Approved"
    elif can_participate:
        status = "Eligible"
    else:
        status = random.choice(["New", "Rejected", "Cancelled"])
    bus_maps.append(
        (
            i, bus_id, season_id, can_participate, approved, out_of_service,
            temporarily_stopped, permanently_stopped, status
        )
    )

cur.executemany(
    """
    INSERT INTO bus_season_map
    (id, bus_id, season_id, can_participate, approved_participant,
     out_of_service, temporarily_stopped, permanently_stopped,
     participation_status)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """,
    bus_maps,
)

driver_maps = []
for i, driver in enumerate(drivers, start=1):
    driver_id = driver[0]
    company_id = driver[1]
    season_id = 1 if i % 4 != 0 else 2
    active = driver[-1] == "Active"
    can_participate = 1 if active else random.choice([0, 1])
    out_of_service = 1 if driver[-1] == "Out of Service" else 0
    cancellation_requested = 1 if i % 23 == 0 else 0
    temporarily_suspended = 1 if driver[-1] == "Suspended" else 0
    approved = 1 if (
        can_participate
        and not out_of_service
        and not cancellation_requested
        and not temporarily_suspended
        and i % 5 == 0
    ) else 0
    if temporarily_suspended:
        status = "Stopped"
    elif cancellation_requested:
        status = "Cancelled"
    elif approved:
        status = "Approved"
    elif can_participate:
        status = "Eligible"
    else:
        status = random.choice(["New", "Rejected"])
    driver_maps.append(
        (
            i, driver_id, company_id, season_id, can_participate, approved,
            out_of_service, cancellation_requested, temporarily_suspended, status
        )
    )

cur.executemany(
    """
    INSERT INTO driver_season_map
    (id, driver_id, company_id, season_id, can_participate,
     approved_participant, out_of_service, cancellation_requested,
     temporarily_suspended, participation_status)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """,
    driver_maps,
)

request_types = ["Add Bus", "Add Driver", "Bus Participation", "Driver Participation"]
request_statuses = ["New", "Waiting for Verification", "Waiting for Approval", "Approved", "Rejected"]
requests = []
start_date = date(2026, 1, 1)

for i in range(1, 101):
    company_id = random.randint(1, len(companies))
    request_type = random.choice(request_types)
    request_date = start_date + timedelta(days=random.randint(0, 210))
    request_status = random.choice(request_statuses)
    bus_id = random.randint(1, len(buses)) if request_type in ("Add Bus", "Bus Participation") else None
    driver_id = random.randint(1, len(drivers)) if request_type in ("Add Driver", "Driver Participation") else None
    comments = random.choice([
        None,
        "Documents are complete.",
        "Additional verification is required.",
        "The request was reviewed.",
        "Missing attachment.",
    ])
    requests.append(
        (
            i, company_id, request_type, request_date.isoformat(),
            request_status, bus_id, driver_id, comments
        )
    )

cur.executemany(
    """
    INSERT INTO requests
    (id, company_id, request_type, request_date, request_status,
     bus_id, driver_id, comments)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """,
    requests,
)

ticket_types = ["Bus Breakdown", "Driver Complaint", "Route Violation", "Safety Issue", "Delay"]
classifications = {
    "Bus Breakdown": "Technical",
    "Driver Complaint": "Administrative",
    "Route Violation": "Operational",
    "Safety Issue": "Safety",
    "Delay": "Operational",
}
ticket_statuses = ["Open", "In Progress", "Closed", "Cancelled"]
descriptions = {
    "Bus Breakdown": "The bus stopped because of a technical issue.",
    "Driver Complaint": "A driver-related complaint requires review.",
    "Route Violation": "The assigned route may have been violated.",
    "Safety Issue": "A safety inspection is required.",
    "Delay": "The bus arrived later than the assigned time.",
}

tickets = []
for i in range(1, 121):
    company_id = random.randint(1, len(companies))
    ticket_type = random.choice(ticket_types)
    city_id = random.randint(1, len(cities))
    ticket_date = date(2026, 1, 1) + timedelta(days=random.randint(0, 210))
    tickets.append(
        (
            i,
            company_id,
            ticket_type,
            classifications[ticket_type],
            random.choice(ticket_statuses),
            city_id,
            ticket_date.isoformat(),
            descriptions[ticket_type],
        )
    )

cur.executemany(
    """
    INSERT INTO tickets
    (id, company_id, ticket_type, classification, ticket_status,
     city_id, ticket_date, description)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """,
    tickets,
)

conn.commit()

counts = {}
for table in [
    "transportation_companies",
    "buses",
    "drivers",
    "bus_season_map",
    "driver_season_map",
    "requests",
    "tickets",
]:
    counts[table] = cur.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]

conn.close()

print(f"Created {DB_FILE}")
for table, count in counts.items():
    print(f"- {table}: {count}")
