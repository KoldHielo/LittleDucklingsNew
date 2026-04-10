from datetime import datetime, timezone
from pathlib import Path

from django.conf import settings
from django.contrib.sitemaps import Sitemap
from django.urls import reverse


def latest_file_modified(*relative_paths: str):
    timestamps = []

    for relative_path in relative_paths:
        file_path = Path(settings.BASE_DIR, relative_path)

        if file_path.exists():
            timestamps.append(datetime.fromtimestamp(file_path.stat().st_mtime, tz=timezone.utc))

    return max(timestamps) if timestamps else None


class PublicPageSitemap(Sitemap):
    protocol = 'https'

    pages = {
        'home': {
            'changefreq': 'weekly',
            'priority': 1.0,
            'files': (
                'main/templates/base.html',
                'main/templates/home.html',
            ),
        },
        'gallery': {
            'changefreq': 'monthly',
            'priority': 0.8,
            'files': (
                'main/templates/base.html',
                'main/templates/gallery.html',
            ),
        },
        'policy_menu': {
            'changefreq': 'monthly',
            'priority': 0.8,
            'files': (
                'main/templates/base.html',
                'main/templates/policy_menu.html',
            ),
        },
    }

    def items(self):
        return list(self.pages.keys())

    def location(self, item):
        return reverse(item)

    def changefreq(self, item):
        return self.pages[item]['changefreq']

    def priority(self, item):
        return self.pages[item]['priority']

    def lastmod(self, item):
        return latest_file_modified(*self.pages[item]['files'])


class PolicyPageSitemap(Sitemap):
    protocol = 'https'
    changefreq = 'yearly'
    priority = 0.7

    def items(self):
        policy_template_dir = Path(settings.BASE_DIR, 'main/templates/policies')

        return sorted(
            template_path.stem
            for template_path in policy_template_dir.glob('*.html')
            if template_path.stem != 'base'
        )

    def location(self, item):
        return reverse('get_policy', kwargs={'policy_slug': item})

    def lastmod(self, item):
        return latest_file_modified(
            'main/templates/base.html',
            'main/templates/policies/base.html',
            f'main/templates/policies/{item}.html',
        )
