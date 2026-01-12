# 🏠 Smart Home IoT - Environmental Monitoring & Alert System

A comprehensive IoT system for domestic environmental monitoring with real-time alerts, developed as an academic project.

## 📋 Table of Contents

- [About the Project](#about-the-project)
- [Features](#features)
- [Technologies Used](#technologies-used)
- [Required Hardware](#required-hardware)
- [System Architecture](#system-architecture)
- [Installation](#installation)
- [Usage](#usage)
- [AWS Deployment](#aws-deployment)
- [API Documentation](#api-documentation)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)

---

## 🎯 About the Project

An intelligent environmental monitoring system that collects sensor data in real-time, stores it in a time-series optimised database, displays it on an interactive dashboard, and sends alerts when parameters exceed configured thresholds.

### Monitored Sensors:
- 🌡️ **Temperature and Humidity** (DHT22)
- 💡 **Light Intensity** (LDR)
- 🚶 **Motion Detection** (PIR)

### Controlled Actuators:
- 🟢 **Green LED** (visual indicators)
- 🔊 **Buzzer** (audio alerts)

---

## ✨ Features

- ✅ Real-time monitoring of temperature, humidity, light, and motion
- ✅ Responsive web dashboard with historical charts
- ✅ Configurable alert system
- ✅ Remote control of LEDs and buzzer via web interface
- ✅ Optimised storage with TimescaleDB
- ✅ Real-time communication via PubNub
- ✅ Complete RESTful API
- ✅ Containerisation with Docker
- ✅ AWS deployment ready

---

## 🛠️ Technologies Used

### Hardware
- Raspberry Pi 4 (8GB RAM)
- DHT22 Sensor (temperature/humidity)
- LDR Sensor (light intensity)
- PIR Sensor (motion)
- LEDs (red, green, blue)
- Buzzer
- Breadboard and jumper wires

### Software
- **Backend**: Python 3.11, Flask
- **Frontend**: React 18, SASS, Axios
- **Database**: PostgreSQL 16 + TimescaleDB
- **IoT Communication**: PubNub
- **Containerisation**: Docker, Docker Compose
- **Cloud**:  AWS (EC2, optional RDS)
- **Web Server**: Nginx (production)

---

## 🔌 Required Hardware

| Component | Quantity | GPIO Pin | Function |
|-----------|----------|----------|----------|
| Raspberry Pi 4 | 1 | - | Main controller |
| DHT22 | 1 | GPIO 4 | Temperature/Humidity |
| LDR | 1 | GPIO 17 | Light intensity |
| PIR | 1 | GPIO 27 | Motion |
| Red LED | 1 | GPIO 22 | Critical alert |
| Green LED | 1 | GPIO 23 | OK status |
| Blue LED | 1 | GPIO 24 | Night mode |
| Buzzer | 1 | GPIO 25 | Audio alert |
| Breadboard | 1 | - | Assembly |
| Resistors | 3x 220Ω | - | LEDs |

See complete diagram at:  [docs/hardware-setup.md](docs/hardware-setup.md)

---

## 🏗️ System Architecture

```
┌─────────────────────┐
│   Raspberry Pi      │
│   ├─ DHT22         │
│   ├─ LDR           │
│   ├─ PIR           │
│   ├─ LEDs          │
│   └─ Buzzer        │
│        │            │
│    Python App      │
└─────────┬───────────┘
          │ PubNub (MQTT-like)
          ▼
┌─────────────────────┐
│     AWS EC2         │
│  ┌───────────────┐  │
│  │ TimescaleDB   │  │
│  └───────┬───────┘  │
│  ┌───────▼───────┐  │
│  │ Flask Backend │  │
│  └───────┬───────┘  │
│  ┌───────▼───────┐  │
│  │  React App    │  │
│  └───────────────┘  │
│  ┌───────────────┐  │
│  │     Nginx     │  │
│  └───────────────┘  │
└─────────────────────┘
```

See detailed architecture at: [docs/architecture. md](docs/architecture.md)

---

## 🚀 Installation

### Prerequisites

- Docker 24+ and Docker Compose 2+
- PubNub account (free): https://dashboard.pubnub.com/
- (Optional) AWS account for deployment

### 1. Clone the repository

```bash
git clone https://github.com/your-username/smart-home-iot.git
cd smart-home-iot
```

### 2. Configure environment variables

```bash
cp .env.example .env
```

Edit the `.env` file and configure:
- PubNub credentials
- Database passwords
- Alert thresholds
- GPIO pins (if necessary)

### 3. Start the development environment

```bash
docker-compose up --build
```

### 4. Access the application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:5000
- **Database**: localhost:5432

---

## 📖 Usage

### Local Development

```bash
# Start all services
docker-compose up

# View logs
docker-compose logs -f

# Stop
docker-compose down

# Clean volumes (reset database)
docker-compose down -v
```

### Real Raspberry Pi (without Docker)

```bash
cd raspberry-pi
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your settings
python main.py
```

### Access database

```bash
docker-compose exec timescaledb psql -U iot_user -d smart_home_iot
```

---

## ☁️ AWS Deployment

See complete guide:  [docs/deployment-guide.md](docs/deployment-guide.md)

### Summary: 

```bash
# 1. Create EC2 t2.micro (Ubuntu 22.04)
# 2. Connect via SSH
ssh -i your-key.pem ubuntu@your-ec2-ip

# 3. Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# 4. Clone repository
git clone https://github.com/your-username/smart-home-iot.git
cd smart-home-iot

# 5. Configure . env
cp .env.example . env
nano .env

# 6. Deploy
docker-compose -f docker-compose.prod.yml up -d
```

---

## 📡 API Documentation

See complete documentation: [docs/api-documentation. md](docs/api-documentation. md)

### Main Endpoints:

```
GET  /api/health                    # Backend status
GET  /api/sensors/latest            # Latest readings
GET  /api/sensors/history           # History (query params)
GET  /api/sensors/stats             # Aggregated statistics
GET  /api/alerts                    # Alert list
POST /api/control/led               # Control LED
POST /api/control/buzzer            # Control buzzer
```

---

## 🐛 Troubleshooting

See complete guide: [docs/troubleshooting.md](docs/troubleshooting.md)

### Common Issues:

**Frontend cannot connect to backend:**
```bash
# Check if backend is running
docker-compose ps
docker-compose logs backend

# Test API directly
curl http://localhost:5000/api/health
```

**Database does not start:**
```bash
# Check logs
docker-compose logs timescaledb

# Recreate volume
docker-compose down -v
docker-compose up
```

**Raspberry Pi does not send data:**
```bash
# Check logs
docker-compose logs raspberry-simulator

# Test PubNub manually
# (see docs/troubleshooting.md)
```

---

## 👨‍💻 Development

### Branch Structure

- `main`: Production
- `develop`: Development
- `feature/*`: New features
- `hotfix/*`: Urgent fixes

### Run Tests

```bash
# Backend
cd backend
pytest

# Frontend
cd frontend
npm test
```

## 👤 Author

**Henrique Joanoni**

Project developed for IoT module - Dundalk Institute of Technology

---

## 🙏 Acknowledgements

- Professor John Loane for guidance
- Python/React community
- PubNub and TimescaleDB documentation
