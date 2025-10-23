#!/usr/bin/env python3
"""
Анализ найденных болевых точек и создание отчета для обновления сайта
"""

import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Any
from database import DatabaseManager

def analyze_pain_points():
    """Анализ найденных болевых точек"""
    db = DatabaseManager()
    
    # Получаем все болевые точки
    pain_points = db.get_all_pain_points()
    
    if not pain_points:
        print("❌ Болевые точки не найдены в базе данных")
        return
    
    print(f"📊 Анализируем {len(pain_points)} болевых точек...")
    
    # Группируем по категориям
    categories = {}
    for pain_point in pain_points:
        category = pain_point.get('category', 'unknown')
        if category not in categories:
            categories[category] = []
        categories[category].append(pain_point)
    
    # Анализируем каждую категорию
    category_analysis = {}
    
    for category, points in categories.items():
        print(f"\n🔍 Анализируем категорию: {category} ({len(points)} болей)")
        
        # Находим общие темы
        common_keywords = {}
        common_texts = []
        
        for point in points:
            # Анализируем ключевые слова
            keywords = json.loads(point.get('keywords', '[]'))
            for keyword in keywords:
                common_keywords[keyword] = common_keywords.get(keyword, 0) + 1
            
            # Собираем тексты для анализа
            text = point.get('text', '')
            if len(text) > 20:  # Только значимые тексты
                common_texts.append(text)
        
        # Топ ключевых слов
        top_keywords = sorted(common_keywords.items(), key=lambda x: x[1], reverse=True)[:10]
        
        # Находим примеры болей
        examples = sorted(points, key=lambda x: x.get('total_score', 0), reverse=True)[:5]
        
        category_analysis[category] = {
            'count': len(points),
            'top_keywords': top_keywords,
            'examples': examples,
            'common_texts': common_texts[:10]  # Первые 10 текстов
        }
        
        print(f"   Топ ключевых слов: {[kw[0] for kw in top_keywords[:5]]}")
        print(f"   Примеры болей: {len(examples)}")
    
    return category_analysis

def generate_agents_suggestions(category_analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Генерирует предложения агентов на основе анализа болей"""
    
    agents = []
    
    # Operational боли - рутинные задачи
    if 'operational' in category_analysis:
        op_data = category_analysis['operational']
        agents.append({
            'name': 'Product Management Agent',
            'description': 'Automatically manages product inventory, updates prices, and handles product uploads across multiple platforms',
            'pain_solved': 'Manual product management taking 4+ hours daily',
            'features': [
                'Auto price monitoring and updates',
                'Bulk product uploads to Shopify/Amazon',
                'Inventory level tracking',
                'Product description optimization'
            ],
            'pilot_price': 750,
            'full_price': 2500,
            'category': 'operational'
        })
    
    # Financial боли - дорогие инструменты
    if 'financial' in category_analysis:
        fin_data = category_analysis['financial']
        agents.append({
            'name': 'Cost-Effective Analytics Agent',
            'description': 'Replaces expensive analytics tools with custom automated reporting and monitoring',
            'pain_solved': 'Expensive price monitoring and analytics tools',
            'features': [
                'Custom price monitoring dashboard',
                'Automated sales reports',
                'Competitor analysis',
                'ROI tracking and alerts'
            ],
            'pilot_price': 500,
            'full_price': 2000,
            'category': 'financial'
        })
    
    # Marketing боли - проблемы с продвижением
    if 'marketing' in category_analysis:
        agents.append({
            'name': 'Marketing Automation Agent',
            'description': 'Handles social media posting, email campaigns, and customer engagement automatically',
            'pain_solved': 'Manual marketing tasks and low engagement',
            'features': [
                'Automated social media posting',
                'Email campaign management',
                'Customer segmentation',
                'A/B testing automation'
            ],
            'pilot_price': 1000,
            'full_price': 3000,
            'category': 'marketing'
        })
    
    # Communication боли - проблемы с клиентами
    if 'communication' in category_analysis:
        agents.append({
            'name': 'Customer Support Agent',
            'description': 'AI-powered customer support that handles common questions and escalates complex issues',
            'pain_solved': 'Overwhelming customer support requests',
            'features': [
                '24/7 automated responses',
                'Ticket categorization',
                'Escalation to human agents',
                'Customer satisfaction tracking'
            ],
            'pilot_price': 800,
            'full_price': 2200,
            'category': 'communication'
        })
    
    # Analytical боли - проблемы с отчетами
    if 'analytical' in category_analysis:
        agents.append({
            'name': 'Business Intelligence Agent',
            'description': 'Creates comprehensive business reports and insights from your e-commerce data',
            'pain_solved': 'Time-consuming manual report creation',
            'features': [
                'Automated daily/weekly reports',
                'Custom dashboard creation',
                'Trend analysis and predictions',
                'Data visualization'
            ],
            'pilot_price': 600,
            'full_price': 1800,
            'category': 'analytical'
        })
    
    # General боли - общие проблемы
    if 'general' in category_analysis:
        agents.append({
            'name': 'Business Process Automation Agent',
            'description': 'Custom automation for your specific business processes and workflows',
            'pain_solved': 'Manual processes slowing down business growth',
            'features': [
                'Custom workflow automation',
                'Integration with existing tools',
                'Process optimization',
                'Scalable solutions'
            ],
            'pilot_price': 1000,
            'full_price': 3500,
            'category': 'general'
        })
    
    return agents

def create_website_update(agents: List[Dict[str, Any]]) -> str:
    """Создает HTML код для обновления раздела Agents на сайте"""
    
    html = """
    <!-- Agents Section - Updated with Real Pain Points -->
    <section id="agents" class="agents">
        <div class="container">
            <h2 class="section-title">AI Agents That Solve Real E-commerce Problems</h2>
            <p class="section-subtitle">Based on analysis of 186+ real business discussions and 56+ identified pain points</p>
            <div class="agents-grid">
"""
    
    for agent in agents:
        html += f"""
                <div class="agent-card">
                    <div class="agent-icon">🤖</div>
                    <h3>{agent['name']}</h3>
                    <p class="pain-solved">Solves: {agent['pain_solved']}</p>
                    <p>{agent['description']}</p>
                    <div class="agent-features">
                        <h4>Key Features:</h4>
                        <ul>
"""
        for feature in agent['features']:
            html += f"                            <li>{feature}</li>\n"
        
        html += f"""
                        </ul>
                    </div>
                    <div class="agent-pricing">
                        <span class="pilot">Pilot: ${agent['pilot_price']}</span>
                        <span class="full">Full: ${agent['full_price']}</span>
                    </div>
                </div>
"""
    
    html += """
            </div>
        </div>
    </section>
"""
    
    return html

def main():
    """Основная функция"""
    print("=" * 60)
    print("🔍 АНАЛИЗ БОЛЕВЫХ ТОЧЕК E-COMMERCE")
    print("=" * 60)
    
    # Анализируем болевые точки
    category_analysis = analyze_pain_points()
    
    if not category_analysis:
        return
    
    # Генерируем предложения агентов
    print("\n🤖 Генерируем предложения агентов...")
    agents = generate_agents_suggestions(category_analysis)
    
    print(f"\n✅ Создано {len(agents)} агентов на основе реальных болей:")
    for agent in agents:
        print(f"   - {agent['name']}: {agent['pain_solved']}")
    
    # Создаем HTML для сайта
    print("\n🌐 Создаем HTML для обновления сайта...")
    website_html = create_website_update(agents)
    
    # Сохраняем в файл
    with open('website_agents_update.html', 'w', encoding='utf-8') as f:
        f.write(website_html)
    
    print("✅ HTML сохранен в website_agents_update.html")
    
    # Создаем детальный отчет
    report = f"""
# E-commerce Pain Points Analysis Report
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Summary
- Total pain points analyzed: {sum(cat['count'] for cat in category_analysis.values())}
- Categories identified: {len(category_analysis)}
- Agents suggested: {len(agents)}

## Category Breakdown
"""
    
    for category, data in category_analysis.items():
        report += f"""
### {category.title()} ({data['count']} pain points)
- Top keywords: {', '.join([kw[0] for kw in data['top_keywords'][:5]])}
- Example pain: {data['examples'][0]['text'][:100]}... (Score: {data['examples'][0]['total_score']:.2f})
"""
    
    report += f"""
## Suggested AI Agents

"""
    
    for agent in agents:
        report += f"""
### {agent['name']}
- **Pain Solved:** {agent['pain_solved']}
- **Description:** {agent['description']}
- **Pilot Price:** ${agent['pilot_price']}
- **Full Price:** ${agent['full_price']}
- **Features:** {', '.join(agent['features'])}
"""
    
    with open('pain_points_analysis_report.md', 'w', encoding='utf-8') as f:
        f.write(report)
    
    print("✅ Детальный отчет сохранен в pain_points_analysis_report.md")
    
    print("\n" + "=" * 60)
    print("🎉 АНАЛИЗ ЗАВЕРШЕН!")
    print("=" * 60)

if __name__ == "__main__":
    main()
