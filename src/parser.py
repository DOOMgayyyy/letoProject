import asyncio
import json
import random
import httpx
from bs4 import BeautifulSoup

class MaximJokesParser:
    """
    Улучшенный парсер для сбора анекдотов с сайта maximonline.ru.
    Корректно обрабатывает анекдоты, разделенные на несколько абзацев.
    """
    def __init__(self):
        # URL страницы с анекдотами
        self.base_url = 'https://www.maximonline.ru/entertainment/100-luchshikh-anekdotov-za-desyat-let-2010-2019-id476643/'
        # Файл для сохранения результата
        self.output_file = 'jokes.json'
        # Заголовки для имитации запроса от браузера
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

    async def fetch_html(self, client: httpx.AsyncClient) -> str | None:
        """Асинхронно загружает HTML-содержимое страницы."""
        print(f"⏳ Загружаю страницу: {self.base_url}")
        try:
            # Небольшая случайная задержка перед запросом
            await asyncio.sleep(random.uniform(0.5, 1.5))
            response = await client.get(self.base_url, timeout=20)
            # Проверка на ошибки HTTP (4xx или 5xx)
            response.raise_for_status()
            print("✅ Страница успешно загружена.")
            return response.text
        except httpx.RequestError as e:
            print(f"🚫 Ошибка при загрузке {e.request.url}: {str(e)}")
            return None
        except httpx.HTTPStatusError as e:
            print(f"🚫 Ошибка статуса {e.response.status_code} для {e.request.url}: {str(e)}")
            return None

    def parse_jokes(self, html: str) -> list[str]:
        """
        Извлекает тексты анекдотов из HTML, объединяя многострочные.
        """
        print("🔍 Начинаю парсинг анекдотов...")
        soup = BeautifulSoup(html, 'html.parser')
        jokes = []
        # Находим все родительские div-контейнеры, в которых лежат анекдоты
        joke_containers = soup.find_all('div', class_='ds-article-content__block_text')

        for container in joke_containers:
            # Внутри каждого контейнера ищем ВСЕ теги <p>
            p_tags = container.find_all('p')
            
            # Собираем непустые строки из всех найденных тегов <p>
            joke_lines = [p.get_text(strip=True) for p in p_tags if p.get_text(strip=True)]
            
            if joke_lines:
                # Объединяем строки в один анекдот с переносами
                full_joke_text = '\n'.join(joke_lines)
                jokes.append(full_joke_text)

        if jokes:
            print(f"👍 Найдено анекдотов: {len(jokes)}")
        else:
            print("⚠️ Анекдоты не найдены. Возможно, изменилась структура сайта.")

        return jokes

    def save_to_json(self, jokes: list[str]):
        """Сохраняет список анекдотов в JSON-файл в нужном формате."""
        if not jokes:
            print("💾 Сохранять нечего, список анекдотов пуст.")
            return

        print(f"💾 Сохраняю анекдоты в файл '{self.output_file}'...")
        # Формируем структуру данных согласно требованиям
        formatted_jokes = [
            {"id": i + 1, "text": text} for i, text in enumerate(jokes)
        ]

        try:
            with open(self.output_file, 'w', encoding='utf-8') as f:
                json.dump(formatted_jokes, f, ensure_ascii=False, indent=2)
            print(f"🎉 Готово! Файл '{self.output_file}' успешно создан/обновлен.")
        except IOError as e:
            print(f"🚫 Не удалось записать в файл '{self.output_file}': {e}")

    async def run(self):
        """Основной метод для запуска всего процесса."""
        async with httpx.AsyncClient(headers=self.headers) as client:
            html = await self.fetch_html(client)
            if html:
                jokes = self.parse_jokes(html)
                self.save_to_json(jokes)


if __name__ == '__main__':
    # Запускаем парсер
    parser = MaximJokesParser()
    asyncio.run(parser.run())

