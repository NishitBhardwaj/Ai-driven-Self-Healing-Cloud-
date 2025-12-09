#!/usr/bin/env python3
"""
Helper script to extract AWS credentials from CSV file
This script is for LOCAL USE ONLY - credentials are NOT committed to git
"""

import csv
import sys
import os
from pathlib import Path

def extract_credentials(csv_file_path, password=None):
    """
    Extract AWS credentials from CSV file
    
    Args:
        csv_file_path: Path to the CSV file
        password: Optional password (not used for CSV, but kept for compatibility)
    """
    if not os.path.exists(csv_file_path):
        print(f"Error: CSV file not found: {csv_file_path}")
        return None
    
    try:
        with open(csv_file_path, 'r', encoding='utf-8') as f:
            # Try to detect delimiter
            sample = f.read(1024)
            f.seek(0)
            sniffer = csv.Sniffer()
            delimiter = sniffer.sniff(sample).delimiter
            
            reader = csv.DictReader(f, delimiter=delimiter)
            
            # Read first row (assuming credentials are in first row)
            row = next(reader, None)
            
            if not row:
                print("Error: CSV file is empty")
                return None
            
            # Common CSV column names for AWS credentials
            access_key_id = None
            secret_access_key = None
            region = None
            
            # Try different possible column names
            for key, value in row.items():
                key_lower = key.lower().strip()
                if 'access' in key_lower and 'key' in key_lower and 'id' in key_lower:
                    access_key_id = value.strip()
                elif 'secret' in key_lower and 'access' in key_lower and 'key' in key_lower:
                    secret_access_key = value.strip()
                elif 'region' in key_lower:
                    region = value.strip()
            
            # If not found by name, try by position (common AWS CSV format)
            if not access_key_id or not secret_access_key:
                values = list(row.values())
                if len(values) >= 2:
                    access_key_id = values[0].strip() if not access_key_id else access_key_id
                    secret_access_key = values[1].strip() if not secret_access_key else secret_access_key
                if len(values) >= 3:
                    region = values[2].strip() if not region else region
            
            if not access_key_id or not secret_access_key:
                print("Error: Could not find Access Key ID and Secret Access Key in CSV")
                print(f"Found columns: {list(row.keys())}")
                return None
            
            return {
                'access_key_id': access_key_id,
                'secret_access_key': secret_access_key,
                'region': region or 'us-east-1'
            }
    
    except Exception as e:
        print(f"Error reading CSV file: {e}")
        return None

def print_github_secrets_instructions(credentials):
    """Print instructions for adding secrets to GitHub"""
    print("\n" + "="*60)
    print("AWS CREDENTIALS EXTRACTED")
    print("="*60)
    print(f"\nAccess Key ID: {credentials['access_key_id']}")
    print(f"Secret Access Key: {'*' * len(credentials['secret_access_key'])}")
    print(f"Region: {credentials['region']}")
    print("\n" + "="*60)
    print("INSTRUCTIONS TO ADD TO GITHUB SECRETS:")
    print("="*60)
    print("\n1. Go to: https://github.com/YOUR_USERNAME/YOUR_REPO/settings/secrets/actions")
    print("\n2. Click 'New repository secret' and add:")
    print(f"\n   Secret Name: AWS_ACCESS_KEY_ID")
    print(f"   Secret Value: {credentials['access_key_id']}")
    print("\n   Secret Name: AWS_SECRET_ACCESS_KEY")
    print(f"   Secret Value: {credentials['secret_access_key']}")
    print("\n   Secret Name: AWS_REGION")
    print(f"   Secret Value: {credentials['region']}")
    print("\n3. Also add:")
    print("   Secret Name: EKS_CLUSTER_NAME")
    print("   Secret Value: <your-eks-cluster-name>")
    print("\n" + "="*60)
    print("⚠️  IMPORTANT: Keep these credentials secure!")
    print("⚠️  Do NOT commit the CSV file to git!")
    print("="*60 + "\n")

def main():
    """Main function"""
    # Look for CSV file in common locations
    csv_file = None
    possible_locations = [
        'Nishit_self_ai_accessKeys.csv',
        './Nishit_self_ai_accessKeys.csv',
        '../Nishit_self_ai_accessKeys.csv',
    ]
    
    for location in possible_locations:
        if os.path.exists(location):
            csv_file = location
            break
    
    if not csv_file:
        print("Error: Could not find CSV file")
        print("Please provide the path to the CSV file:")
        csv_file = input("CSV file path: ").strip()
    
    if not os.path.exists(csv_file):
        print(f"Error: File not found: {csv_file}")
        sys.exit(1)
    
    # Extract credentials
    credentials = extract_credentials(csv_file)
    
    if credentials:
        print_github_secrets_instructions(credentials)
    else:
        print("Failed to extract credentials")
        sys.exit(1)

if __name__ == '__main__':
    main()

