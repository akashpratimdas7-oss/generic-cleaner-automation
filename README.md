## Overview

This project demonstrates a real-world style data cleaning and file
transformation automation workflow using Python and Pandas.

The goal is to build a reusable script that can batch clean and standardize
messy business datasets automatically.

Raw datasets may contain:

- Missing or unknown headers
- Extra spaces in text
- "?" or similar markers used as missing values
- Numbers stored as text
- Invalid negative values
- Incorrect date formats
- Duplicate records

Goal: Automatically inspect, standardize, clean, and export
analysis-ready datasets along with summary reports.

## Datasets Used (for testing)

- Bank Marketing Dataset  
Source: UCI Machine Learning Repository  
https://archive.ics.uci.edu/dataset/222/bank+marketing

- NYC Taxi Trip Records  
Source: NYC Taxi & Limousine Commission  
https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page

- Adult Census Income Dataset  
Source: UCI Machine Learning Repository  
https://archive.ics.uci.edu/ml/datasets/adult

These datasets are publicly available and used only for demonstration.

## Workflow

### 1. File Ingestion
- Detect whether file contains headers
- Load CSV, Excel, Parquet, or .data files
- Handle different delimiters automatically

### 2. Standardization
- Normalize column names
- Trim whitespace from text values

### 3. Cleaning & Validation
- Replace common missing markers with NA
- Convert numeric-like columns safely
- Invalidate negative values where not allowed
- Convert date/time columns
- Validate pickup vs dropoff datetime order
- Drop rows missing critical numeric or ID columns
- Remove duplicate rows

### 4. Output
- Export cleaned file
- Generate summary report

## Folder Structure
before_files/  → raw input files  
after_files/   → cleaned output files  
reports/       → cleaning summary reports  
cleaner.py     → main automation script  

## How To Run

1. Place raw files inside:
before_files/

2. Run:
generic cleaner automation.py

3. Outputs will be created in:
after_files/  
reports/

## Output
- Cleaned dataset
- Text report describing:
- Rows before and after cleaning
- Numeric values coerced
- Negative values invalidated
- Dates coerced
- Invalid datetime rows fixed
- Rows dropped due to missing important values
- Duplicates removed

## Notes
This project focuses on practical data preparation and automation.
It does not include modeling or visualization.
Cleaning rules are heuristic-based and can be adjusted
depending on business or client requirements.

Author: Akash Pratim Das