# PostgreSQL Performance Analysis: Configuration & Parallel Programming

![PostgreSQL](https://img.shields.io/badge/PostgreSQL-17-blue)
![Python](https://img.shields.io/badge/Python-3.10%2B-yellow)
![Status](https://img.shields.io/badge/Status-Completed-green)

## Project Overview

This research project investigates the impact of server configuration on database performance and evaluates the efficiency of different parallel programming paradigms (Threading vs. Asyncio) in high-load database environments.

The study compares two distinct PostgreSQL server configurations using a dataset of **10 million records**, measuring query latency and throughput under various conditions.

##  Experimental Setup

The project was conducted on **Ubuntu 22.04 LTS** with **4 CPUs** and **8 GB RAM**. Two environments were configured to represent "Best Practice" vs. "Common Mistakes":

### 1. Database Configurations

| Parameter | Server A (Optimum) | Server B (Faulty) | Impact |
| :--- | :--- | :--- | :--- |
| **Shared Buffers** | `2GB` (25% RAM) | `128MB` (Default/Low) | Critical for caching frequently accessed data. |
| **Max Connections** | `100` | `1000` | High connection counts increase overhead. |
| **Effective Cache** | `6GB` | `1GB` | Helps the planner estimate available memory. |
| **WAL Buffers** | `16MB` | `3MB` | Affects write performance and checkpointing. |

### 2. Dataset
A `users` table with **10,000,000 rows** was generated with the following schema:
* `id` (Serial PK)
* `name`, `surname`, `email` (Text)
* `birth_date` (Date)
* `created_at` (Timestamp)

##  Methodology

The project performed two types of benchmarks:

1.  **Basic Query Performance**:
    * Direct ID lookup (Index Scan).
    * Email search (Text search).
    * Date range filtering.
    * Complex grouping and sorting (`GROUP BY`, `ORDER BY`).

2.  **Concurrency Models**:
    * **Sequential**: Standard synchronous execution.
    * **Threading**: Multi-threaded execution (Python `threading`).
    * **Asyncio**: Asynchronous execution (Python `asyncio`).

##  Key Findings

### 1. Configuration Impact
* **Server A (Optimum)** was consistently faster across all tests.
* **ID Lookups**: Server A was **4x faster** than Server B (0.0017s vs 0.0063s), proving the massive impact of `shared_buffers` on index lookups.
* **Email Search**: Server A was **2x faster**, highlighting better cache hit ratios.

### 2. Parallel Programming Performance
* **Threading is King**: Threading provided the best performance boost, achieving a **4.08x speedup** on Server A.
* **Asyncio Limitations**: While Asyncio provided a speedup (1.6x - 2.0x), it lagged behind Threading for these specific CPU/IO-bound database operations.
* **Efficiency**: Threading achieved **82% efficiency** on the optimized server, compared to just 32% for Asyncio.

##  Conclusion

* **Configuration Matters**: Proper tuning of `shared_buffers` and `max_connections` is not optional; it is critical for scaling.
* **Concurrency Choice**: For PostgreSQL clients doing heavy read operations, **Threading** generally outperforms Asyncio due to better compatibility with standard connection pooling and blocking I/O behavior in certain drivers.
* **Optimization Synergy**: The optimized server (Server A) benefited *more* from parallel execution than the faulty server, showing that software-level concurrency cannot fix hardware/config-level bottlenecks.

## 📂 Repository Structure

* `src/` - Python scripts for benchmarking (Sequential, Threading, Asyncio).
* `config/` - `postgresql.conf` files for Server A and Server B.
* `docs/` - Project report and presentation slides.
* `data/` - Scripts for data generation (10M rows).
