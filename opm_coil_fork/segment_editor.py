import re
'''

Chat GPT wrote this so I did not have to

'''

def parse_segments(file_path):
    with open(file_path, 'r') as file:
        data = file.read()
    
    # Regular expression to find all segment blocks, considering possible leading tabs
    segments = re.findall(r'(\t*\(segment[\s\S]*?\n\s*\))', data)
    print(f"Parsed {len(segments)} segments")
    
    return segments

def filter_segments(segments, max_x, min_x, max=False, min=False):
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
                    filtered_segments.append(segment)
                    print("Segment added to filtered list")
            elif(max):
                if start_x <= max_x + 1e-9 and end_x <= max_x + 1e-9:
                    filtered_segments.append(segment)
                    print("Segment added to filtered list")
                print("Segment discarded")
    
    print(f"Filtered down to {len(filtered_segments)} segments")
    return filtered_segments

def write_segments(file_path, segments):
    with open(file_path, 'w') as file:
        for segment in segments:
            # Write segment without adding an extra `)` at the end
            file.write(segment + '\n')
    print(f"Wrote {len(segments)} segments to {file_path}")


# Example usage
input_file = 'segments.txt'
output_file = 'filtered_segments.txt'
min_x, max_x = -200, -200  # Set this value based on your requirements

segments = parse_segments(input_file)
filtered_segments = filter_segments(segments, max_x, min_x, min = True)
write_segments(output_file, filtered_segments)




