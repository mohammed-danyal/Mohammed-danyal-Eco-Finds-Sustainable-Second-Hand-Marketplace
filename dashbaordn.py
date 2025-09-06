import streamlit as st
from PIL import Image
import requests
from io import BytesIO

# # ----------------------------
# # 🖼️ Cached image resizer (returns bytes or None)
# # ----------------------------
# @st.cache_data(show_spinner=False)
# def get_resized_image_bytes(url: str, max_size=(100, 100)):
#     """
#     Returns JPEG bytes of a resized image or None on failure.
#     """
#     try:
#         resp = requests.get(url, timeout=6)
#         resp.raise_for_status()
#         img = Image.open(BytesIO(resp.content)).convert("RGB")
#         img.thumbnail(max_size, Image.Resampling.LANCZOS)
#         buf = BytesIO()
#         img.save(buf, format="JPEG", quality=85, optimize=True)
#         return buf.getvalue()
#     except Exception:
#         return None

# # ----------------------------
# # 🧾 Sample Listings Data (fixed structure)
# # ----------------------------
# listings = [
#     {
#         "id": 1,
#         "title": "iPhone 13 Pro",
#         "price": "₹45,000",
#         "location": "Mumbai",
#         "category": "Mobiles",
#         "description": "iPhone 13 Pro, 128GB, excellent condition. Comes with box and charger.",
#         "image": "https://images.pexels.com/photos/5082575/pexels-photo-5082575.jpeg",
#         "seller": {
#             "name": "Rahul Mehta",
#             "member_since": "2022",
#             "phone": "+91-98765-43210",
#             "email": "rahul@example.com",
#             "photo": "https://images.pexels.com/photos/614810/pexels-photo-614810.jpeg"
#         }
#     },
#     {
#         "id": 2,
#         "title": "Mountain Bike",
#         "price": "₹8,500",
#         "location": "Bengaluru",
#         "category": "Bicycles",
#         "description": "21-speed mountain bike, good for trail riding. Minor scratches.",
#         "image": "https://cdn.moglix.com/p/VFkW4EdbrgeSn-xxlarge.jpg",
#         "seller": {
#             "name": "Amit Singh",
#             "member_since": "2021",
#             "phone": "+91-91234-56789",
#             "email": "amit@example.com",
#             "photo": "https://images.pexels.com/photos/91227/pexels-photo-91227.jpeg"
#         }
#     },
#     {
#         "id": 3,
#         "title": "Wooden Dining Table",
#         "price": "₹15,000",
#         "location": "Delhi",
#         "category": "Furniture",
#         "description": "4-seater Sheesham wood dining table with cushioned chairs.",
#         "image": "https://thetimberguy.com/cdn/shop/products/Buy-Compact-Wooden-Dining-table-with-1-Bench-3-chairs-furniture-set-for-modern-Home_600x.jpg?v=1637950097",
#         "seller": {
#             "name": "Pooja Sharma",
#             "member_since": "2020",
#             "phone": "+91-90123-45678",
#             "email": "pooja@example.com",
#             "photo": "https://images.pexels.com/photos/733872/pexels-photo-733872.jpeg"
#         }
#     }
# ]

# # ----------------------------
# # 📦 Dashboard Function
# # ----------------------------
# def show_dashboard():
#     st.title("🛍️ Second-Hand Items Dashboard")

#     # Sidebar Filters
#     with st.sidebar:
#         st.header("🔍 Filter Items")
#         search_query = st.text_input("Search by name")
#         all_categories = sorted({item["category"] for item in listings})
#         selected_category = st.selectbox("Filter by category", ["All"] + all_categories)

#     # Filter Logic
#     filtered_listings = [
#         item for item in listings
#         if (selected_category == "All" or item["category"] == selected_category)
#         and (not search_query or search_query.lower() in item["title"].lower())
#     ]

#     # Display Listings in Grid
#     st.subheader("📦 Available Listings")
#     cols = st.columns(3)

#     for idx, item in enumerate(filtered_listings):
#         with cols[idx % 3]:
#             img_bytes = get_resized_image_bytes(item["image"], max_size=(400, 300))
#             if img_bytes:
#                 st.image(img_bytes, use_container_width=True)
#             else:
#                 try:
#                     st.image(item["image"], use_container_width=True)
#                 except Exception:
#                     st.warning("Product image unavailable")

#             st.markdown(f"### {item['title']}")
#             st.write(f"**💰 Price:** {item['price']}")
#             st.write(f"📍 Location: {item['location']}")
#             st.write(f"🗂️ Category: {item['category']}")
#             st.markdown("**📝 Description:**")
#             st.write(item["description"])

#             # Seller Info
#             st.markdown("---")
#             st.markdown("**👤 Seller Info**")
#             seller = item.get("seller", {})
#             seller_col1, seller_col2 = st.columns([1, 3])
#             with seller_col1:
#                 photo_url = seller.get("photo")
#                 if photo_url:
#                     seller_bytes = get_resized_image_bytes(photo_url, max_size=(80, 80))
#                     if seller_bytes:
#                         st.image(seller_bytes, width=60, use_container_width=True)
#                     else:
#                         st.info("Seller photo unavailable")
#                 else:
#                     st.info("No seller photo")

#             with seller_col2:
#                 st.write(f"**Name:** {seller.get('name','-')}")
#                 st.write(f"📆 Member since: {seller.get('member_since','-')}")
#                 st.write(f"📞 Phone: {seller.get('phone','-')}")
#                 st.write(f"📧 Email: {seller.get('email','-')}")

#             st.markdown("—" * 20)
import backend_db

def show_dashboard():
    st.title("🛍️ Second-Hand Items Dashboard")

    # Sidebar filters
    with st.sidebar:
        st.header("🔍 Filter Items")
        search_query = st.text_input("Search by name")
        categories = sorted({row["category"] for row in backend_db.get_all_products()})
        selected_category = st.selectbox("Filter by category", ["All"] + categories)

    # Fetch filtered products
    if search_query:
        products = backend_db.search_products(search_query)
    else:
        products = backend_db.get_all_products()

    if selected_category != "All":
        products = [p for p in products if p["category"] == selected_category]

    # Show results
    st.subheader("📦 Available Listings")
    cols = st.columns(3)

    for idx, row in enumerate(products):
        with cols[idx % 3]:
            try:
                st.image(row["image_url"], use_container_width=True)
            except Exception:
                st.warning("Image unavailable")

            st.markdown(f"### {row['title']}")
            st.write(f"**💰 Price:** {row['price']}")
            st.write(f"📍 Location: {row['location']}")
            st.write(f"🗂️ Category: {row['category']}")
            st.markdown("**📝 Description:**")
            st.write(row["description"])

            st.markdown("---")
            st.markdown("**👤 Seller Info**")
            st.write(f"**Name:** {row['seller_name']}")
            st.write(f"📆 Member since: {row['seller_since']}")
            st.write(f"📞 Phone: {row['seller_phone']}")
            st.write(f"📧 Email: {row['seller_email']}")
