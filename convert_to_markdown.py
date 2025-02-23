import pymupdf4llm
import os
import path

# Load configuration 
# with open('config.json', 'r') as config_file:
#     config = json.load(config_file)

# section_size = config.get('section_size', 40)

# Define input and output directories
input_dir = 'docs'
output_dir = 'docs/output'

# Create output directory if it doesn't exist
os.makedirs(output_dir, exist_ok=True)

# Process each file in the input directory
for filename in os.listdir(input_dir):
    input_path = os.path.join(input_dir, filename)
    
    if filename.endswith('.pdf'):
        # Convert PDF to Markdown and remove page delineators
        md_text = pymupdf4llm.to_markdown(input_path)
        # Remove page delineators (common patterns like '-----' or page numbers)
        md_text = '\n'.join(line for line in md_text.split('\n')
                            if not line.strip().startswith('-----')
                            and not (line.strip().isdigit() or line.strip() == '')
                            )
        # Save the Markdown output
        output_filename = os.path.splitext(filename)[0] + '.md'
        output_path = os.path.join(output_dir, output_filename)
        with open(output_path, 'w', encoding='utf-8') as output_file:
            output_file.write(md_text)