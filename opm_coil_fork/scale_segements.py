import re

def parse_segments(file_path):
    with open(file_path, 'r') as file:
        data = file.read()
    
    # Capture each segment as a block, including all additional fields
    segments = re.findall(r'\(segment\s+\(start\s+[-.\d]+\s+[-.\d]+\)\s+\(end\s+[-.\d]+\s+[-.\d]+\)(?:\s+\([^)]+\))*\)', data)
    print(f"Parsed {len(segments)} segments")
    
    return segments

def scale_segment_coordinates(segment, scaling_factor):
    # Find and scale the "start" and "end" coordinates
    start_match = re.search(r'\(start\s+([-.\d]+)\s+([-.\d]+)\)', segment)
    end_match = re.search(r'\(end\s+([-.\d]+)\s+([-.\d]+)\)', segment)
    
    if start_match and end_match:
        # Scale start coordinates
        start_x = float(start_match.group(1)) * scaling_factor
        start_y = float(start_match.group(2)) * scaling_factor
        # Scale end coordinates
        end_x = float(end_match.group(1)) * scaling_factor
        end_y = float(end_match.group(2)) * scaling_factor
        
        # Replace coordinates in the segment string
        segment = re.sub(r'\(start\s+[-.\d]+\s+[-.\d]+\)', f'(start {start_x:.6f} {start_y:.6f})', segment)
        segment = re.sub(r'\(end\s+[-.\d]+\s+[-.\d]+\)', f'(end {end_x:.6f} {end_y:.6f})', segment)

    # Set the "width" parameter to 1 without affecting other fields like "layer" and "net"
    segment = re.sub(r'\(width\s+[-.\d]+\)', '(width 1)', segment)
    
    return segment

def scale_all_segments(segments, scaling_factor):
    # Apply scaling to each segment
    scaled_segments = [scale_segment_coordinates(segment, scaling_factor) for segment in segments]
    print(f"Scaled {len(scaled_segments)} segments")
    return scaled_segments

def find_min_x(segments):
    x_coords = []
    for segment in segments:
        start_match = re.search(r'\(start\s+([-.\d]+)\s+([-.\d]+)\)', segment)
        end_match = re.search(r'\(end\s+([-.\d]+)\s+([-.\d]+)\)', segment)
        
        if start_match and end_match:
            x_coords.append(float(start_match.group(1)))
            x_coords.append(float(end_match.group(1)))
    
    # Find the smallest X value
    min_x = min(x_coords) if x_coords else 0
    print(f"Minimum X value found: {min_x}")
    return min_x

def offset_segment_coordinates(segment, offset_x, offset_y):
    # Find and offset the "start" and "end" coordinates by the offset_x and offset_y
    start_match = re.search(r'\(start\s+([-.\d]+)\s+([-.\d]+)\)', segment)
    end_match = re.search(r'\(end\s+([-.\d]+)\s+([-.\d]+)\)', segment)
    
    if start_match and end_match:
        # Offset start coordinates
        start_x = float(start_match.group(1)) + offset_x
        start_y = float(start_match.group(2)) + offset_y
        # Offset end coordinates
        end_x = float(end_match.group(1)) + offset_x
        end_y = float(end_match.group(2)) + offset_y
        
        # Replace coordinates in the segment string
        segment = re.sub(r'\(start\s+[-.\d]+\s+[-.\d]+\)', f'(start {start_x:.6f} {start_y:.6f})', segment)
        segment = re.sub(r'\(end\s+[-.\d]+\s+[-.\d]+\)', f'(end {end_x:.6f} {end_y:.6f})', segment)

    return segment

def offset_all_segments(segments, offset_x, offset_y):
    # Apply offset to each segment
    offset_segments = [offset_segment_coordinates(segment, offset_x, offset_y) for segment in segments]
    print(f"Offset {len(offset_segments)} segments")
    return offset_segments

def write_segments(file_path, segments):
    with open(file_path, 'w') as file:
        for segment in segments:
            file.write('\t' + segment + '\n')  # Add a tab before each segment line
    print(f"Wrote {len(segments)} segments to {file_path}")

# Example usage
input_file = 'final_z_segments.txt'
output_file = 'z_scaled_and_offset_segments.txt'
scaling_factor = 0.38825498
y_offset = +98.5  # Fixed Y offset

# Step 1: Parse and scale segments
segments = parse_segments(input_file)
scaled_segments = scale_all_segments(segments, scaling_factor)

# Step 2: Find the minimum X value in the scaled segments
min_x = find_min_x(scaled_segments)

# Step 3: Offset the scaled segments based on the minimum X value and fixed Y offset
offset_segments = offset_all_segments(scaled_segments, -min_x, y_offset)

# Step 4: Write the results to a file
write_segments(output_file, offset_segments)
