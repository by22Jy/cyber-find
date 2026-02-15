"""
Detailed Reports Module - Создание красивых отчётов
"""

import json
from datetime import datetime
from typing import Dict, List, Optional

from .models import SearchResult


class ReportGenerator:
    """Генерирует красивые и информативные отчёты в разных форматах"""

    @staticmethod
    def generate_html_report(
        username: str,
        results: List[SearchResult],
        output_file: str,
        title: Optional[str] = None,
    ) -> str:
        """
        Генерировать красивый HTML отчёт

        Args:
            username: Юзернейм для анализа
            results: Результаты поиска
            output_file: Путь для сохранения HTML
            title: Заголовок отчёта

        Returns:
            Путь к сохранённому файлу
        """
        if title is None:
            title = f"Отчёт поиска: {username}"

        found = [r for r in results if r.found]
        not_found = [r for r in results if not r.found]

        html = f"""
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            min-height: 100vh;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 10px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
            overflow: hidden;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }}
        .header h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
        }}
        .header p {{
            font-size: 1.1em;
            opacity: 0.9;
        }}
        .stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            padding: 30px;
            background: #f8f9fa;
        }}
        .stat-card {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            text-align: center;
        }}
        .stat-card .number {{
            font-size: 2.5em;
            font-weight: bold;
            color: #667eea;
            margin-bottom: 10px;
        }}
        .stat-card .label {{
            color: #666;
            font-size: 0.95em;
        }}
        .results {{
            padding: 30px;
        }}
        .results-section {{
            margin-bottom: 40px;
        }}
        .results-section h2 {{
            border-bottom: 3px solid #667eea;
            padding-bottom: 10px;
            margin-bottom: 20px;
            color: #333;
        }}
        .result-item {{
            background: #f8f9fa;
            padding: 15px;
            margin-bottom: 15px;
            border-radius: 8px;
            border-left: 4px solid #667eea;
        }}
        .result-item.not-found {{
            border-left-color: #ccc;
        }}
        .result-item h3 {{
            color: #667eea;
            margin-bottom: 8px;
        }}
        .result-item a {{
            color: #667eea;
            text-decoration: none;
        }}
        .result-item a:hover {{
            text-decoration: underline;
        }}
        .result-meta {{
            font-size: 0.9em;
            color: #666;
            margin-top: 10px;
        }}
        .footer {{
            background: #f8f9fa;
            padding: 20px;
            text-align: center;
            border-top: 1px solid #ddd;
            color: #666;
            font-size: 0.9em;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>{title}</h1>
            <p>Дата отчёта: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}</p>
        </div>

        <div class="stats">
            <div class="stat-card">
                <div class="number">{len(results)}</div>
                <div class="label">Всего сайтов</div>
            </div>
            <div class="stat-card">
                <div class="number">{len(found)}</div>
                <div class="label">Найдено профилей</div>
            </div>
            <div class="stat-card">
                <div class="number">{len(not_found)}</div>
                <div class="label">Не найдено</div>
            </div>
            <div class="stat-card">
                <div class="number">{(len(found) / len(results) * 100):.1f}%</div>
                <div class="label">Процент совпадений</div>
            </div>
        </div>

        <div class="results">
"""

        # Добавить найденные профили
        if found:
            html += '<div class="results-section">\n'
            html += f"<h2>✓ Найдено профилей ({len(found)})</h2>\n"

            for result in found:
                html += f"""
            <div class="result-item">
                <h3>{result.site_name}</h3>
                <a href="{result.url}" target="_blank">{result.url}</a>
                <div class="result-meta">
                    Статус: {result.status_code} |
                    Уверенность: {(result.confidence or 0) * 100:.0f}%
                </div>
            </div>
"""
            html += "</div>\n"

        # Добавить ненайденные профили
        if not_found:
            html += '<div class="results-section">\n'
            html += f"<h2>✗ Не найдено ({len(not_found)})</h2>\n"

            for result in not_found:
                html += f"""
            <div class="result-item not-found">
                <h3>{result.site_name}</h3>
                <div class="result-meta">Аккаунт не найден на этом сайте</div>
            </div>
"""
            html += "</div>\n"

        html += """
        </div>

        <div class="footer">
            <p>Отчёт создан с помощью CyberFind v0.2.2</p>
        </div>
    </div>
</body>
</html>
"""

        with open(output_file, "w", encoding="utf-8") as f:
            f.write(html)

        return output_file

    @staticmethod
    def generate_json_report(
        username: str,
        results: List[SearchResult],
        output_file: str,
    ) -> str:
        """
        Генерировать JSON отчёт для программной обработки

        Args:
            username: Юзернейм для анализа
            results: Результаты поиска
            output_file: Путь для сохранения JSON

        Returns:
            Путь к сохранённому файлу
        """
        found = [r for r in results if r.found]

        report = {
            "username": username,
            "timestamp": datetime.now().isoformat(),
            "statistics": {
                "total_sites": len(results),
                "found_count": len(found),
                "not_found_count": len(results) - len(found),
                "success_rate": (len(found) / len(results) * 100) if results else 0,
                "average_confidence": (
                    sum(r.confidence or 0 for r in found) / len(found) if found else 0
                ),
            },
            "results": [
                {
                    "site_name": r.site_name,
                    "url": r.url,
                    "found": r.found,
                    "status_code": r.status_code,
                    "confidence": r.confidence,
                    "category": r.category,
                    "metadata": r.metadata,
                }
                for r in results
            ],
        }

        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2)

        return output_file

    @staticmethod
    def generate_csv_report(
        username: str,
        results: List[SearchResult],
        output_file: str,
    ) -> str:
        """
        Генерировать CSV отчёт для Excel

        Args:
            username: Юзернейм для анализа
            results: Результаты поиска
            output_file: Путь для сохранения CSV

        Returns:
            Путь к сохранённому файлу
        """
        import csv

        with open(output_file, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)

            # Заголовки
            writer.writerow(
                [
                    "Сайт",
                    "URL",
                    "Найден",
                    "Статус",
                    "Уверенность %",
                    "Категория",
                    "Дата поиска",
                ]
            )

            # Данные
            for result in results:
                writer.writerow(
                    [
                        result.site_name,
                        result.url or "",
                        "Да" if result.found else "Нет",
                        result.status_code or "",
                        (result.confidence or 0) * 100,
                        result.category or "",
                        datetime.now().strftime("%d.%m.%Y %H:%M:%S"),
                    ]
                )

        return output_file

    @staticmethod
    def generate_summary_report(
        results: Dict[str, List[SearchResult]],
        output_file: str,
    ) -> str:
        """
        Генерировать сводный отчёт по нескольким юзернеймам

        Args:
            results: Словарь результатов (username -> results)
            output_file: Путь для сохранения отчёта

        Returns:
            Путь к сохранённому файлу
        """
        html = """
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <title>Сводный отчёт</title>
    <style>
        body {
            font-family: 'Segoe UI', sans-serif;
            background: #f5f5f5;
            padding: 20px;
        }
        .summary-table {
            background: white;
            border-collapse: collapse;
            width: 100%;
            max-width: 800px;
            margin: 20px auto;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            border-radius: 8px;
            overflow: hidden;
        }
        .summary-table th {
            background: #667eea;
            color: white;
            padding: 15px;
            text-align: left;
        }
        .summary-table td {
            padding: 15px;
            border-bottom: 1px solid #eee;
        }
        .summary-table tr:hover {
            background: #f8f9fa;
        }
    </style>
</head>
<body>
    <h1 style="text-align: center; color: #333;">Сводный отчёт поиска</h1>
    <table class="summary-table">
        <thead>
            <tr>
                <th>Юзернейм</th>
                <th>Всего сайтов</th>
                <th>Найдено</th>
                <th>% совпадений</th>
            </tr>
        </thead>
        <tbody>
"""

        for username, search_results in results.items():
            found_count = len([r for r in search_results if r.found])
            total_count = len(search_results)
            success_rate = (found_count / total_count * 100) if total_count > 0 else 0

            html += f"""
            <tr>
                <td><strong>{username}</strong></td>
                <td>{total_count}</td>
                <td>{found_count}</td>
                <td>{success_rate:.1f}%</td>
            </tr>
"""

        html += """
        </tbody>
    </table>
</body>
</html>
"""

        with open(output_file, "w", encoding="utf-8") as f:
            f.write(html)

        return output_file
