#!/usr/bin/env python
from sample_project import create_sample_project
from sample_framework import create_sample_frameworks
from sample_indicators import create_sample_indicators
from sample_measurements import create_sample_measurements

def create_all_sample_data():
    print("Starting sample data creation process...")
    print("\n1. Creating sample project...")
    create_sample_project()
    
    print("\n2. Creating frameworks (LogFrame, Theory of Change, Results Framework)...")
    create_sample_frameworks()
    
    print("\n3. Creating indicators...")
    create_sample_indicators()
    
    print("\n4. Creating measurement data...")
    create_sample_measurements()
    
    print("\nAll sample data created successfully!")
    print("\nYou can now log in and explore the sample project with:")
    print("- Username: admin")
    print("- Password: admin123")
    print("\nVisit: http://127.0.0.1:5001/")

if __name__ == "__main__":
    create_all_sample_data()
