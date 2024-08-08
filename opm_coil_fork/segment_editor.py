import re

def parse_segments(file_path):
    with open(file_path, 'r') as file:
        data = file.read()
    
    # Regular expression to find all segment blocks, considering possible leading tabs
    segments = re.findall(r'(\t*\(segment[\s\S]*?\n\s*\))', data)
    print(f"Parsed {len(segments)} segments")
    
    return segments

def scale_segment_coordinates(segment, scaling_factor):
    start_match = re.search(r'\(start ([\-.\d]+) ([\-.\d]+)\)', segment)
    end_match = re.search(r'\(end ([\-.\d]+) ([\-.\d]+)\)', segment)
    
    if start_match and end_match:
        start_x = float(start_match.group(1)) * scaling_factor
        start_y = float(start_match.group(2)) * scaling_factor
        end_x = float(end_match.group(1)) * scaling_factor
        end_y = float(end_match.group(2)) * scaling_factor
        
        # Replace the coordinates in the segment string
        segment = re.sub(r'\(start [\-.\d]+ [\-.\d]+\)', f'(start {start_x} {start_y})', segment)
        segment = re.sub(r'\(end [\-.\d]+ [\-.\d]+\)', f'(end {end_x} {end_y})', segment)
    
    return segment

def filter_segments(segments, scaling_factor, max_x, min_x, max=False, min=False):
    filtered_segments = []
    
    for segment in segments:
        start_match = re.search(r'\(start ([\-.\d]+) ([\-.\d]+)\)', segment)
        end_match = re.search(r'\(end ([\-.\d]+) ([\-.\d]+)\)', segment)
        
        if start_match and end_match:
            start_x = float(start_match.group(1))
            end_x = float(end_match.group(1))
            
            print(f"Segment: {segment.strip()}")
            print(f"Start: (x: {start_x}), End: (x: {end_x})")

            if (min):
                # Add a small tolerance to the comparison to avoid floating-point issues
                if start_x >= min_x - 1e-9 and end_x >= min_x - 1e-9:
                    scaled_segment = scale_segment_coordinates(segment, scaling_factor)
                    filtered_segments.append(scaled_segment)
                    print("Segment added to filtered list")
            elif(max):
                if start_x <= max_x + 1e-9 and end_x <= max_x + 1e-9:
                    scaled_segment = scale_segment_coordinates(segment, scaling_factor)
                    filtered_segments.append(scaled_segment)
                    print("Segment added to filtered list")
                print("Segment discarded")
    
    print(f"Filtered down to {len(filtered_segments)} segments")
    return filtered_segments

def write_segments(file_path, segments):
    with open(file_path, 'w') as file:
        for segment in segments:
            # Write segment without adding an extra `)` at the end
            file.write(segment + '\n')
    #print(f"Wrote {len(segments)} segments to {file_path}")

# Example usage
input_file = 'segments.txt'
output_file = 'filtered_segments.txt'
scaling_factor = 0.38825498
min_x, max_x = -2000, 2000  # Set this value based on your requirements

segments = parse_segments(input_file)
filtered_segments = filter_segments(segments, scaling_factor, max_x, min_x, min=True)
write_segments(output_file, filtered_segments)
