import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from src.utils.technical_indicators import TechnicalIndicators

class TradingStrategies:
    """فئة لتطبيق استراتيجيات التداول المختلفة"""
    
    def __init__(self, data):
        """
        تهيئة استراتيجيات التداول
        data: DataFrame يحتوي على بيانات الأسعار التاريخية
        """
        self.data = data.copy()
        self.indicators = TechnicalIndicators(data)
        self.signals = []
        self.performance = {}
    
    def moving_average_crossover_strategy(self, short_period=20, long_period=50):
        """
        استراتيجية تقاطع المتوسطات المتحركة
        """
        try:
            if len(self.data) < long_period:
                return {
                    'success': False,
                    'error': f'البيانات غير كافية. مطلوب على الأقل {long_period} نقطة بيانات'
                }
            
            # حساب المتوسطات المتحركة
            ma_data = self.indicators.calculate_moving_averages()
            
            if f'SMA_{short_period}' not in ma_data or f'SMA_{long_period}' not in ma_data:
                return {
                    'success': False,
                    'error': 'فشل في حساب المتوسطات المتحركة'
                }
            
            short_ma = ma_data[f'SMA_{short_period}']
            long_ma = ma_data[f'SMA_{long_period}']
            
            signals = []
            positions = []
            current_position = None
            
            for i in range(1, len(short_ma)):
                if short_ma[i] is None or long_ma[i] is None:
                    continue
                    
                # إشارة شراء: تقاطع المتوسط القصير فوق الطويل
                if (short_ma[i-1] <= long_ma[i-1] and short_ma[i] > long_ma[i] and 
                    current_position != 'long'):
                    signals.append({
                        'date': self.data.iloc[i]['date'] if 'date' in self.data.columns else i,
                        'type': 'شراء',
                        'price': self.data.iloc[i]['close'],
                        'short_ma': short_ma[i],
                        'long_ma': long_ma[i],
                        'confidence': self.calculate_signal_confidence(short_ma[i], long_ma[i], 'buy')
                    })
                    current_position = 'long'
                
                # إشارة بيع: تقاطع المتوسط القصير تحت الطويل
                elif (short_ma[i-1] >= long_ma[i-1] and short_ma[i] < long_ma[i] and 
                      current_position != 'short'):
                    signals.append({
                        'date': self.data.iloc[i]['date'] if 'date' in self.data.columns else i,
                        'type': 'بيع',
                        'price': self.data.iloc[i]['close'],
                        'short_ma': short_ma[i],
                        'long_ma': long_ma[i],
                        'confidence': self.calculate_signal_confidence(short_ma[i], long_ma[i], 'sell')
                    })
                    current_position = 'short'
            
            # حساب الأداء
            performance = self.calculate_strategy_performance(signals)
            
            return {
                'success': True,
                'strategy_name': f'تقاطع المتوسطات المتحركة ({short_period}/{long_period})',
                'signals': signals,
                'performance': performance,
                'parameters': {
                    'short_period': short_period,
                    'long_period': long_period
                }
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'خطأ في تطبيق استراتيجية المتوسطات المتحركة: {str(e)}'
            }
    
    def rsi_strategy(self, period=14, oversold=30, overbought=70):
        """
        استراتيجية مؤشر القوة النسبية RSI
        """
        try:
            if len(self.data) < period + 10:
                return {
                    'success': False,
                    'error': f'البيانات غير كافية. مطلوب على الأقل {period + 10} نقطة بيانات'
                }
            
            # حساب RSI
            rsi_data = self.indicators.calculate_rsi(period)
            
            if f'RSI_{period}' not in rsi_data:
                return {
                    'success': False,
                    'error': 'فشل في حساب مؤشر RSI'
                }
            
            rsi_values = rsi_data[f'RSI_{period}']
            signals = []
            current_position = None
            
            for i in range(1, len(rsi_values)):
                if rsi_values[i] is None:
                    continue
                
                # إشارة شراء: RSI يخرج من منطقة ذروة البيع
                if (rsi_values[i-1] <= oversold and rsi_values[i] > oversold and 
                    current_position != 'long'):
                    signals.append({
                        'date': self.data.iloc[i]['date'] if 'date' in self.data.columns else i,
                        'type': 'شراء',
                        'price': self.data.iloc[i]['close'],
                        'rsi': rsi_values[i],
                        'confidence': self.calculate_rsi_confidence(rsi_values[i], 'buy')
                    })
                    current_position = 'long'
                
                # إشارة بيع: RSI يدخل منطقة ذروة الشراء
                elif (rsi_values[i-1] < overbought and rsi_values[i] >= overbought and 
                      current_position != 'short'):
                    signals.append({
                        'date': self.data.iloc[i]['date'] if 'date' in self.data.columns else i,
                        'type': 'بيع',
                        'price': self.data.iloc[i]['close'],
                        'rsi': rsi_values[i],
                        'confidence': self.calculate_rsi_confidence(rsi_values[i], 'sell')
                    })
                    current_position = 'short'
            
            # حساب الأداء
            performance = self.calculate_strategy_performance(signals)
            
            return {
                'success': True,
                'strategy_name': f'استراتيجية RSI ({period})',
                'signals': signals,
                'performance': performance,
                'parameters': {
                    'period': period,
                    'oversold': oversold,
                    'overbought': overbought
                }
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'خطأ في تطبيق استراتيجية RSI: {str(e)}'
            }
    
    def macd_strategy(self):
        """
        استراتيجية MACD
        """
        try:
            if len(self.data) < 50:
                return {
                    'success': False,
                    'error': 'البيانات غير كافية. مطلوب على الأقل 50 نقطة بيانات'
                }
            
            # حساب MACD
            macd_data = self.indicators.calculate_macd()
            
            if 'MACD' not in macd_data or 'MACD_Signal' not in macd_data:
                return {
                    'success': False,
                    'error': 'فشل في حساب مؤشر MACD'
                }
            
            macd_line = macd_data['MACD']
            signal_line = macd_data['MACD_Signal']
            histogram = macd_data['MACD_Histogram']
            
            signals = []
            current_position = None
            
            for i in range(1, len(macd_line)):
                if (macd_line[i] is None or signal_line[i] is None or 
                    macd_line[i-1] is None or signal_line[i-1] is None):
                    continue
                
                # إشارة شراء: تقاطع MACD فوق خط الإشارة
                if (macd_line[i-1] <= signal_line[i-1] and macd_line[i] > signal_line[i] and 
                    current_position != 'long'):
                    signals.append({
                        'date': self.data.iloc[i]['date'] if 'date' in self.data.columns else i,
                        'type': 'شراء',
                        'price': self.data.iloc[i]['close'],
                        'macd': macd_line[i],
                        'signal': signal_line[i],
                        'histogram': histogram[i] if i < len(histogram) else 0,
                        'confidence': self.calculate_macd_confidence(macd_line[i], signal_line[i], 'buy')
                    })
                    current_position = 'long'
                
                # إشارة بيع: تقاطع MACD تحت خط الإشارة
                elif (macd_line[i-1] >= signal_line[i-1] and macd_line[i] < signal_line[i] and 
                      current_position != 'short'):
                    signals.append({
                        'date': self.data.iloc[i]['date'] if 'date' in self.data.columns else i,
                        'type': 'بيع',
                        'price': self.data.iloc[i]['close'],
                        'macd': macd_line[i],
                        'signal': signal_line[i],
                        'histogram': histogram[i] if i < len(histogram) else 0,
                        'confidence': self.calculate_macd_confidence(macd_line[i], signal_line[i], 'sell')
                    })
                    current_position = 'short'
            
            # حساب الأداء
            performance = self.calculate_strategy_performance(signals)
            
            return {
                'success': True,
                'strategy_name': 'استراتيجية MACD',
                'signals': signals,
                'performance': performance,
                'parameters': {
                    'fast_period': 12,
                    'slow_period': 26,
                    'signal_period': 9
                }
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'خطأ في تطبيق استراتيجية MACD: {str(e)}'
            }
    
    def bollinger_bands_strategy(self, period=20, std_dev=2):
        """
        استراتيجية نطاقات بولينجر
        """
        try:
            if len(self.data) < period + 10:
                return {
                    'success': False,
                    'error': f'البيانات غير كافية. مطلوب على الأقل {period + 10} نقطة بيانات'
                }
            
            # حساب نطاقات بولينجر
            bb_data = self.indicators.calculate_bollinger_bands(period, std_dev)
            
            if 'BB_Upper' not in bb_data or 'BB_Lower' not in bb_data:
                return {
                    'success': False,
                    'error': 'فشل في حساب نطاقات بولينجر'
                }
            
            upper_band = bb_data['BB_Upper']
            lower_band = bb_data['BB_Lower']
            middle_band = bb_data['BB_Middle']
            
            signals = []
            current_position = None
            
            for i in range(len(self.data)):
                if (i >= len(upper_band) or upper_band[i] is None or 
                    lower_band[i] is None or middle_band[i] is None):
                    continue
                
                current_price = self.data.iloc[i]['close']
                
                # إشارة شراء: السعر يلامس الحد السفلي
                if (current_price <= lower_band[i] and current_position != 'long'):
                    signals.append({
                        'date': self.data.iloc[i]['date'] if 'date' in self.data.columns else i,
                        'type': 'شراء',
                        'price': current_price,
                        'upper_band': upper_band[i],
                        'lower_band': lower_band[i],
                        'middle_band': middle_band[i],
                        'confidence': self.calculate_bb_confidence(current_price, lower_band[i], middle_band[i], 'buy')
                    })
                    current_position = 'long'
                
                # إشارة بيع: السعر يلامس الحد العلوي
                elif (current_price >= upper_band[i] and current_position != 'short'):
                    signals.append({
                        'date': self.data.iloc[i]['date'] if 'date' in self.data.columns else i,
                        'type': 'بيع',
                        'price': current_price,
                        'upper_band': upper_band[i],
                        'lower_band': lower_band[i],
                        'middle_band': middle_band[i],
                        'confidence': self.calculate_bb_confidence(current_price, upper_band[i], middle_band[i], 'sell')
                    })
                    current_position = 'short'
            
            # حساب الأداء
            performance = self.calculate_strategy_performance(signals)
            
            return {
                'success': True,
                'strategy_name': f'استراتيجية نطاقات بولينجر ({period}, {std_dev})',
                'signals': signals,
                'performance': performance,
                'parameters': {
                    'period': period,
                    'std_dev': std_dev
                }
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'خطأ في تطبيق استراتيجية نطاقات بولينجر: {str(e)}'
            }
    
    def combined_strategy(self):
        """
        استراتيجية مدمجة تجمع عدة مؤشرات
        """
        try:
            # تطبيق الاستراتيجيات الفردية
            ma_result = self.moving_average_crossover_strategy()
            rsi_result = self.rsi_strategy()
            macd_result = self.macd_strategy()
            
            if not all([ma_result['success'], rsi_result['success'], macd_result['success']]):
                return {
                    'success': False,
                    'error': 'فشل في تطبيق إحدى الاستراتيجيات الفرعية'
                }
            
            # دمج الإشارات
            combined_signals = []
            all_dates = set()
            
            # جمع جميع التواريخ
            for result in [ma_result, rsi_result, macd_result]:
                for signal in result['signals']:
                    all_dates.add(signal['date'])
            
            # تحليل كل تاريخ
            for date in sorted(all_dates):
                ma_signal = self.get_signal_for_date(ma_result['signals'], date)
                rsi_signal = self.get_signal_for_date(rsi_result['signals'], date)
                macd_signal = self.get_signal_for_date(macd_result['signals'], date)
                
                # حساب النقاط لكل نوع إشارة
                buy_score = 0
                sell_score = 0
                
                if ma_signal and ma_signal['type'] == 'شراء':
                    buy_score += ma_signal['confidence']
                elif ma_signal and ma_signal['type'] == 'بيع':
                    sell_score += ma_signal['confidence']
                
                if rsi_signal and rsi_signal['type'] == 'شراء':
                    buy_score += rsi_signal['confidence']
                elif rsi_signal and rsi_signal['type'] == 'بيع':
                    sell_score += rsi_signal['confidence']
                
                if macd_signal and macd_signal['type'] == 'شراء':
                    buy_score += macd_signal['confidence']
                elif macd_signal and macd_signal['type'] == 'بيع':
                    sell_score += macd_signal['confidence']
                
                # تحديد الإشارة النهائية
                if buy_score > sell_score and buy_score > 150:  # عتبة للثقة
                    signal_type = 'شراء قوي'
                    confidence = min(buy_score / 3, 100)
                elif sell_score > buy_score and sell_score > 150:
                    signal_type = 'بيع قوي'
                    confidence = min(sell_score / 3, 100)
                elif buy_score > sell_score:
                    signal_type = 'شراء'
                    confidence = min(buy_score / 3, 100)
                elif sell_score > buy_score:
                    signal_type = 'بيع'
                    confidence = min(sell_score / 3, 100)
                else:
                    signal_type = 'محايد'
                    confidence = 50
                
                # إضافة الإشارة المدمجة
                if signal_type != 'محايد':
                    price = (ma_signal or rsi_signal or macd_signal)['price']
                    combined_signals.append({
                        'date': date,
                        'type': signal_type,
                        'price': price,
                        'confidence': confidence,
                        'supporting_signals': {
                            'ma': ma_signal['type'] if ma_signal else None,
                            'rsi': rsi_signal['type'] if rsi_signal else None,
                            'macd': macd_signal['type'] if macd_signal else None
                        }
                    })
            
            # حساب الأداء
            performance = self.calculate_strategy_performance(combined_signals)
            
            return {
                'success': True,
                'strategy_name': 'الاستراتيجية المدمجة',
                'signals': combined_signals,
                'performance': performance,
                'individual_results': {
                    'moving_average': ma_result,
                    'rsi': rsi_result,
                    'macd': macd_result
                }
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'خطأ في تطبيق الاستراتيجية المدمجة: {str(e)}'
            }
    
    def get_signal_for_date(self, signals, target_date):
        """البحث عن إشارة في تاريخ محدد"""
        for signal in signals:
            if signal['date'] == target_date:
                return signal
        return None
    
    def calculate_signal_confidence(self, short_ma, long_ma, signal_type):
        """حساب مستوى الثقة لإشارة المتوسطات المتحركة"""
        if signal_type == 'buy':
            # كلما زاد الفرق بين المتوسطين، زادت الثقة
            diff_percent = ((short_ma - long_ma) / long_ma) * 100
            return min(50 + abs(diff_percent) * 10, 100)
        else:
            diff_percent = ((long_ma - short_ma) / short_ma) * 100
            return min(50 + abs(diff_percent) * 10, 100)
    
    def calculate_rsi_confidence(self, rsi_value, signal_type):
        """حساب مستوى الثقة لإشارة RSI"""
        if signal_type == 'buy':
            # كلما قل RSI عن 30، زادت الثقة
            return min(100, 100 - rsi_value * 2)
        else:
            # كلما زاد RSI عن 70، زادت الثقة
            return min(100, (rsi_value - 50) * 2)
    
    def calculate_macd_confidence(self, macd, signal, signal_type):
        """حساب مستوى الثقة لإشارة MACD"""
        diff = abs(macd - signal)
        return min(50 + diff * 100, 100)
    
    def calculate_bb_confidence(self, price, band, middle, signal_type):
        """حساب مستوى الثقة لإشارة نطاقات بولينجر"""
        if signal_type == 'buy':
            # كلما اقترب السعر من الحد السفلي، زادت الثقة
            distance_percent = abs((price - band) / middle) * 100
        else:
            # كلما اقترب السعر من الحد العلوي، زادت الثقة
            distance_percent = abs((band - price) / middle) * 100
        
        return min(50 + distance_percent * 20, 100)
    
    def calculate_strategy_performance(self, signals):
        """حساب أداء الاستراتيجية"""
        if not signals:
            return {
                'total_signals': 0,
                'profitable_signals': 0,
                'success_rate': 0,
                'total_return': 0,
                'average_return_per_trade': 0
            }
        
        total_signals = len(signals)
        profitable_signals = 0
        total_return = 0
        
        # محاكاة التداول
        position = None
        entry_price = 0
        
        for signal in signals:
            if signal['type'] in ['شراء', 'شراء قوي'] and position != 'long':
                if position == 'short':
                    # إغلاق صفقة بيع
                    trade_return = (entry_price - signal['price']) / entry_price
                    total_return += trade_return
                    if trade_return > 0:
                        profitable_signals += 1
                
                # فتح صفقة شراء
                position = 'long'
                entry_price = signal['price']
                
            elif signal['type'] in ['بيع', 'بيع قوي'] and position != 'short':
                if position == 'long':
                    # إغلاق صفقة شراء
                    trade_return = (signal['price'] - entry_price) / entry_price
                    total_return += trade_return
                    if trade_return > 0:
                        profitable_signals += 1
                
                # فتح صفقة بيع
                position = 'short'
                entry_price = signal['price']
        
        # إغلاق آخر صفقة إذا كانت مفتوحة
        if position and len(self.data) > 0:
            last_price = self.data.iloc[-1]['close']
            if position == 'long':
                trade_return = (last_price - entry_price) / entry_price
            else:
                trade_return = (entry_price - last_price) / entry_price
            
            total_return += trade_return
            if trade_return > 0:
                profitable_signals += 1
        
        success_rate = (profitable_signals / max(total_signals, 1)) * 100
        average_return = (total_return / max(total_signals, 1)) * 100
        
        return {
            'total_signals': total_signals,
            'profitable_signals': profitable_signals,
            'success_rate': round(success_rate, 2),
            'total_return': round(total_return * 100, 2),
            'average_return_per_trade': round(average_return, 2)
        }
    
    def get_all_strategies(self):
        """الحصول على جميع الاستراتيجيات المتاحة"""
        return {
            'moving_average': {
                'name': 'تقاطع المتوسطات المتحركة',
                'description': 'استراتيجية تعتمد على تقاطع المتوسطات المتحركة قصيرة وطويلة المدى',
                'risk_level': 'متوسط',
                'timeframe': 'متوسط المدى',
                'parameters': ['short_period', 'long_period']
            },
            'rsi': {
                'name': 'مؤشر القوة النسبية',
                'description': 'استراتيجية تعتمد على مناطق ذروة الشراء والبيع في مؤشر RSI',
                'risk_level': 'منخفض',
                'timeframe': 'قصير المدى',
                'parameters': ['period', 'oversold', 'overbought']
            },
            'macd': {
                'name': 'MACD',
                'description': 'استراتيجية تعتمد على تقارب وتباعد المتوسطات المتحركة',
                'risk_level': 'عالي',
                'timeframe': 'متوسط المدى',
                'parameters': ['fast_period', 'slow_period', 'signal_period']
            },
            'bollinger_bands': {
                'name': 'نطاقات بولينجر',
                'description': 'استراتيجية تعتمد على النطاقات الديناميكية حول المتوسط المتحرك',
                'risk_level': 'متوسط',
                'timeframe': 'قصير إلى متوسط المدى',
                'parameters': ['period', 'std_dev']
            },
            'combined': {
                'name': 'الاستراتيجية المدمجة',
                'description': 'استراتيجية تجمع عدة مؤشرات لإعطاء إشارات أكثر دقة',
                'risk_level': 'متوسط',
                'timeframe': 'متوسط المدى',
                'parameters': []
            }
        }

