# import streamlit as st

# # Page Config
# st.set_page_config(page_title="Sustainable Frontend", layout="centered")

# # Dynamic values (like HTML attributes)
# heading = "🚀 Welcome to Sustainable"
# button_text = "Click to Visit the Products"
# button_url = "https://example.com"
# background_color = "#403F60"
# text_color = "#333"


# def dash(user):
#     user.name
#     user.products.picture
#     user.period
import streamlit as st
from PIL import Image
import requests
from io import BytesIO

# ---------------------
# Page config
# ---------------------
st.set_page_config(page_title="Reusable Products Site", layout="wide")
st.title("🛒 Reusable Marketplace (OLX-style)")

# ---------------------
# Sample listings data
# ---------------------
listings = [
    {
        "id": 1,
        "title": "iPhone 13 Pro",
        "price": "₹45,000",
        "location": "Mumbai",
        "category": "Mobiles",
        "description": "iPhone 13 Pro, 128GB, great condition. Comes with box & charger.",
        "image": "https://placekitten.com/400/300",
        "seller": "Rahul (Member since 2022)"
    },
    {
        "id": 2,
        "title": "Mountain Bike",
        "price": "₹8,500",
        "location": "Bengaluru",
        "category": "Bikes",
        "description": "Hardtail mountain bike, 21-speed, lightweight frame.",
        "image": "https://placekitten.com/401/300",
        "seller": "Amit (Member since 2021)"
    },
    {
        "id": 3,
        "title": "Wooden Dining Table",
        "price": "₹15,000",
        "location": "Delhi",
        "category": "Furniture",
        "description": "Solid Sheesham wood 4-seater dining table with chairs.",
        "image": "https://placekitten.com/402/300",
        "seller": "Pooja (Member since 2020)"
    },
]

# ---------------------
# Session state for page navigation
# ---------------------
if "page" not in st.session_state:
    st.session_state.page = "home"

def go_to_detail(listing_id):
    st.session_state.page = "detail"
    st.session_state.selected_id = listing_id

def go_home():
    st.session_state.page = "home"

# ---------------------
# Header: Logo | Search | Sell
# ---------------------
col_logo, col_search, col_sell = st.columns([1, 4, 1])
with col_logo:
    st.image("https://upload.wikimedia.org/wikipedia/commons/0/0b/OLX_Logo.svg", width=100)

with col_search:
    search_query = st.text_input("Search for items...", placeholder="Try 'Bamboo', 'Green Materials', etc.")

with col_sell:
    if st.button("Sell"):
        st.info("Redirect to selling workflow (not implemented)")

st.markdown("---")

# ---------------------
# 🏠 HOME
if st.session_state.page == "home":
    # Sidebar filters
    with st.sidebar:
        st.header("🔍 Filters")
        search = st.text_input("Search items...")
        categories = list(set([item["category"] for item in listings]))
        selected_category = st.selectbox("Category", ["All"] + categories)

    # Apply filters
    filtered = listings
    if selected_category != "All":
        filtered = [item for item in filtered if item["category"] == selected_category]
    if search:
        filtered = [item for item in filtered if search.lower() in item["title"].lower()]

    st.subheader("📦 Listings")

    if not filtered:
         st.warning("No items match your search/filter.")
    else:
        cols = st.columns(3)
        for idx, item in enumerate(filtered):
            with cols[idx % 3]:
                try:
                    response = requests.get(item["image"])
                    img = Image.open(BytesIO(response.content))
                    st.image(img, use_column_width=True)
                except:
                    st.warning("⚠️ Image could not be loaded.")

                st.write(f"**{item['title']}**")
                st.write(f"💰 {item['price']}")
                st.write(f"📍 {item['location']}")
                if st.button("View Details", key=f"btn_{item['id']}"):
                    go_to_detail(item["id"])
# ---------------------
# 📄 DETAIL PAGE
# ---------------------
elif st.session_state.page == "detail":
    listing = next((item for item in listings if item["id"] == st.session_state.selected_id), None)
    if listing:
        if st.button("← Back to Listings"):
            go_home()

        try:
            response = requests.get(listing["image"])
            img = Image.open(BytesIO(response.content))
            st.image(img, use_column_width=True)
        except:
            st.warning("⚠️ Image could not be loaded.")

        st.header(listing["title"])
        st.subheader(listing["price"])
        st.write(f"📍 {listing['location']}  |  Category: {listing['category']}")
        st.markdown("### 📃 Description")
        st.write(listing["description"])
        st.markdown("### 🧑‍💼 Seller Info")
        st.info(listing["seller"])
        st.markdown("### 📞 Contact")
        st.write("📞 Phone: +91-98765-43210")
        st.write("📩 Message: [Not implemented]")
    else:
        st.error("Listing not found.")