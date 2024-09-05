import shutil
import csv
import requests
import os
from dotenv import load_dotenv
import platform

# Get Shopify access key as environment variable
load_dotenv()
SHOPIFY_ACCESS_KEY = os.getenv('SHOPIFY_ACCESS_KEY')
print(SHOPIFY_ACCESS_KEY)

url = "https://bakers-paradise-6276.myshopify.com/admin/api/2023-07/orders.json"

headers = {
    'Content-Type': 'application/json',
    'X-Shopify-Access-Token': SHOPIFY_ACCESS_KEY,
}

params = {
    'fields': 'order_number,line_items',
}

# Global variables
database_name = "database.csv"
models_folder = "3D-Models"
current_working_directory = os.getcwd()
missing_sku_warning = False
missing_model_file = False
order_numbers = []
items = []
files_to_copy = []
outputs_count = 0
output_folder = "Output"

# Delete previous output folder
if os.path.exists(current_working_directory + "/Output"):
    shutil.rmtree(current_working_directory + "/Output")


response = requests.request("GET", url, headers=headers , params=params)

if response.status_code == 200:

    # Get last order number from database
    with open(database_name, 'r') as file:
        reader = csv.reader(file)
        try:
            row = next(reader)
            last_order_number = int(row[0])
        except StopIteration:
            print(f"{database_name} is empty or does not contain valid data.")
        except ValueError:
            print(f"{database_name} does not contain a valid order number.")
    
    # Get orders from Shopify
    orders = response.json()["orders"]
    for order in orders:

        # Use only new orders
        order_number = order["order_number"]
        if order_number <= last_order_number:
            continue
        else:
            order_numbers.append(order_number)
            line_items = order["line_items"]
            
            # Get SKU from each item
            for line_item in line_items:
                item_name = line_item["name"]
                sku = line_item["sku"]

                # handle platba dobírkou
                if sku is None:
                    continue

                # handle no SKU
                elif sku == "":
                    missing_sku_warning = True
                    print("No SKU for item: " + item_name)

                else:
                    # Create full item object
                                    
                    
                        
                    full_item = {
                        "sku": sku,
                        "item_name": item_name,
                        "order_number": order_number
                    }
                    for x in range(line_item["fulfillable_quantity"]):

                        items.append(full_item)

    # If there are new orders
    if order_numbers:

        # Create new Output directory to access the 3D models
        new_directory_name = "Output"
        destination_folder = current_working_directory
        output_folder_path = os.path.join(destination_folder, new_directory_name)
        
        os.makedirs(output_folder_path, exist_ok=True)

        # Create new directories for orders divisible by 5 and all other
        new_directory_name = "divisible_by_2"
        destination_folder = os.path.join(current_working_directory, output_folder)
        divisible_by_2_folder_path = os.path.join(destination_folder, new_directory_name)

        os.makedirs(divisible_by_2_folder_path, exist_ok=True)

        new_directory_name = "all_other"
        destination_folder = os.path.join(current_working_directory, output_folder)
        all_other_folder_path = os.path.join(destination_folder, new_directory_name)

        os.makedirs(all_other_folder_path, exist_ok=True)

        # Handle promo sets
        new_items = []
        for item in items:
            item_sku = item["sku"]

           #
# Define a dictionary to map model names to file lists
            model_file_mapping = {
                "SET002": ["P0056", "P0057"],
                "SET003": ["carodejnice_na_kosteti", "strasidelna_kocka", "H0031"],
                "SET004": ["Ghosts_3", "Ghosts_2", "Ghosts_1"],
                "SET005": ["jezek_2D", "P0036"],
                "SET006": ["P0060", "Vceli_plastev"],
                "SET007": ["V0091", "V0092"],
                "SET008": ["P0124", "P0125"],
                "SET009": ["kocka-hlava", "kocka"],
                "SET010": ["netopyr2", "netopyr1"],
                "SET011": ["tlapka_se_srdcem", "tlapka_se_srdcem_mala"],
                "SET013": ["tlapka_se_srdcem", "tlapka_se_srdcem_mala"],
                "SET014": ["MAT014", "MAT013", "MAT012", "MAT011", "MAT010"], 
                "SET015": ["KOKR01", "KOKR02"],
                "SET016": ["FOS001", "FOS002", "FOS003", "FOS004"],
                "SET017": ["FOS005", "FOS006"],
                "SET018": ["PES001", "PES002"],
                "SET019": ["PES003", "PES004"],
                "SET020": ["P0040", "P0128", "P0129"],
                "SET022": ["P0130", "P0131", "P0069"],
                "SET024": ["PIV001", "PIV002", "PIV003"],
                "SET025": ["PES005", "PES006"],
                "SET026": ["PES007", "PES008"],
                "SET027": ["VAL001", "VAL002"],
                "SET030": ["P0117", "P0110", "VV001"],
                "SET031": ["P0132", "P0133"],
                "SET034": ["SYM001", "SYM002", "SYM003", "SYM004"],
                "SET035": ["PES009", "PES010"],
                "SET036": ["P0118", "P0119"],
                "SET037": ["P0121", "P0122"],
                "SET038": ["LIS001", "LIS002", "LIS003", "LIS004"],
                "SET040": ["KOC001", "KOC002"],
                "SET041": ["SKOL001", "SKOL002", "SKOL006", "SKOL004"],
                "SET042": ["mickey_mickey_mouse", "MINNIE_mickey_mouse"],
                "SET043": ["PO007", "PO006"],
                "SET044": ["PWP_CHA", "PWP_SKY", "PWP_ZUM", "PWP_MAR", "PWP_ROC", "PWP_LOG"],
                "SET045": ["dinosaur_peppa_pig", "peppa_peppa_pig", "george_peppa_pig", "grandpa_peppa_pig", "granny_peppa_pig", "daddy_peppa_pig", "mom_peppa_pig"],
                "SET046": ["PO008", "PO009", "PO010"],
                "SET047": ["PO013", "PO014", "PO015", "PO011", "PO012"],
                "SET048": ["PO016", "PO017", "PO018", "PO019"],
                "SET049": ["V0140", "V0141", "V0139"],
            }

            # Check if the item is in the mapping, then update files_to_copy

            if item_sku in model_file_mapping:
                for new_sku in model_file_mapping[item_sku]:
                    new_item = {
                        "sku": new_sku,
                        "item_name": new_sku,
                        "order_number": item["order_number"]
                    }
                    new_items.append(new_item)
            else:
                new_items.append(item)

        items = new_items
        for full_item in items:
            # Get object properties
            sku = full_item["sku"]
            model_name = full_item["sku"] + ".stl"
            order_number = full_item["order_number"]

            try:
                # Construct source_file_path and destination_file_path
                source_file_path = os.path.join(current_working_directory, models_folder, model_name)
                if order_number % 2 == 0: 
                    destination_file_path = os.path.join(divisible_by_2_folder_path, model_name)
                else:
                    destination_file_path = os.path.join(all_other_folder_path, model_name)

                # Copy file to new directory
                shutil.copy(source_file_path, destination_file_path)

                # Rename file
                outputs_count += 1

                new_file_name = f"Order_{order_number}_{outputs_count}.stl"
                old_file_name = os.path.join(current_working_directory, divisible_by_2_folder_path if order_number % 2 ==0 else all_other_folder_path, model_name)
                new_file_name = os.path.join(current_working_directory, divisible_by_2_folder_path if order_number % 2 ==0 else all_other_folder_path, new_file_name)
                os.rename(old_file_name, new_file_name)
            except FileNotFoundError:
                missing_model_file = True
                print(f"Error: {model_name} not found in {models_folder} folder. It was in order {order_number}.")
                continue
        
        # Print warnings
        if missing_sku_warning and missing_model_file:
            print("WARNING: Some items are missing SKU")
            print("WARNING: Some items are missing 3D model")
        elif missing_sku_warning:
            print("WARNING: Some items are missing SKU")
        elif missing_model_file:
            print("WARNING: Some items are missing 3D model")
        else:
            print("Everything is OK!")

        # Open the directory
        if platform.system() == "Windows":
            os.system(f"explorer {output_folder_path}")
        elif platform.system() == "Darwin":  # macOS
            os.system(f"open {output_folder_path}")
        else:  # Linux
            os.system(f"xdg-open {output_folder_path}")


        # Get last order number
        sorted_order_numbers = sorted(order_numbers, reverse=True)
        last_order_number = sorted_order_numbers[0]


        # Write last order number to database
        with open( current_working_directory + "/database.csv", "w", newline='') as file:
           writer = csv.writer(file)
           writer.writerow([last_order_number])

    else:
        print("No new orders.")

else:
    print(f"Error: Unable to fetch orders - {response.status_code}")
    print(response.text)
    
