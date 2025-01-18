from crewai import Agent, Task, Crew, Process
from langchain.tools import BaseTool
from typing import List, Dict, Any
from pydantic import BaseModel, Field
import os
from datetime import datetime
import re

os.makedirs('./crew_memory', exist_ok=True)
os.makedirs('./osint_results', exist_ok=True)

os.environ['SERPER_API_KEY'] = '**' #поменять на свой serper.dev
os.environ['OTEL_SDK_DISABLED'] = 'true' #отключаем телеметрию
os.environ['CREWAI_STORAGE_DIR'] = os.path.abspath('./crew_memory') #хранилка для памяти

# Инициализация инструментов из crewai[tools]
from crewai_tools import SerperDevTool, ScrapeWebsiteTool

search_tool = SerperDevTool(
    n_results=10,
    country="ru",
    locale="ru"
)
scrape_tool = ScrapeWebsiteTool()

# Создаем основных агентов
lead_analyst = Agent(
    role='Ведущий OSINT-аналитик',
    goal='Координировать OSINT-исследование и анализировать полученные данные',
    backstory="""Опытный аналитик с глубоким пониманием OSINT. 
    Специализируюсь на построении полных профилей на основе цифровых следов.
    Умею эффективно делегировать задачи и объединять различные источники информации.""",
    tools=[search_tool],
    verbose=True,
    allow_delegation=True
)

social_expert = Agent(
    role='Эксперт по социальным сетям',
    goal='Находить и анализировать профили в социальных сетях',
    backstory="""Специалист по анализу социальных сетей и онлайн-поведения.
    Умею находить связанные аккаунты и выявлять паттерны активности.""",
    tools=[search_tool, scrape_tool],
    verbose=True
)

technical_analyst = Agent(
    role='Технический аналитик',
    goal='Анализировать техническую информацию и цифровые следы',
    backstory="""Эксперт по технической разведке.
    Специализируюсь на анализе доменов, IP, утечек данных и технических метаданных.""",
    tools=[search_tool, scrape_tool],
    verbose=True
)

behavior_analyst = Agent(
    role='Аналитик поведения',
    goal='Анализировать поведенческие паттерны и связи',
    backstory="""Специалист по поведенческому анализу.
    Умею выявлять интересы, связи и паттерны поведения на основе цифровых следов.""",
    tools=[search_tool],
    verbose=True
)

verification_expert = Agent(
    role='Эксперт по верификации данных',
    goal='Проверять достоверность собранной информации',
    backstory="""Специалист по проверке и подтверждению данных OSINT.
    Использую кросс-референсный анализ и множественные источники для верификации.
    Умею выявлять дезинформацию и ложные следы.""",
    tools=[search_tool, scrape_tool],
    verbose=True
)

deep_search_expert = Agent(
    role='Эксперт по глубокому поиску',
    goal='Находить скрытую и труднодоступную информацию',
    backstory="""Специалист по глубокому OSINT-поиску.
    Умею находить информацию в архивах, исторических данных и специализированных базах.
    Специализируюсь на поиске неочевидных связей и скрытых данных.""",
    tools=[search_tool, scrape_tool],
    verbose=True
)

task_keeper = Agent(
    role='Хранитель задачи',
    goal='Обеспечивать фокус исследования на поставленной задаче',
    backstory="""Специалист по управлению фокусом исследования.
    Отслеживаю соответствие всех действий изначальной задаче.
    Помогаю агентам не отклоняться от цели исследования.""",
    tools=[search_tool],
    verbose=True
)

context_analyst = Agent(
    role='Аналитик контекста',
    goal='Поддерживать контекстную целостность расследования',
    backstory="""Эксперт по контекстному анализу.
    Объединяю разрозненные данные в единый контекст.
    Отслеживаю релевантность информации относительно задачи.""",
    tools=[search_tool],
    verbose=True
)

manager_agent = Agent(
    role='OSINT Менеджер',
    goal='Управлять процессом расследования и координировать работу агентов',
    backstory="""Опытный руководитель OSINT-исследований.
    Специализируюсь на координации сложных расследований и управлении командой аналитиков.
    Обеспечиваю эффективное взаимодействие между агентами и качество результатов.""",
    tools=[],
    verbose=True,
    allow_delegation=True
)

def create_investigation_plan(target: str) -> List[Task]:
    """Создает план расследования"""
    tasks = []
    
    tasks.append(Task(
        description=f"""
        Проведи первичный анализ цели: {target}
        1. Определи основные платформы присутствия
        2. Найди ключевые идентификаторы (email, username, etc.)
        3. Составь начальный профиль
        4. Определи приоритетные направления для глубокого анализа
        
        Делегируй подзадачи другим агентам при необходимости.
        """,
        expected_output="""Предоставь структурированный отчет, содержащий:
        1. Список найденных платформ
        2. Найденные идентификаторы
        3. Краткий профиль цели
        4. Приоритетные направления для дальнейшего анализа""",
        agent=lead_analyst
    ))
    
    tasks.append(Task(
        description=f"""
        На основе первичного анализа исследуй социальные сети {target}:
        1. Найди все связанные профили
        2. Проанализируй контакты и связи
        3. Изучи историю активности
        4. Выяви поведенческие паттерны
        """,
        expected_output="""Предоставь отчет, включающий:
        1. Список найденных профилей с ссылками
        2. Основные контакты и связи
        3. Ключевые моменты из истории активности
        4. Выявленные паттерны поведения""",
        agent=social_expert
    ))
    
    tasks.append(Task(
        description=f"""
        Проведи технический анализ найденных данных о {target}:
        1. Проверь утечки данных
        2. Найди связанные домены и IP
        3. Проанализируй технические метаданные
        4. Исследуй цифровые следы
        """,
        expected_output="""Предоставь технический отчет, содержащий:
        1. Найденные утечки данных
        2. Список связанных технических идентификаторов
        3. Анализ метаданных
        4. Карту цифровых следов""",
        agent=technical_analyst
    ))
    
    tasks.append(Task(
        description=f"""
        На основе собранных данных проанализируй поведение {target}:
        1. Определи основные интересы
        2. Выяви поведенческие паттерны
        3. Проанализируй социальные связи
        4. Составь психологический профиль
        """,
        expected_output="""Предоставь поведенческий анализ, включающий:
        1. Карту интересов
        2. Описание поведенческих паттернов
        3. Схему социальных связей
        4. Психологический профиль""",
        agent=behavior_analyst
    ))
    
    tasks.append(Task(
        description=f"""
        Проанализируй все собранные данные о {target}:
        1. Объедини информацию от всех агентов
        2. Выяви пробелы в данных
        3. Спланируй дополнительные направления поиска
        4. Составь детальный профиль цели
        """,
        expected_output="""Предоставь итоговый отчет, содержащий:
        1. Полный профиль цели
        2. Выявленные пробелы в данных
        3. План дальнейшего расследования
        4. Основные выводы и рекомендации""",
        agent=lead_analyst
    ))
    
    tasks.append(Task(
        description=f"""
        Проведи глубокий поиск информации о {target}:
        1. Исследуй архивные данные и исторические записи
        2. Проанализируй специализированные базы данных
        3. Найди неочевидные связи и упоминания
        4. Исследуй редкие и специфические источники
        """,
        expected_output="""Предоставь детальный отчет, включающий:
        1. Найденные архивные данные
        2. Результаты поиска в специализированных базах
        3. Выявленные неочевидные связи
        4. Информацию из редких источников""",
        agent=deep_search_expert
    ))
    
    tasks.append(Task(
        description=f"""
        Проверь достоверность всей собранной информации о {target}:
        1. Проведи кросс-референсный анализ данных
        2. Подтверди информацию из множественных источников
        3. Выяви возможную дезинформацию
        4. Оцени надежность каждого источника
        """,
        expected_output="""Предоставь отчет о верификации, включающий:
        1. Подтвержденные данные с источниками
        2. Опровергнутую информацию
        3. Данные, требующие дополнительной проверки
        4. Оценку надежности источников""",
        agent=verification_expert
    ))
    
    return tasks

def run_osint_investigation(target: str):
    """Запускает OSINT-расследование"""
    try:
        investigation_id = f"osint_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        crew = Crew(
            agents=[
                lead_analyst,
                social_expert,
                technical_analyst,
                behavior_analyst,
                verification_expert,
                deep_search_expert,
                task_keeper,
                context_analyst
            ],
            tasks=create_investigation_plan(target),
            verbose=True,
            process=Process.hierarchical,
            manager_agent=manager_agent,
            memory=False,  
            planning=True
        )
        
        result = crew.kickoff()
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        os.makedirs('osint_results', exist_ok=True)
        
        with open(f'osint_results/investigation_{timestamp}.txt', 'w', encoding='utf-8') as f:
            f.write(f"OSINT Investigation Report\n")
            f.write("=" * 50 + "\n\n")
            f.write(f"Поставленная задача: {target}\n")
            f.write("=" * 50 + "\n\n")
            f.write(str(result))
        
        return result
        
    except Exception as e:
        print(f"Ошибка: {str(e)}")
        return None

def parse_osint_query(query: str) -> str:
    """Преобразует запрос в формате "Введите цель для OSINT: ..." в задачу для агентов"""
    if "Введите цель для OSINT:" in query:
        query = query.replace("Введите цель для OSINT:", "").strip()
    
    task_description = f"""
    Цель расследования: {query}
    
    Необходимо:
    1. Найти всю доступную информацию о цели
    2. Проверить указанные предположения о возрасте
    3. При наличии запроса - определить месяц рождения
    4. При наличии запроса - проверить присутствие на специализированных форумах
    
    Исходный запрос: {query}
    """
    
    return task_description

if __name__ == "__main__":
    query = input("Введите цель для OSINT: ")
    formatted_task = parse_osint_query(query)
    result = run_osint_investigation(formatted_task)
    if result:
        print("\nРезультаты расследования:")
        print(result)
