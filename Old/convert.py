import json
import os
import pandas as pd
import time

# Create a unique version number based on the exact second you run this script
cloud_version = int(time.time())
version_data = {"version": cloud_version}

# Save it to a tiny version.json file
with open("version.json", "w") as f:
    json.dump(version_data, f)

print("✅ Generated version.json (Version: {cloud_version})")


def parse_specs(specs_string):
    """Converts Excel line breaks into a clean JSON dictionary."""
    if pd.isna(specs_string) or not str(specs_string).strip():
        return {}
    specs_dict = {}
    lines = str(specs_string).split("\n")
    for line in lines:
        if ":" in line:
            key, value = line.split(":", 1)
            specs_dict[key.strip()] = value.strip()
    return specs_dict


def excel_to_techfinder_json(excel_path, json_output_path):
    if not os.path.exists(excel_path):
        print(f"❌ Error: Could not find the file '{excel_path}'!")
        return

    # Read the Excel Sheet
    df = pd.read_excel(excel_path)

    catalog_list = []

    # 🚨 CRITICAL CONFIG: Put your unique Cloudflare R2 Public URL here!
    # Remember to leave the trailing slash '/' at the end.
    # R2_BASE_URL = "https://pub-your-unique-bucket-id.r2.dev/"
    # 🚨 GITHUB STORAGE CONFIG: Change this to pull images directly from GitHub!
    # Make sure to replace 'devabhisheksoni' with your actual username if needed.
    R2_BASE_URL = "https://cdn.jsdelivr.net/gh/devabhisheksoni/techfinder_database@main/images/"

    for index, row in df.iterrows():
        # Crash-proof check: If the row or the ID is completely empty, skip it entirely
        if pd.isna(row["id"]) or not str(row["id"]).strip():
            continue

        # Crash-proof check for price: If empty, set to 0, otherwise convert safely
        try:
            if pd.isna(row["price"]):
                raw_price = 0
            else:
                raw_price = int(float(row["price"]))
        except ValueError:
            print(
                f"⚠️ Warning at row {index + 2}: Invalid price value '{row['price']}'. Setting to 0."
            )
            raw_price = 0

        # AUTOMATED IMAGE ARRAY CALCULATION
        # Reads 'image_count' column. If empty, non-existent, or 0, defaults safely to 1 image.
        try:
            if (
                "image_count" in df.columns
                and not pd.isna(row["image_count"])
                and str(row["image_count"]).strip().isdigit()
            ):
                img_count = int(row["image_count"])
                if img_count < 1:
                    img_count = 1
            else:
                img_count = 1
        except Exception:
            img_count = 1

        # Builds the multi-image URL list instantly based on your indexed folder naming pattern
        # e.g., id_0.webp, id_1.webp, id_2.webp...
        product_id = str(row["id"]).strip()
        image_urls_list = [
            f"{R2_BASE_URL}{product_id}_{i}.webp" for i in range(img_count)
        ]

        # Construct the unified data document dictionary
        product = {
            "id": product_id,
            "category": str(row["category"]).strip()
            if not pd.isna(row["category"])
            else "",
            "tier": str(row["tier"]).strip() if not pd.isna(row["tier"]) else "",
            "brand": str(row["brand"]).strip() if not pd.isna(row["brand"]) else "",
            "title": str(row["title"]).strip() if not pd.isna(row["title"]) else "",
            "price": raw_price,
            "image_urls": image_urls_list,  # Replaces 'image_url' with the smart automated array list!
            "affiliate_link": str(row["affiliate_link"]).strip()
            if not pd.isna(row["affiliate_link"])
            else "",
            "specs": parse_specs(row["specs"]),
        }
        catalog_list.append(product)

    # Output to beautifully indented JSON file
    with open(json_output_path, "w", encoding="utf-8") as f:
        json.dump(catalog_list, f, indent=2, ensure_ascii=False)

    print(
        f"🚀 Success! Processed {len(catalog_list)} products into: {json_output_path}"
    )


# Execute the conversion
excel_to_techfinder_json("TechFinder_Data.xlsx", "TechFinder_Data.json")