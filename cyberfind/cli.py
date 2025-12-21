#!/usr/bin/env python3

import argparse
import asyncio
import sys
import os

# Исправляем путь для импорта
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

try:
    from cyberfind import CyberFind, SearchMode, OutputFormat
    from cyberfind import run_gui, run_api_server
except ImportError as e:
    print(f"Import error: {e}")
    print("Trying alternative import...")
    # Альтернативный импорт
    sys.path.insert(0, os.path.join(current_dir, 'cyberfind'))
    from core import CyberFind, SearchMode, OutputFormat
    from gui import run_gui
    from api import run_api_server

def show_builtin_lists(cybertrace):
    """Показать доступные встроенные списки"""
    print("\n📚 AVAILABLE BUILT-IN SITE LISTS:")
    print("=" * 50)
    
    categories = cybertrace.list_builtin_categories()
    for name, count in sorted(categories.items(), key=lambda x: x[1], reverse=True):
        print(f"  {name:15} - {count:3d} sites")
    
    print("\nUsage examples:")
    print("  cyberfind username --list quick")
    print("  cyberfind username --list social_media")
    print("  cyberfind username --list all")
    print("\nOr use from file:")
    print("  cyberfind username -f sites/social_media.txt")

def main():
    parser = argparse.ArgumentParser(
        description='CyberFind - Advanced OSINT search tool',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Использовать встроенные списки:
  cyberfind username
  cyberfind username --list quick
  cyberfind username --list social_media
  cyberfind username --list programming
  cyberfind username --list all
  
  # Использовать файл:
  cyberfind username -f sites/social_media.txt
  
  # Другие опции:
  cyberfind username --mode deep --format html -o report
  cyberfind username --format csv --threads 50
        """
    )
    
    parser.add_argument(
        'usernames',
        nargs='+',
        help='Usernames to search'
    )
    
    parser.add_argument(
        '-f', '--file',
        help='File with sites list'
    )
    
    parser.add_argument(
        '-l', '--list',
        choices=['quick', 'social_media', 'programming', 'gaming', 
                'blogs', 'ecommerce', 'forums', 'russian', 'all'],
        help='Use built-in site list'
    )
    
    parser.add_argument(
        '--mode',
        choices=[m.value for m in SearchMode],
        default='standard',
        help='Search mode'
    )
    
    parser.add_argument(
        '--format',
        choices=[f.value for f in OutputFormat],
        default='json',
        help='Output format'
    )
    
    parser.add_argument(
        '-o', '--output',
        help='Output file name'
    )
    
    parser.add_argument(
        '-t', '--threads',
        type=int,
        default=20,
        help='Number of threads'
    )
    
    parser.add_argument(
        '--timeout',
        type=int,
        default=10,
        help='Request timeout'
    )
    
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Verbose output'
    )
    
    parser.add_argument(
        '--show-lists',
        action='store_true',
        help='Show available built-in site lists'
    )
    
    parser.add_argument(
        '--gui',
        action='store_true',
        help='Start GUI'
    )
    
    parser.add_argument(
        '--api',
        action='store_true',
        help='Start API server'
    )
    
    parser.add_argument(
        '--config',
        default='config.yaml',
        help='Config file path'
    )
    
    args = parser.parse_args()
    
    if args.gui:
        run_gui()
    elif args.api:
        run_api_server()
    elif args.show_lists:
        cybertrace = CyberFind(args.config)
        show_builtin_lists(cybertrace)
    else:
        print(f"🔍 CyberFind v0.1.0")
        print(f"Searching for: {', '.join(args.usernames)}")
        
        cybertrace = CyberFind(args.config)
        
        # Показать информацию о списке сайтов
        if args.list:
            sites_count = len(cybertrace.get_builtin_site_list(args.list))
            print(f"Using built-in list: {args.list} ({sites_count} sites)")
        elif args.file:
            print(f"Using sites file: {args.file}")
        else:
            sites_count = len(cybertrace.get_builtin_site_list('quick'))
            print(f"Using default list: quick ({sites_count} sites)")
        
        # Обновляем конфиг с аргументами командной строки
        if args.timeout:
            cybertrace.config['general']['timeout'] = args.timeout
        
        try:
            print("Starting search...\n")
            
            # Добавляем обработку Ctrl+C
            async def search_with_progress():
                import time
                start_time = time.time()
                
                try:
                    # Определяем источник сайтов
                    sites_file = args.file
                    builtin_list = args.list
                    
                    results = await cybertrace.search_async(
                        usernames=args.usernames,
                        sites_file=sites_file,
                        builtin_list=builtin_list,
                        mode=SearchMode(args.mode),
                        output_format=OutputFormat(args.format),
                        output_file=args.output,
                        max_concurrent=args.threads
                    )
                    
                    end_time = time.time()
                    total_time = end_time - start_time
                    
                    print(f"\n{'='*60}")
                    print(f"✅ SEARCH COMPLETED in {total_time:.1f} seconds")
                    print(f"{'='*60}")
                    
                    if 'statistics' in results:
                        stats = results['statistics']
                        print(f"📊 STATISTICS:")
                        print(f"  Total checks: {stats.get('total_checks', 0)}")
                        print(f"  Accounts found: {stats.get('found_accounts', 0)}")
                        print(f"  Errors: {stats.get('errors', 0)}")
                    
                    if 'results' in results:
                        for username, data in results['results'].items():
                            print(f"\n👤 {username}:")
                            if data and 'found' in data and data['found']:
                                print(f"  ✅ FOUND {len(data['found'])} accounts:")
                                for i, account in enumerate(data['found'], 1):
                                    print(f"    {i:2d}. {account['site']}: {account['url']}")
                            else:
                                print(f"  ❌ No accounts found")
                            
                            if data and 'errors' in data and data['errors'] and args.verbose:
                                print(f"  ⚠️  Errors: {len(data['errors'])}")
                                for error in data['errors'][:3]:  # Показываем только первые 3 ошибки
                                    print(f"      • {error.get('site', 'Unknown')}: {error.get('error', 'Unknown error')}")
                    
                    if args.output and 'results' in results:
                        print(f"\n💾 Results saved to: {args.output}")
                    
                    return results
                    
                except asyncio.CancelledError:
                    print("\n⚠️ Search cancelled by user")
                    raise
                except Exception as e:
                    print(f"\n❌ Error during search: {e}")
                    raise
            
            # Запускаем с обработкой прерывания
            try:
                results = asyncio.run(search_with_progress())
            except KeyboardInterrupt:
                print("\n\n⏹️ Search interrupted by user")
            except Exception as e:
                print(f"\n❌ Fatal error: {e}")
        
        except KeyboardInterrupt:
            print("\n\n⏹️ Search interrupted by user")
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()