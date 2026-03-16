import xml.etree.ElementTree as ET
import os
import tkinter as tk
from tkinter import filedialog, messagebox

def select_file(title, file_types):
    root = tk.Tk()
    root.withdraw()  # Hide the main tkinter window
    file_path = filedialog.askopenfilename(title=title, filetypes=file_types)
    root.destroy()
    return file_path

def process_xliff():
    # Register namespaces to maintain XLIFF 1.2 structure
    ET.register_namespace('', "urn:oasis:names:tc:xliff:document:1.2")
    ns = {'xliff': 'urn:oasis:names:tc:xliff:document:1.2'}

    while True:
        print("\n--- Starting Alignment ---")
        
        # 1. Select the CURRENT file (Correct IDs)
        print("Waiting for 'Current' file selection...")
        current_path = select_file("Select CURRENT File (Correct IDs/Structure)", [("XLIFF files", "*.xlf *.xliff"), ("All files", "*.*")])
        if not current_path: 
            print("Operation cancelled.")
            break

        # 2. Select the VERIFIED file (Target Text)
        print("Waiting for 'Verified' file selection...")
        verified_path = select_file("Select VERIFIED File (Verified Gujarati Text)", [("XLIFF files", "*.xlf *.xliff"), ("All files", "*.*")])
        if not verified_path:
            print("Operation cancelled.")
            break

        try:
            # 3. Build the Translation Map from the Verified File
            v_tree = ET.parse(verified_path)
            v_root = v_tree.getroot()
            translation_map = {}

            for unit in v_root.findall('.//xliff:trans-unit', ns):
                source = unit.find('xliff:source', ns)
                target = unit.find('xliff:target', ns)
                
                # We map the text content of the source to the text content of the target
                if source is not None and target is not None and source.text:
                    translation_map[source.text.strip()] = target.text

            # 4. Inject into the Current File
            c_tree = ET.parse(current_path)
            c_root = c_tree.getroot()
            match_count = 0
            new_units_count = 0

            for unit in c_root.findall('.//xliff:trans-unit', ns):
                source = unit.find('xliff:source', ns)
                target = unit.find('xliff:target', ns)
                
                if source is not None and source.text:
                    clean_source = source.text.strip()
                    if clean_source in translation_map:
                        if target is None:
                            target = ET.SubElement(unit, '{urn:oasis:names:tc:xliff:document:1.2}target')
                        
                        target.text = translation_map[clean_source]
                        match_count += 1
                    else:
                        new_units_count += 1

            # 5. Save the result in the same directory as the current file
            output_dir = os.path.dirname(current_path)
            output_name = os.path.join(output_dir, f"Aligned_{os.path.basename(current_path)}")
            
            c_tree.write(output_name, encoding='utf-8', xml_declaration=True)
            
            summary = (f"Success!\n\n"
                       f"Matched/Updated: {match_count} units\n"
                       f"Unmatched (New Content): {new_units_count} units\n\n"
                       f"Saved to: {output_name}")
            
            print(summary)
            messagebox.showinfo("Processing Complete", summary)

        except Exception as e:
            error_msg = f"An error occurred: {str(e)}"
            print(error_msg)
            messagebox.showerror("Error", error_msg)

        # 6. Ask to continue
        if not messagebox.askyesno("Continue?", "Would you like to process another file?"):
            break

if __name__ == "__main__":
    process_xliff()
