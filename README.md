# LogRotatorX

LogRotatorX is a lightweight Python-based log rotation utility for Windows and Linux. It performs automatic size-based log rotation, background ZIP compression, archive management, and retention cleanup using a configurable scheduler.

## Features

* Cross-platform support (Windows and Linux)
* Size-based log rotation
* Background ZIP compression
* Scheduled archive movement
* Retention-based cleanup
* Runtime validation of configured log files and directories
* Single-instance execution using file locking
* Interval and Cron-based scheduling
* Configurable through a single YAML file
* Structured application logging
* Graceful startup and shutdown

---

## Project Structure

```text
LogRotatorX/
├── logrotatorx/
│   ├── archive.py
│   ├── compressor.py
│   ├── config.py
│   ├── constants.py
│   ├── context.py
│   ├── exceptions.py
│   ├── lock.py
│   ├── logger.py
│   ├── processor.py
│   ├── rotator.py
│   ├── runtime.py
│   ├── scheduler.py
│   ├── utils.py
│   └── version.py
├── logs/
├── state/
├── config.yaml
├── main.py
└── README.md
```

---

## Architecture

```text
                config.yaml
                     │
                     ▼
          Configuration Validation
                     │
                     ▼
          Runtime Environment Check
                     │
                     ▼
            Application Lock
                     │
                     ▼
         Background Compression Pool
                     │
                     ▼
              APScheduler
      ┌─────────────┼─────────────┐
      ▼             ▼             ▼
 Rotation Job   Archive Job   Cleanup Job
```

---

## Configuration

Application behaviour is controlled through a single `config.yaml` file.

Configuration includes:

* Global defaults
* Scheduler configuration
* Compression settings
* Retention settings
* Windows services
* Linux services
* Log file definitions
* Archive locations

---

## Runtime Validation

During startup, LogRotatorX validates all configured resources before scheduling any jobs.

Validation includes:

* Log file existence
* Destination directory existence
* Archive directory existence

Invalid log definitions are automatically excluded from processing. If no valid log definitions remain, the application terminates without starting scheduled jobs.

---

## Logging

Application logs include:

* Startup and shutdown
* Runtime validation
* Rotation events
* Compression events
* Archive operations
* Cleanup operations
* Scheduler execution
* Warnings and errors

---

## Requirements

* Python 3.12 or later
* Windows or Linux

---

## Current Status

Current version: **1.0.0**

Implemented functionality:

* Configuration management
* Runtime validation
* Size-based log rotation
* Background ZIP compression
* Archive management
* Retention cleanup
* Scheduler integration
* File locking
* Graceful shutdown

---

## License

This project is licensed under the Apache License 2.0. See the LICENSE file for details.

