"""Offline tests only: fake classifiers; never call Gemini."""
import json
import os
import unittest
from unittest.mock import patch

import app
from streamlit.testing.v1 import AppTest


class TriageTests(unittest.TestCase):
    def result(self, priority='medium', review=False):
        return {'priority': priority, 'reason': 'Impact assessment.', 'human_review': review}

    def run_ticket(self, text='Please help with setup', priority='medium', review=False):
        return app.process_ticket({'subject': '', 'body': text}, lambda _: self.result(priority, review))

    def test_critical_always_requires_intervention(self):
        r = self.run_ticket('All operations stopped', 'critical')
        self.assertTrue(r['human_review'])
        self.assertFalse(r['ai_human_review'])
        self.assertEqual(r['routing'], 'ESCALATE IMMEDIATELY')
        self.assertIn('Critical incident', r['review_triggers'][0])

    def test_bilingual_data_loss(self):
        for text in app.DATA_LOSS_TERMS:
            with self.subTest(text=text):
                r = self.run_ticket(text)
                self.assertTrue(r['data_loss_detected'])
                self.assertTrue(r['human_review'])
                self.assertEqual(r['routing'], 'SEND FOR HUMAN REVIEW')

    def test_combined_triggers(self):
        self.assertEqual(len(self.run_ticket('Missing files', 'critical', True)['review_triggers']), 3)

    def test_all_priorities(self):
        for p in app.PRIORITIES:
            r = self.run_ticket(priority=p)
            self.assertEqual(r['priority'], p)
            self.assertEqual(r['human_review'], p == 'critical')

    def test_ai_review(self):
        self.assertTrue(self.run_ticket(review=True)['human_review'])

    def test_invalid_responses(self):
        invalid = [None, [], {}, {'priority': 'urgent', 'reason': 'x', 'human_review': False},
                   self.result(review='false'), self.result() | {'reason': ' '},
                   self.result() | {'reason': 'x' * 2001}, self.result() | {'extra': True}]
        for value in invalid:
            r = app.process_ticket({'subject': '', 'body': 'Missing files'}, lambda _: value)
            self.assertIsNone(r['priority'])
            self.assertTrue(r['human_review'])
            self.assertTrue(r['data_loss_detected'])
            self.assertEqual(len(r['review_triggers']), 2)

    def test_failure_preserves_independent_check(self):
        def fail(_):
            raise RuntimeError('SECRET_SENTINEL')
        r = app.process_ticket({'subject': '', 'body': 'Dateien fehlen'}, fail)
        self.assertTrue(r['data_loss_detected'])
        self.assertNotIn('SECRET_SENTINEL', str(r))
        self.assertIsNone(r['priority'])
        def malformed(_):
            return json.loads('not JSON')
        self.assertEqual(app.process_ticket({'subject': '', 'body': 'Help'}, malformed)['status'], 'fallback')

    def test_invalid_input_never_calls_classifier(self):
        def forbidden(_):
            self.fail('Classifier was called')
        for ticket in [None, {}, {'subject': '', 'body': ' '}, {'subject': 7, 'body': 'Help'},
                       {'subject': 'x'*161, 'body': 'Help'}, {'subject': '', 'body': 'x'*4001}]:
            self.assertEqual(app.process_ticket(ticket, forbidden)['status'], 'fallback')

    def test_shared_limits(self):
        b = app.Budget()
        for _ in range(6):
            self.assertIsNone(b.reserve(0))
        self.assertIsNotNone(b.reserve(1))
        self.assertIsNone(b.reserve(60))
        b = app.Budget()
        for i in range(100):
            self.assertIsNone(b.reserve(i*61))
        self.assertIsNotNone(b.reserve(6100))
        self.assertIsNone(b.reserve(86400))

    def test_settings(self):
        with patch.object(app.st, 'secrets', {'GEMINI_MODEL': 'secret-model'}), patch.dict(os.environ, {'GEMINI_MODEL': 'env-model'}):
            self.assertEqual(app.setting('GEMINI_MODEL'), 'secret-model')
        with patch.object(app.st, 'secrets', {}), patch.dict(os.environ, {'GEMINI_MODEL': 'env-model'}):
            self.assertEqual(app.setting('GEMINI_MODEL'), 'env-model')


class UITests(unittest.TestCase):
    def test_no_key_startup(self):
        with patch.dict(os.environ, {'GEMINI_API_KEY': ''}):
            at = AppTest.from_file('app.py').run()
            self.assertFalse(at.exception)
            self.assertTrue(at.button[0].disabled)

    def test_consent_and_session_limit(self):
        with patch.dict(os.environ, {'GEMINI_API_KEY': 'offline-test-placeholder', 'ENABLE_LIVE_DEMO': 'true'}), patch('google.genai.Client') as client:
            at = AppTest.from_file('app.py').run()
            at.text_area[0].input('A fictional support request')
            at.button[0].click().run()
            self.assertEqual(client.call_count, 0)
            self.assertIn('privacy notice', at.warning[-1].value)
            at.session_state['attempts'] = 10
            at.checkbox[0].check()
            at.button[0].click().run()
            self.assertEqual(client.call_count, 0)
            self.assertIn('10-attempt limit', at.warning[-1].value)
            self.assertFalse(at.exception)

    def test_sample_submit_clear_and_cooldown(self):
        with patch.dict(os.environ, {'GEMINI_API_KEY': 'offline-test-placeholder', 'ENABLE_LIVE_DEMO': 'true'}), patch('google.genai.Client') as client:
            client.return_value.__enter__.return_value.models.generate_content.return_value.text = json.dumps(
                {'priority': 'critical', 'reason': 'Company-wide outage.', 'human_review': False})
            at = AppTest.from_file('app.py').run()
            at.selectbox[0].select('EN · Company-wide outage').run()
            self.assertEqual(client.call_count, 0)
            at.checkbox[0].check()
            at.button[0].click().run()
            self.assertFalse(at.exception)
            self.assertEqual(client.call_count, 1)
            self.assertEqual(client.call_args.kwargs['http_options'].retry_options.attempts, 1)
            config = client.return_value.__enter__.return_value.models.generate_content.call_args.kwargs['config']
            self.assertEqual(config.max_output_tokens, 1024)
            self.assertEqual(config.response_json_schema, app.SCHEMA)
            self.assertEqual(at.metric[0].value, 'CRITICAL')
            self.assertTrue(at.session_state['result']['human_review'])
            at.button[0].click().run()
            self.assertEqual(client.call_count, 1)
            at.button[1].click().run()
            self.assertEqual(at.text_area[0].value, '')
            self.assertEqual(at.session_state['attempts'], 1)
            self.assertFalse(at.exception)


if __name__ == '__main__':
    unittest.main()
