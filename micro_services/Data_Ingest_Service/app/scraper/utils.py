def deduplicate_urls(urls):
    return list(set(urls))


def batch_urls(urls, batch_size=200):
    for i in range(0, len(urls), batch_size):
        yield urls[i:i + batch_size]