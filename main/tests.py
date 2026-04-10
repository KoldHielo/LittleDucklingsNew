from pathlib import Path
from xml.etree import ElementTree

from django.conf import settings
from django.test import TestCase
from django.urls import reverse


class SitemapTests(TestCase):
    def test_sitemap_includes_public_pages_and_policies_only(self):
        response = self.client.get(reverse('sitemap'))

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response['Content-Type'].startswith('application/xml'))

        root = ElementTree.fromstring(response.content)
        namespace = {'sm': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
        locations = {
            element.text
            for element in root.findall('sm:url/sm:loc', namespace)
        }

        policy_template_dir = Path(settings.BASE_DIR, 'main/templates/policies')
        policy_urls = {
            f'https://testserver/policies/{template_path.stem}/'
            for template_path in policy_template_dir.glob('*.html')
            if template_path.stem != 'base'
        }

        expected_urls = {
            'https://testserver/',
            'https://testserver/gallery/',
            'https://testserver/policies/',
            *policy_urls,
        }

        self.assertSetEqual(locations, expected_urls)
        self.assertNotIn('https://testserver/login/', locations)
        self.assertNotIn('https://testserver/password-reset/', locations)

    def test_robots_txt_references_sitemap_and_disallows_private_routes(self):
        response = self.client.get(reverse('robots'))

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response['Content-Type'].startswith('text/plain'))

        body = response.content.decode()

        self.assertIn('User-agent: *', body)
        self.assertIn('Allow: /', body)
        self.assertIn('Disallow: /admin/', body)
        self.assertIn('Disallow: /login/', body)
        self.assertIn('Disallow: /parent_dashboard/', body)
        self.assertIn(f'Sitemap: {settings.SITE_URL}/sitemap.xml', body)


class SeoMetadataTests(TestCase):
    def test_gallery_page_has_location_focused_title_and_canonical(self):
        response = self.client.get(reverse('gallery'))

        self.assertEqual(response.status_code, 200)

        body = response.content.decode()

        self.assertIn(
            '<title>Childminding Gallery in Baddeley Green, Stoke-on-Trent | Little Ducklings Childminding</title>',
            body,
        )
        self.assertIn(
            '<link rel="canonical" href="http://testserver/gallery/" />',
            body,
        )

    def test_home_page_includes_local_business_and_faq_schema(self):
        response = self.client.get(reverse('home'))

        self.assertEqual(response.status_code, 200)

        body = response.content.decode()

        self.assertIn('"@type": "LocalBusiness"', body)
        self.assertIn('"@type": "FAQPage"', body)
        self.assertIn('Baddeley Green, Stoke-on-Trent', body)

    def test_private_pages_are_marked_noindex(self):
        response = self.client.get(reverse('login'))

        self.assertEqual(response.status_code, 200)

        body = response.content.decode()

        self.assertIn(
            '<meta name="robots" content="noindex, nofollow, noarchive" />',
            body,
        )

    def test_policy_page_uses_specific_title_and_canonical(self):
        response = self.client.get(reverse('get_policy', args=['safeguarding-policy']))

        self.assertEqual(response.status_code, 200)

        body = response.content.decode()

        self.assertIn(
            '<title>Safeguarding Policy in Baddeley Green, Stoke-on-Trent | Little Ducklings Childminding</title>',
            body,
        )
        self.assertIn(
            '<link rel="canonical" href="http://testserver/policies/safeguarding-policy/" />',
            body,
        )
