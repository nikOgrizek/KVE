from io import BytesIO
from scipy.interpolate import interp1d
import numpy as np
import matplotlib.pyplot as plt
from reportlab.platypus import Image
from reportlab.lib.units import inch

#from app.gui import logger


def calculate_annual_production(wind_data, turbines, height):
    annual_production = 0
    hours_per_year = 8760

    for turbine in turbines:
        try:
            speeds = list(map(float, turbine["speeds"]))
            powers = list(map(float, turbine["powers"]))

            if len(speeds) != len(powers):
                raise ValueError(f"Speeds and powers arrays must be of equal length for turbine {turbine['name']}.")

            power_curve = interp1d(speeds, powers, kind='linear', bounds_error=False, fill_value=(0.0, max(powers)))

            wind_speeds = wind_data["wind_speed_100m"]
            hourly_production = power_curve(wind_speeds) / 1000  # Convert to MWh
            total_production = np.sum(hourly_production)

            annual_production += total_production
        except ValueError as ve:
            #logger.error(f"ValueError for turbine {turbine['name']}: {ve}")
            continue  # Preskočite to turbino in nadaljujte
        except TypeError as te:
            #logger.error(f"TypeError for turbine {turbine['name']}: {te}")
            continue  # Preskočite to turbino in nadaljujte
        except Exception as e:
            #logger.error(f"Unexpected error for turbine {turbine['name']}: {e}")
            continue  # Preskočite to turbino in nadaljujte
    return annual_production

def calculate_monthly_production(wind_data, turbines, height):
    hours_per_year = 8760
    hours_per_month = [31 * 24, 28 * 24, 31 * 24, 30 * 24, 31 * 24, 30 * 24, 31 * 24, 31 * 24, 30 * 24, 31 * 24, 30 * 24, 31 * 24]

    monthly_production = np.zeros((len(turbines), 12))

    for idx, turbine in enumerate(turbines):
        try:
            speeds = list(map(float, turbine["speeds"]))
            powers = list(map(float, turbine["powers"]))

            if len(speeds) != len(powers):
                raise ValueError(f"Speeds and powers arrays must be of equal length for turbine {turbine['name']}.")

            power_curve = interp1d(speeds, powers, kind='linear', bounds_error=False, fill_value=(0.0, max(powers)))

            wind_speeds = wind_data["wind_speed_100m"]
            hourly_production = power_curve(wind_speeds) / 1000  # Convert to MWh

            start_hour = 0
            for month in range(12):
                end_hour = start_hour + hours_per_month[month]
                monthly_production[idx, month] = np.sum(hourly_production[start_hour:end_hour])
                start_hour = end_hour

        except Exception as e:
            print(f"Error calculating production for turbine {turbine['name']}: {e}")

    # Create the plot
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    plt.figure(figsize=(10, 5))
    for idx, turbine in enumerate(turbines):
        plt.bar(months, monthly_production[idx], label=f"{turbine['name']}")

    plt.xlabel('Month')
    plt.ylabel('Production (GWh)')
    plt.title('Monthly Wind Energy Production')

    # Save plot to BytesIO object
    img_buf = BytesIO()
    plt.savefig(img_buf, format='png')
    plt.close()
    img_buf.seek(0)

    # Return monthly production and plot image
    return monthly_production, Image(img_buf, width=3.2 * inch, height=1.9 * inch)
