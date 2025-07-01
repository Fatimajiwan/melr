from app import create_app, db
from app.models.monitoring import Measurement
from sample_indicators import create_sample_indicators
from datetime import datetime, timedelta
import random

app = create_app()

def create_sample_measurements():
    with app.app_context():
        # Get or create the sample indicators
        indicators = create_sample_indicators()
        
        # Skip if no indicators were returned (already existed)
        if not indicators:
            from app.models.indicator import Indicator
            indicators = Indicator.query.all()
            if not indicators:
                print("No indicators found. Please run sample_indicators.py first.")
                return
        
        # Create Measurements (historical data for the past 12 months)
        measurements = []
        
        for indicator in indicators:
            # Check if measurements already exist for this indicator
            existing_measurements = Measurement.query.filter_by(indicator_id=indicator.id).first()
            if existing_measurements:
                print(f"Measurements already exist for indicator {indicator.name}.")
                continue
            
            # Calculate a realistic progression from baseline to current value
            baseline = indicator.baseline if indicator.baseline is not None else 0
            current = indicator.current_value
            target = indicator.target_value
            
            # Generate data points for the past 12 months
            for i in range(12):
                # Calculate expected value with some randomness
                # Earlier months closer to baseline, recent months closer to current value
                progress_factor = i / 12.0  # 0 to 1 progression factor
                expected_value = baseline + (current - baseline) * progress_factor
                
                # Add some random variation (±10%)
                variation = expected_value * 0.1
                value = expected_value + random.uniform(-variation, variation)
                
                # Ensure the value makes sense (e.g., counts can't be negative)
                if indicator.unit == "count" and value < 0:
                    value = 0
                
                # Create the measurement
                measurement_date = datetime.now() - timedelta(days=(12-i)*30)
                
                measurement = Measurement(
                    indicator_id=indicator.id,
                    value=round(value, 2),
                    date=measurement_date,
                    notes=f"Monthly measurement for {indicator.name}"
                )
                measurements.append(measurement)
        
        if measurements:
            db.session.add_all(measurements)
            db.session.commit()
            print(f"Created {len(measurements)} data points for {len(indicators)} indicators")
        else:
            print("No new measurements created.")

if __name__ == "__main__":
    create_sample_measurements() 