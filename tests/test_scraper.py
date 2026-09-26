import pytest
from modules.scraper import NyaaScraper

# Mock data for feedparser items
MOCK_ITEMS = [
    {
        'title': '[SubsPlease] Oshi no Ko - 14 (1080p) [F1B5C3D2].mkv',
        'link': 'https://nyaa.si/download/12345.torrent',
        'nyaa_infohash': 'abcdef123456'
    },
    {
        'title': '[HorribleSubs] Old Anime - 01 (1080p).mkv',
        'link': 'https://nyaa.si/download/67890.torrent',
        'nyaa_infohash': '123456abcdef'
    },
    {
        'title': '[Erai-raws] Jujutsu Kaisen - 40 [1080p][Multiple Subtitle].mkv',
        'link': 'https://nyaa.si/download/11111.torrent',
        'nyaa_infohash': '999999999999'
    }
]

def test_scraper_filtering():
    """Test if NyaaScraper correctly filters out unwanted groups."""
    scraper = NyaaScraper(target_groups=['[SubsPlease]', '[Erai-raws]'])
    
    filtered = scraper.filter_items(MOCK_ITEMS)
    
    assert len(filtered) == 2
    assert "SubsPlease" in filtered[0]['title']
    assert "Erai-raws" in filtered[1]['title']

def test_scraper_no_matches():
    """Test filtering when no target groups match."""
    scraper = NyaaScraper(target_groups=['[SomeUnknownGroup]'])
    
    filtered = scraper.filter_items(MOCK_ITEMS)
    
    assert len(filtered) == 0
