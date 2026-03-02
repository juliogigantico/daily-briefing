CATEGORIES = {
    "international": {
        "title": "International & Geopolitics",
        "icon": "\U0001F310",
        "language": "en",
        "color": "#2C3E50",
        "max_articles": 5,
        "feeds": [
            # UK — public broadcaster, centrist
            {"name": "BBC World", "url": "https://feeds.bbci.co.uk/news/world/rss.xml"},
            # Qatar — strong Middle East / Global South perspective
            {"name": "Al Jazeera", "url": "https://www.aljazeera.com/xml/rss/all.xml"},
            # France — continental European, centrist
            {"name": "France 24", "url": "https://www.france24.com/en/rss"},
            # Germany — international edition, EU perspective
            {"name": "DW English", "url": "https://rss.dw.com/rdf/rss-en-all"},
            # US — public radio, center-left
            {"name": "NPR World", "url": "https://feeds.npr.org/1004/rss.xml"},
            # UK — left-liberal, strong investigative
            {"name": "The Guardian", "url": "https://www.theguardian.com/world/rss"},
            # US — deep geopolitical analysis, expert essays
            {"name": "Foreign Policy", "url": "https://foreignpolicy.com/feed/"},
            # US — security & defense analysis, realist lens
            {"name": "War on the Rocks", "url": "https://warontherocks.com/feed/"},
        ],
    },
    "environment": {
        "title": "Environment & Climate",
        "icon": "\U0001F33F",
        "language": "en",
        "color": "#27AE60",
        "max_articles": 5,
        "feeds": [
            # UK — climate science specialist, data-driven
            {"name": "Carbon Brief", "url": "https://www.carbonbrief.org/feed/"},
            # US — investigative climate journalism
            {"name": "Inside Climate News", "url": "https://insideclimatenews.org/feed/"},
            # UK — left-liberal, strong climate coverage
            {"name": "The Guardian", "url": "https://www.theguardian.com/environment/rss"},
            # EU — policy-focused, institutional perspective
            {"name": "EurActiv Climate", "url": "https://www.euractiv.com/sections/climate-environment/feed/"},
            # International — UN-adjacent, Global South voices
            {"name": "UN News Climate", "url": "https://news.un.org/feed/subscribe/en/news/topic/climate-change/feed/rss.xml"},
            # UK — public broadcaster, mainstream framing
            {"name": "BBC Environment", "url": "https://feeds.bbci.co.uk/news/science_and_environment/rss.xml"},
        ],
    },
    "tech": {
        "title": "Tech & AI",
        "icon": "\U0001F4BB",
        "language": "en",
        "color": "#8E44AD",
        "max_articles": 5,
        "feeds": [
            # US — VC/startup ecosystem, pro-industry
            {"name": "TechCrunch", "url": "https://techcrunch.com/feed/"},
            # US — deep technical, consumer tech focus
            {"name": "Ars Technica", "url": "https://feeds.arstechnica.com/arstechnica/index"},
            # US — consumer tech, accessible
            {"name": "The Verge", "url": "https://www.theverge.com/rss/index.xml"},
            # UK — public broadcaster, mainstream perspective
            {"name": "BBC Technology", "url": "https://feeds.bbci.co.uk/news/technology/rss.xml"},
            # US — community-driven, developer perspective (80+ upvotes only)
            {"name": "Hacker News", "url": "https://hnrss.org/frontpage?points=80&count=10"},
            # US/EU — digital rights, critical of big tech
            {"name": "EFF Deeplinks", "url": "https://www.eff.org/rss/updates.xml"},
            # Global — open access, AI research
            {"name": "MIT Tech Review", "url": "https://www.technologyreview.com/feed/"},
        ],
    },
    "economy": {
        "title": "Economy & Markets",
        "icon": "\U0001F4C8",
        "language": "en",
        "color": "#E67E22",
        "max_articles": 5,
        "feeds": [
            # UK — public broadcaster, centrist
            {"name": "BBC Business", "url": "https://feeds.bbci.co.uk/news/business/rss.xml"},
            # US — Wall Street perspective, pro-market
            {"name": "CNBC", "url": "https://search.cnbc.com/rs/search/combinedcms/view.xml?partnerId=wrss01&id=100003114"},
            # UK — global business establishment, center-right
            {"name": "Reuters Business", "url": "https://www.reutersagency.com/feed/?best-topics=business-finance&post_type=best"},
            # UK — free-market, globalist, analytical
            {"name": "The Economist", "url": "https://www.economist.com/finance-and-economics/rss.xml"},
            # US — financial establishment, center-right
            {"name": "Bloomberg", "url": "https://feeds.bloomberg.com/markets/news.rss"},
            # EU — European Central Bank / EU economy perspective
            {"name": "EurActiv Economy", "url": "https://www.euractiv.com/sections/economy-jobs/feed/"},
        ],
    },
    "science": {
        "title": "Science",
        "icon": "\U0001F52C",
        "language": "en",
        "color": "#2980B9",
        "max_articles": 5,
        "feeds": [
            # UK — top academic journal, peer-reviewed focus
            {"name": "Nature", "url": "https://www.nature.com/nature.rss"},
            # US — top academic journal, peer-reviewed focus
            {"name": "Science (AAAS)", "url": "https://www.science.org/rss/news_current.xml"},
            # US — accessible science journalism
            {"name": "Scientific American", "url": "https://rss.sciam.com/ScientificAmerican-Global"},
            # UK — public broadcaster, mainstream
            {"name": "BBC Science", "url": "https://feeds.bbci.co.uk/news/science_and_environment/rss.xml"},
            # US — space and physics focused
            {"name": "Space.com", "url": "https://www.space.com/feeds/all"},
            # UK — accessible, broad science
            {"name": "New Scientist", "url": "https://www.newscientist.com/section/news/feed/"},
        ],
    },
    "germany": {
        "title": "Deutschland & EU",
        "icon": "\U0001F1E9\U0001F1EA",
        "language": "de",
        "color": "#C0392B",
        "max_articles": 5,
        "feeds": [
            # Public broadcaster — centrist, factual
            {"name": "Tagesschau", "url": "https://www.tagesschau.de/xml/rss2/"},
            # Liberal, urban, left-of-center
            {"name": "ZEIT Online", "url": "https://newsfeed.zeit.de/index"},
            # Center-left, investigative
            {"name": "Spiegel", "url": "https://www.spiegel.de/schlagzeilen/index.rss"},
            # International edition, EU perspective
            {"name": "DW Deutsch", "url": "https://rss.dw.com/rdf/rss-de-all"},
            # Conservative-liberal, business-friendly
            {"name": "FAZ", "url": "https://www.faz.net/rss/aktuell/"},
            # Business-focused, center-right
            {"name": "Handelsblatt", "url": "https://www.handelsblatt.com/contentexport/feed/top-themen"},
        ],
    },
}
