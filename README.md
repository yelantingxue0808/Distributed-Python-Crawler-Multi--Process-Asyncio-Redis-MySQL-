# Distributed Python Crawler \(Multi\-Process \+ Asyncio \+ Redis \+ MySQL\)

A high\-performance distributed crawler built with Python, combining multi\-processing, asyncio coroutines, Redis for distributed task coordination, and MySQL for persistent data storage\. This crawler fetches and parses agricultural price data from https://www.zyctd.com/jiage/ and stores the structured results in MySQL\.

## Features

- **Distributed Architecture**: Uses Redis for distributed task queue management \(URL storage, parsed data caching\) to avoid duplicate processing across processes\.

- **High Concurrency**:
  - Multi\-processing to utilize multi\-core CPU resources\.

  - Asyncio coroutines for non\-blocking HTTP requests to improve crawling efficiency\.

- **Data Persistence**: Parsed structured data is stored in MySQL \(supports batch insertion for performance optimization\)\.

- **Robust Logging**: Comprehensive logging system to track crawler status, errors, and data processing metrics\.

- **Configurable**: Centralized configuration files for Redis, MySQL, HTTP headers, logging, and crawler behavior\.

- **Fault Tolerance**: Atomic Redis operations \(e\.g\., `spop`, `lpop`\) prevent race conditions in multi\-process environments\.

## Tech Stack

- **Language**: Python 3\.8\+

- **Concurrency**: `multiprocessing` \(multi\-process\), `asyncio` \+ `aiohttp` \(async coroutines\)

- **Distributed Storage**: Redis \(StrictRedis\)

- **Persistent Storage**: MySQL \(pymysql\)

- **Data Parsing**: lxml \(XPath\)

- **Logging**: Python standard `logging` module

- **Configuration Management**: Modular config files \(no third\-party libs\)

## Environment Setup

### 1\. Prerequisites

Install required dependencies:

```bash
pip install aiohttp lxml pymysql redis
```

### 2\. Configuration

Update the configuration files in the `config`directory to match your environment:

- `db_settings.py`: MySQL/Redis connection details \(host, port, username, password, database name\)\.

- `settings.py`: Crawler parameters \(page range, process count, Redis key names, crawler roles\)\.

- `https_settings.py`: HTTP request headers \(user\-agent, etc\.\)\.

- `logging_settings.py`: Log file path and name\.

### 3\. Database Preparation

- **Redis**: Ensure Redis server is running \(configured in `settings.py` and `db_settings.py`\)\.

- **MySQL**:

  1. Create a database \(e\.g\., `text3` as in the config\)\.

  2. Create a table `medical_table` with the following schema:

     ```sql
     CREATE TABLE medical_table (
         id INT AUTO_INCREMENT PRIMARY KEY,
         品名 VARCHAR(255) NOT NULL,
         规格 VARCHAR(255),
         市场 VARCHAR(255),
         价格 VARCHAR(50),
         趋势 VARCHAR(50),
         周涨跌 VARCHAR(50),
         月涨跌 VARCHAR(50),
         年涨跌 VARCHAR(50)
     ) DEFAULT CHARSET=utf8;
     ```

## Usage

### Run the Crawler

Execute the main entry file to start the crawler \(default role: save data to MySQL\):

```bash
python main.py
```

### Crawler Roles

The crawler is divided into 3 modular roles \(configurable via `settings.DEFAULT_ROLE`\):

1. **HEN \(Role 0\)**: Fetch URLs and store them in Redis \(distributed URL queue\)\.

2. **CAT \(Role 1\)**: Parse URLs from Redis \(async coroutines\) and store parsed data in Redis\.

3. **PIG \(Role 2\)**: Read parsed data from Redis and insert it into MySQL \(default role\)\.

To run a specific role:

```python
# Modify main.py
from core import service
from config import settings

if __name__ == '__main__':
    # Run HEN role (fetch URLs)
    service.execute_task(role=settings.CrawlerRole.HEN)
    # Or run CAT role (parse data)
    # service.execute_task(role=settings.CrawlerRole.CAT)
    # Or run PIG role (save to MySQL)
    # service.execute_task(role=settings.CrawlerRole.PIG)
```

## Project Structure

```Plain Text
multi-process-asyncio-redis-mysql/
├── config/                  # Configuration files
│   ├── db_settings.py       # Database (Redis/MySQL) config
│   ├── https_settings.py    # HTTP headers
│   ├── logging_settings.py  # Log config
│   ├── settings.py          # Core crawler settings (page range, roles, etc.)
├── core/                    # Core business logic
│   ├── handler.py           # Crawler logic (request, parse, task distribution)
│   ├── service.py           # Multi-process task execution
├── dao/                     # Data access layer
│   ├── data_base.py         # Singleton database connection (Redis/MySQL)
│   ├── save_data.py         # Data persistence (Redis/MySQL)
├── utils/                   # Utility functions
│   ├── logger.py            # Logging setup
│   ├── utils.py             # URL generation, async batch processing, SQL builder
├── log/                     # Log files (auto-created)
├── main.py                  # Entry point
└── README.md                # Project documentation
```

## Notes

1. **Rate Limiting**: The crawler includes `asyncio.sleep(0.5)` to avoid overwhelming the target server \(adjust as needed\)\.

2. **Process Count**: Modify `settings.PROCESS` to match your CPU core count \(default: 6\)\.

3. **Error Handling**: Logs are stored in `./log/logger.log` – check for parsing/DB errors\.

4. **Redis Cleanup**: Before re\-running the crawler, clear Redis keys \(e\.g\., `urls`, `parse_data`\) to avoid duplicate data.

5. **Encoding**: Ensure all MySQL/Redis connections use UTF\-8 to avoid garbled Chinese characters\.

## License

This project is for learning purposes only\. Please comply with the target website `robots.txt` and legal regulations when using it\.

## Disclaimer

This crawler is designed for educational use\. The author is not responsible for any misuse or violations of the target website terms of service\.
