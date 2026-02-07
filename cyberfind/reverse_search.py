"""
Reverse Username Search Module - Поиск по частичному совпадению и паттернам
"""

import re
from typing import Dict, List

from .models import SearchResult


class ReverseSearch:
    """Обратный поиск - по частичному совпадению и паттернам"""

    @staticmethod
    def search_by_partial_match(
        username_pattern: str,
        all_results: List[SearchResult],
    ) -> List[SearchResult]:
        """
        Поиск по частичному совпадению юзернейма

        Args:
            username_pattern: Часть юзернейма (регулярное выражение)
            all_results: Все результаты поиска

        Returns:
            Отфильтрованные результаты
        """
        pattern = re.compile(username_pattern, re.IGNORECASE)
        return [r for r in all_results if pattern.search(r.username or "")]

    @staticmethod
    def search_by_email_domain(
        domain: str,
        all_results: List[SearchResult],
    ) -> List[SearchResult]:
        """Поиск по домену email'а"""
        return [r for r in all_results if r.metadata and r.metadata.get("email_domain") == domain]

    @staticmethod
    def find_similar_usernames(
        username: str,
        all_usernames: List[str],
        threshold: float = 0.8,
    ) -> List[str]:
        """
        Найти похожие юзернеймы (похожесть Левенштейна)

        Args:
            username: Исходный юзернейм
            all_usernames: Все доступные юзернеймы
            threshold: Порог похожести (0.8 = 80%)

        Returns:
            Список похожих юзернеймов
        """
        from difflib import SequenceMatcher

        similar = []
        for name in all_usernames:
            ratio = SequenceMatcher(None, username.lower(), name.lower()).ratio()
            if ratio >= threshold:
                similar.append(name)
        return similar

    @staticmethod
    def search_by_profile_url(
        url_pattern: str,
        all_results: List[SearchResult],
    ) -> List[SearchResult]:
        """Поиск по паттерну URL профиля"""
        pattern = re.compile(url_pattern, re.IGNORECASE)
        return [r for r in all_results if pattern.search(r.url or "")]

    @staticmethod
    def find_cross_references(
        username: str,
        all_results: Dict[str, List[SearchResult]],
    ) -> Dict[str, List[SearchResult]]:
        """
        Найти кросс-ссылки между разными юзернеймами
        (может помочь найти альты одного человека)
        """
        cross_refs = {}

        for user, results in all_results.items():
            for result in results:
                # Проверить наличие исходного юзернейма в метаданных профиля
                if result.metadata:
                    metadata_text = str(result.metadata).lower()
                    if username.lower() in metadata_text:
                        if user not in cross_refs:
                            cross_refs[user] = []
                        cross_refs[user].append(result)

        return cross_refs

    @staticmethod
    def find_by_metadata_pattern(
        pattern: str,
        all_results: List[SearchResult],
    ) -> List[SearchResult]:
        """Поиск по паттерну в метаданных профиля"""
        regex = re.compile(pattern, re.IGNORECASE)
        results = []

        for result in all_results:
            if result.metadata:
                metadata_str = str(result.metadata)
                if regex.search(metadata_str):
                    results.append(result)

        return results

    @staticmethod
    def find_phone_variations(
        phone: str,
    ) -> List[str]:
        """Генерировать вариации номера телефона для поиска"""
        # Удалить все нецифровые символы
        digits = re.sub(r"\D", "", phone)

        variations = [digits]

        # Добавить вариации с разными форматами
        if len(digits) == 11:  # Россия +7
            variations.extend(
                [
                    digits[1:],  # Без страны
                    f"+7{digits[1:]}",  # С плюсом
                    f"8{digits[1:]}",  # С 8
                ]
            )
        elif len(digits) == 10:  # США
            variations.extend(
                [
                    f"+1{digits}",
                    f"({digits[:3]}) {digits[3:6]}-{digits[6:]}",
                ]
            )

        return list(set(variations))

    @staticmethod
    def find_email_variations(
        email: str,
    ) -> List[str]:
        """Генерировать вариации email для поиска"""
        if "@" not in email:
            return [email]

        username, domain = email.split("@", 1)
        variations = [email, username]

        # Добавить вариации без точек
        variations.append(username.replace(".", ""))

        # Добавить вариации с точками в разных местах
        if "." in username:
            variations.append(username.replace(".", ""))

        return list(set(variations))
