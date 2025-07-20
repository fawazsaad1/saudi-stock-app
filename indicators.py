from flask import Blueprint, jsonify, request
from src.models.stock import db, Stock, StockPrice, TechnicalIndicator
from src.utils.technical_indicators import TechnicalIndicators, create_sample_data
import pandas as pd
from datetime import datetime, date, timedelta

indicators_bp = Blueprint('indicators', __name__)

@indicators_bp.route('/indicators/<symbol>', methods=['GET'])
def get_stock_indicators(symbol):
    """الحصول على المؤشرات التقنية لسهم معين"""
    try:
        # الحصول على معلومات السهم
        stock = Stock.query.filter_by(symbol=symbol).first()
        if not stock:
            return jsonify({
                'success': False,
                'error': 'السهم غير موجود'
            }), 404
        
        # الحصول على عدد الأيام المطلوبة
        days = request.args.get('days', 100, type=int)
        
        # جلب البيانات التاريخية
        end_date = date.today()
        start_date = end_date - timedelta(days=days)
        
        prices = StockPrice.query.filter(
            StockPrice.stock_id == stock.id,
            StockPrice.date >= start_date,
            StockPrice.date <= end_date
        ).order_by(StockPrice.date.asc()).all()
        
        # إذا لم توجد بيانات، استخدم بيانات تجريبية
        if not prices:
            df = create_sample_data(symbol, days)
        else:
            # تحويل البيانات إلى DataFrame
            data = []
            for price in prices:
                data.append({
                    'date': price.date.strftime('%Y-%m-%d'),
                    'open': price.open_price,
                    'high': price.high_price,
                    'low': price.low_price,
                    'close': price.close_price,
                    'volume': price.volume
                })
            df = pd.DataFrame(data)
        
        # حساب المؤشرات التقنية
        tech_indicators = TechnicalIndicators(df)
        indicators = tech_indicators.calculate_all_indicators()
        signals = tech_indicators.get_latest_signals()
        
        return jsonify({
            'success': True,
            'data': {
                'symbol': symbol,
                'indicators': indicators,
                'signals': signals,
                'data_points': len(df),
                'period': f'{days} أيام'
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@indicators_bp.route('/indicators/<symbol>/signals', methods=['GET'])
def get_trading_signals(symbol):
    """الحصول على إشارات التداول للسهم"""
    try:
        stock = Stock.query.filter_by(symbol=symbol).first()
        if not stock:
            return jsonify({
                'success': False,
                'error': 'السهم غير موجود'
            }), 404
        
        # استخدام بيانات تجريبية للإشارات
        df = create_sample_data(symbol, 100)
        tech_indicators = TechnicalIndicators(df)
        signals = tech_indicators.get_latest_signals()
        
        # تحليل شامل للإشارات
        analysis = analyze_signals(signals)
        
        return jsonify({
            'success': True,
            'data': {
                'symbol': symbol,
                'signals': signals,
                'analysis': analysis,
                'timestamp': datetime.now().isoformat()
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@indicators_bp.route('/indicators/popular', methods=['GET'])
def get_popular_indicators():
    """الحصول على قائمة المؤشرات التقنية الشائعة"""
    try:
        popular_indicators = {
            'trend_indicators': [
                {
                    'name': 'المتوسط المتحرك البسيط',
                    'code': 'SMA',
                    'description': 'يحسب متوسط الأسعار خلال فترة زمنية محددة',
                    'periods': [5, 10, 20, 50, 200],
                    'usage': 'تحديد الاتجاه العام للسعر'
                },
                {
                    'name': 'المتوسط المتحرك الأسي',
                    'code': 'EMA',
                    'description': 'يعطي وزناً أكبر للأسعار الحديثة',
                    'periods': [12, 26, 50],
                    'usage': 'أكثر حساسية للتغيرات السعرية'
                },
                {
                    'name': 'MACD',
                    'code': 'MACD',
                    'description': 'مؤشر تقارب وتباعد المتوسطات المتحركة',
                    'parameters': {'fast': 12, 'slow': 26, 'signal': 9},
                    'usage': 'تحديد نقاط الدخول والخروج'
                }
            ],
            'momentum_indicators': [
                {
                    'name': 'مؤشر القوة النسبية',
                    'code': 'RSI',
                    'description': 'يقيس قوة حركة السعر',
                    'range': '0-100',
                    'overbought': 70,
                    'oversold': 30,
                    'usage': 'تحديد مناطق ذروة الشراء والبيع'
                },
                {
                    'name': 'الستوكاستك',
                    'code': 'Stochastic',
                    'description': 'يقارن سعر الإغلاق بنطاق الأسعار',
                    'parameters': {'k_period': 14, 'd_period': 3},
                    'usage': 'تحديد نقاط التحول في السعر'
                }
            ],
            'volatility_indicators': [
                {
                    'name': 'نطاقات بولينجر',
                    'code': 'BB',
                    'description': 'نطاقات حول المتوسط المتحرك',
                    'parameters': {'period': 20, 'std_dev': 2},
                    'usage': 'تحديد مستويات الدعم والمقاومة الديناميكية'
                },
                {
                    'name': 'متوسط المدى الحقيقي',
                    'code': 'ATR',
                    'description': 'يقيس تقلبات السعر',
                    'period': 14,
                    'usage': 'تحديد مستويات وقف الخسارة'
                }
            ],
            'volume_indicators': [
                {
                    'name': 'مؤشر التوازن الحجمي',
                    'code': 'OBV',
                    'description': 'يربط بين الحجم واتجاه السعر',
                    'usage': 'تأكيد الاتجاهات السعرية'
                },
                {
                    'name': 'متوسط حجم التداول',
                    'code': 'Volume_SMA',
                    'description': 'متوسط حجم التداول خلال فترة',
                    'period': 20,
                    'usage': 'تحديد قوة الحركة السعرية'
                }
            ]
        }
        
        return jsonify({
            'success': True,
            'data': popular_indicators
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@indicators_bp.route('/indicators/<symbol>/specific', methods=['POST'])
def calculate_specific_indicator(symbol):
    """حساب مؤشر تقني محدد"""
    try:
        data = request.get_json()
        indicator_type = data.get('indicator')
        parameters = data.get('parameters', {})
        
        stock = Stock.query.filter_by(symbol=symbol).first()
        if not stock:
            return jsonify({
                'success': False,
                'error': 'السهم غير موجود'
            }), 404
        
        # استخدام بيانات تجريبية
        df = create_sample_data(symbol, 100)
        tech_indicators = TechnicalIndicators(df)
        
        result = {}
        
        if indicator_type == 'SMA':
            period = parameters.get('period', 20)
            from ta.trend import SMAIndicator
            sma = SMAIndicator(close=df['close'], window=period)
            result = {
                'indicator': 'SMA',
                'period': period,
                'values': sma.sma_indicator().tolist()
            }
        
        elif indicator_type == 'RSI':
            period = parameters.get('period', 14)
            result = tech_indicators.calculate_rsi(period)
            result['indicator'] = 'RSI'
            result['period'] = period
        
        elif indicator_type == 'MACD':
            result = tech_indicators.calculate_macd()
            result['indicator'] = 'MACD'
        
        elif indicator_type == 'BB':
            period = parameters.get('period', 20)
            std_dev = parameters.get('std_dev', 2)
            result = tech_indicators.calculate_bollinger_bands(period, std_dev)
            result['indicator'] = 'Bollinger Bands'
            result['period'] = period
            result['std_dev'] = std_dev
        
        else:
            return jsonify({
                'success': False,
                'error': 'مؤشر غير مدعوم'
            }), 400
        
        return jsonify({
            'success': True,
            'data': result
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

def analyze_signals(signals):
    """تحليل الإشارات وإعطاء توصية شاملة"""
    if not signals:
        return {
            'recommendation': 'غير محدد',
            'confidence': 0,
            'reasons': ['لا توجد إشارات كافية']
        }
    
    buy_signals = 0
    sell_signals = 0
    neutral_signals = 0
    reasons = []
    
    # تحليل إشارات RSI
    if 'RSI_Signal' in signals:
        if signals['RSI_Signal'] == 'ذروة بيع':
            buy_signals += 1
            reasons.append(f"RSI في منطقة ذروة البيع ({signals.get('RSI_Value', 'N/A')})")
        elif signals['RSI_Signal'] == 'ذروة شراء':
            sell_signals += 1
            reasons.append(f"RSI في منطقة ذروة الشراء ({signals.get('RSI_Value', 'N/A')})")
        else:
            neutral_signals += 1
    
    # تحليل إشارات MACD
    if 'MACD_Signal' in signals:
        if signals['MACD_Signal'] == 'إشارة شراء':
            buy_signals += 1
            reasons.append("MACD يعطي إشارة شراء")
        elif signals['MACD_Signal'] == 'إشارة بيع':
            sell_signals += 1
            reasons.append("MACD يعطي إشارة بيع")
        else:
            neutral_signals += 1
    
    # تحليل إشارات المتوسطات المتحركة
    if 'MA_Signal' in signals:
        if signals['MA_Signal'] == 'اتجاه صاعد':
            buy_signals += 1
            reasons.append("الاتجاه العام صاعد")
        elif signals['MA_Signal'] == 'اتجاه هابط':
            sell_signals += 1
            reasons.append("الاتجاه العام هابط")
        else:
            neutral_signals += 1
    
    # تحليل إشارات نطاقات بولينجر
    if 'BB_Signal' in signals:
        if signals['BB_Signal'] == 'ذروة بيع':
            buy_signals += 1
            reasons.append("السعر عند الحد السفلي لنطاقات بولينجر")
        elif signals['BB_Signal'] == 'ذروة شراء':
            sell_signals += 1
            reasons.append("السعر عند الحد العلوي لنطاقات بولينجر")
        else:
            neutral_signals += 1
    
    # تحديد التوصية النهائية
    total_signals = buy_signals + sell_signals + neutral_signals
    
    if total_signals == 0:
        recommendation = 'غير محدد'
        confidence = 0
    elif buy_signals > sell_signals:
        recommendation = 'شراء'
        confidence = (buy_signals / total_signals) * 100
    elif sell_signals > buy_signals:
        recommendation = 'بيع'
        confidence = (sell_signals / total_signals) * 100
    else:
        recommendation = 'انتظار'
        confidence = 50
    
    return {
        'recommendation': recommendation,
        'confidence': round(confidence, 1),
        'buy_signals': buy_signals,
        'sell_signals': sell_signals,
        'neutral_signals': neutral_signals,
        'reasons': reasons
    }

