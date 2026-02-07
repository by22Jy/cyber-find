"""
Account Age Detection Module - Определение возраста аккаунта
"""

from datetime import datetime
from typing import Dict, Optional

from .models import SearchResult


class AccountAgeDetector:
    """Определяет возраст аккаунта на основе доступных данных"""

    @staticmethod
    def estimate_account_age(result: SearchResult) -> Optional[Dict]:
        """
        Оценить возраст аккаунта на основе метаданных

        Args:
            result: Результат поиска с метаданными

        Returns:
            Словарь с информацией о возрасте аккаунта
        """
        if not result.metadata:
            return None

        metadata = result.metadata

        # Попытка найти дату создания в метаданных
        creation_date = metadata.get("created_at") or metadata.get("creation_date")

        if creation_date:
            try:
                if isinstance(creation_date, str):
                    # Попытка парсить различные форматы
                    for fmt in [
                        "%Y-%m-%d",
                        "%Y-%m-%dT%H:%M:%S",
                        "%d.%m.%Y",
                        "%d/%m/%Y",
                    ]:
                        try:
                            date_obj = datetime.strptime(creation_date, fmt)
                            break
                        except ValueError:
                            continue
                else:
                    date_obj = creation_date

                age = datetime.now() - date_obj
                return {
                    "created_at": creation_date,
                    "age_days": age.days,
                    "age_years": age.days / 365.25,
                    "age_months": age.days / 30.44,
                    "status": AccountAgeDetector._classify_age(age.days),
                }
            except (ValueError, TypeError):
                pass

        return None

    @staticmethod
    def _classify_age(days: int) -> str:
        """Классифицировать возраст аккаунта"""
        if days < 30:
            return "very_new"
        elif days < 90:
            return "new"
        elif days < 365:
            return "relatively_new"
        elif days < 1095:  # 3 года
            return "established"
        else:
            return "old"

    @staticmethod
    def detect_suspicious_activity(result: SearchResult) -> Dict:
        """
        Обнаружить подозрительную активность

        Returns:
            Словарь с индикаторами подозрительной активности
        """
        if not result.metadata:
            return {"suspicious": False, "indicators": []}

        indicators = []
        metadata = result.metadata

        # Очень новый аккаунт
        age_info = AccountAgeDetector.estimate_account_age(result)
        if age_info and age_info["status"] == "very_new":
            indicators.append("account_very_new")

        # Нет аватара/фото
        if not metadata.get("avatar_url") or not metadata.get("has_avatar"):
            indicators.append("no_avatar")

        # Минимальное количество постов
        post_count = metadata.get("post_count", 0)
        if isinstance(post_count, (int, float)) and post_count < 5:
            indicators.append("few_posts")

        # Минимальное количество фолловеров
        followers = metadata.get("followers", 0)
        if isinstance(followers, (int, float)) and followers < 10:
            indicators.append("few_followers")

        # Пустое описание профиля
        if not metadata.get("bio") or len(str(metadata.get("bio", ""))) < 3:
            indicators.append("empty_bio")

        # Профиль приватный
        if metadata.get("is_private"):
            indicators.append("private_profile")

        return {
            "suspicious": len(indicators) >= 3,
            "indicator_count": len(indicators),
            "indicators": indicators,
            "risk_level": ("high" if len(indicators) >= 4 else "medium" if len(indicators) >= 2 else "low"),
        }

    @staticmethod
    def analyze_account_timeline(
        results_by_date: Dict[str, SearchResult],
    ) -> Dict:
        """
        Анализировать временную шкалу аккаунта

        Args:
            results_by_date: Результаты поиска с датами

        Returns:
            Анализ активности во времени
        """
        if not results_by_date:
            return {}

        analysis = {
            "first_seen": None,
            "last_seen": None,
            "activity_days": 0,
            "average_posts_per_day": 0,
        }

        dates = []
        for date_str in results_by_date.keys():
            try:
                dates.append(datetime.fromisoformat(date_str))
            except ValueError:
                pass

        if dates:
            analysis["first_seen"] = min(dates).isoformat()
            analysis["last_seen"] = max(dates).isoformat()

            activity_span = max(dates) - min(dates)
            analysis["activity_days"] = activity_span.days

            if activity_span.days > 0:
                analysis["average_posts_per_day"] = len(results_by_date) / activity_span.days

        return analysis

    @staticmethod
    def compare_account_ages(accounts: Dict[str, SearchResult]) -> Dict:
        """
        Сравнить возраст нескольких аккаунтов

        Args:
            accounts: Словарь аккаунтов с их результатами

        Returns:
            Сравнительный анализ
        """
        ages = {}
        for name, result in accounts.items():
            age_info = AccountAgeDetector.estimate_account_age(result)
            if age_info:
                ages[name] = age_info

        if not ages:
            return {}

        # Отсортировать по возрасту
        sorted_ages = sorted(ages.items(), key=lambda x: x[1]["age_days"])

        return {
            "oldest": sorted_ages[-1] if sorted_ages else None,
            "newest": sorted_ages[0] if sorted_ages else None,
            "average_age_days": sum(a["age_days"] for a in ages.values()) / len(ages),
            "age_variance": (
                max(a["age_days"] for a in ages.values()) - min(a["age_days"] for a in ages.values()) if ages else 0
            ),
            "all_ages": ages,
        }

    @staticmethod
    def predict_next_activity(result: SearchResult) -> Optional[str]:
        """Предсказать следующую вероятную активность аккаунта"""
        if not result.metadata:
            return None

        age_info = AccountAgeDetector.estimate_account_age(result)
        if not age_info:
            return None

        status = age_info["status"]

        if status == "very_new":
            return "high_activity_expected"
        elif status == "new":
            return "activity_expected"
        elif status == "old":
            return "dormant_or_stable"
        else:
            return "unclear"
