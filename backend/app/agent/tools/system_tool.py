import webbrowser
import urllib.parse

KNOWN_SITES = {
    'youtube': 'https://youtube.com',
    'google': 'https://google.com',
    'gmail': 'https://mail.google.com',
    'github': 'https://github.com',
    'chatgpt': 'https://chat.openai.com',
    'claude': 'https://claude.ai',
    'netflix': 'https://netflix.com',
    'spotify': 'https://open.spotify.com',
    'whatsapp': 'https://web.whatsapp.com',
    'twitter': 'https://twitter.com',
    'x': 'https://twitter.com',
    'facebook': 'https://facebook.com',
    'instagram': 'https://instagram.com',
    'linkedin': 'https://linkedin.com',
    'reddit': 'https://reddit.com',
    'amazon': 'https://amazon.com',
    'wikipedia': 'https://wikipedia.org',
    'stackoverflow': 'https://stackoverflow.com',
    'supabase': 'https://supabase.com/dashboard',
    'railway': 'https://railway.app',
    'vercel': 'https://vercel.com',
}


def open_website(site_or_url: str) -> dict:
    """
    Open a website in the default browser.
    Supports: known site names, full URLs, "search <query> on youtube",
    or general queries (defaults to Google search).
    """
    try:
        query = site_or_url.strip()
        query_lower = query.lower()

        # Pattern: "<query> on youtube" or "youtube <query>" or "search youtube for <query>"
        if 'youtube' in query_lower and query_lower != 'youtube':
            search_term = (
                query_lower
                .replace('on youtube', '')
                .replace('youtube search', '')
                .replace('search youtube for', '')
                .replace('search youtube', '')
                .replace('youtube', '')
                .strip()
            )
            if search_term:
                encoded = urllib.parse.quote(search_term)
                url = f'https://www.youtube.com/results?search_query={encoded}'
                webbrowser.open(url)
                return {'success': True, 'url': url}

        if query_lower in KNOWN_SITES:
            url = KNOWN_SITES[query_lower]
        elif query_lower.startswith('http://') or query_lower.startswith('https://'):
            url = query
        elif '.' in query_lower and ' ' not in query_lower:
            url = f'https://{query_lower}'
        else:
            encoded = urllib.parse.quote(query)
            url = f'https://www.google.com/search?q={encoded}'

        webbrowser.open(url)
        return {'success': True, 'url': url}

    except Exception as e:
        return {'success': False, 'error': str(e)}