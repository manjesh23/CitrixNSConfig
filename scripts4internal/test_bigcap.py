import os
from datetime import datetime


def convert_timestamp(timestamp):
    # Define the input and output datetime formats
    input_format = ['%Y-%m-%d %H:%M:%S', '%Y-%m-%d %H:%M',
                    '%Y-%m-%d', '%d-%m-%Y %H:%M:%S', '%d-%m-%Y %H:%M', '%d-%m-%Y']
    output_format = "%b %d %H:%M:%S"

    # Iterate over the input formats and try to convert the timestamp
    for fmt in input_format:
        try:
            dt = datetime.strptime(timestamp, fmt)
            return dt.strftime(output_format)
        except ValueError:
            pass

    # If no format matches, return None
    return None


def find_matching_log_files(timestamp):
    formatted_timestamp = convert_timestamp(timestamp)
    if formatted_timestamp is None:
        print("Invalid timestamp format!")
        return

    matching_logs = []
    for file_name in os.listdir('.'):
        if file_name.endswith('.*'):
            log_timestamp = file_name.split('.')[0]
            if log_timestamp == formatted_timestamp:
                matching_logs.append(file_name)

    return matching_logs


# Get timestamp from user
user_timestamp = input("Enter the timestamp (in any format): ")

# Find matching log files
matching_logs = find_matching_log_files(user_timestamp)

# Display the matching log files
if matching_logs:
    print("Matching log files:")
    for log_file in matching_logs:
        print(log_file)
else:
    print("No matching log files found.")
