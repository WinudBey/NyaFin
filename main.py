import argparse
import sys
from core.logger import get_logger
from pipeline import Pipeline

logger = get_logger("main")

def main():
    parser = argparse.ArgumentParser(description="NyaFin - Anime Otomasyon İş Akışı")
    parser.add_argument('--auto', action='store_true', help='RSS üzerinden otomatik çalıştır')
    parser.add_argument('--url', type=str, help='Manuel indirmek için Torrent/Magnet URL')
    
    args = parser.parse_args()
    
    if not args.auto and not args.url:
        parser.print_help()
        sys.exit(1)
        
    logger.info("NyaFin Başlatılıyor...")
    pipe = Pipeline()
    
    if args.auto:
        pipe.run_auto()
    elif args.url:
        pipe.run_manual(args.url)
        
    logger.info("İşlem tamamlandı.")

if __name__ == "__main__":
    main()
