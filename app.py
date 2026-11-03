import streamlit as st
import MetaTrader5 as mt5
import google.generativeai as genai
import pandas as pd
import time

st.set_page_config(page_title="AI Trading Bot - XM Global", layout="wide")

st.title("🤖 100% Free Autonomous AI Trading Bot for XM MT5")
st.markdown("This dashboard connects your XM Global MT5 account with Google Gemini AI to execute trades automatically.")

# Sidebar configuration for inputs
st.sidebar.header("🔑 Configuration Settings")
api_key = st.sidebar.text_input("Google Gemini API Key", type="password")

st.sidebar.subheader("MT5 Account Details")
mt5_login = st.sidebar.number_input("MT5 Account ID", value=0, step=1)
mt5_password = st.sidebar.text_input("MT5 Password", type="password")
mt5_server = st.sidebar.text_input("MT5 Server Name", value="XMGlobal-Real")

st.sidebar.subheader("Trading Parameters")
symbol = st.sidebar.text_input("Trading Symbol", value="XAUUSD")
lot_size = st.sidebar.number_input("Lot Size", value=0.01, step=0.01)

# Main Dashboard controls
if api_key and mt5_login and mt5_password:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash')

    if st.button("🚀 Start Auto Trading"):
        st.write("Connecting to MT5 and initializing AI analysis...")
        
        # Initialize MT5 connection
        if not mt5.initialize(login=int(mt5_login), password=mt5_password, server=mt5_server):
            st.error(f"MT5 initialization failed, error code = {mt5.last_error()}")
        else:
            st.success("Successfully connected to XM Global MT5!")
            
            # Ensure symbol is available
            if not mt5.symbol_select(symbol, True):
                st.error(f"Failed to select symbol {symbol}")
                mt5.shutdown()
            else:
                placeholder = st.empty()
                
                # Autonomous loop
                for i in range(5): # Runs a few cycles for demonstration
                    rates = mt5.copy_rates_from_pos(symbol, mt5.TIMEFRAME_M1, 0, 10)
                    if rates is not None:
                        df = pd.DataFrame(rates)
                        current_price = mt5.symbol_info_tick(symbol).ask
                        
                        prompt = f"Analyze market data for {symbol}. Current price is {current_price}. Recent candles: {df.tail(3).to_string()}. Give a strict decision: BUY, SELL, or HOLD."
                        
                        response = model.generate_content(prompt)
                        decision = response.text.strip().upper()
                        
                        placeholder.markdown(f"""
                        ### Loop Cycle {i+1}
                        * **Current Price ({symbol}):** {current_price}
                        * **Gemini AI Decision:** {decision}
                        """)
                        
                        # Execute trade based on AI decision
                        if "BUY" in decision:
                            request = {
                                "action": mt5.TRADE_ACTION_DEAL,
                                "symbol": symbol,
                                "volume": float(lot_size),
                                "type": mt5.ORDER_TYPE_BUY,
                                "price": current_price,
                                "deviation": 20,
                                "magic": 234000,
                                "comment": "AI Bot Buy Order",
                                "type_time": mt5.ORDER_TIME_GTC,
                                "type_filling": mt5.ORDER_FILLING_IOC,
                            }
                            result = mt5.order_send(request)
                            if result.retcode != mt5.TRADE_RETCODE_DONE:
                                st.warning(f"Order failed: {result.retcode}")
                            else:
                                st.success(f"BUY Order Executed Successfully at {current_price}!")
                                
                        elif "SELL" in decision:
                            request = {
                                "action": mt5.TRADE_ACTION_DEAL,
                                "symbol": symbol,
                                "volume": float(lot_size),
                                "type": mt5.ORDER_TYPE_SELL,
                                "price": current_price,
                                "deviation": 20,
                                "magic": 234000,
                                "comment": "AI Bot Sell Order",
                                "type_time": mt5.ORDER_TIME_GTC,
                                "type_filling": mt5.ORDER_FILLING_IOC,
                            }
                            result = mt5.order_send(request)
                            if result.retcode != mt5.TRADE_RETCODE_DONE:
                                st.warning(f"Order failed: {result.retcode}")
                            else:
                                st.success(f"SELL Order Executed Successfully at {current_price}!")
                    
                    time.sleep(10)
                
                mt5.shutdown()
                st.info("Trading cycle completed.")
else:
    st.info("Please enter your Google Gemini API Key and XM MT5 credentials in the sidebar to begin.")
