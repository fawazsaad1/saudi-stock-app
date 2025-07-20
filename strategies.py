from flask import Blueprint, jsonify, request
from src.models.stock import db, Stock, StockPrice
from src.utils.trading_strategies import TradingStrategies
from src.utils.technical_indicators import create_sample_data
import pandas as pd
from datetime import datetime, date, timedelta

strategies_bp = Blueprint('strategies', __name__)

@strategies_bp.route('/strategies', methods=['GET'])
def get_available_strategies():
    """الحصول على قائمة الاستراتيجيات المتاحة"""
    try:
        # إنشاء بيانات تجريبية للحصول على قائمة الاستراتيجيات
        sample_data = create_sample_data('SAMPLE', 100)
        trading_strategies = TradingStrategies(sample_data)
        strategies = trading_strategies.get_all_strategies()
        
        return jsonify({
            'success': True,
            'data': strategies
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@strategies_bp.route('/strategies/<strategy_type>/apply', methods=['POST'])
def apply_strategy(strategy_type):
    """تطبيق استراتيجية معينة"""
    try:
        data = request.get_json()
        symbol = data.get('symbol')
        parameters = data.get('parameters', {})
        days = data.get('days', 100)
        
        if not symbol:
            return jsonify({
                'success': False,
                'error': 'رمز السهم مطلوب'
            }), 400
        
        # التحقق من وجود السهم
        stock = Stock.query.filter_by(symbol=symbol).first()
        if not stock:
            return jsonify({
                'success': False,
                'error': 'السهم غير موجود'
            }), 404
        
        # جلب البيانات التاريخية
        df = get_stock_data(stock, days)
        
        # تطبيق الاستراتيجية
        trading_strategies = TradingStrategies(df)
        
        if strategy_type == 'moving_average':
            short_period = parameters.get('short_period', 20)
            long_period = parameters.get('long_period', 50)
            result = trading_strategies.moving_average_crossover_strategy(short_period, long_period)
            
        elif strategy_type == 'rsi':
            period = parameters.get('period', 14)
            oversold = parameters.get('oversold', 30)
            overbought = parameters.get('overbought', 70)
            result = trading_strategies.rsi_strategy(period, oversold, overbought)
            
        elif strategy_type == 'macd':
            result = trading_strategies.macd_strategy()
            
        elif strategy_type == 'bollinger_bands':
            period = parameters.get('period', 20)
            std_dev = parameters.get('std_dev', 2)
            result = trading_strategies.bollinger_bands_strategy(period, std_dev)
            
        elif strategy_type == 'combined':
            result = trading_strategies.combined_strategy()
            
        else:
            return jsonify({
                'success': False,
                'error': 'نوع الاستراتيجية غير مدعوم'
            }), 400
        
        if result['success']:
            # إضافة معلومات إضافية
            result['symbol'] = symbol
            result['stock_name'] = stock.name
            result['analysis_period'] = f'{days} يوم'
            result['timestamp'] = datetime.now().isoformat()
            
            return jsonify({
                'success': True,
                'data': result
            })
        else:
            return jsonify({
                'success': False,
                'error': result['error']
            }), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@strategies_bp.route('/strategies/compare', methods=['POST'])
def compare_strategies():
    """مقارنة عدة استراتيجيات على نفس السهم"""
    try:
        data = request.get_json()
        symbol = data.get('symbol')
        strategy_types = data.get('strategies', ['moving_average', 'rsi', 'macd'])
        days = data.get('days', 100)
        
        if not symbol:
            return jsonify({
                'success': False,
                'error': 'رمز السهم مطلوب'
            }), 400
        
        # التحقق من وجود السهم
        stock = Stock.query.filter_by(symbol=symbol).first()
        if not stock:
            return jsonify({
                'success': False,
                'error': 'السهم غير موجود'
            }), 404
        
        # جلب البيانات التاريخية
        df = get_stock_data(stock, days)
        trading_strategies = TradingStrategies(df)
        
        results = {}
        
        for strategy_type in strategy_types:
            try:
                if strategy_type == 'moving_average':
                    result = trading_strategies.moving_average_crossover_strategy()
                elif strategy_type == 'rsi':
                    result = trading_strategies.rsi_strategy()
                elif strategy_type == 'macd':
                    result = trading_strategies.macd_strategy()
                elif strategy_type == 'bollinger_bands':
                    result = trading_strategies.bollinger_bands_strategy()
                elif strategy_type == 'combined':
                    result = trading_strategies.combined_strategy()
                else:
                    continue
                
                if result['success']:
                    results[strategy_type] = {
                        'name': result['strategy_name'],
                        'performance': result['performance'],
                        'signals_count': len(result['signals']),
                        'latest_signals': result['signals'][-3:] if result['signals'] else []
                    }
                    
            except Exception as e:
                results[strategy_type] = {
                    'error': str(e)
                }
        
        # ترتيب النتائج حسب معدل النجاح
        sorted_results = sorted(
            [(k, v) for k, v in results.items() if 'performance' in v],
            key=lambda x: x[1]['performance']['success_rate'],
            reverse=True
        )
        
        return jsonify({
            'success': True,
            'data': {
                'symbol': symbol,
                'stock_name': stock.name,
                'analysis_period': f'{days} يوم',
                'results': results,
                'ranking': [{'strategy': k, 'success_rate': v['performance']['success_rate']} 
                           for k, v in sorted_results],
                'timestamp': datetime.now().isoformat()
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@strategies_bp.route('/strategies/portfolio', methods=['POST'])
def create_portfolio_strategy():
    """إنشاء استراتيجية محفظة متنوعة"""
    try:
        data = request.get_json()
        symbols = data.get('symbols', [])
        strategy_type = data.get('strategy', 'moving_average')
        allocation = data.get('allocation', {})  # توزيع الأوزان
        days = data.get('days', 100)
        
        if not symbols:
            return jsonify({
                'success': False,
                'error': 'قائمة الأسهم مطلوبة'
            }), 400
        
        portfolio_results = {}
        total_return = 0
        total_signals = 0
        successful_signals = 0
        
        for symbol in symbols:
            try:
                stock = Stock.query.filter_by(symbol=symbol).first()
                if not stock:
                    continue
                
                # جلب البيانات وتطبيق الاستراتيجية
                df = get_stock_data(stock, days)
                trading_strategies = TradingStrategies(df)
                
                if strategy_type == 'moving_average':
                    result = trading_strategies.moving_average_crossover_strategy()
                elif strategy_type == 'rsi':
                    result = trading_strategies.rsi_strategy()
                elif strategy_type == 'macd':
                    result = trading_strategies.macd_strategy()
                else:
                    result = trading_strategies.moving_average_crossover_strategy()
                
                if result['success']:
                    weight = allocation.get(symbol, 1.0 / len(symbols))
                    weighted_return = result['performance']['total_return'] * weight
                    
                    portfolio_results[symbol] = {
                        'stock_name': stock.name,
                        'weight': weight,
                        'performance': result['performance'],
                        'weighted_return': weighted_return,
                        'latest_signal': result['signals'][-1] if result['signals'] else None
                    }
                    
                    total_return += weighted_return
                    total_signals += result['performance']['total_signals']
                    successful_signals += result['performance']['profitable_signals']
                    
            except Exception as e:
                portfolio_results[symbol] = {'error': str(e)}
        
        # حساب أداء المحفظة الإجمالي
        portfolio_performance = {
            'total_return': round(total_return, 2),
            'total_signals': total_signals,
            'successful_signals': successful_signals,
            'success_rate': round((successful_signals / max(total_signals, 1)) * 100, 2),
            'diversification_score': len([r for r in portfolio_results.values() if 'performance' in r])
        }
        
        # توصيات المحفظة
        recommendations = generate_portfolio_recommendations(portfolio_results)
        
        return jsonify({
            'success': True,
            'data': {
                'portfolio_performance': portfolio_performance,
                'individual_results': portfolio_results,
                'recommendations': recommendations,
                'strategy_used': strategy_type,
                'analysis_period': f'{days} يوم',
                'timestamp': datetime.now().isoformat()
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@strategies_bp.route('/strategies/backtest', methods=['POST'])
def backtest_strategy():
    """اختبار استراتيجية على بيانات تاريخية"""
    try:
        data = request.get_json()
        symbol = data.get('symbol')
        strategy_type = data.get('strategy')
        parameters = data.get('parameters', {})
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        initial_capital = data.get('initial_capital', 100000)  # رأس المال الأولي
        
        if not all([symbol, strategy_type]):
            return jsonify({
                'success': False,
                'error': 'رمز السهم ونوع الاستراتيجية مطلوبان'
            }), 400
        
        # التحقق من وجود السهم
        stock = Stock.query.filter_by(symbol=symbol).first()
        if not stock:
            return jsonify({
                'success': False,
                'error': 'السهم غير موجود'
            }), 404
        
        # تحديد فترة الاختبار
        if start_date and end_date:
            days = (datetime.strptime(end_date, '%Y-%m-%d') - 
                   datetime.strptime(start_date, '%Y-%m-%d')).days
        else:
            days = 365  # سنة واحدة افتراضياً
        
        # جلب البيانات وتطبيق الاستراتيجية
        df = get_stock_data(stock, days)
        trading_strategies = TradingStrategies(df)
        
        # تطبيق الاستراتيجية المحددة
        if strategy_type == 'moving_average':
            result = trading_strategies.moving_average_crossover_strategy(
                parameters.get('short_period', 20),
                parameters.get('long_period', 50)
            )
        elif strategy_type == 'rsi':
            result = trading_strategies.rsi_strategy(
                parameters.get('period', 14),
                parameters.get('oversold', 30),
                parameters.get('overbought', 70)
            )
        elif strategy_type == 'macd':
            result = trading_strategies.macd_strategy()
        elif strategy_type == 'bollinger_bands':
            result = trading_strategies.bollinger_bands_strategy(
                parameters.get('period', 20),
                parameters.get('std_dev', 2)
            )
        else:
            return jsonify({
                'success': False,
                'error': 'نوع الاستراتيجية غير مدعوم'
            }), 400
        
        if not result['success']:
            return jsonify({
                'success': False,
                'error': result['error']
            }), 400
        
        # محاكاة التداول التفصيلية
        backtest_results = simulate_detailed_trading(
            result['signals'], 
            df, 
            initial_capital
        )
        
        # إضافة تحليل المخاطر
        risk_analysis = calculate_risk_metrics(backtest_results['equity_curve'])
        
        return jsonify({
            'success': True,
            'data': {
                'strategy_name': result['strategy_name'],
                'symbol': symbol,
                'stock_name': stock.name,
                'backtest_period': f'{days} يوم',
                'initial_capital': initial_capital,
                'final_capital': backtest_results['final_capital'],
                'total_return': backtest_results['total_return'],
                'performance': result['performance'],
                'detailed_trades': backtest_results['trades'],
                'equity_curve': backtest_results['equity_curve'],
                'risk_analysis': risk_analysis,
                'parameters': parameters,
                'timestamp': datetime.now().isoformat()
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

def get_stock_data(stock, days):
    """جلب بيانات السهم التاريخية"""
    try:
        # محاولة جلب البيانات من قاعدة البيانات
        end_date = date.today()
        start_date = end_date - timedelta(days=days)
        
        prices = StockPrice.query.filter(
            StockPrice.stock_id == stock.id,
            StockPrice.date >= start_date,
            StockPrice.date <= end_date
        ).order_by(StockPrice.date.asc()).all()
        
        if prices and len(prices) > 20:
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
            return pd.DataFrame(data)
        else:
            # استخدام بيانات تجريبية
            return create_sample_data(stock.symbol, days)
            
    except Exception as e:
        # في حالة الخطأ، استخدم بيانات تجريبية
        return create_sample_data(stock.symbol, days)

def generate_portfolio_recommendations(portfolio_results):
    """إنشاء توصيات للمحفظة"""
    recommendations = []
    
    # تحليل الأداء
    performing_stocks = []
    underperforming_stocks = []
    
    for symbol, result in portfolio_results.items():
        if 'performance' in result:
            if result['performance']['success_rate'] > 70:
                performing_stocks.append(symbol)
            elif result['performance']['success_rate'] < 50:
                underperforming_stocks.append(symbol)
    
    if performing_stocks:
        recommendations.append({
            'type': 'زيادة الوزن',
            'stocks': performing_stocks,
            'reason': 'أداء قوي ومعدل نجاح عالي'
        })
    
    if underperforming_stocks:
        recommendations.append({
            'type': 'تقليل الوزن',
            'stocks': underperforming_stocks,
            'reason': 'أداء ضعيف ومعدل نجاح منخفض'
        })
    
    # توصيات عامة
    if len(portfolio_results) < 5:
        recommendations.append({
            'type': 'تنويع',
            'reason': 'زيادة عدد الأسهم في المحفظة لتقليل المخاطر'
        })
    
    return recommendations

def simulate_detailed_trading(signals, data, initial_capital):
    """محاكاة تداول تفصيلية"""
    capital = initial_capital
    position = None
    shares = 0
    trades = []
    equity_curve = []
    
    for signal in signals:
        # العثور على السعر في التاريخ المحدد
        signal_date = signal['date']
        price = signal['price']
        
        if signal['type'] in ['شراء', 'شراء قوي'] and position != 'long':
            # شراء
            if position == 'short':
                # إغلاق صفقة بيع
                profit = shares * (entry_price - price)
                capital += profit
                trades.append({
                    'type': 'إغلاق بيع',
                    'date': signal_date,
                    'price': price,
                    'shares': shares,
                    'profit': profit
                })
            
            # فتح صفقة شراء
            shares = int(capital * 0.95 / price)  # استخدام 95% من رأس المال
            capital -= shares * price
            position = 'long'
            entry_price = price
            
            trades.append({
                'type': 'شراء',
                'date': signal_date,
                'price': price,
                'shares': shares,
                'capital_used': shares * price
            })
            
        elif signal['type'] in ['بيع', 'بيع قوي'] and position != 'short':
            # بيع
            if position == 'long':
                # إغلاق صفقة شراء
                profit = shares * (price - entry_price)
                capital += shares * price
                trades.append({
                    'type': 'إغلاق شراء',
                    'date': signal_date,
                    'price': price,
                    'shares': shares,
                    'profit': profit
                })
                shares = 0
            
            position = 'short'
            entry_price = price
        
        # حساب قيمة المحفظة الحالية
        current_value = capital
        if position == 'long' and shares > 0:
            current_value += shares * price
        
        equity_curve.append({
            'date': signal_date,
            'value': current_value
        })
    
    # إغلاق آخر صفقة
    if position and shares > 0:
        last_price = data.iloc[-1]['close']
        if position == 'long':
            profit = shares * (last_price - entry_price)
            capital += shares * last_price
        
        trades.append({
            'type': 'إغلاق نهائي',
            'date': data.iloc[-1]['date'] if 'date' in data.columns else 'النهاية',
            'price': last_price,
            'shares': shares,
            'profit': profit if position == 'long' else shares * (entry_price - last_price)
        })
    
    final_capital = capital
    total_return = ((final_capital - initial_capital) / initial_capital) * 100
    
    return {
        'final_capital': round(final_capital, 2),
        'total_return': round(total_return, 2),
        'trades': trades,
        'equity_curve': equity_curve
    }

def calculate_risk_metrics(equity_curve):
    """حساب مقاييس المخاطر"""
    if len(equity_curve) < 2:
        return {}
    
    values = [point['value'] for point in equity_curve]
    returns = []
    
    for i in range(1, len(values)):
        daily_return = (values[i] - values[i-1]) / values[i-1]
        returns.append(daily_return)
    
    if not returns:
        return {}
    
    # حساب المقاييس
    avg_return = np.mean(returns)
    volatility = np.std(returns)
    max_value = max(values)
    
    # حساب أقصى انخفاض
    max_drawdown = 0
    peak = values[0]
    
    for value in values:
        if value > peak:
            peak = value
        drawdown = (peak - value) / peak
        if drawdown > max_drawdown:
            max_drawdown = drawdown
    
    # نسبة شارب (مبسطة)
    sharpe_ratio = avg_return / volatility if volatility > 0 else 0
    
    return {
        'volatility': round(volatility * 100, 2),
        'max_drawdown': round(max_drawdown * 100, 2),
        'sharpe_ratio': round(sharpe_ratio, 2),
        'max_value': round(max_value, 2)
    }

