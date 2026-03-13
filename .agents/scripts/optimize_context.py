#!/usr/bin/env python3
import os
import re
import glob
from pathlib import Path

def optimize_front_matter(file_path):
    print(f"Processing: {file_path}")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
        
    # Check if the file has front matter
    if not content.startswith('---'):
        print(f"  Skipping: No front matter found in {file_path}")
        return False
        
    # Find the end of the front matter
    end_idx = content.find('---', 3)
    if end_idx == -1:
        print(f"  Skipping: Malformed front matter in {file_path}")
        return False
        
    front_matter = content[3:end_idx]
    markdown_body = content[end_idx+3:]
    
    # Extract the description if it exists
    desc_match = re.search(r'description:\s*(.*?)(?=\n[^\s]|$)', front_matter, re.DOTALL)
    if not desc_match:
        print(f"  Skipping: No description found in {file_path}")
        return False
        
    full_description = desc_match.group(1).strip()
    
    # Simple heuristic to generate tags based on filename/path
    filename = Path(file_path).stem
    parent_dir = Path(file_path).parent.name
    
    # Use the filename or parent dir as the primary tag
    primary_tag = filename if filename != 'SKILL' else parent_dir
    primary_tag = primary_tag.replace('-', '_')
    
    # Add a secondary tag based on the plugin type
    plugin_type = ''
    if 'pm-execution' in file_path: plugin_type = 'execution'
    elif 'pm-product-discovery' in file_path: plugin_type = 'discovery'
    elif 'pm-product-strategy' in file_path: plugin_type = 'strategy'
    elif 'pm-market-research' in file_path: plugin_type = 'research'
    elif 'pm-data-analytics' in file_path: plugin_type = 'analytics'
    elif 'pm-go-to-market' in file_path: plugin_type = 'gtm'
    elif 'pm-marketing-growth' in file_path: plugin_type = 'marketing'
    elif 'pm-toolkit' in file_path: plugin_type = 'toolkit'
    
    capabilities_str = f"[{primary_tag}, {plugin_type}]" if plugin_type else f"[{primary_tag}]"
    
    # 1. Replace the description in the front matter with density tags
    new_front_matter = re.sub(
        r'description:\s*.*?(?=\n[A-Za-z_-]+:|$)', 
        f'description: "capabilities: {capabilities_str}"', 
        front_matter, 
        flags=re.DOTALL
    )
    
    # Clean up single quotes from previous YAML descriptions to avoid parsing errors
    new_front_matter = new_front_matter.replace("''", "'") 
    
    # 2. Append the original description into the Markdown body to preserve intent
    intent_preservation_block = f"""

### Skill Context & Intent
**Original Description:** 
> {full_description}

"""
    
    # If there's an H1 header, insert the intent right after it
    h1_match = re.search(r'^#\s+.*?\n', markdown_body, re.MULTILINE)
    
    if h1_match:
        insert_pos = h1_match.end()
        new_markdown_body = markdown_body[:insert_pos] + intent_preservation_block + markdown_body[insert_pos:]
    else:
        # Just put it at the top of the body
        new_markdown_body = intent_preservation_block + markdown_body
        
    
    # Reassemble the file
    new_content = f"---{new_front_matter}---{new_markdown_body}"
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
        
    print(f"  Success: Optimized {primary_tag}")
    return True

def main():
    root_dir = os.path.dirname(os.path.abspath(__file__))
    agents_dir = os.path.join(root_dir, '.agents')
    
    count = 0
    
    # Find all SKILL.md and workflow .md files
    search_patterns = [
        os.path.join(agents_dir, 'skills', '**', 'SKILL.md'),
        os.path.join(agents_dir, 'workflows', '**', '*.md')
    ]
    
    for pattern in search_patterns:
        for file_path in glob.glob(pattern, recursive=True):
            if optimize_front_matter(file_path):
                count += 1
                
    print(f"\nOptimization complete! Successfully processed {count} files.")

if __name__ == "__main__":
    main()
