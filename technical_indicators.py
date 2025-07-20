import pandas as pd
import numpy as np
from ta import add_all_ta_features
from ta.trend import MACD, EMAIndicator, SMAIndicator
from ta.momentum import RSIIndicator, StochasticOscillator
from ta.volatility import BollingerBands, AverageTrueRange
from ta.volume import OnBalanceVolumeIndicator
from ta.others import DailyReturnIndicator

class TechnicalIndicators:
    """فئة لحساب المؤشرات التقنية المختلفة"""
    
    def __init__(self, data):
        """
        تهيئة المؤشرات التقنية
        data: DataFrame يحتوي على أعمدة: open, high, low, close, volume
        """
        self.data = data.copy()
        self.prepare_data()
    
    def prepare_data(self):
        """تحضير البيانات للحساب"""
        # التأكد من وجود الأعمدة المطلوبة
        required_columns = ['open', 'high', 'low', 'close', 'volume']
        for col in required_columns:
            if col not in self.data.columns:
                raise ValueError(f"العمود {col} مطلوب في البيانات")
        
        # تحويل البيانات إلى أرقام
        for col in required_columns:
            self.data[col] = pd.to_numeric(self.data[col], errors='coerce')
        
        # إزالة الصفوف التي تحتوي على قيم فارغة
        self.data = self.data.dropna()
    
    def calculate_moving_averages(self):
        """حساب المتوسطات المتحركة"""
        indicators = {}
        
        # المتوسط المتحرك البسيط
        sma_periods = [5, 10, 20, 50, 200]
        for period in sma_periods:
            if len(self.data) >= period:
                sma = SMAIndicator(close=self.data['close'], window=period)
                indicators[f'SMA_{period}'] = sma.sma_indicator().tolist()
        
        # المتوسط المتحرك الأسي
        ema_periods = [12, 26, 50]
        for period in ema_periods:
            if len(self.data) >= period:
                ema = EMAIndicator(close=self.data['close'], window=period)
                indicators[f'EMA_{period}'] = ema.ema_indicator().tolist()
        
        return indicators
    
    def calculate_macd(self):
        """حساب مؤشر MACD"""
        if len(self.data) < 26:
            return {}
        
        macd = MACD(close=self.data['close'])
        
        return {
            'MACD': macd.macd().tolist(),
            'MACD_Signal': macd.macd_signal().tolist(),
            'MACD_Histogram': macd.macd_diff().tolist()
        }
    
    def calculate_rsi(self, period=14):
        """حساب مؤشر القوة النسبية RSI"""
        if len(self.data) < period:
            return {}
        
        rsi = RSIIndicator(close=self.data['close'], window=period)
        
        return {
            f'RSI_{period}': rsi.rsi().tolist()
        }
    
    def calculate_bollinger_bands(self, period=20, std_dev=2):
        """حساب نطاقات بولينجر"""
        if len(self.data) < period:
            return {}
        
        bb = BollingerBands(close=self.data['close'], window=period, window_dev=std_dev)
        
        return {
            'BB_Upper': bb.bollinger_hband().tolist(),
            'BB_Middle': bb.bollinger_mavg().tolist(),
            'BB_Lower': bb.bollinger_lband().tolist(),
            'BB_Width': bb.bollinger_wband().tolist(),
            'BB_Percent': bb.bollinger_pband().tolist()
        }
    
    def calculate_stochastic(self, k_period=14, d_period=3):
        """حساب مؤشر الستوكاستك"""
        if len(self.data) < k_period:
            return {}
        
        stoch = StochasticOscillator(
            high=self.data['high'],
            low=self.data['low'],
            close=self.data['close'],
            window=k_period,
            smooth_window=d_period
        )
        
        return {
            'Stoch_K': stoch.stoch().tolist(),
            'Stoch_D': stoch.stoch_signal().tolist()
        }
    
    def calculate_atr(self, period=14):
        """حساب متوسط المدى الحقيقي ATR"""
        if len(self.data) < period:
            return {}
        
        atr = AverageTrueRange(
            high=self.data['high'],
            low=self.data['low'],
            close=self.data['close'],
            window=period
        )
        
        return {
            f'ATR_{period}': atr.average_true_range().tolist()
        }
    
    def calculate_volume_indicators(self):
        """حساب مؤشرات الحجم"""
        indicators = {}
        
        # متوسط حجم التداول (حساب يدوي)
        if len(self.data) >= 20:
            volume_sma = self.data['volume'].rolling(window=20).mean()
            indicators['Volume_SMA_20'] = volume_sma.tolist()
        
        # مؤشر التوازن الحجمي
        obv = OnBalanceVolumeIndicator(close=self.data['close'], volume=self.data['volume'])
        indicators['OBV'] = obv.on_balance_volume().tolist()
        
        return indicators
    
    def calculate_support_resistance(self):
        """حساب مستويات الدعم والمقاومة"""
        if len(self.data) < 20:
            return {}
        
        # حساب مستويات الدعم والمقاومة باستخدام النقاط المحورية
        high = self.data['high'].iloc[-1]
        low = self.data['low'].iloc[-1]
        close = self.data['close'].iloc[-1]
        
        pivot = (high + low + close) / 3
        
        # مستويات المقاومة
        r1 = 2 * pivot - low
        r2 = pivot + (high - low)
        r3 = high + 2 * (pivot - low)
        
        # مستويات الدعم
        s1 = 2 * pivot - high
        s2 = pivot - (high - low)
        s3 = low - 2 * (high - pivot)
        
        return {
            'Pivot': pivot,
            'Resistance_1': r1,
            'Resistance_2': r2,
            'Resistance_3': r3,
            'Support_1': s1,
            'Support_2': s2,
            'Support_3': s3
        }
    
    def calculate_all_indicators(self):
        """حساب جميع المؤشرات التقنية"""
        all_indicators = {}
        
        try:
            # المتوسطات المتحركة
            all_indicators.update(self.calculate_moving_averages())
            
            # MACD
            all_indicators.update(self.calculate_macd())
            
            # RSI
            all_indicators.update(self.calculate_rsi())
            
            # نطاقات بولينجر
            all_indicators.update(self.calculate_bollinger_bands())
            
            # الستوكاستك
            all_indicators.update(self.calculate_stochastic())
            
            # ATR
            all_indicators.update(self.calculate_atr())
            
            # مؤشرات الحجم
            all_indicators.update(self.calculate_volume_indicators())
            
            # مستويات الدعم والمقاومة
            all_indicators.update(self.calculate_support_resistance())
            
        except Exception as e:
            print(f"خطأ في حساب المؤشرات: {e}")
        
        return all_indicators
    
    def get_latest_signals(self):
        """الحصول على الإشارات الحالية"""
        if len(self.data) < 20:
            return {}
        
        signals = {}
        
        try:
            # إشارات RSI
            rsi_data = self.calculate_rsi()
            if 'RSI_14' in rsi_data and len(rsi_data['RSI_14']) > 0:
                latest_rsi = rsi_data['RSI_14'][-1]
                if latest_rsi > 70:
                    signals['RSI_Signal'] = 'ذروة شراء'
                elif latest_rsi < 30:
                    signals['RSI_Signal'] = 'ذروة بيع'
                else:
                    signals['RSI_Signal'] = 'محايد'
                signals['RSI_Value'] = latest_rsi
            
            # إشارات MACD
            macd_data = self.calculate_macd()
            if 'MACD' in macd_data and 'MACD_Signal' in macd_data:
                if len(macd_data['MACD']) > 1 and len(macd_data['MACD_Signal']) > 1:
                    macd_current = macd_data['MACD'][-1]
                    macd_signal_current = macd_data['MACD_Signal'][-1]
                    macd_prev = macd_data['MACD'][-2]
                    macd_signal_prev = macd_data['MACD_Signal'][-2]
                    
                    if macd_prev <= macd_signal_prev and macd_current > macd_signal_current:
                        signals['MACD_Signal'] = 'إشارة شراء'
                    elif macd_prev >= macd_signal_prev and macd_current < macd_signal_current:
                        signals['MACD_Signal'] = 'إشارة بيع'
                    else:
                        signals['MACD_Signal'] = 'محايد'
            
            # إشارات المتوسطات المتحركة
            ma_data = self.calculate_moving_averages()
            if 'SMA_20' in ma_data and 'SMA_50' in ma_data:
                if len(ma_data['SMA_20']) > 0 and len(ma_data['SMA_50']) > 0:
                    sma20 = ma_data['SMA_20'][-1]
                    sma50 = ma_data['SMA_50'][-1]
                    current_price = self.data['close'].iloc[-1]
                    
                    if current_price > sma20 > sma50:
                        signals['MA_Signal'] = 'اتجاه صاعد'
                    elif current_price < sma20 < sma50:
                        signals['MA_Signal'] = 'اتجاه هابط'
                    else:
                        signals['MA_Signal'] = 'محايد'
            
            # إشارات نطاقات بولينجر
            bb_data = self.calculate_bollinger_bands()
            if 'BB_Upper' in bb_data and 'BB_Lower' in bb_data:
                if len(bb_data['BB_Upper']) > 0 and len(bb_data['BB_Lower']) > 0:
                    current_price = self.data['close'].iloc[-1]
                    bb_upper = bb_data['BB_Upper'][-1]
                    bb_lower = bb_data['BB_Lower'][-1]
                    
                    if current_price >= bb_upper:
                        signals['BB_Signal'] = 'ذروة شراء'
                    elif current_price <= bb_lower:
                        signals['BB_Signal'] = 'ذروة بيع'
                    else:
                        signals['BB_Signal'] = 'محايد'
        
        except Exception as e:
            print(f"خطأ في حساب الإشارات: {e}")
        
        return signals

def create_sample_data(symbol, days=100):
    """إنشاء بيانات تجريبية للاختبار"""
    import random
    from datetime import datetime, timedelta
    
    dates = []
    data = []
    base_price = 50.0
    
    for i in range(days):
        date_obj = datetime.now() - timedelta(days=days-i)
        dates.append(date_obj.strftime('%Y-%m-%d'))
        
        # تغيير عشوائي في السعر
        change = random.uniform(-2, 2)
        base_price = max(base_price + change, 10)
        
        high = base_price + random.uniform(0, 2)
        low = base_price - random.uniform(0, 2)
        volume = random.randint(100000, 1000000)
        
        data.append({
            'date': date_obj.strftime('%Y-%m-%d'),
            'open': round(base_price, 2),
            'high': round(high, 2),
            'low': round(low, 2),
            'close': round(base_price, 2),
            'volume': volume
        })
    
    return pd.DataFrame(data)

