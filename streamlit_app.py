"""
P100 Gold Redemption — Streamlit Version (Demo/Test Mode)
Test credentials: login = test / password = master123
"""

import os
import time
import random
import secrets
import requests
import streamlit as st
from dotenv import load_dotenv
from tg_notify import send_message

load_dotenv()

# ---------------------- Constants ----------------------
G_TO_OZ = 31.1035
PREMIUM = 1.05
PREMIUM_PERCENTAGE = float(os.getenv("PREMIUM_PERCENTAGE", "0.05"))
BINANCE_BASE = os.getenv("BINANCE_BASE", "https://api.binance.com")
PAXG_SYMBOL = os.getenv("PAXG_SYMBOL", "PAXGUSDT")
MIN_GRAMS = 50
GRAM_STEP = 50

# ---------------------- Page Config ----------------------
st.set_page_config(
    page_title="P100 Gold Redemption",
    page_icon="🥇",
    layout="centered",
)

# ---------------------- Custom CSS ----------------------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=EB+Garamond:wght@400;600&display=swap');

    html, body, [class*="css"] {
        font-family: 'EB Garamond', 'Baskerville', Georgia, serif;
    }
    .gold-title {
        text-align: center;
        font-size: 2.2rem;
        font-weight: 600;
        color: #333;
        letter-spacing: 1px;
        margin-bottom: 0;
    }
    .gold-word { color: #d4af37; }
    .subtitle {
        text-align: center;
        font-size: 1.1rem;
        color: #888;
        margin-top: 4px;
        margin-bottom: 0;
    }
    .divider {
        border: none;
        border-top: 2px solid #d4af37;
        margin: 16px 0 28px 0;
    }
    .metric-label {
        font-size: 0.85rem;
        color: #888;
        margin-bottom: 2px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .metric-value {
        font-size: 1.6rem;
        font-weight: 600;
        color: #222;
        margin-bottom: 12px;
    }
    .info-box {
        background: #fffdf4;
        border-left: 4px solid #d4af37;
        padding: 12px 16px;
        border-radius: 4px;
        margin: 12px 0;
        font-size: 0.95rem;
        color: #444;
    }
    .success-box {
        background: #f0fff4;
        border-left: 4px solid #2e7d32;
        padding: 14px 18px;
        border-radius: 4px;
        margin: 12px 0;
    }
    .error-box {
        background: #fff0f0;
        border-left: 4px solid #b00020;
        padding: 14px 18px;
        border-radius: 4px;
        margin: 12px 0;
    }
    div[data-testid="stButton"] > button {
        background-color: #333;
        color: white;
        border: 1px solid #333;
        border-radius: 3px;
        padding: 0.5rem 1.5rem;
        font-family: 'EB Garamond', serif;
        font-size: 1rem;
        transition: all 0.2s;
    }
    div[data-testid="stButton"] > button:hover {
        background-color: #d4af37;
        border-color: #d4af37;
        color: #333;
    }
    .tx-box {
        background: #f8f8f8;
        border: 1px solid #ddd;
        border-radius: 4px;
        padding: 14px;
        font-family: monospace;
        font-size: 0.95rem;
        margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)


# ---------------------- Helpers ----------------------
def get_paxg_price() -> float:
    try:
        r = requests.get(
            f"{BINANCE_BASE}/api/v3/ticker/price",
            params={"symbol": PAXG_SYMBOL},
            timeout=10,
        )
        r.raise_for_status()
        return float(r.json().get("price", 0.0))
    except Exception:
        return 4050.0  # fallback


def verify_mt5_credentials(login: str, password: str) -> dict:
    """Demo mode — only test account accepted. Replace with real MT5Manager calls."""
    if login == "test" and password == "master123":
        equity = round(20000.0 + 10000.0 * random.random(), 2)
        return {
            "verified": True,
            "equity": equity,
            "positions": [
                {"ID": "1", "time": "2026-01-01 12:53:00", "symbol": "XAUUSD",   "volume": 0.01, "price": 5010.54},
                {"ID": "2", "time": "2026-01-01 13:19:00", "symbol": "XAUUSD",   "volume": 0.01, "price": 5005.10},
                {"ID": "3", "time": "2026-01-02 09:05:00", "symbol": "XAUUSD.s", "volume": 0.01, "price": 4998.75},
            ],
            "total_lot": 0.03,
        }
    return {"verified": False, "reason": "Invalid credentials"}


def perform_redemption(login: str, password: str, redeem_grams: float,
                       required_equity: float, selected_positions: list) -> str:
    """Demo mode — returns a mock TX ID. Replace with real MT5Manager calls."""
    tx_id = f"TX{int(time.time())}{secrets.token_hex(3)}"
    try:
        bot_token = os.getenv("BOT_TOKEN_TV")
        chat_id = os.getenv("CHAT_ID_TV")
        if bot_token and chat_id:
            send_message(bot_token, chat_id,
                         f"[DEMO] Redemption processed\nLogin: {login}\nGrams: {redeem_grams}\nTX: {tx_id}")
    except Exception:
        pass
    return tx_id


# ---------------------- Session State Init ----------------------
defaults = {
    "step": "login",          # login | verified | redeemed
    "login": "",
    "password": "",
    "equity": 0.0,
    "positions": [],
    "total_lot": 0.0,
    "paxg_price": 0.0,
    "max_grams": 0.0,
    "redeem_grams": 50,
    "selected_ids": [],
    "calc_done": False,
    "required_equity": 0.0,
    "tx_id": "",
    "consent_given": False,
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v


# ---------------------- Header ----------------------
st.markdown('<p class="gold-title">P100 <span class="gold-word">Gold</span> Redemption</p>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">MT5 Account Verification & Gold Redemption</p>', unsafe_allow_html=True)
st.markdown('<hr class="divider">', unsafe_allow_html=True)


# ======================================================
# STEP 1 — LOGIN
# ======================================================
if st.session_state.step == "login":

    with st.form("login_form"):
        st.subheader("Account Verification")
        login_input = st.text_input("MT5 Login", placeholder="e.g. test")
        password_input = st.text_input("MT5 Master Password", type="password", placeholder="e.g. master123")

        consent = st.checkbox(
            "I understand and consent to allow P100 Gold to access and verify my MT5 account data for redemption purposes."
        )
        submitted = st.form_submit_button("🔍 Verify Account")

    if submitted:
        if not login_input or not password_input:
            st.markdown('<div class="error-box">⚠️ Please enter both your MT5 Login and Master Password.</div>', unsafe_allow_html=True)
        elif not consent:
            st.markdown('<div class="error-box">⚠️ You must provide consent to proceed.</div>', unsafe_allow_html=True)
        else:
            with st.spinner("Verifying your account..."):
                result = verify_mt5_credentials(login_input, password_input)

            if not result.get("verified"):
                st.markdown(f'<div class="error-box">❌ Verification failed: {result.get("reason", "Invalid credentials")}</div>', unsafe_allow_html=True)
            else:
                paxg_price = get_paxg_price()
                equity = float(result["equity"])
                redeemable_paxg = equity * (1 - PREMIUM_PERCENTAGE) / paxg_price if paxg_price > 0 else 0.0
                max_grams = redeemable_paxg * G_TO_OZ

                st.session_state.update({
                    "step": "verified",
                    "login": login_input,
                    "password": password_input,
                    "equity": equity,
                    "positions": result.get("positions", []),
                    "total_lot": float(result.get("total_lot", 0.0)),
                    "paxg_price": paxg_price,
                    "max_grams": max_grams,
                    "consent_given": True,
                    "calc_done": False,
                    "selected_ids": [],
                })
                st.rerun()


# ======================================================
# STEP 2 — VERIFIED: SHOW ACCOUNT + REDEMPTION FORM
# ======================================================
elif st.session_state.step == "verified":

    # — Change account button
    if st.button("🔄 Change Account"):
        for k, v in defaults.items():
            st.session_state[k] = v
        st.rerun()

    # — Account Summary
    st.subheader(f"Account Summary — {st.session_state.login}")
    st.markdown('<hr class="divider">', unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown('<div class="metric-label">Equity</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="metric-value">${st.session_state.equity:,.2f}</div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="metric-label">Gold Price (XAU/oz)</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="metric-value">${st.session_state.paxg_price:,.2f}</div>', unsafe_allow_html=True)
    with col3:
        st.markdown('<div class="metric-label">Max Redeemable</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="metric-value">{st.session_state.max_grams:.2f} g</div>', unsafe_allow_html=True)

    per_gram = (st.session_state.paxg_price * PREMIUM) / G_TO_OZ
    st.markdown(
        f'<div class="info-box">💡 1 g = <strong>${per_gram:.2f} USD</strong> (includes 5% premium) &nbsp;|&nbsp; 1 oz = {G_TO_OZ} g</div>',
        unsafe_allow_html=True,
    )

    # — Positions Table
    st.markdown("#### Open Positions")
    positions = st.session_state.positions
    if not positions:
        st.info("No open positions found.")
        selected_positions = []
    else:
        # Checkbox selection per position
        st.caption("Select positions to close as part of your redemption:")
        selected_positions = []
        cols_header = st.columns([0.5, 1.5, 1.5, 1.2, 1.2, 2])
        for h, label in zip(cols_header, ["✓", "Position ID", "Symbol", "Volume", "Price", "Open Time"]):
            h.markdown(f"**{label}**")
        st.divider()

        for pos in positions:
            cols = st.columns([0.5, 1.5, 1.5, 1.2, 1.2, 2])
            checked = cols[0].checkbox("", value=True, key=f"pos_{pos['ID']}", label_visibility="collapsed")
            cols[1].write(pos["ID"])
            cols[2].write(pos["symbol"])
            cols[3].write(f"{float(pos['volume']):.2f}")
            cols[4].write(f"${float(pos['price']):,.2f}")
            cols[5].write(pos["time"])
            if checked:
                selected_positions.append(pos)

        st.session_state.selected_ids = [p["ID"] for p in selected_positions]

    st.markdown('<hr class="divider">', unsafe_allow_html=True)

    # — Redemption Amount
    st.subheader("Redemption Amount")
    redeem_grams = st.number_input(
        "Grams to redeem",
        min_value=MIN_GRAMS,
        max_value=max(MIN_GRAMS, int((st.session_state.max_grams // GRAM_STEP) * GRAM_STEP)),
        step=GRAM_STEP,
        value=st.session_state.redeem_grams,
        help=f"Minimum {MIN_GRAMS} g, must be a multiple of {GRAM_STEP} g",
    )
    st.session_state.redeem_grams = redeem_grams

    # Validate
    def validate_grams(g):
        if g < MIN_GRAMS:
            return f"Minimum is {MIN_GRAMS} g"
        if g % GRAM_STEP != 0:
            return f"Must be a multiple of {GRAM_STEP} g"
        if g > st.session_state.max_grams + 0.001:
            return f"Exceeds your maximum redeemable amount ({st.session_state.max_grams:.2f} g)"
        return None

    gram_error = validate_grams(redeem_grams)

    col_calc, _ = st.columns([1, 3])
    with col_calc:
        calc_clicked = st.button("📊 Calculate")

    if calc_clicked:
        if gram_error:
            st.markdown(f'<div class="error-box">⚠️ {gram_error}</div>', unsafe_allow_html=True)
            st.session_state.calc_done = False
        else:
            oz = redeem_grams / G_TO_OZ
            required_equity = oz * st.session_state.paxg_price * PREMIUM
            st.session_state.required_equity = required_equity
            st.session_state.calc_done = True

    # Show calculation result
    if st.session_state.calc_done and not gram_error:
        oz = st.session_state.redeem_grams / G_TO_OZ
        req = st.session_state.required_equity
        st.markdown(f"""
        <div class="info-box">
            <strong>Redemption Calculation</strong><br>
            Grams: <strong>{st.session_state.redeem_grams} g</strong> → <strong>{oz:.4f} oz</strong><br>
            XAU Price: <strong>${st.session_state.paxg_price:,.4f} USD/oz</strong><br>
            Premium: <strong>5%</strong><br>
            <br>
            Estimated equity required: <strong>${req:,.2f} USD</strong>
        </div>
        """, unsafe_allow_html=True)

        # — Confirm & Redeem
        st.markdown("---")
        st.warning(
            f"⚠️ You are about to redeem **{st.session_state.redeem_grams} g** ({oz:.4f} oz). "
            f"This will deduct **${req:,.2f} USD** from your equity (includes 5% premium). "
            f"This action **cannot be undone**."
        )

        confirm_col, _ = st.columns([1, 3])
        with confirm_col:
            confirm_clicked = st.button("✅ Confirm & Redeem", type="primary")

        if confirm_clicked:
            if not selected_positions:
                st.warning("No positions selected. Proceeding without closing positions.")

            # Final validation
            final_error = validate_grams(st.session_state.redeem_grams)
            if final_error:
                st.markdown(f'<div class="error-box">❌ {final_error}</div>', unsafe_allow_html=True)
            elif st.session_state.equity < req:
                st.markdown('<div class="error-box">❌ Insufficient equity for this redemption.</div>', unsafe_allow_html=True)
            else:
                with st.spinner("Processing your redemption..."):
                    tx_id = perform_redemption(
                        login=st.session_state.login,
                        password=st.session_state.password,
                        redeem_grams=st.session_state.redeem_grams,
                        required_equity=req,
                        selected_positions=selected_positions,
                    )

                st.session_state.tx_id = tx_id
                st.session_state.step = "redeemed"
                st.rerun()


# ======================================================
# STEP 3 — REDEMPTION SUCCESS
# ======================================================
elif st.session_state.step == "redeemed":

    st.markdown("""
    <div class="success-box">
        <h3 style="color:#2e7d32;margin:0 0 8px 0">✅ Redemption Successful</h3>
        <p style="margin:0;color:#444">Your gold redemption has been processed successfully.</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("#### Transaction Details")
    st.markdown(f"""
    <div class="tx-box">
        TX ID: <strong>{st.session_state.tx_id}</strong><br>
        Login: {st.session_state.login}<br>
        Grams Redeemed: {st.session_state.redeem_grams} g<br>
        Equity Deducted: ${st.session_state.required_equity:,.2f} USD
    </div>
    """, unsafe_allow_html=True)

    st.markdown(
        "📧 For assistance, contact support at "
        "[support@p100gold.com](mailto:support@p100gold.com)",
        unsafe_allow_html=False,
    )

    st.markdown("---")
    if st.button("🔄 Start New Redemption"):
        for k, v in defaults.items():
            st.session_state[k] = v
        st.rerun()