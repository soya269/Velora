# products = [
#     {
#         "id": 5,
#         "title": "Classic Black Hooded Sweatshirt",
#         "slug": "classic-black-hooded-sweatshirt",
#         "price": 79,
#         "description": "Elevate your casual wardrobe with our Classic Black Hooded Sweatshirt.",
#         "category": {
#             "id": 1,
#             "name": "Fashion"
#         },
#         "images": [
#             "https://i.imgur.com/cSytoSD.jpeg"
#         ]
#     },
#     {
#         "id": 6,
#         "title": "Classic Comfort Fit Joggers",
#         "slug": "classic-comfort-fit-joggers",
#         "price": 25,
#         "description": "Comfortable black joggers perfect for daily wear.",
#         "category": {
#             "id": 1,
#             "name": "Fashion"
#         },
#         "images": [
#             "https://i.imgur.com/ZKGofuB.jpeg"
#         ]
#     },
#     {
#         "id": 9,
#         "title": "Classic Navy Blue Baseball Cap",
#         "slug": "classic-navy-blue-baseball-cap",
#         "price": 61,
#         "description": "Stylish navy blue baseball cap.",
#         "category": {
#             "id": 1,
#             "name": "Fashion"
#         },
#         "images": [
#             "https://i.imgur.com/R3iobJA.jpeg"
#         ]
#     },
#     {
#         "id": 15,
#         "title": "Classic White Crew Neck T-Shirt",
#         "slug": "classic-white-crew-neck-t-shirt",
#         "price": 39,
#         "description": "Soft and stylish white t-shirt.",
#         "category": {
#             "id": 1,
#             "name": "Fashion"
#         },
#         "images": [
#             "https://i.imgur.com/axsyGpD.jpeg"
#         ]
#     },
#     {
#         "id": 18,
#         "title": "Wireless Gaming Controller",
#         "slug": "wireless-gaming-controller",
#         "price": 69,
#         "description": "Modern wireless gaming controller.",
#         "category": {
#             "id": 2,
#             "name": "Electronics"
#         },
#         "images": [
#             "https://i.imgur.com/ZANVnHE.jpeg"
#         ]
#     },
#     {
#         "id": 20,
#         "title": "Comfort-Fit Headphones",
#         "slug": "comfort-fit-headphones",
#         "price": 28,
#         "description": "High quality over-ear headphones.",
#         "category": {
#             "id": 2,
#             "name": "Electronics"
#         },
#         "images": [
#             "https://i.imgur.com/SolkFEB.jpeg"
#         ]
#     },
#     {
#         "id": 22,
#         "title": "Wireless Computer Mouse",
#         "slug": "wireless-computer-mouse",
#         "price": 10,
#         "description": "Smooth and precise wireless mouse.",
#         "category": {
#             "id": 2,
#             "name": "Electronics"
#         },
#         "images": [
#             "https://i.imgur.com/w3Y8NwQ.jpeg"
#         ]
#     },
#     {
#         "id": 23,
#         "title": "Modern Laptop",
#         "slug": "modern-laptop",
#         "price": 43,
#         "description": "Slim and powerful laptop.",
#         "category": {
#             "id": 2,
#             "name": "Electronics"
#         },
#         "images": [
#             "https://i.imgur.com/OKn1KFI.jpeg"
#         ]
#     },
#     {
#         "id": 28,
#         "title": "Modern Leather Sofa",
#         "slug": "modern-leather-sofa",
#         "price": 53,
#         "description": "Luxury leather sofa for modern homes.",
#         "category": {
#             "id": 3,
#             "name": "Furniture"
#         },
#         "images": [
#             "https://i.imgur.com/Qphac99.jpeg"
#         ]
#     },
#     {
#         "id": 34,
#         "title": "Ergonomic Office Chair",
#         "slug": "ergonomic-office-chair",
#         "price": 71,
#         "description": "Comfortable office chair for productivity.",
#         "category": {
#             "id": 3,
#             "name": "Furniture"
#         },
#         "images": [
#             "https://i.imgur.com/3dU0m72.jpeg"
#         ]
#     },
#     {
#         "id": 35,
#         "title": "Holographic Soccer Cleats",
#         "slug": "holographic-soccer-cleats",
#         "price": 39,
#         "description": "Stylish futuristic soccer shoes.",
#         "category": {
#             "id": 4,
#             "name": "Shoes"
#         },
#         "images": [
#             "https://i.imgur.com/hKcMNJs.jpeg"
#         ]
#     },
#     {
#         "id": 39,
#         "title": "Pink Classic Sneakers",
#         "slug": "pink-classic-sneakers",
#         "price": 84,
#         "description": "Bold and colorful pink sneakers.",
#         "category": {
#             "id": 4,
#             "name": "Shoes"
#         },
#         "images": [
#             "https://i.imgur.com/mcW42Gi.jpeg"
#         ]
#     },
#     {
#         "id": 45,
#         "title": "Electric Bicycle",
#         "slug": "electric-bicycle",
#         "price": 22,
#         "description": "Eco-friendly electric bicycle.",
#         "category": {
#             "id": 5,
#             "name": "Miscellaneous"
#         },
#         "images": [
#             "https://i.imgur.com/BG8J0Fj.jpg"
#         ]
#     },
#     {
#         "id": 47,
#         "title": "Radiant Citrus Perfume",
#         "slug": "radiant-citrus-perfume",
#         "price": 73,
#         "description": "Fresh citrus scented perfume.",
#         "category": {
#             "id": 5,
#             "name": "Miscellaneous"
#         },
#         "images": [
#             "https://i.imgur.com/xPDwUb3.jpg"
#         ]
#     },
#     {
#         "id": 50,
#         "title": "Pink-Tinted Sunglasses",
#         "slug": "pink-tinted-sunglasses",
#         "price": 38,
#         "description": "Fashionable pink sunglasses.",
#         "category": {
#             "id": 5,
#             "name": "Miscellaneous"
#         },
#         "images": [
#             "https://i.imgur.com/0qQBkxX.jpg"
#         ]
#     }
# ]
#
# def get_all_products():
#
#     for product in products:
#
#         product.setdefault(
#             "name",
#             product.get("title", "")
#         )
#
#         product.setdefault(
#             "cost",
#             0
#         )
#
#         product.setdefault(
#             "stock",
#             0
#         )
#
#         product.setdefault(
#             "images",
#             []
#         )
#
#     return products
# def get_next_id():
#     if not products:
#         return 1
#
#     return max(p["id"] for p in products) + 1
#
#
# def add_product(product):
#     products.append(product)
#
#
# def update_product(product_id, updated_product):
#     for index, product in enumerate(products):
#
#         if product["id"] == product_id:
#             products[index] = updated_product
#             return True
#
#     return False
#
#
# def delete_product(product_id):
#     global products
#
#     products = [
#         p for p in products
#         if p["id"] != product_id
#     ]
#
#
# def get_product_by_title(title):
#     return next(
#         (
#             p for p in products
#             if p["title"].lower() == title.lower()
#         ),
#         None
#     )
#
#
# def get_product_by_id(product_id):
#     return next(
#         (
#             p for p in products
#             if p["id"] == product_id
#         ),
#         None
#     )
#
#
# def get_related_products(category_name, current_product_id):
#
#     related_products = []
#
#     for product in products:
#
#         if (
#             product["category"]["name"].lower()
#             == category_name.lower()
#             and product["id"] != current_product_id
#         ):
#             related_products.append(product)
#
#     return related_products


# products.py
# ============================================================
# VELORA SHOP - Shared Product Data
# Used by:
# - Home Page
# - Shop Page
# - Product Detail
# - Cart
# - Admin Products
# - Core API
# ============================================================


# ============================================================
# PRODUCT DATA
# ============================================================

products = [
    {
        "id": 5,
        "title": "Classic Black Hooded Sweatshirt",
        "slug": "classic-black-hooded-sweatshirt",
        "price": 79,
        "description": "Elevate your casual wardrobe with our Classic Black Hooded Sweatshirt.",
        "category": {
            "id": 1,
            "name": "Fashion"
        },
        "images": [
            "https://i.imgur.com/cSytoSD.jpeg"
        ]
    },
    {
        "id": 6,
        "title": "Classic Comfort Fit Joggers",
        "slug": "classic-comfort-fit-joggers",
        "price": 25,
        "description": "Comfortable black joggers perfect for daily wear.",
        "category": {
            "id": 1,
            "name": "Fashion"
        },
        "images": [
            "https://i.imgur.com/ZKGofuB.jpeg"
        ]
    },
    {
        "id": 9,
        "title": "Classic Navy Blue Baseball Cap",
        "slug": "classic-navy-blue-baseball-cap",
        "price": 61,
        "description": "Stylish navy blue baseball cap.",
        "category": {
            "id": 1,
            "name": "Fashion"
        },
        "images": [
            "https://i.imgur.com/R3iobJA.jpeg"
        ]
    },
    {
        "id": 15,
        "title": "Classic White Crew Neck T-Shirt",
        "slug": "classic-white-crew-neck-t-shirt",
        "price": 39,
        "description": "Soft and stylish white t-shirt.",
        "category": {
            "id": 1,
            "name": "Fashion"
        },
        "images": [
            "https://i.imgur.com/axsyGpD.jpeg"
        ]
    },
    {
        "id": 18,
        "title": "Wireless Gaming Controller",
        "slug": "wireless-gaming-controller",
        "price": 69,
        "description": "Modern wireless gaming controller.",
        "category": {
            "id": 2,
            "name": "Electronics"
        },
        "images": [
            "https://i.imgur.com/ZANVnHE.jpeg"
        ]
    },
    {
        "id": 20,
        "title": "Comfort-Fit Headphones",
        "slug": "comfort-fit-headphones",
        "price": 28,
        "description": "High quality over-ear headphones.",
        "category": {
            "id": 2,
            "name": "Electronics"
        },
        "images": [
            "https://i.imgur.com/SolkFEB.jpeg"
        ]
    },
    {
        "id": 22,
        "title": "Wireless Computer Mouse",
        "slug": "wireless-computer-mouse",
        "price": 10,
        "description": "Smooth and precise wireless mouse.",
        "category": {
            "id": 2,
            "name": "Electronics"
        },
        "images": [
            "https://i.imgur.com/w3Y8NwQ.jpeg"
        ]
    },
    {
        "id": 23,
        "title": "Modern Laptop",
        "slug": "modern-laptop",
        "price": 43,
        "description": "Slim and powerful laptop.",
        "category": {
            "id": 2,
            "name": "Electronics"
        },
        "images": [
            "https://i.imgur.com/OKn1KFI.jpeg"
        ]
    },
    {
        "id": 28,
        "title": "Modern Leather Sofa",
        "slug": "modern-leather-sofa",
        "price": 53,
        "description": "Luxury leather sofa for modern homes.",
        "category": {
            "id": 3,
            "name": "Furniture"
        },
        "images": [
            "https://i.imgur.com/Qphac99.jpeg"
        ]
    },
    {
        "id": 34,
        "title": "Ergonomic Office Chair",
        "slug": "ergonomic-office-chair",
        "price": 71,
        "description": "Comfortable office chair for productivity.",
        "category": {
            "id": 3,
            "name": "Furniture"
        },
        "images": [
            "https://i.imgur.com/3dU0m72.jpeg"
        ]
    },
    {
        "id": 35,
        "title": "Holographic Soccer Cleats",
        "slug": "holographic-soccer-cleats",
        "price": 39,
        "description": "Stylish futuristic soccer shoes.",
        "category": {
            "id": 4,
            "name": "Shoes"
        },
        "images": [
            "https://i.imgur.com/hKcMNJs.jpeg"
        ]
    },
    {
        "id": 39,
        "title": "Pink Classic Sneakers",
        "slug": "pink-classic-sneakers",
        "price": 84,
        "description": "Bold and colorful pink sneakers.",
        "category": {
            "id": 4,
            "name": "Shoes"
        },
        "images": [
            "https://i.imgur.com/mcW42Gi.jpeg"
        ]
    },
    {
        "id": 45,
        "title": "Electric Bicycle",
        "slug": "electric-bicycle",
        "price": 22,
        "description": "Eco-friendly electric bicycle.",
        "category": {
            "id": 5,
            "name": "Miscellaneous"
        },
        "images": [
            "https://i.imgur.com/BG8J0Fj.jpg"
        ]
    },
    {
        "id": 47,
        "title": "Radiant Citrus Perfume",
        "slug": "radiant-citrus-perfume",
        "price": 73,
        "description": "Fresh citrus scented perfume.",
        "category": {
            "id": 5,
            "name": "Miscellaneous"
        },
        "images": [
            "https://i.imgur.com/xPDwUb3.jpg"
        ]
    },
    {
        "id": 50,
        "title": "Pink-Tinted Sunglasses",
        "slug": "pink-tinted-sunglasses",
        "price": 38,
        "description": "Fashionable pink sunglasses.",
        "category": {
            "id": 5,
            "name": "Miscellaneous"
        },
        "images": [
            "https://i.imgur.com/0qQBkxX.jpg"
        ]
    }
]


# ============================================================
# NORMALIZE PRODUCT
# ============================================================

def normalize_product(product):

    if not product:
        return product

    # ID
    product.setdefault("id", 0)

    # Title
    product.setdefault("title", "")

    # Name
    product.setdefault(
        "name",
        product.get("title", "")
    )

    # Slug
    product.setdefault("slug", "")

    # Price
    product.setdefault("price", 0)

    # Cost
    product.setdefault("cost", 0)

    # Stock
    product.setdefault("stock", 0)

    # Description
    product.setdefault("description", "")

    # Category
    if not isinstance(product.get("category"), dict):
        product["category"] = {
            "id": 0,
            "name": "No category"
        }

    product["category"].setdefault("id", 0)

    product["category"].setdefault(
        "name",
        "No category"
    )

    # Images
    if not isinstance(product.get("images"), list):
        product["images"] = []

    return product


# ============================================================
# GET ALL PRODUCTS
# ============================================================

def get_all_products():

    for product in products:
        normalize_product(product)

    return products


# ============================================================
# GET NEXT PRODUCT ID
# ============================================================

def get_next_id():

    if not products:
        return 1

    return max(
        product.get("id", 0)
        for product in products
    ) + 1


# ============================================================
# ADD PRODUCT
# ============================================================

def add_product(product):

    normalize_product(product)

    products.append(product)



# ============================================================
# UPDATE PRODUCT
# ============================================================

def update_product(product_id, updated_product):
    """
    Update a product using its ID.

    Returns:
        True  = updated successfully
        False = product not found
    """

    normalize_product(updated_product)

    for index, product in enumerate(products):

        if product.get("id") == product_id:

            products[index] = updated_product

            return True

    return False


# ============================================================
# DELETE PRODUCT
# ============================================================

def delete_product(product_id):
    """
    Delete a product using its ID.
    """

    global products

    products = [
        product
        for product in products
        if product.get("id") != product_id
    ]


# ============================================================
# GET PRODUCT BY ID
# ============================================================

def get_product_by_id(product_id):
    """
    Find a product by ID.

    Returns:
        Product dictionary if found
        None if not found
    """

    for product in products:

        if product.get("id") == product_id:

            return normalize_product(product)

    return None


# ============================================================
# GET PRODUCT BY TITLE
# ============================================================

def get_product_by_title(title):
    """
    Find a product by title.

    Search is case-insensitive.
    """

    if not title:
        return None

    title = title.strip().lower()

    for product in products:

        product_title = product.get(
            "title",
            ""
        ).strip().lower()

        if product_title == title:

            return normalize_product(product)

    return None


# ============================================================
# GET PRODUCT BY SLUG
# ============================================================

def get_product_by_slug(slug):
    """
    Find a product by slug.

    Search is case-insensitive.
    """

    if not slug:
        return None

    slug = slug.strip().lower()

    for product in products:

        product_slug = product.get(
            "slug",
            ""
        ).strip().lower()

        if product_slug == slug:

            return normalize_product(product)

    return None


# ============================================================
# GET RELATED PRODUCTS
# ============================================================

def get_related_products(
    category_name,
    current_product_id
):
    """
    Get products from the same category.

    The current product is excluded.
    """

    if not category_name:
        return []

    related_products = []

    category_name = category_name.strip().lower()

    for product in products:

        normalize_product(product)

        category = product.get(
            "category",
            {}
        )

        product_category = category.get(
            "name",
            ""
        ).strip().lower()

        if (
            product_category == category_name
            and product.get("id") != current_product_id
        ):
            related_products.append(product)

    return related_products


# ============================================================
# SEARCH PRODUCTS
# ============================================================

def search_products(keyword):
    """
    Search products by:
    - title
    - name
    - description
    """

    if not keyword:
        return get_all_products()

    keyword = keyword.strip().lower()

    result = []

    for product in products:

        normalize_product(product)

        title = product.get(
            "title",
            ""
        ).lower()

        name = product.get(
            "name",
            ""
        ).lower()

        description = product.get(
            "description",
            ""
        ).lower()

        if (
            keyword in title
            or keyword in name
            or keyword in description
        ):
            result.append(product)

    return result


# ============================================================
# GET PRODUCTS BY CATEGORY
# ============================================================

def get_products_by_category(category_name):
    """
    Return all products in a category.
    """

    if not category_name:
        return get_all_products()

    category_name = category_name.strip().lower()

    result = []

    for product in products:

        normalize_product(product)

        category = product.get(
            "category",
            {}
        )

        product_category = category.get(
            "name",
            ""
        ).strip().lower()

        if product_category == category_name:

            result.append(product)

    return result


# ============================================================
# INITIAL NORMALIZATION
# ============================================================

# Normalize the original 15 products
# when this module is imported.

for product in products:
    normalize_product(product)

