"""
Detailed Reports Module - Generate beautiful reports
"""

import json
from datetime import datetime
from typing import Dict, List, Optional

from .models import SearchResult


class ReportGenerator:
    """Generates beautiful and informative reports in various formats"""

    @staticmethod
    def generate_html_report(
        username: str,
        results: List[SearchResult],
        output_file: str,
        title: Optional[str] = None,
    ) -> str:
        """
        Generate beautiful HTML report

        Args:
            username: Username for analysis
            results: Search results
            output_file: Path to save HTML
            title: Report title

        Returns:
            Path to saved file
        """
        if title is None:
            title = f"Search Report: {username}"

        found = [r for r in results if r.found]
        not_found = [r for r in results if not r.found]

        html = f"""
<!DOCTYPE html>
<html lang="en">
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
            <p>Report date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>

        <div class="stats">
            <div class="stat-card">
                <div class="number">{len(results)}</div>
                <div class="label">Total sites</div>
            </div>
            <div class="stat-card">
                <div class="number">{len(found)}</div>
                <div class="label">Profiles found</div>
            </div>
            <div class="stat-card">
                <div class="number">{len(not_found)}</div>
                <div class="label">Not found</div>
            </div>
            <div class="stat-card">
                <div class="number">{(len(found) / len(results) * 100):.1f}%</div>
                <div class="label">Match rate</div>
            </div>
        </div>

        <div class="results">
"""

        # Add found profiles
        if found:
            html += '<div class="results-section">\n'
            html += f"<h2>✓ Profiles found ({len(found)})</h2>\n"

            for result in found:
                html += f"""
            <div class="result-item">
                <h3>{result.site_name}</h3>
                <a href="{result.url}" target="_blank">{result.url}</a>
                <div class="result-meta">
                    Status: {result.status_code} |
                    Confidence: {(result.confidence or 0) * 100:.0f}%
                </div>
            </div>
"""
            html += "</div>\n"

        # Add not found profiles
        if not_found:
            html += '<div class="results-section">\n'
            html += f"<h2>✗ Not found ({len(not_found)})</h2>\n"

            for result in not_found:
                html += f"""
            <div class="result-item not-found">
                <h3>{result.site_name}</h3>
                <div class="result-meta">Account not found on this site</div>
            </div>
"""
            html += "</div>\n"

        html += """
        </div>

        <div class="footer">
            <p>Report generated by CyberFind v0.3.4</p>
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
        Generate JSON report for programmatic processing

        Args:
            username: Username for analysis
            results: Search results
            output_file: Path to save JSON

        Returns:
            Path to saved file
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
        Generate CSV report for Excel

        Args:
            username: Username for analysis
            results: Search results
            output_file: Path to save CSV

        Returns:
            Path to saved file
        """
        import csv

        with open(output_file, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)

            # Headers
            writer.writerow(
                [
                    "Site",
                    "URL",
                    "Found",
                    "Status",
                    "Confidence %",
                    "Category",
                    "Search Date",
                ]
            )

            # Данные
            for result in results:
                writer.writerow(
                    [
                        result.site_name,
                        result.url or "",
                        "Yes" if result.found else "No",
                        result.status_code or "",
                        (result.confidence or 0) * 100,
                        result.category or "",
                        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    ]
                )

        return output_file

    @staticmethod
    def generate_summary_report(
        results: Dict[str, List[SearchResult]],
        output_file: str,
    ) -> str:
        """
        Generate summary report for multiple usernames

        Args:
            results: Dictionary of results (username -> results)
            output_file: Path to save report

        Returns:
            Path to saved file
        """
        html = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Summary Report</title>
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
    <h1 style="text-align: center; color: #333;">Search Summary Report</h1>
    <table class="summary-table">
        <thead>
            <tr>
                <th>Username</th>
                <th>Total Sites</th>
                <th>Found</th>
                <th>Match Rate</th>
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
