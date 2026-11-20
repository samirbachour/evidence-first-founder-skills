import json
import os
import re
import unittest
from _load import ROOT, SKILLS_DIR

EXPECTED = {
    'founder-board', 'founder-brand', 'founder-cfo', 'founder-competitors',
    'founder-consumer', 'founder-ecommerce', 'founder-launch', 'founder-marketing',
    'founder-offer', 'founder-ops', 'founder-plan', 'founder-pricing',
    'founder-prioritize', 'founder-validation'
}


class Repo(unittest.TestCase):
    def test_fourteen_skills_have_valid_frontmatter(self):
        existing = {d for d in os.listdir(SKILLS_DIR)
                    if os.path.isfile(os.path.join(SKILLS_DIR, d, 'SKILL.md'))}
        self.assertEqual(existing, EXPECTED)
        for skill in existing:
            with open(os.path.join(SKILLS_DIR, skill, 'SKILL.md'), encoding='utf-8') as fh:
                content = fh.read()
            self.assertTrue(content.startswith('---\nname: ' + skill + '\n'))
            self.assertRegex(content, r'(?m)^description: .+\n')
            self.assertGreater(len(content), 450)
            self.assertNotIn('${CLAUDE_SKILL_DIR}', content)
            self.assertNotIn('subagent_type:', content)

    def test_portable_plugin_manifest_and_license(self):
        with open(os.path.join(ROOT, 'plugin.json'), encoding='utf-8') as f:
            plugin = json.load(f)
        self.assertEqual(plugin['$schema'], 'https://agent-plugins.org/schemas/1.0.0/plugin.schema.json')
        self.assertEqual(plugin['name'], 'evidence-first-founder-skills')
        self.assertEqual(plugin['license'], 'MIT')
        with open(os.path.join(ROOT, 'LICENSE'), encoding='utf-8') as f:
            self.assertIn('Copyright (c) 2026 Jake Schincariol', f.read())
        with open(os.path.join(ROOT, 'README.md'), encoding='utf-8') as f:
            readme = f.read()
        self.assertIn('not automatically install', readme)
        self.assertIn('14 reusable business-analysis skills', readme)

    def test_public_package_has_no_private_project_playbooks(self):
        self.assertFalse(os.path.exists(os.path.join(ROOT, 'projects')))
        for dirname in ('skills', 'research', 'templates'):
            for folder, dirs, files in os.walk(os.path.join(ROOT, dirname)):
                for filename in files:
                    if filename.endswith(('.md', '.json', '.csv', '.py')):
                        with open(os.path.join(folder, filename), encoding='utf-8') as f:
                            content = f.read()
                        self.assertNotIn('@gmail.com', content, filename)
                        self.assertNotIn('sk-proj-', content, filename)
                        self.assertNotIn('github_pat_', content, filename)

    def test_cfo_and_plan_scripts_exist(self):
        for rel in ('founder-cfo/unit_economics.py', 'founder-plan/compile.py',
                    'founder-pricing/van_westendorp.py', 'founder-consumer/panel.py'):
            self.assertTrue(os.path.isfile(os.path.join(SKILLS_DIR, rel)))

    def test_examples_still_parse(self):
        for rel in ('founder-cfo/example.json', 'founder-consumer/customer.example.json'):
            with open(os.path.join(SKILLS_DIR, rel), encoding='utf-8') as f:
                json.load(f)

    def test_unverified_templates_do_not_contain_fake_products(self):
        for item in ('numbers-online-store.json', 'evidence-ledger.csv', 'store-data-checklist.md'):
            self.assertTrue(os.path.isfile(os.path.join(ROOT, 'templates', item)))
        with open(os.path.join(ROOT, 'templates', 'numbers-online-store.json'), encoding='utf-8') as f:
            doc = json.load(f)
        self.assertIsNone(doc['price'])
        self.assertEqual(len(doc['ramp_per_month']), 12)
        self.assertTrue(all(val is None for val in doc['ramp_per_month']))


if __name__ == '__main__':
    unittest.main()
