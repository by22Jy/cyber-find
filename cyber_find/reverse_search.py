"""
Reverse Username Search Module - Search by partial match and patterns
"""

import re
from typing import Dict, List

from .models import SearchResult


class ReverseSearch:
    """Reverse search - by partial match and patterns"""

    @staticmethod
    def search_by_partial_match(
        username_pattern: str,
        all_results: List[SearchResult],
    ) -> List[SearchResult]:
        """
        Search by partial username match

        Args:
            username_pattern: Partial username (regex pattern)
            all_results: All search results

        Returns:
            Filtered results
        """
        pattern = re.compile(username_pattern, re.IGNORECASE)
        return [r for r in all_results if pattern.search(r.username or "")]

    @staticmethod
    def search_by_email_domain(
        domain: str,
        all_results: List[SearchResult],
    ) -> List[SearchResult]:
        """Search by email domain"""
        return [r for r in all_results if r.metadata and r.metadata.get("email_domain") == domain]

    @staticmethod
    def find_similar_usernames(
        username: str,
        all_usernames: List[str],
        threshold: float = 0.8,
    ) -> List[str]:
        """
        Find similar usernames (Levenshtein similarity)

        Args:
            username: Original username
            all_usernames: All available usernames
            threshold: Similarity threshold (0.8 = 80%)

        Returns:
            List of similar usernames
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
        """Search by profile URL pattern"""
        pattern = re.compile(url_pattern, re.IGNORECASE)
        return [r for r in all_results if pattern.search(r.url or "")]

    @staticmethod
    def find_cross_references(
        username: str,
        all_results: Dict[str, List[SearchResult]],
    ) -> Dict[str, List[SearchResult]]:
        """
        Find cross-references between different usernames
        (can help find alternate accounts of the same person)
        """
        cross_refs: Dict[str, List[SearchResult]] = {}

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
        """Search by pattern in profile metadata"""
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
        """Generate phone number variations for search"""
        # Удалить все нецифровые символы
        digits = re.sub(r"\D", "", phone)

        variations = [digits]

        # Add variations with different formats
        if len(digits) == 11:  # Russia +7
            variations.extend(
                [
                    digits[1:],  # Without country code
                    f"+7{digits[1:]}",  # With plus sign
                    f"8{digits[1:]}",  # With 8 prefix
                ]
            )
        elif len(digits) == 10:  # USA
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
        """Generate email variations for search"""
        if "@" not in email:
            return [email]

        username, domain = email.split("@", 1)
        variations = [email, username]

        # Add variations without dots
        variations.append(username.replace(".", ""))

        # Add variations with dots in different positions
        if "." in username:
            variations.append(username.replace(".", ""))

        return list(set(variations))
