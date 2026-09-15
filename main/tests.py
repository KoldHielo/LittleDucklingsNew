from pathlib import Path
from xml.etree import ElementTree

from django.conf import settings
from django.test import TestCase
from django.urls import NoReverseMatch, reverse


class ShowcaseSiteTests(TestCase):
    removed_route_names = (
        'login', 'logout', 'password_reset', 'password_verify', 'activate_account',
        'parent_dashboard', 'staff_dashboard', 'child', 'child_contract',
        'child_consent', 'child_record', 'child_register',
    )

    def test_authentication_and_portal_routes_are_removed(self):
        for route_name in self.removed_route_names:
            with self.subTest(route_name=route_name):
                with self.assertRaises(NoReverseMatch):
                    reverse(route_name)

        for path in ('/login/', '/admin/', '/parent_dashboard/', '/child_register/'):
            with self.subTest(path=path):
                self.assertEqual(self.client.get(path).status_code, 404)

    def test_navigation_has_no_login_or_dashboard_links(self):
        body = self.client.get(reverse('home')).content.decode()

        self.assertNotIn('>Login<', body)
        self.assertNotIn('>Logout<', body)
        self.assertNotIn('>Dashboard<', body)


class SitemapTests(TestCase):
    def test_sitemap_includes_public_pages_and_every_policy(self):
        response = self.client.get(reverse('sitemap'))
        self.assertEqual(response.status_code, 200)

        root = ElementTree.fromstring(response.content)
        namespace = {'sm': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
        locations = {element.text for element in root.findall('sm:url/sm:loc', namespace)}
        policy_template_dir = Path(settings.BASE_DIR, 'main/templates/policies')
        policy_urls = {
            f'https://testserver/policies/{path.stem}/'
            for path in policy_template_dir.glob('*.html')
            if path.stem != 'base'
        }

        self.assertSetEqual(locations, {
            'https://testserver/',
            'https://testserver/gallery/',
            'https://testserver/policies/',
            *policy_urls,
        })

    def test_robots_only_publishes_sitemap(self):
        body = self.client.get(reverse('robots')).content.decode()

        self.assertIn('User-agent: *', body)
        self.assertIn('Allow: /', body)
        self.assertNotIn('Disallow:', body)
        self.assertIn(f'Sitemap: {settings.SITE_URL}/sitemap.xml', body)


class PolicyAuditTests(TestCase):
    def policy_body(self, slug):
        response = self.client.get(reverse('get_policy', args=[slug]))
        self.assertEqual(response.status_code, 200)
        return response.content.decode()

    def test_policy_menu_includes_new_uncollected_child_policy(self):
        body = self.client.get(reverse('policy_menu')).content.decode()
        self.assertIn('/policies/uncollected-child-policy/', body)
        self.assertIn('Special Educational Needs and Disabilities (SEND)', body)

    def test_all_policies_include_document_control(self):
        policy_dir = Path(settings.BASE_DIR, 'main/templates/policies')
        for path in policy_dir.glob('*.html'):
            if path.stem == 'base':
                continue
            with self.subTest(policy=path.stem):
                body = self.policy_body(path.stem)
                self.assertIn('Effective and last reviewed:', body)
                self.assertIn('15 September 2026', body)

    def test_high_priority_audit_corrections_are_published(self):
        self.assertIn('always within 14 days', self.policy_body('accident-procedure'))
        self.assertIn('within 28 days', self.policy_body('complaints-policy'))
        self.assertIn('verbal permission on its own is not enough', self.policy_body('medication-policy'))
        self.assertIn('no blanket 10-day COVID-19 exclusion', self.policy_body('illness-infection-control-policy'))
        self.assertIn('0800 028 0285', self.policy_body('whistleblowing-policy'))
        self.assertIn('adult remains in the same room', self.policy_body('health-safety-policy'))
        self.assertIn('Information Commissioner', self.policy_body('privacy-notice'))

    def test_confirmed_operational_details_are_consistent(self):
        accident = self.policy_body('accident-procedure')
        attendance = self.policy_body('attendance-record')
        doorbell = self.policy_body('doorbell-video-policy')
        privacy = self.policy_body('privacy-notice')

        self.assertIn('ChildLogs', accident)
        self.assertIn('ChildLogs', attendance)
        self.assertIn('video and audio', doorbell)
        self.assertIn('micro SD card', doorbell)
        self.assertIn('not stored in a cloud service', doorbell)
        self.assertIn('secure parent portal', privacy)


class SeoMetadataTests(TestCase):
    def test_home_page_includes_local_business_and_faq_schema(self):
        body = self.client.get(reverse('home')).content.decode()
        self.assertIn('"@type": "LocalBusiness"', body)
        self.assertIn('"@type": "FAQPage"', body)

    def test_policy_page_uses_specific_title_and_canonical(self):
        body = self.client.get(
            reverse('get_policy', args=['safeguarding-policy'])
        ).content.decode()
        self.assertIn(
            '<title>Safeguarding and Child Protection Policy in Baddeley Green, '
            'Stoke-on-Trent | Little Ducklings Childminding</title>',
            body,
        )
        self.assertIn(
            '<link rel="canonical" href="http://testserver/policies/safeguarding-policy/" />',
            body,
        )
