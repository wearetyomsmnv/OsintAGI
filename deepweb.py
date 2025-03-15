from crewai import Agent, Task, Crew, Process
from langchain.tools import BaseTool
from typing import List, Dict, Any
from pydantic import BaseModel, Field
import os
from datetime import datetime
import re

os.makedirs('./crew_memory', exist_ok=True)
os.makedirs('./osint_results', exist_ok=True)

os.environ['SERPER_API_KEY'] = '**'
os.environ['OTEL_SDK_DISABLED'] = 'true'
os.environ['CREWAI_STORAGE_DIR'] = os.path.abspath('./crew_memory')

from crewai_tools import SerperDevTool, ScrapeWebsiteTool

search_tool = SerperDevTool(
    n_results=15
)
scrape_tool = ScrapeWebsiteTool()

# Создаем специализированных агентов для даркнета
darknet_researcher = Agent(
    role='Исследователь даркнета',
    goal='Находить и анализировать информацию в даркнете',
    backstory="""Эксперт по исследованию даркнет-ресурсов.
    Специализируюсь на поиске информации в теневых маркетплейсах, форумах и других ресурсах даркнета.
    Умею находить и верифицировать данные из закрытых источников.""",
    tools=[search_tool],
    verbose=True,
    allow_delegation=True
)

marketplace_analyst = Agent(
    role='Аналитик даркнет-маркетплейсов',
    goal='Анализировать активность на теневых площадках',
    backstory="""Специалист по анализу даркнет-маркетплейсов.
    Умею отслеживать активность, находить связи между аккаунтами и анализировать историю транзакций.
    Знаю специфику работы основных теневых площадок.""",
    tools=[search_tool, scrape_tool],
    verbose=True
)

forum_expert = Agent(
    role='Эксперт по даркнет-форумам',
    goal='Исследовать коммуникации на закрытых форумах',
    backstory="""Специалист по анализу даркнет-форумов.
    Умею находить и анализировать профили, отслеживать связи между участниками.
    Знаю специфику различных закрытых сообществ.""",
    tools=[search_tool, scrape_tool],
    verbose=True
)

crypto_analyst = Agent(
    role='Криптовалютный аналитик',
    goal='Анализировать криптовалютные транзакции и кошельки',
    backstory="""Эксперт по криптовалютному анализу.
    Специализируюсь на отслеживании криптовалютных транзакций и связей между кошельками.
    Умею выявлять паттерны использования криптовалют.""",
    tools=[search_tool],
    verbose=True
)

verification_expert = Agent(
    role='Эксперт по верификации',
    goal='Проверять достоверность данных из даркнета',
    backstory="""Специалист по верификации данных из даркнета.
    Использую кросс-референсный анализ и множественные источники.
    Умею отличать дезинформацию от реальных данных.""",
    tools=[search_tool, scrape_tool],
    verbose=True
)

def create_investigation_plan(target: str) -> List[Task]:
    """Создает план расследования в даркнете"""
    tasks = []
    
    # Задача 1: Первичный анализ в даркнете
    tasks.append(Task(
        description=f"""
        Проведи первичный анализ {target} в даркнете:
        
        1. Поиск по основным даркнет-ресурсам:
           - Теневые маркетплейсы
           - Закрытые форумы
           - Специализированные площадки
        
        2. Определи ключевые точки для исследования:
           - Возможные аккаунты
           - Связанные сервисы
           - Упоминания в утечках
        
        Перед завершением анализа, проверь с человеком правильность найденной информации.
        """,
        expected_output="""Отчет о первичном анализе в даркнете:
        1. Найденные упоминания:
           - На маркетплейсах
           - На форумах
           - В других источниках
        
        2. Потенциальные направления:
           - Выявленные аккаунты
           - Связанные сервисы
           - Данные из утечек""",
        agent=darknet_researcher,
        human_input=True
    ))
    
    # Задача 2: Анализ маркетплейсов
    tasks.append(Task(
        description=f"""
        Проанализируй активность {target} на теневых площадках:
        
        1. Исследуй основные маркетплейсы:
           - История активности
           - Связанные аккаунты
           - Транзакции
        
        2. Проанализируй:
           - Типы взаимодействий
           - Используемые сервисы
           - Временные паттерны
        
        Перед завершением анализа, проверь с человеком найденные данные.
        """,
        expected_output="""Отчет по анализу маркетплейсов:
        1. Активность на площадках:
           - Список аккаунтов
           - История действий
           - Связанные транзакции
        
        2. Выявленные паттерны:
           - Типы активности
           - Временные периоды
           - Предпочитаемые сервисы""",
        agent=marketplace_analyst,
        human_input=True
    ))
    
    # Задача 3: Анализ форумов
    tasks.append(Task(
        description=f"""
        Исследуй присутствие {target} на даркнет-форумах:
        
        1. Анализ форумов:
           - Поиск профилей
           - История сообщений
           - Взаимодействия с другими
        
        2. Изучи:
           - Темы обсуждений
           - Контакты и связи
           - Репутацию
        
        Проверь с человеком найденные профили и связи.
        """,
        expected_output="""Отчет по анализу форумов:
        1. Найденные профили:
           - Список аккаунтов
           - История активности
           - Ключевые обсуждения
        
        2. Социальные связи:
           - Основные контакты
           - Группы взаимодействия
           - Репутационные метрики""",
        agent=forum_expert,
        human_input=True
    ))
    
    # Задача 4: Криптоанализ
    tasks.append(Task(
        description=f"""
        Проведи анализ криптовалютной активности {target}:
        
        1. Исследуй:
           - Связанные кошельки
           - Историю транзакций
           - Паттерны использования
        
        2. Проанализируй:
           - Объемы операций
           - Связи с сервисами
           - Временные паттерны
        
        Обсуди с человеком найденные транзакции и связи.
        """,
        expected_output="""Отчет по криптоанализу:
        1. Криптовалютная активность:
           - Выявленные кошельки
           - Значимые транзакции
           - Используемые сервисы
        
        2. Анализ паттернов:
           - Объемы операций
           - Временные периоды
           - Связи с другими адресами""",
        agent=crypto_analyst,
        human_input=True
    ))
    
    # Задача 5: Верификация данных
    tasks.append(Task(
        description=f"""
        Проверь всю собранную информацию о {target}:
        
        1. Верификация данных:
           - Кросс-проверка источников
           - Подтверждение находок
           - Выявление противоречий
        
        2. Оценка достоверности:
           - Надежность источников
           - Актуальность данных
           - Возможные фальсификации
        
        Обсуди с человеком результаты проверки.
        """,
        expected_output="""Отчет по верификации:
        1. Подтвержденные данные:
           - Проверенные факты
           - Источники подтверждения
           - Уровень достоверности
        
        2. Сомнительная информация:
           - Непроверенные данные
           - Противоречия
           - Рекомендации по проверке""",
        agent=verification_expert,
        human_input=True
    ))
    
    return tasks

def run_osint_investigation(target: str):
    """Запускает OSINT-расследование в даркнете"""
    try:
        crew = Crew(
            agents=[
                darknet_researcher,
                marketplace_analyst,
                forum_expert,
                crypto_analyst,
                verification_expert
            ],
            tasks=create_investigation_plan(target),
            verbose=True,
            process=Process.sequential,
            memory=True
        )
        
        result = crew.kickoff()
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        with open(f'osint_results/darknet_investigation_{timestamp}.txt', 'w', encoding='utf-8') as f:
            f.write(f"Darknet Investigation Report\n")
            f.write("=" * 50 + "\n\n")
            f.write(f"Цель исследования: {target}\n")
            f.write("=" * 50 + "\n\n")
            f.write(str(result))
        
        return result
        
    except Exception as e:
        print(f"Ошибка: {str(e)}")
        return None

if __name__ == "__main__":
    target = input("Введите цель для исследования в даркнете: ")
    result = run_osint_investigation(target)
    if result:
        print("\nРезультаты расследования:")
        print(result)
