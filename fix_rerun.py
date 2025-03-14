import os
import glob

def fix_experimental_rerun():
    """Find and replace all instances of st.rerun() with st.rerun() in Python files"""
    
    # Get all Python files in the directory and subdirectories
    python_files = glob.glob('**/*.py', recursive=True)
    
    fixed_count = 0
    files_modified = []
    
    for file_path in python_files:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        
        if 'experimental_rerun' in content:
            new_content = content.replace('st.rerun()', 'st.rerun()')
            fixed_count += content.count('st.rerun()')
            
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(new_content)
                
            files_modified.append(file_path)
    
    print(f"Fixed {fixed_count} instances of 'st.rerun()' in {len(files_modified)} files.")
    if files_modified:
        print("Modified files:")
        for file_path in files_modified:
            print(f" - {file_path}")

if __name__ == "__main__":
    fix_experimental_rerun()
