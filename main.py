# signal_bot.py
import os
import pandas as pd
import numpy as np
from ta.trend import EMAIndicator, ADXIndicator
from ta.momentum import RSIIndicator
from ta.volatility import AverageTrueRange
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

# ---------- إعدادات ----------
TELEGRAM_TOKEN = "7996482415:AAHEPHHVflgsuDJkG-LUyfB2WCJRtnWZbZE"

EMA_FAST = 5
EMA_SLOW = 20
RSI_PERIOD = 14
ATR_PERIOD = 14
ADX_PERIOD = 14

SCORE_THRESHOLD = 3   # تحتاج 3+ لإشارة قوية
RISK_PCT = 0.01

# ---------- دوال المساعدة ----------
def load_candles(pair: str, limit=200):
    """
    تحميل بيانات الشموع الأخيرة للزوج.
    حالياً يستخدم CSV محلي: اسم الملف يجب أن يكون candles_<PAIR>.csv
    بالصيغ: timestamp,open,high,low,close,volume
    بدل ذلك ضع ربط API هنا.
    """
    fname = f"candles_{pair.replace('/','').upper()}.csv"
    if not os.path.exists(fname):
        raise FileNotFoundError(f"CSV for {pair} not found: {fname}")
    df = pd.read_csv(fname, parse_dates=['timestamp'])
    return df.tail(limit).reset_index(drop=True)

def add_indicators(df):
    df = df.copy()
    df['ema_fast'] = EMAIndicator(df['close'], EMA_FAST).ema_indicator()
    df['ema_slow'] = EMAIndicator(df['close'], EMA_SLOW).ema_indicator()
    df['rsi'] = RSIIndicator(df['close'], RSI_PERIOD).rsi()
    df['atr'] = AverageTrueRange(df['high'], df['low'], df['close'], window=ATR_PERIOD).average_true_range()
    df['adx'] = ADXIndicator(df['high'], df['low'], df['close'], window=ADX_PERIOD).adx()
    return df

def find_swings(df, left=3, right=3):
    highs, lows = [], []
    for i in range(left, len(df)-right):
        win = df.iloc[i-left:i+right+1]
        if df['high'].iat[i] == win['high'].max():
            highs.append((i, df['high'].iat[i]))
        if df['low'].iat[i] == win['low'].min():
            lows.append((i, df['low'].iat[i]))
    return highs, lows

def build_zones(df, swings, atr_multiplier=1.0):
    zones = []
    atr = df['atr'].fillna(method='bfill').iloc[-1] if 'atr' in df.columns else 0
    pad = atr * atr_multiplier
    for idx, price in swings:
        zones.append((price - pad, price + pad))
    return zones

def price_near_zone(price, zones, pct_threshold=0.002):
    for lo, hi in zones:
        if lo <= price <= hi:
            return True
        if abs(price - ((lo+hi)/2)) / (price + 1e-9) < pct_threshold:
            return True
    return False

def score_signal(df):
    """
    يعيد 'BUY' أو 'SELL' أو 'WAIT' مع شرح مختصر.
    """
    df = add_indicators(df)
    highs, lows = find_swings(df, left=3, right=3)
    support_zones = build_zones(df, lows, atr_multiplier=1.0)
    resistance_zones = build_zones(df, highs, atr_multiplier=1.0)

    last = df.iloc[-1]
    prev = df.iloc[-2]

    score = 0
    reasons = []

    # اتجاه EMA
    if last['ema_fast'] > last['ema_slow']:
        score += 1
        reasons.append("EMA up")
    else:
        score -= 1
        reasons.append("EMA down")

    # شمعة قوة
    if last['close'] > last['open'] and last['close'] > prev['close']:
        score += 1
        reasons.append("Bullish candle")
    elif last['close'] < last['open'] and last['close'] < prev['close']:
        score -= 1
        reasons.append("Bearish candle")

    # RSI
    if 35 < last['rsi'] < 72:
        score += 1
        reasons.append("RSI ok")
    elif last['rsi'] > 80:
        score -= 1
        reasons.append("RSI overbought")
    elif last['rsi'] < 20:
        score -= 1
        reasons.append("RSI oversold")

    # ADX قوة اتجاه
    if last['adx'] > 18:
        score += 1
        reasons.append("ADX strong")

    # قرب مناطق S/R
    if price_near_zone(last['close'], support_zones):
        score += 1
        reasons.append("Near support")
    if price_near_zone(last['close'], resistance_zones):
        score -= 1
        reasons.append("Near resistance")

    # القرار
    if score >= SCORE_THRESHOLD:
        return "BUY", score, reasons
    if score <= -SCORE_THRESHOLD:
        return "SELL", score, reasons
    return "WAIT", score, reasons
