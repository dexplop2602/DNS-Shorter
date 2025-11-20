
# 🌐 IONOS DNS URL Shortener

![Python](https://img.shields.io/badge/Python-3.10-blue?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.95+-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![Vagrant](https://img.shields.io/badge/Vagrant-Managed-1563FF?style=for-the-badge&logo=vagrant&logoColor=white)
![IONOS](https://img.shields.io/badge/IONOS-DNS%20API-003D8F?style=for-the-badge)

A robust, asynchronous URL shortener that leverages the **IONOS Cloud DNS API** to store redirection data in public **TXT records**. This project is designed to run within a virtualized environment using Vagrant, ensuring a consistent and reproducible infrastructure.

---

## 📖 Project Architecture & Memory

This project differs from traditional database-driven shorteners by using the Domain Name System (DNS) as a global, distributed database. It implements an **asynchronous architecture** to ensure high performance and fault tolerance.

### How it Works

1.  **Frontend & API (FastAPI):**
    *   The user submits a long URL via the web interface.
    *   The system generates a secure, random short code.
    *   The record is immediately saved to a local inventory (`pending_records.json`).
    *   **Instant Feedback:** The user receives the short URL immediately, without waiting for the external API call to complete.

2.  **Background Synchronization (Cron & Python):**
    *   A dedicated script (`sync_dns.py`) runs automatically every minute via a system Cron job.
    *   It reads the pending records and authenticates with the **IONOS DNS API** using a secure `X-API-Key`.
    *   It constructs the specific payload required by IONOS (handling FQDN and TXT record formatting).
    *   Upon success, records are moved to `synced_records.json`.

3.  **Resolution & Redirection:**
    *   When a short link is accessed, the system queries the global DNS resolvers for the TXT record associated with that subdomain.
    *   If the DNS propagation hasn't finished yet, it falls back to the local inventory to ensure the link works instantly for the creator.

---

## 🚀 Getting Started

Follow these instructions to get the project up and running on your local machine.

### Prerequisites

*   **Vagrant** (installed)
*   **VirtualBox** (installed)
*   An **IONOS** account with access to a domain and the "Hosting" API (Developer API).

### 🛠️ Configuration (Important)

Since `.env` files contain sensitive credentials, they are ignored by Git. **You must create this file manually.**

1.  Create a file named `.env` in the root directory of the project.
2.  Copy the following content and fill in your real data:

```ini
# .env configuration file

# Your registered domain at IONOS (e.g., example.com)
BASE_DOMAIN=your-domain.com

# Your IONOS Developer API Public Prefix
# Found in the IONOS Developer Portal -> API Key
IONOS_PREFIX=your_public_prefix_here

# Your IONOS Developer API Secret
# This is only shown once when creating the key.
IONOS_SECRET=your_secret_key_here
```

> **⚠️ Note:** Ensure there are no spaces around the `=` sign and no quotes (`""`) around the values unless they contain special characters.

### 📦 Installation & Deployment

1.  **Clone the repository:**
    ```bash
    git clone git@github.com:dexplop2602/DNS-Shorter.git
    cd <your-repo-folder>
    ```

2.  **Start the Environment:**
    Run the following command to provision the Virtual Machine. This script will automatically install Python, system dependencies, configure the Firewall, setup SSL certificates, and schedule the cron jobs.
    ```bash
    vagrant up
    ```
    * During the first boot, you might be asked to select your **Network Interface** (Wi-Fi or Ethernet) for the Bridged Network adapter. Select the one that provides Internet access.

3.  **Access the Application:**
    Once the process finishes, open your browser and go to:
    ```
    http://localhost:8000
    ```

---

## 📂 Project Structure

*   **`Vagrantfile`**: Defines the Infrastructure as Code (IaC). Configures Ubuntu 22.04, Bridged Networking, and port forwarding.
*   **`bootstrap.sh`**: System provisioning script. Handles package installation (`ca-certificates`, `ntpdate`), virtual environment creation, and Systemd service registration.
*   **`api/main.py`**: The FastAPI application. Handles the web UI and the redirection logic.
*   **`sync_dns.py`**: The backend worker. Handles the complex communication with the IONOS API (Authentication, Payload formatting, Error handling).
*   **`requirements.txt`**: Python dependencies.

---

## 🐛 Troubleshooting

**The link shows "Site can't be reached" (DNS_PROBE_POSSIBLE):**
*   This is expected if you try to access your domain (e.g., `davidexposito.es`) from your host machine without a public server IP.
*   **Solution:** To test redirections locally, edit your host machine's `/etc/hosts` (Linux/Mac) or `hosts` file (Windows) and map your domain to the VM's IP or use `http://localhost:8000/shortcode`.

**Logs & Debugging:**
*   To check the status of the background synchronization, access the VM and check the cron log:
    ```bash
    vagrant ssh
    cat /vagrant/cron.log
    ```
*   To check the web server status:
    ```bash
    sudo systemctl status dns-shortener.service
    ```

---

## 📜 License

This project is open-source and available under the [MIT License](LICENSE).

---
*Developed for System Administration Practice - 2025*
