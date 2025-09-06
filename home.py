import streamlit as st
from io import BytesIO
from PIL import Image
import sqlite3
import requests

# -------------------- Page config --------------------
st.set_page_config(page_title="EcoFinds Marketplace", layout="wide")
def insert_sample_products():
    conn = get_product_conn()
    cur = conn.cursor()

    sample_products = [
        (
            "iPhone 13 Pro", "₹45,000", "Mumbai", "Mobiles",
            "128GB, excellent condition, comes with box and charger.",
            "https://images.pexels.com/photos/5082575/pexels-photo-5082575.jpeg",
            "Rahul Mehta", "2022", "+91-98765-43210", "rahul@example.com",
            "https://images.pexels.com/photos/614810/pexels-photo-614810.jpeg"
        ),
        (
            "Mountain Bike", "₹8,500", "Bengaluru", "Bicycles",
            "21-speed MTB, great for trails. Minor scratches.",
            "https://cdn.moglix.com/p/VFkW4EdbrgeSn-xxlarge.jpg",
            "Amit Singh", "2021", "+91-91234-56789", "amit@example.com",
            "https://images.pexels.com/photos/91227/pexels-photo-91227.jpeg"
        ),
        (
            "Wooden Dining Table", "₹15,000", "Delhi", "Furniture",
            "4-seater Sheesham wood table with cushioned chairs.",
            "https://thetimberguy.com/cdn/shop/products/Buy-Compact-Wooden-Dining-table-with-1-Bench-3-chairs-furniture-set-for-modern-Home_600x.jpg",
            "Pooja Sharma", "2020", "+91-90123-45678", "pooja@example.com",
            "https://images.pexels.com/photos/733872/pexels-photo-733872.jpeg"
        )
    ]

    cur.executemany('''
        INSERT INTO products 
        (title, price, location, category, description, image_url, 
         seller_name, seller_since, seller_phone, seller_email, seller_photo)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', sample_products)

    conn.commit()
    conn.close()

def init_products_table():
    conn = get_product_conn()
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            price TEXT,
            location TEXT,
            category TEXT,
            description TEXT,
            image_url TEXT,
            seller_name TEXT,
            seller_since TEXT,
            seller_phone TEXT,
            seller_email TEXT,
            seller_photo TEXT
        )
    ''')
    conn.commit()
    conn.close()

# Optional: small dark-mode polish
DARK_CSS = """
<style>
:root {
  --bg: #0e1117;
  --fg: #e6e6e6;
  --muted: #a1a1aa;
  --card: #161a23;
  --accent: #22d3ee;
}
.stApp { background: var(--bg); color: var(--fg); }
.block-container { padding-top: 1.5rem; }
h1,h2,h3,h4,h5,h6 { color: var(--fg); }
[data-testid="stImage"] img { border-radius: 14px; }
.ec-title { font-weight: 700; font-size: 1.05rem; margin-top: 0.35rem; }
.ec-price { font-weight: 700; margin: 0.15rem 0 0.25rem 0; }
.ec-meta { color: var(--muted); font-size: 0.9rem; margin-bottom: 0.35rem; }
.stButton > button {
  background: var(--accent);
  color: #041014;
  border: none;
  border-radius: 10px;
}
.stButton > button:hover { filter: brightness(0.95); }
</style>
"""
st.markdown(DARK_CSS, unsafe_allow_html=True)

# -------------------- DB helpers --------------------
PRODUCT_DB = "product.db"

def get_product_conn():
    conn = sqlite3.connect(PRODUCT_DB)
    conn.row_factory = sqlite3.Row
    return conn

def get_all_products_db():
    conn = get_product_conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM products")
    rows = cur.fetchall()
    conn.close()
    return rows

def get_product_by_id(product_id: int):
    conn = get_product_conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM products WHERE id = ?", (product_id,))
    row = cur.fetchone()
    conn.close()
    return row

# -------------------- Image helper --------------------
@st.cache_data(show_spinner=False)
def get_resized_image_bytes(url: str, max_size=(500, 380)):
    try:
        resp = requests.get(url, timeout=6)
        resp.raise_for_status()
        img = Image.open(BytesIO(resp.content)).convert("RGB")
        img.thumbnail(max_size, Image.Resampling.LANCZOS)
        buf = BytesIO()
        img.save(buf, format="JPEG", quality=85, optimize=True)
        return buf.getvalue()
    except Exception:
        return None

# -------------------- Pages --------------------
def homepage():
    # Initialize DB + Insert sample data only if empty
    init_products_table()   
    if not get_all_products_db():  # only insert if table is empty
        insert_sample_products()

    st.title("🛒 EcoFinds Marketplace")
    st.caption("Scroll the latest second-hand listings")

    products = get_all_products_db()
    if not products:
        st.info("No products found. Add some listings to get started!")
        return

    # Responsive grid: 3 per row on desktop
    for i in range(0, len(products), 3):
        cols = st.columns(3, gap="large")
        for col, product in zip(cols, products[i:i+3]):
            with col:
                img_bytes = get_resized_image_bytes(product["image_url"])
                if img_bytes:
                    st.image(img_bytes, use_container_width=True)
                else:
                    st.empty()

                st.markdown(f'<div class="ec-title">{product["title"]}</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="ec-price">💰 {product["price"]}</div>', unsafe_allow_html=True)
                st.markdown(
                    f'<div class="ec-meta">📍 {product["location"]} &nbsp;•&nbsp; 🏷️ {product["category"]}</div>',
                    unsafe_allow_html=True
                )
                with st.expander("📖 Description"):
                    st.write(product["description"])

                if st.button("View Details", key=f"view_{product['id']}"):
                    st.session_state.page = "Detail"
                    st.session_state.selected_id = int(product["id"])
                    st.rerun()

def product_detail():
    if "selected_id" not in st.session_state or st.session_state.selected_id is None:
        st.session_state.page = "Home"
        st.rerun()

    product = get_product_by_id(st.session_state.selected_id)
    if not product:
        st.error("Product not found.")
        if st.button("⬅ Back to Home"):
            st.session_state.page = "Home"
            st.rerun()
        return

    colA, colB = st.columns([3, 2], gap="large")

    with colA:
        img_bytes = get_resized_image_bytes(product["image_url"], max_size=(1200, 900))
        if img_bytes:
            st.image(img_bytes, use_container_width=True)
        st.header(product["title"])
        st.subheader(product["price"])
        st.caption(f"📍 {product['location']} • 🏷️ {product['category']}")
        st.markdown("### 📃 Description")
        st.write(product["description"])

    with colB:
        st.markdown("### 🧑‍💼 Seller")
        if product["seller_photo"]:
            s_img = get_resized_image_bytes(product["seller_photo"], max_size=(220, 220))
            if s_img:
                st.image(s_img, width=120)
        st.write(f"**{product['seller_name']}**")
        if product["seller_since"]:
            st.caption(f"Member since {product['seller_since']}")
        if product["seller_phone"]:
            st.write(f"📞 {product['seller_phone']}")
        if product["seller_email"]:
            st.write(f"📧 {product['seller_email']}")

        st.divider()
        if st.button("⬅ Back to Home"):
            st.session_state.page = "Home"
            st.rerun()
