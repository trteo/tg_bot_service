# Sample Data
PRODUCTS = {
    "Electronics": ["Laptop", "Smartphone", "Headphones", "Camera"],
    "Clothing": ["T-shirt", "Jeans", "Jacket", "Sneakers"],
    "Groceries": ["Milk", "Eggs", "Bread", "Fruits"],
    "Groceries2": ["Milk", "Eggs", "Bread", "Fruits"],
    "Groceries3": ["Milk", "Eggs", "Bread", "Fruits"],
    "Groceries4": ["Milk", "Eggs", "Bread", "Fruits"],
}

SUBCATEGORIES = {
    "Electronics": {
        "Laptops": ["MacBook", "Dell XPS", "Lenovo ThinkPad"],
        "Phones": ["iPhone", "Samsung Galaxy", "Google Pixel"]
    },
    "Clothing": {
        "Men": ["Shirt", "Trousers", "Blazer"],
        "Women": ["Dress", "Skirt", "Blouse"]
    }
}


# Getters catalogs
async def get_categories(dialog_manager, **kwargs):
    return {"CATEGORIES": list(PRODUCTS.keys())}


async def get_subcategories(dialog_manager, **kwargs):
    category = dialog_manager.current_context().dialog_data.get("selected_category", "")
    return {"SUBCATEGORIES": list(SUBCATEGORIES.get(category, {}).keys())}


async def get_items(dialog_manager, **kwargs):
    subcategory = dialog_manager.current_context().dialog_data.get("selected_subcategory", "")
    return {
        "ITEMS": SUBCATEGORIES.get(
            dialog_manager.current_context().dialog_data["selected_category"], {}
        ).get(subcategory, [])
    }
