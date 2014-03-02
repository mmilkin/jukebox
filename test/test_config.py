from unittest import TestCase
from mock import patch, Mock, call
from jukebox.config import make_root_resource
from jukebox.storage import MemoryStorage


class TestConfig(TestCase):

    @patch('jukebox.scanner.DirScanner')
    @patch('ConfigParser.RawConfigParser')
    def test_multiple_directory(self, RawConfigParser, DirScanner):
        mock_scanner = Mock(name='scanner')
        raw_config = Mock(name='raw_config')
        RawConfigParser.return_value = raw_config
        DirScanner.side_effect = mock_scanner
        raw_config.get.return_value = 'folder1,folder2'
        make_root_resource()
        mock_calls = mock_scanner.call_args_list
        expected_folders = [mock_calls[0][0][1], mock_calls[1][0][1]]
        self.assertEqual(len(mock_calls), 2)
        self.assertTrue('folder1' in expected_folders)
        self.assertTrue('folder2' in expected_folders)

    @patch('jukebox.scanner.DirScanner')
    @patch('ConfigParser.RawConfigParser')
    def test_directory(self, RawConfigParser, DirScanner):
        mock_scanner = Mock(name='scanner')
        raw_config = Mock(name='raw_config')
        RawConfigParser.return_value = raw_config
        DirScanner.side_effect = mock_scanner
        raw_config.get.return_value = 'folder1'
        make_root_resource()
        mock_calls = mock_scanner.call_args_list
        self.assertEqual(len(mock_calls), 1)
        self.assertEqual(mock_calls[0][0][1], 'folder1')
