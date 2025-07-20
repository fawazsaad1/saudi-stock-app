from flask import Blueprint, jsonify, request
from src.models.stock import db, Stock, StockPrice, TechnicalIndicator
from datetime import datetime, date, timedelta
import requests
import json

stock_bp = Blueprint('stock', __name__)

# قائمة الأسهم السعودية الرئيسية
SAUDI_STOCKS = [
    {'symbol': '2222', 'name': 'أرامكو السعودية', 'sector': 'الطاقة'},
    {'symbol': '1120', 'name': 'الراجحي', 'sector': 'البنوك'},
    {'symbol': '2030', 'name': 'سابك', 'sector': 'البتروكيماويات'},
    {'symbol': '1180', 'name': 'الأهلي السعودي', 'sector': 'البنوك'},
    {'symbol': '1211', 'name': 'معادن', 'sector': 'المواد الأساسية'},
    {'symbol': '7010', 'name': 'الاتصالات السعودية', 'sector': 'الاتصالات'},
    {'symbol': '2380', 'name': 'بترو رابغ', 'sector': 'البتروكيماويات'},
    {'symbol': '1140', 'name': 'البنك الأهلي التجاري', 'sector': 'البنوك'},
    {'symbol': '2010', 'name': 'سابك للمغذيات الزراعية', 'sector': 'البتروكيماويات'},
    {'symbol': '4030', 'name': 'الخليج للتدريب', 'sector': 'التعليم'},
]

@stock_bp.route('/stocks', methods=['GET'])
def get_stocks():
    """الحصول على قائمة الأسهم"""
    try:
        stocks = Stock.query.all()
        return jsonify({
            'success': True,
            'data': [stock.to_dict() for stock in stocks],
            'count': len(stocks)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@stock_bp.route('/stocks/init', methods=['POST'])
def init_stocks():
    """تهيئة قاعدة البيانات بالأسهم السعودية الرئيسية"""
    try:
        for stock_data in SAUDI_STOCKS:
            existing_stock = Stock.query.filter_by(symbol=stock_data['symbol']).first()
            if not existing_stock:
                stock = Stock(
                    symbol=stock_data['symbol'],
                    name=stock_data['name'],
                    sector=stock_data['sector']
                )
                db.session.add(stock)
        
        db.session.commit()
        return jsonify({
            'success': True,
            'message': 'تم تهيئة قاعدة البيانات بنجاح'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@stock_bp.route('/stocks/<symbol>/price', methods=['GET'])
def get_stock_price(symbol):
    """الحصول على سعر السهم الحالي"""
    try:
        stock = Stock.query.filter_by(symbol=symbol).first()
        if not stock:
            return jsonify({
                'success': False,
                'error': 'السهم غير موجود'
            }), 404
        
        # محاولة جلب البيانات من مصادر مختلفة
        price_data = fetch_stock_price_from_api(symbol)
        
        if price_data:
            return jsonify({
                'success': True,
                'data': price_data
            })
        else:
            # إرجاع بيانات تجريبية إذا فشل جلب البيانات الحقيقية
            mock_data = generate_mock_price_data(symbol)
            return jsonify({
                'success': True,
                'data': mock_data,
                'note': 'بيانات تجريبية - لأغراض التطوير'
            })
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@stock_bp.route('/stocks/<symbol>/history', methods=['GET'])
def get_stock_history(symbol):
    """الحصول على البيانات التاريخية للسهم"""
    try:
        days = request.args.get('days', 30, type=int)
        stock = Stock.query.filter_by(symbol=symbol).first()
        
        if not stock:
            return jsonify({
                'success': False,
                'error': 'السهم غير موجود'
            }), 404
        
        # جلب البيانات التاريخية من قاعدة البيانات
        end_date = date.today()
        start_date = end_date - timedelta(days=days)
        
        prices = StockPrice.query.filter(
            StockPrice.stock_id == stock.id,
            StockPrice.date >= start_date,
            StockPrice.date <= end_date
        ).order_by(StockPrice.date.desc()).all()
        
        if not prices:
            # إنشاء بيانات تجريبية إذا لم توجد بيانات
            mock_history = generate_mock_history_data(symbol, days)
            return jsonify({
                'success': True,
                'data': mock_history,
                'note': 'بيانات تجريبية - لأغراض التطوير'
            })
        
        return jsonify({
            'success': True,
            'data': [price.to_dict() for price in prices]
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

def fetch_stock_price_from_api(symbol):
    """جلب سعر السهم من API خارجي"""
    try:
        # محاولة استخدام Twelve Data API
        api_key = "demo"  # يجب استبدالها بمفتاح حقيقي
        url = f"https://api.twelvedata.com/price?symbol={symbol}:Tadawul&apikey={api_key}"
        
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if 'price' in data:
                return {
                    'symbol': symbol,
                    'price': float(data['price']),
                    'timestamp': datetime.now().isoformat(),
                    'source': 'Twelve Data'
                }
    except Exception as e:
        print(f"خطأ في جلب البيانات من API: {e}")
    
    return None

def generate_mock_price_data(symbol):
    """إنشاء بيانات سعر تجريبية"""
    import random
    
    base_prices = {
        '2222': 35.50,  # أرامكو
        '1120': 85.20,  # الراجحي
        '2030': 95.80,  # سابك
        '1180': 42.30,  # الأهلي
        '1211': 65.40,  # معادن
    }
    
    base_price = base_prices.get(symbol, 50.0)
    change_percent = random.uniform(-3, 3)
    current_price = base_price * (1 + change_percent / 100)
    
    return {
        'symbol': symbol,
        'price': round(current_price, 2),
        'change': round(current_price - base_price, 2),
        'change_percent': round(change_percent, 2),
        'timestamp': datetime.now().isoformat(),
        'source': 'Mock Data'
    }

def generate_mock_history_data(symbol, days):
    """إنشاء بيانات تاريخية تجريبية"""
    import random
    
    base_price = 50.0
    history = []
    
    for i in range(days):
        date_obj = date.today() - timedelta(days=i)
        
        # تغيير عشوائي في السعر
        change = random.uniform(-2, 2)
        base_price = max(base_price + change, 10)  # منع السعر من أن يصبح سالباً
        
        high = base_price + random.uniform(0, 2)
        low = base_price - random.uniform(0, 2)
        volume = random.randint(100000, 1000000)
        
        history.append({
            'date': date_obj.isoformat(),
            'open': round(base_price, 2),
            'high': round(high, 2),
            'low': round(low, 2),
            'close': round(base_price, 2),
            'volume': volume
        })
    
    return history[::-1]  # ترتيب تصاعدي حسب التاريخ

@stock_bp.route('/market/summary', methods=['GET'])
def get_market_summary():
    """الحصول على ملخص السوق"""
    try:
        # بيانات تجريبية لملخص السوق
        summary = {
            'tasi_index': {
                'value': 11276.91,
                'change': -32.45,
                'change_percent': -0.29
            },
            'market_cap': 2850000000000,  # 2.85 تريليون ريال
            'volume': 156789000,
            'trades': 45678,
            'advancing': 89,
            'declining': 134,
            'unchanged': 23,
            'timestamp': datetime.now().isoformat()
        }
        
        return jsonify({
            'success': True,
            'data': summary
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

